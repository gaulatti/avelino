// Include GLib before Qt's signals macro.
#include <libtracker-sparql/tracker-sparql.h>
#include "filechoosersearch.h"
#include "filechooserexpression.h"
#include <QDir>
#include <QGuiApplication>
#include <QJSEngine>
#include <QMimeDatabase>
#include <QThread>
#include <algorithm>
#include <memory>

class FileSearchQuery final : public QThread {
    Q_OBJECT
public:
    struct Request {quint64 generation;QVariantList expression;bool folderOnly;QUrl folder;QVariantList types;};
    explicit FileSearchQuery(Request request):m_request(std::move(request)),m_cancel(g_cancellable_new()){}
    ~FileSearchQuery()override{g_object_unref(m_cancel);}
    void cancel(){g_cancellable_cancel(m_cancel);}
signals:
    void snapshot(quint64 generation,const QVariantList &rows,const QString &error);
    void querying(quint64 generation);
protected:
    void run()override{
        m_context=g_main_context_new();m_loop=g_main_loop_new(m_context,false);
        g_main_context_push_thread_default(m_context);
        m_validator=std::make_unique<FileChooserModel>();m_validator->setAllowedContentTypes(m_request.types);
        const auto cancellation=g_cancellable_connect(m_cancel,G_CALLBACK(+[](GCancellable*,gpointer data){
            auto self=static_cast<FileSearchQuery*>(data);
            g_main_context_invoke(self->m_context,+[](gpointer data)->gboolean{
                auto self=static_cast<FileSearchQuery*>(data);self->m_stopping=true;
                if(!self->m_pending)g_main_loop_quit(self->m_loop);
                return G_SOURCE_REMOVE;
            },self);
        }),this,nullptr);
        if(!g_cancellable_is_cancelled(m_cancel)){
            m_pending=true;
            tracker_sparql_connection_bus_new_async("org.freedesktop.Tracker3.Miner.Files",nullptr,nullptr,m_cancel,
                +[](GObject*,GAsyncResult *result,gpointer data){static_cast<FileSearchQuery*>(data)->connected(result);},this);
            g_main_loop_run(m_loop);
        }
        if(cancellation)g_cancellable_disconnect(m_cancel,cancellation);
        if(m_notifier){g_signal_handlers_disconnect_by_data(m_notifier,this);g_object_unref(m_notifier);}
        closeCursor();if(m_statement)g_object_unref(m_statement);
        if(m_connection){tracker_sparql_connection_close(m_connection);g_object_unref(m_connection);}
        m_validator.reset();g_main_context_pop_thread_default(m_context);
        g_main_loop_unref(m_loop);g_main_context_unref(m_context);
    }
private:
    bool cancelled()const{return m_stopping||g_cancellable_is_cancelled(m_cancel);}
    void closeCursor(){if(m_cursor){tracker_sparql_cursor_close(m_cursor);g_object_unref(m_cursor);m_cursor=nullptr;}}
    void fail(GError *error){
        m_pending=false;
        if(!cancelled())emit snapshot(m_request.generation,{},QStringLiteral("Indexed search is unavailable: ")+QString::fromUtf8(error?error->message:"unknown index error"));
        if(error)g_error_free(error);g_main_loop_quit(m_loop);
    }
    void connected(GAsyncResult *result){
        GError *error=nullptr;m_connection=tracker_sparql_connection_bus_new_finish(result,&error);
        if(!m_connection){fail(error);return;}
        m_pending=false;if(cancelled()){g_main_loop_quit(m_loop);return;}
        QString expression="?file a nfo:FileDataObject ; nie:url ?url ; nfo:fileName ?name . ";
        for(int index=0;index<m_request.expression.size();++index){
            const auto row=m_request.expression[index].toMap();
            const auto suffix=QString::number(index);
            const auto name="?file nfo:fileName ?matchedName"+suffix+" . FILTER(CONTAINS(LCASE(?matchedName"+suffix+"),LCASE(~name"+suffix+")))";
            const auto content="?file nie:interpretedAs ?document"+suffix+" . ?document"+suffix+" fts:match ~content"+suffix;
            // Join one group per segment. Each Everything/raw segment retains
            // its own name-or-content union; distinct groups form conjunction.
            expression+=" { ";
            if(row.value("mode")=="filename")expression+=name;
            else expression+="{ "+name+" } UNION { "+content+" }";
            expression+=" } ";
        }
        if(m_request.folderOnly)expression+=" FILTER(STRSTARTS(?url,~folder))";
        const auto query=("SELECT DISTINCT ?url WHERE { "+expression+" } ORDER BY LCASE(?name) ?url").toUtf8();
        m_statement=tracker_sparql_connection_query_statement(m_connection,query.constData(),m_cancel,&error);
        if(!m_statement){fail(error);return;}
        for(int index=0;index<m_request.expression.size();++index){
            const auto row=m_request.expression[index].toMap();const auto suffix=QByteArray::number(index);
            const auto text=fileSearchSegmentText(row).toUtf8();
            tracker_sparql_statement_bind_string(m_statement,("name"+suffix).constData(),text.constData());
            if(row.value("mode")!="filename"){
                // Bind each literal phrase; input never becomes FTS operators.
                QString phrase=fileSearchSegmentText(row);phrase.replace('"',"\"\"");phrase='"'+phrase+'"';
                const auto literal=phrase.toUtf8();tracker_sparql_statement_bind_string(m_statement,("content"+suffix).constData(),literal.constData());
            }
        }
        if(m_request.folderOnly){
            auto folder=m_request.folder.toEncoded(QUrl::FullyEncoded);if(!folder.endsWith('/'))folder+='/';
            tracker_sparql_statement_bind_string(m_statement,"folder",folder.constData());
        }
        m_notifier=tracker_sparql_connection_create_notifier(m_connection);
        g_signal_connect(m_notifier,"events",G_CALLBACK(+[](TrackerNotifier*,const gchar*,const gchar*,GPtrArray*,gpointer data){
            auto self=static_cast<FileSearchQuery*>(data);
            if(self->m_pending)self->m_dirty=true;else self->execute();
        }),this);
        execute();
    }
    void execute(){
        if(cancelled()){g_main_loop_quit(m_loop);return;}
        m_rows.clear();m_seen.clear();m_pending=true;m_dirty=false;emit querying(m_request.generation);
        tracker_sparql_statement_execute_async(m_statement,m_cancel,+[](GObject *source,GAsyncResult *result,gpointer data){
            auto self=static_cast<FileSearchQuery*>(data);GError *error=nullptr;
            self->m_cursor=tracker_sparql_statement_execute_finish(TRACKER_SPARQL_STATEMENT(source),result,&error);
            if(!self->m_cursor){self->fail(error);return;}self->next();
        },this);
    }
    void next(){
        tracker_sparql_cursor_next_async(m_cursor,m_cancel,+[](GObject *source,GAsyncResult *result,gpointer data){
            auto self=static_cast<FileSearchQuery*>(data);GError *error=nullptr;
            const auto more=tracker_sparql_cursor_next_finish(TRACKER_SPARQL_CURSOR(source),result,&error);
            if(error){self->fail(error);return;}
            if(!more){
                self->closeCursor();self->m_pending=false;
                if(self->cancelled()){g_main_loop_quit(self->m_loop);return;}
                emit self->snapshot(self->m_request.generation,self->m_rows,{});
                if(self->m_dirty)self->execute();return;
            }
            const auto value=tracker_sparql_cursor_get_string(self->m_cursor,0,nullptr);
            const QUrl url=QUrl::fromEncoded(QByteArray(value?value:""),QUrl::StrictMode);
            const QFileInfo info(url.toLocalFile());
            if(url.isValid()&&url.isLocalFile()&&!url.hasQuery()&&!url.hasFragment()
                &&QDir::isAbsolutePath(url.toLocalFile())&&info.exists()&&!info.isHidden()
                &&(info.isDir()||info.isFile())&&!self->m_seen.contains(url.toString())){
                self->m_seen.insert(url.toString());
                self->m_rows.append(QVariantMap{{"name",info.fileName()},{"url",url},{"directory",info.isDir()},
                    {"eligible",self->m_validator->eligible(url)},
                    {"kind",info.isDir()?QStringLiteral("Folder"):QMimeDatabase().mimeTypeForFile(info,QMimeDatabase::MatchExtension).comment()},
                    {"path",info.absolutePath()}});
            }
            self->next();
        },this);
    }
    Request m_request;
    GCancellable *m_cancel;
    GMainContext *m_context=nullptr;
    GMainLoop *m_loop=nullptr;
    TrackerSparqlConnection *m_connection=nullptr;
    TrackerSparqlStatement *m_statement=nullptr;
    TrackerSparqlCursor *m_cursor=nullptr;
    TrackerNotifier *m_notifier=nullptr;
    std::unique_ptr<FileChooserModel> m_validator;
    QVariantList m_rows;
    QSet<QString> m_seen;
    bool m_pending=false,m_dirty=false,m_stopping=false;
};

FileChooserSearch::FileChooserSearch(QObject *parent):FileChooserRows(parent){}
FileChooserSearch::~FileChooserSearch(){stop();}
QHash<int,QByteArray> FileChooserSearch::roleNames()const{
    return {{NameRole,"fileName"},{UrlRole,"fileUrl"},{DirectoryRole,"fileDirectory"},
        {EligibleRole,"fileEligible"},{SelectedRole,"fileSelected"},{KindRole,"fileKind"},{PathRole,"filePath"}};
}
QVariant FileChooserSearch::data(const QModelIndex &index,int role)const{
    const auto row=entry(index.isValid()?index.row():-1);if(row.isEmpty())return {};
    switch(role){case NameRole:return row["name"];case UrlRole:return row["url"];case DirectoryRole:return row["directory"];
    case EligibleRole:return row["eligible"];case SelectedRole:return row["selected"];case KindRole:return row["kind"];case PathRole:return row["path"];default:return {};}
}
QVariantMap FileChooserSearch::entry(int row)const{
    if(row<0||row>=m_rows.size())return {};auto value=m_rows[row].toMap();
    value["selected"]=m_selected.contains(value["url"].toUrl().toString());return value;
}
void FileChooserSearch::stop(){
    ++m_generation;for(auto job:m_jobs)if(job)job->cancel();
    m_jobs.erase(std::remove_if(m_jobs.begin(),m_jobs.end(),[](auto job){return job.isNull();}),m_jobs.end());
}
void FileChooserSearch::setContext(bool open,const QVariantList &types,const QUrl &folder){
    if(open==m_open&&types==m_types&&folder==m_folder)return;
    const bool opening=open&&!m_open;m_open=open;m_types=types;m_folder=folder;m_validator.setAllowedContentTypes(types);
    if(opening||!open){m_expression.clear();m_folderOnly=false;}
    restart(true);
}
void FileChooserSearch::setExpression(const QVariantList &value){
    if(value==m_expression)return;
    const auto error=fileSearchExpressionError(value);
    if(!error.isEmpty()){
        if(auto engine=qjsEngine(this))engine->throwError(error);else qWarning().noquote()<<error;
        return;
    }
    m_expression=value;restart();
}
void FileChooserSearch::setFolderOnly(bool value){if(value==m_folderOnly)return;m_folderOnly=value;restart();}
void FileChooserSearch::clear(){if(m_expression.isEmpty())return;m_expression.clear();restart();}
void FileChooserSearch::refresh(){restart(true);}
void FileChooserSearch::restart(bool retainSelection){
    stop();m_error.clear();m_busy=false;
    if(!retainSelection||!active()){
        beginResetModel();m_rows.clear();m_selected.clear();m_current.clear();m_anchor.clear();endResetModel();
    }
    if(!active()){emit changed();return;}
    for(const auto &part:m_expression)if(fileSearchSegmentText(part).contains(QChar::Null))m_error="Search text cannot contain NUL.";
    if(m_error.isEmpty()&&m_folderOnly&&(!m_folder.isLocalFile()||!QDir::isAbsolutePath(m_folder.toLocalFile())||!QFileInfo(m_folder.toLocalFile()).isDir()))m_error="The search folder is no longer available.";
    else if(!FileChooserModel::contentTypeError(m_types).isEmpty())m_error=FileChooserModel::contentTypeError(m_types);
    if(!m_error.isEmpty()){emit changed();return;}
    m_busy=true;
    auto job=new FileSearchQuery({m_generation,m_expression,m_folderOnly,m_folder,m_types});m_jobs.append(job);
    connect(job,&FileSearchQuery::querying,this,[this](quint64 generation){if(generation==m_generation){m_busy=true;emit changed();}});
    connect(job,&FileSearchQuery::snapshot,this,[this](quint64 generation,const QVariantList &rows,const QString &error){
        if(generation!=m_generation||!active())return;
        beginResetModel();m_rows=rows;m_error=error;m_busy=false;QSet<QString> visible;
        for(const auto &value:rows){const auto row=value.toMap();if(row["eligible"].toBool()||row["directory"].toBool())visible.insert(row["url"].toUrl().toString());}
        m_selected.intersect(visible);if(!visible.contains(m_current))m_current.clear();if(!visible.contains(m_anchor))m_anchor.clear();
        endResetModel();emit changed();
    });
    connect(job,&QThread::finished,job,&QObject::deleteLater);job->start();emit changed();
}
int FileChooserSearch::currentIndex()const{
    for(int i=0;i<m_rows.size();++i)if(m_rows[i].toMap()["url"].toUrl().toString()==m_current)return i;return -1;
}
void FileChooserSearch::selectionChanged(){
    QPointer<FileChooserSearch> guard(this);
    if(!m_rows.isEmpty())emit dataChanged(index(0),index(m_rows.size()-1),{SelectedRole});
    if(guard)emit changed();
}
QVariantList FileChooserSearch::selection()const{
    QVariantList urls;for(const auto &value:m_rows){const auto row=value.toMap();if(m_selected.contains(row["url"].toUrl().toString()))urls.append(row["url"]);}return urls;
}
void FileChooserSearch::setSelection(const QVariantList &urls){
    if(!active())return;
    QSet<QString> requested;for(const auto &url:urls)requested.insert(url.toUrl().toString());
    m_selected.clear();
    for(const auto &value:m_rows){const auto row=value.toMap();const auto key=row["url"].toUrl().toString();
        if(requested.contains(key)&&(row["eligible"].toBool()||row["directory"].toBool()))m_selected.insert(key);
    }
    if(!m_selected.contains(m_current)){
        m_current.clear();for(const auto &value:m_rows){const auto key=value.toMap()["url"].toUrl().toString();if(m_selected.contains(key)){m_current=key;break;}}
    }
    if(!m_selected.contains(m_anchor))m_anchor=m_current;
    selectionChanged();
}
void FileChooserSearch::select(int row,int modifiers){
    const auto value=entry(row);if(!active()||value.isEmpty()||(!value["directory"].toBool()&&!value["eligible"].toBool()))return;
    const bool toggle=modifiers&(Qt::ControlModifier|Qt::MetaModifier),range=modifiers&Qt::ShiftModifier;
    if(!toggle)m_selected.clear();const auto key=value["url"].toUrl().toString();
    if(range){
        int anchor=0;for(int i=0;i<m_rows.size();++i)if(m_rows[i].toMap()["url"].toUrl().toString()==m_anchor){anchor=i;break;}
        for(int i=std::min(row,anchor);i<=std::max(row,anchor);++i){const auto candidate=entry(i);if(candidate["directory"].toBool()||candidate["eligible"].toBool())m_selected.insert(candidate["url"].toUrl().toString());}
    }else{if(toggle&&m_selected.contains(key))m_selected.remove(key);else m_selected.insert(key);m_anchor=key;}
    m_current=key;selectionChanged();
}
void FileChooserSearch::selectFromInput(int row){select(row,int(QGuiApplication::keyboardModifiers()));}
void FileChooserSearch::move(int offset,int modifiers){
    if(!active()||!offset)return;const auto step=offset>0?1:-1;
    for(int row=currentIndex()<0?(step>0?0:count()-1):std::clamp(currentIndex()+offset,0,count()-1);row>=0&&row<count();row+=step){
        const auto value=entry(row);if(value["directory"].toBool()||value["eligible"].toBool()){select(row,modifiers);return;}
    }
}
void FileChooserSearch::selectAll(){
    if(!active())return;m_selected.clear();
    for(const auto &value:m_rows){const auto row=value.toMap();if(row["eligible"].toBool())m_selected.insert(row["url"].toUrl().toString());}selectionChanged();
}
bool FileChooserSearch::canOpen()const{return active()&&m_error.isEmpty()&&!m_selected.isEmpty();}
QVariantList FileChooserSearch::selectedUrls()const{
    QVariantList urls;for(const auto &value:m_rows){const auto row=value.toMap();if(!row["eligible"].toBool()||!m_selected.contains(row["url"].toUrl().toString()))continue;
        const QFileInfo info(row["url"].toUrl().toLocalFile());auto path=info.canonicalFilePath();if(info.isDir()&&!path.isEmpty()&&!path.endsWith('/'))path+='/';urls.append(path.isEmpty()?QUrl():QUrl::fromLocalFile(path));}return urls;
}
void FileChooserSearch::activate(int row){
    const auto value=entry(row);if(!active()||value.isEmpty())return;
    if(value["directory"].toBool()){emit navigateRequested(value["url"].toUrl());return;}
    if(value["eligible"].toBool()){
        QPointer<FileChooserSearch> guard(this);select(row);if(guard)acceptSelection();
    }
}
void FileChooserSearch::acceptSelection(){
    if(!canOpen()||m_completing)return;
    for(const auto &value:m_rows){const auto row=value.toMap();const auto url=row["url"].toUrl();if(!m_selected.contains(url.toString()))continue;
        if(m_selected.size()==1&&row["directory"].toBool()&&!row["eligible"].toBool()){emit navigateRequested(url);return;}
        if(!m_validator.eligible(url)||QFileInfo(url.toLocalFile()).canonicalFilePath().isEmpty()){
            m_error="A selected item is no longer available for this file type";emit changed();return;
        }
    }
    const auto urls=selectedUrls();if(urls.isEmpty())return;
    m_completing=true;QPointer<FileChooserSearch> guard(this);emit result({{"kind","success"},{"urls",urls}});if(guard)m_completing=false;
}

#include "filechoosersearch.moc"

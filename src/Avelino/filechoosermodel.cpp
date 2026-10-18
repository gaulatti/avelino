#include "filechoosermodel.h"
#include <QCollator>
#include <QDir>
#include <QFile>
#include <QJSEngine>
#include <QMimeDatabase>
#include <QMimeType>
#include <QPointer>
#include <QQmlEngine>
#include <QRegularExpression>
#include <QStandardPaths>
#include <algorithm>
#include <cerrno>
#include <cstring>
#include <dirent.h>

FileChooserModel::FileChooserModel(QObject *parent):QAbstractListModel(parent) {
    connect(&m_watcher,&QFileSystemWatcher::directoryChanged,this,[this]{if(m_active)refresh();});
}
QHash<int,QByteArray> FileChooserModel::roleNames() const {
    return {{NameRole,"fileName"},{UrlRole,"fileUrl"},{DirectoryRole,"fileDirectory"},
        {EligibleRole,"fileEligible"},{SelectedRole,"fileSelected"}};
}
QVariant FileChooserModel::data(const QModelIndex &index,int role) const {
    if(!index.isValid()||index.row()<0||index.row()>=m_rows.size())return {};
    const auto &row=m_rows[index.row()];
    switch(role){
    case NameRole:return row.info.fileName();
    case UrlRole:return row.url;
    case DirectoryRole:return row.info.isDir();
    case EligibleRole:return row.eligible;
    case SelectedRole:return m_selected.contains(row.url.toString());
    default:return {};
    }
}
bool FileChooserModel::compileTypes(const QVariantList &values,QList<Type> &output,QString &error) {
    QMimeDatabase database;
    auto addMime=[&](const QString &name,Type &type){
        if(name=="inode/directory"){type.directories=true;return true;}
        if(name=="*/*"){type.allFiles=true;return true;}
        if(name.endsWith("/*")&&QRegularExpression("^[a-z][a-z0-9.+-]*/\\*$").match(name).hasMatch()){
            const auto all=database.allMimeTypes();
            if(std::none_of(all.begin(),all.end(),[&](const QMimeType &t){return t.name().startsWith(name.chopped(1));}))return false;
            type.mimeTypes.append(name);return true;
        }
        const auto mime=database.mimeTypeForName(name);
        if(!mime.isValid())return false;
        type.mimeTypes.append(mime.name());return true;
    };
    for(const auto &value:values){
        Type type;
        if(value.metaType().id()==QMetaType::QString){
            if(!addMime(value.toString(),type)){error="Unknown file content MIME type: "+value.toString();return false;}
        }else if(value.metaType().id()==QMetaType::QVariantMap){
            const auto object=value.toMap();
            if(object.value("identifier").metaType().id()!=QMetaType::QString||object.value("identifier").toString().trimmed().isEmpty()){
                error="A custom file type requires an identifier";return false;
            }
            for(auto it=object.begin();it!=object.end();++it)if(it.key()!="identifier"&&it.key()!="mimeTypes"&&it.key()!="filenameExtensions"){
                error="Unknown custom file type field: "+it.key();return false;
            }
            for(const auto &key:{QStringLiteral("mimeTypes"),QStringLiteral("filenameExtensions")}){
                if(!object.contains(key))continue;
                const auto list=object[key];
                if(list.metaType().id()!=QMetaType::QVariantList&&list.metaType().id()!=QMetaType::QStringList){error=key+" must be an array";return false;}
                for(const auto &tag:list.toList()){
                    if(tag.metaType().id()!=QMetaType::QString){error=key+" must contain strings";return false;}
                    const auto text=tag.toString();
                    if(key=="mimeTypes"){
                        if(!addMime(text,type)){error="Unknown file content MIME type: "+text;return false;}
                    }else{
                        if(text.isEmpty()||text.startsWith('.')||text.contains('/')||text.contains('\\')||text.contains('*')||text.contains('?')){
                            error="File extensions must be literal suffixes without a leading dot";return false;
                        }
                        type.extensions.append(text.toCaseFolded());
                    }
                }
            }
        }else{error="File content types must be MIME strings or explicit descriptors";return false;}
        output.append(type);
    }
    return true;
}
QString FileChooserModel::contentTypeError(const QVariantList &value){
    QList<Type> rules;QString error;compileTypes(value,rules,error);return error;
}
void FileChooserModel::setAllowedContentTypes(const QVariantList &value){
    if(value==m_types)return;
    QList<Type> rules;QString error;
    if(!compileTypes(value,rules,error)){
        if(auto engine=qjsEngine(this))engine->throwError(error);else qWarning("%s",qPrintable(error));
        // Invalid configuration must never retain a permissive old filter.
        m_types=value;m_rules.clear();m_typeError=error;setError(error,EINVAL);emit allowedContentTypesChanged();
        if(m_active)refresh();return;
    }
    m_types=value;m_rules=rules;m_typeError.clear();setError({});emit allowedContentTypesChanged();
    if(m_active)refresh();
}
bool FileChooserModel::canChooseDirectories() const {
    return std::any_of(m_rules.begin(),m_rules.end(),[](const Type &t){return t.directories;});
}
bool FileChooserModel::canChooseFiles() const {
    return std::any_of(m_rules.begin(),m_rules.end(),[](const Type &t){return !t.directories||t.allFiles||!t.mimeTypes.isEmpty()||!t.extensions.isEmpty();});
}
bool FileChooserModel::matches(const QFileInfo &info) const {
    if(!info.exists())return false;
    if(info.isDir())return canChooseDirectories();
    QMimeDatabase database;
    const auto mime=database.mimeTypeForFile(info,QMimeDatabase::MatchExtension);
    const auto name=info.fileName().toCaseFolded();
    for(const auto &type:m_rules){
        if(type.allFiles)return true;
        for(const auto &extension:type.extensions)if(name.endsWith('.'+extension))return true;
        for(const auto &wanted:type.mimeTypes){
            if(wanted.endsWith("/*") ? mime.name().startsWith(wanted.chopped(1)):mime.inherits(wanted))return true;
        }
    }
    return false;
}
QUrl FileChooserModel::localUrl(const QFileInfo &info,bool canonical){
    auto path=canonical?info.canonicalFilePath():info.absoluteFilePath();
    if(path.isEmpty())return {};
    if(info.isDir()&&!path.endsWith('/'))path+='/';
    return QUrl::fromLocalFile(path);
}
bool FileChooserModel::eligible(const QUrl &url) const {
    return url.isLocalFile()&&!url.hasQuery()&&!url.hasFragment()&&matches(QFileInfo(url.toLocalFile()));
}
bool FileChooserModel::pathFileAvailable(const QUrl &url)const{
    return m_active&&m_typeError.isEmpty()&&canChooseFiles()&&url.isLocalFile()
        &&!url.hasQuery()&&!url.hasFragment()&&QDir::isAbsolutePath(url.toLocalFile())&&QFileInfo(url.toLocalFile()).isFile();
}
bool FileChooserModel::selectPath(const QUrl &url){
    if(!pathFileAvailable(url))return false;
    const QFileInfo info(url.toLocalFile());
    if(QDir::cleanPath(info.absolutePath())!=QDir::cleanPath(folderPath()))return false;
    m_pathSelected=QUrl::fromLocalFile(info.absoluteFilePath());
    m_selected={m_pathSelected.toString()};
    // A deliberately addressed hidden file must have a visible selection too.
    // Ordinary listing/filter eligibility remains unchanged.
    refresh();
    for(int i=0;i<m_rows.size();++i)if(m_rows[i].url==m_pathSelected){m_current=m_anchor=i;selectionUpdated();return true;}
    return false;
}
QUrl FileChooserModel::defaultFolder() const {
    return QUrl::fromLocalFile(QStandardPaths::writableLocation(QStandardPaths::DocumentsLocation));
}
void FileChooserModel::setError(const QString &message,int code){
    if(m_error==message&&m_errorCode==code)return;
    m_error=message;m_errorCode=code;emit errorChanged();
}
bool FileChooserModel::reload(QUrl folder,bool keepSelection){
    QList<Row> rows;int code=0;QString message;
    if(!m_typeError.isEmpty()){
        code=EINVAL;message=m_typeError;
    }else if(!folder.isLocalFile()||folder.hasQuery()||folder.hasFragment()||!QDir::isAbsolutePath(folder.toLocalFile())){
        code=EINVAL;message="Choose an absolute local directory";
    }else{
        const auto path=QFile::encodeName(folder.toLocalFile());
        DIR *directory=opendir(path.constData());
        if(!directory){code=errno;message=QString::fromLocal8Bit(std::strerror(code));}
        else{
            errno=0;
            while(auto entry=readdir(directory)){
                const auto name=QFile::decodeName(entry->d_name);
                if(name=="."||name=="..")continue;
                if(name.startsWith('.')&&QDir(folder.toLocalFile()).filePath(name)!=m_pathSelected.toLocalFile())continue;
                QFileInfo info(QDir(folder.toLocalFile()).filePath(name));
                rows.append({info,localUrl(info,false),matches(info)});
                errno=0;
            }
            code=errno;closedir(directory);
            if(code){message=QString::fromLocal8Bit(std::strerror(code));rows.clear();}
        }
    }
    QCollator collator;collator.setCaseSensitivity(Qt::CaseInsensitive);collator.setNumericMode(true);
    std::stable_sort(rows.begin(),rows.end(),[&](const Row &a,const Row &b){
        const auto comparison=collator.compare(a.info.fileName(),b.info.fileName());
        return comparison==0?a.info.fileName()<b.info.fileName():comparison<0;
    });
    const auto oldCurrent=m_current>=0&&m_current<m_rows.size()?m_rows[m_current].url:QUrl();
    beginResetModel();m_rows=rows;m_current=-1;m_anchor=-1;
    if(!keepSelection){m_selected.clear();m_pathSelected=QUrl();}
    QSet<QString> retained;
    for(int i=0;i<m_rows.size();++i){
        const auto &row=m_rows[i];
        if((row.eligible||(row.url==m_pathSelected&&pathFileAvailable(row.url)))&&m_selected.contains(row.url.toString()))retained.insert(row.url.toString());
        if(row.url==oldCurrent)m_current=i;
    }
    m_selected=retained;if(!m_selected.contains(m_pathSelected.toString()))m_pathSelected=QUrl();endResetModel();
    const auto oldWatch=m_watcher.directories();if(!oldWatch.isEmpty())m_watcher.removePaths(oldWatch);
    const auto location=folder.isLocalFile()&&QDir::isAbsolutePath(folder.toLocalFile())
        ?QUrl::fromLocalFile(QDir::cleanPath(folder.toLocalFile())):folder;
    if(location!=m_folder){m_folder=location;emit folderChanged();}
    if(!code&&m_active)m_watcher.addPath(folder.toLocalFile());
    setError(message,code);emit listingChanged();emit selectionChanged();return code==0;
}
bool FileChooserModel::open(const QUrl &initialFolder){
    if(m_active||m_completing)return false;
    m_active=true;reload(m_folder.isEmpty()?initialFolder:m_folder,false);emit activeChanged();return true;
}
void FileChooserModel::cancel(){
    if(!m_active||m_completing)return;
    m_active=false;m_selected.clear();m_pathSelected=QUrl();m_current=m_anchor=-1;
    const auto watch=m_watcher.directories();if(!watch.isEmpty())m_watcher.removePaths(watch);
    emit activeChanged();selectionUpdated();
}
bool FileChooserModel::navigate(const QUrl &folder){return m_active&&reload(folder,false);}
bool FileChooserModel::goUp(){
    if(!m_active||!m_folder.isLocalFile()||!QDir::isAbsolutePath(folderPath()))return false;
    QDir directory(folderPath());if(!directory.cdUp())return false;
    return navigate(QUrl::fromLocalFile(directory.absolutePath()));
}
void FileChooserModel::refresh(){if(m_active)reload(m_folder,true);}
QVariantMap FileChooserModel::entry(int index) const {
    if(index<0||index>=m_rows.size())return {};
    const auto &row=m_rows[index];
    return {{"name",row.info.fileName()},{"url",row.url},{"directory",row.info.isDir()},
        {"eligible",row.eligible},{"selected",m_selected.contains(row.url.toString())}};
}
void FileChooserModel::selectionUpdated(){
    if(!m_rows.isEmpty())emit dataChanged(index(0),index(m_rows.size()-1),{SelectedRole});
    emit selectionChanged();
}
void FileChooserModel::select(int index,int modifiers){
    if(!m_active||index<0||index>=m_rows.size()||!m_rows[index].eligible)return;
    const bool toggle=modifiers&(Qt::ControlModifier|Qt::MetaModifier),range=modifiers&Qt::ShiftModifier;
    if(!toggle)m_selected.clear();
    if(range){
        if(m_anchor<0)m_anchor=0;
        for(int i=std::min(index,m_anchor);i<=std::max(index,m_anchor);++i)if(m_rows[i].eligible)m_selected.insert(m_rows[i].url.toString());
    }else{
        const auto key=m_rows[index].url.toString();
        if(toggle&&m_selected.contains(key))m_selected.remove(key);else m_selected.insert(key);
        m_anchor=index;
    }
    if(!m_selected.contains(m_pathSelected.toString()))m_pathSelected=QUrl();
    m_current=index;selectionUpdated();
}
void FileChooserModel::selectAll(){
    if(!m_active)return;m_selected.clear();m_pathSelected=QUrl();
    for(const auto &row:m_rows)if(row.eligible)m_selected.insert(row.url.toString());
    selectionUpdated();
}
void FileChooserModel::clearSelection(){m_selected.clear();m_pathSelected=QUrl();m_anchor=-1;selectionUpdated();}
void FileChooserModel::focusIndex(int index){
    if(index<0||index>=m_rows.size())return;
    m_current=index;emit selectionChanged();
}
void FileChooserModel::moveCurrent(int offset,int modifiers){
    if(!m_active||m_rows.isEmpty())return;
    const auto next=m_current<0?(offset>=0?0:m_rows.size()-1):std::clamp(m_current+offset,0,int(m_rows.size()-1));
    if(m_rows[next].eligible)select(next,modifiers);else{m_current=next;emit selectionChanged();}
}
void FileChooserModel::activate(int index){
    if(!m_active||index<0||index>=m_rows.size())return;
    if(m_rows[index].info.isDir()){navigate(m_rows[index].url);return;}
    if(m_rows[index].eligible){select(index);acceptSelection();}
}
QVariantList FileChooserModel::selectedUrls() const {
    QVariantList result;
    for(const auto &row:m_rows)if(m_selected.contains(row.url.toString()))result.append(localUrl(QFileInfo(row.info.absoluteFilePath()),true));
    return result;
}
bool FileChooserModel::canAccept() const {
    if(!m_active||!m_error.isEmpty())return false;
    if(!m_selected.isEmpty())return true;
    return canChooseDirectories()&&QFileInfo(folderPath()).isDir();
}
void FileChooserModel::acceptSelection(){
    if(!canAccept()||m_completing)return;
    QVariantList urls;
    for(const auto &row:m_rows)if(m_selected.contains(row.url.toString())){
        const QFileInfo current(row.info.absoluteFilePath());
        if(row.url==m_pathSelected?!pathFileAvailable(row.url):!matches(current)){setError("A selected item is no longer available for this file type",ENOENT);emit selectionChanged();return;}
        const auto url=localUrl(current,true);
        if(url.isEmpty()){setError("A selected item could not be resolved",ENOENT);emit selectionChanged();return;}
        urls.append(url);
    }
    if(urls.isEmpty()){
        const QFileInfo current(folderPath());
        if(!current.isDir()){setError("The selected directory is no longer available",ENOENT);emit selectionChanged();return;}
        urls.append(localUrl(current,true));
    }
    m_completing=true;QPointer<FileChooserModel> guard(this);
    emit result({{"kind","success"},{"urls",urls}});
    if(!guard)return;
    m_completing=false;cancel();
}

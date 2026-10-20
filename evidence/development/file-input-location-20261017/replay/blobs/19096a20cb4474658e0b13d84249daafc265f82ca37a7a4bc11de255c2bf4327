#include "filechooserbrowser.h"
#include <QDir>
#include <QFile>
#include <QGuiApplication>
#include <QJSEngine>
#include <QPointer>
#include <QQmlEngine>
#include <QStandardPaths>
#include <algorithm>
#include <cerrno>
#include <cstring>
#include <sys/stat.h>

FileChooserBrowser::FileChooserBrowser(QObject *parent):QAbstractListModel(parent),m_listing(new FileChooserListing(this)),m_places(new FileChooserPlaces(this)){
    connect(this,&FileChooserBrowser::metadataChanged,this,[this]{
        m_listing->setRoot(m_active&&m_viewMode!="columns"?modelAt(count()-1):nullptr);
        const auto folder=m_active?folderPath():QString();
        if(folder!=m_places->currentFolder())m_places->refresh(folder);
    });
    connect(m_listing,&FileChooserListing::changed,this,&FileChooserBrowser::metadataChanged);
    connect(m_listing,&FileChooserListing::navigateRequested,this,[this](const QUrl &url){navigatePath(url.toLocalFile());});
    connect(m_listing,&FileChooserListing::result,this,&FileChooserBrowser::completeResult);
}
void FileChooserBrowser::completeResult(const QVariantMap &value){
    if(!m_active||m_completing)return;
    m_completing=true;QPointer<FileChooserBrowser> guard(this);
    // Native Recent Places records the visible chooser location, including
    // results spanning List levels or a directory selected without navigation.
    if(value["kind"]=="success")m_places->rememberAcceptedFolder(folderPath());
    if(!guard)return;emit result(value);
    if(!guard)return;m_completing=false;cancel();
}
void FileChooserBrowser::refreshPlaces(){m_places->refresh(m_active?folderPath():QString());}
bool FileChooserBrowser::chooseLocation(const QUrl &url){
    if(!m_active||!url.isValid()||!url.isLocalFile()||url.hasQuery()||url.hasFragment()||!QDir::isAbsolutePath(url.toLocalFile()))return false;
    const auto path=QDir::cleanPath(url.toLocalFile());
    if(path==QDir::cleanPath(folderPath())&&error().isEmpty()){emit focusRequested(m_focus);return true;}
    return navigatePath(path);
}
void FileChooserBrowser::setViewMode(const QString &mode){
    if(mode==m_viewMode)return;
    if(mode!="columns"&&mode!="list"&&mode!="icons"){
        if(auto engine=qjsEngine(this))engine->throwError(QStringLiteral("File chooser view must be columns, list or icons"));
        else qWarning("File chooser view must be columns, list or icons");return;
    }
    QVariantList selected;
    if(m_viewMode!="columns")selected=m_listing->selection();
    else if(auto model=selectionModel())for(int i=0;i<model->count();++i){auto value=model->entry(i);if(value["selected"].toBool())selected.append(value["url"]);}
    const auto previous=m_viewMode;m_viewMode=mode;
    if(mode!="columns"){
        m_listing->setTreeMode(mode=="list");m_listing->setRoot(m_active?modelAt(count()-1):nullptr);
        if(previous=="columns")m_listing->setSelection(selected);
    }else{
        clearOtherSelections(-1);m_focus=m_selection=count()-1;
        if(auto model=selectionModel())for(int i=0;i<model->count();++i){const auto value=model->entry(i);if(value["eligible"].toBool()&&selected.contains(value["url"]))model->select(i,Qt::ControlModifier);}
        m_listing->setRoot(nullptr);
    }
    emit viewModeChanged();emit metadataChanged();emit focusRequested(m_focus);
}
QVariant FileChooserBrowser::data(const QModelIndex &index,int role) const {
    if(!index.isValid()||index.row()<0||index.row()>=m_columns.size())return {};
    const auto &column=m_columns[index.row()];
    if(role==ModelRole)return QVariant::fromValue(column.model);
    if(role==BranchRole)return column.branch;
    return {};
}
FileChooserModel *FileChooserBrowser::modelAt(int column) const {
    return column>=0&&column<m_columns.size()?m_columns[column].model:nullptr;
}
void FileChooserBrowser::setAllowedContentTypes(const QVariantList &value){
    if(value==m_types)return;
    m_types=value;m_typeError=FileChooserModel::contentTypeError(value);
    for(const auto &column:m_columns)column.model->setAllowedContentTypes(m_typeError.isEmpty()?value:QVariantList{});
    emit allowedContentTypesChanged();emit metadataChanged();
    if(!m_typeError.isEmpty()){
        if(auto engine=qjsEngine(this))engine->throwError(m_typeError);else qWarning("%s",qPrintable(m_typeError));
    }
}
QString FileChooserBrowser::folderPath() const {
    return m_columns.isEmpty()?QString():m_columns.last().model->folderPath();
}
QString FileChooserBrowser::folderLabel() const {
    const auto entries=m_places->entries();
    return m_active&&!entries.isEmpty()&&!entries.first().toMap()["heading"].toBool()?entries.first().toMap()["label"].toString():QString();
}
QString FileChooserBrowser::error() const {
    if(!m_typeError.isEmpty())return m_typeError;
    if(m_viewMode!="columns"&&!m_listing->error().isEmpty())return m_listing->error();
    return m_columns.isEmpty()?QString():m_columns.last().model->error();
}
bool FileChooserBrowser::canAccept() const {
    if(m_viewMode!="columns")return m_active&&m_typeError.isEmpty()&&m_listing->canOpen();
    const auto model=selectionModel();return m_active&&m_typeError.isEmpty()&&model&&model->canAccept();
}
QVariantList FileChooserBrowser::selectedUrls() const {
    if(m_viewMode!="columns")return m_listing->selectedUrls();
    const auto model=selectionModel();return model?model->selectedUrls():QVariantList{};
}
QUrl FileChooserBrowser::defaultFolder() const {
    return QUrl::fromLocalFile(QStandardPaths::writableLocation(QStandardPaths::DocumentsLocation));
}
void FileChooserBrowser::append(const QUrl &folder){
    auto model=new FileChooserModel(this);
    model->setAllowedContentTypes(m_typeError.isEmpty()?m_types:QVariantList{});
    model->open(folder);
    connect(model,&FileChooserModel::selectionChanged,this,&FileChooserBrowser::metadataChanged);
    connect(model,&FileChooserModel::errorChanged,this,&FileChooserBrowser::metadataChanged);
    connect(model,&FileChooserModel::folderChanged,this,&FileChooserBrowser::metadataChanged);
    connect(model,&FileChooserModel::result,this,&FileChooserBrowser::completeResult);
    const auto next=int(m_columns.size());beginInsertRows({},next,next);m_columns.append(Column{model,QUrl{}});endInsertRows();emit countChanged();
}
void FileChooserBrowser::trimAfter(int column){
    if(column+1>=m_columns.size())return;
    QList<FileChooserModel*> removed;
    beginRemoveRows({},column+1,m_columns.size()-1);
    while(m_columns.size()>column+1)removed.append(m_columns.takeLast().model);
    endRemoveRows();
    for(auto model:removed){disconnect(model,nullptr,this,nullptr);model->cancel();model->deleteLater();}
    m_focus=std::min(m_focus,column);m_selection=std::min(m_selection,column);emit countChanged();
}
void FileChooserBrowser::branch(int column,const QUrl &url){
    if(column<0||column>=m_columns.size()||m_columns[column].branch==url)return;
    m_columns[column].branch=url;emit dataChanged(index(column),index(column),{BranchRole});
}
bool FileChooserBrowser::open(const QUrl &initialFolder){
    if(m_active||m_completing)return false;
    trimAfter(-1);m_active=true;append(m_lastFolder.isEmpty()?initialFolder:m_lastFolder);
    m_focus=m_selection=0;m_history={location()};m_historyIndex=0;clearNewFolderError();
    emit activeChanged();emit metadataChanged();emit focusRequested(0);return true;
}
void FileChooserBrowser::cancel(){
    if(!m_active||m_completing)return;
    if(!m_columns.isEmpty())m_lastFolder=QUrl::fromLocalFile(folderPath());
    m_active=false;
    for(const auto &column:m_columns)column.model->cancel();
    emit metadataChanged();emit activeChanged();
}
void FileChooserBrowser::clearOtherSelections(int column){
    for(int i=0;i<m_columns.size();++i)if(i!=column)m_columns[i].model->clearSelection();
}
void FileChooserBrowser::choose(int column,int row,int modifiers){
    auto model=modelAt(column);if(!m_active||!model)return;
    // Copy row values before downstream columns or row models can be reset.
    const auto value=model->entry(row);if(value.isEmpty())return;
    const auto directory=value["directory"].toBool(),eligible=value["eligible"].toBool();
    if(!directory&&!eligible)return;
    const auto before=location();
    const auto url=value["url"].toUrl();
    clearOtherSelections(column);
    if(eligible)model->select(row,modifiers);else{model->clearSelection();model->focusIndex(row);}
    trimAfter(column);branch(column,{});m_focus=m_selection=column;
    const auto selected=model->entry(row)["selected"].toBool();
    if(directory&&(!eligible||(selected&&model->selectedUrls().size()==1))){
        branch(column,url);append(url);
        if(!eligible)m_selection=column+1;
    }
    rememberNavigation(before);emit metadataChanged();emit focusRequested(column);
}
void FileChooserBrowser::chooseFromInput(int column,int row){choose(column,row,int(QGuiApplication::keyboardModifiers()));}
void FileChooserBrowser::activate(int column,int row){
    auto model=modelAt(column);if(!m_active||!model)return;
    const auto value=model->entry(row);if(value.isEmpty())return;
    if(value["directory"].toBool()){choose(column,row);focusRight();}
    else if(value["eligible"].toBool()){choose(column,row);acceptSelection();}
}
void FileChooserBrowser::move(int offset,int modifiers){
    auto model=modelAt(m_focus);if(!m_active||!model||!offset)return;
    const auto step=offset>0?1:-1;
    int row=model->currentIndex()<0?(step>0?0:model->count()-1):model->currentIndex()+step;
    for(;row>=0&&row<model->count();row+=step){
        const auto entry=model->entry(row);
        if(entry["directory"].toBool()||entry["eligible"].toBool()){choose(m_focus,row,modifiers);return;}
    }
}
void FileChooserBrowser::moveFromInput(int offset){move(offset,int(QGuiApplication::keyboardModifiers()));}
void FileChooserBrowser::focusLeft(){
    if(!m_active||m_focus<=0)return;
    --m_focus;emit metadataChanged();emit focusRequested(m_focus);
}
void FileChooserBrowser::focusRight(){
    if(!m_active||m_focus+1>=m_columns.size())return;
    ++m_focus;emit metadataChanged();emit focusRequested(m_focus);
}
void FileChooserBrowser::selectAll(){
    if(m_viewMode!="columns"){m_listing->selectAll();return;}
    auto model=modelAt(m_focus);if(!m_active||!model)return;
    const auto before=location();
    clearOtherSelections(m_focus);model->selectAll();m_selection=m_focus;
    trimAfter(m_focus);branch(m_focus,{});rememberNavigation(before);emit metadataChanged();
}
bool FileChooserBrowser::navigatePath(const QString &path){
    if(!m_active)return false;
    const auto before=location();
    trimAfter(-1);append(QUrl::fromLocalFile(path));m_focus=m_selection=0;
    rememberNavigation(before);emit metadataChanged();emit focusRequested(0);return modelAt(0)->error().isEmpty();
}
bool FileChooserBrowser::goUp(){
    if(!m_active||!QDir::isAbsolutePath(folderPath()))return false;
    QDir directory(folderPath());if(!directory.cdUp())return false;
    return navigatePath(directory.absolutePath());
}
FileChooserBrowser::Location FileChooserBrowser::location() const {
    Location saved;
    for(const auto &column:m_columns)saved.columns.append({column.model->folder(),column.branch});
    return saved;
}
void FileChooserBrowser::rememberNavigation(const Location &before){
    const auto after=location();
    if(m_historyIndex<0||before.columns.isEmpty()||after.columns.isEmpty())return;
    if(before.columns.last().folder==after.columns.last().folder){m_history[m_historyIndex]=after;return;}
    m_history[m_historyIndex]=before;
    m_history.resize(m_historyIndex+1);m_history.append(after);++m_historyIndex;
}
void FileChooserBrowser::restoreLocation(int index){
    if(!m_active||index<0||index>=m_history.size())return;
    m_history[m_historyIndex]=location();
    const auto saved=m_history[index];trimAfter(-1);
    for(const auto &column:saved.columns){
        append(column.folder);branch(m_columns.size()-1,column.branch);
    }
    m_focus=m_selection=m_columns.size()-1;m_historyIndex=index;
    emit metadataChanged();emit focusRequested(m_focus);
}
void FileChooserBrowser::goBack(){if(canGoBack())restoreLocation(m_historyIndex-1);}
void FileChooserBrowser::goForward(){if(canGoForward())restoreLocation(m_historyIndex+1);}
bool FileChooserBrowser::canCreateFolder() const {
    return m_active&&m_typeError.isEmpty()&&!m_columns.isEmpty()&&m_columns.last().model->error().isEmpty()
        &&QDir::isAbsolutePath(folderPath())&&QFileInfo(folderPath()).isDir();
}
QString FileChooserBrowser::suggestedFolderName() const {
    if(!canCreateFolder())return {};
    QString name=QStringLiteral("untitled folder");quint64 suffix=2;
    while(QFileInfo::exists(QDir(folderPath()).filePath(name))||QFileInfo(QDir(folderPath()).filePath(name)).isSymLink())
        name=QStringLiteral("untitled folder ")+QString::number(suffix++);
    return name;
}
QString FileChooserBrowser::folderNameError(const QString &name) const {
    if(name.isEmpty())return {};
    if(!canCreateFolder())return QStringLiteral("The parent folder is no longer available.");
    if(name=="."||name==".."||name.contains('/')||name.contains(QChar::Null))return QStringLiteral("Invalid folder name.");
    const QFileInfo target(QDir(folderPath()).filePath(name));
    if(target.exists()||target.isSymLink())return QStringLiteral("This name is already taken.");
    return {};
}
void FileChooserBrowser::setNewFolderError(const QString &message){
    if(m_newFolderError==message)return;m_newFolderError=message;emit newFolderErrorChanged();
}
void FileChooserBrowser::clearNewFolderError(){setNewFolderError({});}
bool FileChooserBrowser::createFolder(const QString &name,const QString &parentPath){
    clearNewFolderError();
    if(!canCreateFolder()||parentPath!=folderPath()){setNewFolderError(QStringLiteral("The parent folder is no longer available."));return false;}
    const auto validation=folderNameError(name);
    if(name.isEmpty()||!validation.isEmpty()){setNewFolderError(validation.isEmpty()?QStringLiteral("Enter a folder name."):validation);return false;}
    const auto target=QDir(parentPath).filePath(name);
    if(::mkdir(QFile::encodeName(target).constData(),0777)!=0){
        const auto code=errno;setNewFolderError(QString::fromLocal8Bit(std::strerror(code)));return false;
    }
    const auto before=location();const auto column=count()-1;
    modelAt(column)->refresh();clearOtherSelections(-1);
    branch(column,QUrl::fromLocalFile(target+'/'));append(QUrl::fromLocalFile(target));
    m_focus=m_selection=count()-1;rememberNavigation(before);
    emit metadataChanged();emit focusRequested(m_focus);return true;
}
void FileChooserBrowser::acceptSelection(){
    if(!canAccept()||m_completing)return;
    if(m_viewMode!="columns")m_listing->acceptSelection();else selectionModel()->acceptSelection();
}

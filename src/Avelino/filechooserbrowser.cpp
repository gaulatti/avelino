#include "filechooserbrowser.h"
#include <QDir>
#include <QGuiApplication>
#include <QJSEngine>
#include <QPointer>
#include <QQmlEngine>
#include <QStandardPaths>
#include <algorithm>

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
QString FileChooserBrowser::error() const {
    if(!m_typeError.isEmpty())return m_typeError;
    return m_columns.isEmpty()?QString():m_columns.last().model->error();
}
bool FileChooserBrowser::canAccept() const {
    const auto model=selectionModel();return m_active&&m_typeError.isEmpty()&&model&&model->canAccept();
}
QVariantList FileChooserBrowser::selectedUrls() const {
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
    connect(model,&FileChooserModel::result,this,[this](const QVariantMap &value){
        if(!m_active||m_completing)return;
        m_completing=true;QPointer<FileChooserBrowser> guard(this);
        emit result(value);
        if(!guard)return;
        m_completing=false;cancel();
    });
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
    m_focus=m_selection=0;emit activeChanged();emit metadataChanged();emit focusRequested(0);return true;
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
    const auto url=value["url"].toUrl();
    clearOtherSelections(column);
    if(eligible)model->select(row,modifiers);else{model->clearSelection();model->focusIndex(row);}
    trimAfter(column);branch(column,{});m_focus=m_selection=column;
    const auto selected=model->entry(row)["selected"].toBool();
    if(directory&&(!eligible||(selected&&model->selectedUrls().size()==1))){
        branch(column,url);append(url);
        if(!eligible)m_selection=column+1;
    }
    emit metadataChanged();emit focusRequested(column);
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
    auto model=modelAt(m_focus);if(!m_active||!model)return;
    clearOtherSelections(m_focus);model->selectAll();m_selection=m_focus;
    trimAfter(m_focus);branch(m_focus,{});emit metadataChanged();
}
bool FileChooserBrowser::navigatePath(const QString &path){
    if(!m_active)return false;
    trimAfter(-1);append(QUrl::fromLocalFile(path));m_focus=m_selection=0;
    emit metadataChanged();emit focusRequested(0);return modelAt(0)->error().isEmpty();
}
bool FileChooserBrowser::goUp(){
    if(!m_active||!QDir::isAbsolutePath(folderPath()))return false;
    QDir directory(folderPath());if(!directory.cdUp())return false;
    return navigatePath(directory.absolutePath());
}
void FileChooserBrowser::acceptSelection(){if(canAccept()&&!m_completing)selectionModel()->acceptSelection();}

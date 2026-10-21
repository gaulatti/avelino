#include "filechooserhost.h"

void FileChooserHost::detach(){for(auto connection:m_connections)disconnect(connection);m_connections.clear();}
void FileChooserHost::cancel(){if(m_browser)m_browser->cancel();}
FileChooserHost::~FileChooserHost(){detach();cancel();}
void FileChooserHost::setOwner(QQuickItem *owner){
    if(owner==m_owner)return;
    detach();cancel();m_owner=owner;
    if(owner)m_connections={
        connect(owner,&QQuickItem::windowChanged,this,[this]{cancel();}),
        connect(owner,&QObject::destroyed,this,[this]{cancel();m_owner=nullptr;emit ownerChanged();})};
    emit ownerChanged();
}
void FileChooserHost::setBrowser(FileChooserBrowser *browser){
    if(browser==m_browser)return;cancel();m_browser=browser;emit browserChanged();
}

#include "menuitems.h"
#include <QQuickWindow>
#include <QSet>
#include <limits>

void BleeckerMenuItem::setSystemImage(const QVariant &value) {
    if(value.isValid()&&!value.isNull()&&value.metaType()!=QMetaType::fromType<QString>())
        qFatal("MenuItem systemImage must be a string or null");
    if(value==m_image)return;m_image=value;emit systemImageChanged();
}
QVariant MenuItems::data(const QModelIndex &index,int role) const {
    if(!index.isValid()||index.row()<0||index.row()>=m_rows.size()||!m_rows[index.row()])return {};
    const auto item=m_rows[index.row()].data();
    switch(role) {
    case ItemRole:return QVariant::fromValue(item);
    case TitleRole:return item->title();
    case ImageRole:return item->systemImage().isNull() ? QStringLiteral("circle"):item->systemImage().toString();
    case DestructiveRole:return item->destructive();
    case KeyRole:return item->id();
    default:return {};
    }
}
QHash<int,QByteArray> MenuItems::roleNames() const {
    return {{ItemRole,"menuItemObject"},{TitleRole,"menuItemTitle"},{ImageRole,"menuItemSystemImage"},
        {DestructiveRole,"menuItemDestructive"},{KeyRole,"menuItemKey"}};
}
void MenuItems::setItems(const QJSValue &value){m_items=value;if(m_complete)reconcile();emit itemsChanged();}
void MenuItems::cancelPointer(QQuickItem *item) const {
    if(!item||!item->window())return;
    const auto grabbed=item->window()->mouseGrabberItem();
    if(grabbed&&(grabbed==item||item->isAncestorOf(grabbed)))grabbed->ungrabMouse();
}
void MenuItems::refresh(BleeckerMenuItem *item) {
    for(int index=0;index<m_rows.size();++index)if(m_rows[index]==item){emit dataChanged(this->index(index),this->index(index));break;}
    emit changed();
}
void MenuItems::removeDestroyed() {
    for(int index=m_rows.size()-1;index>=0;--index)if(!m_rows[index]){beginRemoveRows({},index,index);m_rows.removeAt(index);endRemoveRows();}
    emit changed();
}
void MenuItems::reconcile() {
    if(!m_items.isArray()&&m_items.toVariant().metaType()!=QMetaType::fromType<QVariantList>())qFatal("DropdownMenu items must be an array of BleeckerMenuItem objects");
    const auto length=m_items.property(QStringLiteral("length")).toUInt();
    if(length>unsigned(std::numeric_limits<int>::max()))qFatal("DropdownMenu item count exceeds Qt's index range");
    QList<QPointer<BleeckerMenuItem>> next;QSet<QString> ids;
    for(unsigned index=0;index<length;++index) {
        const auto item=qobject_cast<BleeckerMenuItem*>(m_items.property(index).toQObject());
        if(!item)qFatal("DropdownMenu items must be BleeckerMenuItem objects");
        if(ids.contains(item->id()))qFatal("DropdownMenu items require distinct identities");
        ids.insert(item->id());next.append(item);
    }
    for(const auto &connection:m_connections)disconnect(connection);m_connections.clear();
    for(int index=m_rows.size()-1;index>=0;--index)if(!m_rows[index]||!ids.contains(m_rows[index]->id())) {
        beginRemoveRows({},index,index);m_rows.removeAt(index);endRemoveRows();
    }
    for(int index=0;index<next.size();++index) {
        const auto previous=m_rows.indexOf(next[index],index);
        if(previous<0){beginInsertRows({},index,index);m_rows.insert(index,next[index]);endInsertRows();}
        else if(previous!=index){beginMoveRows({},previous,previous,{},index);m_rows.move(previous,index);endMoveRows();}
        emit dataChanged(this->index(index),this->index(index));
        const auto item=next[index].data();
        m_connections.append(connect(item,&BleeckerMenuItem::titleChanged,this,[this,item]{refresh(item);}));
        m_connections.append(connect(item,&BleeckerMenuItem::systemImageChanged,this,[this,item]{refresh(item);}));
        m_connections.append(connect(item,&BleeckerMenuItem::destructiveChanged,this,[this,item]{refresh(item);}));
        m_connections.append(connect(item,&QObject::destroyed,this,[this]{removeDestroyed();}));
    }
    emit changed();
}

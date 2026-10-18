#include "filechooserdialogbase.h"
#include <QtQuick/private/qaccessiblequickitem_p.h>
#include <QAccessible>

static_assert(QT_VERSION==QT_VERSION_CHECK(6,8,3),"Revalidate owned chooser modal accessibility before upgrading Qt");
namespace {
class DialogAccessible final : public QAccessibleQuickItem {
    FileChooserDialogBase *dialog() const {
        return object()?qobject_cast<FileChooserDialogBase*>(object()->parent()):nullptr;
    }
    QAccessibleInterface *nestedDialog()const{
        const auto owner=dialog();const auto nested=owner?owner->accessibilityDialog():nullptr;
        return nested&&nested->isVisible()?QAccessible::queryAccessibleInterface(nested->popupItem()):nullptr;
    }
public:
    using QAccessibleQuickItem::QAccessibleQuickItem;
    QAccessible::Role role() const override{return QAccessible::Dialog;}
    QAccessibleInterface *parent()const override{
        const auto owner=dialog();const auto parent=owner?owner->accessibilityParent():nullptr;
        return parent?QAccessible::queryAccessibleInterface(parent->popupItem()):QAccessibleQuickItem::parent();
    }
    int childCount()const override{return QAccessibleQuickItem::childCount()+(nestedDialog()?1:0);}
    QAccessibleInterface *child(int index)const override{
        return index==QAccessibleQuickItem::childCount()?nestedDialog():QAccessibleQuickItem::child(index);
    }
    int indexOfChild(const QAccessibleInterface *child)const override{
        const auto nested=nestedDialog();
        return child&&nested&&child->object()==nested->object()?QAccessibleQuickItem::childCount():QAccessibleQuickItem::indexOfChild(child);
    }
    QAccessibleInterface *childAt(int x,int y)const override{
        if(const auto nested=nestedDialog();nested&&nested->rect().contains(x,y)){
            if(const auto child=nested->childAt(x,y))return child;return nested;
        }
        return QAccessibleQuickItem::childAt(x,y);
    }
    QAccessibleInterface *focusChild()const override{
        if(const auto nested=nestedDialog()){if(const auto focus=nested->focusChild())return focus;return nested;}
        return QAccessibleQuickItem::focusChild();
    }
    QString text(QAccessible::Text kind) const override {
        const auto owner=dialog();
        if(owner&&kind==QAccessible::Name)return owner->title();
        return QAccessibleQuickItem::text(kind);
    }
    QAccessible::State state() const override {
        auto result=QAccessibleQuickItem::state();
        if(const auto owner=dialog())result.modal=owner->isModal();
        return result;
    }
};
QAccessibleInterface *dialogFactory(const QString &,QObject *object){
    if(auto owner=qobject_cast<FileChooserDialogBase*>(object->parent()))
        if(owner->popupItem()==object)return new DialogAccessible(owner->popupItem());
    return nullptr;
}
}
FileChooserDialogBase::FileChooserDialogBase(QObject *parent):QQuickDialog(parent){
    static const bool registered=[] {QAccessible::installFactory(dialogFactory);return true;}();
    Q_UNUSED(registered);
    connect(this,&QQuickPopup::modalChanged,this,[this]{
        QAccessible::State changed;changed.modal=true;
        QAccessibleStateChangeEvent event(popupItem(),changed);QAccessible::updateAccessibility(&event);
    });
}
void FileChooserDialogBase::setAccessibilityDialog(FileChooserDialogBase *dialog){
    if(dialog==m_dialog)return;
    for(auto ancestor=this;ancestor;ancestor=ancestor->accessibilityParent())if(ancestor==dialog)return;
    for(const auto connection:m_connections)disconnect(connection);m_connections.clear();
    if(m_dialog)m_dialog->m_parent=nullptr;
    m_dialog=dialog;
    if(dialog){
        if(auto previous=dialog->m_parent.data();previous&&previous!=this)previous->setAccessibilityDialog(nullptr);
        dialog->m_parent=this;
        m_connections={
            connect(dialog,&QQuickPopup::visibleChanged,this,[this]{QAccessibleEvent event(popupItem(),QAccessible::ObjectReorder);QAccessible::updateAccessibility(&event);}),
            connect(dialog,&QObject::destroyed,this,[this]{m_dialog=nullptr;emit accessibilityDialogChanged();})};
        QAccessibleEvent parentChanged(dialog->popupItem(),QAccessible::ParentChanged);QAccessible::updateAccessibility(&parentChanged);
    }
    emit accessibilityDialogChanged();
}

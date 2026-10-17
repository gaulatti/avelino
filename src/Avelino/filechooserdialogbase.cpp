#include "filechooserdialogbase.h"
#include <QtQuick/private/qaccessiblequickitem_p.h>
#include <QAccessible>

static_assert(QT_VERSION==QT_VERSION_CHECK(6,8,3),"Revalidate owned chooser modal accessibility before upgrading Qt");
namespace {
class DialogAccessible final : public QAccessibleQuickItem {
    FileChooserDialogBase *dialog() const {
        return object()?qobject_cast<FileChooserDialogBase*>(object()->parent()):nullptr;
    }
public:
    using QAccessibleQuickItem::QAccessibleQuickItem;
    QAccessible::Role role() const override{return QAccessible::Dialog;}
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

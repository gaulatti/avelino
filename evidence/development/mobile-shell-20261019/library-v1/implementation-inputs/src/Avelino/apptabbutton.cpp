#include "apptabbutton.h"
#include <QtQuick/private/qaccessiblequickitem_p.h>
#include <QAccessible>

static_assert(QT_VERSION==QT_VERSION_CHECK(6,8,3),"Revalidate app-tab button accessibility before upgrading Qt");
namespace {
class TabAccessible final : public QAccessibleQuickItem {
public:
    using QAccessibleQuickItem::QAccessibleQuickItem;
    QString text(QAccessible::Text kind) const override {
        const auto button=qobject_cast<AppTabButton*>(object());
        if(button &&kind==QAccessible::Name)return button->accessibleTitle();
        if(button &&kind==QAccessible::Value)return button->notificationValue();
        return QAccessibleQuickItem::text(kind);
    }
    void doAction(const QString &action) override {
        if(!state().disabled)QAccessibleQuickItem::doAction(action);
    }
};
QAccessibleInterface *tabFactory(const QString &,QObject *object) {
    if(auto button=qobject_cast<AppTabButton*>(object))return new TabAccessible(button);
    return nullptr;
}
}
AppTabButton::AppTabButton(QQuickItem *parent):QQuickButton(parent) {
    static const bool registered=[] {QAccessible::installFactory(tabFactory);return true;}();
    Q_UNUSED(registered);
}
void AppTabButton::setAccessibleTitle(const QString &value) {
    if(value==m_title)return;m_title=value;emit accessibleTitleChanged();
    QAccessibleEvent event(this,QAccessible::NameChanged);QAccessible::updateAccessibility(&event);
}
void AppTabButton::setNotificationValue(const QString &value) {
    if(value==m_value)return;m_value=value;emit notificationValueChanged();
    QAccessibleValueChangeEvent event(this,value);QAccessible::updateAccessibility(&event);
}

#include "dropdowninput.h"
#include <QPointerEvent>
#include <QtQuick/private/qquickwindow_p.h>
#include <QtQuickTemplates2/private/qquickmenuitem_p.h>

void DropdownInput::setMenu(QObject *value) {
    const auto menu=qobject_cast<QQuickMenu*>(value);
    if(value&&!menu)qFatal("DropdownInput requires a template Menu");
    if(menu==m_menu)return;
    disconnect(m_windowChange);attachWindow(nullptr);m_menu=menu;
    if(menu) {
        const auto item=menu->popupItem();
        m_windowChange=connect(item,&QQuickItem::windowChanged,this,&DropdownInput::attachWindow);
        attachWindow(item->window());
    }
    emit menuChanged();
}
void DropdownInput::attachWindow(QQuickWindow *window) {
    if(m_window)m_window->removeEventFilter(this);
    m_window=window;if(window)window->installEventFilter(this);
}
bool DropdownInput::eventFilter(QObject *object,QEvent *event) {
    if(object!=m_window||!m_menu||!m_menu->isVisible()||!event->isPointerEvent())return false;
    const auto pointer=static_cast<QPointerEvent*>(event);
    if(!pointer->isEndEvent()||pointer->pointCount()!=1||m_window==m_menu->window())return false;
    const auto viewport=m_menu->contentItem();
    const auto global=pointer->point(0).globalPosition();
    if(!viewport||!viewport->contains(viewport->mapFromGlobal(global)))return false;
    QPointer<QQuickMenuItem> target;
    for(int index=0;index<m_menu->count();++index) {
        const auto item=qobject_cast<QQuickMenuItem*>(m_menu->itemAt(index));
        if(item&&item->isVisible()&&item->isEnabled()&&item->contains(item->mapFromGlobal(global))){target=item;break;}
    }
    // Qt 6.8.3's window-menu release path queries itemAt with viewport
    // coordinates. Hit-test the actual row, including the scroll transform.
    const QPointer<QQuickWindow> window=m_window;
    if(target)target->animateClick();
    if(window)QQuickWindowPrivate::get(window)->deliveryAgent->event(event);
    return true;
}

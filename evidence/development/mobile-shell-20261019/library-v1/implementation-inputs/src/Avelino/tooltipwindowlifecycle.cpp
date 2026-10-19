#include "tooltipwindowlifecycle.h"
#include <QQuickWindow>

void TooltipWindowLifecycle::setTarget(QQuickItem *target){
    if(m_target==target)return;
    disconnect(m_windowChanged);m_target=target;
    if(target){
        m_windowChanged=connect(target,&QQuickItem::windowChanged,this,&TooltipWindowLifecycle::configure);
        configure(target->window());
    }
    emit targetChanged();
}

void TooltipWindowLifecycle::configure(QQuickWindow *window){
    // Popup content can briefly return to its owner's overlay while closing.
    // Configure only the separate tooltip window, never the caller's window.
    if(!window || (window->flags()&Qt::WindowType_Mask)!=Qt::ToolTip)return;
    // Qt 6.8.3 Wayland can retain a graphics context after the native popup
    // surface was destroyed. A remount must create resources for its new surface.
    window->setPersistentGraphics(false);
    window->setPersistentSceneGraph(false);
}

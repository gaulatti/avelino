#pragma once
#include <QObject>
#include <QPointer>
#include <QQuickItem>
#include <QQuickWindow>
#include <QtQml/qqmlregistration.h>

// A hidden Wayland popup drops its native surface. Retain the caller and popup
// objects, but let Qt rebuild the popup renderer when that surface returns.
class TooltipWindowResources : public QObject {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QQuickItem *target READ target WRITE setTarget NOTIFY targetChanged)
public:
    explicit TooltipWindowResources(QObject *parent=nullptr):QObject(parent) {}
    QQuickItem *target() const {return m_target;}
    void setTarget(QQuickItem *target) {
        if(m_target==target)return;
        QObject::disconnect(m_windowChanged);
        QObject::disconnect(m_destroyed);
        m_target=target;
        if(target) {
            m_windowChanged=connect(target,&QQuickItem::windowChanged,this,&TooltipWindowResources::configureWindow);
            m_destroyed=connect(target,&QObject::destroyed,this,[this](){m_target=nullptr;emit targetChanged();});
            configureWindow(target->window());
        }
        emit targetChanged();
    }
signals:
    void targetChanged();
private:
    void configureWindow(QQuickWindow *window) {
        if(!window || window->type()!=Qt::ToolTip)return;
        window->setPersistentSceneGraph(false);
        window->setPersistentGraphics(false);
    }
    QPointer<QQuickItem> m_target;
    QMetaObject::Connection m_windowChanged;
    QMetaObject::Connection m_destroyed;
};

#pragma once
#include <QObject>
#include <QPointer>
#include <QQuickItem>
#include <QtQml/qqmlregistration.h>

class QQuickWindow;

// Graphics resources belong to the transient tooltip surface, not its caller.
class TooltipWindowLifecycle : public QObject {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QQuickItem *target READ target WRITE setTarget NOTIFY targetChanged)
public:
    explicit TooltipWindowLifecycle(QObject *parent=nullptr):QObject(parent){}
    QQuickItem *target()const{return m_target;}
    void setTarget(QQuickItem *target);
signals:
    void targetChanged();
private:
    void configure(QQuickWindow *window);
    QPointer<QQuickItem> m_target;
    QMetaObject::Connection m_windowChanged;
};

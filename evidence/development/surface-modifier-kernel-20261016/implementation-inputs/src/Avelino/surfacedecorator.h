#pragma once
#include <QObject>
#include <QPointer>
#include <QQuickItem>
#include <QQmlComponent>
#include <QQmlParserStatus>
#include <QtQml/qqmlregistration.h>

class SurfacePartBase : public QQuickItem {
    Q_OBJECT
    QML_ELEMENT
public:
    explicit SurfacePartBase(QQuickItem *parent=nullptr):QQuickItem(parent){}
};

// Decorate caller leaves in their existing inheritance scope. Reparenting
// never changes the caller's QObject ownership or constructs it again.
class SurfaceDecorator : public QObject, public QQmlParserStatus {
    Q_OBJECT
    QML_ELEMENT
    Q_INTERFACES(QQmlParserStatus)
    Q_PROPERTY(QQuickItem *target READ target WRITE setTarget NOTIFY configurationChanged)
    Q_PROPERTY(QQmlComponent *delegate READ delegate WRITE setDelegate NOTIFY configurationChanged)
public:
    explicit SurfaceDecorator(QObject *parent=nullptr):QObject(parent){}
    QQuickItem *target() const {return m_target;}
    QQmlComponent *delegate() const {return m_delegate;}
    void setTarget(QQuickItem *item);
    void setDelegate(QQmlComponent *component);
    void classBegin() override {}
    void componentComplete() override;
signals:
    void configurationChanged();
private:
    struct Part {QPointer<QQuickItem> originalParent,wrapper,host;};
    static QQuickItem *callerOf(QQuickItem *wrapper);
    static QQuickItem *enclosingPart(QQuickItem *item);
    static QQuickItem *logicalParent(QQuickItem *item);
    void schedule();
    void rebuild();
    void removePart(int index);
    void disconnectObservers();
    QPointer<QQuickItem> m_target;
    QPointer<QQmlComponent> m_delegate;
    QList<Part> m_parts;
    QList<QMetaObject::Connection> m_connections;
    bool m_complete=false,m_queued=false,m_rebuilding=false;
};

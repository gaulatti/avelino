#pragma once
#include <QObject>
#include <QPointer>
#include <QPointF>
#include <QQuickItem>
#include <QtQml/qqmlregistration.h>

// Native rendering utility; it changes painted placement, never control layout.
class PixelAlignment : public QObject {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QQuickItem *target READ target WRITE setTarget NOTIFY targetChanged)
    Q_PROPERTY(QPointF origin READ origin WRITE setOrigin NOTIFY originChanged)
    Q_PROPERTY(QPointF offset READ offset NOTIFY offsetChanged)
    Q_PROPERTY(qreal devicePixelRatio READ devicePixelRatio NOTIFY devicePixelRatioChanged)
public:
    explicit PixelAlignment(QObject *parent = nullptr) : QObject(parent) {}
    QQuickItem *target() const { return m_target; }
    void setTarget(QQuickItem *item);
    QPointF origin() const { return m_origin; }
    void setOrigin(QPointF point);
    QPointF offset() const { return m_offset; }
    qreal devicePixelRatio() const { return m_devicePixelRatio; }
signals:
    void targetChanged();
    void originChanged();
    void offsetChanged();
    void devicePixelRatioChanged();
private:
    void attachWindow();
    void refresh();
    QPointer<QQuickItem> m_target;
    QPointF m_origin, m_offset;
    qreal m_devicePixelRatio = 1;
    QMetaObject::Connection m_windowChange, m_frame;
};

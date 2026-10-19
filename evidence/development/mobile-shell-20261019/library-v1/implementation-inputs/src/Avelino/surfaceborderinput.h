#pragma once

#include <QPainterPath>
#include <QPointer>
#include <QQuickItem>
#include <QtQml/qqmlregistration.h>

// Internal surface presentation support. The caller retains its own hit area;
// only the painted border intercepts the measured primary-button presses.
class SurfaceBorderInput : public QQuickItem {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QObject *outline READ outline WRITE setOutline NOTIFY outlineChanged)
    Q_PROPERTY(qreal strokeWidth READ strokeWidth WRITE setStrokeWidth NOTIFY strokeWidthChanged)
public:
    explicit SurfaceBorderInput(QQuickItem *parent=nullptr);
    QObject *outline() const {return m_outline;}
    qreal strokeWidth() const {return m_width;}
    void setOutline(QObject *outline);
    void setStrokeWidth(qreal width);
    bool contains(const QPointF &point) const override;
signals:
    void outlineChanged();
    void strokeWidthChanged();
protected:
    void mousePressEvent(QMouseEvent *event) override;
    void mouseReleaseEvent(QMouseEvent *event) override;
private:
    void refresh();
    QPointer<QObject> m_outline;
    QMetaObject::Connection m_changed,m_destroyed;
    QPainterPath m_region;
    QRectF m_outer,m_inner;
    bool m_rectangle=false;
    qreal m_width=1;
};

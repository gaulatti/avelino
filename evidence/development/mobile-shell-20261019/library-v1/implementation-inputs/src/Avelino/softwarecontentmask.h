#pragma once

#include <QPointer>
#include <QQuickItem>
#include <QtQml/qqmlregistration.h>

// Renderer support, not a Bleecker API. Qt's private interfaces stay in the .cpp.
class SoftwareContentMask : public QQuickItem {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QQuickItem *source READ source WRITE setSource NOTIFY sourceChanged)
    Q_PROPERTY(QObject *outline READ outline WRITE setOutline NOTIFY outlineChanged)
public:
    explicit SoftwareContentMask(QQuickItem *parent = nullptr);
    ~SoftwareContentMask() override;
    QQuickItem *source() const { return m_source; }
    QObject *outline() const { return m_outline; }
    void setSource(QQuickItem *source);
    void setOutline(QObject *outline);
signals:
    void sourceChanged();
    void outlineChanged();
protected:
    QSGNode *updatePaintNode(QSGNode *node, UpdatePaintNodeData *) override;
    void geometryChange(const QRectF &current, const QRectF &previous) override;
private:
    void attachWindow();
    void refreshRasterPhase();
    QPointer<QQuickItem> m_source;
    QPointer<QObject> m_outline;
    QMetaObject::Connection m_sourceDestroyed, m_sourceChanged, m_outlineDestroyed, m_pathChanged;
    QMetaObject::Connection m_frame;
    QPointF m_rasterPhase;
    qreal m_rasterDpr = 1;
};

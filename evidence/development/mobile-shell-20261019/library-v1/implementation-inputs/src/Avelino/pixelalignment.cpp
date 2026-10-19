#include "pixelalignment.h"
#include <QQuickWindow>
#include <cmath>

void PixelAlignment::setTarget(QQuickItem *item) {
    if (m_target == item) return;
    disconnect(m_windowChange);
    m_target = item;
    if (item) m_windowChange = connect(item, &QQuickItem::windowChanged, this, &PixelAlignment::attachWindow);
    attachWindow();
    emit targetChanged();
}

void PixelAlignment::setOrigin(QPointF point) {
    if (m_origin == point) return;
    m_origin = point;
    refresh();
    emit originChanged();
}

void PixelAlignment::attachWindow() {
    disconnect(m_frame);
    if (m_target && m_target->window())
        m_frame = connect(m_target->window(), &QQuickWindow::afterAnimating, this, &PixelAlignment::refresh);
    refresh();
}

void PixelAlignment::refresh() {
    const qreal dpr = m_target && m_target->window()
        ? m_target->window()->effectiveDevicePixelRatio() : 1;
    if (m_devicePixelRatio != dpr) {
        m_devicePixelRatio = dpr;
        emit devicePixelRatioChanged();
    }
    QPointF offset;
    if (m_target && m_target->window()) {
        const QPointF scene = m_target->mapToScene(m_origin);
        const QPointF aligned(std::round(scene.x() * dpr) / dpr, std::round(scene.y() * dpr) / dpr);
        offset = m_target->mapFromScene(aligned) - m_origin;
    }
    if (offset == m_offset) return;
    m_offset = offset;
    emit offsetChanged();
}

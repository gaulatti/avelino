#include "shellslot.h"
#include "proposalrow.h"
#include <QQmlContext>
#include <QtQml/qqml.h>
#include <QtQuick/private/qquickitem_p.h>
#include <algorithm>
#include <cmath>

ShellSlot::ShellSlot(QQuickItem *parent) : QQuickItem(parent) {
    connect(this, &QQuickItem::widthChanged, this, [this] { polish(); });
    connect(this, &QQuickItem::heightChanged, this, [this] { polish(); });
}

void ShellSlot::setSourceComponent(QQmlComponent *component) {
    if (m_component == component) return;
    disconnect(m_statusConnection);
    m_component = component;
    if (component) m_statusConnection = connect(component, &QQmlComponent::statusChanged, this, [this] {
        if (isComponentComplete()) createItem();
    });
    if (isComponentComplete()) createItem();
    emit sourceComponentChanged();
}

void ShellSlot::componentComplete() {
    QQuickItem::componentComplete();
    createItem();
}

void ShellSlot::createItem() {
    for (const auto &connection : m_connections) disconnect(connection);
    m_connections.clear();
    if (m_item) delete m_item;
    m_item = nullptr;
    m_fixedWidth = m_fixedHeight = 0;
    if (m_component) {
        if (m_component->isError()) qFatal("Shell slot component failed to load");
        if (!m_component->isReady()) { emit itemChanged(); layout(); return; }
        auto context = m_component->creationContext();
        if (!context) context = qmlContext(this);
        if (!context) qFatal("Shell slot requires a QML creation context");
        const QPointer<ShellSlot> self(this);
        const QPointer<QQmlComponent> component(m_component);
        QObject *object = component->beginCreate(context);
        auto child = qobject_cast<QQuickItem *>(object);
        if (!child) qFatal("Shell slot content must be a visual Item");
        child->setParent(this);
        child->setParentItem(this);
        m_item = child;
        component->completeCreate();
        if (!self) return;
        if (!m_item) { emit itemChanged(); layout(); return; }
        m_fixedWidth = m_item->width(); m_fixedHeight = m_item->height();
        m_explicitWidth = QQuickItemPrivate::get(m_item)->widthValid();
        m_explicitHeight = QQuickItemPrivate::get(m_item)->heightValid();
        auto changed = [this] { if (!m_layingOut) polish(); };
        m_connections.append(connect(m_item, &QQuickItem::implicitWidthChanged, this, changed));
        m_connections.append(connect(m_item, &QQuickItem::implicitHeightChanged, this, changed));
        m_connections.append(connect(m_item, &QQuickItem::widthChanged, this, [this] {
            if (!m_layingOut && m_item) {
                m_fixedWidth = m_item->width(); m_explicitWidth = QQuickItemPrivate::get(m_item)->widthValid(); polish();
            }
        }));
        m_connections.append(connect(m_item, &QQuickItem::heightChanged, this, [this] {
            if (!m_layingOut && m_item) {
                m_fixedHeight = m_item->height(); m_explicitHeight = QQuickItemPrivate::get(m_item)->heightValid(); polish();
            }
        }));
        auto hint = qobject_cast<BleeckerLayout *>(qmlAttachedPropertiesObject<BleeckerLayout>(m_item, true));
        m_connections.append(connect(hint, &BleeckerLayout::metricsChanged, this, changed));
        m_connections.append(connect(m_item, &QObject::destroyed, this, [this] { m_item = nullptr; emit itemChanged(); polish(); }));
    }
    emit itemChanged();
    layout();
}

void ShellSlot::layout() {
    if (m_layingOut || !isComponentComplete()) return;
    m_layingOut = true;
    const QPointer<ShellSlot> self(this);
    const QPointer<QQuickItem> child(m_item);
    qreal ideal = 0, lower = 0, naturalHeight = 0, minimumHeight = 0;
    bool fillsHeight = false;
    if (child) {
        auto hint = qobject_cast<BleeckerLayout *>(qmlAttachedPropertiesObject<BleeckerLayout>(child, true));
        ideal = m_explicitWidth ? m_fixedWidth : hint->idealWidth >= 0 ? hint->idealWidth
            : child->implicitWidth() > 0 ? child->implicitWidth() : m_fixedWidth;
        lower = m_explicitWidth ? m_fixedWidth : hint->minimumWidth >= 0 ? hint->minimumWidth : ideal;
        if (!std::isfinite(ideal) || !std::isfinite(lower) || lower < 0 || ideal < lower)
            qFatal("Shell slot requires finite widths with 0 <= minimum <= ideal");
        hint->propose(m_explicitWidth ? m_fixedWidth : width());
        if (!self) return;
        if (child) {
            const auto fitted = hint->fillsWidth ? std::max(lower, width())
                : lower == ideal ? ideal : std::clamp(child->implicitWidth(), lower, ideal);
            if (!m_explicitWidth)
                child->setWidth(fitted);
            if (!self) return;
            if (child) {
                naturalHeight = m_explicitHeight ? m_fixedHeight
                    : child->implicitHeight() > 0 ? child->implicitHeight() : m_fixedHeight;
                fillsHeight = hint->fillsHeight && !m_explicitHeight;
                minimumHeight = fillsHeight ? 0 : naturalHeight;
                if (!std::isfinite(naturalHeight) || naturalHeight < 0)
                    qFatal("Shell slot requires finite nonnegative height");
                if (fillsHeight || !m_explicitHeight)
                    child->setHeight(fillsHeight ? std::max(qreal(0), height()) : naturalHeight);
                if (!self) return;
                if (child) child->setPosition(QPointF((width() - child->width()) / 2, (height() - child->height()) / 2));
                if (!self) return;
            }
        }
    }
    setImplicitSize(ideal, naturalHeight);
    if (!self) return;
    const bool changed = m_minimumWidth != lower || m_minimumHeight != minimumHeight || m_fillsHeight != fillsHeight;
    m_minimumWidth = lower; m_minimumHeight = minimumHeight; m_fillsHeight = fillsHeight;
    m_layingOut = false;
    if (changed) emit metricsChanged();
}

#include "softwarecontentmask.h"

#include <QPainter>
#include <QQuickWindow>
#include <QSGRendererInterface>
#include <QSGSimpleTextureNode>
#include <QtQuick/private/qquickitem_p.h>
#include <QtQuick/private/qquickpath_p.h>
#include <QtQuick/private/qquickshadereffectsource_p.h>
#include <QtQuick/private/qsgabstractsoftwarerenderer_p.h>
#include <QtQuick/private/qsgsoftwarecontext_p.h>
#include <QtQuick/private/qsgsoftwarerenderablenode_p.h>
#include <cmath>
#include <memory>

namespace {
// Use Qt's normal software node dispatcher with an explicitly alpha-capable
// target. Qt 6.8.3's QPixmap layer treats any opaque subregion as full coverage,
// so its RGB target loses transparent holes around otherwise opaque children.
class AlphaRenderer final : public QSGAbstractSoftwareRenderer {
public:
    explicit AlphaRenderer(QSGRenderContext *context) : QSGAbstractSoftwareRenderer(context) {}
    void render() override {}
    void paint(QImage &image, const QRect &projection, QPointF phase) {
        setBackgroundRect(projection, 1);
        setBackgroundColor(Qt::transparent);
        buildRenderList();
        // Offset this renderer's placement records, not Qt's scene-graph nodes.
        // The texture's matching negative origin preserves scene placement while
        // keeping every intermediate texel on a physical pixel. Restore records
        // after painting so subsequent source updates start in local coordinates.
        struct Placement { QSGSoftwareRenderableNode *node; QTransform transform; QRegion clip; };
        QVector<Placement> placements;
        for (auto *node : renderableNodes()) {
            placements.push_back({node, node->transform(), node->clipRegion()});
            node->setTransform(node->transform() * QTransform::fromTranslate(phase.x(), phase.y()));
            if (!node->clipRegion().isEmpty())
                node->setClipRegion(node->clipRegion().translated(qRound(phase.x()), qRound(phase.y())));
        }
        // Each output image starts transparent; Qt's default optimization assumes
        // a retained backing store. Redraw unchanged islands as well as edits.
        markDirty();
        optimizeRenderList();
        QPainter painter(&image);
        painter.setRenderHint(QPainter::Antialiasing);
        painter.setWindow(projection);
        auto *software = static_cast<QSGSoftwareRenderContext *>(context());
        QPainter *previous = software->m_activePainter;
        software->m_activePainter = &painter;
        renderNodes(&painter);
        software->m_activePainter = previous;
        for (const auto &placement : placements) {
            placement.node->setTransform(placement.transform);
            if (!placement.clip.isEmpty()) placement.node->setClipRegion(placement.clip);
        }
    }
};

class MaskNode final : public QObject, public QSGSimpleTextureNode {
public:
    MaskNode(QQuickWindow *window, QSGRenderContext *context)
        : m_window(window), m_renderer(std::make_unique<AlphaRenderer>(context)) {
        setFlag(UsePreprocess);
        setOwnsTexture(true);
        QImage empty(1, 1, QImage::Format_ARGB32_Premultiplied);
        empty.fill(Qt::transparent);
        setTexture(m_window->createTextureFromImage(empty));
        connect(m_renderer.get(), &QSGRenderer::sceneGraphChanged, this, [this] {
            if (m_capturing) return;
            m_dirty = true;
            markDirty(DirtyMaterial);
            QMetaObject::invokeMethod(m_window, "update", Qt::QueuedConnection);
        }, Qt::DirectConnection);
    }

    void synchronize(QSGNode *source, const QPainterPath &path, const QRectF &bounds, qreal dpr, QPointF phase) {
        if (m_source != source) {
            m_source = source;
            m_dirty = true;
        }
        if (m_path != path || m_bounds != bounds || m_dpr != dpr || m_phase != phase) {
            m_path = path;
            m_bounds = bounds;
            m_dpr = dpr;
            m_phase = phase;
            const QSize size(qMax(1, qCeil(bounds.width()*dpr+phase.x()*dpr)),
                             qMax(1, qCeil(bounds.height()*dpr+phase.y()*dpr)));
            // A transparent gutter keeps fractional extents from stretching the
            // child raster. The outer item's geometry and clip stay unchanged.
            setRect(QRectF(-phase, QSizeF(size)/dpr));
            m_mask = {};
            m_dirty = true;
        }
    }

    void preprocess() override {
        // Empty or newly mounted items may not have an effect root during sync.
        // Follow the borrowed scene-graph node here, after all items synchronize;
        // later child creation already schedules a window frame.
        QSGNode *source = m_source;
        while (source->firstChild() && source->type() != QSGNode::RootNodeType) source = source->firstChild();
        auto *root = source->type() == QSGNode::RootNodeType ? static_cast<QSGRootNode *>(source) : nullptr;
        if (root != m_renderer->rootNode()) {
            m_capturing = true;
            m_renderer->setRootNode(root);
            m_capturing = false;
            m_dirty = true;
        }
        if (!m_dirty) return;
        if (!root) {
            QImage empty(1, 1, QImage::Format_ARGB32_Premultiplied);
            empty.fill(Qt::transparent);
            setTexture(m_window->createTextureFromImage(empty));
            markDirty(DirtyMaterial);
            m_dirty = false;
            return;
        }
        m_capturing = true;
        const QSize size(qRound(rect().width()*m_dpr), qRound(rect().height()*m_dpr));
        QImage image(size, QImage::Format_ARGB32_Premultiplied);
        image.setDevicePixelRatio(m_dpr);
        image.fill(Qt::transparent);
        const QRect projection(QPoint(0,0), size);
        m_renderer->setDevicePixelRatio(m_dpr);
        m_renderer->setDeviceRect(size);
        m_renderer->setViewportRect(size);
        m_renderer->setClearColor(Qt::transparent);
        // The effect root and every native child stay owned by Qt. As in Qt's
        // layer renderer, invalidate cached matrices before and after rendering
        // the borrowed root with a separate projection. Never reparent nodes.
        root->markDirty(QSGNode::DirtyForceUpdate);
        m_renderer->nodeChanged(root, QSGNode::DirtyForceUpdate);
        m_renderer->renderScene();
        m_renderer->paint(image, projection, m_phase);
        root->markDirty(QSGNode::DirtyForceUpdate);
        m_capturing = false;
        m_dirty = false;
        image.setDevicePixelRatio(1);
        if (m_mask.size() != size) {
            m_mask = QImage(size, QImage::Format_ARGB32_Premultiplied);
            m_mask.fill(Qt::transparent);
            QPainter painter(&m_mask);
            painter.setRenderHint(QPainter::Antialiasing);
            painter.scale(m_dpr, m_dpr);
            painter.translate(m_phase);
            painter.fillPath(m_path, Qt::white);
        }
        {
            QPainter painter(&image);
            painter.setCompositionMode(QPainter::CompositionMode_DestinationIn);
            painter.drawImage(QPointF(0, 0), m_mask);
        }
        // setTexture deletes the preceding owned texture.
        setTexture(m_window->createTextureFromImage(image));
        markDirty(DirtyMaterial);
    }
private:
    QQuickWindow *m_window;
    QSGNode *m_source = nullptr;
    std::unique_ptr<AlphaRenderer> m_renderer;
    QPainterPath m_path;
    QRectF m_bounds;
    QPointF m_phase;
    QImage m_mask;
    qreal m_dpr = 1;
    bool m_dirty = true;
    bool m_capturing = false;
};
}

SoftwareContentMask::SoftwareContentMask(QQuickItem *parent) : QQuickItem(parent) {
    setFlag(ItemHasContents);
    connect(this, &QQuickItem::visibleChanged, this, &SoftwareContentMask::update);
    connect(this, &QQuickItem::windowChanged, this, &SoftwareContentMask::attachWindow);
    attachWindow();
}

SoftwareContentMask::~SoftwareContentMask() {
    if (m_source) QQuickItemPrivate::get(m_source)->derefFromEffectItem(false);
}

void SoftwareContentMask::attachWindow() {
    disconnect(m_frame);
    if (window()) m_frame = connect(window(), &QQuickWindow::afterAnimating, this, &SoftwareContentMask::refreshRasterPhase);
    refreshRasterPhase();
}

void SoftwareContentMask::refreshRasterPhase() {
    if (!window()) return;
    const qreal dpr = window()->effectiveDevicePixelRatio();
    const QPointF origin = mapToScene(QPointF(0,0))*dpr;
    const QPointF phase((origin.x()-std::floor(origin.x()))/dpr,
                        (origin.y()-std::floor(origin.y()))/dpr);
    if (phase == m_rasterPhase && dpr == m_rasterDpr) return;
    m_rasterPhase = phase;
    m_rasterDpr = dpr;
    update();
}

void SoftwareContentMask::setSource(QQuickItem *source) {
    if (m_source == source) return;
    disconnect(m_sourceDestroyed);
    disconnect(m_sourceChanged);
    auto *effect = qobject_cast<QQuickShaderEffectSource *>(source);
    if (source && !effect) qFatal("SoftwareContentMask source must be ShaderEffectSource");
    if (m_source) QQuickItemPrivate::get(m_source)->derefFromEffectItem(false);
    m_source = source;
    if (effect) {
        // Match Qt's texture consumers: an invisible ShaderEffectSource must
        // still synchronize when its enclosing component is first revealed.
        QQuickItemPrivate::get(effect)->refFromEffectItem(false);
        m_sourceDestroyed = connect(effect, &QObject::destroyed, this, [this] {
            emit sourceChanged();
            update();
        });
        m_sourceChanged = connect(effect, &QQuickShaderEffectSource::sourceItemChanged, this, &SoftwareContentMask::update);
    }
    emit sourceChanged();
    update();
}

void SoftwareContentMask::setOutline(QObject *outline) {
    if (m_outline == outline) return;
    auto *path = qobject_cast<QQuickPath *>(outline);
    if (outline && !path) qFatal("SoftwareContentMask outline must be a Qt Quick path");
    disconnect(m_pathChanged);
    disconnect(m_outlineDestroyed);
    m_outline = outline;
    if (path) {
        m_pathChanged = connect(path, &QQuickPath::changed, this, &SoftwareContentMask::update);
        m_outlineDestroyed = connect(path, &QObject::destroyed, this, [this] {
            emit outlineChanged();
            update();
        });
    }
    emit outlineChanged();
    update();
}

void SoftwareContentMask::geometryChange(const QRectF &current, const QRectF &previous) {
    QQuickItem::geometryChange(current, previous);
    if (current.size() != previous.size()) update();
}

QSGNode *SoftwareContentMask::updatePaintNode(QSGNode *old, UpdatePaintNodeData *) {
    auto *effect = qobject_cast<QQuickShaderEffectSource *>(m_source);
    if (!isVisible() || !effect || !effect->sourceItem() || !m_outline || width() <= 0 || height() <= 0) {
        delete old;
        return nullptr;
    }
    if (window()->rendererInterface()->graphicsApi() != QSGRendererInterface::Software)
        qFatal("Visible SoftwareContentMask requires the Qt software renderer");
    auto *node = static_cast<MaskNode *>(old);
    if (!node) node = new MaskNode(window(), QQuickItemPrivate::get(this)->sceneGraphRenderContext());
    node->synchronize(QQuickItemPrivate::get(effect->sourceItem())->itemNode(), qobject_cast<QQuickPath *>(m_outline)->path(), boundingRect(), window()->effectiveDevicePixelRatio(), m_rasterPhase);
    return node;
}

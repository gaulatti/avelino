#pragma once
#include <QImage>
#include <QQuickItem>
#include <QQuickWindow>
#include <QSGSimpleTextureNode>
#include <QtQml/qqmlregistration.h>
#include <cmath>

// Caller-fixture paint, separate from the grid. Round the two scene edges
// independently, including fills narrower than one pixel. The alpha-capable
// texture keeps software background culling from erasing fractional edges.
class MediaTileFill : public QQuickItem {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QColor color READ color WRITE setColor NOTIFY colorChanged)
public:
    explicit MediaTileFill(QQuickItem *parent=nullptr):QQuickItem(parent) {
        setFlag(ItemHasContents);
        connect(this,&QQuickItem::windowChanged,this,[this](QQuickWindow *window){
            disconnect(m_frame);
            if(window)m_frame=connect(window,&QQuickWindow::afterAnimating,this,&MediaTileFill::refresh);
            watchAncestors();refresh();update();
        });
        connect(this,&QQuickItem::parentChanged,this,[this]{watchAncestors();refresh();});
    }
    ~MediaTileFill() override {
        disconnect(m_frame);for(const auto &connection:m_ancestors)disconnect(connection);
        QObject::disconnect(this,nullptr,this,nullptr);
    }
    QColor color() const{return m_color;}
    void setColor(const QColor &value){if(value==m_color)return;m_color=value;m_colorDirty=true;update();emit colorChanged();}
signals:
    void colorChanged();
protected:
    void geometryChange(const QRectF &next,const QRectF &previous) override {
        QQuickItem::geometryChange(next,previous);refresh();
    }
    QSGNode *updatePaintNode(QSGNode *old,UpdatePaintNodeData*) override {
        const auto bounds=alignedBounds();
        if(bounds.isEmpty()){delete old;return nullptr;}
        auto node=static_cast<QSGSimpleTextureNode*>(old);
        if(!node){node=new QSGSimpleTextureNode;node->setOwnsTexture(true);node->setFiltering(QSGTexture::Nearest);m_colorDirty=true;}
        if(m_colorDirty){
            QImage image(1,1,QImage::Format_ARGB32_Premultiplied);image.fill(m_color);
            auto texture=window()->createTextureFromImage(image);
            if(!texture)qFatal("MediaTileFill texture creation failed");
            node->setTexture(texture);m_colorDirty=false;
        }
        node->setRect(bounds);return node;
    }
private:
    QRectF alignedBounds() const {
        if(!window()||width()<=0||height()<=0)return {};
        const auto dpr=window()->effectiveDevicePixelRatio();
        const auto a=mapToScene(QPointF(0,0)),b=mapToScene(QPointF(width(),height()));
        const auto snap=[dpr](QPointF value){return QPointF(std::round(value.x()*dpr)/dpr,std::round(value.y()*dpr)/dpr);};
        return QRectF(mapFromScene(snap(a)),mapFromScene(snap(b)));
    }
    void refresh(){
        const auto bounds=alignedBounds();
        if(bounds==m_requestedBounds)return;
        m_requestedBounds=bounds;update();
    }
    void watchAncestors(){
        for(const auto &connection:m_ancestors)disconnect(connection);m_ancestors.clear();
        for(auto item=parentItem();item;item=item->parentItem()){
            m_ancestors.append(connect(item,&QQuickItem::xChanged,this,&MediaTileFill::refresh));
            m_ancestors.append(connect(item,&QQuickItem::yChanged,this,&MediaTileFill::refresh));
            m_ancestors.append(connect(item,&QQuickItem::widthChanged,this,&MediaTileFill::refresh));
            m_ancestors.append(connect(item,&QQuickItem::heightChanged,this,&MediaTileFill::refresh));
            m_ancestors.append(connect(item,&QQuickItem::scaleChanged,this,&MediaTileFill::refresh));
            m_ancestors.append(connect(item,&QQuickItem::rotationChanged,this,&MediaTileFill::refresh));
            m_ancestors.append(connect(item,&QQuickItem::transformOriginChanged,this,&MediaTileFill::refresh));
            m_ancestors.append(connect(item,&QQuickItem::parentChanged,this,[this]{watchAncestors();refresh();}));
        }
    }
    QColor m_color=Qt::transparent;
    QRectF m_requestedBounds;
    bool m_colorDirty=true;
    QMetaObject::Connection m_frame;
    QList<QMetaObject::Connection> m_ancestors;
};

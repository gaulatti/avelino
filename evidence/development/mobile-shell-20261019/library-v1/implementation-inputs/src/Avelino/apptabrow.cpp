#include "apptabrow.h"
#include "proposalrow.h"
#include <QtQuick/private/qquickitem_p.h>
#include <QQuickWindow>
#include <QPointer>
#include <QMetaMethod>
#include <algorithm>
#include <cmath>

AppTabRow::AppTabRow(QQuickItem *parent):QQuickItem(parent){connect(this,&QQuickItem::childrenChanged,this,&AppTabRow::childrenUpdated);}
void AppTabRow::componentComplete(){QQuickItem::componentComplete();childrenUpdated();layout();}
void AppTabRow::setProposedWidth(qreal value) {
    if(!std::isfinite(value) ||(value<0 &&value!=-1))qFatal("AppTabBar width proposal must be finite, nonnegative or -1");
    if(value==m_proposal)return;m_proposal=value;emit configurationChanged();polish();
}
void AppTabRow::setMirrored(bool value){if(value==m_mirrored)return;m_mirrored=value;emit configurationChanged();polish();}
void AppTabRow::childrenUpdated() {
    for(const auto &c:m_connections)disconnect(c);m_connections.clear();
    for(auto child:childItems()) {
        auto update=[this]{if(!m_layingOut)polish();};
        m_connections.append(connect(child,&QQuickItem::implicitWidthChanged,this,update));
        m_connections.append(connect(child,&QQuickItem::implicitHeightChanged,this,update));
        for(const auto name:{"minimumWidthChanged()","naturalWidthChanged()"}) {
            const auto signal=child->metaObject()->indexOfSignal(name);
            if(signal>=0)m_connections.append(connect(child,child->metaObject()->method(signal),this,metaObject()->method(metaObject()->indexOfMethod("layout()"))));
        }
    }
    polish();
}
void AppTabRow::layout() {
    if(m_layingOut ||!isComponentComplete())return;m_layingOut=true;
    struct Cell {QQuickItem *item; qreal minimum,ideal,width;QRectF previous;};
    QList<Cell> cells;const QPointer<QQuickItem> grabber=window() ? window()->mouseGrabberItem():nullptr;
    qreal minimum=0,natural=0;
    for(auto child:childItems()) {
        if(child->inherits("QQuickRepeater"))continue;
        const auto lower=child->property("minimumWidth").toDouble(),ideal=child->property("naturalWidth").toDouble();
        if(!std::isfinite(lower) ||!std::isfinite(ideal) ||lower<0 ||ideal<lower)qFatal("AppTabBar content requires finite 0 <= minimum <= ideal widths");
        cells.append({child,lower,ideal,0,QRectF(child->position(),child->size())});minimum+=lower;natural+=ideal;
    }
    if(m_minimum!=minimum ||m_natural!=natural){m_minimum=minimum;m_natural=natural;emit metricsChanged();}
    QList<int> order;for(int i=0;i<cells.size();++i)order.append(i);
    std::stable_sort(order.begin(),order.end(),[&](int a,int b){return cells[a].minimum>cells[b].minimum;});
    auto attached=m_owner ? qobject_cast<BleeckerLayout*>(qmlAttachedPropertiesObject<BleeckerLayout>(m_owner,true)):nullptr;
    const bool intrinsic=m_owner &&!QQuickItemPrivate::get(m_owner)->widthValid() &&attached->proposedWidth()<0;
    const auto offer=intrinsic ? -1:m_proposal;
    qreal remaining=offer<0 ? natural:std::max(minimum,offer);
    for(int at=0;at<order.size();++at) {
        auto &c=cells[order[at]];
        c.width=offer<0 ? c.ideal:std::max(c.minimum,remaining/(order.size()-at));remaining-=c.width;
        c.item->setWidth(c.width);
    }
    qreal width=0,height=0;
    for(auto &c:cells) {
        const auto h=c.item->implicitHeight();
        const auto icon=c.item->property("iconItem").value<QQuickItem*>();
        if(!std::isfinite(h)||h<0||!icon||!std::isfinite(icon->implicitWidth())||!std::isfinite(icon->implicitHeight())||icon->implicitWidth()<0||icon->implicitHeight()<0)
            qFatal("AppTabBar icon and label dimensions must be finite and nonnegative");
        width+=c.width;c.item->setHeight(h);height=std::max(height,h);
    }
    qreal x=m_mirrored ? width:0;
    for(auto &c:cells) {
        if(m_mirrored)x-=c.width;
        c.item->setPosition(QPointF(x,(height-c.item->height())/2));if(!m_mirrored)x+=c.width;
        if(grabber &&(grabber==c.item ||c.item->isAncestorOf(grabber)) &&c.previous!=QRectF(c.item->position(),c.item->size()))grabber->ungrabMouse();
    }
    setImplicitSize(width,height);setSize(QSizeF(width,height));m_layingOut=false;
}

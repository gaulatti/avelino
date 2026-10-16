#include "proposaloverlay.h"
#include "proposalcolumn.h"
#include <QtQml/qqml.h>
#include <algorithm>
#include <cmath>
#include <functional>

ProposalOverlay::ProposalOverlay(QQuickItem *parent):QQuickItem(parent) {
    connect(this,&QQuickItem::childrenChanged,this,&ProposalOverlay::childrenUpdated);
    connect(this,&QQuickItem::widthChanged,this,[this]{if(!m_layingOut)polish();});
    connect(this,&QQuickItem::heightChanged,this,[this]{if(!m_layingOut)polish();});
    connect(this,&QQuickItem::parentChanged,this,[this]{polish();});
}
void ProposalOverlay::setMaximumWidth(qreal value) {
    if(!std::isfinite(value)||(value<0&&value!=-1))qFatal("Overlay maximum width must be nonnegative or -1");
    if(value==m_maximum)return;m_maximum=value;emit configurationChanged();polish();
}
void ProposalOverlay::componentComplete() {QQuickItem::componentComplete();childrenUpdated();layout();}
void ProposalOverlay::childrenUpdated() {
    for(const auto &connection:m_connections)disconnect(connection);m_connections.clear();
    std::function<void(QQuickItem*)> watch=[&](QQuickItem *child) {
        auto changed=[this]{if(!m_layingOut)polish();};
        m_connections.append(connect(child,&QQuickItem::implicitWidthChanged,this,changed));
        m_connections.append(connect(child,&QQuickItem::implicitHeightChanged,this,changed));
        m_connections.append(connect(child,&QQuickItem::widthChanged,this,changed));
        m_connections.append(connect(child,&QQuickItem::heightChanged,this,changed));
        m_connections.append(connect(child,&QQuickItem::baselineOffsetChanged,this,changed));
        if(auto row=qobject_cast<ProposalRow*>(child))m_connections.append(connect(row,&ProposalRow::baselineMetricsChanged,this,changed));
        if(auto column=qobject_cast<ProposalColumn*>(child))m_connections.append(connect(column,&ProposalColumn::baselineMetricsChanged,this,changed));
        if(auto overlay=qobject_cast<ProposalOverlay*>(child))m_connections.append(connect(overlay,&ProposalOverlay::baselineMetricsChanged,this,changed));
        auto hint=qobject_cast<BleeckerLayout*>(qmlAttachedPropertiesObject<BleeckerLayout>(child,true));
        m_connections.append(connect(hint,&BleeckerLayout::metricsChanged,this,changed));
        m_connections.append(connect(hint,&BleeckerLayout::structureChanged,this,&ProposalOverlay::childrenUpdated));
        if(hint->flattenChildren) {
            m_connections.append(connect(child,&QQuickItem::childrenChanged,this,&ProposalOverlay::childrenUpdated));
            for(auto nested:child->childItems())watch(nested);
        }
    };
    for(auto child:childItems())watch(child);
    emit itemsChanged();polish();
}
QList<QQuickItem*> ProposalOverlay::layoutItems() const {
    QList<QQuickItem*> items;
    std::function<void(QQuickItem*)> append=[&](QQuickItem *child) {
        if(child->inherits("QQuickRepeater"))return;
        auto hint=qobject_cast<BleeckerLayout*>(qmlAttachedPropertiesObject<BleeckerLayout>(child,true));
        if(!hint->participates)return;
        if(hint->flattenChildren)for(auto nested:child->childItems())append(nested);
        else items.append(child);
    };
    for(auto child:childItems())append(child);
    return items;
}
QQuickItem *ProposalOverlay::itemAt(int index) const {
    const auto items=layoutItems();return index>=0 && index<items.size() ? items[index]:nullptr;
}
bool ProposalOverlay::delegated() const {
    auto current=const_cast<QQuickItem*>(static_cast<const QQuickItem*>(this));
    while(current) {
        auto hint=qobject_cast<BleeckerLayout*>(qmlAttachedPropertiesObject<BleeckerLayout>(current,true));
        if(!hint->flattenChildren)return false;
        auto parent=current->parentItem();
        if(qobject_cast<ProposalRow*>(parent)||qobject_cast<ProposalColumn*>(parent)||qobject_cast<ProposalOverlay*>(parent))return true;
        current=parent;
    }
    return false;
}
void ProposalOverlay::layout() {
    if(m_layingOut||!isComponentComplete())return;
    m_layingOut=true;
    const bool external=delegated();
    struct Cell {QQuickItem *item;qreal width,height;BleeckerLayout::Baseline baseline;};
    QList<Cell> cells;
    qreal natural=0,minimum=0,fitted=0,height=0;
    for(auto child:layoutItems()) {
        if(auto row=qobject_cast<ProposalRow*>(child))row->layout();
        if(auto column=qobject_cast<ProposalColumn*>(child))column->layout();
        if(auto overlay=qobject_cast<ProposalOverlay*>(child))overlay->layout();
        auto hint=qobject_cast<BleeckerLayout*>(qmlAttachedPropertiesObject<BleeckerLayout>(child,true));
        const auto ideal=hint->idealWidth>=0 ? hint->idealWidth:child->implicitWidth()>0 ? child->implicitWidth():child->width();
        const auto lower=hint->minimumWidth>=0 ? hint->minimumWidth:ideal;
        if(!std::isfinite(ideal)||!std::isfinite(lower)||ideal<0||lower<0||lower>ideal)
            qFatal("Overlay content requires finite widths with 0 <= minimum <= ideal");
        natural=std::max(natural,ideal);minimum=std::max(minimum,lower);
        if(!external) {
            hint->propose(m_maximum);
            if(auto row=qobject_cast<ProposalRow*>(child))row->layout();
            if(auto column=qobject_cast<ProposalColumn*>(child))column->layout();
            if(auto overlay=qobject_cast<ProposalOverlay*>(child))overlay->layout();
        }
        const auto width=lower==ideal ? ideal:std::clamp(child->implicitWidth(),lower,ideal);
        if(!external) {
            child->setWidth(width);
            if(auto column=qobject_cast<ProposalColumn*>(child))column->layout();
        }
        const bool measured=hint->minimumWidth>=0||hint->idealWidth>=0;
        const auto childHeight=measured||child->implicitHeight()>0 ? child->implicitHeight():child->height();
        if(!std::isfinite(childHeight)||childHeight<0)qFatal("Overlay content requires finite nonnegative height");
        if(!external)child->setHeight(childHeight);
        cells.append({child,width,childHeight,BleeckerLayout::baselineFor(child)});
        fitted=std::max(fitted,width);height=std::max(height,childHeight);
    }
    setImplicitSize(fitted,height);
    qreal firstBaseline=height;
    bool hasBaseline=false;
    for(const auto &cell:cells) {
        const qreal y=(this->height()-cell.height)/2;
        if(!external)cell.item->setPosition(QPointF((width()-cell.width)/2,y));
        if(cell.baseline.containsText) {
            const auto baseline=(height-cell.height)/2+cell.baseline.offset;
            firstBaseline=hasBaseline ? std::min(firstBaseline,baseline):baseline;hasBaseline=true;
        }
    }
    setBaselineOffset(firstBaseline);
    if(m_containsTextBaseline!=hasBaseline){m_containsTextBaseline=hasBaseline;emit baselineMetricsChanged();}
    if(m_natural!=natural||m_minimum!=minimum){m_natural=natural;m_minimum=minimum;emit metricsChanged();}
    m_layingOut=false;
}

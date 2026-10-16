#include "proposalcolumn.h"
#include "proposaloverlay.h"
#include <QtQml/qqml.h>
#include <QPointer>
#include <algorithm>
#include <cmath>
#include <functional>

ProposalColumn::ProposalColumn(QQuickItem *parent):QQuickItem(parent) {
    connect(this,&QQuickItem::childrenChanged,this,&ProposalColumn::childrenUpdated);
    connect(this,&QQuickItem::widthChanged,this,[this]{if(!m_layingOut)polish();});
}
void ProposalColumn::setMaximumWidth(qreal value) {
    if(!std::isfinite(value)||(value<0&&value!=-1))qFatal("Column maximum width must be nonnegative or -1");
    if(value==m_maximum)return;m_maximum=value;emit configurationChanged();polish();
}
void ProposalColumn::setPadding(qreal value) {
    if(!std::isfinite(value)||value<0)qFatal("Column padding must be finite and nonnegative");
    if(value==m_padding)return;m_padding=value;emit configurationChanged();polish();
}
void ProposalColumn::setSpacing(qreal value) {
    if(!std::isfinite(value)||value<0)qFatal("Column spacing must be finite and nonnegative");
    if(value==m_spacing)return;m_spacing=value;emit configurationChanged();polish();
}
void ProposalColumn::componentComplete() {QQuickItem::componentComplete();childrenUpdated();layout();}
void ProposalColumn::childrenUpdated() {
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
        m_connections.append(connect(hint,&BleeckerLayout::structureChanged,this,&ProposalColumn::childrenUpdated));
        if(hint->flattenChildren) {
            m_connections.append(connect(child,&QQuickItem::childrenChanged,this,&ProposalColumn::childrenUpdated));
            for(auto nested:child->childItems())watch(nested);
        }
    };
    for(auto child:childItems())watch(child);
    polish();
}
QList<QQuickItem*> ProposalColumn::layoutItems() const {
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
void ProposalColumn::layout() {
    if(m_layingOut||!isComponentComplete())return;
    m_layingOut=true;
    QList<QPointer<QQuickItem>> children;
    struct Cell {QPointer<QQuickItem> item;qreal width,y;};
    QList<Cell> cells;
    for(auto child:layoutItems())children.append(child);
    qreal natural=0,minimum=0,fitted=0,height=0;
    const auto offered=m_maximum<0 ? -1:std::max(qreal(0),m_maximum-2*m_padding);
    for(const auto &child:children) {
        if(!child)continue;
        auto hint=qobject_cast<BleeckerLayout*>(qmlAttachedPropertiesObject<BleeckerLayout>(child,true));
        const auto ideal=hint->idealWidth>=0 ? hint->idealWidth:child->implicitWidth()>0 ? child->implicitWidth():child->width();
        const auto lower=hint->minimumWidth>=0 ? hint->minimumWidth:ideal;
        if(!std::isfinite(ideal)||!std::isfinite(lower)||ideal<0||lower<0||lower>ideal)
            qFatal("Column content requires finite widths with 0 <= minimum <= ideal");
        natural=std::max(natural,ideal+2*m_padding);minimum=std::max(minimum,lower+2*m_padding);
        hint->propose(offered);
        if(!child)continue;
        if(auto row=qobject_cast<ProposalRow*>(child.data()))row->layout();
        if(auto column=qobject_cast<ProposalColumn*>(child.data()))column->layout();
        if(auto overlay=qobject_cast<ProposalOverlay*>(child.data()))overlay->layout();
        if(!child)continue;
        const auto width=hint->fillsWidth && offered>=0 ? std::max(lower,offered)
            :lower==ideal ? ideal:std::clamp(child->implicitWidth(),lower,ideal);
        child->setWidth(width);
        if(!child)continue;
        if(auto column=qobject_cast<ProposalColumn*>(child.data()))column->layout();
        const bool measured=hint->minimumWidth>=0 || hint->idealWidth>=0;
        const auto childHeight=measured || child->implicitHeight()>0 ? child->implicitHeight():child->height();
        if(!std::isfinite(childHeight)||childHeight<0)qFatal("Column content requires finite nonnegative height");
        child->setHeight(childHeight);
        if(!cells.isEmpty())height+=m_spacing;
        cells.append({child,width,height+m_padding});
        fitted=std::max(fitted,width+2*m_padding);height+=childHeight+2*m_padding;
    }
    setImplicitSize(fitted,height);
    const auto available=width();
    qreal implicitBaseline=height;
    bool hasBaseline=false;
    for(const auto &cell:cells)if(cell.item) {
        cell.item->setPosition(QPointF((available-cell.width)/2,cell.y));
        const auto baseline=BleeckerLayout::baselineFor(cell.item);
        if(baseline.containsText) {
            implicitBaseline=hasBaseline ? std::min(implicitBaseline,cell.y+baseline.offset):cell.y+baseline.offset;
            hasBaseline=true;
        }
    }
    setBaselineOffset(implicitBaseline);
    if(m_containsTextBaseline!=hasBaseline){m_containsTextBaseline=hasBaseline;emit baselineMetricsChanged();}
    if(m_natural!=natural||m_minimum!=minimum){m_natural=natural;m_minimum=minimum;emit metricsChanged();}
    m_layingOut=false;
}

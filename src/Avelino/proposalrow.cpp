#include "proposalrow.h"
#include <QtQml/qqml.h>
#include <QQuickWindow>
#include <QPointer>
#include <algorithm>
#include <cmath>
#include <functional>

ProposalRow::ProposalRow(QQuickItem *parent):QQuickItem(parent) {
    m_metrics.setTarget(this);
    connect(&m_metrics,&PixelAlignment::devicePixelRatioChanged,this,[this]{polish();});
    connect(this,&QQuickItem::childrenChanged,this,&ProposalRow::childrenUpdated);
}
void ProposalRow::setSpacing(qreal value) {
    if(!std::isfinite(value)||value<0)qFatal("Row spacing must be finite and nonnegative");
    if(value==m_spacing)return;m_spacing=value;emit configurationChanged();polish();
}
void ProposalRow::setMaximumWidth(qreal value) {
    if(!std::isfinite(value)||(value<0&&value!=-1))qFatal("Row maximum width must be nonnegative or -1");
    if(value==m_maximum)return;m_maximum=value;emit configurationChanged();polish();
}
void ProposalRow::setMirrored(bool value) {
    if(value==m_mirrored)return;m_mirrored=value;emit configurationChanged();polish();
}
void ProposalRow::setVerticalAlignment(Qt::Alignment value) {
    if(value!=Qt::AlignTop && value!=Qt::AlignVCenter && value!=Qt::AlignBottom)qFatal("Row vertical alignment must be top, center or bottom");
    if(value==m_verticalAlignment)return;m_verticalAlignment=value;emit configurationChanged();polish();
}
void ProposalRow::componentComplete() {QQuickItem::componentComplete();childrenUpdated();layout();}
void ProposalRow::childrenUpdated() {
    for(const auto &c:m_connections)disconnect(c);m_connections.clear();
    std::function<void(QQuickItem*)> watch=[&](QQuickItem *child) {
        auto changed=[this]{if(!m_layingOut)polish();};
        m_connections.append(connect(child,&QQuickItem::implicitWidthChanged,this,changed));
        m_connections.append(connect(child,&QQuickItem::implicitHeightChanged,this,changed));
        m_connections.append(connect(child,&QQuickItem::widthChanged,this,changed));
        m_connections.append(connect(child,&QQuickItem::heightChanged,this,changed));
        auto hint=qobject_cast<BleeckerLayout*>(qmlAttachedPropertiesObject<BleeckerLayout>(child,true));
        m_connections.append(connect(hint,&BleeckerLayout::metricsChanged,this,changed));
        m_connections.append(connect(hint,&BleeckerLayout::structureChanged,this,&ProposalRow::childrenUpdated));
        if(hint->flattenChildren) {
            m_connections.append(connect(child,&QQuickItem::childrenChanged,this,&ProposalRow::childrenUpdated));
            for(auto nested:child->childItems())watch(nested);
        }
    };
    for(auto child:childItems())watch(child);
    polish();
}
QList<QQuickItem*> ProposalRow::layoutItems() const {
    QList<QQuickItem*> items;
    std::function<void(QQuickItem*)> append=[&](QQuickItem *child) {
        // A Repeater's delegates are independent siblings. Hidden items retain
        // layout; conditional content uses the explicit participates hint.
        if(child->inherits("QQuickRepeater"))return;
        auto hint=qobject_cast<BleeckerLayout*>(qmlAttachedPropertiesObject<BleeckerLayout>(child,true));
        if(!hint->participates)return;
        if(hint->flattenChildren) {
            for(auto nested:child->childItems())append(nested);
        }else items.append(child);
    };
    for(auto child:childItems())append(child);
    return items;
}
void ProposalRow::layout() {
    if(m_layingOut||!isComponentComplete())return;
    m_layingOut=true;
    struct Cell {QQuickItem *item;BleeckerLayout *hint;qreal ideal,minimum,width=0,height=0;QRectF before;};
    const QPointer<QQuickItem> grabber=window() ? window()->mouseGrabberItem():nullptr;
    QList<Cell> cells;
    qreal ideal=0,minimum=0;
    for(auto child:layoutItems()) {
        if(auto row=qobject_cast<ProposalRow*>(child))row->layout();
        auto hint=qobject_cast<BleeckerLayout*>(qmlAttachedPropertiesObject<BleeckerLayout>(child,true));
        const auto natural=hint->idealWidth>=0 ? hint->idealWidth:child->implicitWidth()>0 ? child->implicitWidth():child->width();
        const auto lower=hint->minimumWidth>=0 ? hint->minimumWidth:natural;
        if(!std::isfinite(natural)||!std::isfinite(lower)||natural<0||lower<0||lower>natural)
            qFatal("Content layout requires finite widths with 0 <= minimum <= ideal");
        cells.append({child,hint,natural,lower,0,0,QRectF(child->position(),child->size())});ideal+=natural;minimum+=lower;
    }
    const qreal gaps=std::max(qsizetype(0),cells.size()-1)*m_spacing;
    ideal+=gaps;minimum+=gaps;
    if(m_natural!=ideal||m_minimum!=minimum){m_natural=ideal;m_minimum=minimum;emit metricsChanged();}
    QList<int> order;int fills=0;
    qreal remaining=m_maximum<0 ? ideal-gaps:std::max(qreal(0),m_maximum-gaps);
    for(int i=0;i<cells.size();++i) {
        if(cells[i].hint->fillsWidth){remaining-=cells[i].minimum;++fills;cells[i].width=cells[i].minimum;}
        else order.append(i);
    }
    std::stable_sort(order.begin(),order.end(),[&cells](int a,int b){return cells[a].ideal-cells[a].minimum<cells[b].ideal-cells[b].minimum;});
    for(int at=0;at<order.size();++at) {
        auto &c=cells[order[at]];
        const auto offered=m_maximum<0 ? c.ideal:std::clamp(remaining/(order.size()-at),c.minimum,c.ideal);
        c.hint->propose(m_maximum<0 ? -1:offered);
        if(auto row=qobject_cast<ProposalRow*>(c.item))row->layout();
        c.width=c.minimum==c.ideal ? c.ideal:std::clamp(c.item->implicitWidth(),c.minimum,c.ideal);
        c.item->setWidth(c.width);remaining-=c.width;
    }
    qreal total=gaps,height=0;
    for(auto &c:cells) {
        if(c.hint->fillsWidth)c.width+=std::max(qreal(0),remaining)/fills;
        const bool measured=c.hint->idealWidth>=0 || c.hint->minimumWidth>=0;
        c.height=measured || c.item->implicitHeight()>0 ? c.item->implicitHeight():c.item->height();
        c.item->setWidth(c.width);c.item->setHeight(c.height);total+=c.width;height=std::max(height,c.height);
    }
    qreal x=m_mirrored ? total:0;
    for(auto &c:cells) {
        if(m_mirrored)x-=c.width;
        c.item->setPosition(QPointF(x,m_verticalAlignment==Qt::AlignTop ? 0:m_verticalAlignment==Qt::AlignBottom ? height-c.height:(height-c.height)/2));
        if(m_cancelPointerOnReflow && grabber && (c.item==grabber || c.item->isAncestorOf(grabber))
            && c.before!=QRectF(c.item->position(),c.item->size()))grabber->ungrabMouse();
        x+=m_mirrored ? -m_spacing:c.width+m_spacing;
    }
    setImplicitSize(total,height);
    m_layingOut=false;
}

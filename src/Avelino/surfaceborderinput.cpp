#include "surfaceborderinput.h"
#include <QMouseEvent>
#include <QPainterPathStroker>
#include <QtQuick/private/qquickpath_p.h>
#include <cmath>

SurfaceBorderInput::SurfaceBorderInput(QQuickItem *parent):QQuickItem(parent) {
    setAcceptedMouseButtons(Qt::LeftButton);
}
void SurfaceBorderInput::setOutline(QObject *outline) {
    if(m_outline==outline)return;
    auto *path=qobject_cast<QQuickPath*>(outline);
    if(outline &&!path)qFatal("Surface border input requires a Qt Quick path");
    disconnect(m_changed);disconnect(m_destroyed);m_outline=outline;
    if(path) {
        m_changed=connect(path,&QQuickPath::changed,this,&SurfaceBorderInput::refresh);
        m_destroyed=connect(path,&QObject::destroyed,this,[this]{m_outline=nullptr;m_region={};m_rectangle=false;emit outlineChanged();});
    }
    refresh();emit outlineChanged();
}
void SurfaceBorderInput::setStrokeWidth(qreal width) {
    if(!std::isfinite(width)||width<0)qFatal("Surface border input width must be finite and nonnegative");
    if(width==m_width)return;
    m_width=width;refresh();emit strokeWidthChanged();
}
void SurfaceBorderInput::refresh() {
    m_region={};
    m_rectangle=false;
    if(!m_outline ||m_width==0)return;
    const auto path=qobject_cast<QQuickPath*>(m_outline)->path();
    const auto bounds=path.boundingRect();
    // A square inset path has an exact half-open rectangular ring. Avoid the
    // stroker's tiny numerical corner fragments for this analytic case.
    QPointF first,previous;qreal twiceArea=0;int moves=0;bool rectangle=!path.isEmpty();
    for(int i=0;i<path.elementCount() &&rectangle;++i) {
        const auto e=path.elementAt(i);const QPointF point(e.x,e.y);
        if(e.type==QPainterPath::MoveToElement){rectangle=++moves==1;first=previous=point;continue;}
        if(e.type!=QPainterPath::LineToElement){rectangle=false;break;}
        rectangle=(previous.x()==point.x() &&(point.x()==bounds.left() ||point.x()==bounds.right()))
            ||(previous.y()==point.y() &&(point.y()==bounds.top() ||point.y()==bounds.bottom()));
        twiceArea+=previous.x()*point.y()-point.x()*previous.y();previous=point;
    }
    m_rectangle=rectangle &&moves==1 &&previous==first &&std::abs(twiceArea)==2*bounds.width()*bounds.height();
    if(m_rectangle){m_outer=bounds.adjusted(-m_width/2,-m_width/2,m_width/2,m_width/2);m_inner=bounds.adjusted(m_width/2,m_width/2,-m_width/2,-m_width/2);}
    QPainterPathStroker stroker;stroker.setWidth(m_width);stroker.setJoinStyle(Qt::MiterJoin);
    m_region=stroker.createStroke(path);
}
bool SurfaceBorderInput::contains(const QPointF &point) const {
    if(point.x()<0 ||point.y()<0 ||point.x()>=width() ||point.y()>=height())return false;
    if(m_rectangle) {
        const auto inside=[&](const QRectF &r){return r.width()>0 &&r.height()>0 &&point.x()>=r.left() &&point.x()<r.right() &&point.y()>=r.top() &&point.y()<r.bottom();};
        return inside(m_outer)&&!inside(m_inner);
    }
    return m_region.contains(point);
}
void SurfaceBorderInput::mousePressEvent(QMouseEvent *event) {event->accept();}
void SurfaceBorderInput::mouseReleaseEvent(QMouseEvent *event) {event->accept();}

#include "chartrenderer.h"
#include <QFontDatabase>
#include <QFontMetricsF>
#include <QJSValue>
#include <QLocale>
#include <QPainter>
#include <QQuickWindow>
#include <algorithm>
#include <cmath>
#include <limits>
#include <QMap>

namespace {
constexpr double pi=3.141592653589793238462643383279502884;
struct Scale {
    double low=0,high=0,step=0;bool valid=false;
    double position(double value,double extent) const {
        if(!valid || !std::isfinite(value))return std::numeric_limits<double>::quiet_NaN();
        if(low==high)return extent/2;
        const double span=high-low,reciprocal=1/span;
        // The source normalizes through a precomputed Double reciprocal.
        // Keep each operation's rounding: direct division and wider arithmetic
        // change ordinary mark positions. Extreme finite domains retain a
        // wider ratio when Double subtraction/reciprocation cannot represent it.
        if(std::isfinite(span) &&std::isfinite(reciprocal) &&reciprocal>0)
            return ((value-low)*reciprocal)*extent;
        return double((static_cast<long double>(value)-low)/(static_cast<long double>(high)-low)*extent);
    }
    double value(double position,double extent,bool reversed) const {
        if(!valid ||extent<=0)return std::numeric_limits<double>::quiet_NaN();
        if(low==high)return low;
        const double normalized=(position-(reversed ? extent:0))/(reversed ? -extent:extent);
        const double span=high-low,reciprocal=1/span;
        if(std::isfinite(span) &&std::isfinite(reciprocal) &&reciprocal>0)
            return normalized/reciprocal+low;
        return double(static_cast<long double>(normalized)*(static_cast<long double>(high)-low)+low);
    }
    QVariantList domain() const{return valid ? QVariantList{low,high}:QVariantList{};}
    QList<double> ticks() const {
        QList<double> result;
        if(!valid || step<=0 || low==high)return result;
        const auto count=static_cast<int>(std::min(20.L,std::round((static_cast<long double>(high)-low)/step)));
        for(int i=0;i<=count;++i)result.append(i==count ? high:low+i*step);
        return result;
    }
};
Scale scaleFor(const QList<double> &values,bool nice) {
    Scale scale;
    for(double value:values)if(std::isfinite(value)) {
        scale.low=std::min(scale.low,value);scale.high=std::max(scale.high,value);scale.valid=true;
    }
    if(!nice || !scale.valid || scale.low==scale.high)return scale;
    const long double raw=(static_cast<long double>(scale.high)-scale.low)/4;
    const long double power=std::pow(10.L,std::floor(std::log10(raw)));
    const long double fraction=raw/power;
    long double factor=10;
    for(int candidate:{1,2,5,10})if(fraction<=candidate*(1+1e-12L)){factor=candidate;break;}
    const double step=static_cast<double>(power*factor);
    if(!std::isfinite(step) ||step<=0)return scale;
    const double low=std::floor(scale.low/step)*step,high=std::ceil(scale.high/step)*step;
    // Preserve finite input handling even when extending a domain would
    // overflow Double. Those domains use a wider ratio rather than inf-inf.
    if(std::isfinite(low) &&std::isfinite(high)) {
        scale.step=step;scale.low=low;scale.high=high;
    }
    return scale;
}
QVariant unpack(const QVariant &value) {
    return value.metaType()==QMetaType::fromType<QJSValue>() ? value.value<QJSValue>().toVariant():value;
}
QVariantList array(const QVariant &value,const char *name) {
    const auto raw=unpack(value);
    if(raw.metaType()!=QMetaType::fromType<QVariantList>())qFatal("Chart %s must be an array",name);
    return raw.toList();
}
bool numeric(const QVariant &value) {
    const auto type=value.metaType().id();
    return type==QMetaType::Double ||type==QMetaType::Float ||type==QMetaType::Int ||type==QMetaType::UInt ||type==QMetaType::LongLong ||type==QMetaType::ULongLong;
}
QString text(const QVariantMap &row,const QString &key,const QString &fallback) {
    if(!row.contains(key))return fallback;
    if(row[key].metaType()!=QMetaType::fromType<QString>())qFatal("Chart point %s must be a string",qPrintable(key));
    return row[key].toString();
}
QVariant number(double value) {return std::isfinite(value) ? QVariant(value):QVariant();}
QVariantMap rectangle(QRectF r) {return {{"x",r.x()},{"y",r.y()},{"width",r.width()},{"height",r.height()}};}
QVariantList pair(double a,double b) {return {number(a),number(b)};}
QFont chartFont(int pixels) {
    auto font=QFontDatabase::systemFont(QFontDatabase::GeneralFont);font.setPixelSize(pixels);font.setWeight(QFont::Normal);
    font.setHintingPreference(QFont::PreferNoHinting);return font;
}
QString formatted(double value,double step,const QLocale &locale) {
    if(std::isnan(value))return QStringLiteral("NaN");
    if(std::isinf(value))return value>0 ? QStringLiteral("Infinity"):QStringLiteral("-Infinity");
    if(value==0)value=0;
    if(std::abs(value)>=1e15 ||(value!=0 &&std::abs(value)<1e-8))return locale.toString(value,'g',6);
    const int digits=step>0 ? std::clamp(-int(std::floor(std::log10(step))),0,12):6;
    auto result=locale.toString(value,'f',digits);
    if(step==0 &&result.contains(locale.decimalPoint())) {
        while(result.endsWith(locale.zeroDigit()))result.chop(locale.zeroDigit().size());
        if(result.endsWith(locale.decimalPoint()))result.chop(locale.decimalPoint().size());
    }
    return result;
}
QPainterPath curve(const QList<QPointF> &input) {
    QPainterPath result;
    if(input.size()<2)return result;
    result.moveTo(input.first());
    // Centripetal Catmull-Rom (alpha 1/2), converted to cubic Bezier tangents.
    // Mathematical formulation: cemyuksel.com/research/catmullrom_param/
    for(int i=0;i+1<input.size();++i) {
        const auto p1=input[i],p2=input[i+1];
        if(p1==p2)continue;
        const auto p0=i>0 ? input[i-1]:2*p1-p2;
        const auto p3=i+2<input.size() ? input[i+2]:2*p2-p1;
        auto distance=[](QPointF a,QPointF b){return std::sqrt(std::hypot(a.x()-b.x(),a.y()-b.y()));};
        const double a=std::max(1e-10,distance(p0,p1)),b=std::max(1e-10,distance(p1,p2)),c=std::max(1e-10,distance(p2,p3));
        const auto m1=b*((p1-p0)/a-(p2-p0)/(a+b)+(p2-p1)/b);
        const auto m2=b*((p2-p1)/b-(p3-p1)/(b+c)+(p3-p2)/c);
        result.cubicTo(p1+m1/3,p2-m2/3,p2);
    }
    return result;
}
QPainterPath barPath(QRectF rect,bool negative) {
    QPainterPath p;if(rect.isEmpty())return p;
    const double radius=std::min({4.,rect.width()/2,rect.height()});
    p.moveTo(rect.left(),rect.bottom());p.lineTo(rect.left(),rect.top()+radius);
    p.quadTo(rect.topLeft(),rect.topLeft()+QPointF(radius,0));p.lineTo(rect.topRight()-QPointF(radius,0));
    p.quadTo(rect.topRight(),rect.topRight()+QPointF(0,radius));p.lineTo(rect.bottomRight());p.closeSubpath();
    if(negative){QTransform flip;flip.translate(0,rect.top()+rect.bottom());flip.scale(1,-1);p=flip.map(p);}
    return p;
}
QPainterPath sectorPath(QPointF center,double outer,double inner,double start,double end) {
    QPainterPath path;if(outer<=0 ||inner>=outer ||end<=start)return path;
    const double span=end-start;
    if(span>=2*pi-1e-10){path.addEllipse(center,outer,outer);if(inner>0)path.addEllipse(center,inner,inner);return path;}
    // Source angularInset(1) leaves a one-point inset on each radial edge.
    // Fillet centers lie on the offset outer/inner circles, not on a widened
    // wedge stroke; widening a wedge incorrectly fills the center gaps.
    constexpr double gap=1;
    const double half=std::min(span/2,pi/2),sine=std::sin(half);
    if(outer*sine<=gap)return path;
    double radius=std::min({3.,(outer-inner)/2,(outer*sine-gap)/(1+sine)});
    if(inner>0 &&sine<1){if(inner*sine<=gap)return path;radius=std::min(radius,(inner*sine-gap)/(1-sine));}
    radius=std::max(0.,radius);
    const double offset=std::asin(std::clamp((gap+radius)/(outer-radius),-1.,1.));
    auto unit=[](double angle){return QPointF(std::cos(angle),std::sin(angle));};
    auto arc=[&](QPointF c,double r,double a,double b){if(r>0)path.arcTo(QRectF(c-QPointF(r,r),QSizeF(2*r,2*r)),-a*180/pi,-(b-a)*180/pi);};
    const QPointF startInside(-std::sin(start),std::cos(start)),endOutside(-std::sin(end),std::cos(end));
    const QPointF first=center+(outer-radius)*unit(start+offset),last=center+(outer-radius)*unit(end-offset);
    path.moveTo(first-radius*startInside);arc(first,radius,start-pi/2,start+offset);
    arc(center,outer,start+offset,end-offset);arc(last,radius,end-offset,end+pi/2);
    if(inner>0) {
        const double delta=std::asin(std::clamp((gap+radius)/(inner+radius),-1.,1.));
        const QPointF a=center+(inner+radius)*unit(end-delta),b=center+(inner+radius)*unit(start+delta);
        path.lineTo(a+radius*endOutside);arc(a,radius,end+pi/2,end-delta+pi);
        arc(center,inner,end-delta,start+delta);arc(b,radius,start+delta+pi,start+3*pi/2);
    }else {
        const double distance=gap/std::max(1e-12,std::sin(span/2));
        path.lineTo(distance<outer ? center+distance*unit((start+end)/2):center);
    }
    path.closeSubpath();return path;
}
}

ChartRenderer::ChartRenderer(QQuickItem *parent):QQuickPaintedItem(parent) {
    setOpaquePainting(false);setAntialiasing(true);setSmooth(false);
    connect(this,&QQuickItem::windowChanged,this,&ChartRenderer::attachWindow);
}
ChartRenderer::~ChartRenderer(){disconnect(m_frameConnection);disconnect(this,nullptr,this,nullptr);}
void ChartRenderer::componentComplete(){QQuickPaintedItem::componentComplete();m_complete=true;relayout();}
void ChartRenderer::attachWindow(QQuickWindow *window) {
    disconnect(m_frameConnection);
    if(window)m_frameConnection=connect(window,&QQuickWindow::afterAnimating,this,&ChartRenderer::refreshSceneOrigin);
    refreshSceneOrigin();
}
void ChartRenderer::refreshSceneOrigin() {
    if(!m_complete ||!window())return;
    const auto origin=mapToScene(-m_bounds.topLeft());
    if(origin==m_sceneOrigin)return;
    m_sceneOrigin=origin;relayout();
}
#define CHART_SETTER(Type,Name,Member) void ChartRenderer::set##Name(Type value){if(Member==value)return;Member=value;emit configurationChanged();relayout();}
CHART_SETTER(const QString &,Kind,m_kind)
CHART_SETTER(const QVariant &,Points,m_points)
CHART_SETTER(const QVariant &,Values,m_values)
CHART_SETTER(bool,Area,m_area)
CHART_SETTER(QSizeF,ChartSize,m_size)
CHART_SETTER(bool,Mirrored,m_mirrored)
CHART_SETTER(QColor,LabelColor,m_labelColor)
CHART_SETTER(QColor,GridColor,m_gridColor)
CHART_SETTER(const QVariantList &,Colors,m_colors)
CHART_SETTER(const QString &,LocaleName,m_locale)
CHART_SETTER(qreal,PixelRatio,m_pixelRatio)
#undef CHART_SETTER
void ChartRenderer::setInnerRadius(qreal value){if(m_innerRadius==value ||(std::isnan(m_innerRadius)&&std::isnan(value)))return;m_innerRadius=value;emit configurationChanged();relayout();}

void ChartRenderer::relayout() {
    if(!m_complete)return;
    if(!QStringList{"line","bar","pie","scatter","sparkline"}.contains(m_kind))qFatal("Unsupported chart kind");
    if(!std::isfinite(m_size.width()) ||!std::isfinite(m_size.height()) ||m_size.width()<1 ||m_size.height()<1)qFatal("Chart layout size must be finite and at least one");
    if(!std::isfinite(m_pixelRatio)||m_pixelRatio<=0)qFatal("Chart pixel ratio must be finite and positive");
    const bool spark=m_kind=="sparkline",pie=m_kind=="pie",bar=m_kind=="bar";
    QList<Point> points;QStringList series,categories;
    const auto raw=array(spark ? m_values:m_points,spark ? "values":"points");
    for(int index=0;index<raw.size();++index) {
        Point point;
        if(spark){if(!numeric(raw[index]))qFatal("Sparkline values must be numeric");point={QString::number(index),"Value","",double(index),raw[index].toDouble()};}
        else {
            const auto value=unpack(raw[index]);if(value.metaType()!=QMetaType::fromType<QVariantMap>())qFatal("Chart points must be objects");const auto row=value.toMap();
            if(!numeric(row.value("x")) ||!numeric(row.value("y")))qFatal("Chart point x and y must be numeric");
            point={text(row,"id",QString::number(index)),text(row,"series","Value"),text(row,"label",""),row["x"].toDouble(),row["y"].toDouble()};
        }
        // Preserve rows even when a channel is non-finite: native legends and
        // independent valid axis channels do not become an empty chart.
        if(!series.contains(point.series))series.append(point.series);
        if(bar &&!categories.contains(point.label))categories.append(point.label);
        point.color=series.indexOf(point.series);points.append(point);
    }
    QList<QColor> palette;
    for(const auto &value:m_colors){const auto color=value.value<QColor>();if(!color.isValid())qFatal("Chart palette entries must be colors");palette.append(color);}
    if(palette.isEmpty())qFatal("Chart palette cannot be empty");
    const int count=pie ? 5:m_kind=="scatter" ? 3:4;while(palette.size()>count)palette.removeLast();
    const QLocale locale(m_locale);const QFont axisFont=chartFont(10),legendFont=chartFont(11);
    const QFontMetricsF axisMetrics(axisFont),legendMetrics(legendFont);
    QList<double> xs,ys;QMap<QString,QPair<long double,long double>> stacks;
    long double negativeAngles=0,positiveAngles=0;
    for(auto &point:points) {
        if(std::isfinite(point.x))xs.append(point.x);
        if(!std::isfinite(point.y)){point.start=point.end=std::numeric_limits<double>::quiet_NaN();continue;}
        if(pie) {
            point.start=double(point.y<0 ? negativeAngles:positiveAngles);
            (point.y<0 ? negativeAngles:positiveAngles)+=point.y;
            point.end=double(point.y<0 ? negativeAngles:positiveAngles);
        } else if(bar ||m_area) {
            if(!bar &&!std::isfinite(point.x))continue;
            const QString key=bar ? point.label:QString::number(point.x,'g',17);auto &stack=stacks[key];auto &sum=point.y<0 ? stack.first:stack.second;
            point.start=double(sum);sum+=point.y;point.end=double(sum);ys.append(point.end);ys.append(point.start);
        }else{point.start=0;point.end=point.y;ys.append(point.y);}
    }
    const Scale xScale=scaleFor(xs,!spark),yScale=scaleFor(ys,!spark);
    const bool xAxis=!pie &&!spark &&(bar ? !categories.isEmpty():xScale.valid &&xScale.low!=xScale.high);
    const bool yAxis=!pie &&!spark &&yScale.valid &&yScale.low!=yScale.high;
    QList<QVariantMap> legend;double cursor=0;int legendRows=series.isEmpty() ? 0:1;
    for(int i=0;i<series.size();++i) {
        // Native legend entries keep their natural unbreakable label even
        // when the chart's offered frame is narrower than a single entry.
        const QString label=series[i];
        const double width=13+legendMetrics.horizontalAdvance(label);
        if(cursor>0 &&cursor+width>m_size.width()){++legendRows;cursor=0;}
        legend.append({{"series",series[i]},{"text",label},{"x",cursor},{"row",legendRows-1},{"width",width},{"color",palette[i%palette.size()].name(QColor::HexArgb)}});cursor+=width+10;
    }
    // The integer-scale source probes retain a five-point gap plus one
    // physical pixel. Fractional-scale native font layout remains unresolved.
    const double legendPadding=5+1/m_pixelRatio;
    const double legendHeight=legendRows ? 12.3203125+legendPadding+22*(legendRows-1):0;
    double axisWidth=0;
    if(yAxis)for(double tick:yScale.ticks())axisWidth=std::max(axisWidth,std::ceil(axisMetrics.horizontalAdvance(formatted(tick,yScale.step,locale)))+7);
    m_plot=QRectF(m_mirrored ? axisWidth:0,0,std::max(1.,m_size.width()-axisWidth),std::max(1.,m_size.height()-legendHeight-(xAxis ? 18:0)));
    auto categoryRange=[&](const Point &p){
        const double band=m_plot.width()/std::max(qsizetype(1),categories.size());
        const double lower=categories.indexOf(p.label)*band;
        return QPair<double,double>{lower,lower+band};
    };
    auto px=[&](const Point &p){
        const auto range=bar ? categoryRange(p):QPair<double,double>{};
        const double value=bar ? (range.first+range.second)/2:xScale.position(p.x,m_plot.width());
        return m_plot.left()+(m_mirrored ? m_plot.width()-value:value);
    };
    auto py=[&](double y){return m_plot.bottom()-yScale.position(y,m_plot.height());};
    const QColor foreground=m_labelColor,grid=m_gridColor;
    m_draws.clear();m_accessibility.clear();QVariantList pointRows,legendReport;
    auto draw=[&](QPainterPath path,QColor color,double stroke=0,bool gradient=false){if(!path.isEmpty())m_draws.append({path,color,stroke,gradient});};
    auto line=[&](QPointF a,QPointF b,QColor color,double width,bool dashed=false){QPainterPath path;path.moveTo(a);path.lineTo(b);m_draws.append({path,color,width,false,dashed});};
    auto label=[&](const QString &text,const QFont &font,QPointF origin,QColor color){QPainterPath path;path.addText(origin,font,text);draw(path,color);};
    if(xAxis) {
        if(bar)for(int i=0;i<categories.size();++i) {
            Point p;p.label=categories[i];const double x=px(p);const double band=m_plot.width()/std::max(qsizetype(1),categories.size());
            const auto text=axisMetrics.elidedText(categories[i],Qt::ElideRight,std::max(0.,band-8));
            line({x-band/2,m_plot.top()},{x-band/2,m_plot.bottom()+4},grid,0.5,true);
            label(text,axisFont,{x-axisMetrics.horizontalAdvance(text)/2,m_plot.bottom()+5+axisMetrics.ascent()},foreground);
        }else for(double tick:xScale.ticks()) {
            Point p;p.x=tick;const double x=px(p);const auto text=formatted(tick,xScale.step,locale);
            line({x,m_plot.top()},{x,m_plot.bottom()+4},grid,0.5,true);
            const double width=axisMetrics.horizontalAdvance(text);double left=x-width/2;
            if(tick==xScale.low)left=m_mirrored ? x-width-4:x+4;
            if(tick==xScale.high)left=m_mirrored ? x+4:x-width-4;
            label(text,axisFont,{left,m_plot.bottom()+5+axisMetrics.ascent()},foreground);
        }
    }
    if(yAxis)for(double tick:yScale.ticks()) {
        const double y=py(tick);const auto text=formatted(tick,yScale.step,locale);
        line({m_plot.left(),y},{m_plot.right(),y},grid,0.5);
        label(text,axisFont,{m_mirrored ? m_plot.left()-4-axisMetrics.horizontalAdvance(text):m_plot.right()+4,y+(axisMetrics.ascent()-axisMetrics.descent())/2},foreground);
    }
    // Areas retain signed stacking by x/series, while line strokes use the raw
    // point y. This is intentionally independent of the categorical bar stack.
    if(m_area &&!pie &&!bar)for(const auto &name:series) {
        QList<QPointF> top,bottom;
        for(const auto &point:points)if(point.series==name &&std::isfinite(point.x)&&std::isfinite(point.end)){top.append({px(point),py(point.end)});bottom.prepend({px(point),py(point.start)});}
        auto path=curve(top);auto lower=curve(bottom);if(!path.isEmpty()&&!lower.isEmpty()){path.lineTo(bottom.first());path.connectPath(lower);path.closeSubpath();draw(path,palette.first(),0,true);}
    }
    if(m_kind=="line" ||spark)for(const auto &name:series) {
        QList<QPointF> segment;
        for(const auto &point:points)if(point.series==name) {
            if(std::isfinite(point.x)&&std::isfinite(point.y))segment.append({px(point),py(point.y)});
            else{draw(curve(segment),palette[series.indexOf(name)%palette.size()],2);segment.clear();}
        }
        draw(curve(segment),palette[series.indexOf(name)%palette.size()],2);
    }
    const long double angleExtent=positiveAngles-negativeAngles;
    for(const auto &point:points) {
        QRectF bounds;bool rendered=false;QVariantMap observed{{"id",point.id},{"series",point.series},{"label",point.label},{"x",number(point.x)},{"y",number(point.y)}};
        if(!pie) {
            observed.insert("xPosition",number(px(point)-m_plot.left()));
            observed.insert("yPosition",number(yScale.valid &&std::isfinite(point.y) ? m_plot.height()-yScale.position(point.y,m_plot.height()):std::numeric_limits<double>::quiet_NaN()));
            if(bar){const auto range=categoryRange(point);observed.insert("xRange",m_mirrored ? pair(m_plot.width()-range.second,m_plot.width()-range.first):pair(range.first,range.second));}
            else observed.insert("xRange",pair(px(point)-m_plot.left(),px(point)-m_plot.left()));
            const double y=yScale.valid &&std::isfinite(point.y) ? m_plot.height()-yScale.position(point.y,m_plot.height()):std::numeric_limits<double>::quiet_NaN();observed.insert("yRange",pair(y,y));
        }
        if(bar &&std::isfinite(point.y)&&std::isfinite(point.end) &&yScale.valid) {
            const double width=m_plot.width()/std::max(qsizetype(1),categories.size())*0.7,a=py(point.start),b=py(point.end);bounds={px(point)-width/2,std::min(a,b),width,std::abs(a-b)};
            draw(barPath(bounds,point.y<0),palette[point.color%palette.size()]);rendered=!bounds.isEmpty();
        }else if(m_kind=="scatter" &&std::isfinite(point.x)&&std::isfinite(point.y)) {
            constexpr double radius=3.989422804014327;bounds={QPointF(px(point)-radius,py(point.y)-radius),QSizeF(2*radius,2*radius)};QPainterPath path;path.addEllipse(bounds);draw(path,palette[point.color%palette.size()]);rendered=true;
        }else if(pie &&angleExtent>0 &&std::isfinite(point.start)&&std::isfinite(point.end)&&!std::isnan(m_innerRadius)) {
            const double start=double((std::min(point.start,point.end)-negativeAngles)/angleExtent)*2*pi-pi/2,end=double((std::max(point.start,point.end)-negativeAngles)/angleExtent)*2*pi-pi/2;
            const double outer=std::min(m_plot.width(),m_plot.height())/2,inner=outer*std::clamp(m_innerRadius,0.,1.);auto path=sectorPath(m_plot.center(),outer,inner,start,end);
            if(m_mirrored){QTransform mirror;mirror.translate(2*m_plot.center().x(),0);mirror.scale(-1,1);path=mirror.map(path);}
            bounds=path.boundingRect();draw(path,palette[point.color%palette.size()]);rendered=!path.isEmpty();observed.insert("angleRange",pair(start+pi/2,end+pi/2));
        }else if((m_kind=="line"||spark)&&std::isfinite(point.x)&&std::isfinite(point.y)) {bounds={px(point)-1,py(point.y)-1,2,2};rendered=true;}
        observed.insert("rendered",rendered);observed.insert("bounds",rectangle(bounds));pointRows.append(observed);
        const QString description=bar ? QStringLiteral("%1, %2: %3").arg(point.series,point.label,formatted(point.y,0,locale)):pie ? QStringLiteral("%1: %2").arg(point.series,formatted(point.y,0,locale)):QStringLiteral("%1, X: %2, Y: %3").arg(point.series,formatted(point.x,0,locale),formatted(point.y,0,locale));
        m_accessibility.append(QVariantMap{{"name",description},{"bounds",rectangle(bounds)},{"rendered",rendered}});
    }
    for(const auto &entry:legend) {
        const double itemWidth=entry["width"].toDouble(),x=m_mirrored ? m_size.width()-entry["x"].toDouble()-itemWidth:entry["x"].toDouble();
        const double y=m_plot.height()+(xAxis ? 18:0)+legendPadding+22*entry["row"].toInt();
        const double markerX=m_mirrored ? x+itemWidth-8:x;
        QPainterPath marker;marker.addEllipse(QRectF(markerX,y+(12.3203125-8)/2,8,8));draw(marker,QColor(entry["color"].toString()));
        label(entry["text"].toString(),legendFont,{m_mirrored ? x:x+13,y+(12.3203125-legendMetrics.height())/2+legendMetrics.ascent()},foreground);
        auto record=entry;record.insert("x",x);record.insert("y",y);legendReport.append(record);
    }
    QRectF bounds(QPointF(0,0),m_size);
    for(const auto &entry:m_draws)bounds=bounds.united(entry.path.controlPointRect().adjusted(-entry.stroke/2-1,-entry.stroke/2-1,entry.stroke/2+1,entry.stroke/2+1));
    m_bounds=QRectF(std::floor(bounds.left()),std::floor(bounds.top()),std::ceil(bounds.right())-std::floor(bounds.left()),std::ceil(bounds.bottom())-std::floor(bounds.top()));
    const auto rounded=[&](double value){return std::round(value*m_pixelRatio)/m_pixelRatio;};
    // Plot anchors round in the window's scene before returning local values.
    // Rounding the width alone loses the half-point phase of a tiny centered
    // caller and changes inverse-coordinate queries at fractional origins.
    const QPointF first(rounded(m_sceneOrigin.x()+m_plot.left()),rounded(m_sceneOrigin.y()+m_plot.top()));
    const QPointF last(rounded(m_sceneOrigin.x()+m_plot.right()),rounded(m_sceneOrigin.y()+m_plot.bottom()));
    const QRectF plotFrame(first-m_sceneOrigin,QSizeF(last.x()-first.x(),last.y()-first.y()));
    m_measurements={{"kind",m_kind},{"plotFrame",rectangle(plotFrame)},{"plotSize",QVariantMap{{"width",m_plot.width()},{"height",m_plot.height()}}},{"xDomain",bar ? QVariant(categories):QVariant(xScale.domain())},{"yDomain",yScale.domain()},{"seriesDomain",series},{"points",pointRows},{"legend",legendReport},{"axisFontFamily",axisFont.family()},{"axisFontPixels",10},{"legendFontPixels",11},{"paintBounds",rectangle(m_bounds)},{"nativeNonfiniteDeterminism","pending; source bar NaN input yields varying initialized domains"},{"nativeRasterAcceptance","pending"}};
    if(pie) {
        QVariantList samples;Scale angleScale;
        angleScale.low=double(negativeAngles);angleScale.high=double(positiveAngles);
        angleScale.valid=std::any_of(points.begin(),points.end(),[](const Point &point){return std::isfinite(point.y);});
        for(int i=0;i<=4;++i)samples.append(number(angleScale.value(i*90*pi/180,2*pi,m_mirrored)));
        m_measurements.insert("angleValues",samples);
        m_measurements.remove("xDomain");m_measurements.remove("yDomain");m_measurements.remove("points");
        // Keep independent point/sector and accessible data in a named report
        // field; the native plot-proxy does not expose per-sector bounds.
        m_measurements.insert("sectors",pointRows);
    }else {
        QVariantList xValues,yValues,ySizes;
        for(int i=0;i<3;++i) {
            const double fraction=i/2.;
            if(bar) {
                const double position=fraction*plotFrame.width()/std::max(1.,m_plot.width())*categories.size();
                int index=std::clamp(int(std::floor(position)),0,std::max(0,int(categories.size())-1));
                if(m_mirrored)index=categories.size()-1-index;
                xValues.append(categories.isEmpty() ? QVariant():QVariant(categories[index]));
            }else xValues.append(number(xScale.value(fraction*plotFrame.width(),m_plot.width(),m_mirrored)));
            yValues.append(number(yScale.value(fraction*plotFrame.height(),m_plot.height(),true)));
            ySizes.append(number(yScale.value(fraction*m_plot.height(),m_plot.height(),true)));
        }
        m_measurements.insert("xValues",xValues);m_measurements.insert("yValues",yValues);m_measurements.insert("yValuesAtPlotSize",ySizes);
    }
    emit layoutChanged();update();
}

void ChartRenderer::paint(QPainter *painter) {
    painter->translate(-m_bounds.topLeft());painter->setRenderHint(QPainter::Antialiasing,true);
    for(const auto &draw:m_draws) {
        if(draw.stroke>0){QPen pen(draw.color,draw.stroke,Qt::SolidLine,Qt::RoundCap,Qt::RoundJoin);if(draw.dashed){pen.setDashPattern({6,6});pen.setCapStyle(Qt::FlatCap);}painter->setPen(pen);painter->setBrush(Qt::NoBrush);}
        else {painter->setPen(Qt::NoPen);if(draw.gradient){QLinearGradient gradient(m_plot.topLeft(),m_plot.bottomLeft());auto a=draw.color,b=draw.color;a.setAlphaF(0.25);b.setAlphaF(0.02);gradient.setColorAt(0,a);gradient.setColorAt(1,b);painter->setBrush(gradient);}else painter->setBrush(draw.color);}
        painter->drawPath(draw.path);
    }
}

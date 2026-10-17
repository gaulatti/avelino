#include <QGuiApplication>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QFile>
#include <QPainterPath>
#include <QPainterPathStroker>
#include <algorithm>
#include <array>
#include <cmath>
#include <vector>
#include <cstdio>
static QPainterPath path(QJsonArray rows) {
    QPainterPath p;p.setFillRule(Qt::WindingFill);
    for(const auto &v:rows){const auto r=v.toObject();const auto pts=r["points"].toArray();auto point=[&](int i){const auto a=pts[i].toArray();return QPointF(a[0].toDouble(),a[1].toDouble());};
        const auto k=r["kind"].toString();if(k=="move")p.moveTo(point(0));else if(k=="line")p.lineTo(point(0));else if(k=="cubic")p.cubicTo(point(0),point(1),point(2));else if(k=="quad")p.quadTo(point(0),point(1));else p.closeSubpath();}
    return p;
}
static QPointF at(const std::array<QPointF,4> &p,double t) {
    auto q=p;for(int n=3;n>0;--n)for(int i=0;i<n;++i)q[i]=q[i]*(1-t)+q[i+1]*t;return q[0];
}
struct Span {std::array<QPointF,4> p;QPointF left,right;double lo,hi,minX,maxX;bool cubic;};
struct CompiledPath {
    std::vector<Span> spans;
    explicit CompiledPath(const QPainterPath &path) {
        auto line=[&](QPointF a,QPointF b){if(a.y()!=b.y())spans.push_back({{a,a,b,b},a,b,0,1,std::min(a.x(),b.x()),std::max(a.x(),b.x()),false});};
        auto curve=[&](std::array<QPointF,4> p){
            const double a=-p[0].y()+3*p[1].y()-3*p[2].y()+p[3].y(),b=2*(p[0].y()-2*p[1].y()+p[2].y()),c=p[1].y()-p[0].y();
            std::vector<double> cuts{0,1};auto cut=[&](double t){if(t>0 &&t<1)cuts.push_back(t);};
            if(a==0){if(b!=0)cut(-c/b);}else {const double disc=b*b-4*a*c;if(disc>=0){const double root=std::sqrt(disc);cut((-b-root)/(2*a));cut((-b+root)/(2*a));}}
            std::sort(cuts.begin(),cuts.end());const double minX=std::min({p[0].x(),p[1].x(),p[2].x(),p[3].x()}),maxX=std::max({p[0].x(),p[1].x(),p[2].x(),p[3].x()});
            for(size_t i=1;i<cuts.size();++i){const double lo=cuts[i-1],hi=cuts[i];const auto left=at(p,lo),right=at(p,hi);if(left.y()!=right.y())spans.push_back({p,left,right,lo,hi,minX,maxX,true});}
        };
        QPointF previous,first;bool open=false;
        for(int i=0;i<path.elementCount();++i){const auto e=path.elementAt(i);const QPointF point(e.x,e.y);
            if(e.type==QPainterPath::MoveToElement){if(open)line(previous,first);first=previous=point;open=true;}
            else if(e.type==QPainterPath::LineToElement){line(previous,point);previous=point;}
            else if(e.type==QPainterPath::CurveToElement){const auto e2=path.elementAt(++i),e3=path.elementAt(++i);const QPointF p2(e2.x,e2.y),p3(e3.x,e3.y);curve({previous,point,p2,p3});previous=p3;}
        }
        if(open)line(previous,first);
    }
    bool contains(QPointF query) const {
        int winding=0;
        for(const auto &s:spans){
            if(query.y()<std::min(s.left.y(),s.right.y()) ||query.y()>=std::max(s.left.y(),s.right.y()) ||query.x()>=s.maxX)continue;
            const int direction=s.right.y()>s.left.y() ? 1:-1;
            if(query.x()<s.minX){winding+=direction;continue;}
            double x;
            if(query.y()==s.left.y())x=s.left.x();else if(query.y()==s.right.y())x=s.right.x();
            else if(!s.cubic)x=s.left.x()+(query.y()-s.left.y())*(s.right.x()-s.left.x())/(s.right.y()-s.left.y());
            else {double lo=s.lo,hi=s.hi;const bool ascending=s.right.y()>s.left.y();
                for(;;){const double mid=(lo+hi)/2;if(mid==lo ||mid==hi)break;const auto v=at(s.p,mid);if((v.y()<query.y())==ascending)lo=mid;else hi=mid;}
                x=at(s.p,(lo+hi)/2).x();
            }
            if(query.x()<x)winding+=direction;
        }
        return winding!=0;
    }
};
static QJsonArray elements(const QPainterPath &p) {
    QJsonArray out;for(int i=0;i<p.elementCount();++i){const auto e=p.elementAt(i);out.append(QJsonObject{{"type",int(e.type)},{"x",e.x},{"y",e.y}});}return out;
}
int main(int argc,char **argv) {
    QGuiApplication app(argc,argv);QFile input("/diag/paths.json");if(!input.open(QIODevice::ReadOnly))return 2;
    const auto data=QJsonDocument::fromJson(input.readAll()).object();QFile qt("/diag/qt-centerlines.json");if(!qt.open(QIODevice::ReadOnly))return 3;const auto qrows=QJsonDocument::fromJson(qt.readAll()).array();
    QJsonArray results;
    for(const auto &v:data["rows"].toArray()) {
        const auto r=v.toObject();const auto nativeCenter=path(r["centerline"].toArray()),nativeStroke=path(r["stroke"].toArray());
        QPainterPath qcenter;bool found=false;for(const auto &q:qrows)if(q.toObject()["fixture"]==r["fixture"]){qcenter=path(q.toObject()["centerline"].toArray());found=true;}if(!found)return 4;
        QPainterPathStroker stroker;stroker.setWidth(1);stroker.setJoinStyle(Qt::MiterJoin);
        const auto nativeQtStroke=stroker.createStroke(nativeCenter),linuxQtStroke=stroker.createStroke(qcenter);
        const std::array<QPainterPath,3> regions{nativeStroke,nativeQtStroke,linuxQtStroke};
        const std::array<CompiledPath,3> compiled{CompiledPath(nativeStroke),CompiledPath(nativeQtStroke),CompiledPath(linuxQtStroke)};
        const auto grid=r["grid"].toObject();const int nx=grid["nx"].toInt(),ny=grid["ny"].toInt(),samples=grid["samples"].toInt();const auto nativeMask=QByteArray::fromBase64(grid["swiftUI"].toString().toLatin1());
        if(samples!=nx*ny*4 ||nativeMask.size()!=(samples+7)/8)return 5;
        QJsonArray methods;
        for(int mode=0;mode<5;++mode) {
            auto hit=[&](QPointF p){return mode<3 ? compiled[mode].contains(p):regions[mode==3 ? 0:2].contains(p);};
            QJsonArray differences;QByteArray queryMask((r["queries"].toArray().size()+7)/8,0);int queryIndex=0;
            for(const auto &query:r["queries"].toArray()) {
                const auto q=query.toObject();const QPointF p(q["x"].toDouble(),q["y"].toDouble());const bool value=hit(p);if(value)queryMask[queryIndex/8]=static_cast<unsigned char>(queryMask[queryIndex/8])|(1<<(queryIndex%8));
                if(value!=q["swiftUIContains"].toBool())differences.append(QJsonObject{{"index",queryIndex},{"point",QJsonArray{p.x(),p.y()}},{"candidate",value},{"swiftUI",q["swiftUIContains"]}});
                ++queryIndex;
            }
            QByteArray mask((samples+7)/8,0);QJsonArray first;int index=0,mismatches=0;
            for(int corner=0;corner<4;++corner)for(int xi=0;xi<nx;++xi)for(int yi=0;yi<ny;++yi){
                const double x=double(xi)/8,y=double(yi)/8;const QPointF p(corner&1 ? r["width"].toDouble()-x:x,corner&2 ? r["height"].toDouble()-y:y);const bool value=hit(p),expected=(static_cast<unsigned char>(nativeMask[index/8])>>(index%8))&1;
                if(value)mask[index/8]=static_cast<unsigned char>(mask[index/8])|(1<<(index%8));
                if(value!=expected){++mismatches;if(first.size()<256)first.append(QJsonObject{{"index",index},{"x",p.x()},{"y",p.y()},{"candidate",value},{"swiftUI",expected}});}++index;
            }
            methods.append(QJsonObject{{"mode",mode},{"queryDifferences",differences},{"queryMask",QString::fromLatin1(queryMask.toBase64())},{"queryCount",queryIndex},{"denseMismatches",mismatches},{"firstDenseDifferences",first},{"mask",QString::fromLatin1(mask.toBase64())}});
        }
        results.append(QJsonObject{{"fixture",r["fixture"]},{"width",r["width"]},{"height",r["height"]},{"radius",r["radius"]},{"samples",samples},{"methods",methods},{"nativeCenterQtStroke",elements(nativeQtStroke)},{"linuxCenterQtStroke",elements(linuxQtStroke)}});
        printf("Completed %s samples=%d\n",qPrintable(r["fixture"].toString()),samples);fflush(stdout);
    }
    QFile output("/diag/qt-results.json");if(!output.open(QIODevice::WriteOnly))return 6;
    output.write(QJsonDocument(QJsonObject{{"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"accepted",false},{"scope","SDK raw path containment only; all native query and dense masks retained"},{"rows",results}}).toJson());
}

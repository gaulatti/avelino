#include <QGuiApplication>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QFile>
#include <QPainterPath>
#include <QPainterPathStroker>
#include <QDir>
static QPainterPath path(QJsonArray rows) {
    QPainterPath p;p.setFillRule(Qt::WindingFill);
    for(const auto &v:rows){const auto r=v.toObject();const auto pts=r["points"].toArray();auto point=[&](int i){const auto a=pts[i].toArray();return QPointF(a[0].toDouble(),a[1].toDouble());};
        const auto k=r["kind"].toString();if(k=="move")p.moveTo(point(0));else if(k=="line")p.lineTo(point(0));else if(k=="cubic")p.cubicTo(point(0),point(1),point(2));else if(k=="quad")p.quadTo(point(0),point(1));else p.closeSubpath();}
    return p;
}
int main(int argc,char **argv) {
    QGuiApplication app(argc,argv);QFile input("/diag/paths.json");input.open(QIODevice::ReadOnly);
    const auto data=QJsonDocument::fromJson(input.readAll()).object();QFile qt("/diag/qt-centerlines.json");qt.open(QIODevice::ReadOnly);const auto qrows=QJsonDocument::fromJson(qt.readAll()).array();
    QJsonArray results;
    for(const auto &v:data["rows"].toArray()) {
        const auto r=v.toObject();const auto center=path(r["centerline"].toArray()),nativeStroke=path(r["stroke"].toArray());
        QPainterPath qcenter;for(const auto &q:qrows)if(q.toObject()["fixture"]==r["fixture"])qcenter=path(q.toObject()["centerline"].toArray());
        QJsonArray outputs;
        for(int mode=0;mode<5;++mode) {
            QPainterPathStroker s;s.setWidth(1);s.setJoinStyle(mode==1 ? Qt::BevelJoin:Qt::MiterJoin);
            if(mode==4)s.setCurveThreshold(.001);
            const auto region=mode==0 ? nativeStroke:s.createStroke(mode==2 ||mode==4 ? qcenter:center);
            QJsonArray differences;
            for(const auto &query:r["queries"].toArray()) {
                const auto q=query.toObject();const QPointF point(q["x"].toDouble(),q["y"].toDouble());
                const bool hit=point.x()>=0 &&point.y()>=0 &&point.x()<r["width"].toDouble() &&point.y()<r["height"].toDouble() &&region.contains(point);
                if(hit!=q["swiftUIContains"].toBool())differences.append(QJsonObject{{"point",QJsonArray{point.x(),point.y()}},{"qt",hit},{"swiftUI",q["swiftUIContains"]}});
            }
            outputs.append(QJsonObject{{"mode",mode},{"differences",differences}});
        }
        results.append(QJsonObject{{"fixture",r["fixture"]},{"methods",outputs}});
    }
    QFile output("/diag/qt-results.json");output.open(QIODevice::WriteOnly);output.write(QJsonDocument(results).toJson());
}

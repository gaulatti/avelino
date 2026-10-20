#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlProperty>
#include <QJSValue>
#include <QQuickItem>
#include <QQuickWindow>
#include <QSignalSpy>
#include <QTimer>
#include <QImage>
#include <QPainter>
#include <QDir>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QCryptographicHash>
#include <QSGRendererInterface>

// Compare ordinary Qt Quick rectangles to QPainter's floating geometry. The
// separate native shell captures establish the platform-reference comparison.
int main(int argc,char **argv)
{
    QGuiApplication app(argc,argv);
    if(app.arguments().size()!=2)return 2;
    const QString output=app.arguments()[1];
    if(!QDir().mkdir(output))return 3;
    QQuickWindow::setDefaultAlphaBuffer(true);
    QQmlApplicationEngine engine;
    engine.loadData(R"(
import QtQuick
Window {
    id:window
    width:88; height:64; visible:true; color:"#ff102030"
    property int kind:0
    property Gradient sampleGradient: Gradient {
        GradientStop {position:0; color:"#2b557f"}
        GradientStop {position:1; color:"#90bd75"}
    }
    Rectangle {
        objectName:"target"; x:7; y:8.5; width:30.5; height:17.125
        color:"#1769db"; radius:window.kind==2?4.5:0
        border.width:window.kind==1?1.25:0; border.color:"#e9a24b"
        gradient:window.kind==3?window.sampleGradient:null
    }
})");
    if(engine.rootObjects().isEmpty())return 4;
    auto window=qobject_cast<QQuickWindow*>(engine.rootObjects().first());
    if(!window)return 5;
    QTimer::singleShot(500,&app,[&] {
        auto target=window->findChild<QQuickItem*>("target");
        if(!target){app.exit(6);return;}
        auto frame=[&] {
            QSignalSpy swapped(window,&QQuickWindow::frameSwapped);
            window->update();
            if(swapped.isEmpty()&&!swapped.wait(5000))return false;
            QCoreApplication::processEvents();return true;
        };
        auto save=[&](const QImage &image,const QString &name) {
            if(!image.save(output+"/"+name))return QString();
            QFile f(output+"/"+name);if(!f.open(QIODevice::ReadOnly))return QString();
            return QString::fromLatin1(QCryptographicHash::hash(f.readAll(),QCryptographicHash::Sha256).toHex());
        };
        QJsonArray rows;int geometryFailures=0,stabilityFailures=0,alphaFailures=0,index=0;
        for(int kind:{0,1,2,3})for(double shift:{0.0,0.25,0.5,0.75,1.0})
            for(double height:{17.125,17.25,17.5,17.75,18.0,18.125}) {
                window->setProperty("kind",kind);target->setX(7+shift);target->setHeight(height);
                if(!frame()||!frame()){app.exit(7);return;}
                const double radius=target->property("radius").toDouble();
                const double borderWidth=QQmlProperty(target,"border.width").read().toDouble();
                const bool gradientActive=QQmlProperty(target,"gradient").read().value<QJSValue>().toQObject()!=nullptr;
                if(window->property("kind").toInt()!=kind || radius!=(kind==2?4.5:0)
                    || borderWidth!=(kind==1?1.25:0) || gradientActive!=(kind==3)) {
                    qWarning("Style binding mismatch: kind=%d radius=%g border=%g gradient=%d",kind,radius,borderWidth,gradientActive);
                    app.exit(14);return;
                }
                const auto first=window->grabWindow().convertToFormat(QImage::Format_ARGB32);
                if(!frame()){app.exit(8);return;}
                const auto actual=window->grabWindow().convertToFormat(QImage::Format_ARGB32);
                if(first.isNull()||actual.isNull()){app.exit(9);return;}
                const bool stable=first==actual;stabilityFailures+=!stable;
                const double dpr=window->devicePixelRatio();
                if(actual.size()!=QSize(qRound(88*dpr),qRound(64*dpr))){app.exit(10);return;}
                int painted=0,nonOpaque=0,mismatch=0;
                QImage expected(actual.size(),QImage::Format_ARGB32_Premultiplied);
                expected.setDevicePixelRatio(dpr);expected.fill(QColor("#102030"));
                if(kind==0) {
                    QPainter painter(&expected);painter.setRenderHint(QPainter::Antialiasing,false);
                    painter.fillRect(QRectF(7+shift,8.5,30.5,height),QColor("#1769db"));
                }
                expected=expected.convertToFormat(QImage::Format_ARGB32);
                for(int y=0;y<actual.height();++y) {
                    const auto a=reinterpret_cast<const QRgb*>(actual.constScanLine(y));
                    const auto b=reinterpret_cast<const QRgb*>(expected.constScanLine(y));
                    for(int x=0;x<actual.width();++x) {
                        painted+=a[x]!=qRgb(16,32,48);nonOpaque+=qAlpha(a[x])!=255;
                        if(kind==0)mismatch+=a[x]!=b[x];
                    }
                }
                alphaFailures+=nonOpaque>0;geometryFailures+=kind==0&&mismatch>0;
                const QString name=QString("frame-%1.png").arg(index,3,10,QChar('0'));
                const auto checksum=save(actual,name);if(checksum.isEmpty()){app.exit(11);return;}
                QJsonObject row{{"index",index++},{"kind",kind},{"shift",shift},{"height",height},
                    {"actualRect",QJsonArray{target->x(),target->y(),target->width(),target->height()}},
                    {"radius",radius},{"borderWidth",borderWidth},{"gradientActive",gradientActive},
                    {"stable",stable},{"paintedPixels",painted},{"nonOpaquePixels",nonOpaque},
                    {"capture",name},{"sha256",checksum},{"hasFloatingReference",kind==0}};
                if(kind==0) {
                    const QString reference="reference-"+name;const auto refChecksum=save(expected,reference);
                    if(refChecksum.isEmpty()){app.exit(12);return;}
                    row.insert("reference",reference);row.insert("referenceSha256",refChecksum);
                    row.insert("changedPixels",mismatch);
                }
                rows.append(row);
            }
        QFile file(output+"/result.json");if(!file.open(QIODevice::WriteOnly)){app.exit(13);return;}
        file.write(QJsonDocument(QJsonObject{{"qt",qVersion()},{"platform",QGuiApplication::platformName()},
            {"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"dpr",window->devicePixelRatio()},
            {"windowColor",window->color().name(QColor::HexArgb)},
            {"frames",rows},{"floatingGeometryFailures",geometryFailures},
            {"stabilityFailures",stabilityFailures},{"alphaFailures",alphaFailures},
            {"physicalDisplay",false},{"nativeAcceptance",false}}).toJson());
        qInfo("Qt rectangles: %lld frames, %d geometry failures",rows.size(),geometryFailures);
        app.exit(geometryFailures||stabilityFailures||alphaFailures?1:0);
    });
    return app.exec();
}

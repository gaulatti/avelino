#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQuickItem>
#include <QQuickWindow>
#include <QSignalSpy>
#include <QTimer>
#include <QImage>
#include <QDir>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QCryptographicHash>
#include <QSGRendererInterface>

// This probe uses only Qt Quick. An opaque window must stay opaque when an
// opaque rectangle moves to fractional coordinates, including clipped edges.
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
    width:160; height:100; visible:true; color:"#ff102030"
    property bool clipped:false
    Rectangle {
        objectName:"cover"; width:160; height:100; color:"#ff334455"
        visible:!window.clipped
    }
    Item {
        objectName:"clip"; x:40; y:25; width:50.375; height:21.5
        visible:window.clipped; clip:true
        Rectangle {x:0.25; width:60; height:parent.height; color:"#ff1769db"}
    }
})");
    if(engine.rootObjects().isEmpty())return 4;
    auto window=qobject_cast<QQuickWindow*>(engine.rootObjects().first());
    if(!window)return 5;
    QTimer::singleShot(500,&app,[&] {
        if(window->color().alpha()!=255){app.exit(6);return;}
        auto frame=[&] {
            QSignalSpy swapped(window,&QQuickWindow::frameSwapped);
            window->update();
            if(swapped.isEmpty()&&!swapped.wait(5000))return false;
            QCoreApplication::processEvents();return true;
        };
        QJsonArray frames;int failures=0;
        for(bool clipped:{false,true})for(double shift:{0.0,0.25,0.5,0.75,1.0}) {
            window->setProperty("clipped",clipped);
            const auto item=window->findChild<QQuickItem*>(clipped?"clip":"cover");
            if(!item||!item->isVisible()){app.exit(7);return;}
            item->setX((clipped?40:0)+shift);
            if(!frame()||!frame()){app.exit(8);return;}
            QImage previous;
            for(int sample=0;sample<3;++sample) {
                if(!frame()){app.exit(9);return;}
                const auto image=window->grabWindow();
                if(image.isNull()){app.exit(10);return;}
                const auto pixels=image.convertToFormat(QImage::Format_ARGB32);
                int nonOpaque=0,painted=0;QRect bounds;
                const auto expected=clipped?qRgb(23,105,219):qRgb(51,68,85);
                for(int y=0;y<pixels.height();++y) {
                    const auto line=reinterpret_cast<const QRgb*>(pixels.constScanLine(y));
                    for(int x=0;x<pixels.width();++x) {
                        painted+=line[x]==expected;
                        if(qAlpha(line[x])!=255) {
                            ++nonOpaque;bounds=bounds.united(QRect(x,y,1,1));
                        }
                    }
                }
                const bool stable=previous.isNull()||image==previous;previous=image;
                const QString name=QString("%1-shift%2-frame%3.png").arg(clipped?"clipped":"plain").arg(shift).arg(sample);
                if(!image.save(output+"/"+name)){app.exit(11);return;}
                QFile file(output+"/"+name);if(!file.open(QIODevice::ReadOnly)){app.exit(12);return;}
                frames.append(QJsonObject{{"clipped",clipped},{"shift",shift},{"sample",sample},
                    {"nonOpaquePixels",nonOpaque},{"paintedPixels",painted},{"stable",stable},
                    {"bounds",QJsonArray{bounds.x(),bounds.y(),bounds.width(),bounds.height()}},
                    {"capture",name},{"sha256",QString::fromLatin1(QCryptographicHash::hash(file.readAll(),QCryptographicHash::Sha256).toHex())}});
                failures+=nonOpaque>0||painted==0||!stable;
            }
        }
        // Canvas2D crosses Qt Quick's private QML-engine boundary. Keep this
        // separate from the opacity fixtures so it cannot hide their fringes.
        engine.loadData(R"(
import QtQuick
Window {
    width:64; height:40; visible:true; color:"#ff102030"
    Canvas {
        anchors.fill:parent
        onPaint: {
            const context=getContext("2d")
            context.fillStyle="#1769db"
            context.fillRect(0,0,width,height)
        }
    }
})");
        if(engine.rootObjects().size()!=2){app.exit(14);return;}
        auto canvasWindow=qobject_cast<QQuickWindow*>(engine.rootObjects().last());
        if(!canvasWindow){app.exit(15);return;}
        auto canvasFrame=[&] {
            QSignalSpy swapped(canvasWindow,&QQuickWindow::frameSwapped);
            canvasWindow->update();
            if(swapped.isEmpty()&&!swapped.wait(5000))return false;
            QCoreApplication::processEvents();return true;
        };
        if(!canvasFrame()||!canvasFrame()){app.exit(16);return;}
        QJsonArray canvasFrames;QImage previousCanvas;bool canvasPassed=true;
        for(int sample=0;sample<3;++sample) {
            if(!canvasFrame()){app.exit(17);return;}
            const auto image=canvasWindow->grabWindow();
            if(image.isNull()){app.exit(18);return;}
            const auto pixels=image.convertToFormat(QImage::Format_ARGB32);
            int painted=0;
            for(int y=0;y<pixels.height();++y) {
                const auto line=reinterpret_cast<const QRgb*>(pixels.constScanLine(y));
                for(int x=0;x<pixels.width();++x)painted+=line[x]==qRgb(23,105,219);
            }
            const bool stable=previousCanvas.isNull()||image==previousCanvas;previousCanvas=image;
            const bool passed=painted==pixels.width()*pixels.height()&&stable;
            canvasPassed=canvasPassed&&passed;
            const QString name=QString("canvas-frame%1.png").arg(sample);
            if(!image.save(output+"/"+name)){app.exit(19);return;}
            QFile file(output+"/"+name);if(!file.open(QIODevice::ReadOnly)){app.exit(20);return;}
            canvasFrames.append(QJsonObject{{"sample",sample},{"passed",passed},{"paintedPixels",painted},
                {"stable",stable},{"capture",name},
                {"sha256",QString::fromLatin1(QCryptographicHash::hash(file.readAll(),QCryptographicHash::Sha256).toHex())}});
        }
        QFile file(output+"/result.json");if(!file.open(QIODevice::WriteOnly)){app.exit(13);return;}
        file.write(QJsonDocument(QJsonObject{{"qt",qVersion()},{"platform",QGuiApplication::platformName()},
            {"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"dpr",window->devicePixelRatio()},
            {"windowColor",window->color().name(QColor::HexArgb)},{"physicalDisplay",false},
            {"frames",frames},{"failedFrames",failures},{"canvasFrames",canvasFrames},
            {"canvasRuntimeChecksPassed",canvasPassed}}).toJson());
        qInfo("Qt software opacity: %lld frames, %d failures",frames.size(),failures);
        app.exit(failures||!canvasPassed?1:0);
    });
    return app.exec();
}

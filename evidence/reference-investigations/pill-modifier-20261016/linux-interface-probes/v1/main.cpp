#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QTimer>
#include <QFont>
#include <QColor>
#include <QJsonDocument>
#include <QJsonObject>
#include <QFile>
int main(int argc,char **argv){QGuiApplication app(argc,argv);QQmlApplicationEngine engine;engine.addImportPath("/installed/lib/qml");engine.load(QUrl::fromLocalFile("/probe/Probe.qml"));if(engine.rootObjects().isEmpty())return 2;
QTimer::singleShot(500,&app,[&]{QJsonObject out;for(const auto *name:{"scope","raw","mapped","rich","owned"}){auto item=engine.rootObjects()[0]->findChild<QObject*>(name);if(!item){app.exit(3);return;}auto font=item->property("font").value<QFont>();QJsonObject row{{"family",font.family()},{"pointSize",font.pointSizeF()},{"pixelSize",font.pixelSize()},{"weight",int(font.weight())},{"resolveMask",int(font.resolveMask())},{"width",item->property("width").toDouble()},{"height",item->property("height").toDouble()},{"baseline",item->property("baselineOffset").toDouble()},{"color",item->property("color").value<QColor>().name()},{"class",item->metaObject()->className()}};out[name]=row;}QFile file("/probe/result.json");file.open(QIODevice::WriteOnly);file.write(QJsonDocument(out).toJson());app.exit(0);});return app.exec();}

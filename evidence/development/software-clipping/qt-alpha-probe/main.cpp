#include <QGuiApplication>
#include <QQuickView>
#include <QQuickItem>
#include <QTest>
#include <QJsonDocument>
#include <QJsonObject>
#include <QFile>
int main(int argc,char **argv) {
    QGuiApplication app(argc,argv);
    if(argc!=3)return 1;
    QQuickView view;view.setSource(QUrl::fromLocalFile(QString::fromLocal8Bit(argv[1])));view.show();
    QTest::qWait(300);
    auto before=view.grabWindow();const qreal dpr=view.devicePixelRatio();
    const auto hole=before.pixelColor(qRound(15*dpr),qRound(15*dpr));
    const auto center=before.pixelColor(qRound(50*dpr),qRound(50*dpr));
    auto ink=view.rootObject()->findChild<QQuickItem *>("ink");if(!ink)return 2;
    ink->setProperty("color",QColor("blue"));QTest::qWait(100);
    const auto after=view.grabWindow();
    const bool reproduced=hole==QColor("black") && center==QColor("red") && after.pixelColor(qRound(50*dpr),qRound(50*dpr))==QColor("blue");
    const QString prefix=QString::fromLocal8Bit(argv[2]);
    if(!before.save(prefix+"-before.png") || !after.save(prefix+"-after.png"))return 3;
    QJsonObject record{{"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"dpr",dpr},
        {"result",reproduced ? "software layer alpha defect reproduced":"different result; inspect"},
        {"expectedHoleColor","#123456"},{"actualHoleColor",hole.name(QColor::HexArgb)},
        {"originalIsland",center.name(QColor::HexArgb)},
        {"updatedIsland",after.pixelColor(qRound(50*dpr),qRound(50*dpr)).name(QColor::HexArgb)},
        {"method","Public Qt Quick ShaderEffectSource; no Avelino or private API; QQuickWindow capture"}};
    QFile file(prefix+".json");if(!file.open(QIODevice::WriteOnly))return 4;file.write(QJsonDocument(record).toJson());
    return reproduced ? 0:5;
}

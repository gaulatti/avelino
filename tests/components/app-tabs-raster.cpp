#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QQuickWindow>
#include <QQuickItem>
#include <QJsonDocument>
#include <QJsonArray>
#include <QJsonObject>
#include <QFile>
#include <QDir>
#include <QTemporaryDir>
#include <QProcess>
#include <QTimer>
#include <QTest>
#include <cstring>
#include "../consumer/apptabfixtures.h"

static QJsonArray sequence() {
    QFile file(":/avelino/fixtures/app-tabs-raster-sequence.json");
    if(!file.open(QIODevice::ReadOnly))qFatal("App-tab raster sequence missing");
    const auto rows=QJsonDocument::fromJson(file.readAll()).array();
    if(rows.size()!=28)qFatal("App-tab raster sequence incomplete");
    return rows;
}

static void setup(QQmlApplicationEngine &engine,bool dark,qreal scale) {
    engine.addImportPath(QStringLiteral(AVELINO_APP_TABS_IMPORT_PATH));
    installAppTabFixtureMetrics(engine);
    engine.rootContext()->setContextProperty("captureDark",dark);
    engine.rootContext()->setContextProperty("captureTextScale",scale);
}

static QQuickItem *findItem(QQuickItem *item,const QString &name) {
    if(item->objectName()==name)return item;
    for(auto child:item->childItems())if(auto match=findItem(child,name))return match;
    return nullptr;
}

static QImage viewport(QQuickWindow *window) {
    const auto dpr=window->devicePixelRatio();
    const auto image=window->grabWindow();
    if(image.size()!=window->size()*dpr)qFatal("App-tab window readback dimensions changed");
    return image.copy(QRect(qRound(0*dpr),qRound(180*dpr),qRound(640*dpr),qRound(400*dpr))).convertToFormat(QImage::Format_RGBA8888);
}

static bool samePixels(const QImage &a,const QImage &b) {
    if(a.isNull()||b.isNull()||a.size()!=b.size()||a.format()!=b.format())return false;
    for(int y=0;y<a.height();++y)if(std::memcmp(a.constScanLine(y),b.constScanLine(y),a.width()*4)!=0)return false;
    return true;
}

// A separate process retains the first-window rendering path and independent
// theme/font initialization. Reusing the retained engine is a weaker oracle.
static int captureFresh(QGuiApplication &app,int index,const QString &path) {
    const auto rows=sequence();
    if(index<0||index>=rows.size()||QFile::exists(path))return 2;
    const auto row=rows[index].toObject();
    auto definition=row["definition"].toObject();
    definition["width"]=definition["tabWidth"];
    definition["height"]=definition["tabHeight"];
    QQmlApplicationEngine engine;
    setup(engine,row["dark"].toBool(),row["textScale"].toDouble());
    engine.setInitialProperties({{"model",definition.toVariantMap()},{"selection",row["selection"].toString()},{"height",580}});
    engine.loadFromModule("AvelinoAppTabRasterTests","AppTabs");
    auto window=qobject_cast<QQuickWindow*>(engine.rootObjects().value(0));
    if(!window)return 3;
    QTimer::singleShot(500,&app,[&]{app.exit(viewport(window).save(path)?0:4);});
    return app.exec();
}

class AppTabRasterTests : public QObject {
    Q_OBJECT
private slots:
    void retainedMatchesFresh() {
        QQmlApplicationEngine engine;
        setup(engine,false,1);
        engine.loadFromModule("AvelinoAppTabRasterTests","AppTabs");
        auto window=qobject_cast<QQuickWindow*>(engine.rootObjects().value(0));
        QVERIFY(window);
        QVERIFY(QTest::qWaitForWindowExposed(window));
        QTest::qWait(500);
        const auto evidenceRoot=QStringLiteral(AVELINO_APP_TABS_RASTER_EVIDENCE_ROOT);
        QVERIFY(QDir().mkpath(evidenceRoot));
        QTemporaryDir evidence(evidenceRoot+"/dpr-"+QString::number(window->devicePixelRatio())+".XXXXXX");
        QVERIFY(evidence.isValid());
        QVERIFY(QFile::setPermissions(evidence.path(),QFile::ReadOwner|QFile::WriteOwner|QFile::ExeOwner|
                                     QFile::ReadGroup|QFile::ExeGroup|QFile::ReadOther|QFile::ExeOther));
        evidence.setAutoRemove(false);
        qInfo().noquote()<<"App-tab raster evidence:"<<evidence.path();
        const auto rows=sequence();
        QJsonArray observations;
        int mismatches=0,clicks=0;
        for(int index=0;index<rows.size();++index) {
            const auto row=rows[index].toObject();
            const auto control=row["control"].toString();
            if(!control.isEmpty()) {
                QString name="appTabsOperator-"+control;
                if(control.startsWith("tab-")) {
                    const auto tabs=rows[index-1].toObject()["definition"].toObject()["tabs"].toArray();
                    int at=-1;
                    for(int i=0;i<tabs.size();++i)if(tabs[i].toObject()["value"]==control.mid(4))at=i;
                    QVERIFY(at>=0);name="bleeckerAppTab"+QString::number(at);
                }
                auto target=findItem(window->contentItem(),name);
                QVERIFY2(target,qPrintable(name));
                QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,target->mapToScene(QPointF(target->width()/2,target->height()/2)).toPoint());
                QTest::mouseMove(window,QPoint(window->width()-2,window->height()-2));
                ++clicks;
            }
            QTest::qWait(150);
            QVariant state;
            QVERIFY(QMetaObject::invokeMethod(window,"ownerState",Q_RETURN_ARG(QVariant,state)));
            if(state.metaType()==QMetaType::fromType<QJSValue>())state=state.value<QJSValue>().toVariant();
            const auto owner=QJsonObject::fromVariantMap(state.toMap());
            QCOMPARE(owner["selection"],row["selection"]);
            QCOMPARE(owner["pending"],row["pending"]);
            const auto actual=viewport(window);
            // A fresh and retained capture could both lose the badge. Require
            // visible capsule pixels independently of their pixel equality.
            const auto definition=row["definition"].toObject();
            if(!definition["disabled"].toBool()&&!definition["tabs"].toArray().isEmpty()) {
                int sunsetPixels=0;
                for(int y=0;y<actual.height();++y)for(int x=0;x<actual.width();++x)
                    sunsetPixels+=actual.pixelColor(x,y)==QColor(255,150,119);
                QVERIFY2(sunsetPixels>0,"Enabled app-tab badges disappeared");
            }
            const auto name=row["name"].toString();
            QVERIFY(actual.save(evidence.filePath(name+"-retained.png")));
            const auto freshPath=evidence.filePath(name+"-fresh.png");
            QProcess child;
            child.setProgram(QCoreApplication::applicationFilePath());
            child.setArguments({"--capture-fresh",QString::number(index),freshPath});
            child.setStandardOutputFile(evidence.filePath(name+"-fresh.log"));
            child.setStandardErrorFile(evidence.filePath(name+"-fresh.log"),QIODevice::Append);
            child.start();QVERIFY(child.waitForStarted());QVERIFY(child.waitForFinished(-1));
            QCOMPARE(child.exitStatus(),QProcess::NormalExit);QCOMPARE(child.exitCode(),0);
            const auto expected=QImage(freshPath).convertToFormat(QImage::Format_RGBA8888);
            const bool identical=samePixels(actual,expected);
            mismatches+=!identical;
            observations.append(QJsonObject{{"phase",name},{"identical",identical},{"selection",owner["selection"]},{"pending",owner["pending"]}});
        }
        QCOMPARE(clicks,27);
        QFile report(evidence.filePath("observations.json"));QVERIFY(report.open(QIODevice::WriteOnly));
        report.write(QJsonDocument(QJsonObject{{"accepted",false},{"dpr",window->devicePixelRatio()},{"clicks",clicks},{"states",observations},{"mismatches",mismatches}}).toJson());
        report.close();
        QCOMPARE(mismatches,0);
    }
};

int main(int argc,char **argv) {
    QGuiApplication app(argc,argv);
    if(argc==4&&QString::fromUtf8(argv[1])=="--capture-fresh") {
        bool ok=false;const auto index=QString::fromUtf8(argv[2]).toInt(&ok);
        return ok?captureFresh(app,index,QString::fromUtf8(argv[3])):2;
    }
    AppTabRasterTests test;
    return QTest::qExec(&test,argc,argv);
}

#include "app-tabs-raster.moc"

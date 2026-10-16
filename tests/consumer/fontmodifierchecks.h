#pragma once
#include "fontmodifierframes.h"
#include <QSignalSpy>

static void runFontModifierConsumer(QQuickWindow *window,QGuiApplication &app,
                                   const QCommandLineParser &parser,double textScale,QQmlApplicationEngine &engine) {
    auto check=[&](bool value,const QString &message){if(!value){qCritical("Installed font modifier: %s",qPrintable(message));app.exit(255);}return value;};
    const auto fixture=window->property("primaryFixture").value<QQuickItem*>();
    if(!check(fixture,"Caller fixture unavailable"))return;
    auto frame=[&](){QSignalSpy displayed(window,&QQuickWindow::frameSwapped);window->update();return check(displayed.count()>0||displayed.wait(5000),"Window did not paint");};
    auto settle=[&](){return frame()&&frame();};
    auto configure=[&](const QJsonObject &values){return check(QMetaObject::invokeMethod(window,"configure",Q_ARG(QVariant,values.toVariantMap())),"Configuration failed")&&settle();};
    const auto theme=engine.singletonInstance<QObject*>(qmlTypeId("Avelino",0,1,"BleeckerTheme"));
    if(!check(theme,"Theme unavailable"))return;
    QFile witness(":/avelino/fixtures/native-font-modifier-witnesses.json");
    if(!check(witness.open(QIODevice::ReadOnly),"Native witnesses unavailable"))return;
    const auto source=QJsonDocument::fromJson(witness.readAll()).object();
    if(!check(source["reference"]=="fe8a1d462fbd793d883fb92086a16aa2947e32c9" && source["contexts"].toArray().size()==1656 && source["accepted"]==false,"Incomplete native witness projection"))return;
    const QString appearance=parser.isSet("dark") ? "dark":"light";
    QJsonArray contexts;int exactFrames=0,exactBaselines=0;
    for(const auto &entry:source["contexts"].toArray()){
        const auto row=entry.toObject();
        if(row["appearance"]!=appearance || row["textScale"].toDouble()!=textScale || row["dpr"].toDouble()!=window->devicePixelRatio())continue;
        fixture->setProperty("mounted",false);if(!settle())return;
        for(const char *name:{"appearances","disappearances","callerInstances"})fixture->setProperty(name,0);
        const auto config=row["configuration"].toObject();window->setProperty("baselineParent",config["baselineParent"].toBool());
        if(!configure(config))return;
        fixture->setProperty("mounted",true);if(!settle())return;
        const auto measured=fontModifierObservation(fixture);
        if(!check(measured["fontModifierState"]==row["state"],"Retained initial caller state differs for "+config["fixture"].toString()))return;
        if(!check(measured["renderedFamily"]==config["family"] && measured["renderedSize"]==config["size"]
            && measured["renderedWeight"]==config["weight"] && measured["renderedTextScale"].toDouble()==textScale
            && measured["renderedRtl"]==config["rtl"],"Font producer did not reach the caller scope"))return;
        const bool frames=measured["fontModifierParts"]==row["parts"],baselines=measured["fontModifierBaselines"]==row["baselines"];
        exactFrames+=frames;exactBaselines+=baselines;
        contexts.append(QJsonObject{{"fixture",config["fixture"]},{"observations",measured},
            {"nativeFrameStatus",frames ? "passed":"failed"},{"nativeBaselineStatus",baselines ? "passed":"failed"}});
    }
    if(!check(contexts.size()==207,"Incomplete runtime source context matrix"))return;
    window->setProperty("baselineParent",false);
    QJsonObject initial{{"family","primary"},{"size",14},{"weight","regular"},{"content","text"},{"text","Keep edition"},
        {"offer",QJsonValue::Null},{"parentLayout","zstack"},{"parentFont",false},{"outerSystem",false},{"outerFontModifier",false},{"rtl",false}};
    theme->setProperty("dark",false);theme->setProperty("textScale",1);
    if(!configure(initial))return;
    auto control=fixture->property("control").value<QQuickItem*>();auto caller=fontModifierPart(control,0);
    if(!check(caller->width()==77 && caller->height()==17,"Primary regular caller did not retain native geometry"))return;
    auto image=[&](){const auto point=fixture->mapToScene(QPointF());const auto dpr=window->devicePixelRatio();return window->grabWindow().copy(qRound(point.x()*dpr),qRound(point.y()*dpr),qRound(fixture->width()*dpr),qRound(fixture->height()*dpr));};
    const auto originalPixels=image();const auto originalState=fontModifierState(fixture);
    auto ax=QAccessible::queryAccessibleInterface(caller);
    if(!check(ax && ax->role()==QAccessible::StaticText && ax->text(QAccessible::Name)=="Keep edition","Caller accessibility name/role"))return;
    QJsonArray updates;
    for(const auto &change:QList<QJsonObject>{{{"family","secondary"}},{{"size",24}},{{"weight","bold"}}}){
        if(!configure(change))return;
        if(!check(fixture->property("control").value<QQuickItem*>()==control && fontModifierPart(control,0)==caller
            && fontModifierState(fixture)==originalState,"Font update recreated caller"))return;
        if(!check(QTest::qWaitFor([&]{return image()!=originalPixels;},5000),"Live font change did not repaint caller"))return;
        updates.append(fontModifierObservation(fixture));
    }
    theme->setProperty("textScale",1.5);if(!settle())return;
    if(!check(control->property("textScale").toDouble()==1.5 && image()!=originalPixels,"Live scale did not reach paint"))return;
    theme->setProperty("textScale",1);if(!configure(initial))return;
    if(!check(QTest::qWaitFor([&]{return image()==originalPixels;},5000) && fontModifierPart(control,0)==caller
        && fontModifierState(fixture)==originalState,"Restored font inputs did not restore retained caller pixels"))return;
    const auto input=window->property("inputItem").value<QQuickItem*>(),transparent=window->property("transparentItem").value<QQuickItem*>();
    if(!check(input && transparent,"Interactive caller unavailable"))return;
    window->requestActivate();if(!check(QTest::qWaitFor([&]{return window->isActive();},5000),"Window activation failed"))return;
    auto click=[&](QQuickItem *item){QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,item->mapToScene(QPointF(item->width()/2,item->height()/2)).toPoint());return settle();};
    if(!click(input) || !check(window->property("activations").toInt()==1,"Font scope blocked caller pointer input"))return;
    input->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_Space);if(!settle())return;
    const auto inputAx=QAccessible::queryAccessibleInterface(input);
    if(!check(window->property("activations").toInt()==2 && inputAx && inputAx->role()==QAccessible::Button && inputAx->text(QAccessible::Name)=="Activate 2","Caller keyboard/accessibility producer"))return;
    if(!click(transparent) || !check(window->property("passthroughActivations").toInt()==1,"Font scope intercepted background pointer"))return;
    theme->setProperty("dark",parser.isSet("dark"));theme->setProperty("textScale",textScale);if(!settle())return;
    qInfo("Installed font modifier: 207 source contexts, retained caller, live/restored pixels, pointer, keyboard and Qt accessibility passed; native comparison remains separate");
    if(!parser.isSet("evidence")){app.exit(0);return;}
    const auto path=parser.value("evidence");if(!check(window->grabWindow().save(path+".png"),"Window capture failed"))return;
    QJsonObject record{{"fixture","font-modifier"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},
        {"compiler",QString::fromUtf8(__VERSION__)},{"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},
        {"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},
        {"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},{"appearance",appearance},{"textScale",textScale},{"accepted",false},
        {"fontModifierChecks","passed"},{"callerStateChecks","passed"},{"liveFontPaintChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},
        {"closedContextCount",contexts.size()},{"exactFrameSets",exactFrames},{"exactBaselineSets",exactBaselines},{"closedContexts",contexts},{"retainedUpdates",updates},
        {"inputMethod","QTest synthetic pointer and keyboard in the consumer window"},
        {"nativeAcceptance","pending; all strict source differences retained separately; complete font/framework, physical and reader gates open"}};
    QFile file(path+".json");if(!check(file.open(QIODevice::WriteOnly),"Metadata write failed"))return;
    file.write(QJsonDocument(record).toJson());file.close();
    auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path]{if(QFile::exists(path+".captured"))app.exit(0);});timer->start(100);
}

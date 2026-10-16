#pragma once
#include "buttonstyleframes.h"
#include <QSignalSpy>
#include <QMouseEvent>
#include <QElapsedTimer>

static void runButtonStyleConsumer(QQuickWindow *window,QGuiApplication &app,
                                  const QCommandLineParser &parser,double textScale,QQmlApplicationEngine &engine) {
    auto check=[&](bool value,const QString &message){if(!value){qCritical("Installed ButtonStyle: %s",qPrintable(message));app.exit(255);}return value;};
    const auto fixture=window->property("primaryFixture").value<QQuickItem*>();
    if(!check(fixture,"Caller fixture unavailable"))return;
    auto frame=[&](){
        QSignalSpy displayed(window,&QQuickWindow::frameSwapped);window->update();
        return check(displayed.count()>0 || displayed.wait(5000),"Window did not display a frame");
    };
    auto settle=[&](){return frame() && frame();};
    auto configure=[&](const QJsonObject &values){
        return check(QMetaObject::invokeMethod(window,"configure",Q_ARG(QVariant,values.toVariantMap())),"Fixture configuration failed") && settle();
    };
    auto control=[&](){return fixture->property("control").value<QQuickItem*>();};
    auto value=[&](){return fixture->property("localValue").toInt();};
    QFile witness(":/avelino/fixtures/native-button-style-witnesses.json");
    if(!check(witness.open(QIODevice::ReadOnly),"Native witnesses unavailable in independent package"))return;
    const auto source=QJsonDocument::fromJson(witness.readAll()).object();
    if(!check(source["reference"]=="fe8a1d462fbd793d883fb92086a16aa2947e32c9","Native reference changed"))return;
    window->requestActivate();
    if(!check(QTest::qWaitFor([&]{return window->isActive();},5000),"Window did not activate"))return;
    const auto preview=window->findChild<QQuickItem*>("buttonStyleVariant-primary");
    const auto previewPart=preview ? buttonStylePart(preview,0):nullptr;
    const auto previewBody=previewPart ? previewPart->property("presentationItem").value<QQuickItem*>():nullptr;
    if(!check(previewBody,"Primary variant preview unavailable"))return;
    auto grownPaint=[&](){
        const auto point=previewBody->mapToScene(QPointF(previewBody->width()-5,previewBody->height()/2));
        const auto dpr=window->devicePixelRatio();const auto pixels=window->grabWindow();
        return pixels.pixelColor(qRound(point.x()*dpr),qRound(point.y()*dpr))==preview->property("fillColor").value<QColor>();
    };
    if(!check(QTest::qWaitFor(grownPaint,5000),"Primary preview paint did not reach its current allocated width"))return;
    const auto theme=engine.singletonInstance<QObject*>(qmlTypeId("Avelino",0,1,"BleeckerTheme"));
    if(!check(theme,"Theme singleton unavailable"))return;
    for(const double scale:{1.0,1.5,textScale}){
        theme->setProperty("textScale",scale);
        if(!settle() || !check(QTest::qWaitFor(grownPaint,5000),"Curve paint remained at an earlier text-scale width"))return;
    }
    QJsonArray closed,unresolved,traces;
    const QString appearance=parser.isSet("dark") ? "dark":"light";
    for(const auto &entry:source["frames"].toArray()){
        const auto row=entry.toObject();
        if(row["appearance"]!=appearance || row["textScale"].toDouble()!=textScale || row["dpr"].toDouble()!=window->devicePixelRatio())continue;
        fixture->setProperty("mounted",false);QTest::qWait(10);
        fixture->setProperty("calls",QVariantList{});fixture->setProperty("mountValues",QVariantList{});
        if(!configure(row["configuration"].toObject()))return;
        fixture->setProperty("mounted",true);if(!settle())return;
        if(!check(control() && value()==0 && buttonStyleList(fixture->property("calls"))==row["calls"].toArray()
            && buttonStyleList(fixture->property("mountValues"))==row["mountValues"].toArray(),"Native initial caller state mismatch"))return;
        const auto name=row["configuration"].toObject()["fixture"].toString();
        const auto actual=buttonStyleFrames(fixture);
        if(QStringList{"content-system-font","text-unicode","text-bidi"}.contains(name))unresolved.append(name);
        else if(!check(actual==row["parts"].toObject(),"Native frames mismatch for "+name))return;
        closed.append(QJsonObject{{"fixture",name},{"parts",actual},{"count",value()}});
    }
    if(!check(closed.size()==88 && unresolved.size()==3,"Incomplete native closed matrix"))return;
    QJsonObject counter{{"fixture","consumer-counter"},{"content","counter"},{"parentLayout","zstack"},
        {"variant","primary"},{"size","md"},{"text","Review"},{"offer",QJsonValue::Null},
        {"parentFont",0},{"parentRed",false},{"destructiveRole",false},{"disabled",false},{"rtl",false},{"width",640},{"height",400}};
    if(!configure(counter))return;
    const auto original=control(),part=buttonStylePart(original,0),label=part->property("labelItem").value<QQuickItem*>();
    const auto input=part->property("inputItem").value<QQuickItem*>();
    if(!check(input && label && value()==0,"Counter caller unavailable"))return;
    auto click=[&](QQuickItem *item){QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,item->mapToScene(QPointF(item->width()/2,item->height()/2)).toPoint());return settle();};
    if(!click(input) || !check(value()==1,"Counter activation"))return;
    if(!configure(QJsonObject{{"variant","secondary"},{"disabled",true}}))return;
    if(!click(input) || !check(value()==1 && !input->isEnabled() && control()==original
        && buttonStylePart(control(),0)->property("labelItem").value<QQuickItem*>()==label,"Style update replaced caller or disabled input activated"))return;
    auto ax=QAccessible::queryAccessibleInterface(input);
    if(!check(ax && ax->role()==QAccessible::Button && ax->state().disabled && ax->text(QAccessible::Name)=="Publish 1","Disabled accessible state/name"))return;
    if(!configure(QJsonObject{{"disabled",false}}))return;
    input->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_Space);
    if(!settle() || !check(input->hasActiveFocus() && value()==2 && ax->text(QAccessible::Name)=="Publish 2","Qt keyboard or accessible producer update"))return;
    int pointerPhases=0;
    for(const auto &entry:source["inputTraces"].toArray()){
        const auto trace=entry.toObject();
        if(!configure(counter))return;
        theme->setProperty("dark",false);theme->setProperty("textScale",1.5);
        if(!configure(QJsonObject{{"content","multi"},{"parentLayout","hstack"},{"variant","primary"}}))return;
        const auto first=buttonStylePart(control(),0)->property("inputItem").value<QQuickItem*>();
        const auto second=buttonStylePart(control(),1)->property("inputItem").value<QQuickItem*>();
        auto firstAx=QAccessible::queryAccessibleInterface(first),secondAx=QAccessible::queryAccessibleInterface(second);
        if(!check(firstAx && secondAx && firstAx->role()==QAccessible::Button && secondAx->role()==QAccessible::Button
            && firstAx->text(QAccessible::Name)=="First child" && secondAx->text(QAccessible::Name).isEmpty(),"Flat accessible button parts"))return;
        const auto image=[&](){const auto point=fixture->mapToScene(QPointF());const auto dpr=window->devicePixelRatio();return window->grabWindow().copy(qRound(point.x()*dpr),qRound(point.y()*dpr),qRound(fixture->width()*dpr),qRound(fixture->height()*dpr));};
        const auto baseline=image();const auto dpr=window->devicePixelRatio();
        if(!check(baseline.pixelColor(int(201.5*dpr),int(180.5*dpr))==QColor(Qt::white),"Rounded corner baseline is not transparent over white"))return;
        QImage heldFirst;QJsonArray phases;int index=0;
        for(const auto &event:trace["phases"].toArray()){
            const auto phase=event.toObject(),down=phase["downPoint"].toObject(),up=phase["upPoint"].toObject();
            const auto scene=fixture->mapToScene(QPointF(down["x"].toDouble(),down["y"].toDouble()));
            const auto end=fixture->mapToScene(QPointF(up["x"].toDouble(),up["y"].toDouble()));
            auto send=[&](QEvent::Type type,QPointF point,Qt::MouseButton button,Qt::MouseButtons buttons){
                const auto global=QPointF(window->position())+point;
                QMouseEvent mouse(type,point,point,global,button,buttons,Qt::NoModifier);QCoreApplication::sendEvent(window,&mouse);
            };
            const int before=value();QElapsedTimer elapsed;elapsed.start();send(QEvent::MouseButtonPress,scene,Qt::LeftButton,Qt::LeftButton);
            QTest::qWait(int(std::ceil(phase["duration"].toDouble()*1000)));
            if(!settle() || !check(value()==before,"Action occurred before release"))return;
            if(index<2){
                if(!check(control()->property("down").toBool(),"Shared pressed state missing"))return;
                const auto held=image();
                if(!check(held!=baseline,"Press changed no pixels"))return;
                if(index==0)heldFirst=held;
                else if(!check(held==heldFirst,"Either target must press both bodies identically"))return;
            }
            if(scene!=end)send(QEvent::MouseMove,end,Qt::NoButton,Qt::LeftButton);
            send(QEvent::MouseButtonRelease,end,Qt::LeftButton,Qt::NoButton);
            if(!settle() || !check(value()-before==phase["delta"].toInt(),"Source pointer outcome mismatch at phase "+QString::number(index)))return;
            phases.append(QJsonObject{{"before",before},{"after",value()},{"delta",value()-before},{"nativeDuration",phase["duration"]},{"qtElapsedMs",elapsed.elapsed()}});
            ++index;++pointerPhases;
        }
        traces.append(QJsonObject{{"id",trace["id"]},{"sourceProfile",trace["profile"]},{"phases",phases},{"sharedHeldPixelsIdentical",true}});
    }
    if(!check(pointerPhases==13,"Incomplete native pointer replay"))return;
    theme->setProperty("dark",parser.isSet("dark"));theme->setProperty("textScale",textScale);if(!settle())return;
    qInfo("Installed ButtonStyle: 88 initial states, 85 exact frame sets, 13 native pointer phases, shared held pixels, retained caller and Qt keyboard/accessibility passed");
    if(!parser.isSet("evidence")){app.exit(0);return;}
    const auto path=parser.value("evidence");if(!check(window->grabWindow().save(path+".png"),"Window capture failed"))return;
    QJsonObject record{{"fixture","button-style"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},
        {"compiler",QString::fromUtf8(__VERSION__)},{"width",window->width()},{"height",window->height()},
        {"dpr",window->devicePixelRatio()},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},
        {"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},{"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},
        {"appearance",appearance},{"textScale",textScale},{"accepted",false},
        {"buttonStyleChecks","passed"},{"callerStateChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},
        {"liveCurvePaintChecks","passed"},
        {"closedContexts",closed},{"closedContextCount",88},{"exactFrameSets",85},{"unresolvedSourceContexts",unresolved},
        {"pointerPhases",pointerPhases},{"nativeTraces",traces},{"sharedHeldPixelsIdentical",true},
        {"inputMethod","QTest keyboard and own-window fractional QMouseEvent pointer replay; source durations retained as hold targets"},
        {"sourceNativeAcceptance","pending; complete font/raster, focused native keyboard, timing, physical input and readers"}};
    QFile file(path+".json");if(!check(file.open(QIODevice::WriteOnly),"Metadata write failed"))return;
    file.write(QJsonDocument(record).toJson());file.close();
    auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path]{if(QFile::exists(path+".captured"))app.exit(0);});
    // The observer may still be capturing the composed display. Its explicit
    // acknowledgment ends this wait; the runner owns cancellation/deadlines.
    timer->start(100);
}

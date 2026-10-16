#pragma once
#include <QEvent>
#include <QCoreApplication>

static void runStepperConsumer(QQuickWindow *window,QGuiApplication &app,
                               const QCommandLineParser &parser,double textScale) {
    auto check=[&app](bool ok,const char *message){if(!ok){qCritical("Installed stepper: %s",message);app.exit(245);}return ok;};
    auto item=[window](const QString &name){return findVisualItem(window->contentItem(),name);};
    auto stepper=item("consumerStepper"),minus=item("bleeckerStepperDecrement"),plus=item("bleeckerStepperIncrement"),value=item("bleeckerStepperValue"),field=item("stepperOutsideField");
    if(!check(stepper && minus && plus && value && field,"missing fixture or owned input"))return;
    auto click=[window](QQuickItem *button){button->parentItem()->ensurePolished();QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,button->mapToScene(QPointF(button->width()/2,button->height()/2)).toPoint());QTest::qWait(2);};
    auto setModel=[window](const QVariantMap &model){if(!window->setProperty("model",model))qFatal("Stepper fixture model is not writable");QTest::qWait(2);};
    auto calls=[window]{return window->property("calls").toInt();};
    auto normal=[](){return QVariantMap{{"value","2"},{"lower","1"},{"upper","10"},{"step","1"},{"offset","0"},{"label","Quantity"},{"disabled",false},{"observeOnly",false},{"parentFont",13},{"rtl",false}};};
    QFile file(":/avelino/fixtures/native-stepper-witnesses.json");
    if(!check(file.open(QIODevice::ReadOnly),"native witnesses unavailable in installed consumer"))return;
    const auto witnesses=QJsonDocument::fromJson(file.readAll()).object();
    if(!check(witnesses.value("reference").toString()=="fe8a1d462fbd793d883fb92086a16aa2947e32c9" && witnesses.value("traces").toArray().size()==25 && witnesses.value("formatting").toArray().size()==126,"native witness coverage"))return;
    QJsonArray traceResults;
    for(const auto &entry:witnesses.value("traces").toArray()) {
        const auto trace=entry.toObject();auto model=normal();
        model["value"]=trace.value("initialValue").toString();model["lower"]=trace.value("lowerBound").toString();model["upper"]=trace.value("upperBound").toString();
        model["step"]=trace.value("step").toString();model["offset"]=trace.value("displayOffset").toString();model["disabled"]=trace.value("disabled").toBool();model["observeOnly"]=trace.value("observeOnly").toBool();
        model["parentFont"]=trace.value("fixture").toString()=="parent-font30" ? 30:13;model["rtl"]=trace.value("rtl").toBool();
        setModel(model);const int beforeTrace=calls();
        for(const auto &v:trace.value("actions").toArray()) {
            const auto action=v.toObject();const auto kind=action.value("action").toString();const int before=calls();
            if(kind=="cancel") {
                QTest::mousePress(window,Qt::LeftButton,Qt::NoModifier,plus->mapToScene(QPointF(plus->width()/2,plus->height()/2)).toPoint());
                QTest::mouseMove(window,QPoint(800,500));QTest::mouseRelease(window,Qt::LeftButton,Qt::NoModifier,QPoint(800,500));
            }else click(kind=="increment" ? plus:minus);
            const auto requests=action.value("requests").toArray();
            if(!check(calls()-before==requests.size() && stepper->property("value").toString()==action.value("after").toString(),qPrintable("native action trace "+trace.value("fixture").toString())))return;
            if(!requests.isEmpty() && !check(window->property("requested").toString()==requests.last().toString(),"exact request string"))return;
        }
        if(!check(calls()-beforeTrace==trace.value("requests").toArray().size(),"native total setter requests"))return;
        const int beforeUpdate=calls();
        model["value"]="6";model["lower"]="5";model["upper"]="7";model["step"]="2";model["offset"]="100";model["label"]="Updated copies";model["disabled"]=false;
        setModel(model);
        if(!check(calls()==beforeUpdate && value->property("text").toString()=="106","external update without request"))return;
        for(const auto &v:trace.value("afterExternalActions").toArray()) {
            const auto action=v.toObject();const int before=calls();click(action.value("action").toString()=="increment" ? plus:minus);
            if(!check(calls()-before==action.value("requests").toArray().size() && stepper->property("value").toString()==action.value("after").toString(),"native actions after external update"))return;
        }
        if(!check(stepper->property("value").toString()==trace.value("finalValue").toString() && value->property("text").toString()==trace.value("finalFormattedValue").toString(),"native final value/display"))return;
        traceResults.append(QJsonObject{{"fixture",trace.value("fixture")},{"status","passed"},{"requests",trace.value("requests")},{"finalValue",stepper->property("value").toString()}});
    }
    int formatting=0;
    for(const auto &v:witnesses.value("formatting").toArray()) {
        const auto witness=v.toObject();QLocale::setDefault(QLocale(witness.value("locale").toString()));QEvent event(QEvent::LocaleChange);QCoreApplication::sendEvent(qApp,&event);
        auto model=normal();model["value"]=witness.value("value").toString();model["lower"]="-9223372036854775808";model["upper"]="9223372036854775807";
        setModel(model);
        if(!check(value->property("text").toString()==witness.value("text").toString(),qPrintable("native Int64 formatting "+witness.value("locale").toString()+" "+witness.value("value").toString())))return;
        ++formatting;
    }
    QLocale::setDefault(QLocale("en_US"));QEvent event(QEvent::LocaleChange);QCoreApplication::sendEvent(qApp,&event);setModel(normal());
    auto minusAx=QAccessible::queryAccessibleInterface(minus),plusAx=QAccessible::queryAccessibleInterface(plus),valueAx=QAccessible::queryAccessibleInterface(value);
    if(!check(minusAx && plusAx && valueAx && minusAx->role()==QAccessible::Button && plusAx->role()==QAccessible::Button
        && minusAx->text(QAccessible::Name)=="Decrease Quantity" && plusAx->text(QAccessible::Name)=="Increase Quantity"
        && valueAx->role()==QAccessible::StaticText && valueAx->text(QAccessible::Name)=="2","Qt roles/names/value"))return;
    int before=calls();
    const auto point=plus->mapToScene(QPointF(plus->width()/2,plus->height()/2)).toPoint();
    QTest::mousePress(window,Qt::LeftButton,Qt::NoModifier,point);QTest::qWait(1200);
    if(!check(calls()==before,"no down/held requests"))return;
    QTest::mouseRelease(window,Qt::LeftButton,Qt::NoModifier,point);
    if(!check(calls()==before+1 && stepper->property("value").toString()=="3","one release request"))return;
    minusAx->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
    plus->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_Space);
    if(!check(calls()==before+3 && stepper->property("value").toString()=="3","Qt keyboard/accessibility actions"))return;
    minus->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_Tab);
    if(!check(plus->hasActiveFocus(),"Qt input traversal"))return;
    auto model=normal();model["value"]="4";model["observeOnly"]=true;setModel(model);before=calls();
    minusAx->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
    if(!check(calls()==before+1 && window->property("requested").toString()=="3" && stepper->property("value").toString()=="4","owner can reject accessibility request"))return;
    model["disabled"]=true;setModel(model);before=calls();plusAx->actionInterface()->doAction(QAccessibleActionInterface::pressAction());click(plus);
    if(!check(calls()==before && plusAx->state().disabled,"disabled pointer/accessibility request rejection"))return;
    model=normal();model["value"]="6";model["label"]="Updated copies";setModel(model);
    if(!check(plusAx->text(QAccessible::Name)=="Increase Updated copies" && valueAx->text(QAccessible::Name)=="6","dynamic names and preserved model binding"))return;
    field->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_X);
    if(!check(field->property("text").toString()=="x","continued editing"))return;
    qInfo("Installed stepper: 25 native action traces, 126 native Int64 formatter witnesses, release/cancel/hold, binding ownership and Qt pointer/keyboard/accessibility paths passed");
    if(!parser.isSet("evidence")){app.exit(0);return;}
    const auto path=parser.value("evidence");if(!window->grabWindow().save(path+".png")){app.exit(246);return;}
    QJsonObject record{{"fixture","stepper"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"compiler",QString::fromUtf8(__VERSION__)},
        {"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},
        {"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},{"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},
        {"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},{"inputMethod","QTest synthetic pointer/keyboard and actual Qt accessibility press actions"},
        {"windowCaptureMethod","QQuickWindow::grabWindow; full session captured separately"},{"stepperChecks","passed"},{"callerBindingChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},
        {"nativeBehaviorTraces",traceResults},{"matchingNativeIntegerFormatterWitnesses",formatting},
        {"sourceKeyboardAcceptance","pending; Qt keyboard input is not source equivalence"},{"fontSymbolAcceptance","pending; system monospace and original plus/minus geometry are unapproved candidates"},
        {"accessibilityAcceptance","pending; Qt interfaces and synthetic input are not screen-reader acceptance"}};
    QFile evidence(path+".json");if(!evidence.open(QIODevice::WriteOnly)){app.exit(247);return;}evidence.write(QJsonDocument(record).toJson());evidence.close();
    auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path]{if(QFile::exists(path+".captured"))app.exit(0);});
    timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(248);});
}

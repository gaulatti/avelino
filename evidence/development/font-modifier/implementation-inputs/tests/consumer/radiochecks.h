#pragma once
#include <functional>
#include <algorithm>

static QVariant radioVariant(QVariant value) {
    if(value.metaType()==QMetaType::fromType<QJSValue>())return value.value<QJSValue>().toVariant();
    return value;
}
static QVariantMap radioConfiguration(const QJsonObject &source) {
    return {{"selection",source.value("selection").toVariant()},{"options",source.value("options").toArray().toVariantList()},
        {"orientation",source.value("horizontal").toBool() ? "horizontal":"vertical"},{"proposalWidth",source.value("width").toDouble(300)},
        {"intrinsic",false},{"disabled",source.value("disabled").toBool()},{"rtl",source.value("rtl").toBool()},
        {"observeOnly",source.value("observeOnly").toBool()},{"parentFont",source.value("font").toDouble()},
        {"parentFontKind",source.value("fontKind").toString("primary")},{"parentFontWeight",source.value("fontWeight").toString("regular")},
        {"parentForeground","inherit"},{"environmentLocale","en_US"}};
}
static void runRadioConsumer(QQuickWindow *window,QGuiApplication &app,
                             const QCommandLineParser &parser,double textScale) {
    auto check=[&app](bool ok,const QString &message){if(!ok){qCritical("Installed RadioGroup: %s",qPrintable(message));app.exit(249);}return ok;};
    auto item=[window](const QString &name){return findVisualItem(window->contentItem(),name);};
    auto control=window->property("control").value<QQuickItem*>();
    if(!check(control,"missing control"))return;
    auto option=[control](int index){return findVisualItem(control,"bleeckerRadioOption"+QString::number(index));};
    std::function<void(QQuickItem*)> polish=[&](QQuickItem *root){root->ensurePolished();for(auto child:root->childItems())polish(child);};
    auto settle=[&](){for(int i=0;i<3;++i){polish(control);QTest::qWait(2);}};
    auto setModel=[&](const QVariantMap &model){if(!window->setProperty("model",model))qFatal("RadioGroup fixture model is not writable");settle();};
    auto calls=[window]{return window->property("calls").toInt();};
    auto selected=[control]{return radioVariant(control->property("selection")).toString();};
    auto click=[&](int index,const QString &target,bool cancel=false){
        settle();const auto button=option(index);if(!button)qFatal("RadioGroup option missing");
        const auto icon=button->property("iconItem").value<QQuickItem*>(),title=button->property("titleItem").value<QQuickItem*>();
        if(!icon || !title)qFatal("RadioGroup option presentation missing");
        QPointF local;
        if(target=="gap")local=QPointF(icon->x()<title->x() ? (icon->x()+icon->width()+title->x())/2:(title->x()+title->width()+icon->x())/2,button->height()/2);
        else {const auto part=target=="title" ? title:icon;local=part->mapToItem(button,QPointF(part->width()/2,part->height()/2));}
        const auto point=button->mapToScene(local).toPoint();
        if(cancel){QTest::mousePress(window,Qt::LeftButton,Qt::NoModifier,point);QTest::mouseMove(window,QPoint(810,590));QTest::mouseRelease(window,Qt::LeftButton,Qt::NoModifier,QPoint(810,590));}
        else QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,point);
        settle();
    };
    const auto normal=radioVariant(window->property("model")).toMap();
    QFile file(":/avelino/fixtures/native-radio-witnesses.json");
    if(!check(file.open(QIODevice::ReadOnly),"native witnesses unavailable"))return;
    const auto witnesses=QJsonDocument::fromJson(file.readAll()).object();
    if(!check(witnesses.value("reference").toString()=="fe8a1d462fbd793d883fb92086a16aa2947e32c9" && witnesses.value("traces").toArray().size()==24 && witnesses.value("stringPairs").toArray().size()==13762,"native witness coverage"))return;
    int strings=0;
    const auto string=[](const QJsonArray &scalars){QList<char32_t> codepoints;for(const auto &v:scalars)codepoints.append(char32_t(v.toInt()));return QString::fromUcs4(codepoints.constData(),codepoints.size());};
    for(const auto &entry:witnesses.value("stringPairs").toArray()) {
        const auto pair=entry.toObject();bool equal=false;
        if(!check(QMetaObject::invokeMethod(window,"nativeStringsEqual",Q_RETURN_ARG(bool,equal),Q_ARG(QString,string(pair.value("left").toArray())),Q_ARG(QString,string(pair.value("right").toArray()))),"identity adapter invocation"))return;
        if(!check(equal==pair.value("equal").toBool(),"native String identity pair "+QString::number(strings)))return;
        ++strings;
    }
    QJsonArray traceResults;
    for(const auto &entry:witnesses.value("traces").toArray()) {
        const auto trace=entry.toObject();auto model=radioConfiguration(trace.value("configuration").toObject());
        const int beforeSetup=calls();setModel(model);
        if(!check(calls()==beforeSetup,"independent fixture setup emitted a request"))return;
        qInfo("Installed RadioGroup trace: %s",qPrintable(trace.value("fixture").toString()));
        const auto action=[&](const QJsonObject &a,bool afterParent){
            if(!check(selected()==a.value("before").toString(),"native action initial value"))return false;
            const int before=calls();
            if(!a.contains("skipped"))click(a.value("index").toInt(),afterParent ? "icon":a.value("target").toString(),a.value("cancel").toBool());
            const auto requests=a.value("requests").toArray();
            if(calls()-before!=requests.size() || selected()!=a.value("after").toString()) {
                qCritical("RadioGroup trace %s index %d target %s: calls %d expected %lld; value %s expected %s",qPrintable(trace.value("fixture").toString()),a.value("index").toInt(),qPrintable(a.value("target").toString()),calls()-before,static_cast<long long>(requests.size()),qPrintable(selected()),qPrintable(a.value("after").toString()));
                return check(false,"native action trace mismatch");
            }
            if(!requests.isEmpty() && !check(radioVariant(window->property("requested")).toString()==requests.last().toString(),"original requested value spelling"))return false;
            return true;
        };
        for(const auto &v:trace.value("actions").toArray())if(!action(v.toObject(),false))return;
        const int beforeParent=calls();model=radioConfiguration(trace.value("externalConfiguration").toObject());model["selection"]="external-missing";setModel(model);
        if(!check(calls()==beforeParent && selected()=="external-missing","external producer update emitted a request"))return;
        for(const auto &v:trace.value("afterExternalActions").toArray())if(!action(v.toObject(),true))return;
        if(!check(selected()==trace.value("finalValue").toString(),"native final value"))return;
        traceResults.append(QJsonObject{{"fixture",trace.value("fixture")},{"status","passed"},{"finalValue",selected()}});
    }
    QJsonArray phaseResults;
    if(!check(witnesses.value("pointerPhases").toArray().size()==11,"native pointer phase coverage"))return;
    for(const auto &entry:witnesses.value("pointerPhases").toArray()) {
        const auto phase=entry.toObject();const auto name=phase.value("fixture").toString();
        auto model=radioConfiguration(phase.value("configuration").toObject());setModel(model);
        const int before=calls();const auto button=option(0),icon=button->property("iconItem").value<QQuickItem*>();
        const auto point=icon->mapToScene(QPointF(icon->width()/2,icon->height()/2)).toPoint();
        auto phaseMatches=[&](const char *key){
            const auto expected=phase.value(key).toObject();const auto requests=expected.value("requests").toArray();
            return check(calls()-before==requests.size() && selected()==expected.value("value").toString(),"native pointer phase "+name+" "+key)
                && (requests.isEmpty() || check(radioVariant(window->property("requested")).toString()==requests.last().toString(),"native pointer phase original value "+name));
        };
        qInfo("Installed RadioGroup pointer phase: %s",qPrintable(name));
        QTest::mousePress(window,Qt::LeftButton,Qt::NoModifier,point);settle();if(!phaseMatches("afterDown"))return;
        if(name=="selection-during-down")model["selection"]="monthly";
        else if(name=="disable-during-down")model["disabled"]=true;
        else if(name=="option-disable-during-down") {
            auto options=model.value("options").toList();auto first=options[0].toMap();first["disabled"]=true;options[0]=first;model["options"]=options;
        } else if(name=="remove-during-down") {
            auto options=model.value("options").toList();options.removeFirst();model["options"]=options;
        } else if(name=="reorder-during-down") {
            auto options=model.value("options").toList();std::reverse(options.begin(),options.end());model["options"]=options;
        } else if(name=="orientation-during-down")model["orientation"]="horizontal";
        if(phase.value("mutation").toString()!="none")setModel(model);
        QTest::qWait(qRound(phase.value("holdSeconds").toDouble()*1000));if(!phaseMatches("afterHold"))return;
        if(name=="cancel") {QTest::mouseMove(window,QPoint(810,590));QTest::mouseRelease(window,Qt::LeftButton,Qt::NoModifier,QPoint(810,590));}
        else QTest::mouseRelease(window,Qt::LeftButton,Qt::NoModifier,point);
        settle();if(!phaseMatches("afterUp"))return;
        phaseResults.append(QJsonObject{{"fixture",name},{"status","passed"}});
    }
    setModel(normal);auto first=option(0),second=option(1);
    auto firstAx=QAccessible::queryAccessibleInterface(first),secondAx=QAccessible::queryAccessibleInterface(second);
    if(!check(firstAx && secondAx && firstAx->role()==QAccessible::Button && secondAx->role()==QAccessible::Button && !firstAx->state().checkable && firstAx->text(QAccessible::Name)=="Daily" && secondAx->text(QAccessible::Name)=="Weekly","Qt plain button roles/names"))return;
    int before=calls();click(0,"icon");
    if(!check(calls()==before+1 && selected()=="daily","selected option still requests setter"))return;
    first=option(0);const auto icon=first->property("iconItem").value<QQuickItem*>();const auto point=icon->mapToScene(QPointF(icon->width()/2,icon->height()/2)).toPoint();
    QTest::mousePress(window,Qt::LeftButton,Qt::NoModifier,point);QTest::qWait(1200);
    if(!check(calls()==before+1,"no pointer-down or held request"))return;
    QTest::mouseRelease(window,Qt::LeftButton,Qt::NoModifier,point);settle();
    if(!check(calls()==before+2,"one held release request"))return;
    secondAx->actionInterface()->doAction(QAccessibleActionInterface::pressAction());settle();
    if(!check(calls()==before+3 && selected()=="weekly","Qt accessible request"))return;
    first->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_Space);settle();
    if(!check(calls()==before+4 && selected()=="daily","Qt keyboard activation"))return;
    QTest::keyClick(window,Qt::Key_Tab);if(!check(option(1)->hasActiveFocus(),"Qt tab traversal"))return;
    auto model=normal;model["observeOnly"]=true;setModel(model);before=calls();secondAx->actionInterface()->doAction(QAccessibleActionInterface::pressAction());settle();
    if(!check(calls()==before+1 && selected()=="daily" && radioVariant(window->property("requested")).toString()=="weekly","owner may reject accessibility request"))return;
    model["disabled"]=true;setModel(model);before=calls();click(1,"icon");secondAx->actionInterface()->doAction(QAccessibleActionInterface::pressAction());settle();
    if(!check(calls()==before && secondAx->state().disabled,"disabled pointer and Qt accessibility"))return;
    model=normal;setModel(model);first=option(0);const auto stable=first;
    model["options"]=QVariantList{QVariantMap{{"value","monthly"},{"label","Monthly"}},QVariantMap{{"value","daily"},{"label","Updated Daily"}},QVariantMap{{"value","weekly"},{"label","Weekly"},{"disabled",true}}};
    setModel(model);if(!check(option(1)==stable && QAccessible::queryAccessibleInterface(stable)->text(QAccessible::Name)=="Updated Daily","stable value identity and updated accessible name"))return;
    auto field=item("radioOutsideField");if(!check(field,"outside editing field"))return;field->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_X);
    if(!check(field->property("text").toString()=="x","continued editing"))return;
    qInfo("Installed RadioGroup: 24 native action traces, 11 native pointer phase traces, 13762 native String pairs, controlled selection, stable identities and Qt pointer/keyboard/accessibility paths passed");
    if(!parser.isSet("evidence")){app.exit(0);return;}
    const auto path=parser.value("evidence");if(!window->grabWindow().save(path+".png")){app.exit(250);return;}
    QJsonObject record{{"fixture","radio-group"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"compiler",QString::fromUtf8(__VERSION__)},
        {"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},
        {"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},{"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},
        {"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},{"inputMethod","QTest synthetic pointer/keyboard and actual Qt accessibility press actions"},
        {"windowCaptureMethod","QQuickWindow::grabWindow; full session captured separately"},{"radioChecks","passed"},{"callerBindingChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},
        {"nativeBehaviorTraces",traceResults},{"nativePointerPhaseTraces",phaseResults},{"matchingNativeStringPairs",strings},
        {"sourceKeyboardAcceptance","pending; Qt keyboard input is not source equivalence"},{"fontSymbolAcceptance","pending; default font and original circles are unapproved candidates"},
        {"accessibilityAcceptance","pending; Qt interfaces and synthetic input are not actual reader acceptance"}};
    QFile evidence(path+".json");if(!evidence.open(QIODevice::WriteOnly)){app.exit(251);return;}evidence.write(QJsonDocument(record).toJson());evidence.close();
    auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path]{if(QFile::exists(path+".captured"))app.exit(0);});
    timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(252);});
}

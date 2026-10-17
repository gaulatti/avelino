#pragma once

static QQuickItem *surfaceModifierPart(QQuickItem *modifier,int index) {
    QQuickItem *item=nullptr;
    if(!modifier || !QMetaObject::invokeMethod(modifier,"partAt",Q_RETURN_ARG(QQuickItem*,item),Q_ARG(int,index)) || !item)
        qFatal("Surface modifier part unavailable");
    return item;
}
static void runSurfaceModifierConsumer(QQuickWindow *window,QGuiApplication &app,
                                      const QCommandLineParser &parser,double textScale,QQmlApplicationEngine &engine) {
    auto check=[&](bool value,const char *message){if(!value){qCritical("Installed surface modifier: %s",message);app.exit(97);}return value;};
    const auto flat=window->property("flatModifier").value<QQuickItem*>(),stack=window->property("stackModifier").value<QQuickItem*>();
    const auto caller=window->property("callerItem").value<QQuickItem*>(),input=window->property("inputItem").value<QQuickItem*>();
    const auto inputModifier=window->property("inputModifier").value<QQuickItem*>(),label=window->property("fontCaller").value<QQuickItem*>();
    auto settle=[&](){return check(waitForShapeFrame(window),"Asynchronous surface geometry did not reach a displayed ready frame");};
    if(!check(flat && stack && caller && input && inputModifier && label,"Public caller fixture unavailable") || !settle())return;
    if(!check(flat->property("partCount").toInt()==2 && stack->property("partCount").toInt()==1,"Flat callers were grouped or explicit stack was split"))return;
    const auto a=surfaceModifierPart(flat,0),b=surfaceModifierPart(flat,1),buttonPart=surfaceModifierPart(inputModifier,0);
    if(!check(a->size()==QSizeF(56,16) && b->size()==QSizeF(72,44) && surfaceModifierPart(stack,0)->size()==QSizeF(133,44),"Caller extents changed"))return;
    const auto font=label->property("font").value<QFont>();
    const auto fonts=engine.singletonInstance<QObject*>(qmlTypeId("Avelino",0,1,"BleeckerFonts"));
    qreal expectedPoints=0;
    if(!check(fonts && QMetaObject::invokeMethod(fonts,"pointSizeForPixels",Q_RETURN_ARG(qreal,expectedPoints),Q_ARG(qreal,32.)),"Font unit mapping unavailable"))return;
    qInfo("Inherited surface caller font: family=%s pointSize=%g rawPixelSize=%d expectedPointSize=%g",qPrintable(font.family()),font.pointSizeF(),font.pixelSize(),expectedPoints);
    if(!check(font.family()=="Encode Sans" && font.pointSizeF()==expectedPoints,"Transparent font scope was replaced by surface defaults"))return;
    const auto theme=engine.singletonInstance<QObject*>(qmlTypeId("Avelino",0,1,"BleeckerTheme"));
    if(!check(theme,"Theme unavailable"))return;
    theme->setProperty("dark",false);theme->setProperty("textScale",1);if(!settle())return;
    auto crop=[&](){const auto p=flat->mapToScene(QPointF());const auto dpr=window->devicePixelRatio();return window->grabWindow().copy(qRound(p.x()*dpr),qRound(p.y()*dpr),qRound(flat->width()*dpr),qRound(flat->height()*dpr));};
    const auto original=crop();
    window->requestActivate();if(!check(QTest::qWaitFor([&]{return window->isActive();},5000),"Window activation failed"))return;
    QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,caller->mapToScene(QPointF(caller->width()/2,caller->height()/2)).toPoint());
    if(!check(window->property("activations").toInt()==1,"Surface intercepted caller pointer input"))return;
    input->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_Space);
    if(!check(window->property("activations").toInt()==2,"Surface intercepted caller keyboard input"))return;
    int changedPaints=0;
    for(const auto radius:{0.,48.,12.}) {
        theme->setProperty("dark",false);theme->setProperty("textScale",1);
        flat->setProperty("radius",radius);inputModifier->setProperty("radius",radius);
        if(!settle())return;
        if(radius!=12 && crop()!=original)++changedPaints;
        theme->setProperty("dark",radius!=12);theme->setProperty("textScale",radius==12 ? 1.:1.5);
        if(!settle())return;
        if(!check(surfaceModifierPart(flat,0)==a && surfaceModifierPart(flat,1)==b
            && surfaceModifierPart(inputModifier,0)==buttonPart && buttonPart->property("callerItem").value<QQuickItem*>()==caller
            && input->hasActiveFocus() && window->property("activations").toInt()==2,"Radius/theme/scale update replaced the caller, state or focus"))return;
        const auto ax=QAccessible::queryAccessibleInterface(input);
        if(!check(ax && ax->role()==QAccessible::Button && ax->text(QAccessible::Name)=="Caller 2","Actual Qt caller accessibility changed"))return;
    }
    if(!check(changedPaints==2 && crop()==original,"Live radius paint or exact restored paint failed"))return;
    QTest::keyClick(window,Qt::Key_Space);
    if(!check(window->property("activations").toInt()==3,"Retained caller lost keyboard activation"))return;
    theme->setProperty("dark",parser.isSet("dark"));theme->setProperty("textScale",textScale);if(!settle())return;
    qInfo("Installed surface modifier: flat callers, explicit stack, inherited font, live/restored radius paint, retained state, focus, input and Qt accessibility passed");
    if(!parser.isSet("evidence")){app.exit(0);return;}
    const auto path=parser.value("evidence");if(!check(window->grabWindow().save(path+".png"),"Window capture failed"))return;
    const QJsonObject record{{"fixture","surface-modifier"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},
        {"compiler",QString::fromUtf8(__VERSION__)},{"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},
        {"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},
        {"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},{"accepted",false},
        {"surfaceModifierChecks","passed"},{"callerStateChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},
        {"liveRadiusPaintChecks","passed"},{"asyncShapeFrameChecks","passed"},{"flatParts",2},{"stackParts",1},{"activations",3},
        {"referenceComparison","pending; complete source context capture, native pixels, first-baseline, physical display and readers remain open"}};
    QFile file(path+".json");if(!check(file.open(QIODevice::WriteOnly),"Metadata write failed"))return;
    file.write(QJsonDocument(record).toJson());file.close();
    auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path]{if(QFile::exists(path+".captured"))app.exit(0);});timer->start(100);
}

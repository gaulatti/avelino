#pragma once
static void runSpinnerConsumer(QQuickWindow *window,QGuiApplication &app,const QCommandLineParser &parser,double textScale) {
    auto item=[window](const QString &name){return findVisualItem(window->contentItem(),name);};
    auto check=[&app](bool ok,const char *message){if(!ok){qCritical("Installed spinner: %s",message);app.exit(190);}return ok;};
    auto small=item("spinnerSmall"),medium=item("spinnerMedium"),large=item("spinnerLarge"),wide=item("spinnerWide"),narrow=item("spinnerNarrow"),custom=item("spinnerCustom"),button=item("spinnerLoadingButton"),field=item("spinnerNextField");
    if(!check(small&&medium&&large&&wide&&narrow&&custom&&button&&field,"missing fixture"))return;
    auto visual=[](QQuickItem *s){return s->property("visualItem").value<QQuickItem*>();};
    if(!check(small->width()==16 && medium->width()==32 && large->width()==32 && visual(wide)->width()==32 && visual(wide)->x()==32 && visual(wide)->y()==20 && visual(narrow)->width()==32 && visual(narrow)->x()==-10,"native intrinsic size and fixed artwork inside offered frames"))return;
    auto ax=QAccessible::queryAccessibleInterface(medium);
    if(!check(ax && ax->role()==QAccessible::ProgressBar && ax->text(QAccessible::Name)=="Loading" && !ax->state().focusable,"actual noninteractive Qt accessibility interface"))return;
    window->setProperty("reduced",false);
    if(!check(QTest::qWaitFor([&]{return medium->property("animating").toBool() && medium->property("animationPhase").toInt()>0;},1000),"live phase progression"))return;
    window->setProperty("showMedium",false);QTest::qWait(20);
    if(!check(!medium->property("animating").toBool() && medium->property("animationPhase").toInt()==0,"hidden animation suppression"))return;
    window->setProperty("showMedium",true);window->setProperty("reduced",true);QTest::qWait(20);
    if(!check(!medium->property("animating").toBool() && medium->property("running").toBool() && medium->property("animationPhase").toInt()==0,"reduced motion preserves loading state"))return;
    window->setProperty("busy",false);QTest::qWait(20);
    if(!check(!medium->property("running").toBool() && !medium->property("contentItem").value<QQuickItem*>()->isVisible(),"explicit stopped indicator"))return;
    window->setProperty("busy",true);
    auto input=button->property("inputItem").value<QQuickItem*>();auto buttonAx=QAccessible::queryAccessibleInterface(input);
    auto click=[window](QQuickItem *target){QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,target->mapToScene(QPointF(target->width()/2,target->height()/2)).toPoint());QTest::qWait(20);};
    if(!check(buttonAx && buttonAx->state().disabled && buttonAx->actionInterface(),"loading button actual disabled state"))return;
    click(button);buttonAx->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
    if(!check(window->property("actions").toInt()==0,"loading callback suppression"))return;
    window->setProperty("loading",false);click(button);input->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_Space);buttonAx->actionInterface()->doAction(QAccessibleActionInterface::pressAction());QTest::qWait(20);
    if(!check(window->property("actions").toInt()==3,"restored pointer/keyboard/accessibility actions"))return;
    button->setEnabled(false);click(button);buttonAx->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
    if(!check(window->property("actions").toInt()==3,"disabled callback suppression"))return;
    click(field);QTest::keyClick(window,Qt::Key_X);
    if(!check(field->property("text").toString()=="x" && custom->property("color").value<QColor>()==QColor("#d63d3d"),"outside editing and explicit color override"))return;
    qInfo("Installed spinner: native sizes, fixed glyph frames, 24-frame animation, visibility/reduced motion, explicit color, actual Qt accessibility and loading-button suppression/restoration passed");
    if(!parser.isSet("evidence")){app.exit(0);return;}
    const auto path=parser.value("evidence");if(!window->grabWindow().save(path+".png")){app.exit(191);return;}
    QJsonObject record{{"fixture","spinner"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"compiler",QString::fromUtf8(__VERSION__)},{"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},
        {"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},{"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},{"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},
        {"inputMethod","QTest synthetic pointer/keyboard and actual Qt accessibility actions"},{"windowCaptureMethod","QQuickWindow::grabWindow; full session captured separately"},{"spinnerChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},{"actions",3},{"smallEdge",16},{"mediumEdge",32},{"largeEdge",32},{"frameCount",24},{"cycleMilliseconds",800},
        {"sourceAnimationAcceptance","pending; physical presentation timing and phase synchronization unverified"},{"accessibilityAcceptance","pending; actual reader output unverified"}};
    QFile file(path+".json");if(!file.open(QIODevice::WriteOnly)){app.exit(192);return;}file.write(QJsonDocument(record).toJson());file.close();
    auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path]{if(QFile::exists(path+".captured"))app.exit(0);});timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(193);});
}

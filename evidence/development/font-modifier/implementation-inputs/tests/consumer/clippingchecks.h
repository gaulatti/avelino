#pragma once
static void runClippingConsumer(QQuickWindow *window, QGuiApplication &app,
                               const QCommandLineParser &parser, double textScale) {
    auto item=[window](const QString &name){return findVisualItem(window->contentItem(),name);};
    auto check=[&app](bool ok,const char *message){if(!ok){qCritical("Installed clipping: %s",message);app.exit(210);}return ok;};
    auto card=item("clipCard"),alert=item("clipAlert"),chip=item("clipChip");
    auto raw=item("clipLifecycle"),button=item("clipButton"),field=item("clipField");
    if(!check(card&&alert&&chip&&raw&&button&&field,"missing fixture"))return;
    const qreal dpr=window->devicePixelRatio();
    auto pixel=[window,dpr](QQuickItem *target,qreal x,qreal y){
        const auto point=target->mapToScene(QPointF(x,y));
        return window->grabWindow().pixelColor(qFloor(point.x()*dpr),qFloor(point.y()*dpr));
    };
    auto background=[window](QQuickItem *target,qreal x,qreal y){
        const auto point=target->mapToScene(QPointF(x,y));
        return int(point.x()/20)%2==0 ? QColor("#234567") : QColor("#123456");
    };
    for(auto target:{card,alert,chip}) {
        if(!check(target->property("roundedContentClipping").toBool(),"all three rounded masks active"))return;
        if(!check(pixel(target,0,0)==background(target,0,0),"transparent corners expose patterned background"))return;
    }
    if(!check(pixel(card,10,70)==QColor("#c03434") && pixel(alert,5,60)==QColor("#3445c0") && pixel(chip,chip->width()/2,chip->height()/2)==QColor("#34c045"),"opaque overflow remains inside each distinct outline"))return;
    if(!check(pixel(raw,0,0)==background(raw,0,0) && pixel(raw,100,75)==QColor("red") && pixel(raw,18,18)==QColor("yellow"),"first frame and source orientation"))return;
    window->setProperty("liveColor",QColor("blue"));QTest::qWait(30);
    if(!check(pixel(raw,100,75)==QColor("blue") && pixel(raw,18,18)==QColor("yellow"),"live source refresh preserves unchanged islands"))return;
    window->setProperty("sparseSource",true);QTest::qWait(30);
    if(!check(pixel(raw,10,75)==background(raw,10,75) && pixel(raw,100,75)==QColor("blue"),"opaque islands preserve transparent holes"))return;
    window->setProperty("sparseSource",false);QTest::qWait(30);
    window->setProperty("maskRadius",0);QTest::qWait(30);
    if(!check(pixel(raw,2,2)==QColor("blue"),"outline refresh without source replacement"))return;
    window->setProperty("sourcePresent",false);QTest::qWait(30);
    if(!check(pixel(raw,100,75)==background(raw,100,75),"empty source clears previous raster"))return;
    window->setProperty("sourcePresent",true);window->setProperty("maskRadius",24);QTest::qWait(30);
    if(!check(pixel(raw,100,75)==QColor("blue") && pixel(raw,0,0)==background(raw,0,0),"source and outline restoration"))return;
    raw->setWidth(180);raw->setHeight(100);QTest::qWait(30);
    if(!check(pixel(raw,179,99)==background(raw,179,99) && pixel(raw,90,50)==QColor("blue"),"resize regenerates mask and source layer"))return;
    raw->setVisible(false);QTest::qWait(30);
    if(!check(pixel(raw,90,50)==background(raw,90,50),"hidden content removal"))return;
    raw->setVisible(true);raw->setWidth(220);raw->setHeight(150);QTest::qWait(30);
    auto click=[window](QQuickItem *target){QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,target->mapToScene(QPointF(target->width()/2,target->height()/2)).toPoint());QTest::qWait(20);};
    auto input=button->property("inputItem").value<QQuickItem*>();auto ax=QAccessible::queryAccessibleInterface(input);
    if(!check(ax&&ax->role()==QAccessible::Button&&ax->actionInterface(),"real Qt accessibility interface through masked content"))return;
    click(button);input->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_Space);
    ax->actionInterface()->doAction(QAccessibleActionInterface::pressAction());QTest::qWait(20);
    if(!check(window->property("actions").toInt()==3,"pointer keyboard and accessibility actions"))return;
    click(field);QTest::keyClick(window,Qt::Key_X);
    if(!check(field->property("text").toString()=="x","live editing inside masked content"))return;
    qInfo("Installed clipping: three outlines, patterned transparent corners, source/path/size/empty/visibility refresh, actual input/focus/editing/accessibility passed");
    if(!parser.isSet("evidence")){app.exit(0);return;}
    const auto path=parser.value("evidence");if(!window->grabWindow().save(path+".png")){app.exit(211);return;}
    QJsonObject record{{"fixture","clipping"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"compiler",QString::fromUtf8(__VERSION__)},
        {"width",window->width()},{"height",window->height()},{"dpr",dpr},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},
        {"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},{"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},
        {"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},{"clippingChecks","passed"},{"layerLifecycleChecks","passed"},
        {"focusChecks","passed"},{"qtAccessibilityChecks","passed"},{"actions",3},{"outlineKinds",3},{"roundedContentClipping",true},
        {"inputMethod","QTest synthetic pointer/keyboard and actual Qt accessibility actions"},{"windowCaptureMethod","QQuickWindow::grabWindow; full output captured separately"},
        {"nativeAcceptance","pending; exact raster, transparent-corner hit regions, physical input/display and actual readers unverified"}};
    QFile file(path+".json");if(!file.open(QIODevice::WriteOnly)){app.exit(212);return;}file.write(QJsonDocument(record).toJson());file.close();
    auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path]{if(QFile::exists(path+".captured"))app.exit(0);});timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(213);});
}

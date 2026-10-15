#pragma once
static void runNavigationConsumer(QQuickWindow *window,QGuiApplication &app,const QCommandLineParser &parser,double textScale) {
    auto item=[window](const QString &name){return findVisualItem(window->contentItem(),name);};
    auto check=[&app](bool ok,const char *message){if(!ok){qCritical("Installed navigation: %s",message);app.exit(210);}return ok;};
    auto requests=[window]{return qjsvalue_cast<QVariantList>(window->property("requests").value<QJSValue>());};
    auto header=item("consumerPageHeader"),crumb=item("consumerBreadcrumb"),field=item("headerChildField"),action=item("headerChildAction");
    if(!check(header&&crumb&&field&&action,"missing header or breadcrumb"))return;
    const auto originalPath=window->property("path");
    auto narrow=item("narrowBreadcrumb"),rtl=item("rtlBreadcrumb");
    auto narrowBody=narrow ? narrow->property("presentationItem").value<QQuickItem*>():nullptr;
    auto rtlFirst=rtl ? findVisualItem(rtl,"bleeckerBreadcrumbItem0"):nullptr;
    auto rtlLast=rtl ? findVisualItem(rtl,"bleeckerBreadcrumbItem2"):nullptr;
    const auto expectedNarrowWidth=window->devicePixelRatio()<2 ? 140.0:138.5;
    if(!check(narrowBody&&qAbs(narrowBody->width()-expectedNarrowWidth)<1e-6&&narrowBody->height()==60&&rtlFirst&&rtlLast&&rtlFirst->x()>rtlLast->x(),"actual narrow and RTL item geometry"))return;
    auto click=[window](QQuickItem *target){QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,target->mapToScene(QPointF(target->width()/2,target->height()/2)).toPoint());QTest::qWait(20);};
    auto first=findVisualItem(crumb,"bleeckerBreadcrumbItem0"),last=findVisualItem(crumb,"bleeckerBreadcrumbItem2");
    auto input=action->property("inputItem").value<QQuickItem*>();
    auto ax=QAccessible::queryAccessibleInterface(input),crumbAx=QAccessible::queryAccessibleInterface(last);
    if(!check(ax&&ax->actionInterface()&&crumbAx&&crumbAx->role()==QAccessible::Button&&crumbAx->text(QAccessible::Name)=="Editions"&&crumbAx->actionInterface(),"actual Qt button roles/names/actions"))return;
    click(action);input->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_Space);ax->actionInterface()->doAction(QAccessibleActionInterface::pressAction());QTest::qWait(20);
    if(!check(window->property("count").toInt()==3,"header pointer/keyboard/Qt accessibility activation"))return;
    click(field);QTest::keyClick(window,Qt::Key_X);window->setProperty("heading","Updated title");QTest::qWait(20);
    if(!check(item("headerChildAction")==action&&field->hasActiveFocus()&&field->property("text").toString()=="x"&&window->property("mounts").toInt()==1,"producer update preserves caller identity/private state/focus"))return;
    header->setEnabled(false);click(action);ax->actionInterface()->doAction(QAccessibleActionInterface::pressAction());QTest::qWait(20);
    if(!check(ax->state().disabled&&window->property("count").toInt()==3,"disabled header action suppression"))return;
    header->setEnabled(true);click(last);last->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_Space);crumbAx->actionInterface()->doAction(QAccessibleActionInterface::pressAction());QTest::qWait(20);
    if(!check(requests()==QVariantList{2,2,2},"last logical item remains active through normal Qt input"))return;
    crumb->setEnabled(false);click(first);crumbAx->actionInterface()->doAction(QAccessibleActionInterface::pressAction());QTest::qWait(20);
    if(!check(crumbAx->state().disabled&&requests().size()==3,"disabled breadcrumb input suppression"))return;
    crumb->setEnabled(true);
    QTest::mousePress(window,Qt::LeftButton,Qt::NoModifier,first->mapToScene(QPointF(first->width()/2,first->height()/2)).toPoint());QTest::mouseMove(window,QPoint(820,540));QTest::mouseRelease(window,Qt::LeftButton,Qt::NoModifier,QPoint(820,540));QTest::qWait(20);
    if(!check(requests().size()==3,"outside release cancels breadcrumb request"))return;
    window->setProperty("path",QVariantList{QVariantMap{{"title","Only"}}});QTest::qWait(20);click(findVisualItem(crumb,"bleeckerBreadcrumbItem0"));
    if(!check(requests()==QVariantList{2,2,2,0},"caller array replacement and logical index"))return;
    window->setProperty("replaceAction",true);QTest::qWait(20);window->setProperty("replaceAction",false);QTest::qWait(20);
    if(!check(window->property("mounts").toInt()==2&&window->property("unmounts").toInt()==1&&window->property("count").toInt()==0,"explicit action replacement resets private state"))return;
    window->setProperty("showHeader",false);QTest::qWait(20);window->setProperty("showHeader",true);QTest::qWait(20);
    if(!check(window->property("mounts").toInt()==3&&window->property("unmounts").toInt()==2&&item("headerChildField")->property("text").toString().isEmpty(),"header remount creates fresh content"))return;
    click(item("navigationOutsideField"));QTest::keyClick(window,Qt::Key_Y);
    if(!check(item("navigationOutsideField")->property("text").toString()=="y","continued outside editing"))return;
    window->setProperty("path",originalPath);QTest::qWait(20);
    qInfo("Installed navigation: producer/index callbacks, caller identity/state/focus, replacement/remount, canceled/disabled input and real Qt accessibility passed");
    if(!parser.isSet("evidence")){app.exit(0);return;}
    const auto path=parser.value("evidence");if(!window->grabWindow().save(path+".png")){app.exit(211);return;}
    QJsonObject record{{"fixture","navigation"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"compiler",QString::fromUtf8(__VERSION__)},{"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},
        {"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},{"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},{"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},
        {"inputMethod","QTest synthetic pointer/keyboard and actual Qt accessibility actions"},{"windowCaptureMethod","QQuickWindow::grabWindow; full output captured separately"},{"navigationChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},
        {"mounts",3},{"unmounts",2},{"requests",QJsonArray{2,2,2,0}},{"narrowWidth",narrowBody->width()},{"narrowHeight",narrowBody->height()},{"rtlVisualOrder","logical first at right"},{"modelRestoredForCapture",true},
        {"acceptance","pending; native font/symbol/raster, source keyboard, physical sessions and actual reader output unverified"}};
    QFile file(path+".json");if(!file.open(QIODevice::WriteOnly)){app.exit(212);return;}file.write(QJsonDocument(record).toJson());file.close();
    auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path]{if(QFile::exists(path+".captured"))app.exit(0);});timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(213);});
}

#pragma once
static void runSidebarBrandConsumer(QQuickWindow *window,QGuiApplication &app,const QCommandLineParser &parser,double textScale) {
    auto item=[window](const QString &name){return findVisualItem(window->contentItem(),name);};
    auto check=[&app](bool ok,const char *message){if(!ok){qCritical("Installed sidebar/brand: %s",message);app.exit(220);}return ok;};
    auto home=item("homeSidebarItem"),edition=item("editionSidebarItem"),disabled=item("disabledSidebarItem"),field=item("sidebarOutsideField"),mark=item("consumerBrandMark"),lockup=item("consumerBrandLockup");
    if(!check(home&&edition&&disabled&&field&&mark&&lockup,"missing fixture"))return;
    auto input=edition->property("inputItem").value<QQuickItem*>();auto ax=QAccessible::queryAccessibleInterface(input);
    auto click=[window](QQuickItem *target,QPointF point){QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,target->mapToScene(point).toPoint());QTest::qWait(20);};
    if(!check(ax&&ax->role()==QAccessible::Button&&ax->text(QAccessible::Name)=="Editions"&&ax->actionInterface(),"real Qt button role/name/actions"))return;
    click(input,QPointF(1,1));click(input,QPointF(input->width()-8,input->height()/2));
    if(!check(window->property("requests").toInt()==2&&window->property("page").toString()=="home"&&!edition->property("selected").toBool(),"complete rectangular hit region and caller selection ownership"))return;
    input->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_Space);ax->actionInterface()->doAction(QAccessibleActionInterface::pressAction());QTest::qWait(20);
    if(!check(window->property("requests").toInt()==4,"keyboard and accessibility requests"))return;
    click(field,QPointF(20,20));QTest::keyClick(window,Qt::Key_X);window->setProperty("page","editions");window->setProperty("editionTitle","Updated editions");QTest::qWait(20);
    if(!check(edition->property("selected").toBool()&&!home->property("selected").toBool()&&item("editionSidebarItem")==edition&&field->hasActiveFocus()&&field->property("text").toString()=="x"&&window->property("requests").toInt()==4,"producer changes preserve controls/focus and do not emit requests"))return;
    if(!check(ax->text(QAccessible::Name)=="Updated editions"&&ax->text(QAccessible::Description)=="Selected","live accessibility metadata"))return;
    auto disabledInput=disabled->property("inputItem").value<QQuickItem*>();auto disabledAx=QAccessible::queryAccessibleInterface(disabledInput);
    click(disabledInput,QPointF(10,10));disabledAx->actionInterface()->doAction(QAccessibleActionInterface::pressAction());QTest::qWait(20);
    if(!check(disabledAx->state().disabled&&window->property("requests").toInt()==4,"disabled action suppression"))return;
    QTest::mousePress(window,Qt::LeftButton,Qt::NoModifier,input->mapToScene(QPointF(20,20)).toPoint());QTest::mouseMove(window,QPoint(820,540));QTest::mouseRelease(window,Qt::LeftButton,Qt::NoModifier,QPoint(820,540));QTest::qWait(20);
    if(!check(window->property("requests").toInt()==4,"outside release cancellation"))return;
    auto rtl=item("rtlSidebarItem"),bar=findVisualItem(rtl,"bleeckerSidebarSelectionBar");
    auto rtlBody=rtl->property("presentationItem").value<QQuickItem*>();auto narrow=item("narrowSidebarItem")->property("presentationItem").value<QQuickItem*>();
    if(!check(bar&&rtlBody&&bar->x()==rtlBody->width()-2&&narrow->width()==120&&narrow->height()==40,"RTL leading bar and narrow layout"))return;
    auto image=mark->property("presentationItem").value<QQuickItem*>();
    window->setProperty("logoSize",1);QTest::qWait(20);
    auto shot=window->grabWindow();const auto origin=image->mapToScene(QPointF(0,0));const auto dpr=window->devicePixelRatio();
    if(!check(image->width()==1&&image->height()==1&&shot.pixelColor(qRound((origin.x()+0.5)*dpr),qRound((origin.y()+0.5)*dpr))==window->color(),"one-point template source coverage"))return;
    window->setProperty("logoSize",64.5);window->setProperty("brandName","Editorial workspace");QTest::qWait(20);
    if(!check(image->width()==64.5&&image->height()==64.5&&image->x()==(250-64.5)/2&&image->y()==(170-64.5)/2,"fractional logo dimensions and caller frame centering"))return;
    auto name=findVisualItem(lockup,"bleeckerBrandLockupName");
    if(!check(name&&name->property("resolvedPixelSize").toDouble()==20,"fixed source brand font"))return;
    auto nameAx=QAccessible::queryAccessibleInterface(name);
    if(!check(nameAx&&nameAx->role()==QAccessible::StaticText&&nameAx->text(QAccessible::Name)=="Editorial workspace","updated brand text accessibility"))return;
    QFile asset(QStringLiteral(":/qt/qml/Avelino/brand/BleeckerLogo.png"));
    if(!check(asset.open(QIODevice::ReadOnly),"embedded pinned source logo"))return;
    const auto checksum=QCryptographicHash::hash(asset.readAll(),QCryptographicHash::Sha256).toHex();
    if(!check(checksum=="3eadafd84a1f3b37261bad85b8a8e5512ed7aa9b3baae38aa8321cc3a6cbb9c2","embedded asset bytes"))return;
    click(field,QPointF(20,20));QTest::keyClick(window,Qt::Key_Y);
    if(!check(field->property("text").toString()=="xy","continued outside editing"))return;
    qInfo("Installed sidebar/brand: caller selection/action binding, full hit region, disabled/canceled input, focus/editing, Qt accessibility, RTL/narrow layout, pinned mask, tiny/fractional sizing and producer updates passed");
    if(!parser.isSet("evidence")){app.exit(0);return;}
    const auto path=parser.value("evidence");if(!window->grabWindow().save(path+".png")){app.exit(221);return;}
    QJsonObject record{{"fixture","sidebar-brand"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"compiler",QString::fromUtf8(__VERSION__)},{"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},
        {"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},{"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},{"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},
        {"inputMethod","QTest synthetic pointer/keyboard and actual Qt accessibility actions"},{"windowCaptureMethod","QQuickWindow::grabWindow; full output captured separately"},{"sidebarBrandChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},{"requests",4},{"callerSelection","editions"},{"logoSize",64.5},{"pinnedAssetSha256",QString::fromLatin1(checksum)},
        {"acceptance","pending; native symbols/raster, source keyboard/focus, physical sessions and actual reader output unverified"}};
    QFile file(path+".json");if(!file.open(QIODevice::WriteOnly)){app.exit(222);return;}file.write(QJsonDocument(record).toJson());file.close();
    auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path]{if(QFile::exists(path+".captured"))app.exit(0);});timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(223);});
}

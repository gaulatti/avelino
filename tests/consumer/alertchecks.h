#pragma once
static void runAlertConsumer(QQuickWindow *window,QGuiApplication &app,const QCommandLineParser &parser,double textScale) {
    auto item=[window](const QString &name){return findVisualItem(window->contentItem(),name);};
    auto check=[&app](bool ok,const char *message){if(!ok){qCritical("Installed alert: %s",message);app.exit(200);}return ok;};
    auto alert=item("consumerAlert"),outside=item("alertOutsideField");
    auto loaded=[alert]{return alert->property("loadedContent").value<QQuickItem*>();};
    if(!check(alert&&outside&&loaded(),"missing fixture"))return;
    auto child=item("alertChildAction"),field=item("alertChildField");
    if(!check(child&&field,"missing generic controls"))return;
    auto input=child->property("inputItem").value<QQuickItem*>();auto ax=QAccessible::queryAccessibleInterface(input);
    auto heading=item("bleeckerAlertTitle");auto headingAx=QAccessible::queryAccessibleInterface(heading);
    if(!check(ax&&ax->actionInterface()&&headingAx&&headingAx->role()==QAccessible::StaticText&&headingAx->text(QAccessible::Name)=="Edition ready","actual Qt control/title accessibility"))return;
    auto click=[window](QQuickItem *target){QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,target->mapToScene(QPointF(target->width()/2,target->height()/2)).toPoint());QTest::qWait(20);};
    click(child);input->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_Space);ax->actionInterface()->doAction(QAccessibleActionInterface::pressAction());QTest::qWait(20);
    if(!check(window->property("counter").toInt()==3,"pointer/keyboard/accessibility activation"))return;
    click(field);QTest::keyClick(window,Qt::Key_X);const auto first=loaded();
    window->setProperty("heading","Updated alert title");window->setProperty("kind","error");QTest::qWait(20);
    if(!check(loaded()==first&&window->property("mounts").toInt()==1&&field->property("text").toString()=="x"&&field->hasActiveFocus(),"producer update preserves factory/private state/focus"))return;
    click(child);alert->setEnabled(false);click(child);QTest::keyClick(window,Qt::Key_Space);ax->actionInterface()->doAction(QAccessibleActionInterface::pressAction());QTest::qWait(20);
    if(!check(ax->state().disabled&&window->property("counter").toInt()==4,"disabled child callback suppression"))return;
    alert->setEnabled(true);window->setProperty("replacement",true);QTest::qWait(20);
    if(!check(window->property("unmounts").toInt()==1,"replacement destroys child"))return;
    window->setProperty("replacement",false);QTest::qWait(20);
    if(!check(window->property("mounts").toInt()==2&&window->property("counter").toInt()==0&&item("alertChildField")->property("text").toString().isEmpty(),"recreated private state is fresh"))return;
    window->setProperty("showContent",false);QTest::qWait(20);
    if(!check(!loaded()&&window->property("unmounts").toInt()==2,"empty factory removes child"))return;
    window->setProperty("showContent",true);QTest::qWait(20);click(outside);QTest::keyClick(window,Qt::Key_Y);
    if(!check(window->property("mounts").toInt()==3&&window->property("actions").toInt()==4&&outside->property("text").toString()=="y","restoration and continued outside editing"))return;
    auto narrow=item("consumerNarrowAlert");auto presentation=narrow->property("presentationItem").value<QQuickItem*>();
    if(!check(presentation&&presentation->width()<=180,"actual narrow fitted presentation"))return;
    qInfo("Installed alert: fitted layout, caller-owned generic content, producer/state/focus preservation, replacement/removal, real Qt accessibility and disabled actions passed");
    if(!parser.isSet("evidence")){app.exit(0);return;}
    const auto path=parser.value("evidence");if(!window->grabWindow().save(path+".png")){app.exit(201);return;}
    QJsonObject record{{"fixture","alert"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"compiler",QString::fromUtf8(__VERSION__)},{"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},
        {"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},{"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},{"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},
        {"inputMethod","QTest synthetic pointer/keyboard and actual Qt accessibility actions"},{"windowCaptureMethod","QQuickWindow::grabWindow; full output captured separately"},{"alertChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},{"mounts",3},{"unmounts",2},{"actions",4},{"counter",0},{"narrowWidth",presentation->width()},{"roundedContentClipping",alert->property("roundedContentClipping").toBool()},
        {"accessibilityAcceptance","pending; actual reader output unverified"},{"genericClippingAcceptance","pending; software rounded overflow and physical/GPU equivalence unaccepted"}};
    QFile file(path+".json");if(!file.open(QIODevice::WriteOnly)){app.exit(202);return;}file.write(QJsonDocument(record).toJson());file.close();
    auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path]{if(QFile::exists(path+".captured"))app.exit(0);});timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(203);});
}

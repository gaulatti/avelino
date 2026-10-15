#pragma once
static void runTabsConsumer(QQuickWindow *window, QGuiApplication &app,
                            const QCommandLineParser &parser, double textScale) {
    auto item=[window](const QString &name) { return findVisualItem(window->contentItem(),name); };
    auto tabs=item("tabs"),segments=item("segments"),disabled=item("disabledTabs"),narrow=item("narrowTabs"),rtl=item("rtlTabs"),numeric=item("numericTabs"),next=item("tabsNext");
    auto check=[&app](bool ok,const char *message) { if (!ok) { qCritical("Installed tabs: %s",message);app.exit(140); } return ok; };
    if (!check(tabs && segments && disabled && narrow && rtl && numeric && next,"missing fixture")) return;
    auto segment=[](QQuickItem *control,int index) { return findVisualItem(control,QStringLiteral("bleeckerSegment%1").arg(index)); };
    auto click=[window](QQuickItem *control) { QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,control->mapToScene(QPointF(control->width()/2,control->height()/2)).toPoint());QTest::qWait(30); };
    const auto first=segment(tabs,0),middle=segment(tabs,1),last=segment(tabs,2);
    const auto accessible=QAccessible::queryAccessibleInterface(first);
    const auto middleAccessible=QAccessible::queryAccessibleInterface(middle);
    qInfo("Tabs interface: present=%d role=%d name=%s action=%d disabled=%d",bool(accessible),accessible ? int(accessible->role()) : -1,accessible ? qPrintable(accessible->text(QAccessible::Name)) : "missing",bool(accessible && accessible->actionInterface()),middleAccessible ? middleAccessible->state().disabled : -1);
    if (!check(accessible && accessible->role()==QAccessible::Button && accessible->text(QAccessible::Name)=="Alpha"
        && accessible->actionInterface() && middleAccessible && middleAccessible->state().disabled,"Qt button interfaces")) return;
    click(middle);click(segment(disabled,2));
    if (!check(window->property("activations").toInt()==0,"disabled pointer")) return;
    click(last);
    if (!check(window->property("chosen").toString()=="c" && segments->property("selection").toString()=="c" && window->property("activations").toInt()==1,"pointer/shared model")) return;
    window->setProperty("chosen","external");
    if (!check(tabs->property("selection").toString()=="external" && segments->property("selection").toString()=="external" && !first->property("selected").toBool() && !last->property("selected").toBool(),"binding after pointer")) return;
    first->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_Space);QTest::keyClick(window,Qt::Key_Tab);
    if (!check(last->hasActiveFocus() && !middle->hasActiveFocus(),"disabled traversal")) return;
    QTest::keyClick(window,Qt::Key_Space);
    accessible->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
    if (!check(window->property("chosen").toString()=="a" && window->property("activations").toInt()==4,"keyboard/accessibility caller update")) return;
    window->setProperty("chosen","c");
    if (!check(tabs->property("selection").toString()=="c" && last->property("selected").toBool(),"external update after Qt actions")) return;
    click(segment(numeric,1));numeric->setProperty("selection",0);
    if (!check(numeric->property("selection").metaType().id()==QMetaType::Int && segment(numeric,0)->property("selected").toBool(),"numeric identity")) return;
    if (!check(segment(rtl,0)->x()>segment(rtl,2)->x() && narrow->width()==140 && narrow->height()>40,"RTL and constrained wrapping")) return;
    next->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_X);
    if (!check(next->property("text").toString()=="x" && next->hasActiveFocus(),"continued editing")) return;
    qInfo("Installed tabs: pointer, keyboard, Qt accessibility action, disabled traversal, typed selection, shared model and subsequent external updates passed");
    if (!parser.isSet("evidence")) { app.exit(0);return; }
    const auto path=parser.value("evidence");
    if (!window->grabWindow().save(path+".png")) { app.exit(141);return; }
    QJsonObject record{{"fixture","tabs"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},
        {"compiler",QString::fromUtf8(__VERSION__)},{"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},
        {"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},
        {"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},{"appearance",parser.isSet("dark") ? "dark" : "light"},{"textScale",textScale},
        {"inputMethod","QTest synthetic in-process pointer and keyboard events; Qt accessibility press action"},
        {"windowCaptureMethod","QQuickWindow::grabWindow; full session captured separately"},
        {"tabsChecks","passed"},{"callerBindingChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},
        {"selectedValue",window->property("chosen").toString()},{"activations",window->property("activations").toInt()},
        {"accessibilityAcceptance","pending; Qt interfaces and synthetic actions are not screen-reader acceptance"},
        {"sourceKeyboardAcceptance","pending; Linux adapter is verified separately from native source input"}};
    QFile file(path+".json");if (!file.open(QIODevice::WriteOnly)) { app.exit(142);return; }
    file.write(QJsonDocument(record).toJson());file.close();
    auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path] { if (QFile::exists(path+".captured")) app.exit(0); });
    timer->start(100);QTimer::singleShot(10000,&app,[&app] { app.exit(143); });
}

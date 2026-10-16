#pragma once
static void runPaginationConsumer(QQuickWindow *window, QGuiApplication &app,
                                  const QCommandLineParser &parser, double textScale) {
    auto item=[window](const QString &name) {return findVisualItem(window->contentItem(),name);};
    auto pager=item("pager"),icon=item("iconButton"),narrow=item("narrowPager"),rtl=item("rtlPager"),empty=item("emptyPager"),disabled=item("disabledPager"),field=item("paginationNext");
    auto check=[&app](bool ok,const char *message) {if (!ok) {qCritical("Installed pagination: %s",message);app.exit(150);}return ok;};
    if (!check(pager && icon && narrow && rtl && empty && disabled && field,"missing fixture")) return;
    auto input=[](QQuickItem *button) {return button->property("inputItem").value<QQuickItem*>();};
    auto previous=findVisualItem(pager,"bleeckerPreviousPage"),next=findVisualItem(pager,"bleeckerNextPage"),label=findVisualItem(pager,"bleeckerPaginationLabel");
    if (!check(previous && next && label && input(previous) && input(next) && input(icon),"missing owned input")) return;
    auto click=[window](QQuickItem *button) {QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,button->mapToScene(QPointF(button->width()/2,button->height()/2)).toPoint());QTest::qWait(30);};
    auto prevAx=QAccessible::queryAccessibleInterface(input(previous)),nextAx=QAccessible::queryAccessibleInterface(input(next));
    auto labelAx=QAccessible::queryAccessibleInterface(label),iconAx=QAccessible::queryAccessibleInterface(input(icon));
    if (!check(prevAx && nextAx && labelAx && iconAx && prevAx->role()==QAccessible::Button && prevAx->text(QAccessible::Name)=="Previous page"
        && nextAx->text(QAccessible::Name)=="Next page" && iconAx->text(QAccessible::Name)=="Continue"
        && labelAx->role()==QAccessible::StaticText && labelAx->text(QAccessible::Name)=="Page 4 of 8","Qt roles and names")) return;
    click(next);
    if (!check(window->property("page").toInt()==5 && window->property("requests").toInt()==1,"pointer/caller update")) return;
    prevAx->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
    input(previous)->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_Space);
    if (!check(window->property("page").toInt()==3 && window->property("requests").toInt()==3,"keyboard/accessibility caller update")) return;
    QTest::keyClick(window,Qt::Key_Tab);
    if (!check(input(next)->hasActiveFocus(),"button traversal")) return;
    window->setProperty("page",7);window->setProperty("applyRequest",false);click(next);
    if (!check(window->property("requested").toInt()==8 && pager->property("page").toInt()==7 && window->property("requests").toInt()==4,"caller owns application of request")) return;
    window->setProperty("applyRequest",true);window->setProperty("page",1);click(previous);
    if (!check(window->property("requests").toInt()==4 && prevAx->state().disabled,"lower bound")) return;
    window->setProperty("page",8);input(previous)->forceActiveFocus();QTest::keyClick(window,Qt::Key_Space);
    if (!check(window->property("page").toInt()==7 && window->property("requests").toInt()==5,"upper bound traversal")) return;
    pager->setEnabled(false);nextAx->actionInterface()->doAction(QAccessibleActionInterface::pressAction());click(next);
    if (!check(nextAx->state().disabled && window->property("requests").toInt()==5,"disabled pointer/accessibility rejection")) return;
    pager->setEnabled(true);window->setProperty("count",3);click(previous);
    if (!check(window->property("page").toInt()==6 && window->property("requests").toInt()==6 && !next->isEnabled(),"count update without page repair")) return;
    window->setProperty("count",8);window->setProperty("page",4);nextAx->actionInterface()->doAction(QAccessibleActionInterface::pressAction());window->setProperty("page",4);
    if (!check(pager->property("page").toInt()==4 && window->property("requests").toInt()==7 && labelAx->text(QAccessible::Name)=="Page 4 of 8","external binding after all input paths")) return;
    click(icon);input(icon)->forceActiveFocus();QTest::keyClick(window,Qt::Key_Space);icon->setEnabled(false);iconAx->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
    if (!check(window->property("iconCalls").toInt()==2 && iconAx->state().disabled,"icon actions and disabled interface")) return;
    icon->setEnabled(true);icon->setProperty("accessibilityLabel","Updated action");
    if (!check(iconAx->text(QAccessible::Name)=="Updated action","dynamic icon name")) return;
    auto narrowLabel=findVisualItem(narrow,"bleeckerPaginationLabel");
    qInfo("Pagination layout: narrowLabel=%g height=%g content=%g rtl=%g/%g empty=%d/%d",narrowLabel ? narrowLabel->height() : -1,narrow->height(),narrow->property("contentSize").toSizeF().width(),findVisualItem(rtl,"bleeckerPreviousPage")->x(),findVisualItem(rtl,"bleeckerNextPage")->x(),findVisualItem(empty,"bleeckerNextPage")->isEnabled(),findVisualItem(empty,"bleeckerPreviousPage")->isEnabled());
    if (!check(narrowLabel && narrowLabel->height()==30 && narrow->height()==36 && narrow->property("contentSize").toSizeF().width()<=140
        && findVisualItem(rtl,"bleeckerPreviousPage")->x()>findVisualItem(rtl,"bleeckerNextPage")->x()
        && !findVisualItem(empty,"bleeckerNextPage")->isEnabled() && !findVisualItem(empty,"bleeckerPreviousPage")->isEnabled(),"wrapped label, RTL and zero count")) return;
    auto longLabel=findVisualItem(item("longPager"),"bleeckerPaginationLabel");
    auto longAx=QAccessible::queryAccessibleInterface(longLabel);
    if (!check(longAx && longAx->text(QAccessible::Name)=="Page 1,000,000,000 of 2,000,000,000","source locale number grouping")) return;
    field->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_X);
    if (!check(field->property("text").toString()=="x","continued editing")) return;
    qInfo("Installed pagination: pointer, keyboard, Qt accessibility actions, disabled bounds, caller ownership and subsequent external page/count updates passed");
    if (!parser.isSet("evidence")) {app.exit(0);return;}
    const auto path=parser.value("evidence");if (!window->grabWindow().save(path+".png")) {app.exit(151);return;}
    QJsonObject record{{"fixture","pagination"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},
        {"compiler",QString::fromUtf8(__VERSION__)},{"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},
        {"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},
        {"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},{"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},
        {"inputMethod","QTest synthetic pointer/keyboard and actual Qt accessibility press actions"},{"windowCaptureMethod","QQuickWindow::grabWindow; full session captured separately"},
        {"paginationChecks","passed"},{"callerBindingChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},
        {"page",window->property("page").toInt()},{"requests",window->property("requests").toInt()},
        {"sourceKeyboardAcceptance","pending; source keyboard equivalence unverified"},{"symbolAcceptance","pending; original chevron paths are unaccepted candidates"},
        {"accessibilityAcceptance","pending; Qt interfaces and synthetic actions are not screen-reader acceptance"}};
    QFile file(path+".json");if (!file.open(QIODevice::WriteOnly)) {app.exit(152);return;}
    file.write(QJsonDocument(record).toJson());file.close();
    auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path] {if (QFile::exists(path+".captured")) app.exit(0);});
    timer->start(100);QTimer::singleShot(10000,&app,[&app] {app.exit(153);});
}

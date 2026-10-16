#pragma once
static void runSliderConsumer(QQuickWindow *window, QGuiApplication &app,
                              const QCommandLineParser &parser, double textScale) {
    auto item=[window](const QString &name) { return findVisualItem(window->contentItem(),name); };
    auto slider=item("slider"), disabled=item("disabledSlider"), narrow=item("narrowSlider"), next=item("sliderNext");
    auto stepped=item("steppedSlider"), odd=item("oddSlider"), decimal=item("decimalSlider"), dense=item("denseSlider");
    auto check=[&app](bool ok,const char *message) { if (!ok) { qCritical("Installed slider: %s",message);app.exit(130); } return ok; };
    if (!check(slider && disabled && narrow && next && stepped && odd && decimal && dense,"missing fixture")) return;
    auto input=[](QQuickItem *control) { return findVisualItem(control,"bleeckerSliderInput"); };
    auto click=[window](QQuickItem *control,qreal x) { QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,control->mapToScene(QPointF(x,control->height()/2)).toPoint());QTest::qWait(30); };
    auto value=[](QQuickItem *control) { return control->property("value").toDouble(); };
    auto near=[](double a,double b) { return std::abs(a-b)<0.00000001; };
    auto accessible=QAccessible::queryAccessibleInterface(input(slider));
    auto values=accessible ? accessible->valueInterface() : nullptr;
    auto actions=accessible ? accessible->actionInterface() : nullptr;
    qInfo("Slider interface: present=%d role=%d name=%s values=%d min=%g max=%g",bool(accessible),accessible ? int(accessible->role()) : -1,accessible ? qPrintable(accessible->text(QAccessible::Name)) : "missing",bool(values),values ? values->minimumValue().toDouble() : -1,values ? values->maximumValue().toDouble() : -1);
    if (!check(accessible && accessible->role()==QAccessible::Slider && accessible->text(QAccessible::Name)=="Amount"
        && values && values->minimumValue().toDouble()==0 && values->maximumValue().toDouble()==1,"Qt slider value interface")) return;
    click(slider,319);
    if (!check(window->property("amount").toDouble()==1 && window->property("edits").toInt()==1,"pointer/caller update")) return;
    click(slider,1);
    if (!check(window->property("amount").toDouble()==0 && window->property("edits").toInt()==2,"minimum endpoint")) return;
    window->setProperty("amount",0.35);
    QTest::mousePress(window,Qt::LeftButton,Qt::NoModifier,slider->mapToScene(QPointF(115,8)).toPoint());
    QTest::mouseMove(window,slider->mapToScene(QPointF(235,8)).toPoint(),30);
    QTest::mouseRelease(window,Qt::LeftButton,Qt::NoModifier,slider->mapToScene(QPointF(235,8)).toPoint());
    if (!check(near(window->property("amount").toDouble(),0.75),"drag binding")) return;
    values->setCurrentValue(0.5);
    if (!check(near(window->property("amount").toDouble(),0.5) && actions,"accessibility setter/caller boundary")) return;
    actions->doAction(QAccessibleActionInterface::increaseAction());
    if (!check(near(window->property("amount").toDouble(),0.6),"accessibility increment/caller boundary")) return;
    window->setProperty("amount",0.8);
    if (!check(near(value(slider),0.8) && near(values->currentValue().toDouble(),0.8),"binding survives pointer and accessibility edits")) return;
    const auto edits=window->property("edits").toInt();click(disabled,319);
    const auto disabledAccessible=QAccessible::queryAccessibleInterface(input(disabled));
    if (!check(disabledAccessible && disabledAccessible->state().disabled,"disabled interface state")) return;
    disabledAccessible->valueInterface()->setCurrentValue(0.9);
    disabledAccessible->actionInterface()->doAction(QAccessibleActionInterface::increaseAction());
    if (!check(value(disabled)==0.35 && !input(disabled)->isEnabled() && window->property("edits").toInt()==edits,"disabled pointer")) return;
    input(slider)->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_Tab);
    if (!check(input(narrow)->hasActiveFocus() && !input(disabled)->hasActiveFocus(),"disabled keyboard traversal")) return;
    QTest::keyClick(window,Qt::Key_Backtab);QTest::keyClick(window,Qt::Key_Right);
    if (!check(near(window->property("amount").toDouble(),0.9) && input(slider)->property("visualFocus").toBool(),"Qt keyboard adapter/caller")) return;
    input(stepped)->forceActiveFocus();QTest::keyClick(window,Qt::Key_Right);QTest::keyClick(window,Qt::Key_Right);QTest::keyClick(window,Qt::Key_Right);
    if (!check(value(stepped)==22,"stepped keyboard upper bound")) return;
    click(odd,odd->width()-1);
    if (!check(near(value(odd),0.9) && odd->property("to").toDouble()==1 && odd->property("intervals").toInt()==3,"partial final interval")) return;
    odd->setProperty("value",1.0);
    if (!check(value(odd)==1 && odd->property("position").toDouble()==1,"caller value preserved beyond final selectable step")) return;
    click(decimal,decimal->width()-1);
    if (!check(value(decimal)==0.30000000000000004 && decimal->property("intervals").toInt()==3,"source decimal endpoint ULP")) return;
    next->forceActiveFocus(Qt::TabFocusReason);
    for (const auto c:QStringLiteral("continued")) QTest::keyClick(window,Qt::Key(c.toUpper().unicode()));
    QTest::qWait(60);
    if (!check(next->property("text").toString()=="continued" && slider->height()==16 && narrow->height()==16
        && dense->property("intervals").toInt()==1000000,"continued editing/fixed size/dense tick bound")) return;
    qInfo("Installed slider: pointer/drag/caller binding, native Qt keyboard/accessibility updates, disabled traversal, fractional intervals and dense ticks passed; source keyboard equivalence pending");
    if (!parser.isSet("evidence")) { app.exit(0);return; }
    const auto path=parser.value("evidence");
    if (!window->grabWindow().save(path+".png")) { app.exit(131);return; }
    QJsonObject record{{"fixture","slider"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},
        {"compiler",QString::fromUtf8(__VERSION__)},{"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},
        {"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},
        {"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},{"appearance",parser.isSet("dark") ? "dark" : "light"},{"textScale",textScale},
        {"inputMethod","QTest synthetic in-process pointer and keyboard events"},{"windowCaptureMethod","QQuickWindow::grabWindow; full session captured separately"},
        {"sliderChecks","passed"},{"callerBindingChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},
        {"sourceHeight",slider->height()},{"sourceKeyboardAcceptance","pending; source helper did not obtain focus"},
        {"accessibilityAcceptance","pending; Qt interfaces and synthetic value actions are not screen-reader acceptance"}};
    QFile file(path+".json");if (!file.open(QIODevice::WriteOnly)) { app.exit(132);return; }
    file.write(QJsonDocument(record).toJson());file.close();
    auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path] { if (QFile::exists(path+".captured")) app.exit(0); });
    timer->start(100);QTimer::singleShot(10000,&app,[&app] { app.exit(133); });
}

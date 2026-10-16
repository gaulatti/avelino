#pragma once
static void runSearchFieldConsumer(QQuickWindow *window, QGuiApplication &app,
                                   const QCommandLineParser &parser, double textScale) {
    auto field=findVisualItem(window->contentItem(),"searchField");
    auto next=findVisualItem(window->contentItem(),"searchNextField");
    auto disabled=findVisualItem(window->contentItem(),"disabledSearch");
    auto narrow=findVisualItem(window->contentItem(),"narrowSearch");
    auto check=[&app](bool ok,const char *message) { if (!ok) { qCritical("Installed search field: %s",message); app.exit(110); } return ok; };
    if (!check(field && next && disabled && narrow,"missing component")) return;
    auto click=[window](QQuickItem *item,qreal x=-1) {
        QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,item->mapToScene(QPointF(x<0 ? item->width()/2 : x,item->height()/2)).toPoint());
        QTest::qWait(40);
    };
    auto type=[window](const QString &text) { for (const auto c:text) QTest::keyClick(window,Qt::Key(c.toUpper().unicode())); };
    auto accessible=QAccessible::queryAccessibleInterface(field);
    if (!check(accessible && accessible->role()==QAccessible::EditableText && !accessible->state().passwordEdit
        && accessible->text(QAccessible::Name)=="Search editions" && field->height()==40*textScale,"editor interface/geometry")) return;
    click(field,60); type("news");
    auto action=findVisualItem(field,"bleeckerSearchClear");
    auto clearAccessible=action ? QAccessible::queryAccessibleInterface(action) : nullptr;
    if (!check(window->property("query").toString()=="news" && window->property("edits").toInt()==4
        && accessible->text(QAccessible::Value)=="news" && clearAccessible
        && clearAccessible->role()==QAccessible::Button && clearAccessible->text(QAccessible::Name)=="Clear search","editing/action interface")) return;
    click(action);
    if (!check(window->property("query").toString().isEmpty() && window->property("edits").toInt()==5
        && field->hasActiveFocus() && !findVisualItem(field,"bleeckerSearchClear"),"pointer clear/caller/focus")) return;
    window->setProperty("query",QStringLiteral("External query"));
    action=findVisualItem(field,"bleeckerSearchClear");
    field->setEnabled(false); click(action);
    if (!check(field->property("text").toString()=="External query" && window->property("edits").toInt()==5 && !action->isEnabled(),"disabled clear")) return;
    field->setEnabled(true); field->forceActiveFocus(Qt::TabFocusReason);
    QTest::keyClick(window,Qt::Key_Tab);
    if (!check(action->hasActiveFocus() && action->property("visualFocus").toBool(),"clear keyboard focus")) return;
    QTest::keyClick(window,Qt::Key_Space); QTest::qWait(20);
    if (!check(window->property("query").toString().isEmpty() && window->property("edits").toInt()==6 && field->hasActiveFocus(),"keyboard clear/model")) return;
    type("again"); QTest::keyClick(window,Qt::Key_Return);
    if (!check(window->property("query").toString()=="again" && window->property("accepts").toInt()==1,"continued editing/accept")) return;
    QTest::keyClick(window,Qt::Key_Tab); QTest::keyClick(window,Qt::Key_Tab);
    if (!check(next->hasActiveFocus() && !disabled->hasActiveFocus(),"disabled traversal")) return;
    type("continued");
    const auto leading=findVisualItem(field,"bleeckerTextFieldLeading");
    const auto trailing=findVisualItem(field,"bleeckerTextFieldTrailing");
    if (!check(next->property("text").toString()=="continued" && leading && trailing
        && leading->width()==16.5 && trailing->width()==18.5 && narrow->height()==40*textScale,"slot sizes/next editor")) return;
    qInfo("Installed search field: editing, caller binding, pointer/keyboard clear, disabled traversal, Return, fixed slots and real Qt interfaces passed");
    if (!parser.isSet("evidence")) { app.exit(0); return; }
    const auto path=parser.value("evidence");
    if (!window->grabWindow().save(path+".png")) { app.exit(111); return; }
    QJsonObject record{{"fixture","search-field"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},
        {"compiler",QString::fromUtf8(__VERSION__)},{"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},
        {"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},
        {"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},{"appearance",parser.isSet("dark") ? "dark" : "light"},{"textScale",textScale},
        {"inputMethod","QTest synthetic in-process pointer and keyboard events"},{"windowCaptureMethod","QQuickWindow::grabWindow; full session captured separately"},
        {"searchFieldChecks","passed"},{"clearBindingChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},
        {"sourceHeight",field->height()},{"leadingWidth",leading->width()},{"clearWidth",trailing->width()},
        {"symbolAcceptance","pending; original magnifier/xmark candidates"},{"accessibilityAcceptance","pending; interface queries are not screen-reader acceptance"}};
    QFile file(path+".json");if (!file.open(QIODevice::WriteOnly)) { app.exit(112);return; }
    file.write(QJsonDocument(record).toJson());file.close();
    auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path] { if (QFile::exists(path+".captured")) app.exit(0); });
    timer->start(100);QTimer::singleShot(10000,&app,[&app] { app.exit(113); });
}

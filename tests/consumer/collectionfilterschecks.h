#pragma once
static void runCollectionFiltersConsumer(QQuickWindow *window, QGuiApplication &app,
                                         const QCommandLineParser &parser, double textScale) {
    auto item=[window](const QString &name) { return findVisualItem(window->contentItem(),name); };
    auto filters=item("collection"), disabled=item("disabledCollection"), next=item("collectionNext"), narrow=item("narrowChip");
    auto check=[&app](bool ok,const char *message) { if (!ok) { qCritical("Installed collection filters: %s",message); app.exit(120); } return ok; };
    if (!check(filters && disabled && next && narrow,"missing fixture")) return;
    auto search=findVisualItem(filters,"bleeckerCollectionSearch");
    auto action=findVisualItem(filters,"bleeckerFilterAction"), remove=findVisualItem(filters,"bleeckerFilterRemove");
    auto click=[window](QQuickItem *target,qreal x=-1) {
        QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,target->mapToScene(QPointF(x<0 ? target->width()/2 : x,target->height()/2)).toPoint()); QTest::qWait(30);
    };
    auto type=[window](const QString &text) { for (const auto c:text) QTest::keyClick(window,Qt::Key(c.toUpper().unicode())); };
    auto group=QAccessible::queryAccessibleInterface(filters), edit=QAccessible::queryAccessibleInterface(search);
    auto primary=QAccessible::queryAccessibleInterface(action), removal=QAccessible::queryAccessibleInterface(remove);
    if (!check(group && group->role()==QAccessible::Grouping && edit && edit->role()==QAccessible::EditableText
        && primary && primary->role()==QAccessible::Button && primary->text(QAccessible::Name)=="Edition"
        && removal && removal->role()==QAccessible::Button && removal->text(QAccessible::Name)=="Remove Edition","real Qt interfaces")) return;
    click(search,60); type("news");
    if (!check(window->property("query").toString()=="news" && window->property("edits").toInt()==4,"caller query editing")) return;
    click(findVisualItem(search,"bleeckerSearchClear"));
    if (!check(window->property("query").toString().isEmpty() && window->property("edits").toInt()==5 && search->hasActiveFocus(),"clear callback/focus")) return;
    type("again"); QTest::keyClick(window,Qt::Key_Return);
    if (!check(window->property("accepts").toInt()==1 && window->property("query").toString()=="again","Return and continued binding")) return;
    click(action);
    if (!check(window->property("selected").toBool() && window->property("activations").toInt()==1 && window->property("removals").toInt()==0,"independent label action")) return;
    action->forceActiveFocus(Qt::TabFocusReason); QTest::keyClick(window,Qt::Key_Tab);
    if (!check(remove->hasActiveFocus() && remove->property("visualFocus").toBool(),"remove keyboard focus")) return;
    QTest::keyClick(window,Qt::Key_Space); QTest::qWait(30);
    if (!check(!window->property("hasChip").toBool() && window->property("removals").toInt()==1
        && search->width()==filters->width() && !findVisualItem(filters,"bleeckerFilterAction"),"caller removal and reclaimed width")) return;
    auto disabledSearch=findVisualItem(disabled,"bleeckerCollectionSearch"), disabledAction=findVisualItem(disabled,"bleeckerFilterAction");
    click(disabledSearch,60); type("x"); click(disabledAction);
    if (!check(disabledSearch->property("text").toString()=="Disabled query" && !disabledAction->isEnabled(),"disabled composition")) return;
    window->setProperty("tallContent",true); QTest::qWait(20);
    if (!check(filters->height()==84 && search->y()==(84-40*textScale)/2 && search->width()==filters->width()-110,"tall content sizing")) return;
    window->setProperty("tallContent",false); window->setProperty("hasChip",true); QTest::qWait(20);
    action=findVisualItem(filters,"bleeckerFilterAction"); remove=findVisualItem(filters,"bleeckerFilterRemove");
    remove->forceActiveFocus(Qt::TabFocusReason); QTest::keyClick(window,Qt::Key_Tab);
    if (!check(findVisualItem(narrow,"bleeckerFilterAction")->hasActiveFocus() && !disabledSearch->hasActiveFocus(),"disabled focus traversal")) return;
    QTest::keyClick(window,Qt::Key_Tab); QTest::keyClick(window,Qt::Key_Tab);
    if (!check(next->hasActiveFocus(),"chip to editor traversal")) return;
    type("continued");
    const bool rounded=narrow->property("roundedContentClipping").toBool();
    qInfo("Collection final geometry: height=%g wrapped=%g rounded=%d api=%d",filters->height(),narrow->height(),rounded,int(window->rendererInterface()->graphicsApi()));
    if (!check(next->property("text").toString()=="continued" && narrow->height()==45
        && filters->height()==40*textScale && rounded,"wrap/scaling/renderer capability")) return;
    qInfo("Installed collection filters: query binding, clear, Return, independent caller actions, removal, slot resizing, disabled focus and Qt interfaces passed");
    if (!parser.isSet("evidence")) { app.exit(0); return; }
    const auto path=parser.value("evidence");
    if (!window->grabWindow().save(path+".png")) { app.exit(121); return; }
    QJsonObject record{{"fixture","collection-filters"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},
        {"compiler",QString::fromUtf8(__VERSION__)},{"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},
        {"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},
        {"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},{"appearance",parser.isSet("dark") ? "dark" : "light"},{"textScale",textScale},
        {"inputMethod","QTest synthetic in-process pointer and keyboard events"},{"windowCaptureMethod","QQuickWindow::grabWindow; full session captured separately"},
        {"collectionFilterChecks","passed"},{"callerBindingChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},
        {"sourceHeight",filters->height()},{"wrappedChipHeight",narrow->height()},{"roundedContentClipping",rounded},
        {"symbolAcceptance","pending; original xmark candidate"},{"accessibilityAcceptance","pending; interface queries are not screen-reader acceptance"}};
    QFile file(path+".json");if (!file.open(QIODevice::WriteOnly)) { app.exit(122);return; }
    file.write(QJsonDocument(record).toJson());file.close();
    auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path] { if (QFile::exists(path+".captured")) app.exit(0); });
    timer->start(100);QTimer::singleShot(10000,&app,[&app] { app.exit(123); });
}

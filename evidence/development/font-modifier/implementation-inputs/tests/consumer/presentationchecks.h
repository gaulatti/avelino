#pragma once
static void runPresentationConsumer(QQuickWindow *window,QGuiApplication &app,
                                    const QCommandLineParser &parser,double textScale) {
    auto item=[window](const QString &name){return findVisualItem(window->contentItem(),name);};
    auto check=[&app](bool ok,const char *message){if(!ok){qCritical("Installed presentation states: %s",message);app.exit(180);}return ok;};
    auto click=[window](QQuickItem *target){QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,target->mapToScene(QPointF(target->width()/2,target->height()/2)).toPoint());QTest::qWait(30);};
    auto input=[](QQuickItem *control){return control->property("inputItem").value<QQuickItem*>();};
    auto empty=item("emptyState"),action=item("emptyStateAction"),error=item("errorState"),retry=item("errorStateAction"),overlay=item("loadingOverlay"),underlying=item("underlyingAction"),outside=item("outsideAction"),field=item("presentationOutsideField");
    if(!check(empty && action && error && retry && overlay && underlying && outside && field,"missing fixture"))return;
    auto ax=QAccessible::queryAccessibleInterface(input(action));
    if(!check(ax && ax->role()==QAccessible::Button && ax->actionInterface() && ax->text(QAccessible::Name)=="Create 0","actual action accessibility interface"))return;
    click(action);input(action)->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_Space);QTest::qWait(30);
    ax->actionInterface()->doAction(QAccessibleActionInterface::pressAction());QTest::qWait(30);
    if(!check(action->property("count").toInt()==3 && window->property("actions").toInt()==3,"pointer, keyboard and actual Qt accessibility actions"))return;
    window->setProperty("heading",QStringLiteral("Updated title"));window->setProperty("message",QStringLiteral("Updated message"));
    auto heading=findVisualItem(empty,"bleeckerEmptyStateTitle"),message=findVisualItem(empty,"bleeckerEmptyStateMessage");
    if(!check(item("emptyStateAction")==action && action->property("count").toInt()==3 && heading->property("text").toString()=="Updated title" && message->property("text").toString()=="Updated message" && window->property("created").toInt()==1,"producer updates preserve action identity and state"))return;
    click(retry);auto retryAx=QAccessible::queryAccessibleInterface(input(retry));error->setEnabled(false);
    if(!check(retryAx && retryAx->state().disabled && retryAx->actionInterface(),"actual disabled retry interface"))return;
    retryAx->actionInterface()->doAction(QAccessibleActionInterface::pressAction());click(retry);
    if(!check(retry->property("count").toInt()==1,"disabled pointer/accessibility rejection"))return;
    error->setEnabled(true);input(retry)->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_Space);QTest::qWait(30);
    if(!check(retry->property("count").toInt()==2 && error->property("title").toString()=="Something went wrong","error default title and normal keyboard"))return;
    click(field);window->setProperty("emptyPresent",false);QTest::qWait(30);
    if(!check(!item("emptyStateAction") && window->property("destroyed").toInt()==1 && field->hasActiveFocus(),"removal destroys subtree without taking outside focus"))return;
    window->setProperty("emptyPresent",true);QTest::qWait(30);action=item("emptyStateAction");
    empty=item("emptyState");heading=empty ? findVisualItem(empty,"bleeckerEmptyStateTitle") : nullptr;message=empty ? findVisualItem(empty,"bleeckerEmptyStateMessage") : nullptr;
    if(!check(action && action->property("count").toInt()==0 && window->property("created").toInt()==2,"recreation resets private state"))return;
    input(action)->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_Space);QTest::qWait(30);
    if(!check(action->property("count").toInt()==1 && window->property("actions").toInt()==4,"recreated action remains usable"))return;
    click(underlying);
    if(!check(window->property("underlying").toInt()==1,"successful underlying-input positive control"))return;
    click(field);window->setProperty("loading",true);QTest::qWait(30);
    if(!check(field->hasActiveFocus(),"overlay insertion preserves existing outside focus"))return;
    QTest::keyClick(window,Qt::Key_X);click(underlying);click(outside);
    if(!check(window->property("underlying").toInt()==1 && window->property("outside").toInt()==1 && field->property("text").toString()=="x","overlay blocks inside pointer while outside action/editing remain usable"))return;
    overlay->setProperty("message",QStringLiteral("Updated loading message"));
    auto loadingLabel=findVisualItem(overlay,"bleeckerLoadingOverlayMessage"),spinner=findVisualItem(overlay,"bleeckerLoadingOverlaySpinner");
    auto spinnerAx=spinner ? QAccessible::queryAccessibleInterface(spinner) : nullptr;
    if(!check(loadingLabel && loadingLabel->property("text").toString()=="Updated loading message" && loadingLabel->property("resolvedPixelSize").toDouble()==14 && heading && message && heading->property("resolvedPixelSize").toDouble()==17 && message->property("resolvedPixelSize").toDouble()==13 && spinnerAx && spinnerAx->role()==QAccessible::ProgressBar,"message producer, fixed font and actual progress interface"))return;
    window->setProperty("loading",false);QTest::qWait(30);click(underlying);
    if(!check(window->property("underlying").toInt()==2,"overlay removal restores underlying pointer input"))return;
    click(field);QTest::keyClick(window,Qt::Key_Y);
    if(!check(field->property("text").toString()=="xy","continued outside editing"))return;
    window->setProperty("loading",true);QTest::qWait(30);
    qInfo("Installed presentation states: source-sized presentation, stateful action factories, producer updates, keyboard/focus, disabled/Qt accessibility actions and bounded loading pointer blocking passed");
    if(!parser.isSet("evidence")){app.exit(0);return;}
    const auto path=parser.value("evidence");if(!window->grabWindow().save(path+".png")){app.exit(181);return;}
    QJsonObject record{{"fixture","presentation-states"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"compiler",QString::fromUtf8(__VERSION__)},
        {"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},
        {"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},{"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},
        {"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},{"inputMethod","QTest synthetic pointer/keyboard and actual Qt accessibility actions"},
        {"windowCaptureMethod","QQuickWindow::grabWindow; full session captured separately"},{"presentationChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},{"overlayPointerChecks","passed"},
        {"created",window->property("created").toInt()},{"destroyed",window->property("destroyed").toInt()},{"actions",window->property("actions").toInt()},
        {"underlying",window->property("underlying").toInt()},{"outside",window->property("outside").toInt()},{"roundedContentClipping",overlay->property("roundedContentClipping").toBool()},
        {"sourceKeyboardAcceptance","pending; source keyboard/focus/modal equivalence unverified"},{"accessibilityAcceptance","pending; actual reader output unverified"}};
    QFile file(path+".json");if(!file.open(QIODevice::WriteOnly)){app.exit(182);return;}file.write(QJsonDocument(record).toJson());file.close();
    auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path]{if(QFile::exists(path+".captured"))app.exit(0);});timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(183);});
}

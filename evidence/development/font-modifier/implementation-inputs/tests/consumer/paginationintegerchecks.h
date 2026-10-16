#pragma once
static void runPaginationIntegerConsumer(QQuickWindow *window,QGuiApplication &app,
                                         const QCommandLineParser &parser,double textScale) {
    auto item=[window](const QString &name){return findVisualItem(window->contentItem(),name);};
    auto pager=item("exactPager"),minimum=item("minimumPager"),safe=item("safePager"),narrow=item("narrowExactPager"),field=item("exactNextField");
    auto check=[&app](bool ok,const char *message){if (!ok){qCritical("Installed exact pagination: %s",message);app.exit(160);}return ok;};
    if (!check(pager && minimum && safe && narrow && field,"missing fixture")) return;
    const qreal nativeNarrowWidth=window->devicePixelRatio()==1 ? 260 : 259.5;
    for (const qreal offered : {257.,260.,264.}) {
        narrow->setWidth(offered);
        const qreal expectedWidth=offered==257 ? 257 : nativeNarrowWidth;
        // Qt positioners batch layout until a frame; elapsed time is not readiness.
        const bool settled=QTest::qWaitFor([narrow,expectedWidth] {
            const auto body=narrow->property("contentSize").toSizeF();
            return body.width()==expectedWidth && body.height()==45;
        },1000);
        if (!settled) {
            const auto body=narrow->property("contentSize").toSizeF();
            qCritical("Pagination resize offered=%.17g DPR=%.17g body=%.17gx%.17g expected=%.17gx45",
                offered,window->devicePixelRatio(),body.width(),body.height(),expectedWidth);
        }
        if (!check(settled,"source wrapped body width/height through resize")) return;
    }
    narrow->setWidth(260);
    auto button=[](QQuickItem *pager,bool next){return findVisualItem(pager,next ? "bleeckerNextPage":"bleeckerPreviousPage");};
    auto input=[](QQuickItem *button){return button->property("inputItem").value<QQuickItem*>();};
    auto click=[window](QQuickItem *button){QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,button->mapToScene(QPointF(button->width()/2,button->height()/2)).toPoint());QTest::qWait(30);};
    auto next=button(pager,true),previous=button(pager,false),label=findVisualItem(pager,"bleeckerPaginationLabel");
    auto ax=QAccessible::queryAccessibleInterface(input(previous)),labelAx=QAccessible::queryAccessibleInterface(label);
    if (!check(ax && labelAx && labelAx->text(QAccessible::Name)=="Page 9,223,372,036,854,775,806 of 9,223,372,036,854,775,807","initial exact accessible label")) return;
    click(next);
    if (!check(window->property("requested").toString()=="9223372036854775807" && !next->isEnabled() && pager->property("page").toString()=="9223372036854775807","pointer exact upper endpoint")) return;
    click(next);if (!check(window->property("requests").toInt()==1,"disabled upper rejection")) return;
    ax->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
    if (!check(window->property("requested").toString()=="9223372036854775806","exact accessibility request")) return;
    window->setProperty("page",QStringLiteral("9007199254740993"));
    input(previous)->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_Space);
    if (!check(window->property("requested").toString()=="9007199254740992" && window->property("requests").toInt()==3,"keyboard beyond JavaScript safe range")) return;
    window->setProperty("page",QStringLiteral("-9223372036854775808"));
    if (!check(!previous->isEnabled() && labelAx->text(QAccessible::Name).startsWith("Page -9,223,372,036,854,775,808"),"external minimum and accessible label")) return;
    click(next);
    if (!check(window->property("requested").toString()=="-9223372036854775807" && window->property("requests").toInt()==4,"minimum increment without overflow")) return;
    window->setProperty("page",QStringLiteral("9223372036854775806"));
    if (!check(pager->property("page").toString()=="9223372036854775806" && !button(minimum,false)->isEnabled()
        && findVisualItem(safe,"bleeckerPaginationLabel")->property("text").toString().contains("9,007,199,254,740,993"),"external binding and independent exact models")) return;
    field->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_X);
    if (!check(field->property("text").toString()=="x","continued editing")) return;
    qInfo("Installed exact pagination: full Int64 labels, pointer/keyboard/accessibility string requests, disabled extremes and external caller updates passed");
    if (!parser.isSet("evidence")){app.exit(0);return;}
    const auto path=parser.value("evidence");if (!window->grabWindow().save(path+".png")){app.exit(161);return;}
    QJsonObject record{{"fixture","pagination-integers"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},
        {"compiler",QString::fromUtf8(__VERSION__)},{"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},
        {"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},
        {"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},{"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},
        {"inputMethod","QTest synthetic pointer/keyboard and actual Qt accessibility actions"},{"windowCaptureMethod","QQuickWindow::grabWindow; full session captured separately"},
        {"paginationIntegerChecks","passed"},{"callerBindingChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},
        {"wrappedBodyWidth",narrow->property("contentSize").toSizeF().width()},{"wrappedBodyHeight",narrow->property("contentSize").toSizeF().height()},
        {"exactPage",window->property("page").toString()},{"requests",window->property("requests").toInt()},
        {"sourceKeyboardAcceptance","pending; source keyboard equivalence unverified"},{"accessibilityAcceptance","pending; actual screen-reader output unverified"}};
    QFile file(path+".json");if (!file.open(QIODevice::WriteOnly)){app.exit(162);return;}file.write(QJsonDocument(record).toJson());file.close();
    auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path]{if(QFile::exists(path+".captured")) app.exit(0);});timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(163);});
}

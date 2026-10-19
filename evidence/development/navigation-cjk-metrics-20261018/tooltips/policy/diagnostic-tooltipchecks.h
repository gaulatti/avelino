#pragma once
#include <QSignalSpy>

static void runTooltipConsumer(QQuickWindow *window,QGuiApplication &app,
                               const QCommandLineParser &parser,double textScale) {
    auto check=[&](bool ok,const QString &message){if(!ok){qCritical("Installed Tooltip: %s",qPrintable(message));app.exit(255);}return ok;};
    auto fixture=window->property("primaryFixture").value<QQuickItem*>();
    auto caller=window->property("primaryCaller").value<QQuickItem*>();
    auto help=window->property("primaryHelp").value<QObject*>();
    auto field=findVisualItem(window->contentItem(),"tooltipHintEditor");
    auto secondary=window->property("secondaryHelp").value<QObject*>();
    if(!check(fixture && caller && help && field && secondary,"Public caller and help objects missing"))return;
    auto input=caller->property("inputItem").value<QQuickItem*>();
    auto popup=help->property("presentation").value<QObject*>();
    if(!check(input && popup,"Input or owned template popup missing"))return;
    auto frame=[&](QQuickWindow *owner){
        // Diagnostic only: release hidden owned-popup graphics and scene graph.
        if(owner!=window){owner->setPersistentGraphics(false);owner->setPersistentSceneGraph(false);}
        QSignalSpy displayed(owner,&QQuickWindow::frameSwapped);owner->update();
        return check(displayed.count()>0 || displayed.wait(5000),"Visible window did not display a frame");
    };
    auto move=[&](QQuickItem *target){QTest::mouseMove(window,target->mapToScene(QPointF(target->width()/2,target->height()/2)).toPoint());QCoreApplication::processEvents();};
    auto away=[&](){QTest::mouseMove(window,QPoint(window->width()-2,window->height()-2));QCoreApplication::processEvents();};
    QString phase="initial";
    auto waitVisible=[&](QObject *owner,bool visible){return check(QTest::qWaitFor([&]{return owner->property("visible").toBool()==visible;},3000),
        QStringLiteral("%1: expected visible=%2; window active=%3, exposed=%4, caller window=%5")
            .arg(phase).arg(visible).arg(window->isActive()).arg(window->isExposed()).arg(caller->window()==window));};
    window->requestActivate();
    if(!check(QTest::qWaitFor([&]{return window->isActive();},3000),"Parent window did not activate"))return;
    auto ax=QAccessible::queryAccessibleInterface(input);
    if(!check(ax && ax->role()==QAccessible::Button && ax->text(QAccessible::Name)=="Publish 0"
        && ax->text(QAccessible::Description)=="Publishes the selected edition","Actual Qt accessible caller name, role or hint"))return;
    input->forceActiveFocus(Qt::TabFocusReason);away();
    if(!frame(window))return;
    const auto before=window->grabWindow();
    fixture->setProperty("helpAttached",false);QCoreApplication::processEvents();if(!frame(window))return;
    const auto bare=window->grabWindow();
    if(before!=bare) {
        const auto diagnostic=parser.isSet("evidence") ? parser.value("evidence"):QStringLiteral("tooltip-closed-diagnostic");
        before.save(diagnostic+"-closed-attached.png");bare.save(diagnostic+"-closed-bare.png");
        qWarning("Closed caller diagnostic: active=%d focus=%d sizes %dx%d / %dx%d",window->isActive(),input->hasActiveFocus(),before.width(),before.height(),bare.width(),bare.height());
    }
    if(!check(before==bare,"Help attachment changed closed caller pixels"))return;
    fixture->setProperty("helpAttached",true);QTest::qWait(10);
    QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,input->mapToScene(QPointF(input->width()/2,input->height()/2)).toPoint());
    away();QTest::qWait(10);
    if(!check(fixture->property("localValue").toInt()==1,"Caller input did not retain local counter"))return;
    const auto parent=caller->parentItem();const auto geometry=QRectF(caller->position(),caller->size());
    phase="first caller hover";move(caller);if(!waitVisible(help,true))return;
    auto content=popup->property("contentItem").value<QQuickItem*>();
    auto tooltipWindow=content ? content->window():nullptr;
    if(!check(tooltipWindow && tooltipWindow!=window && tooltipWindow->isVisible() && popup->property("popupType").toInt()==1
        && (tooltipWindow->flags() & Qt::WindowType_Mask)==Qt::ToolTip,"Real separate tooltip window required"))return;
    if(!frame(tooltipWindow))return;
    if(!check(input->hasActiveFocus(),"Tooltip stole caller focus"))return;
    const auto shown=tooltipWindow->grabWindow();
    window->setProperty("hint","Reviews the published edition");QTest::qWait(10);
    if(!check(window->property("primaryCaller").value<QQuickItem*>()==caller && caller->parentItem()==parent
        && QRectF(caller->position(),caller->size())==geometry && fixture->property("localValue").toInt()==1
        && fixture->property("appears").toInt()==1 && fixture->property("destroyedCount").toInt()==0,"Hint update changed caller identity, geometry or state"))return;
    if(!check(ax->text(QAccessible::Name)=="Publish 1" && ax->text(QAccessible::Description)=="Reviews the published edition"
        && popup->property("text").toString()=="Publishes the selected edition","AX hint and visible popup text must update independently"))return;
    if(!frame(tooltipWindow))return;
    const auto afterHint=tooltipWindow->grabWindow();
    if(!check(shown==afterHint,"Visible popup changed during hint update"))return;
    phase="caller departure";away();if(!waitVisible(help,false))return;
    phase="updated hint re-entry";move(caller);if(!waitVisible(help,true) || !check(popup->property("text").toString()=="Reviews the published edition","Next presentation did not read the updated hint"))return;
    phase="field hover";away();move(field);if(!waitVisible(secondary,true) || !check(!help->property("visible").toBool(),"Multiple help owners remained presented"))return;
    away();if(!waitVisible(secondary,false))return;
    field->forceActiveFocus(Qt::TabFocusReason);QTest::keyClick(window,Qt::Key_A,Qt::ControlModifier);QTest::keyClick(window,Qt::Key_Q);
    if(!check(window->property("hint").toString()=="q","Caller editor binding did not receive actual Qt typing"))return;
    phase="caller after typing";move(caller);if(!waitVisible(help,true))return;
    fixture->setProperty("mounted",false);QCoreApplication::processEvents();if(!waitVisible(help,false))return;
    fixture->setProperty("mounted",true);QTest::qWait(10);
    if(!check(fixture->property("localValue").toInt()==0 && fixture->property("appears").toInt()==2
        && fixture->property("destroyedCount").toInt()==1,"Remount did not create fresh caller state"))return;
    phase="remounted caller";caller=window->property("primaryCaller").value<QQuickItem*>();away();move(caller);if(!waitVisible(help,true))return;
    content=popup->property("contentItem").value<QQuickItem*>();tooltipWindow=content ? content->window():nullptr;
    if(!check(tooltipWindow && tooltipWindow!=window && tooltipWindow->isVisible(),"Remounted tooltip window missing") || !frame(tooltipWindow))return;
    qInfo("Installed Tooltip: closed pixels, caller identity/input/binding, retained shown text, real separate popup, focus and Qt accessibility passed");
    if(!parser.isSet("evidence")){app.exit(0);return;}
    const auto path=parser.value("evidence");
    if(!check(window->grabWindow().save(path+".png") && tooltipWindow->grabWindow().save(path+"-tooltip.png")
        && shown.save(path+"-native-default-tooltip.png") && afterHint.save(path+"-updated-hint-tooltip.png"),"Evidence images could not be written"))return;
    const QJsonObject record{{"fixture","tooltip"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},
        {"dpr",window->devicePixelRatio()},{"width",window->width()},{"height",window->height()},
        {"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},
        {"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},
        {"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},
        {"inputMethod","QTest synthetic pointer and keyboard; actual Qt accessible interfaces"},
        {"windowCaptureMethod","QQuickWindow::grabWindow separately for parent and tooltip; compositor captured separately"},
        {"tooltipChecks","passed"},{"qtAccessibilityChecks","passed"},{"focusChecks","passed"},
        {"separateTooltipWindow",true},{"tooltipWindowType",int(tooltipWindow->flags() & Qt::WindowType_Mask)},
        {"tooltipWidth",tooltipWindow->width()},{"tooltipHeight",tooltipWindow->height()},
        {"defaultTooltipPhysicalWidth",shown.width()},{"defaultTooltipPhysicalHeight",shown.height()},
        {"popupText",popup->property("text").toString()},{"delay",popup->property("delay").toInt()},
        {"timeout",popup->property("timeout").toInt()},{"closedBodyIdentical",true},{"shownHintPixelsIdentical",true},
        {"sourceNativeAcceptance","pending; native timing/dismissal, system font, dark/vibrancy and shown-popup coverage unresolved"},
        {"accessibilityAcceptance","pending; actual reader output unverified"}};
    QFile file(path+".json");if(!check(file.open(QIODevice::WriteOnly),"Evidence metadata could not be written"))return;
    file.write(QJsonDocument(record).toJson());file.close();
    auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path]{if(QFile::exists(path+".captured"))app.exit(0);});
    timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(254);});
}

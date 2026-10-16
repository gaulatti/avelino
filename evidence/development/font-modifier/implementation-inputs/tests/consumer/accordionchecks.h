#pragma once
static void runAccordionConsumer(QQuickWindow *window,QGuiApplication &app,
                                 const QCommandLineParser &parser,double textScale) {
    auto item=[window](const QString &name){return findVisualItem(window->contentItem(),name);};
    auto accordion=item("accordion"),disabled=item("disabledAccordion"),narrow=item("narrowAccordion"),initial=item("initialAccordion"),mirrored=item("mirroredAccordion"),next=item("accordionNextField");
    auto check=[&app](bool ok,const char *message){if(!ok){qCritical("Installed accordion: %s",message);app.exit(170);}return ok;};
    if(!check(accordion && disabled && narrow && initial && mirrored && next,"missing fixture"))return;
    auto input=[](QQuickItem *control){return control->property("inputItem").value<QQuickItem*>();};
    auto loaded=[](QQuickItem *control){return control->property("loadedContent").value<QQuickItem*>();};
    auto click=[window](const QPointF &point){QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,point.toPoint());QTest::qWait(30);};
    auto titleClick=[&click](QQuickItem *control){auto title=findVisualItem(control,"bleeckerAccordionTitle");click(title->mapToScene(QPointF(5,title->height()/2)));};
    auto header=input(accordion);auto ax=QAccessible::queryAccessibleInterface(header);
    if(!check(ax && ax->role()==QAccessible::Button && ax->actionInterface() && ax->text(QAccessible::Name)=="Edition details" && ax->text(QAccessible::Description)=="Collapsed","actual Qt header interface"))return;
    window->setProperty("initial",true);
    if(!check(!accordion->property("expanded").toBool() && !loaded(accordion) && window->property("created").toInt()==0,"initializer is read once"))return;
    click(header->mapToScene(QPointF(header->width()/2,7)));
    if(!check(!accordion->property("expanded").toBool() && window->property("created").toInt()==0,"blank spacer must not activate"))return;
    titleClick(accordion);
    auto first=loaded(accordion);auto field=item("accordionBodyField");auto apply=item("accordionApply");
    if(!check(first && field && apply && accordion->property("expanded").toBool() && window->property("created").toInt()==1 && ax->text(QAccessible::Description)=="Expanded","pointer expansion and content creation"))return;
    click(field->mapToScene(QPointF(30,field->height()/2)));QTest::keyClick(window,Qt::Key_X);
    click(apply->mapToScene(QPointF(apply->width()/2,apply->height()/2)));
    if(!check(field->property("text").toString()=="x" && first->property("applied").toInt()==1 && window->property("actions").toInt()==1,"normal child editing and action path"))return;
    window->setProperty("heading",QStringLiteral("Updated title"));
    if(!check(loaded(accordion)==first && ax->text(QAccessible::Name)=="Updated title" && first->property("applied").toInt()==1,"title binding preserves child state"))return;
    field->forceActiveFocus(Qt::TabFocusReason);ax->actionInterface()->doAction(QAccessibleActionInterface::pressAction());QTest::qWait(30);
    if(!check(!loaded(accordion) && !accordion->property("expanded").toBool() && window->property("destroyed").toInt()==1 && header->hasActiveFocus(),"accessibility collapse, destruction and restored focus"))return;
    QTest::keyClick(window,Qt::Key_Space);QTest::qWait(30);field=item("accordionBodyField");
    if(!check(loaded(accordion) && field && field->property("text").toString().isEmpty() && loaded(accordion)->property("applied").toInt()==0 && window->property("created").toInt()==2,"keyboard reopening resets child state"))return;
    QTest::keyClick(window,Qt::Key_Tab);
    if(!check(field->hasActiveFocus(),"tab enters created content"))return;
    ax->actionInterface()->doAction(QAccessibleActionInterface::pressAction());QTest::qWait(30);
    if(!check(!loaded(accordion) && window->property("destroyed").toInt()==2 && header->hasActiveFocus(),"second collapse restores traversal"))return;
    auto disabledAx=QAccessible::queryAccessibleInterface(input(disabled));
    if(!check(disabledAx && disabledAx->state().disabled && disabledAx->actionInterface(),"actual disabled Qt interface"))return;
    disabledAx->actionInterface()->doAction(QAccessibleActionInterface::pressAction());titleClick(disabled);
    if(!check(disabled->property("expanded").toBool(),"disabled activation rejection"))return;
    titleClick(narrow);
    if(!check(narrow->property("expanded").toBool() && narrow->height()==104,"wrapped header and content geometry"))return;
    initial->setProperty("initiallyExpanded",false);
    if(!check(initial->property("expanded").toBool(),"open initializer stays owned after external update"))return;
    auto glyph=findVisualItem(mirrored,"bleeckerAccordionChevron"),label=findVisualItem(mirrored,"bleeckerAccordionTitle");
    if(!check(glyph && label && glyph->x()<label->x(),"mirrored header layout"))return;
    click(glyph->mapToScene(QPointF(glyph->width()/2,glyph->height()/2)));
    if(!check(mirrored->property("expanded").toBool() && loaded(mirrored) && loaded(mirrored)->parentItem()->x()>0,"mirrored glyph activation and leading content placement"))return;
    ax->actionInterface()->doAction(QAccessibleActionInterface::pressAction());QTest::qWait(30);window->setProperty("bodyCopy",QStringLiteral("Updated body copy"));
    field=item("accordionBodyField");auto body=item("accordionBodyCopy");
    if(!check(field && body && body->property("text").toString()=="Updated body copy" && window->property("created").toInt()==3 && window->property("destroyed").toInt()==2,"later producer update reaches recreated content"))return;
    click(field->mapToScene(QPointF(30,field->height()/2)));QTest::keyClick(window,Qt::Key_Z);
    click(next->mapToScene(QPointF(30,next->height()/2)));QTest::keyClick(window,Qt::Key_X);
    if(!check(field->property("text").toString()=="z" && next->property("text").toString()=="x","continued content and outside editing"))return;
    qInfo("Installed accordion: initializer ownership, title/spacer/glyph input, child creation/destruction/reset, keyboard/focus, disabled and actual Qt accessibility actions passed");
    if(!parser.isSet("evidence")){app.exit(0);return;}
    const auto path=parser.value("evidence");if(!window->grabWindow().save(path+".png")){app.exit(171);return;}
    QJsonObject record{{"fixture","accordion"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"compiler",QString::fromUtf8(__VERSION__)},
        {"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},
        {"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},{"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},
        {"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},{"inputMethod","QTest synthetic pointer/keyboard and actual Qt accessibility actions"},
        {"windowCaptureMethod","QQuickWindow::grabWindow; full session captured separately"},{"accordionChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},
        {"created",window->property("created").toInt()},{"destroyed",window->property("destroyed").toInt()},{"actions",window->property("actions").toInt()},
        {"expanded",accordion->property("expanded").toBool()},{"narrowHeight",narrow->height()},
        {"sourceKeyboardAcceptance","pending; source keyboard/focus equivalence unverified"},{"accessibilityAcceptance","pending; actual reader output unverified"}};
    QFile file(path+".json");if(!file.open(QIODevice::WriteOnly)){app.exit(172);return;}file.write(QJsonDocument(record).toJson());file.close();
    auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path]{if(QFile::exists(path+".captured"))app.exit(0);});timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(173);});
}

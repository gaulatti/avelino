#pragma once

static void runHeroCarouselGallery(QQuickWindow *window,QGuiApplication &app,const QCommandLineParser &parser){
    const auto prefix=parser.value("hero-carousel-report");
    auto check=[&](bool value,const char *message){if(!value){qCritical("HeroCarousel gallery: %s",message);app.exit(99);}return value;};
    auto fixture=window->property("primaryFixture").value<QQuickItem*>();
    if(!check(fixture&&!prefix.isEmpty()&&!QFile::exists(prefix+".json"),"Fresh report prefix and fixture required"))return;
    const QPointer<QQuickItem> original=fixture->property("control").value<QQuickItem*>();
    auto caller=[&](int index){QVariant result;if(!original||!QMetaObject::invokeMethod(original,"slideAt",Q_RETURN_ARG(QVariant,result),Q_ARG(QVariant,index)))return static_cast<QQuickItem*>(nullptr);return result.value<QQuickItem*>();};
    QJsonArray states,clicks;int tabs=0;
    auto capture=[&](const QString &name){
        if(!check(waitForShapeFrame(window)&&waitForShapeFrame(window),"Rendered frame missing"))return false;
        if(!check(original&&fixture->property("control").value<QQuickItem*>()==original,"Operator replaced the carousel"))return false;
        const auto life=heroMap(fixture,"state");
        if(!check(life["appearances"]==1&&life["wrapperInstances"]==1&&life["disappearances"]==0,"Operator replaced the wrapper"))return false;
        const auto image=prefix+"-"+name+".png";
        if(!check(!QFile::exists(image)&&window->grabWindow().save(image),"Capture exists or failed"))return false;
        states.append(QJsonObject{{"step",name},{"frame",heroMap(fixture,"frame")},{"lifecycle",life},{"metrics",heroMap(fixture,"measurements")},{"dark",window->property("fixtureDark").toBool()},{"textScale",window->property("fixtureTextScale").toDouble()}});
        return true;
    };
    auto click=[&](const QString &name){
        auto item=findVisualItem(window->contentItem(),"heroOperator-"+name);
        if(!check(item&&item->isVisible()&&item->isEnabled(),"Visible enabled operator missing"))return false;
        const auto point=item->mapToScene(QPointF(item->width()/2,item->height()/2));
        QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,point.toPoint());clicks.append(name);
        return capture(QString::number(clicks.size())+"-"+name);
    };
    if(!capture("initial")||!check(caller(0),"Initial caller missing"))return;
    const QPointer<QQuickItem> first=caller(0);
    for(const auto &kind:QStringList{"fixed","text","button","fill"}){
        if(!click("slot-"+kind)||!check(caller(0)==first&&first->property("kind").toString()==kind,"Slot edit replaced caller or did not reach it"))return;
        if(kind=="fixed"&&!check(first->width()==91,"Fixed caller width differs"))return;
        if(kind=="fill"&&!check(first->width()==337,"Fill caller width differs"))return;
    }
    if(!click("data")||!check(first->height()==20,"Data edit did not resize caller"))return;
    if(!click("reorder")||!check(caller(2)==first&&!first->property("slideActive").toBool(),"Reorder lost identity"))return;
    if(!click("empty")||!check(original->property("itemCount").toInt()==0&&first,"Empty data discarded caller state"))return;
    if(!click("empty")||!check(caller(0)==first&&first->height()==80,"Restore did not preserve original caller"))return;
    if(!click("size")||!check(first->width()==160,"Narrow proposal did not reach caller"))return;
    if(!click("size")||!check(first->width()==337,"Restored proposal did not reach caller"))return;
    if(!click("rtl")||!check(original->property("effectiveLayoutDirection").toInt()==Qt::RightToLeft,"RTL operator failed"))return;
    if(!click("rtl")||!check(original->property("effectiveLayoutDirection").toInt()==Qt::LeftToRight,"LTR restore failed"))return;
    const auto dark=window->property("fixtureDark").toBool();const auto scale=window->property("fixtureTextScale").toDouble();
    if(!click("theme")||!check(window->property("fixtureDark").toBool()!=dark,"Theme operator failed"))return;
    if(!click("scale")||!check(window->property("fixtureTextScale").toDouble()==(scale==1?1.5:1),"Scale operator failed"))return;
    if(!click("slot-button"))return;
    auto button=findVisualItem(first,"heroSlideButton");
    auto accessible=button?QAccessible::queryAccessibleInterface(button):nullptr;
    if(!check(accessible&&accessible->role()==QAccessible::Button&&!accessible->state().disabled,"Caller accessibility missing"))return;
    window->requestActivate();
    for(int index=0;index<20&&window->activeFocusItem()!=button;++index){QTest::keyClick(window,Qt::Key_Tab);++tabs;if(!check(waitForShapeFrame(window),"Tab frame missing"))return;}
    if(!check(window->activeFocusItem()==button,"Tab did not reach actual caller button"))return;
    const auto actions=heroMap(fixture,"state")["actions"].toArray().size();
    QTest::keyClick(window,Qt::Key_Space);
    if(!capture("keyboard-space")||!check(heroMap(fixture,"state")["actions"].toArray().size()==actions+1,"Space did not activate actual caller"))return;
    const auto offset=original->property("contentX").toDouble();QTest::keyClick(window,Qt::Key_Right);
    if(!capture("keyboard-right")||!check(original->property("contentX").toDouble()==offset&&window->activeFocusItem()==button,"Arrow key changed the owned view"))return;
    if(!click("disabled")||!check(!button->isEnabled()&&accessible->state().disabled,"Disabled state did not reach caller"))return;
    const auto before=heroMap(fixture,"state")["actions"].toArray().size();
    const auto point=button->mapToScene(QPointF(button->width()/2,button->height()/2));QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,point.toPoint());
    for(int index=0;index<16;++index){QTest::keyClick(window,Qt::Key_Tab);++tabs;if(!check(waitForShapeFrame(window)&&window->activeFocusItem()!=button,"Disabled caller retained Tab focus"))return;}
    if(!capture("disabled-pointer-and-tab")||!check(heroMap(fixture,"state")["actions"].toArray().size()==before,"Disabled pointer activated caller"))return;
    if(!click("disabled")||!check(button->isEnabled(),"Enabled state did not restore"))return;
    QJsonObject report{{"accepted",false},{"fixture","hero-carousel-gallery"},{"structuralChecks","passed"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"dpr",window->devicePixelRatio()},{"operatorClicks",clicks},{"tabKeyEvents",tabs},{"callerSpaceActivation",true},{"arrowKeysDoNotNavigate",true},{"disabledPointerAndTab",true},{"states",states},{"nativeInputTimingAcceptance","pending"},{"readerAcceptance","pending"},{"physicalInputAcceptance","pending"}};
    QFile output(prefix+".json");if(!check(output.open(QIODevice::WriteOnly|QIODevice::NewOnly),"Report write failed"))return;output.write(QJsonDocument(report).toJson());
    qInfo("HeroCarousel gallery: %d operator clicks, %d observed states, caller Tab/Space and disabled input pass; native acceptance pending",int(clicks.size()),int(states.size()));
    app.exit(0);
}

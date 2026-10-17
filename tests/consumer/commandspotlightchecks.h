#pragma once
#include <QPointer>

static void runCommandSpotlightConsumer(QQuickWindow *window,QGuiApplication &app,const QCommandLineParser &parser,double textScale) {
    auto check=[&](bool value,const char *message){if(!value){qCritical("CommandSpotlight: %s",message);app.exit(99);}return value;};
    QFile file(":/avelino/fixtures/native-command-spotlight-witnesses.json");
    if(!check(file.open(QIODevice::ReadOnly),"Native observations missing"))return;
    const auto native=QJsonDocument::fromJson(file.readAll()).object();
    if(!check(native["reference"]=="fe8a1d462fbd793d883fb92086a16aa2947e32c9"&&native["accepted"]==false&&native["closed"].toArray().size()==256&&native["histories"].toArray().size()==64&&native["sizing"].toArray().size()==256,"Native observations incomplete"))return;
    const auto prefix=parser.isSet("evidence") ? parser.value("evidence"):parser.value("command-spotlight-report");
    if(!prefix.isEmpty()&&!check(!QFile::exists(prefix+".json"),"Report path exists"))return;
    auto fixture=[&](){return window->property("primaryFixture").value<QQuickItem*>();};
    auto control=[&](){return fixture() ? fixture()->property("control").value<QQuickItem*>():nullptr;};
    auto selected=[&](const QJsonObject &row){return row["appearance"]==(parser.isSet("dark") ? "dark":"light")&&row["textScale"].toDouble()==textScale&&row["dpr"].toDouble()==window->devicePixelRatio();};
    auto configure=[&](const QJsonObject &row,bool fresh){
        if(fresh){window->setProperty("mounted",false);if(!check(waitForShapeFrame(window),"Unmounted frame missing"))return false;}
        if(!check(QMetaObject::invokeMethod(window,"environment",Q_ARG(QVariant,row["appearance"]=="dark"),Q_ARG(QVariant,row["textScale"].toDouble()))&&QMetaObject::invokeMethod(window,fresh ? "configure":"update",Q_ARG(QVariant,row["configuration"].toObject().toVariantMap())),"Caller configuration failed"))return false;
        if(fresh)window->setProperty("mounted",true);
        return check(waitForShapeFrame(window)&&control(),"Displayed control missing");
    };
    auto save=[&](const QString &name){if(prefix.isEmpty())return true;const auto path=prefix+"-"+name+".png";return check(!QFile::exists(path)&&window->grabWindow().save(path),"Capture exists or failed");};
    int frames=0,states=0,images=0,pointers=0,keys=0,restores=0;
    QJsonArray closed,histories,sizing;
    auto observe=[&](const QJsonObject &expected){
        const auto actual=chartMap(fixture(),"state"),frame=chartMap(fixture(),"frame"),owner=chartMap(window,"ownerState");
        auto field=control()->property("searchField").value<QQuickItem*>();
        bool stateMatch=owner["query"]==expected["query"]&&owner["requests"]==expected["requests"]&&owner["pending"]==expected["pending"]&&field&&field->property("text").toString()==expected["editorText"].toString()&&field->isEnabled()==expected["fieldEnabled"].toBool();
        for(const auto &name:{"rowCounts","rowInstances","rowAppearances","rowDisappearances","appearedKeys","lifecycle"})stateMatch&=actual[name]==expected[name];
        const bool frameMatch=frame==expected["frames"];frames+=frameMatch;states+=stateMatch;
        return QJsonObject{{"configuration",expected["configuration"]},{"reference",expected["reference"]},{"frames",frame},{"state",actual},{"query",owner["query"]},{"requests",owner["requests"]},{"pending",owner["pending"]},{"editorText",field ? field->property("text").toString():QString()},{"fieldEnabled",field&&field->isEnabled()},{"nativeFrameMatches",frameMatch},{"nativeStateMatches",stateMatch}};
    };
    for(const auto &entry:native["closed"].toArray()) {
        const auto row=entry.toObject();if(!selected(row))continue;
        if(!configure(row,true)||!check(control()->property("count").toInt()==row["configuration"].toObject()["entries"].toArray().size(),"Caller row count changed"))return;
        closed.append(observe(row));if(!save(row["configuration"].toObject()["id"].toString()))return;++images;
    }
    for(const auto &entry:native["histories"].toArray()) {
        const auto row=entry.toObject();if(!selected(row))continue;
        QJsonArray steps;QPointer<QQuickItem> original;QImage initial;int index=0;
        for(const auto &value:row["steps"].toArray()) {
            const auto step=value.toObject();const auto name=step["step"].toString();
            if(!configure(step,index==0))return;
            if(index==0){original=control();initial=window->grabWindow();}
            if(!check(original==control(),"History replaced control"))return;
            if(name=="external-query")window->setProperty("query",QString("No matching commands"));
            if(name=="restore")window->setProperty("query",row["configuration"].toObject()["query"].toString());
            if(name=="flush-owner"||name=="flush-clear")if(!check(QMetaObject::invokeMethod(window,"flushOwner"),"Owner flush failed"))return;
            if(name=="blur-query")if(!check(QMetaObject::invokeMethod(window,"blur"),"Blur failed"))return;
            QJsonArray delivered;
            for(const auto &actionValue:step["actions"].toArray()) {
                const auto action=actionValue.toObject();const auto kind=action["kind"].toString();
                if(kind=="pointer"||kind=="clearPointer") {
                    const auto point=action["point"].toArray();
                    QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,QPointF(point[0].toDouble(),point[1].toDouble()).toPoint());++pointers;
                    delivered.append(QJsonObject{{"kind",kind},{"point",point},{"method","QTest::mouseClick"}});
                } else if(action["method"]=="NSWindow.sendEvent keyDown/keyUp") {
                    auto field=control()->property("searchField").value<QQuickItem*>();const bool available=field&&field->isEnabled();
                    if(available){field->forceActiveFocus();QMetaObject::invokeMethod(field,"selectAll");QTest::keyClick(window,Qt::Key_Q);++keys;}
                    delivered.append(QJsonObject{{"kind","key"},{"available",available},{"method","QTest::keyClick"}});
                } else if(name=="scroll-bottom"||name=="scroll-top") {
                    const auto rows=control()->property("rowContainer").value<QQuickItem*>();
                    const qreal y=name=="scroll-bottom" ? rows->property("contentHeight").toDouble():0;
                    if(!check(QMetaObject::invokeMethod(control(),"scrollTo",Q_ARG(qreal,y)),"Scroll failed"))return;
                    delivered.append(QJsonObject{{"kind","scroll"},{"requestedY",y},{"nativeAction",action}});
                } else if(!check(false,"Unknown native input action"))return;
            }
            if(!check(waitForShapeFrame(window),"History result frame missing"))return;
            auto observed=observe(step);observed["step"]=name;observed["appearance"]=step["appearance"];observed["textScale"]=step["textScale"];observed["actions"]=delivered;observed["nativeActions"]=step["actions"];observed["matchesInitialPixels"]=window->grabWindow()==initial;
            if(name=="restore")restores+=observed["matchesInitialPixels"].toBool();
            if(!save(row["configuration"].toObject()["id"].toString()+"-history-step"+QString::number(index)))return;
            steps.append(observed);++index;++images;
        }
        histories.append(QJsonObject{{"configuration",row["configuration"]},{"steps",steps}});
    }
    for(const auto &entry:native["sizing"].toArray()) {
        const auto row=entry.toObject();if(!selected(row))continue;
        if(!configure(row,true))return;
        sizing.append(QJsonObject{{"configuration",row["configuration"]},{"nativeProposals",row["proposals"]},{"qtImplicitSize",QJsonObject{{"width",control()->implicitWidth()},{"height",control()->implicitHeight()}}},{"status","Native direct-proposal equivalence pending"}});
    }
    if(!check(closed.size()==32&&histories.size()==8&&sizing.size()==32&&images==224,"Incomplete context"))return;
    QJsonObject report{{"reference",native["reference"]},{"fixture","command-spotlight"},{"accepted",false},{"structuralChecks","passed"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},{"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},{"images",images},{"frameMatches",frames},{"stateMatches",states},{"pointerDeliveries",pointers},{"keyDeliveries",keys},{"retainedRestores",restores},{"nativeSizingAcceptance","pending"},{"nativeInputTimingAcceptance","pending"},{"nativeAccessibilityAcceptance","unobserved"},{"nativeRasterAcceptance","pending"},{"physicalInputAcceptance","pending"},{"readerAcceptance","pending"},{"closed",closed},{"histories",histories},{"sizing",sizing}};
    if(parser.isSet("evidence")&&!check(window->grabWindow().save(prefix+".png"),"Window capture failed"))return;
    if(!prefix.isEmpty()){QFile output(prefix+".json");if(!check(output.open(QIODevice::WriteOnly|QIODevice::NewOnly),"Report write failed"))return;output.write(QJsonDocument(report).toJson());}
    qInfo("Installed CommandSpotlight: 32 closed, eight retained histories; frames %d/224, state %d/224; acceptance pending",frames,states);
    const int code=parser.isSet("command-spotlight-observe") ? 0:1;
    if(parser.isSet("evidence")) {
        auto timer=new QTimer(&app);
        QObject::connect(timer,&QTimer::timeout,&app,[&app,prefix,code]{if(QFile::exists(prefix+".captured"))app.exit(code);});
        timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(93);});return;
    }
    app.exit(code);
}

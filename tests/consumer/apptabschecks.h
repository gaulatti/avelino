#pragma once
#include <QPointer>

static QQuickItem *appTabItem(QQuickItem *bar,int index) {
    QQuickItem *result=nullptr;
    if(!QMetaObject::invokeMethod(bar,"tabAt",Q_RETURN_ARG(QQuickItem*,result),Q_ARG(int,index)))return nullptr;
    return result;
}
static void runAppTabsConsumer(QQuickWindow *window,QGuiApplication &app,const QCommandLineParser &parser,double textScale) {
    auto check=[&](bool condition,const char *message){if(!condition){qCritical("AppTabs: %s",message);app.exit(99);}return condition;};
    QFile file(":/avelino/fixtures/native-app-tabs-witnesses.json");if(!check(file.open(QIODevice::ReadOnly),"Native observations missing"))return;
    const auto native=QJsonDocument::fromJson(file.readAll()).object();
    if(!check(native["reference"]=="fe8a1d462fbd793d883fb92086a16aa2947e32c9"&&native["accepted"]==false&&native["closed"].toArray().size()==344&&native["histories"].toArray().size()==48&&native["sizing"].toArray().size()==344,"Incomplete native observations"))return;
    const auto prefix=parser.isSet("evidence") ? parser.value("evidence"):parser.value("app-tabs-report");
    if(!prefix.isEmpty()&&!check(!QFile::exists(prefix+".json"),"Report path exists"))return;
    auto fixture=[&](){return window->property("primaryFixture").value<QQuickItem*>();};
    auto bar=[&](){return fixture() ? fixture()->property("control").value<QQuickItem*>():nullptr;};
    auto selected=[&](const QJsonObject &row){return row["appearance"]==(parser.isSet("dark") ? "dark":"light")&&row["textScale"].toDouble()==textScale&&row["dpr"].toDouble()==window->devicePixelRatio();};
    auto environment=[&](const QJsonObject &row){return check(QMetaObject::invokeMethod(window,"environment",Q_ARG(QVariant,row["appearance"]=="dark"),Q_ARG(QVariant,row["textScale"].toDouble())),"Environment update failed");};
    auto configure=[&](const QJsonObject &configuration,bool fresh){
        if(fresh){window->setProperty("mounted",false);if(!check(waitForShapeFrame(window),"Unmounted frame missing"))return false;}
        if(!check(QMetaObject::invokeMethod(window,fresh ? "configure":"update",Q_ARG(QVariant,configuration.toVariantMap())),"Caller configuration failed"))return false;
        if(fresh)window->setProperty("mounted",true);
        return check(waitForShapeFrame(window)&&bar(),"Displayed tab bar missing");
    };
    auto save=[&](const QString &name){if(prefix.isEmpty())return true;const auto path=prefix+"-"+name+".png";return check(!QFile::exists(path)&&window->grabWindow().save(path),"Capture exists or failed");};
    int frames=0,states=0,images=0,pointers=0,interfaces=0,restores=0;
    QJsonArray closed,histories,sizing;
    auto verify=[&](const QJsonObject &configuration){
        const auto tabs=configuration["tabs"].toArray();
        if(!check(bar()->property("count").toInt()==tabs.size(),"Tab count differs from caller"))return false;
        for(int index=0;index<tabs.size();++index) {
            const auto tab=tabs[index].toObject();const auto button=appTabItem(bar(),index);
            if(!check(button,"Retained Qt button missing"))return false;
            auto accessible=QAccessible::queryAccessibleInterface(button);
            const auto title=tab["accessibilityLabel"].isString() ? tab["accessibilityLabel"].toString():tab["label"].toString();
            const auto value=tab["badge"].isNull()||tab["badge"].isUndefined() ? QString():tab["badge"].toString()+" notifications";
            if(!check(accessible&&accessible->role()==QAccessible::Button&&accessible->text(QAccessible::Name)==title
                &&accessible->text(QAccessible::Value)==value&&accessible->state().selected==button->property("selected").toBool()
                &&accessible->state().disabled==(!button->isEnabled()),"Actual Qt button accessibility differs from source contract"))return false;
            const auto loader=button->property("iconItem").value<QQuickItem*>();
            const auto glyph=loader ? loader->property("item").value<QQuickItem*>():nullptr;
            if(!check(glyph&&glyph->property("dimensionsAvailable").toBool(),"Native fixture symbol dimensions unavailable"))return false;
            ++interfaces;
        }
        return check(chartMap(fixture(),"state")==QJsonObject{{"appearances",1},{"disappearances",0},{"wrapperInstances",1}},"Caller wrapper recreated");
    };
    auto observe=[&](const QJsonObject &expected){
        const auto frame=chartMap(fixture(),"frame"),life=chartMap(fixture(),"state"),owner=chartMap(window,"ownerState");
        const QJsonValue selectedValues=chartMap(fixture(),"selectionState").value("selectedValues");
        QJsonArray expectedValues;
        for(const auto &entry:expected["configuration"].toObject()["tabs"].toArray()) {
            const auto value=entry.toObject()["value"].toString();
            if(value.normalized(QString::NormalizationForm_D)==expected["selection"].toString().normalized(QString::NormalizationForm_D))expectedValues.append(value);
        }
        const bool frameMatch=frame==expected["frames"],stateMatch=life==expected["lifecycle"]&&owner["selection"]==expected["selection"]&&owner["requests"]==expected["requests"]&&owner["pending"]==expected["pending"]&&selectedValues.toArray()==expectedValues;
        frames+=frameMatch;states+=stateMatch;
        return QJsonObject{{"configuration",expected["configuration"]},{"reference",expected["reference"]},{"frames",frame},{"lifecycle",life},{"selection",owner["selection"]},{"selectedValues",selectedValues},{"requests",owner["requests"]},{"pending",owner["pending"]},{"nativeFrameMatches",frameMatch},{"nativeStateMatches",stateMatch}};
    };
    for(const auto &value:native["closed"].toArray()) {
        const auto row=value.toObject();if(!selected(row))continue;
        if(!environment(row)||!configure(row["configuration"].toObject(),true)||!verify(row["configuration"].toObject()))return;
        closed.append(observe(row));if(!save(row["configuration"].toObject()["id"].toString()))return;++images;
    }
    for(const auto &value:native["histories"].toArray()) {
        const auto row=value.toObject();if(!selected(row))continue;
        QJsonArray steps;QPointer<QQuickItem> original;QImage initial;int index=0;
        for(const auto &entry:row["steps"].toArray()) {
            const auto step=entry.toObject(),configuration=step["configuration"].toObject();const auto name=step["step"].toString();
            if(!environment(step)||!configure(configuration,index==0))return;
            if(index==0){original=bar();initial=window->grabWindow();}
            if(!check(original==bar(),"History replaced control"))return;
            if(name=="external-selection")window->setProperty("selection",configuration["tabs"].toArray().last().toObject()["value"].toString());
            if(name=="restore")window->setProperty("selection",row["configuration"].toObject()["selection"].toString());
            if(name=="flush-owner"&&!check(QMetaObject::invokeMethod(window,"flushOwner"),"Owner flush failed"))return;
            if(!check(waitForShapeFrame(window),"History frame missing"))return;
            const auto actions=step["actions"].toArray();
            if(!actions.isEmpty()&&actions[0].toObject()["kind"]=="pointer") {
                const auto action=actions[0].toObject();
                const auto button=appTabItem(bar(),action["target"].toInt());if(!check(button,"Pointer target missing"))return;
                const QPointF point(action["x"].toDouble(),action["y"].toDouble());
                QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,point.toPoint());++pointers;
                if(!check(waitForShapeFrame(window),"Pointer result frame missing"))return;
            }
            // Source AX presses were unavailable. They remain unobserved here;
            // actual Qt action dispatch is exercised separately by component tests.
            if(!verify(configuration))return;
            auto observed=observe(step);observed["step"]=name;observed["appearance"]=step["appearance"];observed["textScale"]=step["textScale"];observed["actions"]=actions;observed["matchesInitialPixels"]=window->grabWindow()==initial;
            if(name=="restore")restores+=observed["matchesInitialPixels"].toBool();
            if(!save(row["configuration"].toObject()["id"].toString()+"-history-step"+QString::number(index)))return;
            steps.append(observed);++images;++index;
        }
        histories.append(QJsonObject{{"configuration",row["configuration"]},{"steps",steps}});
    }
    for(const auto &value:native["sizing"].toArray()) {const auto row=value.toObject();if(selected(row))sizing.append(QJsonObject{{"configuration",row["configuration"]},{"public",row["public"]},{"witnesses",row["witnesses"]},{"actual",QJsonValue::Null},{"status","unobserved; native direct-proposal adapter pending"}});}
    if(!check(closed.size()==43&&histories.size()==6&&sizing.size()==43&&images==151&&pointers==24,"Incomplete context"))return;
    QJsonObject report{{"reference",native["reference"]},{"fixture","app-tabs"},{"accepted",false},{"structuralChecks","passed"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},{"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},{"images",images},{"frameMatches",frames},{"stateMatches",states},{"pointerDeliveries",pointers},{"retainedRestores",restores},{"qtButtonInterfaces",interfaces},{"nativeSizingAcceptance","pending"},{"nativeAccessibilityAcceptance","unobserved"},{"nativeRasterAcceptance","pending"},{"physicalInputAcceptance","pending"},{"readerAcceptance","pending"},{"closed",closed},{"histories",histories},{"sizing",sizing}};
    if(parser.isSet("evidence")&&!check(window->grabWindow().save(prefix+".png"),"Window capture failed"))return;
    if(!prefix.isEmpty()){QFile output(prefix+".json");if(!check(output.open(QIODevice::WriteOnly|QIODevice::NewOnly),"Report write failed"))return;output.write(QJsonDocument(report).toJson());}
    qInfo("Installed AppTabs: 43 closed and six retained cases; frames %d/151, state %d/151; strict acceptance pending",frames,states);
    const int code=parser.isSet("app-tabs-observe") ? 0:1;
    if(parser.isSet("evidence")){auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,prefix,code]{if(QFile::exists(prefix+".captured"))app.exit(code);});timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(93);});return;}
    app.exit(code);
}

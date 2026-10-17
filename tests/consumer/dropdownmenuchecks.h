#pragma once
#include <QPointer>

static QQuickItem *dropdownMenuItem(QQuickItem *control,int index) {
    QQuickItem *result=nullptr;
    if(!QMetaObject::invokeMethod(control,"itemAt",Q_RETURN_ARG(QQuickItem*,result),Q_ARG(int,index)))return nullptr;
    return result;
}
static void runDropdownMenuConsumer(QQuickWindow *window,QGuiApplication &app,const QCommandLineParser &parser,double textScale) {
    auto check=[&](bool value,const char *message){if(!value){qCritical("DropdownMenu: %s",message);app.exit(99);}return value;};
    QFile file(":/avelino/fixtures/native-dropdown-menu-witnesses.json");
    if(!check(file.open(QIODevice::ReadOnly),"Native observations missing"))return;
    const auto native=QJsonDocument::fromJson(file.readAll()).object();
    if(!check(native["reference"]=="fe8a1d462fbd793d883fb92086a16aa2947e32c9"&&native["accepted"]==false&&native["closed"].toArray().size()==256&&native["sizing"].toArray().size()==256&&native["dispatch"].toArray().size()==3,"Incomplete native observations"))return;
    const auto prefix=parser.isSet("evidence") ? parser.value("evidence"):parser.value("dropdown-menu-report");
    if(!prefix.isEmpty()&&!check(!QFile::exists(prefix+".json"),"Report path exists"))return;
    auto fixture=[&](){return window->property("primaryFixture").value<QQuickItem*>();};
    auto control=[&](){return fixture() ? fixture()->property("control").value<QQuickItem*>():nullptr;};
    auto selected=[&](const QJsonObject &row){return row["appearance"]==(parser.isSet("dark") ? "dark":"light")&&row["textScale"].toDouble()==textScale&&row["dpr"].toDouble()==window->devicePixelRatio();};
    auto configure=[&](const QJsonObject &configuration){
        window->setProperty("mounted",false);
        if(!check(waitForShapeFrame(window),"Unmounted frame missing"))return false;
        if(!check(QMetaObject::invokeMethod(window,"configure",Q_ARG(QVariant,configuration.toVariantMap())),"Caller configuration failed"))return false;
        window->setProperty("mounted",true);
        return check(waitForShapeFrame(window)&&control(),"Displayed control missing");
    };
    auto save=[&](QQuickWindow *target,const QString &name){if(prefix.isEmpty())return true;const auto path=prefix+"-"+name+".png";return check(target&&!QFile::exists(path)&&target->grabWindow().save(path),"Capture exists or failed");};
    int completeFrames=0,bodyFrames=0,states=0,pointers=0,keys=0,popupImages=0;
    QJsonArray closed,sizing,actions,accessibility;
    QJsonObject standard,many;
    for(const auto &value:native["closed"].toArray()) {
        const auto row=value.toObject();if(!selected(row))continue;
        const auto configuration=row["configuration"].toObject();
        if(!configure(configuration))return;
        const auto actual=chartMap(fixture(),"state"),frame=chartMap(fixture(),"frame");
        const int count=configuration["empty"].toBool() ? 0:configuration["itemMode"]=="many" ? 40:configuration["itemMode"]=="single" ? 1:configuration["itemMode"]=="long" ? 2:3;
        if(!check(actual["count"].toInt()==count&&actual["distinctIdentities"].toInt()==count&&actual["popupBuiltCount"].toInt()==0&&actual["labelActions"].toInt()==0,"Caller items, identity or lazy menu construction differs"))return;
        const bool frameMatch=frame==row["frames"],bodyMatch=frame["body"]==row["frames"].toObject()["body"]&&frame["caller"]==row["frames"].toObject()["caller"];
        const bool stateMatch=actual["title"]==row["title"]&&actual["enabled"]==row["enabled"]&&actual["actions"]==row["calls"];
        completeFrames+=frameMatch;bodyFrames+=bodyMatch;states+=stateMatch;
        closed.append(QJsonObject{{"configuration",configuration},{"reference",row["reference"]},{"frames",frame},{"state",actual},{"nativeFrames",row["frames"]},{"nativeViews",row["nativeViews"]},{"nativeCompleteFramesMatch",frameMatch},{"nativeBodyCallerFramesMatch",bodyMatch},{"nativeStateMatch",stateMatch}});
        if(!save(window,configuration["id"].toString()))return;
        if(configuration["id"]=="default")standard=configuration;
        if(configuration["id"]=="many-items")many=configuration;
    }
    for(const auto &value:native["sizing"].toArray()) {
        const auto row=value.toObject();if(!selected(row))continue;
        if(!configure(row["configuration"].toObject()))return;
        sizing.append(QJsonObject{{"configuration",row["configuration"]},{"nativeProposals",row["proposals"]},{"qtImplicitSize",QJsonObject{{"width",control()->implicitWidth()},{"height",control()->implicitHeight()}}},{"status","Native direct-proposal equivalence pending"}});
    }
    auto open=[&](){
        auto trigger=control()->property("presentationItem").value<QQuickItem*>();
        if(!check(trigger,"Trigger missing"))return false;
        QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,trigger->mapToScene(QPointF(trigger->width()/2,trigger->height()/2)).toPoint());++pointers;
        QCoreApplication::processEvents();
        QElapsedTimer opening;opening.start();
        while(opening.elapsed()<1000){
            auto current=dropdownMenuItem(control(),0);
            if(current&&current->window()&&current->window()!=window)break;
            QTest::qWait(10);
        }
        auto item=dropdownMenuItem(control(),0);
        if(!item||!item->window()||item->window()==window)
            qCritical()<<"DropdownMenu popup observation:"<<control()->property("menu").value<QObject*>()->property("visible")
                <<control()->property("menu").value<QObject*>()->property("popupType")<<item<<(item ? item->window():nullptr)<<window;
        return check(item&&item->window()&&item->window()!=window&&waitForShapeFrame(item->window()),"Owned menu window missing");
    };
    auto click=[&](QQuickItem *item){
        if(!check(item&&item->window(),"Menu pointer target missing"))return false;
        QTest::mouseClick(item->window(),Qt::LeftButton,Qt::NoModifier,item->mapToScene(QPointF(item->width()/2,item->height()/2)).toPoint());++pointers;
        QTest::qWait(150);
        return check(waitForShapeFrame(window),"Owner result frame missing");
    };
    const auto nativeActions=native["dispatch"].toArray()[0].toObject()["steps"].toArray().last().toObject()["calls"].toArray();
    if(!check(closed.size()==32&&sizing.size()==32&&!standard.isEmpty()&&!many.isEmpty()&&nativeActions.size()==3,"Incomplete context"))return;
    for(int index=0;index<3;++index) {
        if(!configure(standard)||!open())return;
        auto item=dropdownMenuItem(control(),index);
        if(!save(item->window(),"open-action"+QString::number(index)))return;++popupImages;
        auto accessible=QAccessible::queryAccessibleInterface(item);
        if(!accessible||accessible->role()!=QAccessible::MenuItem||accessible->text(QAccessible::Name)!=item->property("text").toString())
            qCritical()<<"DropdownMenu accessibility observation:"<<accessible<<(accessible ? int(accessible->role()):-1)<<(accessible ? accessible->text(QAccessible::Name):QString())<<item->property("text");
        if(!check(accessible&&accessible->role()==QAccessible::MenuItem&&accessible->text(QAccessible::Name)==item->property("text").toString(),"Actual Qt menu accessibility differs"))return;
        accessibility.append(QJsonObject{{"role",int(accessible->role())},{"name",accessible->text(QAccessible::Name)},{"target",index}});
        if(!click(item))return;
        const auto actual=chartMap(fixture(),"state");
        if(!check(actual["actions"]==QJsonArray{nativeActions[index]}&&actual["popupVisible"]==false,"Owner action duplicated or misrouted"))return;
        actions.append(QJsonObject{{"kind","owner-action"},{"target",index},{"state",actual},{"method","QTest::mouseClick on actual menu window"}});
    }
    if(!configure(many)||!open())return;
    auto menu=control()->property("menu").value<QObject*>();
    auto viewport=menu ? menu->property("contentItem").value<QQuickItem*>():nullptr;
    if(!check(viewport&&QMetaObject::invokeMethod(viewport,"positionViewAtEnd"),"Menu scroll unavailable"))return;
    auto last=dropdownMenuItem(control(),39);
    if(!check(last&&waitForShapeFrame(last->window()),"Scrolled menu frame missing")||!save(last->window(),"scrolled-menu"))return;++popupImages;
    if(!click(last))return;
    const auto scrolled=chartMap(fixture(),"state");
    if(!check(scrolled["actions"]==QJsonArray{"command-39"}&&scrolled["count"].toInt()==40,"Last command is unreachable or misrouted"))return;
    actions.append(QJsonObject{{"kind","scroll-last"},{"state",scrolled},{"method","ListView.positionViewAtEnd then actual window pointer"}});
    if(!configure(standard)||!open())return;
    fixture()->setProperty("removeOnAction",true);
    if(!click(dropdownMenuItem(control(),0)))return;
    const auto removed=chartMap(fixture(),"state");
    if(!check(removed["count"].toInt()==0&&removed["actions"]==QJsonArray{"open"}&&removed["popupVisible"]==false,"Removal during owner action failed to close the popup"))return;
    actions.append(QJsonObject{{"kind","remove-in-action"},{"state",removed}});
    if(!configure(standard)||!open())return;
    auto first=dropdownMenuItem(control(),0);QTest::keyClick(first->window(),Qt::Key_Escape);++keys;
    if(!check(waitForShapeFrame(window),"Escape result frame missing"))return;
    const auto canceled=chartMap(fixture(),"state");
    if(!check(canceled["popupVisible"]==false&&canceled["actions"].toArray().isEmpty(),"Escape invoked an action or retained the popup"))return;
    actions.append(QJsonObject{{"kind","escape"},{"state",canceled}});
    QJsonObject report{{"reference",native["reference"]},{"fixture","dropdown-menu"},{"accepted",false},{"structuralChecks","passed"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},{"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},{"images",32},{"popupImages",popupImages},{"completeFrameMatches",completeFrames},{"bodyCallerFrameMatches",bodyFrames},{"stateMatches",states},{"pointerDeliveries",pointers},{"keyDeliveries",keys},{"closed",closed},{"sizing",sizing},{"actions",actions},{"qtMenuAccessibility",accessibility},{"nativeSizingAcceptance","pending"},{"nativeLabelBuilderAcceptance","pending"},{"nativeItemIdentityUpdatesAcceptance","pending"},{"nativePopupPresentationAcceptance","pending"},{"nativeInputTimingAcceptance","pending"},{"nativeAccessibilityAcceptance","unobserved"},{"nativeRasterAcceptance","pending"},{"physicalInputAcceptance","pending"},{"readerAcceptance","pending"}};
    if(parser.isSet("evidence")&&!check(window->grabWindow().save(prefix+".png"),"Window capture failed"))return;
    if(!prefix.isEmpty()){QFile output(prefix+".json");if(!check(output.open(QIODevice::WriteOnly|QIODevice::NewOnly),"Report write failed"))return;output.write(QJsonDocument(report).toJson());}
    qInfo("Installed DropdownMenu: 32 closed contexts, 32 sizing observations, six actual owner/input traces; acceptance pending");
    const int code=parser.isSet("dropdown-menu-observe") ? 0:1;
    if(parser.isSet("evidence")){auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,prefix,code]{if(QFile::exists(prefix+".captured"))app.exit(code);});timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(93);});return;}
    app.exit(code);
}

#pragma once
#include <QPointer>

static QJsonObject heroMap(QObject *object,const char *method){
    QVariant result;if(!QMetaObject::invokeMethod(object,method,Q_RETURN_ARG(QVariant,result)))qFatal("HeroCarousel observation method missing");
    return QJsonObject::fromVariantMap(result.toMap());
}
#include "herocarouselgallerychecks.h"
static void runHeroCarouselConsumer(QQuickWindow *window,QGuiApplication &app,const QCommandLineParser &parser,double textScale){
    if(parser.isSet("hero-carousel-gallery")){runHeroCarouselGallery(window,app,parser);return;}
    auto check=[&](bool value,const char *message){if(!value){qCritical("HeroCarousel: %s",message);app.exit(99);}return value;};
    auto fixture=window->property("primaryFixture").value<QQuickItem*>();if(!check(fixture,"Fixture missing"))return;
    QFile input(":/avelino/fixtures/native-hero-carousel-witnesses.json");if(!check(input.open(QIODevice::ReadOnly),"Native observations missing"))return;
    const auto native=QJsonDocument::fromJson(input.readAll()).object();
    if(!check(native["reference"]=="fe8a1d462fbd793d883fb92086a16aa2947e32c9"&&native["accepted"]==false&&native["closed"].toArray().size()==160&&native["histories"].toArray().size()==2,"Incomplete native observations"))return;
    const auto prefix=parser.isSet("evidence")?parser.value("evidence"):parser.value("hero-carousel-report");
    if(!prefix.isEmpty()&&!check(!QFile::exists(prefix+".json"),"Evidence path exists"))return;
    auto selected=[&](const QJsonObject &row){return row["appearance"]==(parser.isSet("dark")?"dark":"light")&&row["textScale"].toDouble()==textScale&&row["dpr"].toDouble()==window->devicePixelRatio();};
    auto control=[&](){return fixture->property("control").value<QQuickItem*>();};
    auto configure=[&](const QJsonObject &value,bool fresh){
        if(fresh){fixture->setProperty("mounted",false);if(!check(waitForShapeFrame(window),"Unmounted frame missing"))return false;}
        if(!check(QMetaObject::invokeMethod(window,"configure",Q_ARG(QVariant,value.toVariantMap())),"Configuration failed"))return false;
        if(fresh&&!check(QMetaObject::invokeMethod(fixture,"resetCounters"),"Counter reset failed"))return false;
        fixture->setProperty("mounted",true);
        return check(waitForShapeFrame(window)&&waitForShapeFrame(window)&&control(),"Displayed carousel missing");
    };
    int frames=0,lifecycles=0,observations=0,images=0,buttons=0,pointers=0;
    QJsonArray closed,histories;
    auto verify=[&](const QJsonObject &configuration){
        const auto view=control();if(!check(view&&view->property("itemCount").toInt()==configuration["items"].toArray().size(),"Item count differs"))return false;
        const auto life=heroMap(fixture,"state");
        if(!check(life["appearances"]==1&&life["disappearances"]==0&&life["wrapperInstances"]==1,"Wrapper recreated"))return false;
        if(!check(view->property("clip").toBool()&&!view->property("keyNavigationEnabled").toBool(),"Owned viewport policy missing"))return false;
        const auto expected=configuration["items"].toArray().isEmpty()?0:configuration["items"].toArray().size()*configuration["width"].toDouble()+16*(configuration["items"].toArray().size()-1);
        if(!check(view->property("documentWidth").toDouble()==expected,"Document extent differs"))return false;
        return true;
    };
    auto observe=[&](const QJsonObject &source,bool history){
        auto frame=heroMap(fixture,"frame");if(history)frame.remove("caller");
        const auto life=heroMap(fixture,"state");const bool sameFrame=frame==source["frame"],sameLife=life==source["lifecycle"];
        ++observations;frames+=sameFrame;lifecycles+=sameLife;
        return QJsonObject{{"configuration",source["configuration"]},{"actualActiveFrame",frame},{"nativeActiveFrame",source["frame"]},{"nativeRawCachedSlideFrames",source["rawCachedSlideFrames"]},{"lifecycle",life},{"nativeLifecycle",source["lifecycle"]},{"metrics",heroMap(fixture,"measurements")},{"activeFrameMatches",sameFrame},{"lifecycleMatches",sameLife},{"completeNativeGeometryAcceptance","pending"}};
    };
    auto save=[&](const QString &name){if(prefix.isEmpty())return true;const auto path=prefix+"-"+name+".png";return check(!QFile::exists(path)&&window->grabWindow().save(path),"Capture exists or failed");};
    for(const auto &value:native["closed"].toArray()){
        const auto row=value.toObject();if(!selected(row))continue;const auto configuration=row["configuration"].toObject();
        if(!configure(configuration,true)||!verify(configuration))return;
        closed.append(observe(row,false));if(!save(configuration["id"].toString()))return;++images;
        if(configuration["slot"]=="button"&&!configuration["items"].toArray().isEmpty()){
            const auto actual=control();QVariant result;
            if(!check(QMetaObject::invokeMethod(actual,"slideAt",Q_RETURN_ARG(QVariant,result),Q_ARG(QVariant,0)),"Caller lookup failed"))return;
            auto caller=result.value<QQuickItem*>();auto button=caller?findVisualItem(caller,"heroSlideButton"):nullptr;auto accessible=button?QAccessible::queryAccessibleInterface(button):nullptr;
            if(!check(accessible&&accessible->role()==QAccessible::Button&&accessible->text(QAccessible::Name)==configuration["items"].toArray()[0].toObject()["title"].toString(),"Actual caller button interface missing"))return;
            ++buttons;
            const auto point=button->mapToScene(QPointF(button->width()/2,button->height()/2));QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,point.toPoint());++pointers;
            if(!check(waitForShapeFrame(window),"Pointer frame missing"))return;
            const auto actions=heroMap(fixture,"state")["actions"].toArray();
            if(!check(actions.size()==(configuration["disabled"].toBool()?0:1),"Disabled or enabled callback differs"))return;
        }
    }
    for(const auto &value:native["histories"].toArray()){
        const auto row=value.toObject();if(!selected(row))continue;
        QJsonArray steps;QPointer<QQuickItem> original;int index=0;
        for(const auto &entry:row["steps"].toArray()){
            const auto source=entry.toObject();auto configuration=source["configuration"].toObject();configuration["fitHeight"]=row["fitHeight"];
            if(!configure(configuration,index==0))return;if(index==0)original=control();
            if(!check(original==control(),"History replaced carousel"))return;
            const auto name=source["step"].toString();
            if(QStringList{"last","last-again","last-restored","first","first-again","first-restored"}.contains(name)){
                const auto items=configuration["items"].toArray();const auto target=items[name.startsWith("last")?items.size()-1:0].toObject()["id"].toString();
                if(!check(QMetaObject::invokeMethod(fixture,"scrollTo",Q_ARG(QVariant,target)),"History scroll failed"))return;
                if(!check(waitForShapeFrame(window)&&waitForShapeFrame(window),"Scroll frame missing"))return;
            }
            if(name=="empty-idle-1"||name=="empty-idle-3"){QTest::qWait(name.endsWith('1')?1000:3000);if(!check(waitForShapeFrame(window),"Idle frame missing"))return;}
            if(!verify(configuration))return;auto observed=observe(source,true);observed["step"]=name;observed["configuration"]=configuration;steps.append(observed);
            if(!save(QString(row["fitHeight"].toBool()?"fit-":"bounded-")+name))return;++images;++index;
        }
        histories.append(QJsonObject{{"fitHeight",row["fitHeight"]},{"steps",steps}});
    }
    if(!check(closed.size()==20,"Incomplete closed context"))return;
    const bool supportedHistory=!parser.isSet("dark")&&textScale==1&&window->devicePixelRatio()==1;
    if(!check(histories.size()==(supportedHistory?2:0),"Incomplete supported history context"))return;
    QJsonObject report{{"reference",native["reference"]},{"fixture","hero-carousel"},{"accepted",false},{"structuralChecks","passed"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},{"appearance",parser.isSet("dark")?"dark":"light"},{"textScale",textScale},{"images",images},{"activeFrameObservations",observations},{"activeFrameMatches",frames},{"lifecycleMatches",lifecycles},{"nativeActiveFrameComparison",frames==observations?"passed":"failed"},{"nativeLifecycleComparison",lifecycles==observations?"passed":"failed"},{"nativeCompleteGeometryAcceptance","pending"},{"nativeGestureAndTimingAcceptance","pending"},{"nativeSizingAcceptance","pending; source responses retained without a complete Linux proposal replay"},{"nativeRasterAcceptance","pending"},{"physicalInputAcceptance","pending"},{"readerAcceptance","pending"},{"qtButtonInterfaces",buttons},{"pointerDeliveries",pointers},{"closed",closed},{"histories",histories}};
    if(!prefix.isEmpty()){QFile output(prefix+".json");if(!check(output.open(QIODevice::WriteOnly|QIODevice::NewOnly),"Report write failed"))return;output.write(QJsonDocument(report).toJson());}
    qInfo("Installed HeroCarousel: 20 closed contexts, %d history groups; active frames %d/%d, lifecycle %d/%d; native acceptance pending",int(histories.size()),frames,observations,lifecycles,observations);
    const auto code=parser.isSet("hero-carousel-observe")?0:1;
    if(parser.isSet("evidence")){
        auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,prefix,code]{if(QFile::exists(prefix+".captured"))app.exit(code);});timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(93);});return;
    }
    app.exit(code);
}

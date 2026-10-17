#pragma once
#include <QPointer>

static QQuickItem *mediaItem(QQuickItem *grid,int index) {
    QQuickItem *item=nullptr;
    if(!QMetaObject::invokeMethod(grid,"itemAt",Q_RETURN_ARG(QQuickItem*,item),Q_ARG(int,index)))return nullptr;
    return item;
}
static void runMediaLibraryConsumer(QQuickWindow *window,QGuiApplication &app,const QCommandLineParser &parser,double textScale) {
    auto check=[&](bool value,const char *message){if(!value){qCritical("MediaLibrary: %s",message);app.exit(99);}return value;};
    auto fixture=window->property("primaryFixture").value<QQuickItem*>();if(!check(fixture,"Fixture missing"))return;
    QFile file(":/avelino/fixtures/native-media-library-witnesses.json");if(!check(file.open(QIODevice::ReadOnly),"Native projection missing"))return;
    const auto native=QJsonDocument::fromJson(file.readAll()).object();
    if(!check(native["reference"]=="fe8a1d462fbd793d883fb92086a16aa2947e32c9"&&native["accepted"]==false&&native["closed"].toArray().size()==496&&native["histories"].toArray().size()==48&&native["edges"].toArray().size()==112&&native["sizing"].toArray().size()==496,"Incomplete projection"))return;
    const auto prefix=parser.isSet("evidence") ? parser.value("evidence"):parser.value("media-library-report");
    if(!prefix.isEmpty()&&!check(!QFile::exists(prefix+".json"),"Evidence path exists"))return;
    auto selected=[&](const QJsonObject &row){return row["appearance"]==(parser.isSet("dark") ? "dark":"light")&&row["textScale"].toDouble()==textScale&&row["dpr"].toDouble()==window->devicePixelRatio();};
    auto control=[&](){return fixture->property("control").value<QQuickItem*>();};
    auto environment=[&](bool dark,double scale){return check(QMetaObject::invokeMethod(window,"environment",Q_ARG(QVariant,dark),Q_ARG(QVariant,scale)),"Environment update failed");};
    auto configure=[&](const QJsonObject &value,bool fresh){
        if(fresh){fixture->setProperty("mounted",false);if(!check(waitForShapeFrame(window),"Unmounted frame missing"))return false;}
        if(!check(QMetaObject::invokeMethod(window,"configure",Q_ARG(QVariant,value.toVariantMap())),"Configuration failed"))return false;
        if(fresh&&!check(QMetaObject::invokeMethod(fixture,"resetCounters"),"Counter reset failed"))return false;
        fixture->setProperty("mounted",true);
        return check(waitForShapeFrame(window)&&control(),"Displayed grid missing");
    };
    if(parser.isSet("media-library-fatal")) {
        for(const auto &value:native["edges"].toArray()) {
            const auto row=value.toObject();if(selected(row)&&row["nativeExitCode"].toInt()!=0){configure(row["configuration"].toObject(),true);qCritical("Native fatal input unexpectedly survived");app.exit(98);return;}
        }
        app.exit(98);return;
    }
    int frames=0,lifecycles=0,images=0,observations=0,accessibility=0,pointers=0;
    QJsonArray closed,edges,histories,sizing;
    auto verify=[&](const QJsonObject &configuration){
        const auto grid=control();if(!check(grid&&grid->property("itemCount").toInt()==configuration["items"].toArray().size(),"Item count differs from producer"))return false;
        const auto state=chartMap(fixture,"state");
        if(!check(state["appearances"]==1&&state["disappearances"]==0&&state["wrapperInstances"]==1,"Wrapper recreated"))return false;
        if(configuration["slot"]=="button")for(int index=0;index<grid->property("itemCount").toInt();++index) {
            const auto item=mediaItem(grid,index);if(!item ||!item->property("tileActive").toBool())continue;
            const auto button=findVisualItem(item,"mediaTileButton");auto actual=button ? QAccessible::queryAccessibleInterface(button):nullptr;
            if(!check(actual&&actual->role()==QAccessible::Button&&actual->text(QAccessible::Name)==configuration["items"].toArray()[index].toObject()["title"].toString(),"Actual Qt button interface missing"))return false;
            ++accessibility;
        }
        return true;
    };
    auto save=[&](const QString &name){if(prefix.isEmpty())return true;const auto path=prefix+"-"+name+".png";return check(!QFile::exists(path)&&window->grabWindow().save(path),"Capture exists or failed");};
    auto observe=[&](const QJsonObject &source){
        const auto frame=chartMap(fixture,"frame"),state=chartMap(fixture,"state");const bool sameFrame=frame==source["frame"],sameState=state==source["lifecycle"];
        ++observations;frames+=sameFrame;lifecycles+=sameState;
        return QJsonObject{{"configuration",source["configuration"]},{"reference",source["reference"]},{"frame",frame},{"lifecycle",state},{"metrics",chartMap(fixture,"measurements")},{"nativeFrameMatches",sameFrame},{"nativeLifecycleMatches",sameState}};
    };
    for(const auto &value:native["closed"].toArray()) {
        const auto row=value.toObject();if(!selected(row))continue;
        if(!environment(parser.isSet("dark"),textScale)||!configure(row["configuration"].toObject(),true)||!verify(row["configuration"].toObject()))return;
        closed.append(observe(row));if(!save(row["configuration"].toObject()["id"].toString()))return;++images;
    }
    for(const auto &value:native["edges"].toArray()) {
        const auto row=value.toObject();if(!selected(row))continue;
        if(row["nativeExitCode"].toInt()!=0){edges.append(QJsonObject{{"configuration",row["configuration"]},{"nativeExitCode",row["nativeExitCode"]},{"nativeLog",row["nativeLog"]},{"captureStatus","separate isolated process required"}});continue;}
        if(!environment(parser.isSet("dark"),textScale)||!configure(row["configuration"].toObject(),true)||!verify(row["configuration"].toObject()))return;
        auto observed=observe(row);observed["nativeExitCode"]=row["nativeExitCode"];edges.append(observed);
        if(!save("edge-"+row["configuration"].toObject()["id"].toString()))return;++images;
    }
    for(const auto &value:native["histories"].toArray()) {
        const auto row=value.toObject();if(!selected(row))continue;
        QJsonArray steps;QPointer<QQuickItem> original;QImage initial;QMap<QString,QPointer<QQuickItem>> retained;int index=0;
        for(const auto &entry:row["steps"].toArray()) {
            const auto step=entry.toObject();const auto configuration=step["configuration"].toObject();
            if(!environment(step["appearance"]=="dark",step["textScale"].toDouble())||!configure(configuration,index==0))return;
            if(index==0){original=control();initial=window->grabWindow();}
            if(!check(original==control(),"History replaced grid"))return;
            const auto name=step["step"].toString();
            if(name=="scroll-bottom"||name=="scroll-top") {
                const auto items=configuration["items"].toArray();
                if(!items.isEmpty()&&!check(QMetaObject::invokeMethod(fixture,"scrollTo",Q_ARG(QVariant,items[name=="scroll-top" ? 0:items.size()-1].toObject()["id"].toString())),"Scroll request failed"))return;
                if(!check(waitForShapeFrame(window),"Scroll frame missing"))return;
            }
            if(configuration["scroll"].toBool()&&(name=="wait-0.2"||name=="wait-1.0")){QTest::qWait(name=="wait-0.2" ? 200:1000);if(!check(waitForShapeFrame(window),"Wait frame missing"))return;}
            const auto pointer=step["pointer"].toObject();
            if(!pointer.isEmpty()){QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,QPointF(pointer["x"].toDouble(),pointer["y"].toDouble()).toPoint());++pointers;if(!check(waitForShapeFrame(window),"Pointer frame missing"))return;}
            if(!verify(configuration))return;
            if(index<=2 ||name=="zero-width"||name=="width-restored") {
                for(int i=0;i<control()->property("itemCount").toInt();++i) {
                    auto item=mediaItem(control(),i);if(!item)continue;
                    const auto key=item->property("lifecycleKey").toString();if(item->property("ordinal").toInt()==0)continue;
                    if(index==0)retained.insert(key,item);
                    else if(index<=2&&retained.contains(key)&&!check(retained[key]==item,"Data/reorder replaced caller tile"))return;
                }
            }
            auto observed=observe(step);observed["step"]=name;observed["appearance"]=step["appearance"];observed["textScale"]=step["textScale"];observed["pointer"]=pointer;observed["matchesInitialPixels"]=window->grabWindow()==initial;
            if(name=="restore"&&!observed["matchesInitialPixels"].toBool())qWarning("MediaLibrary retained restore pixels differ for %s; strict raster comparison remains failed",qPrintable(row["configuration"].toObject()["id"].toString()));
            if(!save(row["configuration"].toObject()["id"].toString()+"-history-step"+QString::number(index)))return;
            ++images;steps.append(observed);++index;
        }
        histories.append(QJsonObject{{"configuration",row["configuration"]},{"steps",steps}});
    }
    for(const auto &value:native["sizing"].toArray()) {const auto row=value.toObject();if(selected(row))sizing.append(QJsonObject{{"configuration",row["configuration"]},{"public",row["public"]},{"witnesses",row["witnesses"]},{"actual",QJsonValue::Null},{"status","unobserved; direct proposal adapter pending"}});}
    if(!check(closed.size()==62&&edges.size()==14&&histories.size()==6&&sizing.size()==62&&images==201&&observations==201&&pointers==12,"Incomplete context"))return;
    int restored=0;for(const auto &history:histories)restored+=history.toObject()["steps"].toArray()[13].toObject()["matchesInitialPixels"].toBool();
    const bool nativeGeometry=frames==observations&&lifecycles==observations;
    QJsonObject report{{"reference",native["reference"]},{"fixture","media-library"},{"accepted",false},{"structuralChecks","passed"},{"nativeGeometryComparisonStatus",nativeGeometry ? "passed":"failed"},{"nativeRasterAcceptance","pending"},{"nativeSizingAcceptance","pending; all 15 source responses retained with no Linux direct-proposal observations"},{"nativeLazyTimingAcceptance","pending"},{"physicalInputAcceptance","pending"},{"readerAcceptance","pending"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},{"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},{"images",images},{"geometryObservations",observations},{"frameMatches",frames},{"lifecycleMatches",lifecycles},{"pointerDeliveries",pointers},{"retainedRestorePixelMatches",restored},{"retainedRestoreRasterStatus",restored==6 ? "passed":"failed"},{"qtButtonInterfaces",accessibility},{"closed",closed},{"edges",edges},{"histories",histories},{"sizing",sizing}};
    if(parser.isSet("evidence")&&!check(window->grabWindow().save(prefix+".png"),"Window capture failed"))return;
    if(!prefix.isEmpty()){QFile output(prefix+".json");if(!check(output.open(QIODevice::WriteOnly|QIODevice::NewOnly),"Report write failed"))return;output.write(QJsonDocument(report).toJson());}
    qInfo("Installed MediaLibrary: 62 closed, 14 edge and six retained cases; frames %d/201, lifecycle %d/201; direct sizing and native acceptance pending",frames,lifecycles);
    const int code=parser.isSet("media-library-observe") ? 0:1;
    if(parser.isSet("evidence")){auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,prefix,code]{if(QFile::exists(prefix+".captured"))app.exit(code);});timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(93);});return;}
    app.exit(code);
}

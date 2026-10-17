#pragma once
#include <QAccessible>
#include <QElapsedTimer>
#include <QFont>

static QJsonArray pillPaintGraph(QQuickItem *root) {
    QJsonArray records;
    std::function<void(QObject*,const QString&)> object=[&](QObject *node,const QString &path){
        const QString type=node->metaObject()->className();
        if(type.contains("PathSvg"))records.append(QJsonObject{{"path",path},{"type",type},{"svg",node->property("path").toString()}});
        int index=0;for(auto child:node->children())if(!qobject_cast<QQuickItem*>(child))object(child,path+"/object"+QString::number(index++));
    };
    std::function<void(QQuickItem*,const QString&)> visit=[&](QQuickItem *item,const QString &path){
        QJsonObject row{{"path",path},{"type",item->metaObject()->className()},{"x",item->x()},{"y",item->y()},{"width",item->width()},{"height",item->height()},{"visible",item->isVisible()}};
        for(const auto *name:{"rendererType","status","hideSource","live","textureMirroring","text","color"})if(item->property(name).isValid())row[name]=QJsonValue::fromVariant(item->property(name));
        if(item->property("sourceRect").isValid()){const auto r=item->property("sourceRect").toRectF();row["sourceRect"]=QJsonArray{r.x(),r.y(),r.width(),r.height()};}
        if(item->property("textureSize").isValid()){const auto s=item->property("textureSize").toSize();row["textureSize"]=QJsonArray{s.width(),s.height()};}
        records.append(row);object(item,path);int index=0;for(auto child:item->childItems())visit(child,path+"/item"+QString::number(index++));
    };
    visit(root,"fixture");return records;
}

static void runPillConsumer(QQuickWindow *window,QGuiApplication &app,const QCommandLineParser &parser,double textScale) {
    auto check=[&](bool value,const char *message){if(!value){qCritical("Pill: %s",message);app.exit(98);}return value;};
    const auto fixture=window->property("primaryFixture").value<QQuickItem*>();
    if(!check(fixture,"Fixture missing"))return;
    QFile input(":/avelino/fixtures/native-pill-witnesses.json");if(!check(input.open(QIODevice::ReadOnly),"Native witnesses missing"))return;
    const auto native=QJsonDocument::fromJson(input.readAll()).object();
    if(!check(native["reference"]=="fe8a1d462fbd793d883fb92086a16aa2947e32c9" &&native["accepted"]==false
        &&native["closed"].toArray().size()==888 &&native["histories"].toArray().size()==56,"Native projection incomplete"))return;
    const auto prefix=parser.isSet("evidence") ? parser.value("evidence"):parser.value("pill-report");
    if(!prefix.isEmpty() &&!check(!QFile::exists(prefix+".json"),"Evidence path exists"))return;
    auto label=[&](){return fixture->property("label").value<QQuickItem*>();};
    auto settle=[&](){QElapsedTimer timer;timer.start();do {
        if(!check(waitForShapeFrame(window),"Displayed frame failed to settle"))return false;
        if(auto item=label()){bool ready=false;if(!check(QMetaObject::invokeMethod(item,"resourcesReady",Q_RETURN_ARG(bool,ready)),"Resource readiness unavailable"))return false;if(ready)return true;}
        else if(!fixture->property("mounted").toBool())return true;
    }while(timer.elapsed()<5000);return check(false,"Inline image resources did not finish");};
    auto environment=[&](bool dark,double scale){return check(QMetaObject::invokeMethod(window,"environment",Q_ARG(QVariant,dark),Q_ARG(QVariant,scale)),"Environment update failed");};
    auto configure=[&](const QJsonObject &value,bool reset,bool styled){
        if(reset){fixture->setProperty("mounted",false);if(!settle())return false;for(const auto *name:{"appearances","disappearances","callerInstances"})fixture->setProperty(name,0);}
        fixture->setProperty("styled",styled);
        if(!check(QMetaObject::invokeMethod(window,"configure",Q_ARG(QVariant,value.toVariantMap())),"Configuration failed"))return false;
        fixture->setProperty("mounted",true);return settle();
    };
    auto state=[&](){QJsonObject value;for(const auto *key:{"appearances","disappearances","callerInstances"})value[key]=fixture->property(key).toInt();return value;};
    auto verifyCaller=[&](){auto caller=label();if(!check(caller,"Text caller missing"))return false;
        auto accessible=QAccessible::queryAccessibleInterface(caller);
        return check(accessible &&accessible->role()==QAccessible::StaticText &&accessible->text(QAccessible::Name)==caller->property("accessibleText").toString(),"Actual Qt static text accessibility failed")
            &&check(state()==QJsonObject{{"appearances",1},{"disappearances",0},{"callerInstances",1}},"Caller lifecycle changed");};
    auto save=[&](const QString &name){if(prefix.isEmpty())return true;const auto path=prefix+"-"+name+".png";return check(!QFile::exists(path)&&window->grabWindow().save(path),"Capture exists or failed");};
    auto observation=[&](const QJsonObject &expected){const auto frames=surfaceModifierMap(fixture,"frames"),guides=surfaceModifierMap(fixture,"baselines");
        return QJsonObject{{"parts",frames},{"guides",guides},{"nativeFramesMatch",frames==expected["parts"]},{"nativeGuidesMatch",guides==expected["guides"]},{"state",state()},
            {"accessibleText",label()->property("accessibleText").toString()},{"color",label()->property("color").value<QColor>().name(QColor::HexArgb)}};};
    auto context=[&](const QJsonObject &row){return row["appearance"]==(parser.isSet("dark") ? "dark":"light") &&row["textScale"].toDouble()==textScale &&row["dpr"].toDouble()==window->devicePixelRatio();};
    QJsonArray rows,histories;int frames=0,guides=0,total=0;
    for(const auto &value:native["closed"].toArray()) {
        const auto row=value.toObject();if(!context(row))continue;const auto configuration=row["configuration"].toObject();QJsonArray modes;
        for(int mode:{0,3}) {
            if(!environment(parser.isSet("dark"),textScale)||!configure(configuration,true,mode==0)||!verifyCaller())return;
            const auto expected=mode==0 ? row:row["bare"].toObject();auto measured=observation(expected);measured["mode"]=mode;
            frames+=measured["nativeFramesMatch"].toBool();guides+=measured["nativeGuidesMatch"].toBool();++total;
            const auto parts=measured["parts"].toObject();
            if(mode==0){const auto outer=parts["styled"].toArray().first().toObject(),inner=parts["label"].toArray().first().toObject();
                if(!check(outer["width"].toDouble()==inner["width"].toDouble()+14 &&outer["height"].toDouble()==inner["height"].toDouble()+8,"Fixed padding changed"))return;}
            if(!save(configuration["id"].toString()+"-mode"+QString::number(mode)))return;
            modes.append(measured);
        }
        rows.append(QJsonObject{{"configuration",configuration},{"modes",modes}});
    }
    if(!check(rows.size()==111 &&total==222,"Incomplete closed contexts"))return;
    for(const auto &value:native["histories"].toArray()) {
        const auto row=value.toObject();if(!context(row))continue;QJsonArray steps,initialPaintGraph;QQuickItem *caller=nullptr,*control=nullptr;QImage initial;QJsonObject initialParts,initialGuides;
        int index=0;
        for(const auto &entry:row["steps"].toArray()) {
            const auto step=entry.toObject();if(!environment(step["appearance"]=="dark",step["textScale"].toDouble()) ||!configure(step["configuration"].toObject(),index==0,true)||!verifyCaller())return;
            const auto current=label();if(index==0){caller=current;control=fixture->property("control").value<QQuickItem*>();initial=window->grabWindow();initialParts=surfaceModifierMap(fixture,"frames");initialGuides=surfaceModifierMap(fixture,"baselines");initialPaintGraph=pillPaintGraph(fixture);}
            if(!check(current==caller &&fixture->property("control").value<QQuickItem*>()==control,"History replaced the caller or modifier"))return;
            auto measured=observation(step);measured["step"]=step["step"];measured["configuration"]=step["configuration"];measured["appearance"]=step["appearance"];measured["textScale"]=step["textScale"];
            frames+=measured["nativeFramesMatch"].toBool();guides+=measured["nativeGuidesMatch"].toBool();++total;
            if(index==1 &&!check(window->grabWindow()!=initial,"Text step did not change pixels"))return;
            if(index==5){const auto currentPixels=window->grabWindow();const bool samePixels=currentPixels==initial,sameParts=surfaceModifierMap(fixture,"frames")==initialParts,sameGuides=surfaceModifierMap(fixture,"baselines")==initialGuides;
                const bool restored=samePixels &&sameParts &&sameGuides;measured["restoredInitialPixelsAndGeometry"]=restored;
                if(!restored){
                    qCritical("Pill history %s restore: pixels=%d parts=%d guides=%d",qPrintable(row["configuration"].toObject()["id"].toString()),samePixels,sameParts,sameGuides);
                    if(!prefix.isEmpty()){
                        const auto path=prefix+"-failure";
                        if(!check(initial.save(path+"-initial.png") &&currentPixels.save(path+"-final.png"),"Failure images were not saved"))return;
                        QFile failure(path+".json");if(!check(failure.open(QIODevice::WriteOnly|QIODevice::NewOnly),"Failure report exists or could not be written"))return;
                        failure.write(QJsonDocument(QJsonObject{{"accepted",false},{"configuration",row["configuration"]},{"final",measured},{"initialParts",initialParts},{"initialGuides",initialGuides},
                            {"initialPaintGraph",initialPaintGraph},{"finalPaintGraph",pillPaintGraph(fixture)},{"pixelsRestored",samePixels},{"partsRestored",sameParts},{"guidesRestored",sameGuides}}).toJson());
                    }
                    if(!check(false,"History did not restore complete pixels and geometry"))return;
                }
            }
            if(!save(row["configuration"].toObject()["id"].toString()+"-history-step"+QString::number(index)))return;
            steps.append(measured);++index;
        }
        if(!check(steps.size()==6,"History skipped a step"))return;
        histories.append(QJsonObject{{"configuration",row["configuration"]},{"steps",steps}});
    }
    if(!check(histories.size()==7 &&total==264,"Incomplete histories"))return;
    if(!environment(parser.isSet("dark"),textScale))return;
    const bool matches=frames==total &&guides==total;
    QJsonObject report{{"reference",native["reference"]},{"accepted",false},{"fixture","pill-modifier"},{"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},
        {"dpr",window->devicePixelRatio()},{"width",window->width()},{"height",window->height()},{"platform",QGuiApplication::platformName()},{"qt",qVersion()},
        {"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"rows",rows},{"histories",histories},{"measurements",total},{"exactFrameSets",frames},{"exactGuideSets",guides},
        {"structuralChecks","passed"},{"nativeComparisonStatus",matches ? "passed":"failed"},{"nativeRasterAcceptance","pending"},{"physicalInputAcceptance","pending"},{"readerAcceptance","pending"}};
    if(!prefix.isEmpty()){QFile output(prefix+".json");if(!check(output.open(QIODevice::WriteOnly),"Report write failed"))return;output.write(QJsonDocument(report).toJson());output.close();}
    qInfo("Installed pill: 111 public/bare contexts, seven retained histories, %d/%d frame and %d/%d guide sets; native acceptance pending",frames,total,guides,total);
    const int code=!parser.isSet("pill-observe") &&!matches ? 1:0;
    if(parser.isSet("evidence")) {
        if(!check(window->grabWindow().save(prefix+".png"),"Window evidence failed"))return;
        auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,prefix,code]{if(QFile::exists(prefix+".captured"))app.exit(code);});timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(93);});return;
    }
    app.exit(code);
}

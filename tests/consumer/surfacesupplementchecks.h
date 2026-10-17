#pragma once
#include <QMouseEvent>
#include <QDir>

static void runSurfaceSupplementConsumer(QQuickWindow *window,QGuiApplication &app,
        const QCommandLineParser &parser,double textScale) {
    auto check=[&](bool ok,const char *message){if(!ok){qCritical("Surface supplement: %s",message);app.exit(98);}return ok;};
    const bool input=parser.isSet("surface-input");
    const auto fixture=window->property("primaryFixture").value<QQuickItem*>();
    if(!check(fixture,"Caller fixture unavailable"))return;
    QFile file(":/avelino/fixtures/native-surface-supplement-witnesses.json");
    if(!check(file.open(QIODevice::ReadOnly),"Native supplement projection unavailable"))return;
    const auto source=QJsonDocument::fromJson(file.readAll()).object();
    if(!check(source["reference"]=="fe8a1d462fbd793d883fb92086a16aa2947e32c9" &&source["accepted"]==false
        &&source["nativeBaselineContexts"].toArray().size()==440 &&source["nativeInputProfiles"].toArray().size()==288,"Native supplement incomplete"))return;
    const auto prefix=parser.isSet("evidence") ? parser.value("evidence"):parser.value("surface-supplement-report");
    if(!prefix.isEmpty() &&!check(!QFile::exists(prefix+".json"),"Report path already exists"))return;
    auto settle=[&](){return check(waitForShapeFrame(window),"Displayed shape/window frame did not settle");};
    auto configure=[&](const QJsonObject &configuration,int mode){
        fixture->setProperty("mounted",false);if(!settle())return false;
        for(const auto *name:{"appearances","disappearances","callerInstances","actions","counter"})fixture->setProperty(name,0);
        window->setProperty("inputMode",mode);
        if(!check(QMetaObject::invokeMethod(window,"configure",Q_ARG(QVariant,configuration.toVariantMap())),"Configuration did not reach fixture"))return false;
        fixture->setProperty("mounted",true);return settle();
    };
    auto save=[&](const QString &name){
        if(prefix.isEmpty())return true;
        const auto path=prefix+"-"+name+".png";
        return check(!QFile::exists(path)&&window->grabWindow().save(path),"Capture exists or could not be written");
    };
    QJsonArray observations;int framesMatched=0,guidesMatched=0,modesMatched=0,totalPoints=0,activationMismatches=0,sequenceMismatches=0;
    auto matchesContext=[&](const QJsonObject &row){return row["appearance"]==(parser.isSet("dark") ? "dark":"light")
        &&row["textScale"].toDouble()==textScale &&row["dpr"].toDouble()==window->devicePixelRatio();};
    if(!input) {
        for(const auto &value:source["nativeBaselineContexts"].toArray()) {
            const auto row=value.toObject();if(!matchesContext(row))continue;
            const auto configuration=row["configuration"].toObject();if(!configure(configuration,0))return;
            const auto parts=surfaceModifierMap(fixture,"frames"),guides=surfaceModifierMap(fixture,"baselines");
            if(!check(surfaceModifierState(fixture)==row["state"],"Native baseline caller state changed"))return;
            const bool frames=parts==row["parts"],sameGuides=guides==row["guides"];
            framesMatched+=frames;guidesMatched+=sameGuides;
            const auto marker=parts["reference"].toArray().first().toObject();
            if(!check(marker["width"].toDouble()==3 &&marker["height"].toDouble()==30,"Baseline marker dimensions changed"))return;
            const auto key=configuration["parentLayout"]=="zstack" ? "root":"parent";
            const auto roots=parts[key].toArray(),baselines=guides[key].toArray();
            if(!check(roots.size()==baselines.size(),"Guide/frame association incomplete"))return;
            for(int i=0;i<roots.size();++i)if(!check(roots[i].toObject()["y"].toDouble()+baselines[i].toDouble()==marker["y"].toDouble()+30,
                "Caller/parent guide did not reach the baseline parent"))return;
            if(!configuration["guide"].isNull()) {
                if(!check(guides["caller"].toArray()==QJsonArray{configuration["guide"]},"Explicit caller guide was clamped or lost"))return;
            }
            if(!save(configuration["fixture"].toString()))return;
            observations.append(QJsonObject{{"configuration",configuration},{"parts",parts},{"guides",guides},
                {"state",surfaceModifierState(fixture)},{"nativeFramesMatch",frames},{"nativeGuidesMatch",sameGuides}});
        }
        if(!check(observations.size()==55,"Incomplete baseline profile"))return;
    } else {
        quint64 timestamp=0;
        auto mouse=[&](QEvent::Type type,const QPointF &position){
            const auto scene=fixture->mapToScene(position);
            QMouseEvent event(type,scene,window->mapToGlobal(scene),Qt::LeftButton,
                type==QEvent::MouseButtonPress ? Qt::LeftButton:Qt::NoButton,Qt::NoModifier);
            event.setTimestamp(++timestamp);QCoreApplication::sendEvent(window,&event);
        };
        for(const auto &value:source["nativeInputProfiles"].toArray()) {
            const auto row=value.toObject();if(!matchesContext(row))continue;
            const auto configuration=row["configuration"].toObject();const auto points=row["points"].toArray();QJsonArray modes;
            for(const auto &entry:row["modes"].toArray()) {
                const auto native=entry.toObject();const int mode=native["mode"].toInt();if(!configure(configuration,mode))return;
                const auto control=fixture->property("control").value<QQuickItem*>(),caller=fixture->property("caller").value<QQuickItem*>(),button=fixture->property("button").value<QQuickItem*>();
                if(!check(control &&caller &&button,"Input caller/button missing"))return;
                const auto before=surfaceModifierState(fixture),parts=surfaceModifierMap(fixture,"frames");
                if(!check(before==QJsonObject{{"appearances",1},{"disappearances",0},{"callerInstances",1},{"actions",0},{"counter",0}},"Input initial caller state changed"))return;
                const bool frames=parts==row["parts"];framesMatched+=frames;
                if(!save(configuration["fixture"].toString()+"-mode"+QString::number(mode)))return;
                const auto expectedSequences=native["sequences"].toArray(),expectedActivations=native["activations"].toArray();
                QJsonArray sequences,activations,differentPoints,differentSequences;
                for(int i=0;i<points.size();++i) {
                    const auto point=points[i].toObject();const QPointF position(point["x"].toDouble(),point["y"].toDouble());
                    const int start=fixture->property("actions").toInt();
                    mouse(QEvent::MouseButtonPress,position);const int down=fixture->property("actions").toInt();
                    mouse(QEvent::MouseButtonRelease,position);const int up=fixture->property("actions").toInt();
                    QCoreApplication::processEvents();const int end=fixture->property("actions").toInt();
                    const QJsonArray sequence{start,down,up,end};sequences.append(sequence);activations.append(end-start);
                    if(end-start!=expectedActivations[i].toInt()){differentPoints.append(i);++activationMismatches;}
                    if(sequence!=expectedSequences[i].toArray()){differentSequences.append(i);++sequenceMismatches;}
                    ++totalPoints;
                }
                if(!check(activations.first().toInt()==(configuration["disabled"].toBool() ? 0:1),"Enabled center or disabled input failed"))return;
                if(configuration["disabled"].toBool())for(const auto &activation:activations)if(!check(activation.toInt()==0,"Disabled caller activated"))return;
                if(!check(fixture->property("control").value<QQuickItem*>()==control &&fixture->property("caller").value<QQuickItem*>()==caller
                    &&fixture->property("button").value<QQuickItem*>()==button &&surfaceModifierMap(fixture,"frames")==parts,"Pointer samples replaced or moved the caller"))return;
                const bool exact=differentPoints.isEmpty()&&differentSequences.isEmpty()&&frames;modesMatched+=exact;
                modes.append(QJsonObject{{"mode",mode},{"parts",parts},{"initialState",before},{"finalState",surfaceModifierState(fixture)},
                    {"sequences",sequences},{"activations",activations},{"differentActivationPoints",differentPoints},
                    {"differentSequencePoints",differentSequences},{"nativeFramesMatch",frames},{"nativeInputMatch",exact},{"callerRetained",true}});
            }
            observations.append(QJsonObject{{"configuration",configuration},{"modes",modes}});
        }
        if(!check(observations.size()==36 &&totalPoints>0,"Incomplete input profile"))return;
    }
    const bool nativeMatches=input ? framesMatched==72 &&activationMismatches==0 &&sequenceMismatches==0:framesMatched==55 &&guidesMatched==55;
    QJsonObject report{{"reference",source["reference"]},{"accepted",false},{"fixture",input ? "surface-input":"surface-baseline"},
        {"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"dpr",window->devicePixelRatio()},
        {"width",window->width()},{"height",window->height()},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},
        {"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},{"rows",observations},
        {"exactFrameSets",framesMatched},{"exactGuideSets",guidesMatched},{"exactInputModes",modesMatched},
        {"inputPoints",totalPoints},{"activationMismatches",activationMismatches},{"sequenceMismatches",sequenceMismatches},
        {"inputMethod","QMouseEvent with fractional logical positions delivered directly to QQuickWindow"},
        {"structuralChecks","passed"},{"nativeComparisonStatus",nativeMatches ? "passed":"failed"},
        {"physicalInputAcceptance","pending"},{"readerAcceptance","pending"},{"rasterAcceptance","pending"}};
    if(!prefix.isEmpty()) {
        QFile output(prefix+".json");if(!check(output.open(QIODevice::WriteOnly),"Could not save comparison report"))return;
        output.write(QJsonDocument(report).toJson());output.close();
    }
    qInfo("Surface supplement %s: rows=%d exact frames=%d guides=%d input modes=%d points=%d mismatches=%d",input ? "input":"baseline",
        int(observations.size()),framesMatched,guidesMatched,modesMatched,totalPoints,activationMismatches);
    if(parser.isSet("evidence")) {
        if(!check(window->grabWindow().save(prefix+".png"),"Whole fixture capture failed"))return;
        auto timer=new QTimer(&app);
        const int exitCode=!parser.isSet("surface-supplement-observe") &&!nativeMatches ? 1:0;
        QObject::connect(timer,&QTimer::timeout,&app,[&app,prefix,exitCode]{if(QFile::exists(prefix+".captured"))app.exit(exitCode);});
        timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(93);});return;
    }
    app.exit(!parser.isSet("surface-supplement-observe") &&!nativeMatches ? 1:0);
}

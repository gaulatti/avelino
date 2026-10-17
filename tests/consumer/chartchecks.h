#pragma once
#include <QAccessible>
#include <QPointer>
#include <QSet>

static QJsonObject chartMap(QObject *object,const char *method) {
    QVariant result;
    if(!QMetaObject::invokeMethod(object,method,Q_RETURN_ARG(QVariant,result)))return {};
    if(result.metaType()==QMetaType::fromType<QJSValue>())result=result.value<QJSValue>().toVariant();
    return QJsonObject::fromVariantMap(result.toMap());
}
static bool chartSubset(const QJsonValue &actual,const QJsonValue &expected) {
    if(expected.isObject()) {
        if(!actual.isObject())return false;const auto a=actual.toObject(),e=expected.toObject();
        for(auto i=e.begin();i!=e.end();++i)if(!a.contains(i.key())||!chartSubset(a[i.key()],i.value()))return false;
        return true;
    }
    if(expected.isArray()) {
        if(!actual.isArray())return false;const auto a=actual.toArray(),e=expected.toArray();if(a.size()!=e.size())return false;
        for(int i=0;i<a.size();++i)if(!chartSubset(a[i],e[i]))return false;return true;
    }
    return actual==expected;
}
static void runChartsConsumer(QQuickWindow *window,QGuiApplication &app,const QCommandLineParser &parser,double textScale) {
    auto check=[&](bool value,const char *message){if(!value){qCritical("Charts: %s",message);app.exit(99);}return value;};
    const auto fixture=window->property("primaryFixture").value<QQuickItem*>();if(!check(fixture,"Chart fixture missing"))return;
    QFile file(":/avelino/fixtures/native-chart-witnesses.json");if(!check(file.open(QIODevice::ReadOnly),"Chart witnesses missing"))return;
    const auto native=QJsonDocument::fromJson(file.readAll()).object();
    if(!check(native["reference"]=="fe8a1d462fbd793d883fb92086a16aa2947e32c9"&&native["accepted"]==false&&native["closed"].toArray().size()==960&&native["histories"].toArray().size()==48&&native["edges"].toArray().size()==400,"Incomplete native chart projection"))return;
    const auto prefix=parser.isSet("evidence") ? parser.value("evidence"):parser.value("charts-report");
    if(!prefix.isEmpty()&&!check(!QFile::exists(prefix+".json"),"Evidence path exists"))return;
    auto control=[&](){return fixture->property("control").value<QQuickItem*>();};
    auto environment=[&](bool dark,double scale){return check(QMetaObject::invokeMethod(window,"environment",Q_ARG(QVariant,dark),Q_ARG(QVariant,scale)),"Environment update failed");};
    auto configure=[&](const QJsonObject &configuration,bool fresh){
        if(fresh){fixture->setProperty("mounted",false);if(!check(waitForShapeFrame(window),"Unmounted frame not displayed"))return false;}
        if(!check(QMetaObject::invokeMethod(window,"configure",Q_ARG(QVariant,configuration.toVariantMap())),"Chart configuration failed"))return false;
        if(fresh)for(const auto *name:{"appearances","disappearances","callerInstances"})fixture->setProperty(name,0);
        fixture->setProperty("mounted",true);return check(waitForShapeFrame(window),"Chart did not reach stable displayed pixels");
    };
    QSet<QString> inputContexts;
    auto verifyControl=[&](){auto item=control();if(!check(item,"Chart missing"))return false;auto accessible=QAccessible::queryAccessibleInterface(item);
        if(!check(accessible&&accessible->role()==QAccessible::Graphic&&accessible->text(QAccessible::Name)==item->property("accessibleName").toString(),"Actual Qt graphic role/name unavailable"))return false;
        auto renderer=item->property("__chart").value<QObject*>();
        if(!check(renderer,"Chart renderer unavailable"))return false;
        const auto rows=renderer->property("accessibilityRows").toList();
        if(!check(accessible->text(QAccessible::Description)==QString::number(rows.size())+" data points","Actual Qt chart description unavailable"))return false;
        for(int index=0;index<rows.size();++index) {
            auto child=findVisualItem(item,"bleeckerChartData"+QString::number(index));
            auto actual=child ? QAccessible::queryAccessibleInterface(child):nullptr;
            if(!check(actual&&actual->role()==QAccessible::StaticText&&actual->text(QAccessible::Name)==rows[index].toMap()["name"].toString(),"Actual Qt data row role/name unavailable"))return false;
        }
        const auto inputContext=renderer->property("kind").toString()+(item->isEnabled() ? "-enabled":"-disabled");
        if(!inputContexts.contains(inputContext)) {
            const auto before=window->grabWindow();const auto beforeFrame=chartMap(fixture,"frame"),beforeMetrics=chartMap(fixture,"measurements");
            QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,item->mapToScene(QPointF(item->width()/2,item->height()/2)).toPoint());
            for(auto key:{Qt::Key_Tab,Qt::Key_Space,Qt::Key_Left,Qt::Key_Right,Qt::Key_Return})QTest::keyClick(window,key);
            if(!check(waitForShapeFrame(window)&&window->grabWindow()==before&&chartMap(fixture,"frame")==beforeFrame&&chartMap(fixture,"measurements")==beforeMetrics&&!item->hasActiveFocus()&&!item->activeFocusOnTab()&&item->acceptedMouseButtons()==Qt::NoButton,"Read-only chart changed pixels, geometry or focus under pointer/keyboard input"))return false;
            inputContexts.insert(inputContext);
        }
        return check(chartMap(fixture,"state")==QJsonObject{{"appearances",1},{"disappearances",0},{"wrapperInstances",1}},"Chart wrapper replaced");};
    auto save=[&](const QString &name){if(prefix.isEmpty())return true;const auto path=prefix+"-"+name+".png";return check(!QFile::exists(path)&&window->grabWindow().save(path),"Image capture exists or failed");};
    auto selected=[&](const QJsonObject &row){return row["appearance"]==(parser.isSet("dark") ? "dark":"light")&&row["textScale"].toDouble()==textScale&&row["dpr"].toDouble()==window->devicePixelRatio();};
    int geometry=0,frames=0,metrics=0,images=0;QJsonArray closed,edges,histories;
    auto observation=[&](const QJsonObject &source){
        const auto frame=chartMap(fixture,"frame"),measurement=chartMap(fixture,"measurements");const bool sameFrame=frame==source["frame"],sameMetrics=chartSubset(measurement,source["metrics"]);
        ++geometry;frames+=sameFrame;metrics+=sameMetrics;
        return QJsonObject{{"frame",frame},{"metrics",measurement},{"state",chartMap(fixture,"state")},{"nativeFrameMatches",sameFrame},{"nativeMetricsMatch",sameMetrics}};
    };
    for(const auto &value:native["closed"].toArray()) {
        const auto source=value.toObject();if(!selected(source))continue;const auto configuration=source["configuration"].toObject();
        if(!environment(parser.isSet("dark"),textScale)||!configure(configuration,true)||!verifyControl())return;
        auto observed=observation(source);observed["configuration"]=configuration;observed["reference"]=source["reference"];
        if(!save(configuration["id"].toString()))return;++images;closed.append(observed);
    }
    for(const auto &value:native["edges"].toArray()) {
        const auto source=value.toObject();if(!selected(source))continue;const auto configuration=source["configuration"].toObject();
        if(!environment(parser.isSet("dark"),textScale)||!configure(configuration,true)||!verifyControl())return;
        edges.append(QJsonObject{{"configuration",configuration},{"specification",source["specification"]},{"frame",chartMap(fixture,"frame")},{"metrics",chartMap(fixture,"measurements")},{"state",chartMap(fixture,"state")},{"reference",source["reference"]},{"nativeNonfiniteDeterminism",source["nativeNonfiniteDeterminism"]}});
        if(!save("edge-"+configuration["id"].toString()))return;++images;
    }
    for(const auto &value:native["histories"].toArray()) {
        const auto source=value.toObject();if(!selected(source))continue;QJsonArray steps;QPointer<QQuickItem> original;QPointer<QObject> renderer;QImage initial;QJsonObject initialFrame,initialMetrics;int index=0;
        for(const auto &entry:source["steps"].toArray()) {
            const auto step=entry.toObject();if(!environment(step["appearance"]=="dark",step["textScale"].toDouble())||!configure(step["configuration"].toObject(),index==0)||!verifyControl())return;
            if(index==0){original=control();renderer=control()->property("__chart").value<QObject*>();initial=window->grabWindow();initialFrame=chartMap(fixture,"frame");initialMetrics=chartMap(fixture,"measurements");}
            if(!check(original==control()&&renderer==control()->property("__chart").value<QObject*>(),"History replaced the chart or renderer"))return;
            auto observed=observation(step);observed["step"]=step["step"];observed["configuration"]=step["configuration"];observed["appearance"]=step["appearance"];observed["textScale"]=step["textScale"];observed["reference"]=step["reference"];
            if(index==1&&!check(window->grabWindow()!=initial,"Data step did not change pixels"))return;
            if(index==7) {
                const bool restored=window->grabWindow()==initial&&chartMap(fixture,"frame")==initialFrame&&chartMap(fixture,"measurements")==initialMetrics;observed["restoredInitialPixelsAndGeometry"]=restored;
                if(!restored&&!prefix.isEmpty()){initial.save(prefix+"-failure-initial.png");window->grabWindow().save(prefix+"-failure-final.png");}
                if(!check(restored,"History did not restore exact pixels and geometry"))return;
            }
            if(!save(source["configuration"].toObject()["id"].toString()+"-history-step"+QString::number(index)))return;
            ++images;steps.append(observed);++index;
        }
        histories.append(QJsonObject{{"configuration",source["configuration"]},{"steps",steps}});
    }
    if(!check(closed.size()==120&&edges.size()==50&&histories.size()==6&&geometry==168&&images==218&&inputContexts.size()==10,"Incomplete chart context"))return;
    const bool nativeGeometry=frames==geometry&&metrics==geometry;
    QJsonObject report{{"reference",native["reference"]},{"fixture","charts"},{"accepted",false},{"structuralChecks","passed"},{"nativeGeometryComparisonStatus",nativeGeometry ? "passed":"failed"},{"nativeRasterAcceptance","pending"},{"nativeNonfiniteInputDeterminism","pending; source bar NaN values produce varying initialized Y domains"},{"physicalInputAcceptance","pending"},{"readerAcceptance","pending"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},{"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},{"images",images},{"geometryObservations",geometry},{"frameMatches",frames},{"metricMatches",metrics},{"closed",closed},{"edges",edges},{"histories",histories}};
    report["qtAccessibilityChecks"]="passed; real graphic and per-data-row role/name/description interfaces";
    report["inputChecks"]="passed; synthetic pointer and keyboard leave enabled/disabled charts read-only and outside tab focus";
    report["inputContexts"]=inputContexts.size();
    if(parser.isSet("evidence")&&!check(window->grabWindow().save(prefix+".png"),"Displayed window evidence failed"))return;
    if(!prefix.isEmpty()){QFile output(prefix+".json");if(!check(output.open(QIODevice::WriteOnly|QIODevice::NewOnly),"Report write failed"))return;output.write(QJsonDocument(report).toJson());}
    qInfo("Installed charts: 120 closed inputs, 50 edge inputs, six retained histories; exact frame sets %d/168 and metric sets %d/168. Native raster/readers remain pending.",frames,metrics);
    const int code=parser.isSet("charts-observe")||nativeGeometry ? 0:1;
    if(parser.isSet("evidence")) {
        auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,prefix,code]{if(QFile::exists(prefix+".captured"))app.exit(code);});timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(93);});return;
    }
    app.exit(code);
}

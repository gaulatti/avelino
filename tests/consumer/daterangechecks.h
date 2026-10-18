#pragma once
#include <QPointer>

static QJsonObject dateRangeSnapshot(QObject *fixture){
    QVariant value;
    if(!QMetaObject::invokeMethod(fixture,"snapshot",Q_RETURN_ARG(QVariant,value)))qFatal("DateRangePicker snapshot missing");
    return QJsonObject::fromVariantMap(value.toMap());
}
static void runDateRangeConsumer(QQuickWindow *window,QGuiApplication &app,const QCommandLineParser &parser,double textScale){
    auto check=[&](bool value,const char *message){if(!value){qCritical("DateRangePicker: %s",message);app.exit(103);}return value;};
    auto fixture=window->property("primaryFixture").value<QQuickItem*>();if(!check(fixture,"Fixture missing"))return;
    const auto prefix=parser.isSet("evidence")?parser.value("evidence"):parser.value("date-range-report");
    if(!prefix.isEmpty()&&!check(!QFile::exists(prefix+".json"),"Report already exists"))return;
    auto call=[&](QObject *target,const char *method,const QJsonObject &value){return check(QMetaObject::invokeMethod(target,method,Q_ARG(QVariant,value.toVariantMap())),"Caller update failed");};
    auto frame=[&](){return check(waitForShapeFrame(window)&&waitForShapeFrame(window),"Rendered frame missing");};
    auto save=[&](const QString &name){return prefix.isEmpty()||check(!QFile::exists(prefix+"-"+name+".png")&&window->grabWindow().save(prefix+"-"+name+".png"),"Capture exists or failed");};
    QJsonArray closed,inputs,operators;int modelMatches=0,geometryMatches=0;
    auto configure=[&](const QJsonObject &configuration){
        fixture->setProperty("mounted",false);if(!frame())return false;
        if(!check(QMetaObject::invokeMethod(fixture,"resetCounters"),"Counter reset missing")||!call(window,"configure",configuration))return false;
        fixture->setProperty("mounted",true);return frame()&&check(fixture->property("picker").value<QQuickItem*>(),"Picker missing");
    };
    if(parser.isSet("date-range-gallery")){
        for(const QString name:{"style-field","owner-ignore","owner-delay","apply","bounds","crossed","disabled","disabled","locale","calendar","timezone","size","rtl","narrow","theme","default","style-graphical"}){
            auto button=findVisualItem(window->contentItem(),"dateOperator-"+name);
            if(!check(button&&button->isVisible()&&button->isEnabled(),"Gallery operator missing"))return;
            QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,button->mapToScene(QPointF(button->width()/2,button->height()/2)).toPoint());
            if(!frame())return;
            operators.append(QJsonObject{{"operator",name},{"actual",dateRangeSnapshot(fixture)}});
            if(!save(QStringLiteral("gallery-%1-%2").arg(operators.size()).arg(name)))return;
        }
    }else{
        QFile input(":/avelino/fixtures/native-date-range-witnesses.json");if(!check(input.open(QIODevice::ReadOnly),"Native observations missing"))return;
        const auto native=QJsonDocument::fromJson(input.readAll()).object();
        if(!check(native["reference"]=="fe8a1d462fbd793d883fb92086a16aa2947e32c9"&&native["accepted"]==false&&native["closed"].toArray().size()==384,"Native observations incomplete"))return;
        for(const auto &item:native["closed"].toArray()){
            const auto row=item.toObject();
            if(row["appearance"]!=(parser.isSet("dark")?"dark":"light")||row["textScale"].toDouble()!=textScale||row["dpr"].toDouble()!=window->devicePixelRatio())continue;
            const auto configuration=row["configuration"].toObject();if(!configure(configuration))return;
            const auto actual=dateRangeSnapshot(fixture);auto actualFrames=actual["frames"].toObject();actualFrames.remove("arrow");
            const bool sameModel=actual["model"]==row["model"]&&actual["displayed"]==row["displayed"];
            const bool sameGeometry=actualFrames==row["frames"];modelMatches+=sameModel;geometryMatches+=sameGeometry;
            closed.append(QJsonObject{{"configuration",configuration},{"actual",actual},{"native",row},{"modelMatches",sameModel},{"geometryMatches",sameGeometry}});
            if(!check(actual["model"].toObject()["requests"].toArray().isEmpty(),"Cold presentation requested a binding change")||!save(configuration["id"].toString()))return;
        }
        if(!check(closed.size()==48,"Expected 48 cold contexts per profile"))return;
        // These are actual Qt template input events. Native OS input is retained
        // separately; this does not establish platform reader/physical acceptance.
        const QJsonObject base{{"id","input"},{"start",1710000000.625},{"end",1710864000.125},{"locale","en_US"},{"calendar","gregorian"},{"timeZone","UTC"},{"pickerStyle","field"},{"controlSize","regular"},{"owner","echo"}};
        for(const QString policy:{"echo","ignore","delay"}){
            auto configuration=base;configuration["owner"]=policy;if(!configure(configuration))return;
            auto picker=fixture->property("picker").value<QQuickItem*>();auto editor=picker->property("startInput").value<QQuickItem*>();
            if(!check(editor,"Owned editor missing"))return;
            editor->forceActiveFocus(Qt::OtherFocusReason);if(!frame())return;
            QTest::keyClick(editor->window(),Qt::Key_Right);QTest::keyClick(editor->window(),Qt::Key_Right);QTest::keyClick(editor->window(),Qt::Key_Up);
            if(!frame())return;
            const auto actual=dateRangeSnapshot(fixture),model=actual["model"].toObject();
            if(!check(actual["displayed"].toArray()[0].toDouble()==1741536000.625&&model["start"].toDouble()==(policy=="echo"?1741536000.625:1710000000.625)&&model["end"].toDouble()==1710864000.125&&model["requests"].toArray().size()==1,"Owner/input behavior differs"))return;
            inputs.append(QJsonObject{{"owner",policy},{"actual",actual}});if(!save("input-"+policy))return;
        }
    }
    const bool strict=closed.isEmpty()||(modelMatches==closed.size()&&geometryMatches==closed.size());
    if(!prefix.isEmpty()){
        const QJsonObject report{{"fixture","date-range"},{"structuralChecks","passed"},{"platform",QGuiApplication::platformName()},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"width",window->width()},{"height",window->height()},{"appearance",parser.isSet("dark")?"dark":"light"},{"accepted",false},{"reference","fe8a1d462fbd793d883fb92086a16aa2947e32c9"},{"textScale",textScale},{"dpr",window->devicePixelRatio()},{"closed",closed},{"input",inputs},{"gallery",operators},{"modelMatches",modelMatches},{"geometryMatches",geometryMatches},{"strictObservationsMatch",strict},{"visualAcceptance","pending"},{"readerPhysicalAcceptance","pending"}};
        QFile output(prefix+".json");if(!check(output.open(QIODevice::WriteOnly|QIODevice::NewOnly)&&output.write(QJsonDocument(report).toJson())>0,"Report write failed"))return;
    }
    qInfo("DateRangePicker: %lld cold contexts, %d exact models, %d exact geometry, %lld input owners, %lld gallery operators; acceptance pending",closed.size(),modelMatches,geometryMatches,inputs.size(),operators.size());
    if(!strict&&!parser.isSet("date-range-observe")){check(false,"Native model/geometry differs; observations retained");return;}
    if(parser.isSet("evidence")){
        auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,prefix]{if(QFile::exists(prefix+".captured"))app.quit();});timer->start(100);
        QTimer::singleShot(10000,&app,[&app]{app.exit(93);});return;
    }
    app.quit();
}

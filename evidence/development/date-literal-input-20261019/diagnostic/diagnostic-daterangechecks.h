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
    QJsonArray closed,inputs,operators,histories,chinese,literalInput;int modelMatches=0,geometryMatches=0,historyModels=0,historyGeometry=0,historyInstances=0,historyCalendars=0,historyEnvironment=0,chineseModels=0,chineseTexts=0,chineseCalendars=0,chineseIntrinsic=0;
    auto configure=[&](const QJsonObject &configuration){
        fixture->setProperty("mounted",false);if(!frame())return false;
        if(!check(QMetaObject::invokeMethod(fixture,"resetCounters"),"Counter reset missing")||!call(window,"configure",configuration))return false;
        fixture->setProperty("mounted",true);return frame()&&check(fixture->property("picker").value<QQuickItem*>(),"Picker missing");
    };
    if(parser.isSet("date-range-gallery")){
        for(const QString name:{"style-field","owner-ignore","owner-delay","apply","bounds","crossed","disabled","disabled","locale","calendar","timezone","size","rtl","narrow","theme","chinese-en_US","chinese-zh_CN","chinese-ko_KR","leap-month","default","style-graphical"}){
            auto button=findVisualItem(window->contentItem(),"dateOperator-"+name);
            if(!check(button&&button->isVisible()&&button->isEnabled(),"Gallery operator missing"))return;
            QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,button->mapToScene(QPointF(button->width()/2,button->height()/2)).toPoint());
            if(!frame())return;
            const auto actual=dateRangeSnapshot(fixture);
            if(name=="leap-month"){
                QFile source(":/avelino/fixtures/native-date-chinese-witnesses.json");if(!check(source.open(QIODevice::ReadOnly),"Leap source observation missing"))return;
                QJsonObject expected;
                for(const auto &entry:QJsonDocument::fromJson(source.readAll()).object()["cases"].toArray()){
                    const auto row=entry.toObject();if(row["configuration"].toObject()["id"]=="chinese-zh-cn-leap-regular")expected=row;
                }
                if(!check(!expected.isEmpty()&&actual["displayed"]==expected["displayed"]&&actual["editorText"]==expected["editorText"]&&actual["editorRoles"]==expected["editableRoles"],"Leap fixture presentation differs from source"))return;
                for(int index=0;index<2;++index){
                    const auto parts=actual["calendarParts"].toArray()[index].toObject(),native=expected["calendarParts"].toArray()[index].toObject();
                    for(const auto &key:native.keys())if(!check(parts[key]==native[key],"Leap fixture hidden calendar field differs"))return;
                }
            }
            operators.append(QJsonObject{{"operator",name},{"actual",actual}});
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
        const bool historySupported=!parser.isSet("dark")&&textScale==1&&window->devicePixelRatio()==1;
        const auto history=native["history"].toObject();
        if(!check(history["steps"].toArray().size()==17,"Native typed history missing"))return;
        if(historySupported){
            QList<QPointer<QQuickItem>> observedEditors;
            auto identity=[&](QQuickItem *item){
                for(qsizetype i=0;i<observedEditors.size();++i)if(observedEditors[i]&&observedEditors[i]==item)return int(i+1);
                observedEditors.append(QPointer<QQuickItem>(item));return int(observedEditors.size());
            };
            auto external=[&](const char *method,double value){return check(QMetaObject::invokeMethod(fixture,method,Q_ARG(double,value)),"External date update failed");};
            auto environment=[&](bool dark){return check(QMetaObject::invokeMethod(window,"environment",Q_ARG(QVariant,dark),Q_ARG(QVariant,textScale)),"Appearance update failed");};
            for(const auto &entry:history["steps"].toArray()){
                const auto row=entry.toObject(),action=row["action"].toObject();const auto kind=action["kind"].toString();
                if(kind=="initial"){if(!environment(false)||!configure(action["configuration"].toObject()))return;}
                else if(kind=="externalStart"){if(!external("externalStart",action["value"].toDouble()))return;}
                else if(kind=="externalEnd"){if(!external("externalEnd",action["value"].toDouble()))return;}
                else if(kind=="configuration"){if(!call(fixture,"replaceConfiguration",action["configuration"].toObject()))return;}
                else if(kind=="appearance"){if(!environment(action["dark"].toBool()))return;}
                else if(kind=="restore"){
                    const auto definition=action["configuration"].toObject();
                    if(!call(fixture,"replaceConfiguration",definition)||!external("externalStart",definition["start"].toDouble())||!external("externalEnd",definition["end"].toDouble())||!environment(action["dark"].toBool()))return;
                }else{check(false,"Unknown typed history action");return;}
                if(!frame())return;
                auto picker=fixture->property("picker").value<QQuickItem*>();if(!check(picker,"History picker disappeared"))return;
                QJsonArray actualIds,nativeIds;
                for(const char *endpoint:{"startInput","endInput"}){
                    auto editor=picker->property(endpoint).value<QQuickItem*>();if(!check(editor,"History editor missing"))return;actualIds.append(identity(editor));
                }
                for(const auto &value:row["nativeInstances"].toArray())nativeIds.append(value.toObject()["instance"]);
                const auto actual=dateRangeSnapshot(fixture);auto actualFrames=actual["frames"].toObject();actualFrames.remove("arrow");
                const bool sameModel=actual["model"]==row["model"]&&actual["displayed"]==row["displayed"];
                const bool sameGeometry=actualFrames==row["frames"],sameInstances=actualIds==nativeIds;
                bool sameCalendar=true;const auto parts=actual["calendarParts"].toArray(),instances=row["nativeInstances"].toArray();
                if(!check(parts.size()==2&&instances.size()==2,"Calendar history observations incomplete"))return;
                for(int i=0;i<2;++i){
                    const auto value=parts[i].toObject(),calendar=instances[i].toObject()["calendar"].toObject();
                    for(const QString key:{"firstWeekday","minimumDaysInFirstWeek"})sameCalendar&=value[key]==calendar[key];
                    const auto expected=calendar["components"].toObject();for(const auto &key:expected.keys())sameCalendar&=value[key]==expected[key];
                }
                const auto configuration=row["configuration"].toObject();
                const bool sameEnvironment=window->property("fixtureDark").toBool()==row["dark"].toBool()&&actual["enabled"].toBool()==!configuration["disabled"].toBool()&&actual["mirrored"]==configuration["rtl"]&&actual["controlSize"]==configuration["controlSize"]&&actual["style"]==configuration["pickerStyle"]&&actual["locale"]==configuration["locale"]&&actual["calendar"]==configuration["calendar"]&&actual["timeZone"]==configuration["timeZone"];
                historyEnvironment+=sameEnvironment;historyModels+=sameModel;historyGeometry+=sameGeometry;historyInstances+=sameInstances;historyCalendars+=sameCalendar;
                histories.append(QJsonObject{{"step",row["step"]},{"action",action},{"actual",actual},{"native",row},{"actualEditorInstances",actualIds},{"nativeEditorInstances",nativeIds},{"modelMatches",sameModel},{"geometryMatches",sameGeometry},{"editorInstancesMatch",sameInstances},{"calendarMatches",sameCalendar},{"environmentMatches",sameEnvironment},{"actualDark",window->property("fixtureDark").toBool()},{"nativeDark",row["dark"]},{"nativeOuterProbeScope","raw retained probes; restore retains the preceding graphical outer height"}});
                if(!check(actual["model"].toObject()["requests"].toArray().isEmpty(),"Typed history unexpectedly requested a binding change")||!save("history-"+row["step"].toString()))return;
            }
        }
        if(!check(histories.size()==(historySupported?17:0),"Typed history context incomplete"))return;
        QFile chineseSource(":/avelino/fixtures/native-date-chinese-witnesses.json");if(!check(chineseSource.open(QIODevice::ReadOnly),"Chinese native observations missing"))return;
        const auto supplement=QJsonDocument::fromJson(chineseSource.readAll()).object();
        if(!check(supplement["reference"]==native["reference"]&&supplement["accepted"]==false&&supplement["cases"].toArray().size()==36,"Chinese native observations incomplete"))return;
        for(const auto &item:supplement["cases"].toArray()){
            const auto row=item.toObject(),configuration=row["configuration"].toObject();if(!configure(configuration))return;
            const auto actual=dateRangeSnapshot(fixture);
            const bool sameModel=actual["model"]==row["model"]&&actual["displayed"]==row["displayed"];
            const bool sameText=actual["editorText"]==row["editorText"]&&actual["editorRoles"]==row["editableRoles"];
            bool sameCalendar=true,sameIntrinsic=true;
            for(int index=0;index<2;++index){
                const auto expected=row["calendarParts"].toArray()[index].toObject(),parts=actual["calendarParts"].toArray()[index].toObject();
                for(const auto &key:expected.keys())sameCalendar&=parts[key]==expected[key];
                const auto size=row["intrinsic"].toArray()[index].toObject(),frame=actual["frames"].toObject()[index==0?"start":"end"].toObject();
                sameIntrinsic&=frame["width"]==size["width"]&&frame["height"]==size["height"];
            }
            if(!check(sameModel&&sameText&&sameCalendar,"Chinese model, field strings or calendar parts differ"))return;
            chineseModels+=sameModel;chineseTexts+=sameText;chineseCalendars+=sameCalendar;chineseIntrinsic+=sameIntrinsic;
            chinese.append(QJsonObject{{"configuration",configuration},{"actual",actual},{"native",row},{"modelMatches",sameModel},{"textMatches",sameText},{"calendarMatches",sameCalendar},{"intrinsicSizeMatches",sameIntrinsic}});
            if(!save(configuration["id"].toString()))return;
        }
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
        QFile literalSource(":/avelino/fixtures/native-date-literal-input-witnesses.json");
        if(!check(literalSource.open(QIODevice::ReadOnly),"Native literal input observations missing"))return;
        const auto literalWitness=QJsonDocument::fromJson(literalSource.readAll()).object();
        if(!check(literalWitness["reference"]==native["reference"]&&literalWitness["accepted"]==false
            &&literalWitness["profiles"].toArray().size()==4,"Native literal input observations incomplete"))return;
        auto literalState=[&](const QString &endpoint){
            QVariant state;
            if(!QMetaObject::invokeMethod(fixture,"literalInputState",Q_RETURN_ARG(QVariant,state),Q_ARG(QString,endpoint)))return QJsonObject{};
            return QJsonObject::fromVariantMap(state.toMap());
        };
        for(const auto &entry:literalWitness["profiles"].toArray())for(const bool callerRtl:{false,true})for(const QString endpoint:{"start","end"}){
            const auto profile=entry.toObject();auto configuration=base;
            configuration["pickerStyle"]="inherit";configuration["locale"]=profile["locale"];configuration["calendar"]=profile["calendar"];configuration["rtl"]=callerRtl;
            if(!configure(configuration))return;
            auto settings=profile;settings["endpoint"]=endpoint;QVariant prepared;
            if(!check(QMetaObject::invokeMethod(fixture,"prepareLiteralInput",Q_RETURN_ARG(QVariant,prepared),Q_ARG(QVariant,settings.toVariantMap())),"Literal input setup failed")||!frame())return;
            const auto point=QJsonObject::fromVariantMap(prepared.toMap());
            auto picker=fixture->property("picker").value<QQuickItem*>();auto editor=picker->property((endpoint+"Input").toUtf8()).value<QQuickItem*>();
            const auto before=literalState(endpoint),beforeModel=dateRangeSnapshot(fixture)["model"].toObject();const auto beforePixels=window->grabWindow();
            if(!check(editor&&!before.isEmpty()&&before["activeFocus"].toBool()&&!before["calendarVisible"].toBool()&&!beforePixels.isNull(),"Literal input baseline missing"))return;
            QTest::mouseClick(editor->window(),Qt::LeftButton,Qt::NoModifier,editor->mapToScene(QPointF(point["x"].toDouble(),point["y"].toDouble())).toPoint());
            if(!frame())return;
            const auto after=literalState(endpoint),afterModel=dateRangeSnapshot(fixture)["model"].toObject();const auto afterPixels=window->grabWindow();
            if(after!=before||afterModel!=beforeModel||beforePixels!=afterPixels){
                const QJsonObject failure{{"sourceCase",profile["nativeCase"]},{"endpoint",endpoint},{"callerRtl",callerRtl},{"point",point},
                    {"before",before},{"after",after},{"beforeModel",beforeModel},{"afterModel",afterModel},
                    {"sameState",after==before},{"sameModel",afterModel==beforeModel},{"samePixels",beforePixels==afterPixels}};
                qWarning().noquote()<<"LITERAL_FAILURE"<<QJsonDocument(failure).toJson(QJsonDocument::Compact);
                if(!prefix.isEmpty()){
                    beforePixels.save(prefix+"-failed-before.png");afterPixels.save(prefix+"-failed-after.png");
                    QFile detail(prefix+"-failed.json");if(detail.open(QIODevice::WriteOnly))detail.write(QJsonDocument(failure).toJson());
                }
            }
            if(!check(after==before&&afterModel==beforeModel&&beforePixels==afterPixels,"Literal click changed selection, pixels, focus, model or calendar"))return;
            QTest::keyClick(editor->window(),Qt::Key_Up);if(!frame())return;
            const auto stepped=dateRangeSnapshot(fixture),model=stepped["model"].toObject();const auto requests=model["requests"].toArray();
            if(!check(requests.size()==1&&requests[0].toObject()["endpoint"]==endpoint
                &&literalState(endpoint)["selectedSegment"]==before["selectedSegment"],"Literal click changed the following edit target"))return;
            if(endpoint=="start"){
                if(!check(model["start"]==profile["nativeStartAfterUp"]&&model["end"].toDouble()==1710864000.125,"Literal retained-field edit differs from native source"))return;
            }else if(!check(model["start"].toDouble()==1710000000.625,"End literal edit changed the start"))return;
            literalInput.append(QJsonObject{{"sourceCase",profile["nativeCase"]},{"endpoint",endpoint},{"callerRtl",callerRtl},
                {"point",point},{"before",before},{"after",after},{"samePixels",true},{"afterUp",stepped},{"nativeValueCompared",endpoint=="start"}});
            if(!save("literal-"+profile["nativeCase"].toString()+"-"+endpoint+(callerRtl?"-rtl1":"-rtl0")))return;
        }
        if(!check(literalInput.size()==16,"Literal input matrix incomplete"))return;
    }
    const bool strict=closed.isEmpty()||(modelMatches==closed.size()&&geometryMatches==closed.size()&&historyModels==histories.size()&&historyGeometry==histories.size()&&historyInstances==histories.size()&&historyCalendars==histories.size()&&historyEnvironment==histories.size()&&chineseModels==chinese.size()&&chineseTexts==chinese.size()&&chineseCalendars==chinese.size()&&chineseIntrinsic==chinese.size());
    if(!prefix.isEmpty()){
        const QJsonObject report{{"fixture","date-range"},{"structuralChecks","passed"},{"platform",QGuiApplication::platformName()},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"width",window->width()},{"height",window->height()},{"appearance",parser.isSet("dark")?"dark":"light"},{"accepted",false},{"reference","fe8a1d462fbd793d883fb92086a16aa2947e32c9"},{"textScale",textScale},{"dpr",window->devicePixelRatio()},{"closed",closed},{"input",inputs},{"literalInput",literalInput},{"gallery",operators},{"histories",histories},{"chinese",chinese},{"chineseModelMatches",chineseModels},{"chineseTextMatches",chineseTexts},{"chineseCalendarMatches",chineseCalendars},{"chineseIntrinsicSizeMatches",chineseIntrinsic},{"historyModelMatches",historyModels},{"historyGeometryMatches",historyGeometry},{"historyEditorInstanceMatches",historyInstances},{"historyCalendarMatches",historyCalendars},{"historyEnvironmentMatches",historyEnvironment},{"modelMatches",modelMatches},{"geometryMatches",geometryMatches},{"strictObservationsMatch",strict},{"visualAcceptance","pending"},{"readerPhysicalAcceptance","pending"}};
        QFile output(prefix+".json");if(!check(output.open(QIODevice::WriteOnly|QIODevice::NewOnly)&&output.write(QJsonDocument(report).toJson())>0,"Report write failed"))return;
    }
    qInfo("DateRangePicker native literal input: %lld Qt pointer/retained-field checks; native initial-field and RTL glyph acceptance pending",literalInput.size());
    qInfo("DateRangePicker typed history: %lld steps, %d model/lifecycle, %d raw geometry, %d editor identity and %d calendar matches",histories.size(),historyModels,historyGeometry,historyInstances,historyCalendars);
    qInfo("DateRangePicker: %lld cold contexts, %d exact models, %d exact geometry, %lld input owners, %lld gallery operators; acceptance pending",closed.size(),modelMatches,geometryMatches,inputs.size(),operators.size());
    if(!strict&&!parser.isSet("date-range-observe")){check(false,"Native model/geometry differs; observations retained");return;}
    if(parser.isSet("evidence")){
        auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,prefix]{if(QFile::exists(prefix+".captured"))app.quit();});timer->start(100);
        QTimer::singleShot(10000,&app,[&app]{app.exit(93);});return;
    }
    app.quit();
}

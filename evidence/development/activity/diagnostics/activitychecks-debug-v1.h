#pragma once

static void runActivityConsumer(QQuickWindow *window,QGuiApplication &app,
                                const QCommandLineParser &parser,double textScale) {
    auto check=[&app](bool ok,const QString &message){if(!ok){qCritical("Installed ActivityItem: %s",qPrintable(message));app.exit(253);}return ok;};
    const auto fixture=window->property("primaryFixture").value<QQuickItem*>();
    const auto control=window->property("primaryControl").value<QQuickItem*>();
    if(!check(fixture && control,"Missing public ActivityItem and shared fixture"))return;
    QFile file(":/avelino/fixtures/native-activity-witnesses.json");
    if(!check(file.open(QIODevice::ReadOnly),"Native action witnesses missing in independent package"))return;
    const auto witnesses=QJsonDocument::fromJson(file.readAll()).object();
    const auto traces=witnesses.value("traces").toArray();
    if(!check(traces.size()==13 && witnesses.value("reference").toString()=="fe8a1d462fbd793d883fb92086a16aa2947e32c9","Native witness coverage"))return;
    auto variant=[](QVariant value){return value.metaType()==QMetaType::fromType<QJSValue>() ? value.value<QJSValue>().toVariant():value;};
    auto configure=[&](const QVariantMap &configuration) {
        if(!check(QMetaObject::invokeMethod(window,"configure",Q_ARG(QVariant,QVariant(configuration))),"Producer update failed"))return false;
        QTest::qWait(10);return true;
    };
    auto action=[fixture](const QString &name){const auto item=findVisualItem(fixture,"activityAction"+name);return item ? item->property("inputItem").value<QQuickItem*>():nullptr;};
    auto center=[](QQuickItem *item){return item->mapToScene(QPointF(item->width()/2,item->height()/2)).toPoint();};
    auto click=[&](QQuickItem *item){if(!check(item,"Missing action target"))return false;QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,center(item));return true;};
    QJsonArray results;int snapshots=0;QPoint pressed;
    for(const auto &value:traces) {
        const auto trace=value.toObject();const auto events=trace.value("events").toArray();
        if(!configure(QVariantMap{{"actions","empty"},{"disabled",false}}))return;
        fixture->setProperty("calls",QVariantList{});fixture->setProperty("appears",0);fixture->setProperty("disappears",0);fixture->setProperty("reportedCount",0);
        QJsonArray observations;
        for(const auto &entry:events) {
            const auto event=entry.toObject(),expected=event.value("state").toObject();const auto name=event.value("action").toString();
            const auto configuration=expected.value("configuration").toObject().toVariantMap();
            const auto current=variant(window->property("model")).toMap();bool changed=false;
            for(auto it=configuration.begin();it!=configuration.end();++it)if(current.value(it.key())!=it.value()){changed=true;break;}
            if(changed && !configure(configuration))return;
            if(name.startsWith("click-")) {
                const auto part=name.mid(6);
                const auto item=part=="padding" ? control->property("presentationItem").value<QQuickItem*>():findVisualItem(fixture,
                    part=="badge" ? "bleeckerActivityBadge":part=="title" ? "bleeckerActivityTitle":part=="detail" ? "bleeckerActivityDetail":part=="timestamp" ? "bleeckerActivityTimestamp":"bleeckerActivitySpacer");
                if(!check(item,"Missing body target "+part))return;
                const auto point=part=="padding" ? item->mapToScene(QPointF(item->width()/2,4)).toPoint():center(item);
                qInfo()<<"Body click"<<name<<point<<"target"<<item->position()<<item->size()<<"review"<<center(action("Review"))<<action("Review")->size();
                QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,point);
            }else if(name=="review" || name=="archive") {if(!click(action(name=="review" ? "Review":"Archive")))return;}
            else if(name=="review-cancel") {
                const auto item=action("Review");if(!check(item,"Missing canceled action"))return;
                QTest::mousePress(window,Qt::LeftButton,Qt::NoModifier,center(item));
                QTest::mouseMove(window,QPoint(4,window->height()-4));QTest::mouseRelease(window,Qt::LeftButton,Qt::NoModifier,QPoint(4,window->height()-4));
            }else if(name=="down") {
                const auto item=action("Review");if(!check(item,"Missing pressed action"))return;pressed=center(item);
                QTest::mousePress(window,Qt::LeftButton,Qt::NoModifier,pressed);
            }else if(name=="up")QTest::mouseRelease(window,Qt::LeftButton,Qt::NoModifier,pressed);
            else if(name=="hold-or-update")QTest::qWait(trace.value("fixture").toString()=="during-down-hold" ? 1100:10);
            else if(name.startsWith("increment") || name=="disabled-counter" || name=="enabled-counter") {if(!click(action("Counter")))return;}
            else if(!check(QStringList{"initial","producer-update","remove-actions","restore-actions","replace-actions","restore-after-replacement"}.contains(name),"Unmapped native event "+name))return;
            QTest::qWait(5);
            const auto calls=QJsonArray::fromVariantList(variant(fixture->property("calls")).toList());
            const bool counter=configuration.value("actions").toString()=="counter";
            const QJsonObject values=counter ? QJsonObject{{"counter",fixture->property("localValue").toInt()}}:QJsonObject{};
            const QJsonObject actual{{"calls",calls},{"actionValues",values},{"count",fixture->property("reportedCount").toInt()},
                {"appears",fixture->property("appears").toInt()},{"disappears",fixture->property("disappears").toInt()}};
            for(const auto &key:QStringList{"calls","actionValues","count","appears","disappears"}) {
                if(actual.value(key)!=expected.value(key))qInfo()<<"Mismatch"<<key<<"actual"<<actual<<"expected"<<expected;
                if(!check(actual.value(key)==expected.value(key),trace.value("fixture").toString()+" "+name+" "+key+" mismatch"))return;
            }
            ++snapshots;observations.append(QJsonObject{{"action",name},{"actual",actual},{"nativeStateMatch",true}});
        }
        results.append(QJsonObject{{"fixture",trace.value("fixture")},{"events",observations}});
    }
    if(!check(snapshots==94,"Native snapshot count"))return;
    if(!configure(QVariantMap{{"actions","multi"},{"proposalWidth",600},{"disabled",false},{"rtl",false},{"title","Edition updated"},{"detail","Ready for review"},{"timestamp","2 min ago"},{"symbol","clock"}}))return;
    const auto before=findVisualItem(window->contentItem(),"activityBefore"),after=findVisualItem(window->contentItem(),"activityAfter");
    const auto beforeInput=before ? before->property("inputItem").value<QQuickItem*>():nullptr,afterInput=after ? after->property("inputItem").value<QQuickItem*>():nullptr;
    const auto review=action("Review"),archive=action("Archive");
    if(!check(beforeInput && afterInput && review && archive,"Missing traversal targets"))return;
    beforeInput->forceActiveFocus(Qt::TabFocusReason);
    for(auto item:{review,archive,afterInput}){QTest::keyClick(window,Qt::Key_Tab);if(!check(item->hasActiveFocus(),"Forward Tab action traversal"))return;}
    for(auto item:{archive,review,beforeInput}){QTest::keyClick(window,Qt::Key_Backtab);if(!check(item->hasActiveFocus(),"Backward Tab action traversal"))return;}
    for(const auto &pair:QList<QPair<QString,double>>{{"Title",14},{"Detail",12},{"Timestamp",10}}) {
        const auto label=findVisualItem(fixture,"bleeckerActivity"+pair.first);
        if(!check(label && qAbs(label->property("logicalPixelSize").toDouble()-pair.second)<.001,"Fixed field typography"))return;
        const auto ax=QAccessible::queryAccessibleInterface(label);
        if(!check(ax && ax->role()==QAccessible::StaticText && ax->text(QAccessible::Name)==label->property("text").toString(),"Qt static text accessibility"))return;
    }
    const auto ax=QAccessible::queryAccessibleInterface(review);
    if(!check(ax && ax->role()==QAccessible::Button && ax->text(QAccessible::Name)=="Review","Qt action accessibility"))return;
    if(parser.isSet("evidence")) {
        const auto path=parser.value("evidence");if(!check(window->grabWindow().save(path+".png"),"Cannot save original window pixels"))return;
        const QJsonObject meta{{"accepted",false},{"fixture","activity-item"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},
            {"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},{"textScale",textScale},
            {"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"appearance",parser.isSet("dark") ? "dark":"light"},
            {"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},{"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},
            {"windowCaptureMethod","QQuickWindow::grabWindow; full session captured separately"},
            {"activityChecks","passed"},{"callerStateChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},
            {"nativeTraces",results},{"nativeSnapshots",snapshots},{"inputMethod","QtTest synthetic mouse/key events; physical input and native keyboard/reader acceptance pending"}};
        QFile output(path+".json");if(!check(output.open(QIODevice::WriteOnly),"Cannot save metadata"))return;output.write(QJsonDocument(meta).toJson());output.close();
        auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path]{if(QFile::exists(path+".captured"))app.exit(0);});
        timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(252);});
        qInfo("Installed ActivityItem: 13 traces / 94 native snapshots and Qt focus/accessibility passed; awaiting full session capture");return;
    }
    qInfo("Installed ActivityItem: 13 traces / 94 native action/lifecycle snapshots and Qt focus/accessibility passed");app.quit();
}

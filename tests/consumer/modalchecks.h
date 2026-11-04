#pragma once
#include <QMouseEvent>
#include <QSignalSpy>

static void runModalConsumer(QQuickWindow *window,QGuiApplication &app,
                             const QCommandLineParser &parser,double textScale) {
    auto check=[&app](bool ok,const QString &message){if(!ok){qCritical("Installed Modal: %s",qPrintable(message));app.exit(255);}return ok;};
    auto variant=[](QVariant value){return value.metaType()==QMetaType::fromType<QJSValue>() ? value.value<QJSValue>().toVariant():value;};
    auto array=[&](QObject *object,const char *name){return QJsonArray::fromVariantList(variant(object->property(name)).toList());};
    QFile file(":/avelino/fixtures/native-modal-witnesses.json");
    if(!check(file.open(QIODevice::ReadOnly),"Native state/input witnesses missing from independent package"))return;
    const auto witnesses=QJsonDocument::fromJson(file.readAll()).object();
    if(!check(witnesses.value("reference").toString()=="fe8a1d462fbd793d883fb92086a16aa2947e32c9"
        && witnesses.value("traces").toArray().size()==14 && witnesses.value("reopening").toArray().size()==3,"Native witness coverage"))return;
    int frames=0,snapshots=0,clippingQueries=0,glyphQueries=0,peakSourceWindows=0;
    QString frameContext="initial";
    auto setTextScale=[&](double value){return check(QMetaObject::invokeMethod(window,"setTextScale",Q_ARG(QVariant,QVariant(value))),"Replay text scale update failed");};
    if(!setTextScale(1))return;
    QJsonArray focusTransitions;
    // isActive() includes the transient chain. Keyboard input needs this
    // window itself and its Quick focus scope to have received focus.
    auto parentKeyboardReady=[&](){return QGuiApplication::focusWindow()==window && window->contentItem()->hasActiveFocus();};
    auto parentFocus=[&](const QString &phase){
        window->requestActivate();
        const bool ready=QTest::qWaitFor(parentKeyboardReady,5000);
        focusTransitions.append(QJsonObject{{"phase",phase},{"parentIsFocusWindow",QGuiApplication::focusWindow()==window},
            {"parentRootActiveFocus",window->contentItem()->hasActiveFocus()}});
        return check(ready,QStringLiteral("Parent keyboard focus unavailable: %1; focus window %2; chain active %3; Quick root focus %4")
            .arg(phase,QGuiApplication::focusWindow()?QGuiApplication::focusWindow()->title():"none")
            .arg(window->isActive()).arg(window->contentItem()->hasActiveFocus()));
    };
    auto frame=[&](QQuickWindow *owner){
        if(!check(owner && owner->isVisible(),"Cannot await a hidden presentation"))return false;
        QSignalSpy synchronized(owner,&QQuickWindow::afterSynchronizing);owner->update();
        if(!check(synchronized.count()>0 || synchronized.wait(5000),QStringLiteral("Presentation did not synchronize: %1; context %2; visible %3, exposed %4, active %5, size %6x%7, transient parent %8")
            .arg(owner->title(),frameContext).arg(owner->isVisible()).arg(owner->isExposed()).arg(owner->isActive())
            .arg(owner->width()).arg(owner->height()).arg(owner->transientParent() ? owner->transientParent()->title():"none")))return false;
        QSignalSpy displayed(owner,&QQuickWindow::frameSwapped);owner->update();
        if(!check(displayed.count()>0 || displayed.wait(5000),QStringLiteral("Presentation did not display a frame: %1; context %2; exposed %3, active %4")
            .arg(owner->title(),frameContext).arg(owner->isExposed()).arg(owner->isActive())))return false;
        ++frames;return true;
    };
    auto send=[&](QQuickWindow *owner,const QPointF &point,QEvent::Type type){
        const auto global=owner->mapToGlobal(point);
        QMouseEvent event(type,point,global,Qt::LeftButton,
                          type==QEvent::MouseButtonPress ? Qt::LeftButton:Qt::NoButton,Qt::NoModifier);
        QCoreApplication::sendEvent(owner,&event);
    };
    auto clickPoint=[&](QQuickWindow *owner,const QPointF &point){send(owner,point,QEvent::MouseButtonPress);send(owner,point,QEvent::MouseButtonRelease);QCoreApplication::processEvents();};
    auto center=[](QQuickItem *item){return item->mapToScene(QPointF(item->width()/2,item->height()/2));};
    auto click=[&](QQuickItem *item){if(!check(item && item->window(),"Missing public input target"))return false;clickPoint(item->window(),center(item));return true;};
    auto input=[](QQuickItem *item){return item ? item->property("inputItem").value<QQuickItem*>():nullptr;};
    QQuickWindow *sourceWindow=nullptr;
    QQuickItem *sourceFixture=nullptr;
    auto releaseSource=[&](){
        // This replay stays inside a timer callback and nested frame waits.
        // QML destroy() defers deletion until the outer event loop resumes;
        // retaining every trace window also retains its OpenGL renderer.
        const auto previous=sourceWindow;sourceWindow=nullptr;sourceFixture=nullptr;
        window->setProperty("sourceWindow",QVariant::fromValue<QObject*>(nullptr));
        if(previous){previous->close();delete previous;}
    };
    auto openSource=[&](const QJsonObject &configuration){
        releaseSource();
        frameContext="source "+configuration.value("fixture").toString()+" "+configuration.value("content").toString();
        if(!check(QMetaObject::invokeMethod(window,"openSourceWindow",Q_ARG(QVariant,QVariant(configuration.toVariantMap()))),"Source workflow creation failed"))return false;
        sourceWindow=qobject_cast<QQuickWindow*>(variant(window->property("sourceWindow")).value<QObject*>());
        sourceFixture=sourceWindow ? sourceWindow->property("fixture").value<QQuickItem*>():nullptr;
        peakSourceWindows=qMax(peakSourceWindows,int(QGuiApplication::allWindows().size()));
        return check(sourceWindow && sourceFixture,"Source workflow public objects missing") && frame(sourceWindow);
    };
    auto configureSource=[&](const QJsonObject &configuration){
        return check(QMetaObject::invokeMethod(sourceWindow,"configure",Q_ARG(QVariant,QVariant(configuration.toVariantMap()))),"Source producer update failed") && frame(sourceWindow);
    };
    QJsonArray traceResults;
    for(const auto &value:witnesses.value("traces").toArray()) {
        const auto trace=value.toObject();if(trace.value("presentation").toString()!="embedded")continue;
        if(!openSource(trace.value("initialConfiguration").toObject()))return;
        QJsonArray observations;QPointF pressed;
        for(const auto &entry:trace.value("events").toArray()) {
            const auto event=entry.toObject(),expected=event.value("state").toObject();const auto action=event.value("action").toString();
            const auto configuration=expected.value("configuration").toObject();
            if(configuration!=QJsonObject::fromVariantMap(variant(sourceWindow->property("model")).toMap()) && !configureSource(configuration))return;
            if(sourceFixture->property("mounted").toBool()!=expected.value("mounted").toBool()) {
                sourceFixture->setProperty("mounted",expected.value("mounted").toBool());if(!frame(sourceWindow))return;
            }
            if(action=="producer-text")sourceFixture->setProperty("edition",expected.value("text").toString());
            const auto control=sourceWindow->property("control").value<QQuickItem*>();
            const auto counter=findVisualItem(sourceFixture,"modalContent-counter");
            if(action.startsWith("increment") || action=="disabled-counter" || action=="enabled-counter") {if(!click(input(counter)))return;}
            else if(action=="embedded-close") {if(!click(control ? control->property("closeInput").value<QQuickItem*>():nullptr))return;}
            else if(action=="click-title") {if(!click(findVisualItem(sourceFixture,"bleeckerModalTitle")))return;}
            else if(action=="click-outside")clickPoint(sourceWindow,QPointF(2,sourceWindow->height()-2));
            else if(action=="escape")QTest::keyClick(sourceWindow,Qt::Key_Escape);
            else if(action=="down") {const auto target=input(counter);if(!check(target,"Counter press target missing"))return;pressed=center(target);send(sourceWindow,pressed,QEvent::MouseButtonPress);}
            else if(action=="up")send(sourceWindow,pressed,QEvent::MouseButtonRelease);
            else if(action=="hold-or-update")QTest::qWait(trace.value("id").toString()=="during-down-hold" ? 1100:5);
            else if(!check(QStringList{"initial","producer-update","producer-text","producer-layout","remove-content","restore-content","unmount-modal","remount-modal"}.contains(action),"Unmapped native event "+action))return;
            QCoreApplication::processEvents();
            const QJsonObject actual{{"calls",array(sourceFixture,"calls")},{"appears",sourceFixture->property("appears").toInt()},
                {"mountValues",array(sourceFixture,"mountValues")},{"text",sourceFixture->property("edition").toString()},
                {"mounted",sourceFixture->property("mounted").toBool()},{"windowVisible",sourceWindow->isVisible()}};
            for(const auto &key:QStringList{"calls","appears","mountValues","text","mounted","windowVisible"})
                if(!check(actual.value(key)==expected.value(key),trace.value("id").toString()+" "+action+" "+key+" mismatch"))return;
            ++snapshots;observations.append(QJsonObject{{"action",action},{"actual",actual},
                {"qtDestroyed",sourceFixture->property("disappears").toInt()},{"nativeDisappearObservation",expected.value("disappears")}});
        }
        traceResults.append(QJsonObject{{"id",trace.value("id")},{"events",observations}});sourceWindow->close();
    }
    const auto retained=witnesses.value("reopening").toArray().first().toObject();
    const QJsonObject defaultConfiguration{{"fixture","retained-window"},{"title","Edit edition"},{"modalWidth",480},
        {"outerOffer",QJsonValue(QJsonValue::Null)},{"content","counter"},{"disabled",false},{"rtl",false},
        {"parentFont",0},{"parentRed",false},{"width",960},{"height",900}};
    if(!openSource(defaultConfiguration))return;
    QJsonArray retainedResults;
    for(const auto &entry:retained.value("events").toArray()) {
        const auto event=entry.toObject(),expected=event.value("state").toObject();const auto action=event.value("action").toString();
        if(action.startsWith("increment")){if(!click(input(findVisualItem(sourceFixture,"modalContent-counter"))))return;}
        else if(action.startsWith("close")){const auto control=sourceWindow->property("control").value<QQuickItem*>();if(!click(control->property("closeInput").value<QQuickItem*>()))return;}
        else if(action=="reopen"){sourceWindow->show();if(!frame(sourceWindow))return;}
        else if(!check(action=="initial","Unmapped retained event "+action))return;
        const QJsonObject actual{{"calls",array(sourceFixture,"calls")},{"appears",sourceFixture->property("appears").toInt()},
            {"mountValues",array(sourceFixture,"mountValues")},{"windowVisible",sourceWindow->isVisible()}};
        for(const auto &key:QStringList{"calls","appears","mountValues","windowVisible"})
            if(!check(actual.value(key)==expected.value(key),"Retained "+action+" "+key))return;
        ++snapshots;retainedResults.append(QJsonObject{{"action",action},{"actual",actual}});
    }
    traceResults.append(QJsonObject{{"id","retained-window"},{"events",retainedResults}});
    for(const auto &groupValue:witnesses.value("groups").toArray()) {
        const auto group=groupValue.toObject(),configuration=group.value("configuration").toObject();
        if(!openSource(configuration))return;
        for(const auto &queryValue:witnesses.value("queries").toArray()) {
            const auto query=queryValue.toObject();if(query.value("fixture")!=configuration.value("fixture"))continue;
            if(!sourceWindow->isVisible()){sourceWindow->show();if(!frame(sourceWindow))return;}
            const auto before=array(sourceFixture,"calls").size();const auto point=query.value("point").toObject();
            clickPoint(sourceWindow,QPointF(point.value("x").toDouble(),point.value("y").toDouble()));
            if(!check(sourceWindow->isVisible()==query.value("windowVisible").toBool()
                && array(sourceFixture,"calls").size()-before==query.value("calls").toArray().size(),"Clipped input "+query.value("fixture").toString()))return;
            ++clippingQueries;
        }
        sourceWindow->close();
    }
    if(!setTextScale(textScale))return;
    auto hitConfiguration=defaultConfiguration;hitConfiguration.insert("content","rectangle");
    for(const auto &profileValue:witnesses.value("hitProfiles").toArray()) {
        const auto profile=profileValue.toObject();
        if(profile.value("dpr").toDouble()!=window->devicePixelRatio() || profile.value("textScale").toDouble()!=textScale)continue;
        if(!openSource(hitConfiguration))return;
        const auto bounds=profile.value("closeFrame").toObject();
        const QPointF origin(bounds.value("x").toDouble()+bounds.value("width").toDouble()/2,
                             bounds.value("y").toDouble()+bounds.value("height").toDouble()/2);
        for(const auto &sampleValue:profile.value("samples").toArray()) {
            const auto sample=sampleValue.toObject();if(!sourceWindow->isVisible()){sourceWindow->show();if(!frame(sourceWindow))return;}
            clickPoint(sourceWindow,origin+QPointF(sample.value("x").toDouble(),sample.value("y").toDouble()));
            if(!check(!sourceWindow->isVisible()==sample.value("activated").toBool(),
                QStringLiteral("Precise Close symbol input at %1,%2; expected activation %3, observed %4")
                    .arg(sample.value("x").toDouble(),0,'g',17).arg(sample.value("y").toDouble(),0,'g',17)
                    .arg(sample.value("activated").toBool()).arg(!sourceWindow->isVisible())))return;
            ++glyphQueries;
        }
        sourceWindow->close();
    }
    if(!check(clippingQueries==170 && glyphQueries==142,"Independent input witness count"))return;
    releaseSource();
    if(!check(peakSourceWindows<=3,"Replay retained earlier source windows"))return;
    if(!setTextScale(1))return;
    const auto dialog=window->property("presentedDialog").value<QObject*>();
    if(!check(dialog,"Presentation owner missing"))return;
    auto modal=[&](){return dialog->property("modalItem").value<QQuickItem*>();};
    auto popup=[&](){return qobject_cast<QQuickWindow*>(dialog->property("presentationWindow").value<QObject*>());};
    auto closeSheet=[&](){
        if(dialog->property("visible").toBool())QMetaObject::invokeMethod(dialog,"close");
        return check(QTest::qWaitFor([&]{return !dialog->property("visible").toBool() && !modal();},5000),"Presentation did not unload caller content");
    };
    auto resetSheet=[&](bool disabled){
        if(!closeSheet())return false;
        window->setProperty("sheetCalls",QVariantList{});window->setProperty("sheetMountValues",QVariantList{});
        window->setProperty("sheetAppears",0);window->setProperty("sheetDestroyed",0);window->setProperty("sheetDismissals",0);
        window->setProperty("sheetDisabled",disabled);window->setProperty("edition","Draft edition");return true;
    };
    auto openSheet=[&](const QString &mode){
        frameContext="sheet "+mode;
        if(!parentFocus("before-sheet-"+mode))return false;
        if(!frame(window))return false;
        if(!check(QMetaObject::invokeMethod(window,"openSheet",Q_ARG(QVariant,QVariant(mode))),"Presentation open failed"))return false;
        if(!check(QTest::qWaitFor([&]{return modal() && popup() && popup()->isVisible();},5000),"Separate presentation window missing"))return false;
        if(!check(popup()!=window && dialog->property("popupType").toInt()==1,"Presentation reused parent window") || !frame(popup()))return false;
        if(!check(QTest::qWaitFor([&]{return QGuiApplication::focusWindow()==popup() && popup()->contentItem()->hasActiveFocus();},5000),"Presented sheet did not gain keyboard focus"))return false;
        focusTransitions.append(QJsonObject{{"phase","sheet-focus-negative-control"},{"parentChainActive",window->isActive()},
            {"parentKeyboardReady",parentKeyboardReady()},{"sheetIsFocusWindow",QGuiApplication::focusWindow()==popup()}});
        return check(!parentKeyboardReady(),"Transient sheet focus satisfied parent keyboard readiness");
    };
    auto sheetState=[&](){return QJsonObject{{"calls",array(window,"sheetCalls")},{"appears",window->property("sheetAppears").toInt()},
        {"mountValues",array(window,"sheetMountValues")},{"parentVisible",window->isVisible()},
        {"presented",dialog->property("visible").toBool()},{"sheetCount",dialog->property("visible").toBool() ? 1:0},
        {"sheetDismissCount",window->property("sheetDismissals").toInt()}};};
    for(const auto &traceValue:witnesses.value("traces").toArray()) {
        const auto trace=traceValue.toObject();if(trace.value("presentation").toString()!="SwiftUI.sheet")continue;
        const auto id=trace.value("id").toString();
        if(!resetSheet(trace.value("initialConfiguration").toObject().value("disabled").toBool()) || !openSheet("counter"))return;
        QJsonArray observations;
        for(const auto &eventValue:trace.value("events").toArray()) {
            const auto event=eventValue.toObject();const auto action=event.value("action").toString();
            if(action=="close-click"){if(!click(modal()->property("closeInput").value<QQuickItem*>()))return;}
            else if(action=="escape")QTest::keyClick(popup(),Qt::Key_Escape);
            else if(action=="click-parent")clickPoint(window,QPointF(2,window->height()-2));
            else if(!check(action=="initial","Unmapped sheet event "+action))return;
            QCoreApplication::processEvents();const auto actual=sheetState(),expected=event.value("state").toObject();
            for(const auto &key:QStringList{"calls","appears","mountValues","parentVisible","presented","sheetCount","sheetDismissCount"})
                if(!check(actual.value(key)==expected.value(key),id+" "+action+" "+key))return;
            ++snapshots;observations.append(QJsonObject{{"action",action},{"actual",actual}});
        }
        traceResults.append(QJsonObject{{"id",id},{"events",observations}});
    }
    for(const auto &traceValue:witnesses.value("reopening").toArray()) {
        const auto trace=traceValue.toObject();const auto id=trace.value("id").toString();if(id=="retained-window")continue;
        const auto mode=id=="sheet-counter" ? QStringLiteral("counter"):QStringLiteral("editor");
        if(!resetSheet(false))return;QJsonArray observations;
        for(const auto &eventValue:trace.value("events").toArray()) {
            const auto event=eventValue.toObject(),expected=event.value("state").toObject();const auto action=event.value("action").toString();
            if(action=="initial" || action.startsWith("reopen")){if(!openSheet(mode))return;}
            else if(action.startsWith("update")){
                if(mode=="counter"){if(!click(input(findVisualItem(modal(),"modalSheetCounter"))))return;}
                else {window->setProperty("edition",expected.value("text").toString());if(!frame(popup()))return;}
            }else if(action.startsWith("close")){if(!click(modal()->property("closeInput").value<QQuickItem*>()))return;}
            else if(!check(false,"Unmapped reopening event "+action))return;
            QCoreApplication::processEvents();auto actual=sheetState();actual.insert("text",window->property("edition").toString());
            for(const auto &key:QStringList{"calls","appears","mountValues","parentVisible","presented","sheetCount","sheetDismissCount","text"})
                if(!check(actual.value(key)==expected.value(key),id+" "+action+" "+key))return;
            if(mode=="editor" && dialog->property("visible").toBool()) {
                const auto editor=findVisualItem(modal(),"modalSheetEditor");
                if(!check(editor && editor->property("text").toString()==expected.value("text").toString(),"Controlled editor did not receive producer binding"))return;
            }
            ++snapshots;observations.append(QJsonObject{{"action",action},{"actual",actual},
                {"qtDestroyed",window->property("sheetDestroyed").toInt()},{"nativeDisappearObservation",expected.value("disappears")}});
        }
        traceResults.append(QJsonObject{{"id",id},{"events",observations}});
    }
    if(!check(snapshots==80,"Native state snapshot count") || !closeSheet())return;
    if(!setTextScale(textScale) || !frame(window))return;
    auto openEditorFromGallery=[&](){
        frameContext="gallery editor";
        if(!parentFocus("before-gallery-editor"))return false;
        if(!frame(window) || !click(input(findVisualItem(window->contentItem(),"modalOpenEditor"))))return false;
        if(!check(QTest::qWaitFor([&]{return modal() && popup() && popup()->isVisible();},5000),"Gallery editor action did not present content"))return false;
        return frame(popup());
    };
    if(!openEditorFromGallery())return;
    auto editor=findVisualItem(modal(),"modalSheetEditor");
    if(!check(editor,"Presented editor missing"))return;
    editor->forceActiveFocus(Qt::OtherFocusReason);
    if(!check(editor->hasActiveFocus(),"Presented editor keyboard focus"))return;
    QTest::keyClick(popup(),Qt::Key_A,Qt::ControlModifier);QTest::keyClick(popup(),Qt::Key_Q);
    if(!check(editor->property("text").toString()=="q" && window->property("edition").toString()=="q","Typed text did not cross the caller binding"))return;
    const auto editorAx=QAccessible::queryAccessibleInterface(editor);
    if(!check(editorAx && editorAx->role()==QAccessible::EditableText && editorAx->text(QAccessible::Name)=="Edition name","Presented Qt editor accessibility"))return;
    if(!click(modal()->property("closeInput").value<QQuickItem*>()) || !closeSheet() || !openEditorFromGallery())return;
    editor=findVisualItem(modal(),"modalSheetEditor");
    if(!check(editor && editor->property("text").toString()=="q" && window->property("edition").toString()=="q","Typed caller binding did not survive reopening") || !closeSheet())return;
    const auto fixture=window->property("primaryFixture").value<QQuickItem*>(),control=window->property("primaryControl").value<QQuickItem*>();
    const auto close=control ? control->property("closeInput").value<QQuickItem*>():nullptr;
    const auto counter=fixture ? input(findVisualItem(fixture,"modalContent-counter")):nullptr;
    if(!check(close && counter,"Gallery input targets missing"))return;
    if(!parentFocus("after-sheet-close"))return;
    if(!frame(window))return;
    if(!parentFocus("before-parent-traversal"))return;
    close->forceActiveFocus(Qt::TabFocusReason);
    if(!check(close->hasActiveFocus() && counter->isVisible() && counter->isEnabled(),"Parent Close focus and caller traversal availability"))return;
    QTest::keyClick(window,Qt::Key_Tab);
    if(!check(counter->hasActiveFocus(),QStringLiteral("Tab from Close to caller content; active item %1, parent %2")
        .arg(window->activeFocusItem() ? QString::fromUtf8(window->activeFocusItem()->metaObject()->className()):"none")
        .arg(window->activeFocusItem() && window->activeFocusItem()->parentItem() ? window->activeFocusItem()->parentItem()->objectName():"none")))return;
    QTest::keyClick(window,Qt::Key_Backtab);if(!check(close->hasActiveFocus(),"Backtab from caller content to Close"))return;
    const auto title=findVisualItem(control,"bleeckerModalTitle");
    for(const auto &pair:QList<QPair<QQuickItem*,QAccessible::Role>>{{title,QAccessible::StaticText},{close,QAccessible::Button},{counter,QAccessible::Button}}) {
        const auto ax=pair.first ? QAccessible::queryAccessibleInterface(pair.first):nullptr;
        if(!check(ax && ax->role()==pair.second && !ax->text(QAccessible::Name).isEmpty(),"Qt title/Close/caller accessibility"))return;
    }
    if(!resetSheet(false) || !openSheet("counter"))return;
    if(parser.isSet("evidence")) {
        const auto path=parser.value("evidence");
        if(!check(window->grabWindow().save(path+".png") && popup()->grabWindow().save(path+"-popup.png"),"Cannot save original parent/presentation pixels"))return;
        const QJsonObject metadata{{"accepted",false},{"fixture","modal"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},
            {"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},{"textScale",textScale},
            {"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"appearance",parser.isSet("dark") ? "dark":"light"},
            {"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},{"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},
            {"windowCaptureMethod","QQuickWindow::grabWindow; parent and popup separately; full session captured separately"},
            {"focusTransitions",focusTransitions},{"producerFramesAwaited",frames},{"modalChecks","passed"},{"callerStateChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},
            {"qtEditorChecks","passed"},{"qtEditedAndReopenedValue","q"},{"nativeTypingAcceptance","pending"},
            {"nativeTraces",traceResults},{"nativeSnapshots",snapshots},{"nativeReplayTextScale",1},{"clippingQueries",clippingQueries},{"glyphQueries",glyphQueries},
            {"peakSourceWindows",peakSourceWindows},{"sourceWindowCleanup","Immediate deletion between traces; retained-window lifecycle is preserved within its own trace"},
            {"separatePresentationWindow",popup()!=window},{"popupWidth",popup()->width()},{"popupHeight",popup()->height()},
            {"lifecycleScope","Qt destruction and native onDisappear retained separately; hosting-window dismissal uses caller presentation callback"},
            {"inputMethod","Fractional Qt synthetic mouse/key events; inactive native Escape/outside guards do not establish active native keyboard policy; physical input, IME and readers pending"}};
        QFile output(path+".json");if(!check(output.open(QIODevice::WriteOnly),"Cannot save metadata"))return;output.write(QJsonDocument(metadata).toJson());output.close();
        auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path]{if(QFile::exists(path+".captured"))app.exit(0);});
        timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(254);});
        qInfo("Installed Modal: 80 native states, 170 clipping and 142 glyph queries plus Qt focus/accessibility passed; awaiting session capture");return;
    }
    qInfo("Installed Modal: 80 native states, 170 clipping and 142 glyph queries plus Qt focus/accessibility passed");app.quit();
}

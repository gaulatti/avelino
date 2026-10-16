#pragma once
#include <QInputMethodEvent>
#include <QRawFont>

static void runOTPConsumer(QQuickWindow *window,QGuiApplication &app,
                           const QCommandLineParser &parser,double textScale) {
    auto check=[&app](bool ok,const QString &message){if(!ok){qCritical("Installed OTP: %s",qPrintable(message));app.exit(246);}return ok;};
    const auto otp=findVisualItem(window->contentItem(),"consumerOTP"),outside=findVisualItem(window->contentItem(),"otpOutsideField");
    const auto editor=otp ? otp->property("editor").value<QQuickItem*>():nullptr;
    if(!check(otp && outside && editor,"Missing public OTP and owned editor"))return;
    QFile file(":/avelino/fixtures/native-otp-witnesses.json");
    if(!check(file.open(QIODevice::ReadOnly),"Native witnesses missing in independent package"))return;
    const auto witnesses=QJsonDocument::fromJson(file.readAll()).object();
    const auto traces=witnesses.value("traces").toArray();
    if(!check(traces.size()==19 && witnesses.value("reference").toString()=="fe8a1d462fbd793d883fb92086a16aa2947e32c9","Native witness coverage"))return;
    auto invoke=[&check,window](const char *method,const QVariant &value){return check(QMetaObject::invokeMethod(window,method,Q_ARG(QVariant,value)),QString("Owner method ")+method);};
    auto input=[editor](const QString &text,bool marked){if(!marked)QMetaObject::invokeMethod(editor,"selectAll");QInputMethodEvent event(marked ? text:QString(),{});if(!marked)event.setCommitString(text);QCoreApplication::sendEvent(editor,&event);};
    auto variant=[](QVariant value){return value.metaType()==QMetaType::fromType<QJSValue>() ? value.value<QJSValue>().toVariant():value;};
    QJsonArray results;int snapshots=0,callbackComparable=0,callbackMatches=0,selectionComparable=0,selectionMatches=0;
    for(const auto &value:traces) {
        const auto trace=value.toObject();const bool observed=trace.value("bindingMode").toString()=="functional-observed",deferred=trace.value("deferredOwner").toBool();
        outside->forceActiveFocus();
        window->setProperty("requests",QVariantList{});window->setProperty("pendingWrites",QVariantList{});
        const QVariantMap model{{"code",trace.value("initialCode").toString()},{"length",trace.value("initialLength").toInt()},
            {"disabled",trace.value("disabled").toBool()},{"observeOnly",trace.value("observeOnly").toBool()},
            {"publishesWrites",observed},{"deferredOwner",deferred}};
        if(!check(window->setProperty("model",model),"Cannot install caller-owned model"))return;
        QTest::qWait(2);QJsonArray events;
        for(const auto &entry:trace.value("events").toArray()) {
            const auto event=entry.toObject(),expected=event.value("state").toObject();const auto action=event.value("action").toString();
            if(action=="focus")editor->forceActiveFocus(Qt::OtherFocusReason);
            else if(action=="select-all")QMetaObject::invokeMethod(editor,"selectAll");
            else if(action=="insert-mixed")input(QString::fromUtf8("a1b٢Ⅳ1́2"),false);
            else if(action=="insert-keycap")input(QString::fromUtf8("1️⃣٢Ⅳ³一"),false);
            else if(action=="commit-mixed")input(QString::fromUtf8("a𝟙1️⃣一b٢"),false);
            else if(action=="insert-40001")input(QString(40000,'a')+'1',false);
            else if(action=="delete-backward")QTest::keyClick(window,Qt::Key_Backspace);
            else if(action=="external-unfiltered"){if(!invoke("externalCode",QString("X987654321")))return;}
            else if(action=="external-length-two" || action=="length-two"){if(!invoke("externalLength",2))return;}
            else if(action=="return-command")QTest::keyClick(window,Qt::Key_Return);
            else if(action=="blur")outside->forceActiveFocus();
            else if(action=="mark-one"){QMetaObject::invokeMethod(editor,"selectAll");input(QString::fromUtf8("一"),true);}
            else if(action=="mark-two")input(QString::fromUtf8("一二"),true);
            else if(action=="unmark"){QInputMethodEvent unmark;unmark.setCommitString(QString::fromUtf8("一二"));QCoreApplication::sendEvent(editor,&unmark);}
            else if(action=="settled" || action.endsWith("-settled"))QTest::qWait(20);
            else if(!check(action=="initial","Unmapped native action "+action))return;
            if(action=="focus" && otp->isEnabled() && !check(editor->hasActiveFocus(),"Editor did not receive focus"))return;
            if(action=="blur" && !check(!editor->hasActiveFocus(),"Editor retained focus after blur"))return;
            const bool flush=deferred && (action=="settled" || action.endsWith("-settled") || observed && QStringList{"focus","delete-backward","insert-keycap","return-command","blur"}.contains(action));
            if(flush && !check(QMetaObject::invokeMethod(window,"flushWrites"),"Owner queue acknowledgement failed"))return;
            const auto requests=QJsonArray::fromVariantList(variant(window->property("requests")).toList());
            const QJsonObject actual{{"code",otp->property("code").toString()},{"fieldValue",editor->property("displayText").toString()},
                {"hasMarkedText",editor->property("inputMethodComposing").toBool()},{"requests",requests}};
            if(!check(actual.value("code")==expected.value("code") && actual.value("fieldValue")==expected.value("fieldValue")
                && (!expected.contains("hasMarkedText") || actual.value("hasMarkedText")==expected.value("hasMarkedText")),
                trace.value("fixture").toString()+" "+action+" native model/editor mismatch"))return;
            ++snapshots;
            const bool compareCallbacks=trace.value("bindingMode").toString()!="projected-state";
            if(compareCallbacks){++callbackComparable;callbackMatches+=requests==expected.value("requests").toArray();}
            const auto selection=expected.value(expected.contains("editorSelection") ? "editorSelection":"selection").toObject();
            bool selectionMatch=false;
            if(!selection.isEmpty()){++selectionComparable;selectionMatch=editor->property("selectionStart").toInt()==selection.value("location").toInt()
                && editor->property("selectionEnd").toInt()-editor->property("selectionStart").toInt()==selection.value("length").toInt();selectionMatches+=selectionMatch;}
            events.append(QJsonObject{{"action",action},{"actual",actual},{"modelAndEditorMatch",true},{"ownerQueueFlushed",flush},
                {"callbacksComparable",compareCallbacks},{"callbacksMatch",compareCallbacks && requests==expected.value("requests").toArray()},
                {"selectionComparable",!selection.isEmpty()},{"selectionMatch",selectionMatch}});
        }
        results.append(QJsonObject{{"fixture",trace.value("fixture")},{"sourceFile",trace.value("sourceFile")},{"bindingMode",trace.value("bindingMode")},{"events",events}});
    }
    outside->forceActiveFocus();
    const auto partial=findVisualItem(window->contentItem(),"otpPartial");
    const auto partialEditor=partial ? partial->property("editor").value<QQuickItem*>():nullptr;
    if(!check(partialEditor,"Missing following keyboard input"))return;
    QTest::keyClick(window,Qt::Key_Tab);if(!check(editor->hasActiveFocus(),"Tab into composite editor"))return;
    QTest::keyClick(window,Qt::Key_Tab);if(!check(partialEditor->hasActiveFocus(),"Tab out of composite editor"))return;
    QTest::keyClick(window,Qt::Key_Backtab);if(!check(editor->hasActiveFocus(),"Backtab into composite editor"))return;
    QTest::keyClick(window,Qt::Key_Backtab);if(!check(outside->hasActiveFocus(),"Backtab out of composite editor"))return;
    otp->forceActiveFocus();if(!check(editor->hasActiveFocus(),"Programmatic focus forwards to native editor"))return;
    outside->forceActiveFocus();
    if(!check(snapshots==200,"Native snapshot count"))return;
    const auto ax=QAccessible::queryAccessibleInterface(editor);
    if(!check(ax && ax->role()==QAccessible::EditableText && ax->text(QAccessible::Name)=="Verification code","Qt accessible editable label"))return;
    const auto disabled=findVisualItem(window->contentItem(),"otpDisabled");
    if(!check(disabled && !disabled->isEnabled(),"Disabled input state"))return;
    const auto font=editor->property("font").value<QFont>();
    if(!check(qAbs(editor->implicitHeight()-40*textScale)<.001 && qAbs(QRawFont::fromFont(font).pixelSize()-20)<.001,"Fixed monospace font and scaled minimum height"))return;
    if(parser.isSet("evidence")) {
        const auto path=parser.value("evidence");
        if(!check(window->grabWindow().save(path+".png"),"Cannot save original window pixels"))return;
        QJsonObject meta{{"accepted",false},{"fixture","otp-input"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},
            {"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},{"textScale",textScale},
            {"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"appearance",parser.isSet("dark") ? "dark":"light"},
            {"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},{"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},
            {"windowCaptureMethod","QQuickWindow::grabWindow; full session captured separately"},
            {"otpChecks","passed"},{"callerBindingChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},
            {"nativeModelEditorSnapshots",snapshots},{"callbackComparable",callbackComparable},{"callbackMatches",callbackMatches},
            {"selectionComparable",selectionComparable},{"selectionMatches",selectionMatches},{"nativeTraces",results},
            {"ownerTimingScope","Explicit acknowledgement schedule replays queued actual requests; native 50/100ms delayed-owner timing equivalence pending"},
            {"nativeLifecycleAcceptance","pending; native callback and selection comparisons are retained"},
            {"inputMethod","QInputMethodEvent commits/preedit and QtTest keys, no physical keyboard/IME or reader acceptance"}};
        QFile output(path+".json");if(!check(output.open(QIODevice::WriteOnly),"Cannot save metadata"))return;output.write(QJsonDocument(meta).toJson());output.close();
        auto timer=new QTimer(&app);
        QObject::connect(timer,&QTimer::timeout,&app,[&app,path]{if(QFile::exists(path+".captured"))app.exit(0);});
        timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(252);});
        qInfo("Installed OTP: 19 traces / 200 native snapshots passed; callback %d/%d, selection %d/%d; awaiting full session capture",callbackMatches,callbackComparable,selectionMatches,selectionComparable);
        return;
    }
    qInfo("Installed OTP: 19 traces / 200 native model-editor snapshots passed; callback %d/%d, selection %d/%d (strict lifecycle acceptance pending)",callbackMatches,callbackComparable,selectionMatches,selectionComparable);
    app.quit();
}

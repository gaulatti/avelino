#include <QtQuickTest/quicktest.h>
#include <QQmlEngine>
#include <QQmlContext>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QLocale>
#include <QCoreApplication>
#include <QEvent>
#include <QInputMethodEvent>
#include <QQuickItem>
#include <QQuickWindow>
#include <QMouseEvent>
#include <QTemporaryDir>
#include <QDir>
#include <QAccessible>

class FixtureSetup : public QObject {
    Q_OBJECT
public slots:
    void setAccessibilityActive(bool active) {QAccessible::setActive(active);}
    bool accessibleAvailable(QQuickItem *item) {return item && QAccessible::queryAccessibleInterface(item);}
    QString accessibleDescription(QQuickItem *item) {
        const auto interface=QAccessible::queryAccessibleInterface(item);
        if(!interface)qFatal("Tooltip reader check requires an actual Qt accessibility interface");
        return interface->text(QAccessible::Description);
    }
    QString accessibleName(QQuickItem *item) {
        const auto interface=QAccessible::queryAccessibleInterface(item);
        if(!interface)qFatal("Tooltip reader check requires an actual Qt accessibility interface");
        return interface->text(QAccessible::Name);
    }
    QString accessibleValue(QQuickItem *item) {
        const auto interface=QAccessible::queryAccessibleInterface(item);
        if(!interface)qFatal("App-tab check requires an actual Qt accessibility interface");
        return interface->text(QAccessible::Value);
    }
    bool accessibleSelected(QQuickItem *item) {
        const auto interface=QAccessible::queryAccessibleInterface(item);
        if(!interface)qFatal("App-tab check requires an actual Qt accessibility interface");
        return interface->state().selected;
    }
    void accessiblePress(QQuickItem *item) {
        const auto interface=QAccessible::queryAccessibleInterface(item);
        if(!interface ||!interface->actionInterface())qFatal("App-tab check requires an actual Qt action interface");
        interface->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
    }
    void clickModalPoint(QQuickItem *item,qreal x,qreal y) {
        if(!item || !item->window() || !item->window()->isVisible())qFatal("Modal pointer test requires a visible owned window");
        auto window=item->window();const auto point=item->mapToScene(QPointF(x,y));
        const auto global=QPointF(window->position())+point;
        // Preserve the source's fractional synthetic coordinates. QtTest's
        // ordinary mouse helper rounds window positions to integer points.
        QMouseEvent press(QEvent::MouseButtonPress,point,point,global,Qt::LeftButton,Qt::LeftButton,Qt::NoModifier);
        QCoreApplication::sendEvent(window,&press);
        QMouseEvent release(QEvent::MouseButtonRelease,point,point,global,Qt::LeftButton,Qt::NoButton,Qt::NoModifier);
        QCoreApplication::sendEvent(window,&release);
    }
    QString saveOTPTraceReport(const QVariantList &traces) {
        const auto root=QStringLiteral(OTP_TRACE_OUTPUT_DIRECTORY);
        if(!QDir().mkpath(root))qFatal("Cannot create OTP trace output root");
        QTemporaryDir attempt(root+"/attempt-XXXXXX");
        if(!attempt.isValid())qFatal("Cannot create fresh OTP trace output directory");
        attempt.setAutoRemove(false);
        const auto path=attempt.path()+"/traces.json";
        QFile file(path);if(!file.open(QIODevice::WriteOnly))qFatal("Cannot write OTP trace report");
        const QJsonObject report{{"accepted",false},{"qt",qVersion()},
            {"scope","QInputMethodEvent and QtTest replay with explicit queued-owner acknowledgement order; delayed-owner clock, source callback/selection, physical input and reader acceptance pending"},
            {"traces",QJsonArray::fromVariantList(traces)}};
        file.write(QJsonDocument(report).toJson());return path;
    }
    void commitText(QQuickItem *item,const QString &text) {
        QInputMethodEvent event;event.setCommitString(text);QCoreApplication::sendEvent(item,&event);
    }
    void preeditText(QQuickItem *item,const QString &text) {
        QInputMethodEvent event(text,{});QCoreApplication::sendEvent(item,&event);
    }
    void setProcessLocale(const QString &name) {QLocale::setDefault(QLocale(name));QEvent event(QEvent::LocaleChange);QCoreApplication::sendEvent(qApp,&event);}
    void qmlEngineAvailable(QQmlEngine *engine) {
        engine->rootContext()->setContextProperty("fixtureSetup",this);
        QFile media(QStringLiteral(NATIVE_MEDIA_LIBRARY_FILE));
        if(!media.open(QIODevice::ReadOnly))qFatal("Native media library evidence missing");
        const auto mediaData=QJsonDocument::fromJson(media.readAll()).object();
        if(mediaData.value("reference").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9"
            ||mediaData.value("histories").toArray().size()!=48)qFatal("Native media library histories incomplete");
        engine->rootContext()->setContextProperty("nativeMediaLibraryHistories",mediaData.value("histories").toArray().toVariantList());
        QFile surface(QStringLiteral(NATIVE_SURFACE_MODIFIER_DIRECTORY)+"/captures/captures.json");
        if(!surface.open(QIODevice::ReadOnly))qFatal("Native surface modifier evidence missing");
        const auto surfaceData=QJsonDocument::fromJson(surface.readAll()).object();
        const auto surfaceCaptures=surfaceData.value("captures").toArray();
        if(surfaceData.value("reference").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9"
            ||surfaceCaptures.size()!=416)qFatal("Native surface modifier reference incomplete");
        QJsonArray surfaceContexts;
        for(const auto &value:surfaceCaptures) {
            const auto row=value.toObject();
            if(!row.value("publicProbedIdentical").toBool()||!row.value("publicWitnessIdentical").toBool())
                qFatal("Surface geometry requires transparent public and literal-body witnesses");
            QJsonObject selected;
            for(const auto &key:QStringList{"configuration","appearance","textScale","dpr"})selected.insert(key,row.value(key));
            selected.insert("state",row.value("states").toArray().at(1));surfaceContexts.append(selected);
        }
        engine->rootContext()->setContextProperty("nativeSurfaceModifierCaptures",surfaceContexts.toVariantList());
        for(const auto &source:QList<QPair<QString,QString>>{
            {QStringLiteral(NATIVE_FONT_MODIFIER_DIRECTORY),"nativeFontModifierCaptures"},
            {QStringLiteral(NATIVE_FONT_BASELINE_DIRECTORY),"nativeFontBaselineCaptures"}}) {
            QFile file(source.first+"/captures/captures.json");
            if(!file.open(QIODevice::ReadOnly))qFatal("Native font modifier source evidence missing");
            const auto data=QJsonDocument::fromJson(file.readAll()).object();
            if(data.value("reference").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9")qFatal("Native font modifier reference invalid");
            const auto captures=data.value("captures").toArray();
            if(captures.size()!=(source.second=="nativeFontModifierCaptures" ? 864:720))qFatal("Native font modifier contexts incomplete");
            QJsonArray compact;
            for(const auto &value:captures) {
                const auto row=value.toObject();
                if(!row.value("publicProbedIdentical").toBool())qFatal("Font geometry requires a transparent public probe");
                QJsonObject selected;
                for(const auto &key:QStringList{"configuration","appearance","textScale","dpr"})selected.insert(key,row.value(key));
                selected.insert("state",row.value("states").toArray().at(1));compact.append(selected);
            }
            engine->rootContext()->setContextProperty(source.second,compact.toVariantList());
        }
        QFile buttonStyle(QStringLiteral(NATIVE_BUTTON_STYLE_DIRECTORY)+"/captures/captures.json");
        if(!buttonStyle.open(QIODevice::ReadOnly))qFatal("Native ButtonStyle evidence missing");
        const auto buttonStyleData=QJsonDocument::fromJson(buttonStyle.readAll()).object();
        if(buttonStyleData.value("reference").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9")qFatal("Native ButtonStyle reference invalid");
        engine->rootContext()->setContextProperty("nativeButtonStyleCaptures",buttonStyleData.value("captures").toArray().toVariantList());
        const auto alignmentDirectory=QStringLiteral(NATIVE_ACTIVITY_ALIGNMENT_DIRECTORY);
        QFile directions(alignmentDirectory+"/directions/text-directions.json");
        if(!directions.open(QIODevice::ReadOnly))qFatal("Native text direction evidence missing");
        const auto directionData=QJsonDocument::fromJson(directions.readAll()).object();
        if(directionData.value("reference").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9")qFatal("Native text direction reference invalid");
        engine->rootContext()->setContextProperty("nativeTextDirectionQueries",directionData.value("queries").toArray().toVariantList());
        engine->rootContext()->setContextProperty("nativeTextDirectionFresh",directionData.value("fresh").toArray().toVariantList());
        QFile alignments(alignmentDirectory+"/lines/lines.json");
        if(!alignments.open(QIODevice::ReadOnly))qFatal("Native bare text alignment evidence missing");
        const auto alignmentData=QJsonDocument::fromJson(alignments.readAll()).object();
        if(alignmentData.value("reference").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9")qFatal("Native text alignment reference invalid");
        QJsonArray bareAlignmentCases;
        for(const auto &value:alignmentData.value("rows").toArray()) {
            const auto row=value.toObject();QJsonObject bare;
            for(const auto &key:QStringList{"key","text","dpr","rtl","alignment","proposalWidth","bareRect"})bare.insert(key,row.value(key));
            bareAlignmentCases.append(bare);
        }
        engine->rootContext()->setContextProperty("nativeTextAlignmentCases",bareAlignmentCases.toVariantList());
        const auto layoutDirectory=QStringLiteral(NATIVE_ACTIVITY_LAYOUT_DIRECTORY);
        for(const auto &name:QStringList{"text/fixed-queries.json","buckets/buckets.json"}) {
            QFile file(layoutDirectory+"/"+name);if(!file.open(QIODevice::ReadOnly))qFatal("Native text layout/history evidence missing");
            const auto data=QJsonDocument::fromJson(file.readAll()).object();
            if(data.value("reference").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9")qFatal("Native text layout/history reference invalid");
            const auto key=name.startsWith("text/") ? "rows":"traces";
            const auto context=name.startsWith("text/") ? "nativeTextLayoutQueries":"nativeTextLayoutHistory";
            engine->rootContext()->setContextProperty(context,data.value(key).toArray().toVariantList());
        }
        const auto activityDirectory=QStringLiteral(NATIVE_ACTIVITY_DIRECTORY);
        QFile modal(QStringLiteral(NATIVE_MODAL_DIRECTORY)+"/captures/captures.json");
        if(!modal.open(QIODevice::ReadOnly))qFatal("Native Modal evidence missing");
        const auto modalData=QJsonDocument::fromJson(modal.readAll()).object();
        if(modalData.value("reference").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9")qFatal("Native Modal reference invalid");
        engine->rootContext()->setContextProperty("nativeModalCaptures",modalData.value("captures").toArray().toVariantList());
        QFile modalInput(QStringLiteral(NATIVE_MODAL_INPUT_DIRECTORY)+"/outputs/input.json");
        QFile modalHits(QStringLiteral(NATIVE_MODAL_INPUT_DIRECTORY)+"/outputs/hit-profiles.json");
        if(!modalInput.open(QIODevice::ReadOnly)||!modalHits.open(QIODevice::ReadOnly))qFatal("Native Modal input evidence missing");
        const auto modalInputData=QJsonDocument::fromJson(modalInput.readAll()).object();
        const auto modalHitData=QJsonDocument::fromJson(modalHits.readAll()).object();
        if(!modalInputData.value("complete").toBool() || modalInputData.value("reference").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9"
            || modalHitData.value("reference").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9")qFatal("Native Modal input reference invalid");
        // The field body's nontransparent witness is intentionally not exposed.
        engine->rootContext()->setContextProperty("nativeModalInputGroups",modalInputData.value("groups").toArray().toVariantList());
        engine->rootContext()->setContextProperty("nativeModalClippingQueries",modalInputData.value("queries").toArray().toVariantList());
        engine->rootContext()->setContextProperty("nativeModalHitProfiles",modalHitData.value("profiles").toArray().toVariantList());
        for(const auto &name:QStringList{"captures/captures.json","layout-queries.json","behavior/behavior.json"}) {
            QFile file(activityDirectory+"/"+name);if(!file.open(QIODevice::ReadOnly))qFatal("Native ActivityItem evidence missing");
            const auto data=QJsonDocument::fromJson(file.readAll()).object();
            if(data.value("reference").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9")qFatal("Native ActivityItem reference invalid");
            const auto key=name.startsWith("captures/") ? "captures":name.startsWith("layout-") ? "queries":"traces";
            const auto context=name.startsWith("captures/") ? "nativeActivityCaptures":name.startsWith("layout-") ? "nativeActivityLayout":"nativeActivityBehavior";
            engine->rootContext()->setContextProperty(context,data.value(key).toArray().toVariantList());
        }
        QJsonArray otpTraces;
        for(const auto &name:QStringList{"behavior-final/behavior.json","state-bindings/state-bindings.json","edges/edges.json"}) {
            QFile file(QStringLiteral(NATIVE_OTP_DIRECTORY)+"/"+name);
            if(!file.open(QIODevice::ReadOnly))qFatal("Native OTP editor evidence missing");
            const auto data=QJsonDocument::fromJson(file.readAll()).object();
            if(data.value("reference").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9")qFatal("Native OTP editor reference invalid");
            for(const auto &value:data.value("traces").toArray()) {
                auto trace=value.toObject();trace.insert("sourceFile",name);otpTraces.append(trace);
            }
        }
        if(otpTraces.size()!=19)qFatal("Native OTP editor coverage invalid");
        engine->rootContext()->setContextProperty("nativeOTPTraces",otpTraces.toVariantList());
        const auto radioDirectory=QStringLiteral(NATIVE_RADIO_DIRECTORY);
        for(const auto &name:QStringList{"captures/captures.json","behavior/behavior.json","native-string-identity.json"}) {
            QFile file(radioDirectory+"/"+name);if(!file.open(QIODevice::ReadOnly))qFatal("Native RadioGroup evidence missing");
            const auto data=QJsonDocument::fromJson(file.readAll()).object();
            if(data.value("reference").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9")qFatal("Native RadioGroup reference invalid");
            if(name.startsWith("captures/"))engine->rootContext()->setContextProperty("nativeRadioCaptures",data.value("captures").toArray().toVariantList());
            else if(name.startsWith("behavior/")){engine->rootContext()->setContextProperty("nativeRadioBehavior",data.value("traces").toArray().toVariantList());engine->rootContext()->setContextProperty("nativeRadioPointerPhases",data.value("pointerPhases").toArray().toVariantList());}
            else engine->rootContext()->setContextProperty("nativeRadioStringPairs",data.value("results").toArray().toVariantList());
        }
        const auto stepperDirectory=QStringLiteral(NATIVE_STEPPER_DIRECTORY);
        QFile stepperBehavior(stepperDirectory+"/behavior/behavior.json");
        if(!stepperBehavior.open(QIODevice::ReadOnly))qFatal("Native stepper behavior missing");
        const auto stepperData=QJsonDocument::fromJson(stepperBehavior.readAll()).object();
        if(stepperData.value("reference").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9" || stepperData.value("traces").toArray().size()!=25)qFatal("Native stepper behavior invalid");
        engine->rootContext()->setContextProperty("nativeStepperBehavior",stepperData.value("traces").toArray().toVariantList());
        QJsonArray stepperFormatting;
        for(const auto &locale:QStringList{"en_US","de_DE","es_CL","fr_FR","ja_JP","ar_EG","hi_IN"}) {
            QFile file(stepperDirectory+"/locale-"+locale+"/formatting.json");
            if(!file.open(QIODevice::ReadOnly))qFatal("Native stepper formatting missing");
            const auto rows=QJsonDocument::fromJson(file.readAll()).object().value("formatting").toArray();
            if(rows.size()!=18)qFatal("Native stepper formatting invalid");
            for(const auto &v:rows){auto row=v.toObject();row.insert("locale",locale);stepperFormatting.append(row);}
        }
        engine->rootContext()->setContextProperty("nativeStepperFormatting",stepperFormatting.toVariantList());
        QFile numericText(QStringLiteral(NATIVE_NUMERIC_TEXT_FILE));if(!numericText.open(QIODevice::ReadOnly))qFatal("Numeric text witnesses missing");
        const auto numericData=QJsonDocument::fromJson(numericText.readAll()).object();if(numericData.value("cases").toArray().size()!=40)qFatal("Numeric text witnesses invalid");
        engine->rootContext()->setContextProperty("nativeNumericText",numericData.value("cases").toArray().toVariantList());
        QFile metric(QStringLiteral(NATIVE_DATA_METRICS_FILE)),inputs(QStringLiteral(NATIVE_DATA_METRICS_INPUT_FILE));
        if(!metric.open(QIODevice::ReadOnly)||!inputs.open(QIODevice::ReadOnly))qFatal("Native metric source/input evidence missing");
        auto dataMetric=QJsonDocument::fromJson(metric.readAll()).object();const auto inputRows=QJsonDocument::fromJson(inputs.readAll()).object().value("fixtures").toArray();
        QHash<QString,double> widths;for(const auto &v:inputRows){auto row=v.toObject();widths.insert(row.value("fixture").toString(),row.value("proposalWidth").toDouble());}
        QJsonArray dataCases;for(const auto &v:dataMetric.value("captures").toArray()){auto row=v.toObject();if(!widths.contains(row.value("fixture").toString()))qFatal("Missing native metric width proposal");row.insert("proposalWidth",widths.value(row.value("fixture").toString()));dataCases.append(row);}
        if(dataCases.size()!=1048)qFatal("Native metric source matrix invalid");
        engine->rootContext()->setContextProperty("nativeDataMetricsCaptures",dataCases.toVariantList());
        engine->rootContext()->setContextProperty("nativeMetricFormatting",dataMetric.value("formatting").toArray().toVariantList());
        QFile sidebarBrand(QStringLiteral(NATIVE_SIDEBAR_BRAND_FILE));
        if(!sidebarBrand.open(QIODevice::ReadOnly))qFatal("Native sidebar/brand evidence missing");
        const auto sidebarData=QJsonDocument::fromJson(sidebarBrand.readAll()).object();
        if(sidebarData.value("reference").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9" || sidebarData.value("captures").toArray().size()!=416)qFatal("Native sidebar/brand evidence invalid");
        engine->rootContext()->setContextProperty("nativeSidebarBrandCaptures",sidebarData.value("captures").toArray().toVariantList());
        engine->rootContext()->setContextProperty("nativeSidebarBrandBehavior",sidebarData.value("behavior").toArray().toVariantList());
        QFile navigation(QStringLiteral(NATIVE_NAVIGATION_FILE));
        if(!navigation.open(QIODevice::ReadOnly))qFatal("Native navigation source evidence missing");
        const auto navigationData=QJsonDocument::fromJson(navigation.readAll()).object();
        if(navigationData.value("reference").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9" || navigationData.value("captures").toArray().size()!=392)qFatal("Native navigation source evidence invalid");
        engine->rootContext()->setContextProperty("nativeNavigationCaptures",navigationData.value("captures").toArray().toVariantList());
        QFile navigationText(QStringLiteral(NATIVE_NAVIGATION_TEXT_FILE));
        if(!navigationText.open(QIODevice::ReadOnly))qFatal("Native navigation text evidence missing");
        const auto navigationTextData=QJsonDocument::fromJson(navigationText.readAll()).array();
        if(navigationTextData.size()!=104)qFatal("Native navigation text evidence invalid");
        engine->rootContext()->setContextProperty("nativeNavigationText",navigationTextData.toVariantList());
        QFile proseBoundaries(QStringLiteral(NATIVE_PROSE_BOUNDARIES_FILE));
        if(!proseBoundaries.open(QIODevice::ReadOnly))qFatal("Native prose boundaries missing");
        const auto proseData=QJsonDocument::fromJson(proseBoundaries.readAll()).object();
        if(proseData.value("reference").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9" || proseData.value("cases").toArray().size()!=84)qFatal("Native prose boundaries invalid");
        engine->rootContext()->setContextProperty("nativeProseBoundaries",proseData.value("cases").toArray().toVariantList());
        QFile alertText(QStringLiteral(NATIVE_ALERT_TEXT_FILE));
        if(!alertText.open(QIODevice::ReadOnly))qFatal("Native alert text evidence missing");
        const auto alertTextData=QJsonDocument::fromJson(alertText.readAll()).object();
        if(alertTextData.value("reference").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9" || alertTextData.value("cases").toArray().size()!=96)qFatal("Native alert text evidence invalid");
        engine->rootContext()->setContextProperty("nativeAlertTextCases",alertTextData.value("cases").toArray().toVariantList());
        QFile alert(QStringLiteral(NATIVE_ALERT_FILE));
        if(!alert.open(QIODevice::ReadOnly))qFatal("Native alert evidence missing");
        const auto alertData=QJsonDocument::fromJson(alert.readAll()).object();
        if(alertData.value("reference").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9" || alertData.value("captures").toArray().size()!=256)qFatal("Native alert evidence invalid");
        QJsonArray alertCases;for(const auto &entry:alertData.value("captures").toArray())if(entry.toObject().value("api").toString()=="BleeckerAlert")alertCases.append(entry);
        engine->rootContext()->setContextProperty("nativeAlertCaptures",alertCases.toVariantList());
        engine->rootContext()->setContextProperty("nativeAlertBehavior",alertData.value("behavior").toArray().toVariantList());
        QFile file(QStringLiteral(NATIVE_GEOMETRY_FILE));
        if (!file.open(QIODevice::ReadOnly)) qFatal("Native geometry evidence is missing");
        const auto cases = QJsonDocument::fromJson(file.readAll()).object().value("cases").toArray();
        if (cases.size() != 8) qFatal("Native geometry evidence is incomplete");
        engine->rootContext()->setContextProperty("nativeGeometry", cases.toVariantList());
        QFile typography(QStringLiteral(NATIVE_TYPOGRAPHY_FILE));
        if (!typography.open(QIODevice::ReadOnly)) qFatal("Native typography evidence is missing");
        const auto data = QJsonDocument::fromJson(typography.readAll()).object();
        if (data.value("referenceRevision").toString() != "fe8a1d462fbd793d883fb92086a16aa2947e32c9")
            qFatal("Native typography reference revision differs");
        const auto fontCases = data.value("cases").toArray();
        if (fontCases.size() != 2160) qFatal("Native typography evidence is incomplete");
        engine->rootContext()->setContextProperty("nativeTypography", fontCases.toVariantList());
        QFile wrapping(QStringLiteral(NATIVE_WRAPPING_FILE));
        if (!wrapping.open(QIODevice::ReadOnly)) qFatal("Native wrapping evidence is missing");
        const auto wrapData = QJsonDocument::fromJson(wrapping.readAll()).object();
        if (wrapData.value("referenceRevision").toString() != "fe8a1d462fbd793d883fb92086a16aa2947e32c9") qFatal("Native wrapping reference revision differs");
        const auto wrapCases = wrapData.value("cases").toArray();
        if (wrapCases.size() != 120) qFatal("Native wrapping evidence is incomplete");
        engine->rootContext()->setContextProperty("nativeWrapping", wrapCases.toVariantList());
        QFile centered(QStringLiteral(NATIVE_CENTERED_TEXT_FILE));
        if (!centered.open(QIODevice::ReadOnly)) qFatal("Native centered-text evidence is missing");
        const auto centeredData = QJsonDocument::fromJson(centered.readAll()).object();
        if (centeredData.value("reference").toString() != "fe8a1d462fbd793d883fb92086a16aa2947e32c9") qFatal("Centered-text reference differs");
        const auto centeredCases = centeredData.value("centeredTextLines").toArray();
        if (centeredCases.size() != 63) qFatal("Native centered-text evidence is incomplete");
        engine->rootContext()->setContextProperty("nativeCenteredText", centeredCases.toVariantList());
        QJsonArray validPresentation;
        for (const auto &entry : centeredData.value("captures").toArray())
            if (entry.toObject().value("api").toString() != "BleeckerLoadingOverlay") validPresentation.append(entry);
        QFile hosted(QStringLiteral(NATIVE_HOSTED_LOADING_FILE));
        if (!hosted.open(QIODevice::ReadOnly)) qFatal("Hosted loading evidence is missing");
        const auto hostedData=QJsonDocument::fromJson(hosted.readAll()).object();
        if (hostedData.value("reference").toString() != "fe8a1d462fbd793d883fb92086a16aa2947e32c9") qFatal("Hosted loading reference differs");
        const auto hostedCases=hostedData.value("captures").toArray();
        if (hostedCases.size()!=32) qFatal("Hosted loading evidence is incomplete");
        for (const auto &entry : hostedCases) validPresentation.append(entry);
        engine->rootContext()->setContextProperty("nativePresentationCaptures", validPresentation.toVariantList());
        engine->rootContext()->setContextProperty("nativePresentationBehavior", centeredData.value("behavior").toArray().toVariantList());
        QFile spinner(QStringLiteral(NATIVE_SPINNER_FILE));
        if(!spinner.open(QIODevice::ReadOnly))qFatal("Native spinner evidence is missing");
        const auto spinnerData=QJsonDocument::fromJson(spinner.readAll()).object();
        if(spinnerData.value("reference").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9" || spinnerData.value("captures").toArray().size()!=186)qFatal("Native spinner evidence differs");
        engine->rootContext()->setContextProperty("nativeSpinnerContexts",spinnerData.value("captures").toArray().toVariantList());
    }
};
QUICK_TEST_MAIN_WITH_SETUP(avelino, FixtureSetup)
#include "main.moc"

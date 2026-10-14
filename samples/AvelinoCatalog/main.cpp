#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QQuickWindow>
#include <QTimer>
#include <QCommandLineParser>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QFile>
#include <QSysInfo>
#include <QFont>
#include <QRawFont>
#include <QQuickItem>
#include <QMouseEvent>
#include <QSGRendererInterface>
#include <cmath>

static QQuickItem *findVisual(QQuickItem *root, const QString &name) {
    if (root->objectName() == name) return root;
    for (auto child : root->childItems()) if (auto found = findVisual(child, name)) return found;
    return nullptr;
}

static void recordLabels(QQuickItem *root, QJsonArray &labels) {
    const auto fontProperty = root->property("font");
    if (root->isVisible() && fontProperty.isValid() && root->property("text").isValid()) {
        const auto font = fontProperty.value<QFont>();
        const auto raw = QRawFont::fromFont(font);
        const auto position = root->mapToScene(QPointF(0, 0));
        QJsonObject record{{"role", root->objectName()}, {"text", root->property("text").toString()},
            {"family", raw.familyName()}, {"style", raw.styleName()}, {"weight", int(font.weight())},
            {"requestedPointSize", font.pointSizeF()}, {"requestedPixelSize", font.pixelSize()},
            {"width", root->width()}, {"height", root->height()}, {"x", position.x()}, {"y", position.y()},
            {"sceneBaseline", root->mapToScene(QPointF(0, root->baselineOffset())).y()}};
        if (root->property("resolvedPixelSize").isValid()) {
            record.insert("requestedLogicalPixelSize",root->property("logicalPixelSize").toDouble());
            record.insert("resolvedGlyphPixelSize",root->property("resolvedPixelSize").toDouble());
            record.insert("glyphAdvance",root->property("glyphAdvance").toDouble());
        }
        labels.append(record);
    }
    for (auto child : root->childItems()) recordLabels(child, labels);
}

int main(int argc, char *argv[]) {
    QGuiApplication app(argc, argv);
    QCommandLineParser parser;
    parser.addHelpOption();
    parser.addOptions({QCommandLineOption("capture", "Save the displayed fixture to PNG and exit", "path"),
                       QCommandLineOption("dark", "Use dark reference appearance"),
                       QCommandLineOption("fixture", "Render a fixture (button, foundations, surfaces, data-display, controls, composition, selection, checkbox, secure-field, search-field, collection-filters, slider or reference-case)", "name"),
                       QCommandLineOption("case", "Isolated reference fixture identifier", "id"),
                       QCommandLineOption("case-definitions", "JSON file containing the isolated fixture definitions", "path"),
                       QCommandLineOption("variant", "Button variant", "name", "primary"),
                       QCommandLineOption("size", "Button size", "name", "md"),
                       QCommandLineOption("disabled", "Disable the fixture control"),
                       QCommandLineOption("text-scale", "Use a positive logical text scale", "factor", "1")});
    parser.process(app);
    bool validScale = false;
    const qreal textScale = parser.value("text-scale").toDouble(&validScale);
    if (!validScale || !std::isfinite(textScale) || textScale <= 0) return 5;
    const auto fixture = parser.value("fixture");
    const bool isolated = fixture == "reference-case";
    QJsonObject definition;
    if (isolated) {
        if (!parser.isSet("case") || !parser.isSet("case-definitions")) return 6;
        QFile file(parser.value("case-definitions"));
        if (!file.open(QIODevice::ReadOnly)) return 6;
        QJsonParseError error;
        const auto definitions = QJsonDocument::fromJson(file.readAll(), &error).object().value("fixtures").toArray();
        if (error.error != QJsonParseError::NoError) return 6;
        int matches = 0;
        for (const auto &value : definitions) {
            const auto entry = value.toObject();
            if (entry.value("fixture").toString() == parser.value("case")) { definition = entry; ++matches; }
        }
        if (matches != 1 || definition.value("width").toDouble() <= 0 || definition.value("height").toDouble() <= 0) return 6;
    } else if (parser.isSet("case") || parser.isSet("case-definitions")) return 6;
    QQmlApplicationEngine engine;
    engine.rootContext()->setContextProperty("captureDark", parser.isSet("dark"));
    engine.rootContext()->setContextProperty("captureVariant", parser.value("variant"));
    engine.rootContext()->setContextProperty("captureSize", parser.value("size"));
    engine.rootContext()->setContextProperty("captureDisabled", parser.isSet("disabled"));
    engine.rootContext()->setContextProperty("captureTextScale", textScale);
    engine.rootContext()->setContextProperty("captureDefinition", definition.toVariantMap());
    QObject::connect(&engine, &QQmlApplicationEngine::objectCreationFailed, &app, [] { QCoreApplication::exit(1); }, Qt::QueuedConnection);
    if (parser.isSet("fixture") && fixture != "button" && fixture != "foundations" && fixture != "surfaces" && fixture != "data-display" && fixture != "controls" && fixture != "composition" && fixture != "selection" && fixture != "checkbox" && fixture != "secure-field" && fixture != "search-field" && fixture != "collection-filters" && fixture != "slider" && !isolated) return 4;
    engine.loadFromModule("AvelinoCatalog", isolated ? "ReferenceCaseFixture" : fixture == "slider" ? "SliderFixture" : fixture == "collection-filters" ? "CollectionFiltersFixture" : fixture == "search-field" ? "SearchFieldFixture" : fixture == "secure-field" ? "SecureFieldFixture" : fixture == "checkbox" ? "CheckboxFixture" : fixture == "selection" ? "SelectionFixture" : fixture == "composition" ? "CompositionFixture" : fixture == "controls" ? "ControlsFixture" : fixture == "data-display" ? "DataDisplayFixture" : fixture == "surfaces" ? "SurfacesFixture" : fixture == "foundations" ? "FoundationsFixture"
        : fixture == "button" ? "ButtonFixture" : "Main");
    if (parser.isSet("capture")) {
        const auto path = parser.value("capture");
        if (isolated && definition.value("fixture").toString().startsWith("search-") && definition.value("variant").toString()=="cleared") {
            QTimer::singleShot(150,&app,[&engine,&app] {
                const auto window=qobject_cast<QQuickWindow *>(engine.rootObjects().value(0));
                const auto field=window ? findVisual(window->contentItem(),"referenceCaseComponent") : nullptr;
                const auto action=field ? findVisual(field,"bleeckerSearchClear") : nullptr;
                if (!action || !QMetaObject::invokeMethod(action,"click") || !field->property("text").toString().isEmpty()) { app.exit(10); return; }
                // Native proposal captures are defocused after the action.
                // Interactive consumers separately verify restored editing focus.
                field->setFocus(false);
            });
        }
        if (isolated && definition.value("api").toString()=="BleeckerSlider") {
            QTimer::singleShot(150,&app,[&engine,&app,definition] {
                const auto window=qobject_cast<QQuickWindow *>(engine.rootObjects().value(0));
                const auto slider=window ? findVisual(window->contentItem(),"referenceCaseComponent") : nullptr;
                if (!slider) { app.exit(13);return; }
                const auto variant=definition.value("variant").toString();
                if (variant.startsWith("clicked-")) {
                    const auto point=slider->mapToScene(QPointF(variant.endsWith("upper") ? slider->width()-1 : 1,slider->height()/2));
                    const auto global=QPointF(window->mapToGlobal(point.toPoint()));
                    QMouseEvent down(QEvent::MouseButtonPress,point,global,Qt::LeftButton,Qt::LeftButton,Qt::NoModifier);
                    QMouseEvent up(QEvent::MouseButtonRelease,point,global,Qt::LeftButton,Qt::NoButton,Qt::NoModifier);
                    QCoreApplication::sendEvent(window,&down);QCoreApplication::sendEvent(window,&up);
                }
                if (variant=="dragged") {
                    const auto start=slider->mapToScene(QPointF(10+0.35*(slider->width()-20),8));
                    const auto end=slider->mapToScene(QPointF(10+0.75*(slider->width()-20),8));
                    QMouseEvent down(QEvent::MouseButtonPress,start,QPointF(window->mapToGlobal(start.toPoint())),Qt::LeftButton,Qt::LeftButton,Qt::NoModifier);
                    QMouseEvent move(QEvent::MouseMove,end,QPointF(window->mapToGlobal(end.toPoint())),Qt::NoButton,Qt::LeftButton,Qt::NoModifier);
                    QMouseEvent up(QEvent::MouseButtonRelease,end,QPointF(window->mapToGlobal(end.toPoint())),Qt::LeftButton,Qt::NoButton,Qt::NoModifier);
                    QCoreApplication::sendEvent(window,&down);QCoreApplication::sendEvent(window,&move);QCoreApplication::sendEvent(window,&up);
                }
                if (variant=="external") window->setProperty("sliderValue",0.8);
                slider->setFocus(false);
            });
        }
        if (isolated && definition.value("api").toString()=="BleeckerCollectionFilters") {
            QTimer::singleShot(150, &app, [&engine,&app,definition] {
                const auto window=qobject_cast<QQuickWindow *>(engine.rootObjects().value(0));
                const auto filters=window ? findVisual(window->contentItem(),"referenceCaseComponent") : nullptr;
                const auto variant=definition.value("variant").toString();
                const QString actionName=variant=="cleared" ? "bleeckerSearchClear" : variant=="removed" ? "bleeckerFilterRemove" : variant=="activated" ? "bleeckerFilterAction" : "";
                if (!actionName.isEmpty()) {
                    const auto action=filters ? findVisual(filters,actionName) : nullptr;
                    if (!action || !QMetaObject::invokeMethod(action,"click")) { app.exit(12); return; }
                }
                if (filters) if (const auto search=findVisual(filters,"bleeckerCollectionSearch")) search->setFocus(false);
            });
        }
        if (fixture == "secure-field" || (isolated && definition.value("api").toString()=="BleeckerSecureField"
            && definition.value("variant").toString().startsWith("revealed-"))) {
            QTimer::singleShot(150, &app, [&engine,&app,isolated] {
                const auto window=qobject_cast<QQuickWindow *>(engine.rootObjects().value(0));
                const auto field=window ? findVisual(window->contentItem(),isolated ? "referenceCaseComponent" : "galleryRevealedField") : nullptr;
                const auto action=field ? findVisual(field,"bleeckerSecureReveal") : nullptr;
                if (!action || !QMetaObject::invokeMethod(action,"click") || !field->property("revealed").toBool()) app.exit(9);
            });
        }
        QTimer::singleShot(700, &app, [&engine, &app, &parser, path, isolated, definition] {
            const auto window = qobject_cast<QQuickWindow *>(engine.rootObjects().value(0));
            if (!window) { app.exit(2); return; }
            const auto component = isolated ? findVisual(window->contentItem(), "referenceCaseComponent") : nullptr;
            const bool expectedEmpty = definition.value("expectedEmpty").toBool();
            QObject *selectorPopup=nullptr;
            QQuickItem *selectorPopupContent=nullptr;
            if (parser.value("fixture")=="selection") {
                const auto selector=findVisual(window->contentItem(),"selectorCandidate");
                if (selector) selectorPopup=selector->property("popup").value<QObject*>();
                if (selectorPopup) selectorPopupContent=selectorPopup->property("contentItem").value<QQuickItem*>();
                if (!selectorPopup || !selectorPopupContent || !selectorPopup->property("visible").toBool()
                    || selectorPopup->property("popupType").toInt()!=0) { app.exit(7); return; }
            }
            const bool openSelector=isolated && definition.value("api").toString()=="BleeckerSelect"
                && definition.value("variant").toString().startsWith("open-");
            if (openSelector && component) {
                selectorPopup=component->property("popup").value<QObject*>();
                if (selectorPopup) selectorPopupContent=selectorPopup->property("contentItem").value<QQuickItem*>();
                if (!selectorPopup || !selectorPopupContent || !selectorPopup->property("visible").toBool()
                    || selectorPopup->property("popupType").toInt()!=0) { app.exit(7); return; }
            }
            if (isolated && (!component || component->width() <= 0 || component->height() < 0
                || (component->height() == 0 && !expectedEmpty)
                || (expectedEmpty && (definition.value("api").toString() != "BleeckerDashboardGrid"
                    || definition.value("variant").toString() != "empty" || component->height() != 0)))) { app.exit(6); return; }
            if (!window->grabWindow().save(path)) { app.exit(2); return; }
            QJsonObject meta{{"qt", qVersion()}, {"os", QSysInfo::prettyProductName()},
                {"compiler", QString::fromUtf8(__VERSION__)}, {"environmentRecord", "environment.json"},
                {"architecture", QSysInfo::currentCpuArchitecture()}, {"platform", QGuiApplication::platformName()},
                {"captureMethod", "QQuickWindow::grabWindow (single window; not compositor overlay evidence)"},
                {"width", window->width()}, {"height", window->height()}, {"dpr", window->devicePixelRatio()},
                {"graphicsApi", int(window->rendererInterface()->graphicsApi())},
                {"requestedGraphicsBackend", qEnvironmentVariable("QSG_RHI_BACKEND")},
                {"quickBackend", qEnvironmentVariable("QT_QUICK_BACKEND")}};
            QFont font("Encode Sans"); font.setPixelSize(14); font.setWeight(QFont::Medium);
            const auto raw = QRawFont::fromFont(font);
            meta.insert("resolvedFontFamily", raw.familyName());
            meta.insert("resolvedFontStyle", raw.styleName());
            const auto surface = window->findChild<QQuickItem *>("bleeckerButtonSurface");
            if (surface) {
                meta.insert("surfaceWidth", surface->width());
                meta.insert("surfaceHeight", surface->height());
                const auto surfaceOrigin = surface->mapToScene(QPointF(0, 0));
                meta.insert("surfaceX", surfaceOrigin.x());
                meta.insert("surfaceY", surfaceOrigin.y());
                meta.insert("surfaceRadius", surface->property("radius").toDouble());
                meta.insert("surfaceRendererType", surface->property("rendererType").toInt());
                meta.insert("surfaceOuterPath", surface->property("outerPath").toString());
                meta.insert("surfaceBorderPath", surface->property("borderPath").toString());
            }
            const auto label = window->findChild<QQuickItem *>("bleeckerButtonLabel");
            if (label) {
                const auto labelFont = label->property("font").value<QFont>();
                meta.insert("labelFontFamily", label->property("resolvedFamily").toString());
                meta.insert("labelFontStyle", label->property("resolvedStyle").toString());
                meta.insert("labelFontWeight", int(labelFont.weight()));
                meta.insert("labelFontHintingPreference", int(labelFont.hintingPreference()));
                meta.insert("labelRenderer", "QQuickPaintedItem/QPainter glyph runs at logical font size");
                meta.insert("labelPixelSize", label->property("logicalPixelSize").toDouble());
                meta.insert("labelFontPointSize", labelFont.pointSizeF());
                meta.insert("labelWidth", label->width());
                meta.insert("labelHeight", label->height());
                meta.insert("labelBaseline", label->baselineOffset());
                const auto origin = label->mapToScene(QPointF(0, 0));
                meta.insert("labelX", origin.x()); meta.insert("labelY", origin.y());
                meta.insert("labelSceneBaseline", label->mapToScene(QPointF(0, label->baselineOffset())).y());
                const auto content = label->parentItem();
                meta.insert("labelLocalX", label->x()); meta.insert("labelLocalY", label->y());
                meta.insert("contentX", content->x()); meta.insert("contentY", content->y());
                meta.insert("contentWidth", content->width()); meta.insert("contentHeight", content->height());
                meta.insert("contentImplicitHeight", content->implicitHeight());
            }
            meta.insert("fixture", parser.value("fixture"));
            meta.insert("textScale", window->property("fixtureTextScale").toDouble());
            meta.insert("variant", parser.value("variant"));
            meta.insert("size", parser.value("size"));
            meta.insert("state", parser.isSet("disabled") ? "disabled" : "enabled");
            meta.insert("appearance", parser.isSet("dark") ? "dark" : "light");
            if (selectorPopup) {
                const auto origin=selectorPopupContent->mapToScene(QPointF(0,0));
                meta.insert("popoverGeometry",QJsonObject{{"x",origin.x()-selectorPopup->property("leftPadding").toDouble()},
                    {"y",origin.y()-selectorPopup->property("topPadding").toDouble()},
                    {"width",selectorPopup->property("width").toDouble()},{"height",selectorPopup->property("height").toDouble()}});
                meta.insert("popupVisible",true); meta.insert("popupType",selectorPopup->property("popupType").toInt());
                meta.insert("popupContentOrigin",QJsonObject{{"x",origin.x()},{"y",origin.y()}});
                meta.insert("popupContentSize",QJsonObject{{"width",selectorPopupContent->width()},{"height",selectorPopupContent->height()}});
                meta.insert("overlayCoverage","Open owned Popup.Item is inside the captured window; compositor/session evidence is separate");
                meta.insert("symbolAcceptance","pending; original chevron/checkmark candidates");
                QJsonArray labels; recordLabels(window->contentItem(),labels); meta.insert("labels",labels);
            }
            if (isolated) {
                if (definition.value("api").toString()=="BleeckerSecureField") {
                    const bool revealed=component->property("revealed").toBool();
                    if (revealed!=definition.value("variant").toString().startsWith("revealed-")
                        || component->property("text").toString()!=definition.value("text").toString()
                        || (!revealed && !component->property("text").toString().isEmpty()
                            && component->property("displayText")==component->property("text"))) { app.exit(9); return; }
                    meta.insert("revealed",revealed); meta.insert("sourceValuePreserved",true);
                }
                if (definition.value("fixture").toString().startsWith("search-"))
                    meta.insert("sourceValueAfterAction",component->property("text").toString());
                if (definition.value("api").toString()=="BleeckerSlider") {
                    meta.insert("sourceMinimum",component->property("from").toDouble());
                    meta.insert("sourceMaximum",component->property("to").toDouble());
                    meta.insert("sourceStep",component->property("stepSize").toDouble());
                    meta.insert("sourceValueAfterAction",component->property("value").toDouble());
                    meta.insert("linuxModelEdits",window->property("sliderEdits").toInt());
                    meta.insert("sourceBindingUpdated",window->property("sliderEdits").toInt()>0);
                    meta.insert("sourceControlActiveState","active");
                }
                if (definition.value("api").toString()=="BleeckerCollectionFilters") {
                    meta.insert("sourceQueryAfterAction",component->property("query").toString());
                    meta.insert("sourceContentAfterAction",window->property("collectionHasChip").toBool());
                    meta.insert("sourceSelectedAfterAction",window->property("collectionSelected").toBool());
                    meta.insert("sourceActionCounts",QJsonObject{{"activations",window->property("collectionActivations").toInt()},{"removals",window->property("collectionRemovals").toInt()}});
                }
                for (auto it = definition.begin(); it != definition.end(); ++it) meta.insert(it.key(), it.value());
                meta.insert("caseDefinitions", parser.value("case-definitions"));
                meta.insert("componentSize", QJsonObject{{"width", component->width()}, {"height", component->height()}});
                const auto position = component->mapToScene(QPointF(0, 0));
                meta.insert("componentOrigin", QJsonObject{{"x", position.x()}, {"y", position.y()}});
                QJsonArray labels;
                recordLabels(component, labels);
                meta.insert("labels", labels);
                meta.insert("dynamicStateTiming", "700 ms settlement; reduced motion; no matched native animation phase");
                meta.insert("referenceAcceptance", "proposed reference; diagnostic comparison only");
            }
            QFile file(path + ".json");
            if (!file.open(QIODevice::WriteOnly)) { app.exit(3); return; }
            file.write(QJsonDocument(meta).toJson());
            app.exit(0);
        });
    }
    return app.exec();
}

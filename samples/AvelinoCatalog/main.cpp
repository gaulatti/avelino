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
        labels.append(QJsonObject{{"role", root->objectName()}, {"text", root->property("text").toString()},
            {"family", raw.familyName()}, {"style", raw.styleName()}, {"weight", int(font.weight())},
            {"requestedPointSize", font.pointSizeF()}, {"requestedPixelSize", font.pixelSize()},
            {"width", root->width()}, {"height", root->height()}, {"x", position.x()}, {"y", position.y()},
            {"sceneBaseline", root->mapToScene(QPointF(0, root->baselineOffset())).y()}});
    }
    for (auto child : root->childItems()) recordLabels(child, labels);
}

int main(int argc, char *argv[]) {
    QGuiApplication app(argc, argv);
    QCommandLineParser parser;
    parser.addHelpOption();
    parser.addOptions({QCommandLineOption("capture", "Save the displayed fixture to PNG and exit", "path"),
                       QCommandLineOption("dark", "Use dark reference appearance"),
                       QCommandLineOption("fixture", "Render a fixture (button, foundations, surfaces, data-display, controls, composition or reference-case)", "name"),
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
    if (parser.isSet("fixture") && fixture != "button" && fixture != "foundations" && fixture != "surfaces" && fixture != "data-display" && fixture != "controls" && fixture != "composition" && !isolated) return 4;
    engine.loadFromModule("AvelinoCatalog", isolated ? "ReferenceCaseFixture" : fixture == "composition" ? "CompositionFixture" : fixture == "controls" ? "ControlsFixture" : fixture == "data-display" ? "DataDisplayFixture" : fixture == "surfaces" ? "SurfacesFixture" : fixture == "foundations" ? "FoundationsFixture"
        : fixture == "button" ? "ButtonFixture" : "Main");
    if (parser.isSet("capture")) {
        const auto path = parser.value("capture");
        QTimer::singleShot(700, &app, [&engine, &app, &parser, path, isolated, definition] {
            const auto window = qobject_cast<QQuickWindow *>(engine.rootObjects().value(0));
            if (!window) { app.exit(2); return; }
            const auto component = isolated ? findVisual(window->contentItem(), "referenceCaseComponent") : nullptr;
            if (isolated && (!component || component->width() <= 0 || component->height() <= 0)) { app.exit(6); return; }
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
            if (isolated) {
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

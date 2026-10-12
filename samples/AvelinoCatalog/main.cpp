#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QQuickWindow>
#include <QTimer>
#include <QCommandLineParser>
#include <QJsonDocument>
#include <QJsonObject>
#include <QFile>
#include <QSysInfo>
#include <QFont>
#include <QRawFont>
#include <QQuickItem>
#include <QSGRendererInterface>
#include <cmath>

int main(int argc, char *argv[]) {
    QGuiApplication app(argc, argv);
    QCommandLineParser parser;
    parser.addHelpOption();
    parser.addOptions({QCommandLineOption("capture", "Save the displayed fixture to PNG and exit", "path"),
                       QCommandLineOption("dark", "Use dark reference appearance"),
                       QCommandLineOption("fixture", "Render a deterministic fixture (button, foundations, surfaces, data-display or controls)", "name"),
                       QCommandLineOption("variant", "Button variant", "name", "primary"),
                       QCommandLineOption("size", "Button size", "name", "md"),
                       QCommandLineOption("disabled", "Disable the fixture control"),
                       QCommandLineOption("text-scale", "Use a positive logical text scale", "factor", "1")});
    parser.process(app);
    bool validScale = false;
    const qreal textScale = parser.value("text-scale").toDouble(&validScale);
    if (!validScale || !std::isfinite(textScale) || textScale <= 0) return 5;
    QQmlApplicationEngine engine;
    engine.rootContext()->setContextProperty("captureDark", parser.isSet("dark"));
    engine.rootContext()->setContextProperty("captureVariant", parser.value("variant"));
    engine.rootContext()->setContextProperty("captureSize", parser.value("size"));
    engine.rootContext()->setContextProperty("captureDisabled", parser.isSet("disabled"));
    engine.rootContext()->setContextProperty("captureTextScale", textScale);
    QObject::connect(&engine, &QQmlApplicationEngine::objectCreationFailed, &app, [] { QCoreApplication::exit(1); }, Qt::QueuedConnection);
    const auto fixture = parser.value("fixture");
    if (parser.isSet("fixture") && fixture != "button" && fixture != "foundations" && fixture != "surfaces" && fixture != "data-display" && fixture != "controls") return 4;
    engine.loadFromModule("AvelinoCatalog", fixture == "controls" ? "ControlsFixture" : fixture == "data-display" ? "DataDisplayFixture" : fixture == "surfaces" ? "SurfacesFixture" : fixture == "foundations" ? "FoundationsFixture"
        : fixture == "button" ? "ButtonFixture" : "Main");
    if (parser.isSet("capture")) {
        const auto path = parser.value("capture");
        QTimer::singleShot(700, &app, [&engine, &app, &parser, path] {
            const auto window = qobject_cast<QQuickWindow *>(engine.rootObjects().value(0));
            if (!window || !window->grabWindow().save(path)) { app.exit(2); return; }
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
            QFile file(path + ".json");
            if (!file.open(QIODevice::WriteOnly)) { app.exit(3); return; }
            file.write(QJsonDocument(meta).toJson());
            app.exit(0);
        });
    }
    return app.exec();
}

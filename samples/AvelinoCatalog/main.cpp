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

int main(int argc, char *argv[]) {
    QGuiApplication app(argc, argv);
    QCommandLineParser parser;
    parser.addHelpOption();
    parser.addOptions({QCommandLineOption("capture", "Save the displayed fixture to PNG and exit", "path"),
                       QCommandLineOption("dark", "Use dark reference appearance"),
                       QCommandLineOption("fixture", "Render a deterministic fixture (button)", "name"),
                       QCommandLineOption("variant", "Button variant", "name", "primary"),
                       QCommandLineOption("size", "Button size", "name", "md"),
                       QCommandLineOption("disabled", "Disable the fixture control")});
    parser.process(app);
    QQmlApplicationEngine engine;
    engine.rootContext()->setContextProperty("captureDark", parser.isSet("dark"));
    engine.rootContext()->setContextProperty("captureVariant", parser.value("variant"));
    engine.rootContext()->setContextProperty("captureSize", parser.value("size"));
    engine.rootContext()->setContextProperty("captureDisabled", parser.isSet("disabled"));
    QObject::connect(&engine, &QQmlApplicationEngine::objectCreationFailed, &app, [] { QCoreApplication::exit(1); }, Qt::QueuedConnection);
    if (parser.isSet("fixture") && parser.value("fixture") != "button") return 4;
    engine.loadFromModule("AvelinoCatalog", parser.isSet("fixture") ? "ButtonFixture" : "Main");
    if (parser.isSet("capture")) {
        const auto path = parser.value("capture");
        QTimer::singleShot(700, &app, [&engine, &app, &parser, path] {
            const auto window = qobject_cast<QQuickWindow *>(engine.rootObjects().value(0));
            if (!window || !window->grabWindow().save(path)) { app.exit(2); return; }
            QJsonObject meta{{"qt", qVersion()}, {"os", QSysInfo::prettyProductName()},
                {"architecture", QSysInfo::currentCpuArchitecture()}, {"platform", QGuiApplication::platformName()},
                {"captureMethod", "QQuickWindow::grabWindow (single window; not compositor overlay evidence)"},
                {"width", window->width()}, {"height", window->height()}, {"dpr", window->devicePixelRatio()},
                {"graphicsBackend", qEnvironmentVariable("QSG_RHI_BACKEND")},
                {"quickBackend", qEnvironmentVariable("QT_QUICK_BACKEND")}};
            QFont font("Encode Sans"); font.setPixelSize(14); font.setWeight(QFont::Medium);
            const auto raw = QRawFont::fromFont(font);
            meta.insert("resolvedFontFamily", raw.familyName());
            meta.insert("resolvedFontStyle", raw.styleName());
            meta.insert("fixture", parser.value("fixture"));
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

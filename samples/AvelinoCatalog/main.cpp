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

int main(int argc, char *argv[]) {
    QGuiApplication app(argc, argv);
    QCommandLineParser parser;
    parser.addHelpOption();
    parser.addOptions({{{"capture"}, "Save the displayed fixture to PNG and exit", "path"},
                       {{"dark"}, "Use dark reference appearance"}});
    parser.process(app);
    QQmlApplicationEngine engine;
    engine.rootContext()->setContextProperty("captureDark", parser.isSet("dark"));
    QObject::connect(&engine, &QQmlApplicationEngine::objectCreationFailed, &app, [] { QCoreApplication::exit(1); }, Qt::QueuedConnection);
    engine.loadFromModule("AvelinoCatalog", "Main");
    if (parser.isSet("capture")) {
        const auto path = parser.value("capture");
        QTimer::singleShot(700, &app, [&engine, &app, path] {
            const auto window = qobject_cast<QQuickWindow *>(engine.rootObjects().value(0));
            if (!window || !window->grabWindow().save(path)) { app.exit(2); return; }
            QJsonObject meta{{"qt", qVersion()}, {"os", QSysInfo::prettyProductName()},
                {"architecture", QSysInfo::currentCpuArchitecture()}, {"platform", QGuiApplication::platformName()},
                {"captureMethod", "QQuickWindow::grabWindow (single window; not compositor overlay evidence)"},
                {"width", window->width()}, {"height", window->height()}, {"dpr", window->devicePixelRatio()},
                {"graphicsBackend", qEnvironmentVariable("QSG_RHI_BACKEND")},
                {"quickBackend", qEnvironmentVariable("QT_QUICK_BACKEND")}};
            QFile file(path + ".json");
            if (!file.open(QIODevice::WriteOnly)) { app.exit(3); return; }
            file.write(QJsonDocument(meta).toJson());
            app.exit(0);
        });
    }
    return app.exec();
}

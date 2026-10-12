#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QTimer>
#include <QQuickWindow>
#include <QQuickItem>
#include <QTest>
#include <QFontDatabase>
#include <QCommandLineParser>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QQmlContext>
#include <QSGRendererInterface>
#include <cmath>
int main(int argc, char **argv) {
    QGuiApplication app(argc, argv);
    QCommandLineParser parser;
    parser.addHelpOption();
    parser.addOption(QCommandLineOption("evidence", "Save window capture and metadata, then wait for a session capture marker.", "path"));
    parser.addOption(QCommandLineOption("dark", "Exercise dark appearance."));
    parser.addOption(QCommandLineOption("text-scale", "Exercise text scaling.", "factor", "1"));
    parser.process(app);
    bool validScale = false;
    const double textScale = parser.value("text-scale").toDouble(&validScale);
    if (!validScale || !std::isfinite(textScale) || textScale <= 0) return 12;
    QQmlApplicationEngine engine;
    engine.rootContext()->setContextProperty("consumerDark", parser.isSet("dark"));
    engine.rootContext()->setContextProperty("consumerTextScale", textScale);
    engine.addImportPath(QStringLiteral(AVELINO_INSTALLED_IMPORT_PATH));
    QObject::connect(&engine, &QQmlApplicationEngine::objectCreationFailed, &app, [] { QCoreApplication::exit(1); }, Qt::QueuedConnection);
    engine.loadFromModule("InstalledConsumer", "Main");
    QTimer::singleShot(500, &app, [&engine, &app, &parser, textScale] {
        auto window = qobject_cast<QQuickWindow *>(engine.rootObjects().value(0));
        if (!window) { app.exit(2); return; }
        auto button = window->findChild<QQuickItem *>("button");
        auto field = window->findChild<QQuickItem *>("field");
        if (!button || !field) { app.exit(3); return; }
        QTest::mouseClick(window, Qt::LeftButton, Qt::NoModifier, button->mapToScene(QPointF(button->width()/2, button->height()/2)).toPoint());
        if (window->property("invocations").toInt() != 1) { app.exit(4); return; }
        button->setProperty("enabled", false);
        QTest::mouseClick(window, Qt::LeftButton, Qt::NoModifier, button->mapToScene(QPointF(10,10)).toPoint());
        if (window->property("invocations").toInt() != 1) { app.exit(5); return; }
        button->setProperty("enabled", true);
        button->setProperty("loading", true);
        QTest::mouseClick(window, Qt::LeftButton, Qt::NoModifier, button->mapToScene(QPointF(10,10)).toPoint());
        if (window->property("invocations").toInt() != 1) { app.exit(10); return; }
        field->forceActiveFocus();
        QTest::keyClick(window, Qt::Key_A);
        QTest::keyClick(window, Qt::Key_B);
        if (field->property("text").toString() != "ab") { app.exit(6); return; }
        QTest::keyClick(window, Qt::Key_A, Qt::ControlModifier);
        if (field->property("selectedText").toString() != "ab") { app.exit(7); return; }
        QTest::keyClick(window, Qt::Key_C);
        if (field->property("text").toString() != "c") { app.exit(8); return; }
        if (!QFontDatabase::families().contains("Encode Sans") || !QFontDatabase::families().contains("Libre Franklin")) { app.exit(9); return; }
        qInfo("Installed consumer: pointer, disabled action, editing, selection replacement, and bundled font registration passed");
        if (parser.isSet("evidence")) {
            const auto path = parser.value("evidence");
            if (!window->grabWindow().save(path + ".png")) { app.exit(13); return; }
            QJsonObject metadata{{"qt", qVersion()}, {"platform", QGuiApplication::platformName()},
                {"compiler", QString::fromUtf8(__VERSION__)},
                {"width", window->width()}, {"height", window->height()}, {"dpr", window->devicePixelRatio()},
                {"graphicsApi", int(window->rendererInterface()->graphicsApi())},
                {"requestedGraphicsBackend", qEnvironmentVariable("QSG_RHI_BACKEND")},
                {"quickBackend", qEnvironmentVariable("QT_QUICK_BACKEND")},
                {"appearance", parser.isSet("dark") ? "dark" : "light"}, {"textScale", textScale},
                {"inputMethod", "QTest synthetic in-process pointer and keyboard events"},
                {"windowCaptureMethod", "QQuickWindow::grabWindow; session capture recorded separately"},
                {"overlayCoverage", "pending; no overlay component implemented"},
                {"behaviorChecks", "passed"}};
            QFile file(path + ".json");
            if (!file.open(QIODevice::WriteOnly)) { app.exit(14); return; }
            file.write(QJsonDocument(metadata).toJson());
            file.close();
            auto poll = new QTimer(&app);
            QObject::connect(poll, &QTimer::timeout, &app, [&app, path] {
                if (QFile::exists(path + ".captured")) app.exit(0);
            });
            poll->start(100);
            QTimer::singleShot(10000, &app, [&app] { app.exit(15); });
            return;
        }
        app.exit(0);
    });
    return app.exec();
}

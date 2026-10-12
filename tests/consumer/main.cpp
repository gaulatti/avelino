#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QTimer>
#include <QQuickWindow>
#include <QQuickItem>
#include <QTest>
#include <QFontDatabase>
int main(int argc, char **argv) {
    QGuiApplication app(argc, argv);
    QQmlApplicationEngine engine;
    engine.addImportPath(QStringLiteral(AVELINO_INSTALLED_IMPORT_PATH));
    QObject::connect(&engine, &QQmlApplicationEngine::objectCreationFailed, &app, [] { QCoreApplication::exit(1); }, Qt::QueuedConnection);
    engine.loadFromModule("InstalledConsumer", "Main");
    QTimer::singleShot(500, &app, [&engine, &app] {
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
        app.exit(0);
    });
    return app.exec();
}

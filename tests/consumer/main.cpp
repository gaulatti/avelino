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
#include <QColor>
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
        auto surface = button->findChild<QQuickItem *>("bleeckerButtonSurface");
        if (!surface || surface->property("radius").toDouble() != 7
            || surface->property("borderWidth").toDouble() != 1
            || surface->property("outerPath").toString().isEmpty()) { app.exit(16); return; }
        QTest::mouseClick(window, Qt::LeftButton, Qt::NoModifier, button->mapToScene(QPointF(button->width()/2, button->height()/2)).toPoint());
        if (window->property("invocations").toInt() != 1) { app.exit(4); return; }
        button->setProperty("enabled", false);
        QTest::mouseClick(window, Qt::LeftButton, Qt::NoModifier, button->mapToScene(QPointF(10,10)).toPoint());
        if (window->property("invocations").toInt() != 1) { app.exit(5); return; }
        button->setProperty("enabled", true);
        button->setProperty("loading", true);
        QTest::mouseClick(window, Qt::LeftButton, Qt::NoModifier, button->mapToScene(QPointF(10,10)).toPoint());
        if (window->property("invocations").toInt() != 1) { app.exit(10); return; }
        auto groupFirst = window->findChild<QQuickItem *>("groupFirst");
        auto groupSecond = window->findChild<QQuickItem *>("groupSecond");
        if (!groupFirst || !groupSecond) { app.exit(20); return; }
        groupFirst->forceActiveFocus();
        QTest::keyClick(window, Qt::Key_Space);
        QTest::keyClick(window, Qt::Key_Tab);
        if (!groupSecond->hasActiveFocus()) { app.exit(21); return; }
        QTest::keyClick(window, Qt::Key_Space);
        if (window->property("groupedInvocations").toInt() != 2) { app.exit(22); return; }
        field->forceActiveFocus();
        QTest::keyClick(window, Qt::Key_A);
        QTest::keyClick(window, Qt::Key_B);
        if (field->property("text").toString() != "ab") { app.exit(6); return; }
        QTest::keyClick(window, Qt::Key_A, Qt::ControlModifier);
        if (field->property("selectedText").toString() != "ab") { app.exit(7); return; }
        QTest::keyClick(window, Qt::Key_C);
        if (field->property("text").toString() != "c") { app.exit(8); return; }
        if (!QFontDatabase::families().contains("Encode Sans") || !QFontDatabase::families().contains("Libre Franklin")) { app.exit(9); return; }
        const auto separator = window->findChild<QQuickItem *>("separator");
        const auto progress = window->findChild<QQuickItem *>("progress");
        const auto progressFill = progress ? progress->findChild<QQuickItem *>("bleeckerProgressFill") : nullptr;
        const auto skeleton = window->findChild<QQuickItem *>("skeleton");
        const auto header = window->findChild<QQuickItem *>("header");
        const auto panel = window->findChild<QQuickItem *>("panelLayout");
        const auto panelCenter = panel ? panel->findChild<QQuickItem *>("bleeckerPanelContent") : nullptr;
        const auto bauhaus = window->findChild<QQuickItem *>("bauhaus");
        if (!separator || separator->height() != 1
            || separator->property("color").value<QColor>().alphaF() != QColor::fromRgbF(0,0,0,0.08).alphaF()
            || !progressFill || progressFill->width() != 63
            || !skeleton || skeleton->property("animating").toBool()
            || !header || header->height() != 56
            || !panelCenter || panelCenter->width() != 86
            || !bauhaus || !bauhaus->clip()) { app.exit(23); return; }
        // Loading changes the composition and label origin. Wait for its frame,
        // then inspect painted coordinates inside the installed component.
        QTest::qWait(50);
        auto label = button->findChild<QQuickItem *>("bleeckerButtonLabel");
        if (!label) { app.exit(17); return; }
        const auto fractional = window->findChild<QQuickItem *>("fractionalButton");
        const auto fractionalLabel = fractional ? fractional->findChild<QQuickItem *>("bleeckerButtonLabel") : nullptr;
        if (!fractionalLabel || std::abs(fractionalLabel->property("logicalPixelSize").toDouble() - 13 * textScale) > 0.000001
            || fractionalLabel->property("resolvedFamily").toString() != "Encode Sans") { app.exit(19); return; }
        const qreal dpr = window->effectiveDevicePixelRatio();
        const auto surfaceOrigin = surface->mapToScene(QPointF());
        const auto labelBaseline = label->mapToScene(QPointF(0, label->baselineOffset()));
        for (const qreal coordinate : {surfaceOrigin.x(), surfaceOrigin.y(), labelBaseline.x(), labelBaseline.y()}) {
            if (std::abs(coordinate * dpr - std::round(coordinate * dpr)) > 0.00001) { app.exit(18); return; }
        }
        qInfo("Installed consumer: actions, group keyboard navigation, editing, fonts, painted placement, and surface/layout contracts passed");
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
                {"buttonSurfaceRendererType", surface->property("rendererType").toInt()},
                {"buttonSurfaceRadius", surface->property("radius").toDouble()},
                {"buttonSurfaceOuterPath", surface->property("outerPath").toString()},
                {"buttonSurfaceX", surfaceOrigin.x()}, {"buttonSurfaceY", surfaceOrigin.y()},
                {"buttonLabelBaselineX", labelBaseline.x()}, {"buttonLabelBaselineY", labelBaseline.y()},
                {"paintPlacementChecks", "passed"},
                {"fractionalButtonGlyphPixels", fractionalLabel->property("logicalPixelSize").toDouble()},
                {"foundationChecks", "passed"}, {"groupKeyboardChecks", "passed"},
                {"labelRenderer", "QQuickPaintedItem/QPainter glyph runs at logical font size"},
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

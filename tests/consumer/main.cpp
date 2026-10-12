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
static QQuickItem *findVisualItem(QQuickItem *item, const QString &name) {
    if (item->objectName() == name) return item;
    for (auto child : item->childItems())
        if (auto found = findVisualItem(child,name)) return found;
    return nullptr;
}
static void runCompositionConsumer(QQuickWindow *window, QGuiApplication &app,
                                   const QCommandLineParser &parser, double textScale) {
    auto item = [window](const QString &name) { return findVisualItem(window->contentItem(),name); };
    const auto shell=item("appShell"), grid=item("dashboardGrid"), section=item("dashboardSection");
    const auto action=item("reviewAction"), feed=item("feedItem"), footer=item("footer");
    const auto sidebar=item("bleeckerAppSidebar"), content=item("bleeckerAppContent");
    const auto first=item("bleeckerDashboardTile0"), second=item("bleeckerDashboardTile1");
    if (!shell || !grid || !section || !action || !feed || !footer || !sidebar || !content || !first || !second) {
        qCritical("Installed composition is missing a visual slot"); app.exit(50); return;
    }
    if (grid->property("columns").toInt()!=2 || sidebar->width()!=240 || content->width()!=519
        || first->width()!=251.5 || second->x()!=267.5 || first->height()<=0 || footer->height()<=41) {
        qCritical("Installed composition geometry: columns=%d sidebar=%g content=%g first=%g secondX=%g tileHeight=%g footer=%g",
            grid->property("columns").toInt(),sidebar->width(),content->width(),first->width(),second->x(),first->height(),footer->height());
        app.exit(51); return;
    }
    QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,
        action->mapToScene(QPointF(action->width()/2,action->height()/2)).toPoint());
    action->forceActiveFocus(); QTest::keyClick(window,Qt::Key_Space);
    if (window->property("reviewInvocations").toInt()!=2 || !action->hasActiveFocus()) { app.exit(52); return; }
    window->resize(700,560); QTest::qWait(80);
    if (grid->property("columns").toInt()!=1 || second->y()<=first->y() || content->width()!=379
        || !action->hasActiveFocus()) { app.exit(53); return; }
    window->resize(840,560); QTest::qWait(80);
    if (grid->property("columns").toInt()!=2 || first->width()!=251.5 || !action->hasActiveFocus()) { app.exit(54); return; }
    qInfo("Installed composition: adaptive grid reflow, slots, pointer/keyboard actions and focus through resize passed");
    if (!parser.isSet("evidence")) { app.exit(0); return; }
    const auto path=parser.value("evidence");
    if (!window->grabWindow().save(path+".png")) { app.exit(55); return; }
    QJsonObject record{{"fixture","composition"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},
        {"compiler",QString::fromUtf8(__VERSION__)},{"width",window->width()},{"height",window->height()},
        {"dpr",window->devicePixelRatio()},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},
        {"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},{"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},
        {"appearance",parser.isSet("dark") ? "dark" : "light"},{"textScale",textScale},
        {"inputMethod","QTest synthetic in-process pointer and keyboard events"},
        {"windowCaptureMethod","QQuickWindow::grabWindow; session capture recorded separately"},
        {"compositionChecks","passed"},{"focusResizeChecks","passed"},
        {"gridColumns",grid->property("columns").toInt()},{"tileWidth",first->width()},
        {"accessibilityAcceptance","pending; screen-reader output unverified"},
        {"referenceComparison","pending; no native composition fixtures accepted"}};
    QFile file(path+".json");
    if (!file.open(QIODevice::WriteOnly)) { app.exit(56); return; }
    file.write(QJsonDocument(record).toJson()); file.close();
    auto timer=new QTimer(&app);
    QObject::connect(timer,&QTimer::timeout,&app,[&app,path] { if (QFile::exists(path+".captured")) app.exit(0); });
    timer->start(100); QTimer::singleShot(10000,&app,[&app] { app.exit(57); });
}
static void runControlsConsumer(QQuickWindow *window, QGuiApplication &app,
                                const QCommandLineParser &parser, double textScale) {
    auto item = [window](const QString &name) { return findVisualItem(window->contentItem(),name); };
    auto click = [window](QQuickItem *control) {
        QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,
            control->mapToScene(QPointF(control->width()/2,control->height()/2)).toPoint());
    };
    const auto field = item("formInput"), area = item("textArea"), editor = item("bleeckerTextAreaInput");
    const auto toggle = item("toggle"), switchControl = item("switch"), segments = item("segments");
    const auto first = item("bleeckerSegment0"), disabled = item("bleeckerSegment1"), last = item("bleeckerSegment2");
    if (!field || !area || !editor || !toggle || !switchControl || !segments || !first || !disabled || !last) {
        qCritical("Installed form control missing from visual tree"); app.exit(30); return;
    }
    const auto placeholder = field->findChild<QQuickItem *>("bleeckerTextFieldPlaceholder");
    if (!placeholder || !placeholder->isVisible() || !field->isVisible() || field->width()<=0 || field->height()<=0) { app.exit(46); return; }
    click(field);
    if (!field->hasActiveFocus()) { app.exit(47); return; }
    QTest::keyClick(window,Qt::Key_A); QTest::keyClick(window,Qt::Key_B);
    if (field->property("text").toString() != "ab") { app.exit(31); return; }
    area->forceActiveFocus(); QTest::keyClick(window,Qt::Key_X); QTest::keyClick(window,Qt::Key_Return); QTest::keyClick(window,Qt::Key_Z);
    QTest::keyClick(window,Qt::Key_A,Qt::ControlModifier);
    if (area->property("selectedText").toString() != "x\nz") { app.exit(32); return; }
    QTest::keyClick(window,Qt::Key_N);
    if (area->property("text").toString() != "n") { app.exit(33); return; }
    click(switchControl);
    if (!switchControl->property("checked").toBool()) { app.exit(34); return; }
    switchControl->forceActiveFocus(); QTest::keyClick(window,Qt::Key_Space);
    if (switchControl->property("checked").toBool()) { app.exit(35); return; }
    click(toggle);
    if (!toggle->property("selected").toBool() || window->property("toggleInvocations").toInt()!=1) { app.exit(36); return; }
    click(disabled);
    if (segments->property("selection").toString() != "a") { app.exit(37); return; }
    click(last);
    if (segments->property("selection").toString() != "c") { app.exit(38); return; }
    first->forceActiveFocus(); QTest::keyClick(window,Qt::Key_Space); QTest::keyClick(window,Qt::Key_Tab);
    if (!last->hasActiveFocus()) { app.exit(39); return; }
    QTest::keyClick(window,Qt::Key_Space);
    if (segments->property("selection").toString() != "c") { app.exit(40); return; }
    QStringList lines; for (int i=0;i<30;++i) lines << "Multiline content";
    area->setProperty("text",lines.join('\n')); QTest::qWait(50);
    const auto viewport = item("bleeckerTextAreaViewport"), scrollbar = item("bleeckerTextAreaScrollBar");
    if (!viewport || !scrollbar || viewport->property("contentHeight").toDouble()<=viewport->height()
        || scrollbar->property("size").toDouble()>=1) { app.exit(41); return; }
    scrollbar->setProperty("active",true);
    field->forceActiveFocus(); QTest::keyClick(window,Qt::Key_A,Qt::ControlModifier);
    for (const auto key : {Qt::Key_D,Qt::Key_O,Qt::Key_N,Qt::Key_E}) QTest::keyClick(window,key);
    if (!field->hasActiveFocus() || field->property("text").toString()!="done") { app.exit(42); return; }
    qInfo("Installed controls: editing, selection, multiline scrolling, switch/toggle actions, segmented disabled/tab order, and focus restoration passed");
    if (!parser.isSet("evidence")) { app.exit(0); return; }
    const auto path = parser.value("evidence");
    if (!window->grabWindow().save(path+".png")) { app.exit(43); return; }
    QJsonObject record{{"fixture","controls"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},
        {"compiler",QString::fromUtf8(__VERSION__)},{"width",window->width()},{"height",window->height()},
        {"dpr",window->devicePixelRatio()},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},
        {"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},{"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},
        {"appearance",parser.isSet("dark") ? "dark" : "light"},{"textScale",textScale},
        {"inputMethod","QTest synthetic in-process pointer and keyboard events"},
        {"windowCaptureMethod","QQuickWindow::grabWindow; session capture recorded separately"},
        {"overlayCoverage","pending; text editor context menu and other overlays unimplemented"},
        {"controlsChecks","passed"},{"focusRestorationChecks","passed"},
        {"scrollbarSize",scrollbar->property("size").toDouble()},{"textareaContentHeight",viewport->property("contentHeight").toDouble()},
        {"accessibilityAcceptance","pending; attached/native Qt semantics do not prove screen-reader output"}};
    QFile file(path+".json");
    if (!file.open(QIODevice::WriteOnly)) { app.exit(44); return; }
    file.write(QJsonDocument(record).toJson()); file.close();
    auto timer = new QTimer(&app);
    QObject::connect(timer,&QTimer::timeout,&app,[&app,path] { if (QFile::exists(path+".captured")) app.exit(0); });
    timer->start(100); QTimer::singleShot(10000,&app,[&app] { app.exit(45); });
}
int main(int argc, char **argv) {
    QGuiApplication app(argc, argv);
    QCommandLineParser parser;
    parser.addHelpOption();
    parser.addOption(QCommandLineOption("evidence", "Save window capture and metadata, then wait for a session capture marker.", "path"));
    parser.addOption(QCommandLineOption("dark", "Exercise dark appearance."));
    parser.addOption(QCommandLineOption("controls", "Exercise the form-control fixture."));
    parser.addOption(QCommandLineOption("composition", "Exercise the composition fixture."));
    parser.addOption(QCommandLineOption("text-scale", "Exercise text scaling.", "factor", "1"));
    parser.process(app);
    if (parser.isSet("controls") && parser.isSet("composition")) return 58;
    bool validScale = false;
    const double textScale = parser.value("text-scale").toDouble(&validScale);
    if (!validScale || !std::isfinite(textScale) || textScale <= 0) return 12;
    QQmlApplicationEngine engine;
    engine.rootContext()->setContextProperty("consumerDark", parser.isSet("dark"));
    engine.rootContext()->setContextProperty("consumerTextScale", textScale);
    engine.addImportPath(QStringLiteral(AVELINO_INSTALLED_IMPORT_PATH));
    QObject::connect(&engine, &QQmlApplicationEngine::objectCreationFailed, &app, [] { QCoreApplication::exit(1); }, Qt::QueuedConnection);
    engine.loadFromModule("InstalledConsumer", parser.isSet("composition") ? "Composition" : parser.isSet("controls") ? "Controls" : "Main");
    QTimer::singleShot(500, &app, [&engine, &app, &parser, textScale] {
        auto window = qobject_cast<QQuickWindow *>(engine.rootObjects().value(0));
        if (!window) { app.exit(2); return; }
        if (parser.isSet("composition")) { runCompositionConsumer(window,app,parser,textScale); return; }
        if (parser.isSet("controls")) { runControlsConsumer(window,app,parser,textScale); return; }
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
        const auto dataFirst = findVisualItem(window->contentItem(),"dataAction0");
        const auto dataSecond = findVisualItem(window->contentItem(),"dataAction1");
        if (!dataFirst || !dataSecond) { qCritical("Data-list actions missing from visual tree"); app.exit(25); return; }
        QTest::mouseClick(window, Qt::LeftButton, Qt::NoModifier,
            dataFirst->mapToScene(QPointF(dataFirst->width()/2,dataFirst->height()/2)).toPoint());
        dataFirst->forceActiveFocus();
        QTest::keyClick(window, Qt::Key_Space);
        QTest::keyClick(window, Qt::Key_Tab);
        if (!dataSecond->hasActiveFocus()) { app.exit(26); return; }
        QTest::keyClick(window, Qt::Key_Space);
        if (window->property("dataInvocations").toInt() != 3) { app.exit(27); return; }
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
        const auto card = window->findChild<QQuickItem *>("card");
        const auto panelSurface = window->findChild<QQuickItem *>("panelSurface");
        const auto attention = window->findChild<QQuickItem *>("attentionSurface");
        const auto status = window->findChild<QQuickItem *>("statusBadge");
        const auto statusLabel = status ? status->findChild<QQuickItem *>("bleeckerStatusLabel") : nullptr;
        const auto notification = window->findChild<QQuickItem *>("notificationBadge");
        const auto eyebrow = window->findChild<QQuickItem *>("eyebrow");
        if (!card || card->property("padding").toDouble() != 0
            || !panelSurface || panelSurface->property("hasTitle").toBool()
            || !attention || attention->property("urgency").toDouble() != 5
            || !statusLabel || std::abs(statusLabel->property("logicalPixelSize").toDouble() - 11 * textScale) > 0.000001
            || !notification || notification->property("text").toString() != "99+"
            || !eyebrow || eyebrow->property("logicalPixelSize").toDouble() != 10) { app.exit(24); return; }
        const auto avatar = window->findChild<QQuickItem *>("avatar");
        const auto imageAvatar = window->findChild<QQuickItem *>("imageAvatar");
        const auto dataList = window->findChild<QQuickItem *>("dataList");
        const auto timeline = window->findChild<QQuickItem *>("timeline");
        const auto contentLabel = timeline ? timeline->findChild<QQuickItem *>("timelineContentLabel") : nullptr;
        const auto timelineConnector = timeline ? timeline->findChild<QQuickItem *>("bleeckerTimelineConnector") : nullptr;
        const auto surfaceModifier = window->findChild<QQuickItem *>("surfaceModifier");
        if (!avatar || avatar->property("initials").toString() != "JD"
            || !imageAvatar || imageAvatar->property("imageStatus").toInt() != 1
            || !dataList || dataList->property("count").toInt() != 2
            || !contentLabel || contentLabel->property("font").value<QFont>().family() != "Libre Franklin"
            || !timelineConnector || timelineConnector->isVisible()
            || !surfaceModifier || surfaceModifier->property("radius").toDouble() != 18) { app.exit(28); return; }
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
        qInfo("Installed consumer: actions, group/list keyboard navigation, editing, fonts, painted placement, foundations, cards, badges and data display passed");
        if (parser.isSet("evidence")) {
            const auto path = parser.value("evidence");
            if (!window->grabWindow().save(path + ".png")) { app.exit(13); return; }
            QJsonObject metadata{{"fixture","base"},{"qt", qVersion()}, {"platform", QGuiApplication::platformName()},
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
                {"cardBadgeChecks", "passed"},
                {"dataDisplayChecks", "passed"}, {"dataListInputChecks", "passed"},
                {"roundedContentClipping", card->property("roundedContentClipping").toBool()},
                {"roundedClippingAcceptance", "pending; GPU mask and software gap require reference comparison"},
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

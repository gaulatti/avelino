#pragma once
#include <QElapsedTimer>
#include <QFileInfo>
#include <QQuickItemGrabResult>
#include <QPointer>

static void runAdminShellConsumer(QQuickWindow *window, QGuiApplication &app,
                                 const QCommandLineParser &parser, double textScale) {
    auto check = [&](bool value, const char *message) {
        if (!value) { qCritical("AdminShell: %s", message); app.exit(99); }
        return value;
    };
    QFile file(":/avelino/fixtures/native-admin-shell-witnesses.json");
    if (!check(file.open(QIODevice::ReadOnly), "Native witnesses missing")) return;
    const auto native = QJsonDocument::fromJson(file.readAll()).object();
    if (!check(native["reference"] == "fe8a1d462fbd793d883fb92086a16aa2947e32c9"
               && native["profiles"].toArray().size() == 80 && native["histories"].toArray().size() == 6
               && native["boundaries"].toArray().size() == 168 && native["accepted"] == false,
               "Native matrix invalid")) return;
    const auto prefix = parser.isSet("evidence") ? parser.value("evidence") : parser.value("admin-shell-report");
    if (!prefix.isEmpty()) {
        if (!check(!QFile::exists(prefix + ".json"), "Evidence already exists")) return;
        QDir().mkpath(QFileInfo(prefix).absolutePath());
    }
    auto fixture = [&]() { return window->property("primaryFixture").value<QQuickItem *>(); };
    auto shell = [&]() { return fixture() ? fixture()->property("shell").value<QQuickItem *>() : nullptr; };
    auto configure = [&](const QJsonObject &value, const QString &owner = QString("echo")) {
        return check(QMetaObject::invokeMethod(window, "configure", Q_ARG(QVariant, value.toVariantMap()),
                         Q_ARG(QVariant, owner)) && waitForShapeFrame(window) && fixture() && shell(),
                     "Public caller configuration failed");
    };
    auto stateMatches = [&](QJsonObject expected, const QString &step) {
        expected.remove("step");
        const auto actual = chartMap(fixture(), "snapshot");
        if (actual != expected) {
            qCritical("AdminShell state %s: expected %s actual %s", qPrintable(step),
                QJsonDocument(expected).toJson(QJsonDocument::Compact).constData(),
                QJsonDocument(actual).toJson(QJsonDocument::Compact).constData());
            return check(false, "Native geometry or binding state differs");
        }
        return true;
    };
    QJsonArray layouts, histories, boundaries;
    int geometry = 0, historyStates = 0;
    for (const auto &entry : native["profiles"].toArray()) {
        const auto row = entry.toObject();
        if (!configure(row) || !stateMatches(row["state"].toObject(), row["name"].toString())) return;
        auto record = chartMap(fixture(), "snapshot");
        record["name"] = row["name"];
        if (!prefix.isEmpty()) {
            const auto path = prefix + "-" + row["name"].toString() + ".png";
            if (!check(!QFile::exists(path), "Body capture exists")) return;
            auto grab = fixture()->grabToImage();
            if (!check(bool(grab), "Body capture unavailable")) return;
            QElapsedTimer timer; timer.start();
            while (grab->image().isNull() && timer.elapsed() < 5000) QTest::qWait(10);
            const auto image = grab->image();
            if (!check(!image.isNull() && image.width() == qRound(fixture()->width() * window->devicePixelRatio())
                       && image.height() == qRound(fixture()->height() * window->devicePixelRatio())
                       && image.save(path), "Raw body capture failed")) return;
            record["capture"] = QFileInfo(path).fileName();
            record["pixelWidth"] = image.width(); record["pixelHeight"] = image.height();
        }
        layouts.append(record); ++geometry;
    }
    for (const auto &entry : native["histories"].toArray()) {
        const auto history = entry.toObject();
        QJsonObject config{{"definition", history["definition"]}, {"initial", history["initial"]}, {"dark", parser.isSet("dark")}};
        if (!configure(config, history["owner"].toString())) return;
        QJsonArray states;
        for (const auto &entryState : history["states"].toArray()) {
            const auto expected = entryState.toObject(); const auto step = expected["step"].toString();
            if (!check(QMetaObject::invokeMethod(window, "applyStep", Q_ARG(QVariant, step))
                       && waitForShapeFrame(window), "Native history step failed") || !stateMatches(expected, step)) return;
            auto actual = chartMap(fixture(), "snapshot"); actual["step"] = step;
            states.append(actual); ++historyStates;
        }
        histories.append(QJsonObject{{"owner", history["owner"]}, {"initial", history["initial"]}, {"states", states}});
    }
    const auto base = native["profiles"].toArray().first().toObject()["definition"].toObject();
    for (const auto &entry : native["boundaries"].toArray()) {
        const auto row = entry.toObject(); auto definition = base; definition["columnWidth"] = row["columnWidth"];
        if (!configure(QJsonObject{{"definition", definition}, {"initial", row["initial"]}, {"dark", parser.isSet("dark")}}, "ignore")) return;
        if (!check(QMetaObject::invokeMethod(shell(), "setDividerPosition", Q_ARG(double, row["requestedPosition"].toDouble()))
                   && waitForShapeFrame(window), "Divider action failed")) return;
        const auto actual = chartMap(fixture(), "snapshot");
        const auto pane = row["after"].toArray().first().toObject();
        if (!check(actual["displayedNavigation"].toBool() == !pane["collapsed"].toBool()
                   && actual["columnWidth"] == pane["width"] && actual["navigation"] == row["navigation"]
                   && actual["requests"] == row["requests"], "Fresh native divider state differs")) return;
        boundaries.append(QJsonObject{{"columnWidth",row["columnWidth"]}, {"initial",row["initial"]},
            {"requestedPosition",row["requestedPosition"]}, {"actual",actual}});
    }
    QJsonObject config{{"definition",base},{"initial",true},{"dark",parser.isSet("dark")}};
    if (!configure(config, "ignore")) return;
    auto toolbar = shell()->property("toolbarItem").value<QQuickItem *>();
    auto visibilityButton = toolbar ? toolbar->property("visibilityButton").value<QQuickItem *>() : nullptr;
    auto requestButton = toolbar ? toolbar->property("requestButton").value<QQuickItem *>() : nullptr;
    if (!check(toolbar && visibilityButton && requestButton && toolbar->window() == window, "Hosted toolbar missing")) return;
    const QPointer<QQuickItem> side(shell()->property("sidebarItem").value<QQuickItem *>());
    const QPointer<QQuickItem> head(shell()->property("headerItem").value<QQuickItem *>());
    const QPointer<QQuickItem> content(shell()->property("contentSlotItem").value<QQuickItem *>());
    auto click = [&](QQuickItem *item) {
        QTest::mouseClick(window, Qt::LeftButton, Qt::NoModifier,
            item->mapToScene(QPointF(item->width()/2,item->height()/2)).toPoint());
        return check(waitForShapeFrame(window), "Toolbar result frame missing");
    };
    if (!click(visibilityButton) || !check(!shell()->property("displayedNavigation").toBool()
        && fixture()->property("navigation").toBool(), "Ignoring owner lost caller/display distinction")) return;
    if (!click(requestButton) || !check(chartMap(fixture(),"snapshot")["requests"].toArray() == QJsonArray{false,false},
                                      "Explicit toolbar action did not toggle caller value")) return;
    if (!click(visibilityButton) || !check(shell()->property("displayedNavigation").toBool()
        && chartMap(fixture(),"snapshot")["requests"].toArray() == QJsonArray{false,false,true}, "Native visibility toggle failed")) return;
    if (!check(side && head && content && shell()->property("sidebarItem").value<QQuickItem *>() == side
        && shell()->property("headerItem").value<QQuickItem *>() == head
        && shell()->property("contentSlotItem").value<QQuickItem *>() == content, "Caller identity changed")) return;
    shell()->setEnabled(false);
    if (!click(requestButton) || !check(!visibilityButton->isEnabled() && !requestButton->isEnabled()
        && chartMap(fixture(),"snapshot")["requests"].toArray() == QJsonArray{false,false,true}, "Disabled toolbar accepted input")) return;
    if (!configure(config)) return;
    toolbar = shell()->property("toolbarItem").value<QQuickItem *>();
    visibilityButton = toolbar->property("visibilityButton").value<QQuickItem *>();
    requestButton = toolbar->property("requestButton").value<QQuickItem *>();
    window->requestActivate();
    if (!check(QTest::qWaitForWindowActive(window, 5000), "Keyboard test window did not become active")) return;
    visibilityButton->forceActiveFocus(Qt::TabFocusReason);
    QTest::keyClick(window, Qt::Key_Tab);
    if (!check(waitForShapeFrame(window) && requestButton->hasActiveFocus(), "Toolbar tab order failed")) return;
    QTest::keyClick(window, Qt::Key_Space);
    if (!check(waitForShapeFrame(window) && !fixture()->property("navigation").toBool(), "Space action failed")) return;
    QTest::keyClick(window, Qt::Key_S, Qt::MetaModifier | Qt::ControlModifier);
    if (!check(waitForShapeFrame(window) && fixture()->property("navigation").toBool(), "Window shortcut failed")) return;
    int interfaces = 0;
    for (auto button : {visibilityButton, requestButton}) {
        auto accessible = QAccessible::queryAccessibleInterface(button);
        const auto name = button == visibilityButton ? QString("Toggle Sidebar") : QString("Hide navigation");
        if (!check(accessible && accessible->role() == QAccessible::Button && accessible->text(QAccessible::Name) == name,
                   "Qt toolbar accessibility failed")) return;
        ++interfaces;
    }
    if (!check(geometry == 80 && historyStates == 160 && boundaries.size() == 168, "Native matrix incomplete")) return;
    QJsonObject result{{"reference",native["reference"]},{"fixture","admin-shell"},{"qt",qVersion()},
        {"platform",QGuiApplication::platformName()},{"dpr",window->devicePixelRatio()},{"textScale",textScale},
        {"structuralChecks","passed"},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},
        {"width",window->width()},{"height",window->height()},{"appearance",parser.isSet("dark") ? "dark" : "light"},
        {"nativeLayouts",geometry},{"nativeHistoryStates",historyStates},{"nativeDividerCases",boundaries.size()},
        {"layouts",layouts},{"histories",histories},{"boundaries",boundaries},{"qtToolbarPointerActions",4},
        {"qtCallerIdentityRetained",true},{"qtKeyboardActivation",true},{"qtShortcutActivation",true},
        {"qtAccessibilityInterfaces",interfaces},{"nativeToolbarEquivalentVerified",false},{"nativeKeyboardEquivalentVerified",false},
        {"nativeRasterAccepted",false},{"physicalDisplay",false},{"physicalInput",false},{"readerAcceptance",false},{"accepted",false}};
    if (!prefix.isEmpty()) {
        QFile output(prefix + ".json");
        if (!check(output.open(QIODevice::WriteOnly | QIODevice::NewOnly), "Report cannot be written")) return;
        output.write(QJsonDocument(result).toJson());
    }
    if (parser.isSet("evidence")) {
        if (!check(window->grabWindow().save(prefix + ".png"), "Window evidence capture failed")) return;
        auto timer = new QTimer(&app);
        QObject::connect(timer,&QTimer::timeout,&app,[&app,prefix]{if(QFile::exists(prefix+".captured"))app.exit(0);});
        timer->start(100); QTimer::singleShot(10000,&app,[&app]{app.exit(93);});
    } else app.exit(0);
    qInfo("AdminShell: %d native layouts, %d native history states, %d divider cases; Qt toolbar input and accessibility passed; mirror acceptance pending",
          geometry, historyStates, int(boundaries.size()));
}

#pragma once
#include <QQuickItemGrabResult>
#include <QElapsedTimer>
#include <QFileInfo>

static void runMobileShellConsumer(QQuickWindow *window, QGuiApplication &app,
                                  const QCommandLineParser &parser, double textScale) {
    auto check = [&](bool value, const char *message) {
        if (!value) { qCritical("MobileShell: %s", message); app.exit(99); }
        return value;
    };
    QFile file(":/avelino/fixtures/native-mobile-shell-witnesses.json");
    if (!check(file.open(QIODevice::ReadOnly), "Native slot witnesses missing")) return;
    const auto native = QJsonDocument::fromJson(file.readAll()).object();
    if (!check(native["reference"] == "fe8a1d462fbd793d883fb92086a16aa2947e32c9"
               && native["profiles"].toArray().size() == 72, "Native slot matrix invalid")) return;
    QFile inputFile(":/avelino/fixtures/native-mobile-shell-input-witnesses.json");
    if (!check(inputFile.open(QIODevice::ReadOnly), "Native input witnesses missing")) return;
    const auto inputs = QJsonDocument::fromJson(inputFile.readAll()).object();
    if (!check(inputs["histories"].toArray().size() == 3 && inputs["accepted"] == false,
               "Native input histories invalid")) return;
    const auto prefix = parser.isSet("evidence") ? parser.value("evidence") : parser.value("mobile-shell-report");
    if (!prefix.isEmpty()) {
        if (!check(!QFile::exists(prefix + ".json"), "Evidence path exists")) return;
        QDir().mkpath(QFileInfo(prefix).absolutePath());
    }
    auto fixture = window->property("primaryFixture").value<QQuickItem *>();
    auto shell = fixture ? fixture->property("shell").value<QQuickItem *>() : nullptr;
    auto toolbar = fixture ? fixture->property("toolbarItem").value<QQuickItem *>() : nullptr;
    if (!check(fixture && shell && toolbar, "Public shell or hosted toolbar missing")) return;
    auto configure = [&](QJsonObject value) {
        return check(QMetaObject::invokeMethod(window, "configure", Q_ARG(QVariant, value.toVariantMap()))
                     && waitForShapeFrame(window), "Caller configuration failed");
    };
    auto segment = [&](int index) {
        QQuickItem *item = nullptr;
        QMetaObject::invokeMethod(toolbar, "segmentAt", Q_RETURN_ARG(QQuickItem *, item), Q_ARG(int, index));
        return item;
    };
    auto click = [&](int index) {
        auto button = segment(index);
        if (!check(button && button->isEnabled(), "Actual toolbar input unavailable")) return false;
        QTest::mouseClick(window, Qt::LeftButton, Qt::NoModifier,
                          button->mapToScene(QPointF(button->width()/2, button->height()/2)).toPoint());
        return check(waitForShapeFrame(window), "Pointer result frame missing");
    };
    QJsonArray layouts, histories;
    int geometry = 0, stateChecks = 0, pointerActions = 0;
    for (const auto &entry : native["profiles"].toArray()) {
        const auto row = entry.toObject();
        if (row["dark"].toBool() != parser.isSet("dark") || row["dpr"].toDouble() != window->devicePixelRatio()) continue;
        if (!configure(row)) return;
        const auto snapshot = chartMap(fixture, "snapshot");
        if (snapshot["frames"] != row["frames"]) {
            qCritical("MobileShell frames %s: expected %s actual %s",qPrintable(row["name"].toString()),
                      QJsonDocument(row["frames"].toObject()).toJson(QJsonDocument::Compact).constData(),
                      QJsonDocument(snapshot["frames"].toObject()).toJson(QJsonDocument::Compact).constData());
            check(false,"Native slot frames differ");return;
        }
        QJsonObject record{{"name", row["name"]}, {"frames", snapshot["frames"]}, {"geometryPassed", true}};
        if (!prefix.isEmpty()) {
            const QString path = prefix + "-" + row["name"].toString() + ".png";
            if (!check(!QFile::exists(path), "Capture path exists")) return;
            // The integer client parent supplies an unscaled device-pixel grid.
            // Item::grabToImage() truncates a fractional item's logical extent.
            // Preserve this raw parent image and retain every pixel of the
            // native caller viewport; never resize either comparison input.
            const auto parent = fixture->parentItem();
            const auto origin = parent ? fixture->mapToItem(parent,QPointF()) : QPointF(-1,-1);
            if(!check(parent && origin==QPointF(),"Body capture parent does not match caller origin"))return;
            auto grab = parent->grabToImage();
            if (!check(bool(grab), "Body capture unavailable")) return;
            QElapsedTimer timer; timer.start();
            while (grab->image().isNull() && timer.elapsed() < 5000) QTest::qWait(10);
            const auto original=grab->image();
            const QRect viewport(0,0,row["pixelWidth"].toInt(),row["pixelHeight"].toInt());
            const auto overscan=prefix+"-"+row["name"].toString()+"-overscan.png";
            if (!check(!original.isNull() && original.rect().contains(viewport)
                       && !QFile::exists(overscan) && original.save(overscan)
                       && original.copy(viewport).save(path), "Body capture failed")) return;
            record["capture"] = QFileInfo(path).fileName();
            record["overscanCapture"] = QFileInfo(overscan).fileName();
            record["captureViewport"] = QJsonObject{{"x",0},{"y",0},{"width",viewport.width()},{"height",viewport.height()}};
            record["pixelWidth"] = viewport.width(); record["pixelHeight"] = viewport.height();
        }
        layouts.append(record); ++geometry;
    }
    if (!check(geometry == 18, "Incomplete native geometry profile")) return;
    QJsonObject configuration{{"width",360},{"height",240},{"header",36},{"footer",24},
        {"content","flex"},{"hiddenHeader",false},{"dark",parser.isSet("dark")},
        {"tabs",QJsonArray{QJsonObject{{"value","news"},{"label","News"},{"systemImage","newspaper"},{"badge",8}},
                           QJsonObject{{"value","saved"},{"label","Saved"},{"systemImage","bookmark"},{"disabled",true},{"accessibilityLabel","Stored items"}}}}};
    for (const auto &entry : inputs["histories"].toArray()) {
        const auto history = entry.toObject();
        shell->setEnabled(true);
        if (!configure(configuration)) return;
        if (!check(QMetaObject::invokeMethod(window,"resetOwner",Q_ARG(QVariant,history["owner"].toString()))
                   && waitForShapeFrame(window), "Owner reset failed")) return;
        QJsonArray steps;
        for (const auto &value : history["history"].toArray()) {
            const auto expected = value.toObject(); const auto step = expected["step"].toString();
            if (step.endsWith("-immediate") || step == "right-arrow") continue;
            if (step.startsWith("action-") && step.endsWith("-settled")) {
                if (!click(step.split('-')[1].toInt())) return;
                ++pointerActions;
            } else if (step == "before-disable") {
                if (!click(1)) return; ++pointerActions;
            } else if (step == "flush-pending") {
                if (!check(QMetaObject::invokeMethod(window,"applyPending"), "Pending writeback failed")) return;
            } else if (step == "external-news" || step == "external-unknown") {
                shell->setEnabled(true);
                if (!check(QMetaObject::invokeMethod(window,"externalSelection",Q_ARG(QVariant,expected["selection"].toString())),
                           "Explicit caller selection failed")) return;
            } else if (step == "parent-disabled") shell->setEnabled(false);
            else if (step != "initial") { check(false,"Unexpected native history step"); return; }
            if (!check(waitForShapeFrame(window), "History frame missing")) return;
            auto actual = chartMap(window,"ownerState");
            actual["selectedSegment"] = toolbar->property("displayedIndex").toInt();
            actual["enabled"] = toolbar->isEnabled(); actual["step"] = step;
            if (!chartSubset(actual,expected)) {
                qCritical("MobileShell history %s: expected %s actual %s",qPrintable(step),
                          QJsonDocument(expected).toJson(QJsonDocument::Compact).constData(),
                          QJsonDocument(actual).toJson(QJsonDocument::Compact).constData());
                check(false,"Native caller/display history differs");return;
            }
            steps.append(actual); ++stateChecks;
        }
        histories.append(QJsonObject{{"owner",history["owner"]},{"steps",steps}});
    }
    shell->setEnabled(true);
    if (!check(QMetaObject::invokeMethod(window,"resetOwner",Q_ARG(QVariant,QString("echo")))
               && waitForShapeFrame(window), "Keyboard owner reset failed")) return;
    auto first = segment(0);
    if (!check(first, "Keyboard segment missing")) return;
    first->forceActiveFocus();
    QTest::keyClick(window, Qt::Key_Space);
    if (!check(waitForShapeFrame(window) && chartMap(window,"ownerState")["requests"].toArray().size()==1,
               "Qt Space activation failed")) return;
    int interfaces = 0;
    for (int i=0; i<2; ++i) {
        auto item = segment(i); auto accessible = item ? QAccessible::queryAccessibleInterface(item) : nullptr;
        if (!check(accessible && accessible->role()==QAccessible::RadioButton
                   && accessible->text(QAccessible::Name)==(i==0 ? "News":"Saved")
                   && accessible->state().checked==item->property("selected").toBool(), "Qt segment accessibility differs")) return;
        ++interfaces;
    }
    QJsonObject result{{"reference",native["reference"]},{"fixture","mobile-shell"},{"structuralChecks","passed"},
        {"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},
        {"width",window->width()},{"height",window->height()},{"appearance",parser.isSet("dark") ? "dark":"light"},
        {"dpr",window->devicePixelRatio()},{"textScale",textScale},{"geometryPassed",geometry},{"layouts",layouts},
        {"nativeOwnerHistories",histories},{"nativeStateChecks",stateChecks},{"pointerActions",pointerActions},
        {"qtSpaceActivation",true},{"qtAccessibilityInterfaces",interfaces},{"nativeKeyboardEquivalentVerified",false},
        {"nativeToolbarRasterAccepted",false},{"physicalDisplay",false},{"readerAcceptance",false},{"accepted",false},
        {"nativeRasterAcceptance","pending"},{"nativeAccessibilityAcceptance","unobserved"},{"physicalInputAcceptance","pending"}};
    if(parser.isSet("evidence") && !check(window->grabWindow().save(prefix+".png"),"Displayed window capture failed"))return;
    if (!prefix.isEmpty()) {
        QFile output(prefix+".json");
        if (!check(output.open(QIODevice::WriteOnly|QIODevice::NewOnly), "Report path exists or cannot be opened")) return;
        output.write(QJsonDocument(result).toJson());
    }
    qInfo("MobileShell: %d native layouts, %d native state checks, %d pointer actions, two Qt accessibility interfaces; mirror acceptance pending",geometry,stateChecks,pointerActions);
    if(parser.isSet("evidence")) {
        auto timer=new QTimer(&app);
        QObject::connect(timer,&QTimer::timeout,&app,[&app,prefix]{if(QFile::exists(prefix+".captured"))app.exit(0);});
        timer->start(100);
        QTimer::singleShot(10000,&app,[&app]{app.exit(93);});
        return;
    }
    app.exit(0);
}

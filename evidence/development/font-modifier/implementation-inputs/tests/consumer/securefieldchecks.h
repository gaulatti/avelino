#pragma once
#include <QClipboard>

static void runSecureFieldConsumer(QQuickWindow *window, QGuiApplication &app,
                                   const QCommandLineParser &parser, double textScale) {
    auto item=[window](const QString &name) { return findVisualItem(window->contentItem(),name); };
    const auto field=item("secureField"), disabled=item("disabledSecureField");
    const auto next=item("secureNextField"), narrow=item("narrowSecureField");
    const auto action=field ? findVisualItem(field,"bleeckerSecureReveal") : nullptr;
    auto check=[&app](bool result,const char *message) {
        if (!result) { qCritical("Installed secure field: %s",message); app.exit(100); }
        return result;
    };
    if (!check(field && disabled && next && narrow && action,"missing component")) return;
    auto click=[window](QQuickItem *target,qreal x=-1) {
        QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,
            target->mapToScene(QPointF(x<0 ? target->width()/2 : x,target->height()/2)).toPoint());
        QTest::qWait(40);
    };
    auto typeValue=[window](const QString &value) {
        for (const auto character : value) QTest::keyClick(window,Qt::Key(character.toUpper().unicode()));
    };
    auto accessible=QAccessible::queryAccessibleInterface(field);
    auto actionAccessible=QAccessible::queryAccessibleInterface(action);
    if (!accessible || accessible->role()!=QAccessible::EditableText || !accessible->state().passwordEdit
        || accessible->text(QAccessible::Name)!="Passphrase" || !actionAccessible
        || actionAccessible->role()!=QAccessible::Button || actionAccessible->text(QAccessible::Name)!="Show contents") {
        qCritical("Secure interfaces: editor role=%d password=%d named=%d; button role=%d named=%d",
            accessible ? int(accessible->role()) : -1, accessible ? int(accessible->state().passwordEdit) : -1,
            accessible ? int(accessible->text(QAccessible::Name)=="Passphrase") : -1,
            actionAccessible ? int(actionAccessible->role()) : -1,
            actionAccessible ? int(actionAccessible->text(QAccessible::Name)=="Show contents") : -1);
    }
    const auto font=field->property("font").value<QFont>();
    if (!check(field->height()==40 && font.family()=="Encode Sans" && font.weight()==QFont::Normal
        && font.pointSizeF()==window->property("expectedFontPointSize").toDouble(),"source geometry/font")) return;
    if (!check(accessible && accessible->role()==QAccessible::EditableText && accessible->state().passwordEdit
        && accessible->text(QAccessible::Name)=="Passphrase" && actionAccessible
        && actionAccessible->role()==QAccessible::Button && actionAccessible->text(QAccessible::Name)=="Show contents",
        "masked accessibility interface")) return;
    click(field,20); typeValue("sample");
    if (!check(window->property("entry").toString()=="sample" && window->property("edits").toInt()==6
        && field->property("displayText").toString()!="sample" && accessible->text(QAccessible::Value)!="sample",
        "masked editing or accessible value")) return;
    auto clipboard=QGuiApplication::clipboard();
    clipboard->setText("clipboard sentinel");
    QMetaObject::invokeMethod(field,"selectAll"); QTest::keyClick(window,Qt::Key_C,Qt::ControlModifier);
    if (!check(clipboard->text()=="clipboard sentinel","masked copy exported text")) return;
    click(action);
    if (!check(field->property("revealed").toBool() && field->property("text").toString()=="sample"
        && field->property("displayText").toString()=="sample" && !accessible->state().passwordEdit
        && accessible->text(QAccessible::Value)=="sample" && actionAccessible->text(QAccessible::Name)=="Hide contents",
        "revealed value or accessibility state")) return;
    field->forceActiveFocus(); QMetaObject::invokeMethod(field,"selectAll");
    QTest::keyClick(window,Qt::Key_C,Qt::ControlModifier);
    if (!check(clipboard->text()=="sample","revealed normal editing copy")) return;
    typeValue("updated"); click(action);
    if (!check(window->property("entry").toString()=="updated" && !field->property("revealed").toBool()
        && field->property("displayText").toString()!="updated" && accessible->state().passwordEdit,
        "hide after editing")) return;
    const int edits=window->property("edits").toInt();
    window->setProperty("entry","External entry");
    field->setEnabled(false); click(action); typeValue("x");
    if (!check(field->property("text").toString()=="External entry" && !field->property("revealed").toBool()
        && window->property("edits").toInt()==edits && !action->isEnabled(),"external value or disabled input")) return;
    field->setEnabled(true); field->forceActiveFocus(Qt::TabFocusReason);
    QTest::keyClick(window,Qt::Key_Tab);
    if (!check(action->hasActiveFocus() && action->property("visualFocus").toBool(),"reveal keyboard focus")) return;
    QTest::keyClick(window,Qt::Key_Space); QTest::keyClick(window,Qt::Key_Tab);
    if (!check(field->property("revealed").toBool() && next->hasActiveFocus() && !disabled->hasActiveFocus(),
        "keyboard reveal or disabled traversal")) return;
    typeValue("continued");
    if (!check(next->property("text").toString()=="continued" && narrow->height()==40
        && narrow->property("contentWidth").toDouble()>narrow->width()-58,"subsequent editing or narrow content")) return;
    qInfo("Installed secure field: caller value, masking, reveal, disabled input, clipboard, keyboard focus and real Qt accessibility interfaces passed");
    if (!parser.isSet("evidence")) { app.exit(0); return; }
    const auto path=parser.value("evidence");
    if (!window->grabWindow().save(path+".png")) { app.exit(101); return; }
    QJsonObject record{{"fixture","secure-field"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},
        {"compiler",QString::fromUtf8(__VERSION__)},{"width",window->width()},{"height",window->height()},
        {"dpr",window->devicePixelRatio()},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},
        {"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},{"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},
        {"appearance",parser.isSet("dark") ? "dark" : "light"},{"textScale",textScale},
        {"inputMethod","QTest synthetic in-process pointer and keyboard events"},
        {"windowCaptureMethod","QQuickWindow::grabWindow; full session captured separately"},
        {"secureFieldChecks","passed"},{"maskingChecks","passed"},{"clipboardChecks","passed"},
        {"focusChecks","passed"},{"qtAccessibilityChecks","passed"},{"revealed",field->property("revealed").toBool()},
        {"sourceHeight",field->height()},{"fontPointSize",font.pointSizeF()},
        {"fontScalePolicy","fixed 14 logical pixels; source has no text-scale multiplier"},
        {"symbolAcceptance","pending; original eye and slashed-eye geometry has no approved source equivalence"},
        {"accessibilityAcceptance","pending; interface queries do not prove screen-reader output"}};
    QFile file(path+".json");
    if (!file.open(QIODevice::WriteOnly)) { app.exit(102); return; }
    file.write(QJsonDocument(record).toJson()); file.close();
    auto timer=new QTimer(&app);
    QObject::connect(timer,&QTimer::timeout,&app,[&app,path] { if (QFile::exists(path+".captured")) app.exit(0); });
    timer->start(100); QTimer::singleShot(10000,&app,[&app] { app.exit(103); });
}

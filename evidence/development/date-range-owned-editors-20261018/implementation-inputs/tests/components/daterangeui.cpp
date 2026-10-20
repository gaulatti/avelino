#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QQuickItem>
#include <QQuickWindow>
#include <QJSValue>
#include <QPointer>
#include <QtTest>

namespace {
struct Fixture {
    QQmlApplicationEngine engine;
    QQuickWindow *window=nullptr;
    QQuickItem *picker=nullptr;
    Fixture(){
        engine.addImportPath(QStringLiteral(AVELINO_DATE_IMPORT_PATH));
        engine.load(QUrl("qrc:/date-range-tests/date-range-fixture.qml"));
        if(engine.rootObjects().size()!=1)return;
        window=qobject_cast<QQuickWindow*>(engine.rootObjects().first());
        if(window)picker=window->property("picker").value<QQuickItem*>();
        if(window){window->show();window->requestActivate();if(!QTest::qWaitForWindowExposed(window))window=nullptr;}
    }
    QQuickItem *field(const char *name){return picker->property(name).value<QQuickItem*>();}
    int requests()const{const auto value=window->property("requests");return (value.metaType().id()==qMetaTypeId<QJSValue>() ? value.value<QJSValue>().toVariant():value).toList().size();}
};
void click(QQuickItem *item){
    QTest::mouseClick(item->window(),Qt::LeftButton,Qt::NoModifier,item->mapToScene(QPointF(item->width()/2,item->height()/2)).toPoint());
}
QQuickItem *visual(QQuickItem *root,const QString &name){
    if(root->objectName()==name)return root;
    for(auto child:root->childItems())if(auto found=visual(child,name))return found;
    return nullptr;
}
}
class DateRangeUiTests:public QObject {
    Q_OBJECT
private slots:
    void fieldKeyboardOwners();
    void graphicalPreviewAndCommit();
    void overlayInputWindow();
    void disabledAndCallerOverflow();
    void rangeEditorLifetime();
    void delayedOwnerAndExternalUpdate();
    void ownerRemovalDuringRequest();
    void independentEndpointsAndExactBounds();
    void numericYearAfterDayEdit();
};
void DateRangeUiTests::fieldKeyboardOwners(){
    for(const QString policy:{"echo","ignore","delay"}){
        Fixture f;QVERIFY(f.window &&f.picker);f.window->setProperty("ownerPolicy",policy);
        auto input=f.field("startInput");QVERIFY(input);input->forceActiveFocus(Qt::OtherFocusReason);
        QTRY_VERIFY(input->hasActiveFocus());
        QTest::keyClick(input->window(),Qt::Key_Right);QTest::keyClick(input->window(),Qt::Key_Right);
        QTest::keyClick(input->window(),Qt::Key_Up);
        auto field=f.field("startField");QVERIFY(field);
        QTRY_VERIFY(field->property("bufferValue").toDouble()==1741536000.625);
        QVERIFY(f.window->property("sourceStart").toDouble()==(policy=="echo" ? 1741536000.625:1710000000.625));
        QVERIFY(f.window->property("sourceEnd").toDouble()==1710864000.125);
        QCOMPARE(f.requests(),1);
    }
}
void DateRangeUiTests::graphicalPreviewAndCommit(){
    Fixture f;QVERIFY(f.window&&f.picker);f.window->setProperty("pickerStyle","graphical");
    auto calendar=f.field("startInput");QVERIFY(calendar);
    QTRY_VERIFY(calendar->isVisible() &&calendar->height()==148);
    auto day=visual(calendar,"bleeckerDateDay-16");QVERIFY(day);click(day);
    QTRY_VERIFY(f.window->property("sourceStart").toDouble()==1710259200.625);
    QCOMPARE(f.requests(),2);
    QTRY_VERIFY(calendar->hasActiveFocus());
    QTest::keyClick(calendar->window(),Qt::Key_Right);
    QTRY_VERIFY(f.field("startField")->property("bufferValue").toDouble()==1710345600);
    QVERIFY(f.window->property("sourceStart").toDouble()==1710259200.625);QCOMPARE(f.requests(),2);
    QTest::keyClick(calendar->window(),Qt::Key_Space);
    QTRY_VERIFY(f.window->property("sourceStart").toDouble()==1710345600);QCOMPARE(f.requests(),3);
}
void DateRangeUiTests::overlayInputWindow(){
    Fixture f;QVERIFY(f.window&&f.picker);f.window->setProperty("pickerStyle","stepperField");
    auto input=f.field("startInput");QVERIFY(input);click(input);
    auto field=f.field("startField");QVERIFY(field);
    auto panel=field->property("calendarPanel").value<QObject*>();QVERIFY(panel);
    QTRY_VERIFY(panel->property("visible").toBool());
    QTRY_VERIFY(input->window()!=f.window);
    QTRY_VERIFY(input->hasActiveFocus());
    QTest::keyClick(input->window(),Qt::Key_Up);
    QTRY_VERIFY(f.window->property("sourceStart").toDouble()==1741536000.625);
    QCOMPARE(f.requests(),2);
    QTest::keyClick(input->window(),Qt::Key_Escape);
    QTRY_VERIFY(!panel->property("visible").toBool());
}
void DateRangeUiTests::disabledAndCallerOverflow(){
    Fixture f;QVERIFY(f.window&&f.picker);f.window->setProperty("callerWidth",100);
    auto body=f.field("presentationItem");QVERIFY(body);
    QTRY_VERIFY(body->width()>f.picker->width());
    QVERIFY(body->x()==(f.picker->width()-body->width())/2);
    f.window->setProperty("disabled",true);auto input=f.field("startInput");QVERIFY(input);click(input);
    QTest::keyClick(f.window,Qt::Key_Up);QTest::qWait(20);
    QCOMPARE(f.requests(),0);QVERIFY(f.window->property("sourceStart").toDouble()==1710000000.625);
}

void DateRangeUiTests::rangeEditorLifetime(){
    Fixture f;QVERIFY(f.window&&f.picker);
    QPointer<QQuickItem> initial=f.field("startInput");QVERIFY(initial);
    f.window->setProperty("bounds",QVariantMap{{"lower",1709251200.0},{"upper",1711843200.0}});
    QTRY_VERIFY(initial.isNull());
    QPointer<QQuickItem> restricted=f.field("startInput");QVERIFY(restricted);
    f.window->setProperty("bounds",QVariantMap{{"lower",1709251200.0},{"upper",1711756800.0}});
    QTest::qWait(1);QVERIFY(restricted);QCOMPARE(f.field("startInput"),restricted.data());
    f.window->setProperty("bounds",QVariant::fromValue(nullptr));
    QTRY_VERIFY(restricted.isNull());QVERIFY(f.field("startInput"));QCOMPARE(f.requests(),0);
}
void DateRangeUiTests::delayedOwnerAndExternalUpdate(){
    Fixture f;QVERIFY(f.window&&f.picker);f.window->setProperty("ownerPolicy","delay");
    auto input=f.field("startInput");input->forceActiveFocus(Qt::OtherFocusReason);
    QTest::keyClick(input->window(),Qt::Key_Up);
    QTRY_VERIFY(f.field("startField")->property("bufferValue").toDouble()==1712678400.625);
    QVERIFY(f.window->property("sourceStart").toDouble()==1710000000.625);QCOMPARE(f.requests(),1);
    auto value=f.window->property("pending");
    auto pending=(value.metaType().id()==qMetaTypeId<QJSValue>() ? value.value<QJSValue>().toVariant():value).toMap();
    QVERIFY(pending["start"].toDouble()==1712678400.625);
    f.window->setProperty("sourceStart",pending["start"]);
    QTRY_VERIFY(f.field("startField")->property("bufferValue").toDouble()==1712678400.625);
    f.window->setProperty("sourceStart",1710086400.25);
    QTRY_VERIFY(f.field("startField")->property("bufferValue").toDouble()==1710086400.25);
    QCOMPARE(f.requests(),1);
}
void DateRangeUiTests::ownerRemovalDuringRequest(){
    Fixture f;QVERIFY(f.window&&f.picker);f.window->setProperty("removeOnRequest",true);
    QPointer<QQuickItem> picker=f.picker;
    auto input=f.field("startInput");input->forceActiveFocus(Qt::OtherFocusReason);
    QTest::keyClick(input->window(),Qt::Key_Up);
    QTRY_VERIFY(picker.isNull());QCOMPARE(f.requests(),1);
}

void DateRangeUiTests::independentEndpointsAndExactBounds(){
    Fixture f;QVERIFY(f.window&&f.picker);
    auto input=f.field("endInput");input->forceActiveFocus(Qt::OtherFocusReason);
    QTest::keyClick(input->window(),Qt::Key_Right);QTest::keyClick(input->window(),Qt::Key_Right);QTest::keyClick(input->window(),Qt::Key_Down);
    QTRY_VERIFY(f.window->property("sourceEnd").toDouble()==1679241600.125);
    QVERIFY(f.window->property("sourceStart").toDouble()==1710000000.625);QCOMPARE(f.requests(),1);
    f.window->setProperty("bounds",QVariantMap{{"lower",1709251200.0},{"upper",1711843200.0}});
    QTRY_VERIFY(f.field("endField")->property("bufferValue").toDouble()==1709251200.0);
    QVERIFY(f.window->property("sourceEnd").toDouble()==1679241600.125);QCOMPARE(f.requests(),1);
    input=f.field("startInput");input->forceActiveFocus(Qt::OtherFocusReason);
    QTest::keyClick(input->window(),Qt::Key_Right);QTest::keyClick(input->window(),Qt::Key_Right);QTest::keyClick(input->window(),Qt::Key_Up);
    QTRY_VERIFY(f.window->property("sourceStart").toDouble()==1711843200.0);
    QVERIFY(f.window->property("sourceEnd").toDouble()==1679241600.125);QCOMPARE(f.requests(),2);
}
void DateRangeUiTests::numericYearAfterDayEdit(){
    Fixture f;QVERIFY(f.window&&f.picker);auto input=f.field("startInput");input->forceActiveFocus(Qt::OtherFocusReason);
    QTest::keyClick(input->window(),Qt::Key_Right);QTest::keyClick(input->window(),Qt::Key_Right);QTest::keyClick(input->window(),Qt::Key_Up);
    QTest::keyClick(input->window(),Qt::Key_Left);QTest::keyClick(input->window(),Qt::Key_Up);
    QTRY_VERIFY(f.window->property("sourceStart").toDouble()==1741622400.625);
    QTest::keyClick(input->window(),Qt::Key_Right);for(auto key:{Qt::Key_2,Qt::Key_0,Qt::Key_2,Qt::Key_6})QTest::keyClick(input->window(),key);
    QTRY_VERIFY(f.window->property("sourceStart").toDouble()==1773158400.625);
    QVERIFY(f.window->property("sourceEnd").toDouble()==1710864000.125);QCOMPARE(f.requests(),3);
}
QTEST_MAIN(DateRangeUiTests)
#include "daterangeui.moc"

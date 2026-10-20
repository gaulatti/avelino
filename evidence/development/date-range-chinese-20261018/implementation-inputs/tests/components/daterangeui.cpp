#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QQmlError>
#include <QQuickItem>
#include <QQuickWindow>
#include <QJSValue>
#include <QInputMethodEvent>
#include <QPointer>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QtTest>

namespace {
struct Fixture {
    QStringList warnings;
    QQmlApplicationEngine engine;
    QQuickWindow *window=nullptr;
    QQuickItem *picker=nullptr;
    Fixture(){
        QObject::connect(&engine,&QQmlEngine::warnings,&engine,[this](const QList<QQmlError> &errors){for(const auto &error:errors)warnings.append(error.toString());});
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
    void ownerRemovalWhileCommittingTypedField();
    void localeDirectionInsideCallerLayout();
    void nativeChromeProfilesReachOwnedEditors();
    void widthsStayFixedAcrossNativeDates();
    void chinesePresentationReachesOwnedEditors();
    void chineseDayInputMethodCommit();
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
    auto input=f.field("startInput");QVERIFY(input);
    QRectF year;QVERIFY(QMetaObject::invokeMethod(input,"positionToRectangle",Q_RETURN_ARG(QRectF,year),Q_ARG(int,input->property("text").toString().size()-2)));
    QTest::mouseClick(input->window(),Qt::LeftButton,Qt::NoModifier,input->mapToScene(year.center()).toPoint());
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

void DateRangeUiTests::ownerRemovalWhileCommittingTypedField(){
    for(auto ending:{Qt::Key_Up,Qt::Key_Left,Qt::Key_Tab}){
        Fixture f;QVERIFY(f.window&&f.picker);f.window->setProperty("removeOnRequest",true);
        QPointer<QQuickItem> picker=f.picker;auto input=f.field("startInput");input->forceActiveFocus(Qt::OtherFocusReason);
        QTest::keyClick(input->window(),Qt::Key_Right);QTest::keyClick(input->window(),Qt::Key_Right);
        QTest::keyClick(input->window(),Qt::Key_2);QCOMPARE(f.requests(),0);
        QTest::keyClick(input->window(),ending);
        QTRY_VERIFY(picker.isNull());QCOMPARE(f.requests(),1);
        QVERIFY2(f.warnings.isEmpty(),qPrintable(f.warnings.join('\n')));
    }
}

void DateRangeUiTests::localeDirectionInsideCallerLayout(){
    for(const QString locale:{"en_US","ar_EG"})for(const bool rtl:{false,true}){
        Fixture f;QVERIFY(f.window&&f.picker);f.window->setProperty("pickerStyle","stepperField");f.window->setProperty("rtl",rtl);f.window->setProperty("localeName",locale);
        auto input=f.field("startInput");auto stepper=visual(f.field("startField"),"bleeckerDateStepper");QVERIFY(input&&stepper);
        const bool localRtl=locale=="ar_EG";
        QTRY_VERIFY((input->x()>stepper->x())==localRtl);
        QCOMPARE(input->property("horizontalAlignment").toInt(),int(localRtl?Qt::AlignRight:Qt::AlignLeft));
        QCOMPARE(f.picker->property("mirrored").toBool(),rtl);QCOMPARE(f.requests(),0);
        QVERIFY2(f.warnings.isEmpty(),qPrintable(f.warnings.join('\n')));
    }
}
void DateRangeUiTests::nativeChromeProfilesReachOwnedEditors(){
    QFile file(QStringLiteral(NATIVE_DATE_WIDTH_DIRECTORY "/chrome/output/bounds.json"));QVERIFY(file.open(QIODevice::ReadOnly));
    QJsonParseError error;const auto document=QJsonDocument::fromJson(file.readAll(),&error);QCOMPARE(error.error,QJsonParseError::NoError);
    const auto rows=document.object()["rows"].toArray();QCOMPARE(rows.size(),36);int compared=0;
    for(const auto &item:rows){
        const auto row=item.toObject(),configuration=row["configuration"].toObject();
        QJsonArray fields;
        for(const auto &candidate:rows){
            const auto other=candidate.toObject()["configuration"].toObject();
            if(other["locale"]==configuration["locale"]&&other["calendar"]==configuration["calendar"]&&other["controlSize"]==configuration["controlSize"]&&other["pickerStyle"]=="field")fields=candidate.toObject()["editors"].toArray();
        }
        QCOMPARE(fields.size(),2);
        Fixture f;QVERIFY(f.window&&f.picker);
        f.window->setProperty("pickerStyle",configuration["pickerStyle"].toString());
        f.window->setProperty("localeName",configuration["locale"].toString());
        f.picker->setProperty("calendar",configuration["calendar"].toString());
        f.picker->setProperty("controlSize",configuration["controlSize"].toString());
        const auto editors=row["editors"].toArray();QCOMPARE(editors.size(),2);
        for(int index=0;index<2;++index){
            auto field=f.field(index==0?"startField":"endField"),input=f.field(index==0?"startInput":"endInput");
            auto stepper=visual(field,"bleeckerDateStepper");QVERIFY(input&&stepper);
            const auto native=editors[index].toObject()["intrinsic"].toObject(),withoutStepper=fields[index].toObject()["intrinsic"].toObject();
            const auto extraWidth=native["width"].toDouble()-withoutStepper["width"].toDouble();
            QTRY_VERIFY(field->height()==native["height"].toDouble());
            QCOMPARE(input->height(),native["height"].toDouble());
            QCOMPARE(field->width()-input->width(),extraWidth);
            QCOMPARE(stepper->isVisible(),extraWidth>0);
            ++compared;
        }
        QCOMPARE(f.requests(),0);QVERIFY2(f.warnings.isEmpty(),qPrintable(f.warnings.join('\n')));
    }
    QCOMPARE(compared,72);
}
void DateRangeUiTests::widthsStayFixedAcrossNativeDates(){
    QFile file(QStringLiteral(NATIVE_DATE_WIDTH_DIRECTORY "/output/widths.json"));QVERIFY(file.open(QIODevice::ReadOnly));
    QJsonParseError error;const auto document=QJsonDocument::fromJson(file.readAll(),&error);QCOMPARE(error.error,QJsonParseError::NoError);
    const auto contexts=document.object()["contexts"].toArray();QCOMPARE(contexts.size(),23);int compared=0,coldCompared=0;
    const auto configure=[](Fixture &f,const QJsonObject &configuration){
        f.window->setProperty("localeName",configuration["locale"].toString());
        f.window->setProperty("pickerStyle",configuration["pickerStyle"].toString());
        f.picker->setProperty("calendar",configuration["calendar"].toString());
        f.picker->setProperty("timeZone",configuration["timeZone"].toString());
        f.picker->setProperty("controlSize",configuration["controlSize"].toString());
    };
    for(const auto &item:contexts){
        const auto context=item.toObject(),configuration=context["configuration"].toObject();
        Fixture f;QVERIFY(f.window&&f.picker);configure(f,configuration);
        QQuickItem *fields[]={f.field("startField"),f.field("endField")};
        QPointer<QQuickItem> inputs[]={f.field("startInput"),f.field("endInput")};
        const qreal widths[]={fields[0]->width(),fields[1]->width()};
        for(const auto &value:context["updates"].toArray()){
            const auto update=value.toObject();const double date=update["requestedDate"].toDouble();
            f.window->setProperty("sourceStart",date);f.window->setProperty("sourceEnd",date);
            QCoreApplication::processEvents();
            for(int index=0;index<2;++index){
                QVERIFY(fields[index]->property("bufferValue").toDouble()==update["editors"].toArray()[index].toObject()["date"].toDouble());
                QVERIFY2(fields[index]->width()==widths[index],qPrintable(configuration["id"].toString()));
                QCOMPARE(f.field(index==0?"startInput":"endInput"),inputs[index].data());++compared;
            }
        }
        for(const auto &value:context["coldExtremes"].toArray()){
            const auto cold=value.toObject();Fixture fresh;QVERIFY(fresh.window&&fresh.picker);
            fresh.window->setProperty("mounted",false);QCoreApplication::processEvents();
            fresh.window->setProperty("sourceStart",cold["requestedDate"].toDouble());fresh.window->setProperty("sourceEnd",cold["requestedDate"].toDouble());
            fresh.window->setProperty("mounted",true);QCoreApplication::processEvents();fresh.picker=fresh.window->property("picker").value<QQuickItem*>();QVERIFY(fresh.picker);configure(fresh,configuration);
            for(int index=0;index<2;++index){
                auto field=fresh.field(index==0?"startField":"endField");
                QVERIFY2(field->width()==widths[index],qPrintable(configuration["id"].toString()));
                QVERIFY(field->property("bufferValue").toDouble()==cold["editors"].toArray()[index].toObject()["date"].toDouble());++coldCompared;
            }
            QCOMPARE(fresh.requests(),0);QVERIFY2(fresh.warnings.isEmpty(),qPrintable(fresh.warnings.join('\n')));
        }
        QCOMPARE(f.requests(),0);QVERIFY2(f.warnings.isEmpty(),qPrintable(f.warnings.join('\n')));
    }
    QCOMPARE(compared,3696);QCOMPARE(coldCompared,92);
}
void DateRangeUiTests::chinesePresentationReachesOwnedEditors(){
    QFile file(QStringLiteral(NATIVE_DATE_CHINESE_DIRECTORY "/samples/output/samples.json"));QVERIFY(file.open(QIODevice::ReadOnly));
    const auto rows=QJsonDocument::fromJson(file.readAll()).object()["rows"].toArray();QCOMPARE(rows.size(),36);int compared=0;
    for(const auto &value:rows){
        const auto row=value.toObject(),configuration=row["configuration"].toObject();Fixture f;QVERIFY(f.window&&f.picker);
        f.window->setProperty("localeName",configuration["locale"].toString());f.window->setProperty("pickerStyle",configuration["pickerStyle"].toString());
        f.picker->setProperty("calendar","chinese");f.picker->setProperty("controlSize",configuration["controlSize"].toString());
        f.window->setProperty("sourceStart",configuration["start"].toDouble());f.window->setProperty("sourceEnd",configuration["end"].toDouble());
        for(int index=0;index<2;++index){
            auto field=f.field(index==0?"startField":"endField"),input=f.field(index==0?"startInput":"endInput");
            const auto native=row["editors"].toArray()[index].toObject();
            QCOMPARE(QString(input->property("text").toString()).remove(QChar(0x2007)),native["candidateText"].toString());
            QVERIFY(field->property("bufferValue").toDouble()==native["date"].toDouble());++compared;
        }
        QCOMPARE(f.requests(),0);QVERIFY2(f.warnings.isEmpty(),qPrintable(f.warnings.join('\n')));
    }
    QCOMPARE(compared,72);
}
void DateRangeUiTests::chineseDayInputMethodCommit(){
    QFile file(QStringLiteral(NATIVE_DATE_CHINESE_DIRECTORY "/samples/output/samples.json"));QVERIFY(file.open(QIODevice::ReadOnly));
    const auto rows=QJsonDocument::fromJson(file.readAll()).object()["rows"].toArray();int compared=0;
    for(const auto &value:rows){
        const auto row=value.toObject(),configuration=row["configuration"].toObject();
        if(configuration["locale"]!="zh_CN"||configuration["controlSize"]!="regular")continue;
        Fixture f;QVERIFY(f.window&&f.picker);f.window->setProperty("localeName","zh_CN");f.picker->setProperty("calendar","chinese");
        const double initial=configuration["start"].toDouble(),end=configuration["end"].toDouble();
        f.window->setProperty("sourceStart",initial);f.window->setProperty("sourceEnd",end);
        auto field=f.field("startField"),input=f.field("startInput");field->setProperty("selectedSegment",1);input->forceActiveFocus(Qt::OtherFocusReason);QTRY_VERIFY(input->hasActiveFocus());
        QVERIFY(QMetaObject::invokeMethod(field,"restoreSelection"));
        QInputMethodEvent event;event.setCommitString(QString::fromUtf8("初十"));QGuiApplication::sendEvent(input,&event);
        const int day=row["editors"].toArray()[0].toObject()["components"].toObject()["day"].toInt();
        QVERIFY(f.window->property("sourceStart").toDouble()==initial+(10-day)*86400.0);
        QVERIFY(f.window->property("sourceEnd").toDouble()==end);QCOMPARE(f.requests(),1);
        QVERIFY2(f.warnings.isEmpty(),qPrintable(f.warnings.join('\n')));++compared;
    }
    QCOMPARE(compared,3);
}
QTEST_MAIN(DateRangeUiTests)
#include "daterangeui.moc"

#include "daterangetools.h"
#include <QFile>
#include <QFontMetricsF>
#include <QTextLayout>
#include <QGlyphRun>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QtTest>
#include <algorithm>
#include <cmath>

#define EXACT_DATE(actual,expected) do {const double dateActual=(actual),dateExpected=(expected); \
    QVERIFY2(dateActual==dateExpected,qPrintable(QStringLiteral("Exact date mismatch: %1 != %2") \
        .arg(dateActual,0,'g',17).arg(dateExpected,0,'g',17)));} while(false)

namespace {
QJsonObject read(const QString &path) {
    QFile file(path);
    if(!file.open(QIODevice::ReadOnly))qFatal("Cannot read native date evidence: %s",qPrintable(path));
    QJsonParseError error;const auto data=QJsonDocument::fromJson(file.readAll(),&error);
    if(error.error!=QJsonParseError::NoError || !data.isObject())qFatal("Invalid native date evidence");
    return data.object();
}
QVariant range(const QJsonObject &configuration) {
    if(!configuration.contains("lower"))return {};
    return QVariantMap{{"lower",configuration.value("lower").toDouble()},{"upper",configuration.value("upper").toDouble()}};
}
}
class DateRangeToolsTests:public QObject {
    Q_OBJECT
private slots:
    void sourceDateConstructionAndDisplayClamp();
    void sourceCalendarHistoryComponents();
    void nativeInputArithmetic();
    void localizedSegmentBoundaries();
    void ownedCalendarGrid();
    void editableFieldParsing();
    void editorPresentationAndRoundTrip();
    void nativeNumericFontContract();
    void nativeChromeProfiles();
    void widthsStayFixedAcrossNativeDates();
    void reservedWidthsUseNativeFontSamples();
    void chineseEditorPresentationAndParsing();
    void chineseWidthsUseNativeFontSamples();
    void chineseGlyphCoverage();
};
void DateRangeToolsTests::sourceDateConstructionAndDisplayClamp() {
    DateRangeTools tools;
    const auto rows=read(QStringLiteral(NATIVE_DATE_RANGE_DIRECTORY "/output/captures.json")).value("rows").toArray();
    QCOMPARE(rows.size(),384);
    for(const auto &item:rows){
        const auto row=item.toObject(),configuration=row.value("configuration").toObject();
        const auto state=row.value("states").toArray()[0].toObject();
        const auto model=state.value("model").toObject();
        const auto pickers=state.value("nativeControls").toObject().value("datePickers").toArray();
        for(int index=0;index<2;++index){
            const auto name=index==0 ? QStringLiteral("start"):QStringLiteral("end");
            EXACT_DATE(tools.fromUnixSeconds(configuration.value(name).toDouble()),model.value(name).toDouble());
            EXACT_DATE(tools.clamped(model.value(name).toDouble(),range(configuration)),pickers[index].toObject().value("date").toDouble());
        }
    }
}
void DateRangeToolsTests::sourceCalendarHistoryComponents() {
    DateRangeTools tools;int compared=0;
    const auto modes=read(QStringLiteral(NATIVE_DATE_RANGE_DIRECTORY "/history-output/histories.json")).value("modes").toArray();
    for(const auto &mode:modes)for(const auto &item:mode.toObject().value("steps").toArray()){
        const auto row=item.toObject(),configuration=row.value("configuration").toObject();
        for(const auto &native:row.value("nativeInstances").toArray()){
            const auto picker=native.toObject(),calendar=picker.value("calendar").toObject();
            const auto actual=tools.parts(picker.value("date").toDouble(),configuration.value("locale").toString(),configuration.value("calendar").toString(),configuration.value("timeZone").toString());
            QCOMPARE(actual.value("firstWeekday").toInt(),calendar.value("firstWeekday").toInt());
            QCOMPARE(actual.value("minimumDaysInFirstWeek").toInt(),calendar.value("minimumDaysInFirstWeek").toInt());
            const auto expected=calendar.value("components").toObject();
            for(const auto &key:expected.keys()){
                const auto value=expected.value(key).toVariant();
                QVERIFY2(actual.contains(key),qPrintable(key));
                if(key=="leapMonth")QCOMPARE(actual.value(key).toBool(),value.toBool());
                else QCOMPARE(actual.value(key).toLongLong(),value.toLongLong());
            }
            ++compared;
        }
    }
    QCOMPARE(compared,102);
}
void DateRangeToolsTests::nativeInputArithmetic() {
    DateRangeTools tools;
    const QString locale="en_US",calendar="gregorian",zone="UTC";
    const auto evidence=read(QStringLiteral(NATIVE_DATE_INPUT_DIRECTORY "/output/journal.json"));
    const auto cases=read(QStringLiteral(NATIVE_DATE_INPUT_DIRECTORY "/cases.json"));
    const auto records=evidence.value("records").toArray();
    const auto instant=[&](const char *name){
        const auto ordinal=cases.value(QLatin1String(name)).toObject().value("observationOrdinal").toInt();
        return records[ordinal].toObject().value("state").toObject().value("model").toObject().value("start").toDouble();
    };
    const auto year=tools.stepped(1710000000.625,"year",1,locale,calendar,zone,{});
    EXACT_DATE(year,instant("keyboard-year"));
    const auto day=tools.stepped(year,"day",1,locale,calendar,zone,{});
    EXACT_DATE(day,instant("keyboard-day"));
    const auto typed=tools.replaced(day,"year",2026,locale,calendar,zone,{});
    EXACT_DATE(typed,instant("typed-year"));
    EXACT_DATE(tools.stepped(typed,"month",1,locale,calendar,zone,{}),instant("stepper-month"));
    EXACT_DATE(tools.stepped(1710000000.625,"month",1,locale,calendar,zone,{}),instant("field-month-increment"));
    const QVariantMap bounds{{"lower",1709251200.0},{"upper",1711843200.0}};
    const auto upper=tools.stepped(1710000000.625,"year",1,locale,calendar,zone,bounds);
    EXACT_DATE(upper,instant("upper-bound-clamp"));
    EXACT_DATE(tools.stepped(upper,"year",-1,locale,calendar,zone,bounds),instant("lower-bound-clamp"));
    EXACT_DATE(tools.selectingDay(year,1739836800.0,locale,calendar,zone,{}),1739894400.625);
    const auto preview=tools.previewedDay(1710259200.625,1,locale,calendar,zone,{});
    EXACT_DATE(preview,instant("graphical-space-commit"));
    EXACT_DATE(tools.previewedDay(1709990861.625,1,locale,calendar,zone,{}),1710077261.0);
    EXACT_DATE(preview-std::floor(preview),0);
    EXACT_DATE(std::fmod(preview,86400.0),57600.0);
    EXACT_DATE(tools.stepped(1710864000.125,"year",-1,locale,calendar,zone,{}),1679241600.125);
    EXACT_DATE(tools.stepped(1709222400.625,"year",1,locale,calendar,zone,{}),1740758400.625);
    EXACT_DATE(tools.replaced(1709222400.625,"year",2025,locale,calendar,zone,{}),1740758400.625);
}
void DateRangeToolsTests::localizedSegmentBoundaries() {
    DateRangeTools tools;int checked=0;
    const auto rows=read(QStringLiteral(NATIVE_DATE_RANGE_DIRECTORY "/output/captures.json")).value("rows").toArray();
    for(const auto &item:rows){
        const auto configuration=item.toObject().value("configuration").toObject();
        const auto value=tools.clamped(configuration.value("start").toDouble(),range(configuration));
        const auto formatted=tools.formatted(value,configuration.value("locale").toString(),configuration.value("calendar").toString(),configuration.value("timeZone").toString());
        QString combined;QSet<QString> kinds;
        for(const auto &segment:formatted.value("segments").toList()){
            const auto data=segment.toMap();combined+=data.value("text").toString();kinds.insert(data.value("kind").toString());
        }
        QCOMPARE(combined,formatted.value("text").toString());
        QVERIFY(kinds.contains("year") && kinds.contains("month") && kinds.contains("day"));
        ++checked;
    }
    QCOMPARE(checked,384);
    QCOMPARE(tools.formatted(1710000000.625,"en_US","gregorian","UTC").value("text").toString(),QStringLiteral("3/9/2024"));
    // Locale/calendar formatted raster equivalence remains a separate gate.
}
void DateRangeToolsTests::ownedCalendarGrid() {
    DateRangeTools tools;
    const QVariantMap bounds{{"lower",1709251200.0},{"upper",1711843200.0}};
    const auto grid=tools.month(1710000000.625,"en_US","gregorian","UTC",bounds);
    QCOMPARE(grid.value("title").toString(),QStringLiteral("Mar 2024"));
    QCOMPARE(grid.value("weekdays").toList(),QVariantList({"Su","Mo","Tu","We","Th","Fr","Sa"}));
    const auto days=grid.value("days").toList();QCOMPARE(days.size(),42);
    EXACT_DATE(days.first().toMap().value("instant").toDouble(),1708819200.0);
    EXACT_DATE(days.last().toMap().value("instant").toDouble(),1712361600.0);
    QCOMPARE(days[13].toMap().value("selected").toBool(),true);
    int enabled=0;for(const auto &day:days)enabled+=day.toMap().value("enabled").toBool();
    QCOMPARE(enabled,31);
}
void DateRangeToolsTests::editableFieldParsing(){
    DateRangeTools tools;const auto value=1710000000.625;
    const auto year=tools.parsedField(value,"year",QString::fromUtf8("٢٠٢٦"),"ar_EG","gregorian","UTC");
    QVERIFY(year.value("valid").toBool());QCOMPARE(year.value("number").toInt(),2026);
    QVERIFY(year.value("complete").toBool());
    const auto prefix=tools.parsedField(value,"month","1","en_US","gregorian","UTC");
    QVERIFY(prefix.value("valid").toBool());QVERIFY(!prefix.value("complete").toBool());
    const auto day=tools.parsedField(value,"day","9","en_US","gregorian","UTC");
    QVERIFY(day.value("valid").toBool());QVERIFY(day.value("complete").toBool());
    const auto date=tools.parsedDate(value,"3/12/2024","en_US","gregorian","UTC",{});
    QVERIFY(date.value("valid").toBool());EXACT_DATE(date.value("instant").toDouble(),1710259200.625);
    QVERIFY(!tools.parsedDate(value,"2/29/2025","en_US","gregorian","UTC",{}).value("valid").toBool());
    QVERIFY(!tools.parsedField(value,"month","99","en_US","gregorian","UTC").value("valid").toBool());
}

void DateRangeToolsTests::nativeChromeProfiles(){
    DateRangeTools tools;
    const auto rows=read(QStringLiteral(NATIVE_DATE_WIDTH_DIRECTORY "/chrome/output/bounds.json"))["rows"].toArray();
    QCOMPARE(rows.size(),36);int compared=0;
    for(const auto &item:rows){
        const auto row=item.toObject(),configuration=row["configuration"].toObject();
        const auto style=configuration["pickerStyle"].toString(),size=configuration["controlSize"].toString();
        const auto actual=tools.presentation(style,size);
        QJsonArray fields;
        for(const auto &candidate:rows){
            const auto other=candidate.toObject()["configuration"].toObject();
            if(other["locale"]==configuration["locale"]&&other["calendar"]==configuration["calendar"]&&other["controlSize"]==configuration["controlSize"]&&other["pickerStyle"]=="field")fields=candidate.toObject()["editors"].toArray();
        }
        QCOMPARE(fields.size(),2);
        const auto editors=row["editors"].toArray();QCOMPARE(editors.size(),2);
        for(int index=0;index<2;++index){
            const auto native=editors[index].toObject()["intrinsic"].toObject(),field=fields[index].toObject()["intrinsic"].toObject();
            QCOMPARE(actual["fieldHeight"].toDouble(),native["height"].toDouble());
            QCOMPARE(actual["stepperWidth"].toDouble(),native["width"].toDouble()-field["width"].toDouble());
            ++compared;
        }
    }
    QCOMPARE(compared,72);
}

void DateRangeToolsTests::nativeNumericFontContract(){
    DateRangeTools tools;const auto rows=read(QStringLiteral(NATIVE_DATE_FONT_DIRECTORY "/metrics.json"))["rows"].toArray();
    QCOMPARE(rows.size(),48);int compared=0;
    for(const auto &row:rows)for(const auto &item:row.toObject()["editors"].toArray()){
        const auto native=item.toObject()["font"].toObject();bool monospaced=false;
        for(const auto &entry:native["features"].toArray()){const auto feature=entry.toObject();monospaced|=feature["type"]==6&&feature["selector"]==0;}
        QVERIFY(monospaced);const auto font=tools.systemFont(native["pointSize"].toInt());
        QVERIFY(font.isFeatureSet(QFont::Tag("tnum")));QCOMPARE(font.featureValue(QFont::Tag("tnum")),quint32(1));
        const QFontMetricsF metrics(font);const auto widths=native["widths"].toObject();
        for(QChar digit=u'0';digit<=u'9';digit=QChar(digit.unicode()+1)){
            QVERIFY(widths[QString(digit)].toDouble()==widths["0"].toDouble());
            QVERIFY(metrics.horizontalAdvance(QString(digit))==metrics.horizontalAdvance(QStringLiteral("0")));
        }
        ++compared;
    }
    QCOMPARE(compared,96);
}
void DateRangeToolsTests::widthsStayFixedAcrossNativeDates(){
    DateRangeTools tools;int compared=0;
    const auto contexts=read(QStringLiteral(NATIVE_DATE_WIDTH_DIRECTORY "/output/widths.json"))["contexts"].toArray();
    QCOMPARE(contexts.size(),23);
    for(const auto &item:contexts){
        const auto context=item.toObject(),configuration=context["configuration"].toObject();
        const auto locale=configuration["locale"].toString(),calendar=configuration["calendar"].toString(),zone=configuration["timeZone"].toString();
        const auto profile=tools.presentation(configuration["pickerStyle"].toString(),configuration["controlSize"].toString());
        const int pixels=profile["fontPixels"].toInt();
        const auto initial=tools.fieldTextWidth(configuration["start"].toDouble(),locale,calendar,zone,pixels);
        const auto nativeWidth=context["initialEditors"].toArray()[0].toObject()["intrinsic"].toObject()["width"].toDouble();
        for(const auto &value:context["updates"].toArray()){
            const auto update=value.toObject();
            for(const auto &editor:update["editors"].toArray())QVERIFY(editor.toObject()["intrinsic"].toObject()["width"].toDouble()==nativeWidth);
            const auto actual=tools.fieldTextWidth(update["requestedDate"].toDouble(),locale,calendar,zone,pixels);
            QVERIFY2(actual==initial,qPrintable(QStringLiteral("%1: %2 != %3").arg(configuration["id"].toString()).arg(actual,0,'g',17).arg(initial,0,'g',17)));
            ++compared;
        }
    }
    QCOMPARE(compared,1848);
}
void DateRangeToolsTests::reservedWidthsUseNativeFontSamples(){
    DateRangeTools tools;int compared=0;
    const auto rows=read(QStringLiteral(NATIVE_DATE_RESERVATION_DIRECTORY "/validation/output/validation.json"))["rows"].toArray();
    QCOMPARE(rows.size(),59);
    for(const auto &item:rows){
        const auto row=item.toObject(),configuration=row["configuration"].toObject();
        for(const auto &entry:row["observations"].toArray()){
            const auto observation=entry.toObject();if(observation["fontProfile"]!="source")continue;
            const QFontMetricsF metrics(tools.systemFont(observation["fontSize"].toInt()));qreal expected=0;
            for(const auto &value:observation["fields"].toArray()){
                qreal maximum=0;
                for(const auto &label:value.toObject()["labels"].toArray()){
                    auto text=label.toString();if(text.isRightToLeft())while(!text.isEmpty()&&text.back().isSpace())text.chop(1);
                    maximum=std::max(maximum,metrics.horizontalAdvance(text));
                }
                expected+=maximum;
            }
            const auto actual=tools.fieldTextWidth(configuration["start"].toDouble(),configuration["locale"].toString(),configuration["calendar"].toString(),configuration["timeZone"].toString(),observation["fontSize"].toInt());
            QVERIFY2(actual==expected,qPrintable(QStringLiteral("%1: %2 != %3").arg(configuration["id"].toString()).arg(actual,0,'g',17).arg(expected,0,'g',17)));++compared;
        }
    }
    QCOMPARE(compared,118);
}
void DateRangeToolsTests::editorPresentationAndRoundTrip(){
    DateRangeTools tools;
    QCOMPARE(tools.editorFormatted(1710000000.625,"en_US","gregorian","UTC")["text"].toString(),QString::fromUtf8(" 3/ 9/2024"));
    QCOMPARE(tools.editorFormatted(1710000000.625,"en_GB","gregorian","UTC")["text"].toString(),QStringLiteral("09/03/2024"));
    QCOMPARE(tools.editorFormatted(1710000000.625,"ja_JP","gregorian","UTC")["text"].toString(),QString::fromUtf8("2024/ 3/ 9"));
    QCOMPARE(tools.editorFormatted(1710000000.625,"ja_JP","japanese","UTC")["text"].toString(),QString::fromUtf8("R   6/03/09"));
    QCOMPARE(tools.editorFormatted(1710000000.625,"he_IL","hebrew","UTC")["text"].toString(),QString::fromUtf8("כ״ט באדר א׳ תשפ״ד"));
    const auto rows=read(QStringLiteral(NATIVE_DATE_FONT_DIRECTORY "/metrics.json"))["rows"].toArray();int compared=0;
    for(const auto &item:rows){
        const auto row=item.toObject(),configuration=row["configuration"].toObject();
        const auto locale=configuration["locale"].toString(),calendar=configuration["calendar"].toString(),zone=configuration["timeZone"].toString();
        const auto native=row["state"].toObject()["nativeControls"].toObject()["datePickers"].toArray();
        for(const auto &picker:native){
            const auto value=picker.toObject()["date"].toDouble();const auto presentation=tools.editorFormatted(value,locale,calendar,zone);
            const auto parsed=tools.parsedDate(value,presentation["text"].toString(),locale,calendar,zone,{});
            QVERIFY2(parsed["valid"].toBool(),qPrintable(configuration["id"].toString()+": "+presentation["text"].toString()));
            EXACT_DATE(parsed["instant"].toDouble(),value);
            const auto parts=tools.parts(value,locale,calendar,zone);
            for(const auto &field:presentation["segments"].toList()){
                const auto segment=field.toMap();const auto kind=segment["kind"].toString();if(kind=="literal"||kind=="relatedYear"||kind=="yearName")continue;
                const auto result=tools.parsedField(value,kind,segment["text"].toString().remove(QChar(0x2007)),locale,calendar,zone);
                QVERIFY2(result["valid"].toBool(),qPrintable(configuration["id"].toString()+" field "+kind+": "+segment["text"].toString()));
                QCOMPARE(result["number"].toLongLong(),parts[kind].toLongLong());
            }
            ++compared;
        }
    }
    QCOMPARE(compared,96);
}
void DateRangeToolsTests::chineseEditorPresentationAndParsing(){
    DateRangeTools tools;int compared=0;
    const auto rows=read(QStringLiteral(NATIVE_DATE_CHINESE_DIRECTORY "/samples/output/samples.json"))["rows"].toArray();QCOMPARE(rows.size(),36);
    for(const auto &item:rows){
        const auto row=item.toObject(),configuration=row["configuration"].toObject();const auto locale=configuration["locale"].toString();
        for(const auto &value:row["editors"].toArray()){
            const auto editor=value.toObject();const double date=editor["date"].toDouble();const auto presentation=tools.editorFormatted(date,locale,"chinese","UTC");
            QCOMPARE(QString(presentation["text"].toString()).remove(QChar(0x2007)),editor["candidateText"].toString());
            QStringList roles;
            for(const auto &entry:presentation["segments"].toList()){
                const auto segment=entry.toMap();const auto kind=segment["kind"].toString();if(kind=="literal")continue;roles.append(kind);
                const auto parsed=tools.parsedField(date,kind,QString(segment["text"].toString()).remove(QChar(0x2007)),locale,"chinese","UTC");
                QVERIFY2(parsed["valid"].toBool(),qPrintable(configuration["id"].toString()+" "+segment["text"].toString()));
                QCOMPARE(parsed["number"].toInt(),editor["components"].toObject()[kind].toInt());
            }
            QCOMPARE(roles,QStringList({"month","day"}));
            const auto parsed=tools.parsedDate(date,presentation["text"].toString(),locale,"chinese","UTC",{});QVERIFY(parsed["valid"].toBool());EXACT_DATE(parsed["instant"].toDouble(),date);
            const auto parts=tools.parts(date,locale,"chinese","UTC");for(const auto &key:editor["components"].toObject().keys())QCOMPARE(parts[key],editor["components"].toObject()[key].toVariant());
            ++compared;
        }
    }
    QCOMPARE(compared,72);
}
void DateRangeToolsTests::chineseWidthsUseNativeFontSamples(){
    DateRangeTools tools;int compared=0;
    const auto rows=read(QStringLiteral(NATIVE_DATE_CHINESE_DIRECTORY "/validation/output/validation.json"))["rows"].toArray();QCOMPARE(rows.size(),36);
    for(const auto &item:rows){
        const auto row=item.toObject(),configuration=row["configuration"].toObject();
        for(const auto &value:row["observations"].toArray()){
            const auto observation=value.toObject();if(observation["strategy"]!="maximum"||observation["fontProfile"]!="source")continue;
            const QFontMetricsF metrics(tools.systemFont(observation["fontSize"].toInt()));qreal expected=0;
            for(const auto &entry:observation["fields"].toArray()){
                qreal maximum=0;for(const auto &label:entry.toObject()["labels"].toArray())maximum=std::max(maximum,metrics.horizontalAdvance(label.toString()));expected+=maximum;
            }
            const auto actual=tools.fieldTextWidth(configuration["start"].toDouble(),configuration["locale"].toString(),"chinese","UTC",observation["fontSize"].toInt());
            QVERIFY2(actual==expected,qPrintable(QStringLiteral("%1: %2 != %3").arg(configuration["id"].toString()).arg(actual,0,'g',17).arg(expected,0,'g',17)));++compared;
        }
    }
    QCOMPARE(compared,72);
}
void DateRangeToolsTests::chineseGlyphCoverage(){
    DateRangeTools tools;int compared=0;
    const auto rows=read(QStringLiteral(NATIVE_DATE_CHINESE_DIRECTORY "/samples/output/samples.json"))["rows"].toArray();QCOMPARE(rows.size(),36);
    for(const auto &value:rows){
        const auto row=value.toObject(),configuration=row["configuration"].toObject();
        for(const auto &item:row["editors"].toArray()){
            const auto editor=item.toObject();QTextLayout layout(editor["candidateText"].toString(),tools.systemFont(editor["font"].toObject()["pointSize"].toInt()));
            layout.beginLayout();auto line=layout.createLine();QVERIFY(line.isValid());line.setLineWidth(10000);layout.endLayout();
            const auto runs=layout.glyphRuns();QVERIFY(!runs.isEmpty());
            for(const auto &run:runs)for(auto glyph:run.glyphIndexes())QVERIFY2(glyph!=0,qPrintable(configuration["id"].toString()+": missing glyph in "+editor["candidateText"].toString()));
            ++compared;
        }
    }
    QCOMPARE(compared,72);
}
QTEST_MAIN(DateRangeToolsTests)
#include "daterangetools.moc"

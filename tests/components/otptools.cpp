#include "otptools.h"
#include <QtTest>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>

namespace {
QJsonObject read(const QString &name) {
    QFile file(QStringLiteral(NATIVE_OTP_DIRECTORY)+"/"+name);
    if(!file.open(QIODevice::ReadOnly))qFatal("Native OTP evidence missing");
    return QJsonDocument::fromJson(file.readAll()).object();
}
QString text(const QJsonArray &scalars) {
    QList<char32_t> values;for(const auto &value:scalars)values.append(char32_t(value.toInt()));
    return QString::fromUcs4(values.constData(),values.size());
}
}
class OTPTransformationTests : public QObject {
    Q_OBJECT
    BleeckerOTPTools tools;
private slots:
    void nativeExamples() {
        const auto data=read("native-otp-semantics.json");
        QCOMPARE(data.value("reference").toString(),QString("fe8a1d462fbd793d883fb92086a16aa2947e32c9"));
        const auto rows=data.value("examples").toArray();QCOMPARE(rows.size(),204);
        for(const auto &value:rows) {
            const auto row=value.toObject();
            QCOMPARE(tools.filter(text(row.value("input").toObject().value("scalars").toArray()),row.value("length").toInt()),
                     text(row.value("result").toObject().value("scalars").toArray()));
        }
    }
    void nativeMarksAndVectors() {
        const auto data=read("native-otp-graphemes.json");
        const auto marks=data.value("markContexts").toArray(),vectors=data.value("officialTests").toArray();
        QCOMPARE(marks.size(),17801);QCOMPARE(vectors.size(),766);
        for(const auto &value:marks) {
            const auto row=value.toObject();const auto input=text({row.value("base"),row.value("mark"),50});
            QCOMPARE(tools.filter(input,3),text(row.value("filteredScalars").toArray()));
            QCOMPARE(tools.filter(input,1),text(row.value("prefixOneScalars").toArray()));
        }
        for(const auto &value:vectors) {
            const auto row=value.toObject();const auto input=row.value("scalars").toArray();
            QCOMPARE(tools.filter(text(input),input.size()),text(row.value("filteredScalars").toArray()));
        }
    }
    void everyNumericTransition() {
        const auto semantics=read("native-otp-semantics.json"),facts=read("numeric-cluster-properties.json"),proof=read("native-otp-cluster-proof.json");
        const auto numbers=semantics.value("singleScalarNumbers").toArray(),joining=facts.value("joiningScalars").toArray(),prepend=facts.value("prependScalars").toArray();
        QCOMPARE(numbers.size(),2023);QCOMPARE(joining.size(),2619);QCOMPARE(prepend.size(),27);
        quint64 hash=14695981039346656037ULL;int cases=0;
        auto mix=[&](char32_t scalar){hash=(hash^quint64(scalar))*1099511628211ULL;};
        auto test=[&](char32_t base,char32_t middle){
            const char32_t values[]{base,middle,0x32};const auto input=QString::fromUcs4(values,3);
            const auto all=tools.filter(input,3).toUcs4(),one=tools.filter(input,1).toUcs4();
            ++cases;mix(0x110000);mix(base);mix(middle);for(auto scalar:all)mix(scalar);mix(0x110001);for(auto scalar:one)mix(scalar);
        };
        for(const auto &number:numbers)for(const auto &tail:joining)test(number.toInt(),tail.toInt());
        QCOMPARE(cases,proof.value("joiningCases").toInt());
        for(const auto &number:numbers)for(const auto &prefix:prepend)test(number.toInt(),prefix.toInt());
        QCOMPARE(cases,proof.value("joiningCases").toInt()+proof.value("prependCases").toInt());
        for(char32_t base:{0x31,0x661,0x2163,0x4e00,0x1d7d9,0x1f100,0xf33})
            for(char32_t scalar=0;scalar<=0x10ffff;++scalar)if(scalar<0xd800 || scalar>0xdfff)test(base,scalar);
        QCOMPARE(cases,13137306);QCOMPARE(cases,proof.value("cases").toInt());
        QCOMPARE(QString::number(hash,16),proof.value("resultFNV1a64").toString());
        QCOMPARE(QString::number(hash,16),QString("3d551fb50bf22f59"));
    }
    void getterValidationDoesNotTransform() {
        const auto input=QStringLiteral("A123456789");tools.validate(input,0);
        QCOMPARE(input,QString("A123456789"));
        QCOMPARE(tools.filter(input,0),QString());
        QCOMPARE(tools.filter(QString(40000,'a')+'1',6),QString("1"));
        QCOMPARE(tools.filter(QStringLiteral("1\u0900"),1),QStringLiteral("1\u0900"));
    }
};
QTEST_GUILESS_MAIN(OTPTransformationTests)
#include "otptools.moc"

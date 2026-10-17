#pragma once
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <cmath>

static void installAppTabFixtureMetrics(QQmlApplicationEngine &engine) {
    QFile file(":/avelino/fixtures/native-app-tab-icon-metrics.json");
    if(!file.open(QIODevice::ReadOnly))qFatal("App-tab fixture dimensions resource missing");
    const auto value=QJsonDocument::fromJson(file.readAll()).object();
    if(value["reference"]!="fe8a1d462fbd793d883fb92086a16aa2947e32c9" ||value["accepted"]!=false ||value["rows"].toArray().size()!=22)
        qFatal("App-tab fixture dimensions identity changed");
    engine.rootContext()->setContextProperty("appTabFixtureMetrics",value["rows"].toArray().toVariantList());
}

static bool appTabFixtureInteger(const QJsonValue &value) {
    if(value.isString()){bool ok=false;const auto text=value.toString();const auto number=text.toLongLong(&ok);return ok&&QString::number(number)==text;}
    return value.isDouble()&&std::isfinite(value.toDouble())&&std::floor(value.toDouble())==value.toDouble()&&std::abs(value.toDouble())<=9007199254740991.0;
}
static bool validAppTabFixture(const QJsonObject &value) {
    if(value.keys()!=QStringList{"api","disabled","fixture","height","id","owner","parentFont","parentRed","rtl","selection","source","tabHeight","tabWidth","tabs","valueKind","width"}
        ||value["api"]!="BleeckerAppTabBar"||value["source"]!="fe8a1d462fbd793d883fb92086a16aa2947e32c9"
        ||!value["id"].isString()||value["id"].toString().isEmpty()||value["fixture"]!="app-tabs-"+value["id"].toString()
        ||value["width"].toDouble()!=640||value["height"].toDouble()!=400||!value["tabs"].isArray()
        ||!QStringList{"echo","observe","delayed","redirect"}.contains(value["owner"].toString())
        ||!QStringList{"string","integer","boolean","record"}.contains(value["valueKind"].toString()))return false;
    for(const auto key:{"disabled","parentFont","parentRed","rtl"})if(!value[key].isBool())return false;
    for(const auto key:{"tabWidth","tabHeight"}) {
        const auto size=value[key];if(QByteArray(key)=="tabHeight"&&size.isNull())continue;
        if(!size.isDouble()||!std::isfinite(size.toDouble())||size.toDouble()<0)return false;
    }
    const auto kind=value["valueKind"].toString();
    const auto validValue=[&](const QJsonValue &id){
        if(!id.isString())return false;
        if(kind=="integer")return appTabFixtureInteger(id);
        if(kind=="boolean")return id=="true"||id=="false";
        if(kind=="record"){const auto parts=id.toString().split('|');return parts.size()==2&&!parts[0].isEmpty()&&appTabFixtureInteger(parts[1]);}
        return true;
    };
    if(!validValue(value["selection"]))return false;
    for(const auto &entry:value["tabs"].toArray()) {
        if(!entry.isObject())return false;const auto tab=entry.toObject();
        for(const auto &key:tab.keys())if(!QStringList{"value","label","systemImage","badge","accessibilityLabel","disabled"}.contains(key))return false;
        if(!validValue(tab["value"])||!tab["label"].isString()||!tab["systemImage"].isString()
            ||(!tab["badge"].isUndefined()&&!tab["badge"].isNull()&&!appTabFixtureInteger(tab["badge"]))
            ||(!tab["accessibilityLabel"].isUndefined()&&!tab["accessibilityLabel"].isNull()&&!tab["accessibilityLabel"].isString())
            ||(!tab["disabled"].isUndefined()&&!tab["disabled"].isBool()))return false;
    }
    return true;
}

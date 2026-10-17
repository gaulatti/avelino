#pragma once
#include "apptabfixtures.h"
#include <QSet>

static bool validCommandSpotlightFixture(const QJsonObject &value) {
    if(value.keys()!=QStringList{"api","callerHeight","callerWidth","disabled","entries","fixture","height","id","owner","parentFont","parentRed","query","rtl","source","valueKind","width"}
        ||value["api"]!="BleeckerCommandSpotlight"||value["source"]!="fe8a1d462fbd793d883fb92086a16aa2947e32c9"
        ||!value["id"].isString()||value["id"].toString().isEmpty()||value["fixture"]!="command-spotlight-"+value["id"].toString()
        ||value["width"].toDouble()!=720||value["height"].toDouble()!=520||!value["query"].isString()||!value["entries"].isArray()
        ||!QStringList{"echo","observe","delayed","redirect"}.contains(value["owner"].toString())
        ||!QStringList{"string","integer","boolean","record"}.contains(value["valueKind"].toString()))return false;
    for(const auto key:{"disabled","parentFont","parentRed","rtl"})if(!value[key].isBool())return false;
    for(const auto key:{"callerWidth","callerHeight"})if(!value[key].isNull()&&(!value[key].isDouble()||!std::isfinite(value[key].toDouble())||value[key].toDouble()<0))return false;
    QSet<QString> identifiers,keys;const auto kind=value["valueKind"].toString();
    for(const auto &entry:value["entries"].toArray()) {
        if(!entry.isObject())return false;const auto row=entry.toObject();
        for(const auto &key:row.keys())if(!QStringList{"detail","disabled","height","id","key","kind","title","width"}.contains(key))return false;
        for(const auto key:{"detail","id","key","kind","title"})if(!row[key].isString())return false;
        const auto id=row["id"].toString(),key=row["key"].toString(),rowKind=row["kind"].toString();
        if(!row["disabled"].isBool()||!row["height"].isDouble()||!std::isfinite(row["height"].toDouble())||row["height"].toDouble()<0
            ||!QStringList{"text","button","detail","fixed","fill","tall","overflow"}.contains(rowKind)
            ||identifiers.contains(id.normalized(QString::NormalizationForm_C))||keys.contains(key))return false;
        if((kind=="integer"&&!appTabFixtureInteger(row["id"]))||(kind=="boolean"&&id!="true"&&id!="false"))return false;
        if(kind=="record"){const auto pair=id.split('|');if(pair.size()!=2||pair[0].isEmpty()||!appTabFixtureInteger(pair[1]))return false;}
        if(!row["width"].isUndefined()&&(!row["width"].isDouble()||!std::isfinite(row["width"].toDouble())||row["width"].toDouble()<0))return false;
        if((rowKind=="fixed"||rowKind=="overflow")&&!row["width"].isDouble())return false;
        identifiers.insert(id.normalized(QString::NormalizationForm_C));keys.insert(key);
    }
    return true;
}

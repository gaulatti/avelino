#pragma once
#include <QJsonArray>
#include <QJsonObject>
#include <QSet>
#include <QStringList>
#include <cmath>

static bool validHeroCarouselFixture(const QJsonObject &value) {
    const auto finite=[](QJsonValue number){return number.isDouble()&&std::isfinite(number.toDouble())&&number.toDouble()>=0;};
    if(value.keys()!=QStringList{"api","carouselHeight","carouselWidth","disabled","fixture","height","id","items","parentFont","parentRed","rtl","scroll","slot","source","width"}
        ||value["api"]!="BleeckerHeroCarousel"||value["source"]!="fe8a1d462fbd793d883fb92086a16aa2947e32c9"
        ||!value["id"].isString()||value["id"].toString().isEmpty()||value["fixture"]!="hero-"+value["id"].toString()
        ||value["width"].toDouble()!=640||value["height"].toDouble()!=400
        ||!finite(value["carouselWidth"])||(!value["carouselHeight"].isNull()&&!finite(value["carouselHeight"]))
        ||!QStringList{"fill","fixed","text","button"}.contains(value["slot"].toString())
        ||!value["items"].isArray()||!value["scroll"].isBool()||value["scroll"].toBool())return false;
    for(const auto key:{"disabled","parentFont","parentRed","rtl"})if(!value[key].isBool())return false;
    QSet<QString> identities;
    for(const auto &item:value["items"].toArray()) {
        if(!item.isObject())return false;
        const auto row=item.toObject();const auto color=row["color"].toDouble(-1);
        if(row.keys()!=QStringList{"color","height","id","title","width"}||!row["id"].isString()||!row["title"].isString()
            ||!finite(row["width"])||!finite(row["height"])||!row["color"].isDouble()||color<0||color>3||std::floor(color)!=color)return false;
        const auto key=row["id"].toString().normalized(QString::NormalizationForm_C);
        if(identities.contains(key))return false;
        identities.insert(key);
    }
    return true;
}

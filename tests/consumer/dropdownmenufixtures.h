#pragma once
#include <QJsonObject>
#include <QStringList>
#include <cmath>

static bool validDropdownMenuFixture(const QJsonObject &value) {
    if(value.keys()!=QStringList{"api","configuration","fixture","height","source","width"}
        ||value["api"]!="BleeckerDropdownMenu"||value["source"]!="fe8a1d462fbd793d883fb92086a16aa2947e32c9"
        ||value["width"].toDouble()!=600||value["height"].toDouble()!=300||!value["configuration"].isObject())return false;
    const auto data=value["configuration"].toObject();
    for(const auto &key:data.keys())if(!QStringList{"controlSize","disabled","empty","height","id","itemMode","label","parentFont","parentRed","rtl","symbol","title","width"}.contains(key))return false;
    for(const auto key:{"controlSize","id","itemMode","label","symbol","title"})if(!data[key].isString())return false;
    for(const auto key:{"disabled","empty","parentFont","parentRed","rtl"})if(!data[key].isBool())return false;
    if(data["id"].toString().isEmpty()||value["fixture"]!="dropdown-menu-"+data["id"].toString()
        ||!QStringList{"mini","small","regular","large"}.contains(data["controlSize"].toString())
        ||!QStringList{"normal","single","many","long","duplicate-titles","destructive","no-symbols"}.contains(data["itemMode"].toString())
        ||!QStringList{"text","icon","rect","stack","flat","empty","button","explicit-font","explicit-red"}.contains(data["label"].toString()))return false;
    for(const auto key:{"width","height"})if(!data[key].isUndefined()&&!data[key].isNull()
        &&(!data[key].isDouble()||!std::isfinite(data[key].toDouble())||data[key].toDouble()<0))return false;
    return true;
}

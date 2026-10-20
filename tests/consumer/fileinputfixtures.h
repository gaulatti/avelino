#pragma once
#include <QJsonArray>
#include <QJsonObject>
#include <QStringList>
#include <cmath>

static bool validFileInputFixture(const QJsonObject &value){
    if(value.keys()!=QStringList{"api","configuration","fixture","height","linuxContentTypes","source","width"}
        ||value["api"]!="BleeckerFileInput"||value["source"]!="fe8a1d462fbd793d883fb92086a16aa2947e32c9"
        ||value["width"]!=600||value["height"]!=300||!value["configuration"].isObject()||!value["linuxContentTypes"].isArray())return false;
    const auto data=value["configuration"].toObject();
    for(const auto &key:data.keys())if(!QStringList{"controlSize","disabled","height","id","parentFont","parentRed","rtl","title","types","width"}.contains(key))return false;
    if(!data["id"].isString()||data["id"].toString().isEmpty()||value["fixture"]!="file-input-"+data["id"].toString()
        ||!data["types"].isArray()||!QStringList{"mini","small","regular","large"}.contains(data["controlSize"].toString()))return false;
    if(!data["title"].isUndefined()&&!data["title"].isNull()&&!data["title"].isString())return false;
    for(const auto key:{"disabled","parentFont","parentRed","rtl"})if(!data[key].isBool())return false;
    for(const auto &type:data["types"].toArray())if(!type.isString())return false;
    for(const auto key:{"width","height"})if(!data[key].isUndefined()&&!data[key].isNull()
        &&(!data[key].isDouble()||!std::isfinite(data[key].toDouble())||data[key].toDouble()<0))return false;
    for(const auto &type:value["linuxContentTypes"].toArray())if(!type.isString()&&!type.isObject())return false;
    return true;
}

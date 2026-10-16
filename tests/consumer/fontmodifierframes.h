#pragma once
#include <QQuickItem>
#include <QJsonObject>
#include <QJsonArray>
#include <QJSValue>
#include <QFont>
#include <cmath>

static QJsonObject fontModifierMap(QQuickItem *fixture,const char *method) {
    QVariant value;
    if(!fixture || !QMetaObject::invokeMethod(fixture,method,Q_RETURN_ARG(QVariant,value)))qFatal("Font modifier live observation unavailable");
    if(value.metaType()==QMetaType::fromType<QJSValue>())value=value.value<QJSValue>().toVariant();
    return QJsonObject::fromVariantMap(value.toMap());
}
static QQuickItem *fontModifierPart(QQuickItem *control,int index) {
    QQuickItem *item=nullptr;
    if(!control || !QMetaObject::invokeMethod(control,"partAt",Q_RETURN_ARG(QQuickItem*,item),Q_ARG(int,index)) || !item)qFatal("Font modifier caller unavailable");
    return item;
}
static QJsonObject fontModifierState(QQuickItem *fixture) {
    return {{"appearances",fixture->property("appearances").toInt()},
        {"disappearances",fixture->property("disappearances").toInt()},
        {"callerInstances",fixture->property("callerInstances").toInt()}};
}
static QJsonObject fontModifierObservation(QQuickItem *fixture) {
    const auto control=fixture ? fixture->property("control").value<QQuickItem*>():nullptr;
    if(!control)qFatal("Font modifier scope unavailable");
    QJsonArray callers;
    for(int index=0;index<control->property("partCount").toInt();++index){
        auto item=fontModifierPart(control,index);
        QJsonObject row{{"objectName",item->objectName()},{"visible",item->isVisible()}};
        if(item->property("text").isValid())row.insert("text",item->property("text").toString());
        if(item->property("font").isValid()){
            const auto font=item->property("font").value<QFont>();
            row.insert("font",QJsonObject{{"family",font.family()},{"pointSize",font.pointSizeF()},{"weight",int(font.weight())},{"italic",font.italic()}});
        }
        callers.append(row);
    }
    return {{"renderedFamily",control->property("family").toString()},{"renderedSize",control->property("size").toDouble()},
        {"renderedWeight",control->property("weight").toString()},{"renderedTextScale",control->property("textScale").toDouble()},
        {"renderedResolvedPixelSize",control->property("resolvedPixelSize").toDouble()},{"renderedRtl",control->property("mirrored").toBool()},
        {"fontModifierParts",fontModifierMap(fixture,"frames")},{"fontModifierBaselines",fontModifierMap(fixture,"baselines")},
        {"fontModifierState",fontModifierState(fixture)},{"renderedCallerObjects",callers}};
}

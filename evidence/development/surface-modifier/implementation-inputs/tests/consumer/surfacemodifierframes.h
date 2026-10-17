#pragma once
#include <QQuickItem>
#include <QJsonObject>
#include <QJsonArray>
#include <QJSValue>
#include <QFont>

static QQuickItem *surfaceModifierPart(QQuickItem *modifier,int index) {
    QQuickItem *item=nullptr;
    if(!modifier || !QMetaObject::invokeMethod(modifier,"partAt",Q_RETURN_ARG(QQuickItem*,item),Q_ARG(int,index)) || !item)
        qFatal("Surface modifier part unavailable");
    return item;
}
static QJsonObject surfaceModifierMap(QQuickItem *fixture,const char *method) {
    QVariant value;
    if(!fixture || !QMetaObject::invokeMethod(fixture,method,Q_RETURN_ARG(QVariant,value)))qFatal("Surface caller observation unavailable");
    if(value.metaType()==QMetaType::fromType<QJSValue>())value=value.value<QJSValue>().toVariant();
    return QJsonObject::fromVariantMap(value.toMap());
}
static QJsonObject surfaceModifierState(QQuickItem *fixture) {
    QJsonObject state;
    for(const auto *name:{"appearances","disappearances","callerInstances","actions","counter"})state.insert(name,fixture->property(name).toInt());
    return state;
}
static QJsonObject surfaceModifierObservation(QQuickItem *fixture) {
    const auto control=fixture ? fixture->property("control").value<QQuickItem*>():nullptr;
    if(!control)qFatal("Surface caller scope unavailable");
    QJsonArray callers;
    for(int i=0;i<control->property("partCount").toInt();++i){
        const auto part=surfaceModifierPart(control,i),caller=part->property("callerItem").value<QQuickItem*>();
        if(!caller)qFatal("Surface decorated caller unavailable");
        QJsonObject row{{"objectName",caller->objectName()},{"visible",caller->isVisible()},{"width",caller->width()},{"height",caller->height()}};
        if(caller->property("text").isValid())row.insert("text",caller->property("text").toString());
        if(caller->property("font").isValid()){
            const auto font=caller->property("font").value<QFont>();
            row.insert("font",QJsonObject{{"family",font.family()},{"pointSize",font.pointSizeF()},{"weight",int(font.weight())}});
        }
        callers.append(row);
    }
    return {{"renderedRadius",control->property("radius").toDouble()},
        {"renderedRtl",fixture->property("mirrored").toBool()},{"renderedTextScale",fixture->property("observedTextScale").toDouble()},
        {"surfaceModifierParts",surfaceModifierMap(fixture,"frames")},{"surfaceModifierBaselines",surfaceModifierMap(fixture,"baselines")},
        {"surfaceModifierState",surfaceModifierState(fixture)},{"renderedCallerObjects",callers}};
}

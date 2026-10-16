#pragma once
#include <QQuickItem>
#include <QJsonObject>
#include <QJsonArray>
#include <QJSValue>
#include <QMap>
#include <algorithm>
#include <tuple>

static QJsonArray buttonStyleList(const QVariant &value) {
    return QJsonArray::fromVariantList(value.metaType()==QMetaType::fromType<QJSValue>()
        ? value.value<QJSValue>().toVariant().toList():value.toList());
}
static QQuickItem *buttonStylePart(QQuickItem *control,int index) {
    QQuickItem *part=nullptr;
    if(!control || !QMetaObject::invokeMethod(control,"partAt",Q_RETURN_ARG(QQuickItem*,part),Q_ARG(int,index)) || !part)
        qFatal("ButtonStyle part unavailable");
    return part;
}
static QJsonObject buttonStyleFrames(QQuickItem *fixture) {
    const auto control=fixture->property("control").value<QQuickItem*>();
    if(!control)qFatal("ButtonStyle caller unavailable");
    QMap<QString,QList<QJsonObject>> rectangles;
    auto append=[&](const QString &key,QQuickItem *item){
        if(!item)qFatal("ButtonStyle geometry witness unavailable");
        const auto point=item->mapToItem(fixture,QPointF());
        rectangles[key].append(QJsonObject{{"x",point.x()},{"y",point.y()},{"width",item->width()},{"height",item->height()}});
    };
    const int count=control->property("partCount").toInt();
    for(int index=0;index<count;++index){
        const auto part=buttonStylePart(control,index),label=part->property("labelItem").value<QQuickItem*>();
        append("root",part);append("body",part->property("presentationItem").value<QQuickItem*>());
        append(count==2 ? index==0 ? "first":"second":"label",label);
    }
    if(const auto parent=fixture->property("parentLayout").value<QQuickItem*>()){
        append("parent",parent);append("leading",fixture->property("leadingItem").value<QQuickItem*>());
        append("trailing",fixture->property("trailingItem").value<QQuickItem*>());
    }
    QJsonObject result;
    for(auto it=rectangles.begin();it!=rectangles.end();++it){
        auto values=it.value();
        const auto key=[](const QJsonObject &r){return std::make_tuple(r["x"].toDouble(),r["y"].toDouble(),r["width"].toDouble(),r["height"].toDouble());};
        std::sort(values.begin(),values.end(),[&](const auto &a,const auto &b){return key(a)<key(b);});
        QJsonArray array;for(const auto &rect:values)array.append(rect);result.insert(it.key(),array);
    }
    return result;
}

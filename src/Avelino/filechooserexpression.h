#pragma once
#include <QString>
#include <QVariantList>
#include <QVariantMap>

// Ordered document segments. Each committed token is independent; raw text
// stays at its position instead of being folded into a token's query.
inline QString fileSearchExpressionError(const QVariantList &expression){
    bool previousRaw=false;
    for(const auto &value:expression){
        if(value.metaType().id()!=QMetaType::QVariantMap)return QStringLiteral("Search expression segments must be objects");
        const auto row=value.toMap();const auto kind=row.value("kind");
        if(kind.metaType().id()!=QMetaType::QString)return QStringLiteral("Search expression segments require a kind");
        if(kind=="text"){
            if(previousRaw)return QStringLiteral("Adjacent raw search segments must be one text segment");
            if(row.size()!=2||row.value("text").metaType().id()!=QMetaType::QString||row.value("text").toString().isEmpty())
                return QStringLiteral("Raw search segments require nonempty text");
        }else if(kind=="token"){
            if(row.size()!=3||row.value("query").metaType().id()!=QMetaType::QString||row.value("query").toString().isEmpty()
                ||row.value("mode").metaType().id()!=QMetaType::QString||(row.value("mode")!="filename"&&row.value("mode")!="everything"))
                return QStringLiteral("Search tokens require a query and Filename or Everything mode");
        }else return QStringLiteral("Unknown search expression segment kind");
        previousRaw=kind=="text";
    }
    return {};
}
inline QString fileSearchSegmentText(const QVariant &value){
    const auto row=value.toMap();return row.value(row.value("kind")=="token"?"query":"text").toString();
}

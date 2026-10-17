#include "selectionidentity.h"
#include <QFile>
#include <QHash>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <cmath>

namespace {
struct Normalization {
    QHash<char32_t,QList<char32_t>> canonical;
    QHash<char32_t,int> classes;
    Normalization() {
        QFile file(QStringLiteral(":/qt/qml/Avelino/unicode-normalization-17.json"));
        if(!file.open(QIODevice::ReadOnly))qFatal("Pinned Unicode normalization facts missing");
        const auto data=QJsonDocument::fromJson(file.readAll()).object();
        if(data.value("unicodeVersion").toString()!="17.0.0")qFatal("Pinned Unicode normalization version invalid");
        const auto mappings=data.value("canonical").toObject(),combining=data.value("combiningClasses").toObject();
        if(mappings.size()!=2081 || combining.size()!=968)qFatal("Pinned Unicode normalization facts incomplete");
        for(auto it=mappings.begin();it!=mappings.end();++it) {
            QList<char32_t> values;for(const auto &value:it.value().toArray())values.append(char32_t(value.toInt()));
            canonical.insert(char32_t(it.key().toUInt(nullptr,16)),values);
        }
        for(auto it=combining.begin();it!=combining.end();++it)classes.insert(char32_t(it.key().toUInt(nullptr,16)),it.value().toInt());
    }
    void append(char32_t scalar,QList<char32_t> &result) const {
        // Unicode 17 canonical decomposition, including algorithmic Hangul.
        constexpr char32_t sBase=0xac00,lBase=0x1100,vBase=0x1161,tBase=0x11a7;
        constexpr int tCount=28,nCount=21*tCount,sCount=19*nCount;
        if(scalar>=sBase && scalar<sBase+sCount) {
            const auto index=scalar-sBase;
            append(lBase+index/nCount,result);append(vBase+(index%nCount)/tCount,result);
            if(index%tCount)append(tBase+index%tCount,result);
            return;
        }
        const auto mapping=canonical.constFind(scalar);
        if(mapping!=canonical.cend()) {for(const auto child:mapping.value())append(child,result);return;}
        result.append(scalar);
        // Stable canonical ordering stops at each starter. Equal classes retain order.
        const auto rank=classes.value(scalar,0);
        for(auto index=result.size()-1;index>0 && rank && classes.value(result[index-1],0)>rank;--index)
            std::swap(result[index],result[index-1]);
    }
};
const Normalization &normalization(){static const Normalization data;return data;}
QString primitiveKey(const QJSValue &value,const char *owner) {
    if(value.isString())return QStringLiteral("s:")+SelectionIdentity::canonicalString(value.toString(),owner);
    if(value.isBool())return value.toBool() ? QStringLiteral("b:1"):QStringLiteral("b:0");
    if(value.isNull())return QStringLiteral("null:");
    if(value.isNumber()) {
        const auto number=value.toNumber();
        if(std::isnan(number))return QStringLiteral("n:nan");
        return QStringLiteral("n:")+QString::number(number==0 ? 0:number,'g',17);
    }
    qFatal("%s values require primitive identity or a valueIdentity function returning a primitive key",owner);
}
}

QString SelectionIdentity::canonicalString(const QString &value,const char *owner) {
    QList<char32_t> result;
    result.reserve(value.size());
    const auto &data=normalization();
    for(qsizetype i=0;i<value.size();++i) {
        char32_t scalar=value[i].unicode();
        if(QChar::isHighSurrogate(scalar)) {
            if(i+1>=value.size() || !value[i+1].isLowSurrogate())qFatal("%s String identity requires valid Unicode scalars",owner);
            scalar=QChar::surrogateToUcs4(value[i],value[i+1]);++i;
        } else if(QChar::isLowSurrogate(scalar))qFatal("%s String identity requires valid Unicode scalars",owner);
        data.append(scalar,result);
    }
    return QString::fromUcs4(result.constData(),result.size());
}

QString SelectionIdentity::key(const QJSValue &value,const QJSValue &identity,const char *owner) {
    if(identity.isUndefined() || identity.isNull())return primitiveKey(value,owner);
    if(!identity.isCallable())qFatal("%s valueIdentity must be a function or null",owner);
    const auto projected=identity.call({value});
    if(projected.isError())qFatal("%s valueIdentity callback failed",owner);
    return primitiveKey(projected,owner);
}

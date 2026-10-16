#include "valuetools.h"
#include <QQmlComponent>

QJSValue BleeckerValueTools::breadcrumbItems(const QJSValue &items) const {
    // C++ producers expose QVariantList as a native QML sequence rather than
    // a JavaScript Array; both carry the same ordered item contract.
    if(!items.isArray() && items.toVariant().metaType()!=QMetaType::fromType<QVariantList>())
        qFatal("Breadcrumb items must be an array");
    const auto count=items.property(QStringLiteral("length")).toUInt();
    for(quint32 index=0;index<count;++index) {
        const auto item=items.property(index);
        if(!item.isObject()||!item.property(QStringLiteral("title")).isString())
            qFatal("Breadcrumb items require string titles");
        const auto icon=item.property(QStringLiteral("icon"));
        if(!icon.isNull()&&!icon.isUndefined()&&!qobject_cast<QQmlComponent*>(icon.toQObject()))
            qFatal("Breadcrumb item icons must be Components or null");
    }
    return items;
}

int BleeckerValueTools::spinnerEdge(const QString &size) const {
    if (size==QStringLiteral("sm")) return 16;
    if (size==QStringLiteral("md") || size==QStringLiteral("lg")) return 32;
    qFatal("Unknown Bleecker loading-spinner size");
}
#include <QVariant>
#include <QJSValue>
#include <algorithm>
#include <cmath>
#include <limits>
#include <unicode/numberformatter.h>

qreal BleeckerValueTools::brandSize(qreal value) const {
    if(!std::isfinite(value)||value<0)qFatal("Brand size must be finite and nonnegative");
    return value;
}

void BleeckerValueTools::setValue(QObject *control, qreal value) const {
    // Native writes retain QML bindings; JavaScript assignments remove them.
    if (!control || !control->setProperty("value", value))
        qFatal("Value adapter requires a writable value property");
}

void BleeckerValueTools::moveSlider(QObject *control, qreal value) const {
    setValue(control, value);
    if (!QMetaObject::invokeMethod(control, "moved"))
        qFatal("Slider value adapter requires a moved signal");
}

qreal BleeckerValueTools::sliderIntervals(qreal from, qreal to, qreal step) const {
    if (!std::isfinite(from) || !std::isfinite(to) || from > to || !std::isfinite(step) || step < 0)
        qFatal("Slider requires finite ascending bounds and nonnegative stepSize");
    if (step == 0) return -1;
    // Include an integral endpoint lost by one division ULP (0.3 / 0.1),
    // matching the measured source without rounding partial intervals up.
    const auto quotient = (to-from)/step;
    return std::floor(std::nextafter(quotient, std::numeric_limits<qreal>::infinity()));
}

void BleeckerValueTools::select(QObject *control, const QVariant &value) const {
    if (!control || !control->setProperty("selection", value)
        || !QMetaObject::invokeMethod(control, "activated", Q_ARG(QVariant, value)))
        qFatal("Selection adapter requires a selection property and activated signal");
}

namespace {
[[noreturn]] void invalidInteger(const char *owner) {
    qFatal("%s requires signed 64-bit integers; use canonical decimal strings outside the JavaScript safe integer range", owner);
}
qint64 signedInteger(QVariant value, const char *owner) {
    if (value.metaType()==QMetaType::fromType<QJSValue>()) {
        const auto js=value.value<QJSValue>();
        if (js.isString()) value=js.toString();
        else if (js.isNumber()) value=js.toNumber();
        else invalidInteger(owner);
    }
    switch (value.metaType().id()) {
    case QMetaType::QString: {
        const auto text=value.toString();bool ok=false;
        const auto number=text.toLongLong(&ok);
        if (!ok || QString::number(number)!=text) invalidInteger(owner);
        return number;
    }
    case QMetaType::Double: case QMetaType::Float: {
        const auto number=value.toDouble();
        constexpr double safeInteger=9007199254740991.0;
        if (!std::isfinite(number) || std::trunc(number)!=number || std::abs(number)>safeInteger) invalidInteger(owner);
        return qint64(number);
    }
    case QMetaType::Int: case QMetaType::UInt: case QMetaType::Short: case QMetaType::UShort:
    case QMetaType::Long: case QMetaType::LongLong:
        return value.toLongLong();
    case QMetaType::ULong: case QMetaType::ULongLong: {
        const auto number=value.toULongLong();
        if (number>quint64(std::numeric_limits<qint64>::max())) invalidInteger(owner);
        return qint64(number);
    }
    default: invalidInteger(owner);
    }
}

qint64 stepperAdd(qint64 value, qint64 step, const char *phase) {
    if ((step>0 && value>std::numeric_limits<qint64>::max()-step)
        || (step<0 && value<std::numeric_limits<qint64>::min()-step))
        qFatal("Stepper %s overflow", phase);
    return value+step;
}

qint64 stepperSubtract(qint64 value, qint64 step) {
    // Do not negate step: Int.min is a valid source step.
    if ((step>0 && value<std::numeric_limits<qint64>::min()+step)
        || (step<0 && value>std::numeric_limits<qint64>::max()+step))
        qFatal("Stepper decrement overflow");
    return value-step;
}
}

QVariantMap BleeckerValueTools::pagination(const QVariant &pageValue,const QVariant &countValue,const QLocale &locale) const {
    const auto page=signedInteger(pageValue,"Pagination"),count=signedInteger(countValue,"Pagination");
    const bool previous=page>1,next=page<count;
    // An enabled action cannot overflow: previous implies page>1; next implies page<Int.max.
    return {{"pageText",locale.toString(page)},{"countText",locale.toString(std::max(qint64(1),count))},
        {"previousEnabled",previous},{"nextEnabled",next},
        {"previousRequest",previous ? QVariant(QString::number(page-1)) : QVariant()},
        {"nextRequest",next ? QVariant(QString::number(page+1)) : QVariant()}};
}

QVariantMap BleeckerValueTools::stepper(const QVariant &valueInput,const QVariant &lowerInput,const QVariant &upperInput,
    const QVariant &stepInput,const QVariant &offsetInput,const QLocale &locale) const {
    const auto value=signedInteger(valueInput,"Stepper"),lower=signedInteger(lowerInput,"Stepper"),upper=signedInteger(upperInput,"Stepper");
    signedInteger(stepInput,"Stepper");
    const auto offset=signedInteger(offsetInput,"Stepper");
    if(lower>upper)qFatal("Stepper requires an ascending closed range");
    const auto displayed=stepperAdd(value,offset,"display");
    UErrorCode status=U_ZERO_ERROR;
    const auto number=icu::number::NumberFormatter::withLocale(icu::Locale(locale.name().toUtf8().constData())).formatInt(displayed,status);
    const auto text=number.toString(status);
    if(U_FAILURE(status))qFatal("Stepper integer formatting failed: %s",u_errorName(status));
    return {{"value",QString::number(value)},{"displayValue",QString::number(displayed)},
        {"formattedValue",QString::fromUtf16(reinterpret_cast<const char16_t*>(text.getBuffer()),text.length())},
        {"decrementEnabled",value>lower},{"incrementEnabled",value<upper}};
}

QVariant BleeckerValueTools::stepperRequest(const QVariant &valueInput,const QVariant &lowerInput,const QVariant &upperInput,
    const QVariant &stepInput,bool increment) const {
    const auto value=signedInteger(valueInput,"Stepper"),lower=signedInteger(lowerInput,"Stepper"),upper=signedInteger(upperInput,"Stepper"),step=signedInteger(stepInput,"Stepper");
    if(lower>upper)qFatal("Stepper requires an ascending closed range");
    if(increment ? value>=upper:value<=lower)return {};
    // Source arithmetic happens on activation, before its one-sided clamp.
    // Precomputing either request in stepper() would trap too early.
    const auto requested=increment ? std::min(upper,stepperAdd(value,step,"increment"))
        : std::max(lower,stepperSubtract(value,step));
    return QString::number(requested);
}

int BleeckerValueTools::alertTypeIndex(const QString &type) const {
    if(type==QStringLiteral("info"))return 0;
    if(type==QStringLiteral("success"))return 1;
    if(type==QStringLiteral("error"))return 2;
    if(type==QStringLiteral("warning"))return 3;
    qFatal("Unknown Bleecker alert type");
}

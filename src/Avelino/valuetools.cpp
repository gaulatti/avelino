#include "valuetools.h"
#include <QVariant>
#include <QJSValue>
#include <algorithm>
#include <cmath>
#include <limits>

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
[[noreturn]] void invalidPageInteger() {
    qFatal("Pagination requires signed 64-bit integers; use canonical decimal strings outside the JavaScript safe integer range");
}
qint64 pageInteger(QVariant value) {
    if (value.metaType()==QMetaType::fromType<QJSValue>()) {
        const auto js=value.value<QJSValue>();
        if (js.isString()) value=js.toString();
        else if (js.isNumber()) value=js.toNumber();
        else invalidPageInteger();
    }
    switch (value.metaType().id()) {
    case QMetaType::QString: {
        const auto text=value.toString();bool ok=false;
        const auto number=text.toLongLong(&ok);
        if (!ok || QString::number(number)!=text) invalidPageInteger();
        return number;
    }
    case QMetaType::Double: case QMetaType::Float: {
        const auto number=value.toDouble();
        constexpr double safeInteger=9007199254740991.0;
        if (!std::isfinite(number) || std::trunc(number)!=number || std::abs(number)>safeInteger) invalidPageInteger();
        return qint64(number);
    }
    case QMetaType::Int: case QMetaType::UInt: case QMetaType::Short: case QMetaType::UShort:
    case QMetaType::Long: case QMetaType::LongLong:
        return value.toLongLong();
    case QMetaType::ULong: case QMetaType::ULongLong: {
        const auto number=value.toULongLong();
        if (number>quint64(std::numeric_limits<qint64>::max())) invalidPageInteger();
        return qint64(number);
    }
    default: invalidPageInteger();
    }
}
}

QVariantMap BleeckerValueTools::pagination(const QVariant &pageValue,const QVariant &countValue,const QLocale &locale) const {
    const auto page=pageInteger(pageValue),count=pageInteger(countValue);
    const bool previous=page>1,next=page<count;
    // An enabled action cannot overflow: previous implies page>1; next implies page<Int.max.
    return {{"pageText",locale.toString(page)},{"countText",locale.toString(std::max(qint64(1),count))},
        {"previousEnabled",previous},{"nextEnabled",next},
        {"previousRequest",previous ? QVariant(QString::number(page-1)) : QVariant()},
        {"nextRequest",next ? QVariant(QString::number(page+1)) : QVariant()}};
}

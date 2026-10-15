#include "valuetools.h"
#include <QVariant>
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

#pragma once
#include <QObject>
#include <QtQml/qqmlregistration.h>

class BleeckerValueTools final : public QObject {
    Q_OBJECT
    QML_ELEMENT
    QML_SINGLETON
public:
    using QObject::QObject;
    Q_INVOKABLE qreal sliderIntervals(qreal from, qreal to, qreal step) const;
    Q_INVOKABLE void setValue(QObject *control, qreal value) const;
    Q_INVOKABLE void moveSlider(QObject *control, qreal value) const;
};

#pragma once
#include <QObject>
#include <QVariant>
#include <QVariantMap>
#include <QLocale>
#include <QtQml/qqmlregistration.h>

class BleeckerValueTools final : public QObject {
    Q_OBJECT
    QML_ELEMENT
    QML_SINGLETON
public:
    using QObject::QObject;
    Q_INVOKABLE qreal sliderIntervals(qreal from, qreal to, qreal step) const;
    Q_INVOKABLE int spinnerEdge(const QString &size) const;
    Q_INVOKABLE QVariantMap pagination(const QVariant &page, const QVariant &pageCount, const QLocale &locale) const;
    Q_INVOKABLE void select(QObject *control, const QVariant &value) const;
    Q_INVOKABLE void setValue(QObject *control, qreal value) const;
    Q_INVOKABLE void moveSlider(QObject *control, qreal value) const;
};

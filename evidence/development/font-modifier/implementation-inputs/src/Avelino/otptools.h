#pragma once
#include <QObject>
#include <QtQml/qqmlregistration.h>

// Exact numeric-character filter for the pinned source OTP setter. This is not
// a replacement for general Swift Character segmentation or normalization.
class BleeckerOTPTools final : public QObject {
    Q_OBJECT
    QML_ELEMENT
    QML_SINGLETON
public:
    using QObject::QObject;
    Q_INVOKABLE QString filter(const QString &value, double length) const;
    Q_INVOKABLE void validate(const QString &value, double length) const;
};

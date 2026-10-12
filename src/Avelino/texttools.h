#pragma once
#include <QObject>
#include <QtQml/qqmlregistration.h>

class BleeckerTextTools final : public QObject {
    Q_OBJECT
    QML_ELEMENT
    QML_SINGLETON
public:
    using QObject::QObject;
    Q_INVOKABLE QString avatarInitials(const QString &name) const;
};

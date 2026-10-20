#pragma once
#include <QJSValue>
#include <QObject>
#include <QtQml/qqmlregistration.h>

namespace SelectionIdentity {
QString canonicalString(const QString &value, const char *owner="RadioGroup");
QString key(const QJSValue &value, const QJSValue &identity = {}, const char *owner="RadioGroup");
}

class BleeckerSelectionTools final : public QObject {
    Q_OBJECT
    QML_ELEMENT
    QML_SINGLETON
public:
    using QObject::QObject;
    Q_INVOKABLE QString canonicalString(const QString &value) const {return SelectionIdentity::canonicalString(value);}
    Q_INVOKABLE bool stringsEqual(const QString &left, const QString &right) const {
        return canonicalString(left)==canonicalString(right);
    }
};

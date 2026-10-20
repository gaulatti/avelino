#pragma once
#include <QObject>
#include <QFont>
#include <QtQml/qqmlregistration.h>

class BleeckerTextTools final : public QObject {
    Q_OBJECT
    QML_ELEMENT
    QML_SINGLETON
public:
    using QObject::QObject;
    Q_INVOKABLE QString avatarInitials(const QString &name) const;
    Q_INVOKABLE qreal proposedWidth(qreal maximumWidth, qreal insets) const;
    Q_INVOKABLE QFont spacedFont(const QFont &font, qreal spacing) const;
    Q_INVOKABLE QString plainText(const QString &text, int format) const;
    Q_INVOKABLE bool textResourcesReady(QObject *item) const;
};

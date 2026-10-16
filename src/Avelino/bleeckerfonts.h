#pragma once
#include <QObject>
#include <QtQml/qqmlregistration.h>

class BleeckerFonts final : public QObject {
    Q_OBJECT
    QML_ELEMENT
    QML_SINGLETON
    Q_PROPERTY(QString primary READ primary CONSTANT)
    Q_PROPERTY(QString secondary READ secondary CONSTANT)
    Q_PROPERTY(QString monospace READ monospace CONSTANT)
public:
    explicit BleeckerFonts(QObject *parent = nullptr);
    QString primary() const { return QStringLiteral("Encode Sans"); }
    QString secondary() const { return QStringLiteral("Libre Franklin"); }
    QString monospace() const;
    Q_INVOKABLE qreal pointSizeForPixels(qreal pixels) const;
    static qreal logicalFontDpi();
};

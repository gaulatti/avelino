#pragma once
#include <QObject>
#include <QLocale>
#include <QtQml/qqmlregistration.h>

class BleeckerNumberTools final : public QObject {
    Q_OBJECT
    QML_ELEMENT
    QML_SINGLETON
    Q_PROPERTY(QLocale processLocale READ processLocale NOTIFY processLocaleChanged)
public:
    explicit BleeckerNumberTools(QObject *parent=nullptr);
    QLocale processLocale() const {return QLocale();}
    Q_INVOKABLE QString format(double value,const QString &format,const QString &currencyCode,const QLocale &locale,bool signedPercent=false) const;
signals:
    void processLocaleChanged();
protected:
    bool eventFilter(QObject *object,QEvent *event) override;
};

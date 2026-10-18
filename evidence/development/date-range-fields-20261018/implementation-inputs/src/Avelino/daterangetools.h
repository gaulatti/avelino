#pragma once
#include <QObject>
#include <QVariantMap>
#include <QFont>
#include <QtQml/qqmlregistration.h>

// Date values are Unix seconds, retaining Foundation Date's Double precision.
// Formatting/calendar arithmetic is separate from the caller's bound model.
class DateRangeTools final : public QObject {
    Q_OBJECT
    QML_ELEMENT
    QML_SINGLETON
public:
    explicit DateRangeTools(QObject *parent=nullptr):QObject(parent){}
    Q_INVOKABLE double fromUnixSeconds(double value) const;
    Q_INVOKABLE double clamped(double value,const QVariant &range) const;
    Q_INVOKABLE QVariantMap parts(double value,const QString &locale,const QString &calendar,const QString &timeZone) const;
    Q_INVOKABLE QVariantMap formatted(double value,const QString &locale,const QString &calendar,const QString &timeZone) const;
    Q_INVOKABLE QVariantMap editorFormatted(double value,const QString &locale,const QString &calendar,const QString &timeZone) const;
    Q_INVOKABLE QString editorFieldText(const QString &part,const QString &input) const;
    Q_INVOKABLE double stepped(double value,const QString &part,int amount,const QString &locale,const QString &calendar,const QString &timeZone,const QVariant &range) const;
    Q_INVOKABLE double replaced(double value,const QString &part,int number,const QString &locale,const QString &calendar,const QString &timeZone,const QVariant &range) const;
    Q_INVOKABLE double midnight(double value,const QString &locale,const QString &calendar,const QString &timeZone) const;
    Q_INVOKABLE double previewedDay(double value,int amount,const QString &locale,const QString &calendar,const QString &timeZone,const QVariant &range) const;
    Q_INVOKABLE double selectingDay(double value,double day,const QString &locale,const QString &calendar,const QString &timeZone,const QVariant &range) const;
    Q_INVOKABLE QVariantMap month(double value,const QString &locale,const QString &calendar,const QString &timeZone,const QVariant &range) const;
    Q_INVOKABLE QString calendarForLocale(const QString &locale) const;
    Q_INVOKABLE QString systemTimeZone() const;
    Q_INVOKABLE QFont systemFont(int pixels) const;
    Q_INVOKABLE QVariantMap presentation(const QString &style,const QString &size) const;
    Q_INVOKABLE qreal fieldTextWidth(double value,const QString &locale,const QString &calendar,const QString &timeZone,int pixels) const;
    Q_INVOKABLE QVariantList fieldWidths(const QString &locale,const QString &calendar,const QString &timeZone,int pixels) const;
    Q_INVOKABLE QVariantMap parsedField(double value,const QString &part,const QString &input,const QString &locale,const QString &calendar,const QString &timeZone) const;
    Q_INVOKABLE QVariantMap parsedDate(double value,const QString &input,const QString &locale,const QString &calendar,const QString &timeZone,const QVariant &range) const;
};

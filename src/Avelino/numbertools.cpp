#include "numbertools.h"
#include <QCoreApplication>
#include <QEvent>
#include <QQmlEngine>
#include <array>
#include <charconv>
#include <cmath>
#include <unicode/currunit.h>
#include <unicode/numberformatter.h>
#include <unicode/nounit.h>

namespace {
QString rawDouble(double value) {
    if(std::isnan(value))return QStringLiteral("nan");
    if(std::isinf(value))return value<0 ? QStringLiteral("-inf"):QStringLiteral("inf");
    if(value==0)return std::signbit(value) ? QStringLiteral("-0.0"):QStringLiteral("0.0");
    std::array<char,64> buffer;
    const auto absolute=std::abs(value);
    const auto style=absolute>=1e-4 && absolute<1e16 ? std::chars_format::fixed:std::chars_format::general;
    const auto result=std::to_chars(buffer.data(),buffer.data()+buffer.size(),value,style);
    if(result.ec!=std::errc{})qFatal("Double description conversion failed");
    auto text=QString::fromLatin1(buffer.data(),result.ptr-buffer.data());
    if(!text.contains('.')&&!text.contains('e'))text+=QStringLiteral(".0");
    return text;
}
bool currencyIdentifier(const QString &code) {
    if(code.size()!=3)return false;
    for(auto c:code)if(!((c>='A'&&c<='Z')||(c>='a'&&c<='z')))return false;
    return true;
}
}
BleeckerNumberTools::BleeckerNumberTools(QObject *parent):QObject(parent) {
    if(qApp)qApp->installEventFilter(this);
}
bool BleeckerNumberTools::eventFilter(QObject *object,QEvent *event) {
    if(object==qApp && event->type()==QEvent::LocaleChange)emit processLocaleChanged();
    return QObject::eventFilter(object,event);
}
QString BleeckerNumberTools::format(double value,const QString &format,const QString &currencyCode,const QLocale &locale,bool signedPercent) const {
    auto error=[](const QString &message){qFatal("%s",qPrintable(message));return QString();};
    using namespace icu::number;
    auto formatter=NumberFormatter::withLocale(icu::Locale(locale.name().toUtf8().constData()));
    if(format=="number")formatter=formatter.precision(Precision::maxFraction(6));
    else if(format=="percent")formatter=formatter.unit(icu::NoUnit::percent()).scale(Scale::powerOfTen(2)).precision(Precision::maxFraction(6));
    else if(format=="compact")formatter=formatter.notation(Notation::compactShort());
    else if(format=="currency") {
        // The recorded source framework returns Double's description when its
        // currency identifier cannot be constructed. Preserve that source path.
        if(!currencyIdentifier(currencyCode))return rawDouble(value);
        UErrorCode status=U_ZERO_ERROR;
        const icu::CurrencyUnit currency(currencyCode.toUpper().toLatin1().constData(),status);
        if(U_FAILURE(status))return error(QStringLiteral("Currency construction failed: ")+QString::fromLatin1(u_errorName(status)));
        formatter=formatter.unit(currency);
    }else return error(QStringLiteral("Unknown Bleecker metric format: ")+format);
    if(signedPercent) {
        if(format!="percent")return error(QStringLiteral("Signed metric formatting requires percent"));
        formatter=formatter.sign(UNUM_SIGN_ALWAYS);
    }
    UErrorCode status=U_ZERO_ERROR;
    const auto text=formatter.formatDouble(value,status).toString(status);
    if(U_FAILURE(status))return error(QStringLiteral("Metric formatting failed: ")+QString::fromLatin1(u_errorName(status)));
    return QString::fromUtf16(reinterpret_cast<const char16_t*>(text.getBuffer()),text.length());
}

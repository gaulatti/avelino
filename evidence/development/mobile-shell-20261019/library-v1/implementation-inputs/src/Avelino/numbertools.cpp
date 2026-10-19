#include "numbertools.h"
#include <QCoreApplication>
#include <QEvent>
#include <QQmlEngine>
#include <array>
#include <charconv>
#include <cmath>
#include <string>
#include <unicode/currunit.h>
#include <unicode/dcfmtsym.h>
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
double compactCoefficient(const icu::number::FormattedNumber &number,UErrorCode &status) {
    const auto decimal=number.toDecimalNumber<std::string>(status);
    double coefficient=0;
    const auto parsed=std::from_chars(decimal.data(),decimal.data()+decimal.size(),coefficient);
    if(parsed.ec!=std::errc{} || parsed.ptr!=decimal.data()+decimal.size())status=U_INVALID_FORMAT_ERROR;
    return std::abs(coefficient);
}
icu::UnicodeString sourceChileanCompact(double value,const icu::Locale &locale,
    const icu::number::FormattedNumber &original,UErrorCode &status) {
    auto text=original.toString(status);
    if(!std::isfinite(value))return text;
    const auto absolute=std::abs(value);
    bool nativePattern=absolute>=1e9 && absolute<1e12;
    // A rounded 999.5 million advances into the source's billion pattern.
    // Inspect ICU's rounded coefficient rather than pre-rounding the Double.
    if(absolute>=1e8 && absolute<1e9)nativePattern=compactCoefficient(original,status)>=1000;
    if(!nativePattern)return text;
    using namespace icu::number;
    const auto number=NumberFormatter::withLocale(locale).scale(Scale::powerOfTen(-9))
        .precision(Precision::integer().withMinDigits(2)).grouping(UNUM_GROUPING_OFF)
        .formatDouble(value,status);
    // Pinned native es_CL adds 0k NBSP M, 00k NBSP M and 000k NBSP M
    // for 10^9..10^11. ICU still owns decimal conversion and half-even rounding.
    // Rounding to 1000 advances to the inherited 10^12 pattern instead.
    if(compactCoefficient(number,status)<1000)
        return number.toString(status)+icu::UnicodeString::fromUTF8("k M");
    return text;
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
    const auto name=locale.name();
    const icu::Locale nativeLocale(name.toUtf8().constData());
    auto formatter=NumberFormatter::withLocale(nativeLocale);
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
    // Source data is preserved in number-locales-20261016/native-locale-data.json.
    // These are measured locale symbols, not replacements of formatted strings.
    const bool sourceYen=name=="ja_JP" && format=="currency" && currencyCode.toUpper()=="JPY";
    if(name=="ar_EG" || sourceYen) {
        icu::DecimalFormatSymbols symbols(nativeLocale,status);
        if(name=="ar_EG")symbols.setSymbol(icu::DecimalFormatSymbols::kNaNSymbol,
            icu::UnicodeString::fromUTF8("ليس رقمًا"));
        if(sourceYen)symbols.setSymbol(icu::DecimalFormatSymbols::kCurrencySymbol,
            icu::UnicodeString::fromUTF8("¥"));
        formatter=formatter.symbols(symbols);
    }
    const auto number=formatter.formatDouble(value,status);
    const auto text=name=="es_CL" && format=="compact" ? sourceChileanCompact(value,nativeLocale,number,status):number.toString(status);
    if(U_FAILURE(status))return error(QStringLiteral("Metric formatting failed: ")+QString::fromLatin1(u_errorName(status)));
    return QString::fromUtf16(reinterpret_cast<const char16_t*>(text.getBuffer()),text.length());
}

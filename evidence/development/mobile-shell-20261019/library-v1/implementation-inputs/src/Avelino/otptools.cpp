#include "otptools.h"
#include "otpunicode.h"
#include <algorithm>
#include <cmath>

namespace {
template<size_t N> bool contains(const std::array<OtpUnicode::Range,N> &ranges,char32_t scalar) {
    const auto match=std::lower_bound(ranges.begin(),ranges.end(),scalar,
        [](const OtpUnicode::Range &range,char32_t value){return range.last<value;});
    return match!=ranges.end() && match->first<=scalar;
}
qint64 checkedLength(double length) {
    if(!std::isfinite(length) || length<0 || std::floor(length)!=length || length>9007199254740991.)
        qFatal("OTP length must be a nonnegative safe integer");
    return qint64(length);
}
char32_t nextScalar(const QString &value,qsizetype &index) {
    char32_t scalar=value[index++].unicode();
    if(QChar::isHighSurrogate(scalar)) {
        if(index>=value.size() || !value[index].isLowSurrogate())qFatal("OTP code requires valid Unicode scalars");
        scalar=QChar::surrogateToUcs4(char16_t(scalar),value[index++].unicode());
    } else if(QChar::isLowSurrogate(scalar))qFatal("OTP code requires valid Unicode scalars");
    return scalar;
}
}

void BleeckerOTPTools::validate(const QString &value,double length) const {
    checkedLength(length);
    for(qsizetype index=0;index<value.size();)nextScalar(value,index);
}

QString BleeckerOTPTools::filter(const QString &value,double length) const {
    const auto limit=checkedLength(length);
    qint64 count=0;
    bool retaining=false,previousPrepend=false;
    QString result;
    result.reserve(value.size());
    for(qsizetype index=0;index<value.size();) {
        const auto start=index;
        const auto scalar=nextScalar(value,index);
        if(contains(OtpUnicode::numbers,scalar) && !previousPrepend) {
            retaining=count<limit;
            if(retaining)++count;
        } else if(!contains(OtpUnicode::joining,scalar))retaining=false;
        if(retaining)result.append(QStringView(value).mid(start,index-start));
        previousPrepend=contains(OtpUnicode::prepend,scalar);
    }
    // Scan the complete string, including after the prefix limit, to refuse
    // malformed UTF-16 rather than silently repairing or dropping its tail.
    return result;
}

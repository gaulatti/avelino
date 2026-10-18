#include "daterangetools.h"
#include <QJSValue>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLocale>
#include <QTimeZone>
#include <QFontDatabase>
#include <QFontMetricsF>
#include <algorithm>
#include <array>
#include <cmath>
#include <climits>
#include <memory>
#include <vector>
#include <unicode/calendar.h>
#include <unicode/datefmt.h>
#include <unicode/dtfmtsym.h>
#include <unicode/dtptngen.h>
#include <unicode/fieldpos.h>
#include <unicode/fpositer.h>
#include <unicode/gregocal.h>
#include <unicode/locid.h>
#include <unicode/numfmt.h>
#include <unicode/smpdtfmt.h>
#include <unicode/strenum.h>
#include <unicode/timezone.h>
#include <unicode/uchar.h>
#include <unicode/parsepos.h>

namespace {
void checked(UErrorCode status,const char *operation) {
    if(U_FAILURE(status))qFatal("DateRange %s failed: %s",operation,u_errorName(status));
}
void finite(double value) {
    if(!std::isfinite(value))qFatal("DateRange date must be finite");
}
double canonical(double value) {
    finite(value);
    // Preserve the source Date initializer's reference-date round trip.
    const double reference=value-978307200.0;
    return reference+978307200.0;
}
QString text(const icu::UnicodeString &value) {
    return QString::fromUtf16(reinterpret_cast<const char16_t*>(value.getBuffer()),value.length());
}
icu::UnicodeString unicode(const QString &value) {
    return icu::UnicodeString(reinterpret_cast<const UChar*>(value.utf16()),value.size());
}
QVariant plain(const QVariant &value) {
    return value.metaType().id()==qMetaTypeId<QJSValue>() ? value.value<QJSValue>().toVariant():value;
}
double numeric(const QVariant &input) {
    const auto value=plain(input);
    const auto type=value.metaType().id();
    if(type!=QMetaType::Double && type!=QMetaType::Float && type!=QMetaType::Int && type!=QMetaType::UInt
       && type!=QMetaType::LongLong && type!=QMetaType::ULongLong)qFatal("DateRange bounds require numeric Unix seconds");
    return canonical(value.toDouble());
}
struct Bounds {
    bool supplied=false;
    double lower=0,upper=0;
    explicit Bounds(const QVariant &input) {
        const auto value=plain(input);
        if(!value.isValid() || value.isNull())return;
        if(value.metaType().id()!=QMetaType::QVariantMap)qFatal("DateRange range must be null or a lower/upper map");
        const auto map=value.toMap();
        if(map.size()!=2 || !map.contains("lower") || !map.contains("upper"))qFatal("DateRange range requires exactly lower and upper");
        supplied=true;lower=numeric(map.value("lower"));upper=numeric(map.value("upper"));
        if(lower>upper)qFatal("DateRange lower bound exceeds upper bound");
    }
    double clamp(double value) const {return supplied ? std::max(lower,std::min(upper,value)):value;}
    bool intersects(double start,double end) const {return !supplied || (end>lower && start<=upper);}
};
QString calendarName(QString value) {
    if(value=="islamic-umm-al-qura")return QStringLiteral("islamic-umalqura");
    if(value=="islamic-tabular")return QStringLiteral("islamic-tbla");
    if(value=="ethioaa")return QStringLiteral("ethiopic-amete-alem");
    return value;
}
icu::Locale localeFor(const QString &name,const QString &calendar) {
    if(name.isEmpty())qFatal("DateRange locale is required");
    auto locale=icu::Locale::createCanonical(name.toUtf8().constData());
    if(locale.isBogus())qFatal("DateRange locale is invalid");
    UErrorCode status=U_ZERO_ERROR;
    std::unique_ptr<icu::StringEnumeration> calendars(icu::Calendar::getKeywordValuesForLocale("calendar",locale,false,status));
    checked(status,"calendar enumeration");
    const auto requested=calendarName(calendar).toUtf8();
    bool found=false;int32_t length=0;
    while(const auto item=calendars->next(&length,status))if(QByteArray(item,length)==requested)found=true;
    checked(status,"calendar enumeration");
    if(!found)qFatal("DateRange calendar is unsupported: %s",qPrintable(calendar));
    locale.setKeywordValue("calendar",requested.constData(),status);checked(status,"calendar locale");
    return locale;
}
std::unique_ptr<icu::Calendar> calendarFor(const QString &locale,const QString &calendar,const QString &zone) {
    if(zone.isEmpty())qFatal("DateRange time zone is required");
    UErrorCode status=U_ZERO_ERROR;icu::UnicodeString canonicalZone;
    icu::TimeZone::getCanonicalID(unicode(zone),canonicalZone,status);checked(status,"time zone identifier");
    std::unique_ptr<icu::TimeZone> timeZone(icu::TimeZone::createTimeZone(canonicalZone));
    auto nativeLocale=localeFor(locale,calendar);
    std::unique_ptr<icu::Calendar> result(icu::Calendar::createInstance(timeZone.release(),nativeLocale,status));
    checked(status,"calendar construction");
    result->setLenient(true);
    if(calendar=="iso8601"){result->setFirstDayOfWeek(UCAL_MONDAY);result->setMinimalDaysInFirstWeek(4);}
    return result;
}
void setTime(icu::Calendar &calendar,double value) {
    finite(value);UErrorCode status=U_ZERO_ERROR;
    // ICU owns calendrical fields; retain subsecond data outside its fields.
    calendar.setTime(std::floor(value)*1000.0,status);checked(status,"calendar time");
}
double seconds(icu::Calendar &calendar) {
    UErrorCode status=U_ZERO_ERROR;const auto value=calendar.getTime(status)/1000.0;
    checked(status,"calendar instant");return value;
}
int field(icu::Calendar &calendar,UCalendarDateFields value) {
    UErrorCode status=U_ZERO_ERROR;const auto result=calendar.get(value,status);checked(status,"calendar field");return result;
}
UCalendarDateFields dateField(const QString &name) {
    if(name=="year" || name=="yearName" || name=="relatedYear")return UCAL_YEAR;
    if(name=="month")return UCAL_MONTH;
    if(name=="day")return UCAL_DATE;
    if(name=="era")return UCAL_ERA;
    qFatal("Unknown DateRange field: %s",qPrintable(name));
    return UCAL_DATE;
}
std::unique_ptr<icu::SimpleDateFormat> formatter(const QString &locale,const QString &calendar,const QString &zone,const char *skeleton) {
    const auto nativeLocale=localeFor(locale,calendar);UErrorCode status=U_ZERO_ERROR;
    std::unique_ptr<icu::DateTimePatternGenerator> generator(icu::DateTimePatternGenerator::createInstance(nativeLocale,status));
    checked(status,"date pattern generator");
    const auto pattern=generator->getBestPattern(icu::UnicodeString::fromUTF8(skeleton),status);checked(status,"date pattern");
    std::unique_ptr<icu::SimpleDateFormat> result(new icu::SimpleDateFormat(pattern,nativeLocale,status));checked(status,"date formatter");
    result->adoptCalendar(calendarFor(locale,calendar,zone).release());return result;
}
std::unique_ptr<icu::SimpleDateFormat> editorFormatter(const QString &locale,const QString &calendar,const QString &zone) {
    std::unique_ptr<icu::DateFormat> base(icu::DateFormat::createDateInstance(icu::DateFormat::kShort,localeFor(locale,calendar)));
    auto simple=dynamic_cast<icu::SimpleDateFormat*>(base.get());
    if(!simple)qFatal("DateRange short-date formatter is unavailable");
    static const QJsonObject presentation=[](){
        QFile file(QStringLiteral(":/qt/qml/Avelino/date-editor-patterns.json"));
        if(!file.open(QIODevice::ReadOnly))qFatal("Pinned date editor patterns are unavailable");
        QJsonParseError error;const auto document=QJsonDocument::fromJson(file.readAll(),&error);
        const auto object=document.object();
        if(error.error!=QJsonParseError::NoError||object["schemaVersion"]!=2||object["reference"]!="fe8a1d462fbd793d883fb92086a16aa2947e32c9"||!object["patterns"].isObject()||!object["numberingOverrides"].isObject())qFatal("Invalid pinned date editor patterns");
        return object;
    }();
    const auto patterns=presentation["patterns"].toObject();
    icu::UnicodeString pattern;simple->toPattern(pattern);
    const auto key=QString::fromLatin1(localeFor(locale,calendar).getBaseName())+"|"+calendarName(calendar);
    if(patterns.contains(key)){
        if(!patterns[key].isString()||patterns[key].toString().isEmpty())qFatal("Invalid native date pattern");
        pattern=unicode(patterns[key].toString());
    }
    icu::UnicodeString fullYear;bool quoted=false;
    for(int i=0;i<pattern.length();++i){
        const auto point=pattern.charAt(i);fullYear.append(point);
        if(point==u'\''){
            if(i+1<pattern.length()&&pattern.charAt(i+1)==point){fullYear.append(point);++i;}
            else quoted=!quoted;
        }else if(!quoted&&(point==u'y'||point==u'r'))while(i+1<pattern.length()&&pattern.charAt(i+1)==point)++i;
    }
    // Preserve the locale's date-style number-format overrides (for example
    // Hebrew numerals); reconstructing a formatter from its pattern loses them.
    simple->applyPattern(fullYear);simple->adoptCalendar(calendarFor(locale,calendar,zone).release());
    const auto overrides=presentation["numberingOverrides"].toObject();
    if(overrides.contains(key)){
        if(!overrides[key].isObject())qFatal("Invalid native date field numbering");
        const auto fields=overrides[key].toObject();
        for(auto field=fields.begin();field!=fields.end();++field){
            if(field.key().size()!=1||!field.value().isString()||field.value().toString().isEmpty())qFatal("Invalid native date field numbering rule");
            auto numberLocale=localeFor(locale,calendar);UErrorCode status=U_ZERO_ERROR;
            numberLocale.setKeywordValue("numbers",field.value().toString().toUtf8().constData(),status);checked(status,"date field numbering locale");
            auto numbers=icu::NumberFormat::createInstance(numberLocale,status);checked(status,"date field numbering formatter");
            simple->adoptNumberFormat(unicode(field.key()),numbers,status);checked(status,"date field numbering override");
        }
    }
    base.release();return std::unique_ptr<icu::SimpleDateFormat>(simple);
}
QString dateFieldText(const QString &part,const QString &input) {
    const int minimum=part=="year"||part=="relatedYear" ? 4:part=="month"||part=="day" ? 2:0;
    const auto points=input.toUcs4();
    for(auto point:points)if(u_charType(UChar32(point))!=U_DECIMAL_DIGIT_NUMBER)return input;
    return QString(std::max(0,minimum-int(points.size())),QChar(0x2007))+input;
}
QString formatted(icu::SimpleDateFormat &formatter,double value) {
    icu::UnicodeString result;formatter.format(value*1000.0,result);return text(result);
}
int relatedYear(double value,const QString &locale,const QString &calendar,const QString &zone) {
    UErrorCode status=U_ZERO_ERROR;icu::SimpleDateFormat output(icu::UnicodeString("r"),localeFor(locale,calendar),status);
    checked(status,"related year formatter");output.adoptCalendar(calendarFor(locale,calendar,zone).release());
    const auto string=formatted(output,value);qint64 number=0;bool negative=false;
    for(auto point:string.toUcs4()){
        if(point=='-' || point==0x2212){negative=true;continue;}
        const auto digit=u_charDigitValue(UChar32(point));
        if(digit<0 || number>(INT_MAX-digit)/10)qFatal("Invalid DateRange related year");number=number*10+digit;
    }
    return int(negative ? -number:number);
}
QString fieldKind(int id) {
    if(id==UDAT_YEAR_FIELD || id==UDAT_YEAR_WOY_FIELD || id==UDAT_EXTENDED_YEAR_FIELD)return QStringLiteral("year");
    if(id==UDAT_RELATED_YEAR_FIELD)return QStringLiteral("relatedYear");
    if(id==UDAT_YEAR_NAME_FIELD)return QStringLiteral("yearName");
    if(id==UDAT_MONTH_FIELD || id==UDAT_STANDALONE_MONTH_FIELD)return QStringLiteral("month");
    if(id==UDAT_DATE_FIELD)return QStringLiteral("day");
    if(id==UDAT_ERA_FIELD)return QStringLiteral("era");
    qFatal("Unexpected DateRange formatted field: %d",id);return {};
}
QVariantMap datePresentation(icu::SimpleDateFormat &native,double value,bool padded) {
    UErrorCode status=U_ZERO_ERROR;icu::UnicodeString output;icu::FieldPositionIterator positions;
    native.format(value*1000.0,output,&positions,status);checked(status,"date formatting");
    struct Piece {int first,last,id;};std::vector<Piece> fields;icu::FieldPosition position;
    while(positions.next(position))fields.push_back({position.getBeginIndex(),position.getEndIndex(),position.getField()});
    std::sort(fields.begin(),fields.end(),[](const Piece &a,const Piece &b){return a.first<b.first;});
    const auto string=text(output);QString displayed;QVariantList segments;int offset=0;
    for(const auto &piece:fields){
        if(piece.first<offset || piece.last>string.size())qFatal("Overlapping DateRange formatted fields");
        if(piece.first>offset){const auto literal=string.mid(offset,piece.first-offset);segments.append(QVariantMap{{"kind","literal"},{"text",literal}});displayed+=literal;}
        const auto kind=fieldKind(piece.id),raw=string.mid(piece.first,piece.last-piece.first);
        const auto value=padded ? dateFieldText(kind,raw):raw;const int first=displayed.size();displayed+=value;
        segments.append(QVariantMap{{"kind",kind},{"text",value},{"first",first},{"last",displayed.size()}});offset=piece.last;
    }
    if(offset<string.size()){const auto literal=string.mid(offset);segments.append(QVariantMap{{"kind","literal"},{"text",literal}});displayed+=literal;}
    return {{"text",displayed},{"segments",segments}};
}
std::vector<double> sizingDates(icu::Calendar &calendar) {
    // The native field reserves representative calendar samples, independently
    // of the edited date. Public sizing/font probes validate this recipe; these
    // are neither allowed-date bounds nor an assumed longest year/month.
    static constexpr std::array<std::array<int,7>,15> samples={{
        {1,2066,10,26,12,26,26},{1,2000,10,30,12,59,59},
        {1,4444,10,30,10,44,44},{1,2000,10,30,23,59,59},
        {1,4444,4,4,0,44,44},{1,4444,4,4,4,44,44},
        {1,3920,6,25,12,59,59},{1,3920,6,25,20,44,44},
        {1,8204,7,27,20,44,44},{1,8204,7,29,20,44,44},
        {1,5761,1,6,0,0,0},{0,1435,9,6,16,20,44},
        {0,1435,9,10,12,44,44},{0,7777,12,12,12,57,57},
        {0,7777,7,7,7,7,7}
    }};
    // Cyclic calendars have astronomical maximum eras. Build the sizing
    // samples in the current era, independently of the edited date's era.
    const int positiveEra=field(calendar,UCAL_ERA);
    std::vector<double> dates={978307200.0};
    for(const auto &sample:samples){
        calendar.clear();calendar.set(UCAL_ERA,sample[0] ? positiveEra:0);
        calendar.set(sample[1],sample[2]-1,sample[3],sample[4],sample[5],sample[6]);
        dates.push_back(seconds(calendar));
    }
    return dates;
}
QString measurementText(QString value,bool literal,bool rtl) {
    if(literal&&rtl){
        auto points=value.toUcs4();std::reverse(points.begin(),points.end());
        value=QString::fromUcs4(points.constData(),points.size());
    }
    // Native NSString measurement excludes trailing whitespace in an RTL
    // paragraph, while Latin/neutral and all-space literals retain it.
    if(value.isRightToLeft())while(!value.isEmpty()&&value.back().isSpace())value.chop(1);
    return value;
}

}

double DateRangeTools::fromUnixSeconds(double value) const {return canonical(value);}
double DateRangeTools::clamped(double value,const QVariant &range) const {return Bounds(range).clamp(canonical(value));}
QString DateRangeTools::systemTimeZone() const {return QString::fromUtf8(QTimeZone::systemTimeZoneId());}
QString DateRangeTools::calendarForLocale(const QString &locale) const {
    UErrorCode status=U_ZERO_ERROR;
    std::unique_ptr<icu::Calendar> value(icu::Calendar::createInstance(icu::Locale::createCanonical(locale.toUtf8().constData()),status));
    checked(status,"default calendar");return QString::fromLatin1(value->getType());
}
QVariantMap DateRangeTools::parts(double value,const QString &locale,const QString &calendar,const QString &timeZone) const {
    value=canonical(value);auto native=calendarFor(locale,calendar,timeZone);setTime(*native,value);
    UErrorCode status=U_ZERO_ERROR;const auto maximum=native->getActualMaximum(UCAL_DATE,status);checked(status,"month range");
    return {{"instant",value},{"era",field(*native,UCAL_ERA)},{"year",field(*native,UCAL_YEAR)},
        {"extendedYear",field(*native,UCAL_EXTENDED_YEAR)},{"month",field(*native,UCAL_MONTH)+1},
        {"day",field(*native,UCAL_DATE)},{"hour",field(*native,UCAL_HOUR_OF_DAY)},{"minute",field(*native,UCAL_MINUTE)},
        {"second",field(*native,UCAL_SECOND)},{"nanosecond",qint64(std::llround((value-std::floor(value))*1e9))},
        {"weekday",field(*native,UCAL_DAY_OF_WEEK)},{"weekOfYear",field(*native,UCAL_WEEK_OF_YEAR)},
        {"yearForWeekOfYear",field(*native,UCAL_YEAR_WOY)},{"leapMonth",bool(field(*native,UCAL_IS_LEAP_MONTH))},
        {"daysInMonth",maximum},{"firstWeekday",int(native->getFirstDayOfWeek())},
        {"minimumDaysInFirstWeek",int(native->getMinimalDaysInFirstWeek())}};
}
QVariantMap DateRangeTools::formatted(double value,const QString &locale,const QString &calendar,const QString &timeZone) const {
    auto native=formatter(locale,calendar,timeZone,"yMd");return datePresentation(*native,canonical(value),false);
}
QVariantMap DateRangeTools::editorFormatted(double value,const QString &locale,const QString &calendar,const QString &timeZone) const {
    auto native=editorFormatter(locale,calendar,timeZone);return datePresentation(*native,canonical(value),true);
}
QString DateRangeTools::editorFieldText(const QString &part,const QString &input) const {return dateFieldText(part,input);}
double DateRangeTools::stepped(double value,const QString &part,int amount,const QString &locale,const QString &calendar,const QString &timeZone,const QVariant &range) const {
    value=canonical(value);auto native=calendarFor(locale,calendar,timeZone);setTime(*native,value);
    UErrorCode status=U_ZERO_ERROR;native->add(dateField(part),amount,status);checked(status,"date step");
    return Bounds(range).clamp(canonical(seconds(*native)+(value-std::floor(value))));
}
double DateRangeTools::replaced(double value,const QString &part,int number,const QString &locale,const QString &calendar,const QString &timeZone,const QVariant &range) const {
    value=canonical(value);auto native=calendarFor(locale,calendar,timeZone);setTime(*native,value);
    if(part=="relatedYear"){
        UErrorCode status=U_ZERO_ERROR;native->add(UCAL_YEAR,number-relatedYear(value,locale,calendar,timeZone),status);checked(status,"related year replacement");
    }else if(part=="year" || part=="yearName" || part=="month" || part=="era"){
        const auto previousDay=field(*native,UCAL_DATE);native->set(UCAL_DATE,1);
        native->set(dateField(part),part=="month" ? number-1:number);
        UErrorCode status=U_ZERO_ERROR;const auto maximum=native->getActualMaximum(UCAL_DATE,status);checked(status,"replacement month range");
        native->set(UCAL_DATE,std::min(previousDay,maximum));
    }else native->set(dateField(part),number);
    return Bounds(range).clamp(canonical(seconds(*native)+(value-std::floor(value))));
}
double DateRangeTools::midnight(double value,const QString &locale,const QString &calendar,const QString &timeZone) const {
    auto native=calendarFor(locale,calendar,timeZone);setTime(*native,canonical(value));
    native->set(UCAL_HOUR_OF_DAY,0);native->set(UCAL_MINUTE,0);native->set(UCAL_SECOND,0);native->set(UCAL_MILLISECOND,0);
    return canonical(seconds(*native));
}
double DateRangeTools::previewedDay(double value,int amount,const QString &locale,const QString &calendar,const QString &timeZone,const QVariant &range) const {
    // The observed graphical keyboard path drops fractional seconds, retaining
    // hour/minute/second. Midnight is only used for calendar cell boundaries.
    const auto next=stepped(value,QStringLiteral("day"),amount,locale,calendar,timeZone,{});
    return Bounds(range).clamp(canonical(std::floor(next)));
}
double DateRangeTools::selectingDay(double value,double day,const QString &locale,const QString &calendar,const QString &timeZone,const QVariant &range) const {
    value=canonical(value);auto native=calendarFor(locale,calendar,timeZone),selected=calendarFor(locale,calendar,timeZone);
    setTime(*native,value);setTime(*selected,canonical(day));
    // Transfer the complete calendar date, retaining the original local time.
    native->set(UCAL_ERA,field(*selected,UCAL_ERA));native->set(UCAL_YEAR,field(*selected,UCAL_YEAR));
    native->set(UCAL_MONTH,field(*selected,UCAL_MONTH));native->set(UCAL_IS_LEAP_MONTH,field(*selected,UCAL_IS_LEAP_MONTH));
    native->set(UCAL_DATE,field(*selected,UCAL_DATE));
    return Bounds(range).clamp(canonical(seconds(*native)+(value-std::floor(value))));
}
QVariantMap DateRangeTools::month(double value,const QString &locale,const QString &calendar,const QString &timeZone,const QVariant &range) const {
    value=canonical(value);const Bounds bounds(range);auto native=calendarFor(locale,calendar,timeZone);setTime(*native,value);
    const auto year=field(*native,UCAL_EXTENDED_YEAR),monthIndex=field(*native,UCAL_MONTH);
    const auto firstWeekday=int(native->getFirstDayOfWeek());
    auto title=formatter(locale,calendar,timeZone,"yMMM");
    UErrorCode status=U_ZERO_ERROR;icu::DateFormatSymbols symbols(localeFor(locale,calendar),status);checked(status,"calendar labels");
    int32_t count=0;const auto names=symbols.getWeekdays(count,icu::DateFormatSymbols::FORMAT,icu::DateFormatSymbols::SHORT);
    QVariantList weekdays;for(int i=0;i<7;++i){const auto day=(firstWeekday-1+i)%7+1;if(day>=count)qFatal("Missing DateRange weekday label");weekdays.append(text(names[day]));}
    native->set(UCAL_DATE,1);native->set(UCAL_HOUR_OF_DAY,0);native->set(UCAL_MINUTE,0);native->set(UCAL_SECOND,0);native->set(UCAL_MILLISECOND,0);
    const auto leading=(field(*native,UCAL_DAY_OF_WEEK)-firstWeekday+7)%7;
    native->add(UCAL_DATE,-leading,status);checked(status,"calendar first week");QVariantList days;
    auto label=formatter(locale,calendar,timeZone,"d");
    for(int i=0;i<42;++i){
        const auto start=seconds(*native);const auto inMonth=field(*native,UCAL_EXTENDED_YEAR)==year && field(*native,UCAL_MONTH)==monthIndex;
        native->add(UCAL_DATE,1,status);checked(status,"calendar day");const auto end=seconds(*native);
        days.append(QVariantMap{{"instant",start},{"end",end},{"text",::formatted(*label,start)},
            {"inMonth",inMonth},{"enabled",bounds.intersects(start,end)},
            {"selected",start<=value && value<end}});
    }
    return {{"title",::formatted(*title,value)},{"weekdays",weekdays},{"days",days},{"firstWeekday",firstWeekday}};
}
QFont DateRangeTools::systemFont(int pixels) const {
    if(pixels<=0)qFatal("DateRange font size must be positive");
    auto font=QFontDatabase::systemFont(QFontDatabase::GeneralFont);font.setPixelSize(pixels);
    font.clearFeatures();font.setFeature(QFont::Tag("tnum"),1);
    font.setWeight(QFont::Normal);font.setStyleName({});font.setItalic(false);font.setUnderline(false);
    font.setStrikeOut(false);font.setOverline(false);font.setResolveMask(QFont::AllPropertiesResolved);return font;
}
QVariantMap DateRangeTools::presentation(const QString &style,const QString &size) const {
    if(style!="inherit" && style!="automatic" && style!="compact" && style!="stepperField" && style!="field" && style!="graphical")qFatal("Unknown DateRange picker style");
    int pixels=13,fieldHeight=21,stepperHeight=20,stepperWidth=17;
    if(size=="mini"){pixels=9;fieldHeight=16;stepperHeight=16;stepperWidth=11;}
    else if(size=="small"){pixels=11;fieldHeight=19;stepperHeight=18;stepperWidth=15;}
    else if(size=="large"){stepperHeight=24;stepperWidth=20;}
    else if(size!="regular")qFatal("Unknown DateRange control size");
    return {{"fontPixels",pixels},{"fieldHeight",style=="field" ? fieldHeight:stepperHeight},
        {"stepperWidth",style=="field" ? 0:stepperWidth},{"overlay",style!="field" && style!="graphical"},
        {"graphical",style=="graphical"},{"calendarWidth",138.5},{"calendarHeight",148}};
}
qreal DateRangeTools::fieldTextWidth(double value,const QString &locale,const QString &calendar,const QString &timeZone,int pixels) const {
    canonical(value);
    qreal width=0;for(const auto &reserved:fieldWidths(locale,calendar,timeZone,pixels))width+=reserved.toReal();return width;
}
QVariantList DateRangeTools::fieldWidths(const QString &locale,const QString &calendar,const QString &timeZone,int pixels) const {
    const QFontMetricsF metrics(systemFont(pixels));auto output=editorFormatter(locale,calendar,timeZone);
    auto native=calendarFor(locale,calendar,timeZone);const bool rtl=QLocale(locale).textDirection()==Qt::RightToLeft;
    std::vector<qreal> widths;QStringList kinds;
    for(const auto date:sizingDates(*native)){
        const auto segments=datePresentation(*output,date,false)["segments"].toList();
        if(widths.empty()){
            widths.resize(segments.size(),0);
            for(const auto &segment:segments)kinds.append(segment.toMap()["kind"].toString());
        }
        if(segments.size()!=qsizetype(widths.size()))qFatal("DateRange sizing samples changed field structure");
        for(qsizetype index=0;index<segments.size();++index){
            const auto segment=segments[index].toMap();const auto kind=segment["kind"].toString();
            if(kind!=kinds[index])qFatal("DateRange sizing samples changed field kind");
            widths[index]=std::max(widths[index],metrics.horizontalAdvance(measurementText(segment["text"].toString(),kind=="literal",rtl)));
        }
    }
    QVariantList result;for(const auto reserved:widths)result.append(reserved);return result;
}
QVariantMap DateRangeTools::parsedField(double value,const QString &part,const QString &input,const QString &locale,const QString &calendar,const QString &timeZone) const {
    auto native=calendarFor(locale,calendar,timeZone);setTime(*native,canonical(value));
    const auto key=part=="yearName" ? QStringLiteral("year"):part;
    const auto type=key=="relatedYear" ? UCAL_YEAR:dateField(key);
    UErrorCode status=U_ZERO_ERROR;int minimum=native->getActualMinimum(type,status),maximum=native->getActualMaximum(type,status);checked(status,"editable field range");
    if(type==UCAL_MONTH){++minimum;++maximum;}
    if(part=="relatedYear"){
        const auto offset=field(*native,UCAL_EXTENDED_YEAR)-relatedYear(value,locale,calendar,timeZone);
        minimum=native->getActualMinimum(UCAL_EXTENDED_YEAR,status)-offset;
        maximum=native->getActualMaximum(UCAL_EXTENDED_YEAR,status)-offset;checked(status,"related year range");
    }
    qint64 number=0;bool digits=!input.isEmpty();
    for(auto point:input.toUcs4()){
        const auto digit=u_charDigitValue(UChar32(point));
        if(digit<0 || u_charType(UChar32(point))!=U_DECIMAL_DIGIT_NUMBER || number>(INT_MAX-digit)/10){digits=false;break;}
        number=number*10+digit;
    }
    if(!digits && type==UCAL_MONTH && !input.isEmpty()){
        auto display=formatter(locale,calendar,timeZone,"MMM");native->set(UCAL_DATE,1);
        for(int month=minimum;month<=maximum;++month){native->set(UCAL_MONTH,month-1);
            if(::formatted(*display,seconds(*native)).compare(input,Qt::CaseInsensitive)==0){digits=true;number=month;break;}}
    }
    bool named=false;
    if(!digits && !input.isEmpty() && (part=="era" || part=="yearName")){
        icu::DateFormatSymbols symbols(localeFor(locale,calendar),status);checked(status,"date field names");
        const auto match=[&](const icu::UnicodeString *names,int32_t count,int offset){
            for(int i=0;i<count;++i)if(text(names[i]).compare(input,Qt::CaseInsensitive)==0){number=i+offset;named=true;break;}
        };
        int32_t count=0;
        if(part=="yearName"){
            const auto names=symbols.getYearNames(count,icu::DateFormatSymbols::FORMAT,icu::DateFormatSymbols::ABBREVIATED);match(names,count,1);
        }else{
            const auto shortNames=symbols.getEras(count);match(shortNames,count,0);
            const auto longNames=symbols.getEraNames(count);match(longNames,count,0);
            const auto narrow=symbols.getNarrowEras(count);match(narrow,count,0);
        }
    }
    bool algorithmic=false;
    if(!digits&&!named&&!input.isEmpty()){
        const auto presentation=editorFormatted(value,locale,calendar,timeZone);
        for(const auto &segment:presentation.value("segments").toList()){
            const auto item=segment.toMap();if(item.value("kind").toString()!=part)continue;
            auto replacement=presentation.value("text").toString();replacement.replace(item.value("first").toInt(),item.value("last").toInt()-item.value("first").toInt(),input);
            const auto parsed=parsedDate(value,replacement,locale,calendar,timeZone,{});
            if(parsed.value("valid").toBool()){
                auto date=calendarFor(locale,calendar,timeZone);setTime(*date,parsed.value("instant").toDouble());
                number=part=="relatedYear" ? relatedYear(parsed.value("instant").toDouble(),locale,calendar,timeZone):field(*date,type)+(type==UCAL_MONTH?1:0);algorithmic=true;
            }
            break;
        }
    }
    const bool valid=(digits||named||algorithmic) && number>=minimum && number<=maximum;
    return {{"valid",valid},{"number",number},{"minimum",minimum},{"maximum",maximum},
        {"complete",valid && (named || (type==UCAL_YEAR ? input.size()>=4:number*10>maximum))}};
}
QVariantMap DateRangeTools::parsedDate(double value,const QString &input,const QString &locale,const QString &calendar,const QString &timeZone,const QVariant &range) const {
    value=canonical(value);auto native=calendarFor(locale,calendar,timeZone);setTime(*native,value);
    auto parser=editorFormatter(locale,calendar,timeZone);parser->setLenient(false);native->setLenient(false);
    const auto source=QString(input).remove(QChar(0x2007));
    icu::ParsePosition position(0);parser->parse(unicode(source),*native,position);
    UErrorCode status=U_ZERO_ERROR;const auto parsed=native->getTime(status)/1000.0;
    if(U_FAILURE(status) || position.getErrorIndex()>=0 || position.getIndex()!=source.size())return {{"valid",false}};
    return {{"valid",true},{"instant",Bounds(range).clamp(canonical(parsed+(value-std::floor(value))))}};
}

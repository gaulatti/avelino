#include <unicode/datefmt.h>
#include <unicode/smpdtfmt.h>
#include <unicode/timezone.h>
#include <unicode/uversion.h>
#include <unicode/numfmt.h>
#include <iostream>
#include <memory>
#include <string>
std::string utf8(const icu::UnicodeString &value){std::string result;value.toUTF8String(result);return result;}
int main(){
    UVersionInfo version;u_getVersion(version);char name[U_MAX_VERSION_STRING_LENGTH];u_versionToString(version,name);std::cout<<"ICU "<<name<<'\n';
    for(const char *locale:{"en_US@calendar=chinese","zh_CN@calendar=chinese","ko_KR@calendar=chinese"}){
        std::unique_ptr<icu::DateFormat> base(icu::DateFormat::createDateInstance(icu::DateFormat::kShort,icu::Locale(locale)));
        auto format=dynamic_cast<icu::SimpleDateFormat*>(base.get());if(!format)return 1;
        std::unique_ptr<icu::TimeZone> zone(icu::TimeZone::createTimeZone("UTC"));format->setTimeZone(*zone);
        icu::UnicodeString pattern;format->toPattern(pattern);std::cout<<locale<<" short "<<utf8(pattern)<<'\n';
        if(std::string(locale).find("zh_CN")==0){
            UErrorCode status=U_ZERO_ERROR;auto numberLocale=icu::Locale(locale);numberLocale.setKeywordValue("numbers","hanidays",status);
            auto numbers=icu::NumberFormat::createInstance(numberLocale,status);if(U_FAILURE(status))return 2;
            format->adoptNumberFormat(icu::UnicodeString("d"),numbers,status);if(U_FAILURE(status))return 3;
        }
        for(const char *candidate:{"r年MMMd","MMMddd","MMMd","M/d/'r'","M. d.","d","ddd","y","r"}){
            format->applyPattern(icu::UnicodeString::fromUTF8(candidate));icu::UnicodeString text;
            format->format(1710000000625.0,text);std::cout<<candidate<<" -> "<<utf8(text)<<'\n';
        }
    }
}

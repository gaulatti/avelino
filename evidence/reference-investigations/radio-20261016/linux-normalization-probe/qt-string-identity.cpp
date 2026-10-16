#include <QCoreApplication>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QString>
QString string(const QJsonArray &scalars) {
 QList<char32_t> codepoints;
 for(const auto &value:scalars)codepoints.append(static_cast<char32_t>(value.toInt()));
 return QString::fromUcs4(codepoints.constData(),codepoints.size());
}
int main(int argc,char**argv){
 QCoreApplication app(argc,argv);QFile input(argv[1]);if(!input.open(QIODevice::ReadOnly))return 2;
 const auto native=QJsonDocument::fromJson(input.readAll()).object();QJsonArray rows;int mismatches=0;
 for(const auto &value:native["results"].toArray()){
  auto row=value.toObject();const auto a=string(row["left"].toArray()),b=string(row["right"].toArray());
  const bool equal=a.normalized(QString::NormalizationForm_D)==b.normalized(QString::NormalizationForm_D);
  if(equal!=row["equal"].toBool())++mismatches;
  row["qtCanonicalEqual"]=equal;rows.append(row);
 }
 QFile output(argv[2]);if(!output.open(QIODevice::WriteOnly))return 3;
 output.write(QJsonDocument(QJsonObject{{"qtVersion",qVersion()},{"qcharUnicodeVersion",int(QChar::currentUnicodeVersion())},{"mismatches",mismatches},{"results",rows}}).toJson());return 0;
}

#include <QColorSpace>
#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QImage>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
int main(int argc,char **argv){
 QCoreApplication app(argc,argv);
 QFile file("/probe/capture-profile.icc");if(!file.open(QIODevice::ReadOnly))return 1;
 const auto target=QColorSpace::fromIccProfile(file.readAll());if(!target.isValid())return 2;
 QJsonArray results;
 for(const auto &name:QDir("/probe/raw").entryList({"*.png"},QDir::Files,QDir::Name)){
  QImage raw("/probe/raw/"+name);if(raw.isNull())return 3;
  const bool embedded=raw.colorSpace().isValid();
  raw.setColorSpace(QColorSpace::SRgb);
  const auto converted=raw.convertedToColorSpace(target);
  if(converted.isNull()||!converted.save("/probe/matched/"+name))return 4;
  results.append(QJsonObject{{"name",name},{"rawHadEmbeddedSpace",embedded},{"assumedRawColorSpace","Qt default sRGB"},{"targetDescription",target.description()},{"width",raw.width()},{"height",raw.height()}});
 }
 QFile output("/probe/profile-result.json");if(!output.open(QIODevice::WriteOnly|QIODevice::NewOnly))return 5;
 output.write(QJsonDocument(results).toJson());return results.size()==80?0:6;
}

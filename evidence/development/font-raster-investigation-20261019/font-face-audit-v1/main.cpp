#include <QGuiApplication>
#include <QFontDatabase>
#include <QRawFont>
#include <QTextLayout>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QFile>
#include <QDir>
#include <QCryptographicHash>
#include <QtEndian>
#include <cstdio>
static QString sha(const QByteArray &bytes){return QCryptographicHash::hash(bytes,QCryptographicHash::Sha256).toHex();}
static QJsonObject tables(const QRawFont &raw){QJsonObject result;for(const auto *tag:{"head","hhea","hmtx","maxp","OS/2","cmap","loca","glyf","name","GPOS","GSUB"}){auto data=raw.fontTable(tag);if(!data.isEmpty())result.insert(tag,sha(data));}return result;}
int main(int argc,char **argv){
 QGuiApplication app(argc,argv);if(argc!=3)return 2;
 QDir fonts(argv[1]);
 for(const auto &family:{QStringLiteral("EncodeSans"),QStringLiteral("LibreFranklin")})
  for(const auto &weight:{QStringLiteral("Thin"),QStringLiteral("ExtraLight"),QStringLiteral("Light"),QStringLiteral("Regular"),QStringLiteral("Medium"),QStringLiteral("SemiBold"),QStringLiteral("Bold"),QStringLiteral("ExtraBold"),QStringLiteral("Black")})
   if(QFontDatabase::addApplicationFont(fonts.filePath(family+"-"+weight+".ttf"))<0)return 3;
 QJsonArray records;
 for(const auto &family:{QStringLiteral("primary"),QStringLiteral("secondary")})
  for(const auto &weight:{QStringLiteral("regular"),QStringLiteral("medium"),QStringLiteral("bold")})
   for(int size:{12,15,18,23})for(const auto &text:{QStringLiteral("Short"),QStringLiteral("Tall"),QStringLiteral("Keep edition")}){
    QFont request(family=="primary"?"Encode Sans":"Libre Franklin");request.setWeight(weight=="regular"?QFont::Normal:weight=="medium"?QFont::Medium:QFont::Bold);request.setPixelSize(1000);
    auto physical=QRawFont::fromFont(request);const auto head=physical.fontTable("head");if(head.size()<20)return 4;
    int units=qFromBigEndian<quint16>(reinterpret_cast<const uchar*>(head.constData()+18));
    QFont shape=request;shape.setPixelSize(units);shape.setStyleStrategy(QFont::StyleStrategy(shape.styleStrategy()|QFont::PreferTypoLineMetrics));
    QTextOption option;option.setUseDesignMetrics(true);option.setWrapMode(QTextOption::NoWrap);option.setFlags(QTextOption::IncludeTrailingSpaces);
    QTextLayout layout(text,shape);layout.setTextOption(option);layout.beginLayout();auto line=layout.createLine();line.setLineWidth(1000000);line.setPosition(QPointF(0,-line.ascent()));layout.endLayout();
    QJsonArray runs;
    for(const auto &glyph:line.glyphRuns()){
     auto raw=glyph.rawFont();QJsonArray indexes,positions,advances;auto ids=glyph.glyphIndexes();auto points=glyph.positions();auto widths=raw.advancesForGlyphIndexes(ids);
     for(qsizetype i=0;i<ids.size();++i){indexes.append(int(ids[i]));positions.append(QJsonObject{{"x",points[i].x()*size/units},{"y",points[i].y()*size/units}});advances.append(QJsonObject{{"x",widths[i].x()*size/units},{"y",widths[i].y()*size/units}});}
     QFont paint=request;paint.setFamily(raw.familyName());paint.setStyleName(raw.styleName());paint.setWeight(QFont::Weight(raw.weight()));paint.setPixelSize(1000);auto paintFont=QRawFont::fromFont(paint);paintFont.setPixelSize(size);
     runs.append(QJsonObject{{"family",raw.familyName()},{"style",raw.styleName()},{"weight",raw.weight()},{"glyphs",indexes},{"positions",positions},{"advances",advances},{"shapeTables",tables(raw)},{"paintTables",tables(paintFont)},{"paintStyle",paintFont.styleName()},{"paintWeight",paintFont.weight()},{"paintPixelSize",paintFont.pixelSize()},{"paintHintingPreference",int(paintFont.hintingPreference())}});
    }
    records.append(QJsonObject{{"family",family},{"weight",weight},{"size",size},{"text",text},{"unitsPerEm",units},{"glyphRuns",runs}});
   }
 QFile out(argv[2]);if(!out.open(QIODevice::WriteOnly))return 5;out.write(QJsonDocument(QJsonObject{{"qt",qVersion()},{"records",records},{"accepted",false}}).toJson());return 0;
}

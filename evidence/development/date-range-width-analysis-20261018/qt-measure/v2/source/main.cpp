#include <QGuiApplication>
#include <QQmlEngine>
#include <QQmlComponent>
#include <QFile>
#include <QJsonDocument>
#include <QDebug>
int main(int argc,char **argv){
    QGuiApplication app(argc,argv);if(argc!=3)return 2;
    QFile input(argv[1]);if(!input.open(QIODevice::ReadOnly))return 3;
    QJsonParseError error;const auto data=QJsonDocument::fromJson(input.readAll(),&error);if(error.error!=QJsonParseError::NoError)return 4;
    QQmlEngine engine;engine.addImportPath("/measure-check/install/lib/qml");QQmlComponent component(&engine);
    component.setData(R"QML(import QtQuick
import Avelino
Item {
    TextMetrics{id:metrics}
    function measure(rows) {
        const result=[]
        for(const row of rows){
            metrics.font=DateRangeTools.systemFont(row.fontPixels)
            const presentation=DateRangeTools.editorFormatted(row.date,row.locale,row.calendar,row.timeZone)
            metrics.text=presentation.text;const width=metrics.advanceWidth
            const segments=[]
            for(const segment of presentation.segments){metrics.text=segment.text;segments.push({kind:segment.kind,text:segment.text,width:metrics.advanceWidth})}
            metrics.text=row.shortDateString
            result.push({id:row.id,index:row.index,date:row.date,editorText:presentation.text,editorWidth:width,shortDateString:row.shortDateString,shortDateWidth:metrics.advanceWidth,segments:segments,fieldTextWidth:DateRangeTools.fieldTextWidth(row.date,row.locale,row.calendar,row.timeZone,row.fontPixels),fontFamily:metrics.font.family,fontPixels:metrics.font.pixelSize})
        }
        return result
    }
})QML",QUrl("measure.qml"));
    if(component.isError()){qCritical()<<component.errors();return 5;}
    auto root=component.create();if(!root){qCritical()<<component.errors();return 6;}
    QVariant result;if(!QMetaObject::invokeMethod(root,"measure",Q_RETURN_ARG(QVariant,result),Q_ARG(QVariant,data.toVariant()))){delete root;return 7;}
    QFile output(argv[2]);if(!output.open(QIODevice::WriteOnly)){delete root;return 8;}
    output.write(QJsonDocument::fromVariant(result).toJson(QJsonDocument::Indented));delete root;return 0;
}

#include <QGuiApplication>
#include <QAccessible>
#include <QQmlApplicationEngine>
#include <QQuickItem>
#include <QTest>
#include <QJsonDocument>
#include <QJsonArray>
#include <QJsonObject>
#include <QFile>
int main(int argc,char **argv){
    QGuiApplication app(argc,argv);QAccessible::setActive(true);
    QQmlApplicationEngine engine;engine.addImportPath("/package/install/lib/qml");
    engine.loadData(R"QML(import QtQuick
import QtQuick.Templates as T
import Avelino
Window {
 id:root;width:400;height:200;visible:true
 property string description:"Original action description"
 property bool attached:false
 T.Action {id:action;text:"Native action";Accessible.description:root.description}
 T.Button {id:caller;objectName:"caller";width:120;height:40;action:action}
 BleeckerTooltip {target:root.attached ? caller:null;text:"Tooltip action outcome"}
})QML");
    if(engine.rootObjects().isEmpty())return 2;auto root=engine.rootObjects()[0];auto caller=root->findChild<QQuickItem*>("caller");
    auto ax=QAccessible::queryAccessibleInterface(caller);if(!ax)return 3;
    QJsonArray observations;
    auto sample=[&](const char *step){QTest::qWait(30);observations.append(QJsonObject{{"step",step},{"description",ax->text(QAccessible::Description)}});};
    sample("initial");root->setProperty("attached",true);sample("attached");root->setProperty("description","Revised while attached");sample("producer-while-attached");root->setProperty("attached",false);sample("detached");root->setProperty("description","Revised after detach");sample("producer-after-detach");
    QJsonObject result{{"accepted",false},{"qt",qVersion()},{"observations",observations}};QFile file("/diagnostic/result.json");if(!file.open(QIODevice::WriteOnly))return 4;file.write(QJsonDocument(result).toJson());
    return observations[3].toObject()["description"]=="Revised while attached" && observations[4].toObject()["description"]=="Revised after detach" ? 0:1;
}

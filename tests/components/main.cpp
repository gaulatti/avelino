#include <QtQuickTest/quicktest.h>
#include <QQmlEngine>
#include <QQmlContext>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>

class FixtureSetup : public QObject {
    Q_OBJECT
public slots:
    void qmlEngineAvailable(QQmlEngine *engine) {
        QFile file(QStringLiteral(NATIVE_GEOMETRY_FILE));
        if (!file.open(QIODevice::ReadOnly)) qFatal("Native geometry evidence is missing");
        const auto cases = QJsonDocument::fromJson(file.readAll()).object().value("cases").toArray();
        if (cases.size() != 8) qFatal("Native geometry evidence is incomplete");
        engine->rootContext()->setContextProperty("nativeGeometry", cases.toVariantList());
    }
};
QUICK_TEST_MAIN_WITH_SETUP(avelino, FixtureSetup)
#include "main.moc"

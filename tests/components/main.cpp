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
        QFile typography(QStringLiteral(NATIVE_TYPOGRAPHY_FILE));
        if (!typography.open(QIODevice::ReadOnly)) qFatal("Native typography evidence is missing");
        const auto data = QJsonDocument::fromJson(typography.readAll()).object();
        if (data.value("referenceRevision").toString() != "fe8a1d462fbd793d883fb92086a16aa2947e32c9")
            qFatal("Native typography reference revision differs");
        const auto fontCases = data.value("cases").toArray();
        if (fontCases.size() != 2160) qFatal("Native typography evidence is incomplete");
        engine->rootContext()->setContextProperty("nativeTypography", fontCases.toVariantList());
        QFile wrapping(QStringLiteral(NATIVE_WRAPPING_FILE));
        if (!wrapping.open(QIODevice::ReadOnly)) qFatal("Native wrapping evidence is missing");
        const auto wrapData = QJsonDocument::fromJson(wrapping.readAll()).object();
        if (wrapData.value("referenceRevision").toString() != "fe8a1d462fbd793d883fb92086a16aa2947e32c9") qFatal("Native wrapping reference revision differs");
        const auto wrapCases = wrapData.value("cases").toArray();
        if (wrapCases.size() != 120) qFatal("Native wrapping evidence is incomplete");
        engine->rootContext()->setContextProperty("nativeWrapping", wrapCases.toVariantList());
        QFile centered(QStringLiteral(NATIVE_CENTERED_TEXT_FILE));
        if (!centered.open(QIODevice::ReadOnly)) qFatal("Native centered-text evidence is missing");
        const auto centeredData = QJsonDocument::fromJson(centered.readAll()).object();
        if (centeredData.value("reference").toString() != "fe8a1d462fbd793d883fb92086a16aa2947e32c9") qFatal("Centered-text reference differs");
        const auto centeredCases = centeredData.value("centeredTextLines").toArray();
        if (centeredCases.size() != 63) qFatal("Native centered-text evidence is incomplete");
        engine->rootContext()->setContextProperty("nativeCenteredText", centeredCases.toVariantList());
        QJsonArray validPresentation;
        for (const auto &entry : centeredData.value("captures").toArray())
            if (entry.toObject().value("api").toString() != "BleeckerLoadingOverlay") validPresentation.append(entry);
        QFile hosted(QStringLiteral(NATIVE_HOSTED_LOADING_FILE));
        if (!hosted.open(QIODevice::ReadOnly)) qFatal("Hosted loading evidence is missing");
        const auto hostedData=QJsonDocument::fromJson(hosted.readAll()).object();
        if (hostedData.value("reference").toString() != "fe8a1d462fbd793d883fb92086a16aa2947e32c9") qFatal("Hosted loading reference differs");
        const auto hostedCases=hostedData.value("captures").toArray();
        if (hostedCases.size()!=32) qFatal("Hosted loading evidence is incomplete");
        for (const auto &entry : hostedCases) validPresentation.append(entry);
        engine->rootContext()->setContextProperty("nativePresentationCaptures", validPresentation.toVariantList());
        engine->rootContext()->setContextProperty("nativePresentationBehavior", centeredData.value("behavior").toArray().toVariantList());
    }
};
QUICK_TEST_MAIN_WITH_SETUP(avelino, FixtureSetup)
#include "main.moc"

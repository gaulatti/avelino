#include "bleeckerfonts.h"
#include <QFontDatabase>
#include <QRawFont>

BleeckerFonts::BleeckerFonts(QObject *parent) : QObject(parent) {
    static const bool registered = [] {
        const QStringList weights{"Thin", "ExtraLight", "Light", "Regular", "Medium",
                                  "SemiBold", "Bold", "ExtraBold", "Black"};
        for (const auto &family : {QStringLiteral("EncodeSans"), QStringLiteral("LibreFranklin")}) {
            for (const auto &weight : weights) {
                const auto path = QStringLiteral(":/qt/qml/Avelino/fonts/%1-%2.ttf").arg(family, weight);
                if (QFontDatabase::addApplicationFont(path) < 0)
                    qFatal("Required bundled font could not be registered: %s", qPrintable(path));
            }
        }
        return true;
    }();
    Q_UNUSED(registered);
}

qreal BleeckerFonts::logicalFontDpi() {
    QFont probe;
    probe.setPointSizeF(72);
    return QRawFont::fromFont(probe).pixelSize();
}

qreal BleeckerFonts::pointSizeForPixels(qreal pixels) const {
    return pixels * 72 / logicalFontDpi();
}

QString BleeckerFonts::monospace() const {return QFontDatabase::systemFont(QFontDatabase::FixedFont).family();}

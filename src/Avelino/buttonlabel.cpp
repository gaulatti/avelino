#include "buttonlabel.h"
#include "bleeckerfonts.h"
#include <QPainter>
#include <QRawFont>
#include <QTextLayout>
#include <QtEndian>
#include <algorithm>
#include <cmath>

ButtonLabel::ButtonLabel(QQuickItem *parent) : QQuickPaintedItem(parent) {
    setAntialiasing(true);
    relayout();
}

void ButtonLabel::setText(const QString &text) {
    if (m_text == text) return;
    m_text = text; relayout(); emit textChanged();
}

void ButtonLabel::setFont(const QFont &font) {
    if (m_font == font) return;
    m_font = font; relayout(); emit fontChanged();
}

void ButtonLabel::setColor(QColor color) {
    if (m_color == color) return;
    m_color = color; update(); emit colorChanged();
}

void ButtonLabel::relayout() {
    m_pixels = m_font.pixelSize() > 0 ? m_font.pixelSize()
        : m_font.pointSizeF() * BleeckerFonts::logicalFontDpi() / 72;
    if (!std::isfinite(m_pixels) || m_pixels <= 0) qFatal("Button label requires a positive finite font size");
    const auto original = QRawFont::fromFont(m_font);
    const auto head = original.fontTable("head");
    if (head.size() < 20) qFatal("Button label font has no readable design-unit table");
    const int units = qFromBigEndian<quint16>(reinterpret_cast<const uchar *>(head.constData() + 18));
    if (units <= 0) qFatal("Button label font has invalid design units");
    const qreal ratio = m_pixels / units;
    QFont shapeFont = m_font;
    shapeFont.setPixelSize(units);
    if (shapeFont.letterSpacingType() == QFont::AbsoluteSpacing)
        shapeFont.setLetterSpacing(QFont::AbsoluteSpacing, shapeFont.letterSpacing() / ratio);
    shapeFont.setWordSpacing(shapeFont.wordSpacing() / ratio);
    QString layoutText = m_text;
    layoutText.replace(QChar('\n'), QChar::LineSeparator);
    QTextLayout layout(layoutText, shapeFont);
    QTextOption option;
    option.setWrapMode(QTextOption::NoWrap);
    option.setUseDesignMetrics(true);
    option.setFlags(QTextOption::IncludeTrailingSpaces);
    layout.setTextOption(option);
    qreal width = 0, height = 0, baseline = 0;
    layout.beginLayout();
    for (;;) {
        auto line = layout.createLine();
        if (!line.isValid()) break;
        line.setLineWidth(1000000);
        line.setPosition(QPointF(0, height));
        if (height == 0) baseline = line.ascent();
        width = std::max(width, line.naturalTextWidth());
        height += line.height();
    }
    layout.endLayout();
    m_runs.clear();
    m_family = original.familyName(); m_style = original.styleName();
    for (const auto &glyphRun : layout.glyphRuns()) {
        const auto raw = glyphRun.rawFont();
        Run run{raw.familyName(), raw.styleName(), raw.weight(), glyphRun.glyphIndexes(),
                glyphRun.positions(), glyphRun.flags()};
        for (auto &position : run.positions) position *= ratio;
        m_runs.append(run);
    }
    m_height = height * ratio;
    setImplicitWidth(width * ratio); setImplicitHeight(m_height);
    setBaselineOffset(baseline * ratio);
    update(); emit layoutChanged();
}

void ButtonLabel::paint(QPainter *painter) {
    painter->setPen(m_color);
    painter->setRenderHint(QPainter::TextAntialiasing);
    for (const auto &data : m_runs) {
        // QRawFont is thread-local. Recreate it on the painting thread; only
        // value data (face, indexes, positions, flags) crosses synchronization.
        QFont font = m_font;
        font.setFamily(data.family); font.setStyleName(data.style);
        font.setWeight(QFont::Weight(data.weight)); font.setPixelSize(1000);
        auto raw = QRawFont::fromFont(font);
        raw.setPixelSize(m_pixels);
        QGlyphRun run;
        run.setRawFont(raw); run.setGlyphIndexes(data.glyphs);
        run.setPositions(data.positions); run.setFlags(data.flags);
        painter->drawGlyphRun(QPointF(), run);
    }
}

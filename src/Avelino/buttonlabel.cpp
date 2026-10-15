#include "buttonlabel.h"
#include "bleeckerfonts.h"
#include <QPainter>
#include <QRawFont>
#include <QTextLayout>
#include <QFontMetricsF>
#include <QtEndian>
#include <algorithm>
#include <cmath>

ButtonLabel::ButtonLabel(QQuickItem *parent) : QQuickPaintedItem(parent) {
    setAntialiasing(true);
    connect(&m_layoutMetrics, &PixelAlignment::devicePixelRatioChanged, this, &ButtonLabel::relayout);
    m_layoutMetrics.setTarget(this);
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

void ButtonLabel::setTracking(qreal tracking) {
    if (!std::isfinite(tracking)) qFatal("Label tracking requires a finite value");
    if (m_tracking == tracking) return;
    m_tracking = tracking; relayout(); emit trackingChanged();
}

void ButtonLabel::setWrapWidth(qreal width) {
    if (!std::isfinite(width) || (width < 0 && width != -1))
        qFatal("Label wrap width must be nonnegative or -1 for explicit lines only");
    if (m_wrapWidth == width) return;
    m_wrapWidth = width; relayout(); emit wrapWidthChanged();
}

void ButtonLabel::setLineHeight(qreal height) {
    if (!std::isfinite(height) || height < 0)
        qFatal("Label line height must be finite and nonnegative");
    if (m_lineHeight == height) return;
    m_lineHeight = height; relayout(); emit lineHeightChanged();
}

void ButtonLabel::setElideWidth(qreal width) {
    if (!std::isfinite(width) || (width < 0 && width != -1))
        qFatal("Label elide width must be nonnegative or -1 when disabled");
    if (m_elideWidth == width) return;
    m_elideWidth = width; relayout(); emit elideWidthChanged();
}

void ButtonLabel::relayout() {
    m_pixels = m_font.pixelSize() > 0 ? m_font.pixelSize()
        : m_font.pointSizeF() * BleeckerFonts::logicalFontDpi() / 72;
    if (!std::isfinite(m_pixels) || m_pixels <= 0) qFatal("Button label requires a positive finite font size");
    const auto sourceFamily = [](const QString &family) {
        return family == QStringLiteral("Encode Sans") || family == QStringLiteral("Libre Franklin");
    };
    QFont lookupFont = m_font;
    const bool declaredSourceFont = sourceFamily(m_font.family());
    m_resolvedPixels = declaredSourceFont ? std::round(m_pixels) : m_pixels;
    // Source Font.resolve uses its 12-point custom-font default when a
    // positive sub-half-point request rounds to zero. This is measured source
    // behavior, including its discontinuity, rather than a new clamp.
    if (declaredSourceFont && m_resolvedPixels == 0) m_resolvedPixels = 12;
    if (declaredSourceFont)
        lookupFont.setPointSizeF(m_resolvedPixels * 72 / BleeckerFonts::logicalFontDpi());
    auto original = QRawFont::fromFont(lookupFont);
    const bool sourceFont = sourceFamily(original.familyName());
    if (sourceFont && !declaredSourceFont) {
        m_resolvedPixels = std::round(m_pixels);
        if (m_resolvedPixels == 0) m_resolvedPixels = 12;
        lookupFont.setPointSizeF(m_resolvedPixels * 72 / BleeckerFonts::logicalFontDpi());
        original = QRawFont::fromFont(lookupFont);
    }
    const auto head = original.fontTable("head");
    if (head.size() < 20) qFatal("Button label font has no readable design-unit table");
    const int units = qFromBigEndian<quint16>(reinterpret_cast<const uchar *>(head.constData() + 18));
    if (units <= 0) qFatal("Button label font has invalid design units");
    const qreal ratio = m_resolvedPixels / units;
    const qreal dpr = m_layoutMetrics.devicePixelRatio();
    const auto viewWidth = [sourceFont, dpr](qreal advance) {
        return sourceFont ? std::ceil(advance * dpr) / dpr : advance;
    };
    QFont shapeFont = m_font;
    shapeFont.setPixelSize(units);
    if (shapeFont.letterSpacingType() == QFont::AbsoluteSpacing)
        shapeFont.setLetterSpacing(QFont::AbsoluteSpacing, shapeFont.letterSpacing() / ratio);
    // Apply explicit logical tracking at design-unit scale. QFont otherwise
    // quantizes a 1.15 px request to 1.140625 before shaping starts.
    if (m_tracking != 0)
        shapeFont.setLetterSpacing(QFont::AbsoluteSpacing, m_tracking / ratio);
    shapeFont.setWordSpacing(shapeFont.wordSpacing() / ratio);
    struct SourceTextMetrics { qreal advance; qreal width; };
    const auto sourceMetrics = [units, pixels = m_resolvedPixels, tracking = m_tracking, finalSpacing = m_tracking != 0 ? shapeFont.letterSpacing() : 0](const QTextLine &line, QStringView text, qreal offeredWidth = -1) -> SourceTextMetrics {
        // Source measures scaled glyph advances and positioning separately.
        // Summing a design-space total first loses floating-point boundary
        // behavior before the source's physical-pixel ceil. Keep each operation
        // distinct: an FMA contraction changes a few exact integer boundaries.
        struct Glyph { qreal x, advance; };
        QList<Glyph> glyphs;
        for (const auto &run : line.glyphRuns()) {
            const auto positions = run.positions();
            const auto advances = run.rawFont().advancesForGlyphIndexes(run.glyphIndexes());
            for (qsizetype i = 0; i < positions.size(); ++i)
                glyphs.append({positions[i].x(), advances[i].x()});
        }
        if (glyphs.isEmpty()) return {0, 0};
        std::stable_sort(glyphs.begin(), glyphs.end(), [](const Glyph &a, const Glyph &b) { return a.x < b.x; });
        qreal advance = glyphs.first().x / units * pixels;
        for (qsizetype i = 0; i + 1 < glyphs.size(); ++i) {
            const qreal positioning = glyphs[i + 1].x - glyphs[i].x - glyphs[i].advance;
            const volatile qreal glyphAdvance = glyphs[i].advance * (pixels / units);
            const volatile qreal positioningAdvance = positioning * (pixels / units);
            const volatile qreal positionedAdvance = glyphAdvance + positioningAdvance;
            advance += positionedAdvance;
        }
        const volatile qreal finalAdvance = glyphs.last().advance * (pixels / units);
        // Explicit source tracking includes the final glyph's spacing. The
        // shaped positions contain only the spaces before that final glyph.
        advance = advance + finalAdvance + tracking;
        // Natural width retains ink overhang and spaces omitted by Qt's
        // wrapped glyph runs. Both contribute to the measured source box.
        const auto missing = std::max(qreal(0), line.naturalTextWidth()
            - glyphs.last().x - glyphs.last().advance - finalSpacing) * (pixels / units);
        qreal width = advance + missing;
        const auto end = line.textStart() + line.textLength();
        if (end > 0 && text.at(end - 1).isSpace()
            && text.at(end - 1) != QChar::LineSeparator && text.at(end - 1) != QChar::ParagraphSeparator) {
            advance += missing;
            // Source Text counts trailing whitespace up to its proposal.
            if (offeredWidth >= 0) width = std::min(width, offeredWidth);
        }
        return {advance, width};
    };
    QString layoutText = m_text;
    layoutText.replace(QChar('\n'), QChar::LineSeparator);
    QTextOption option;
    option.setWrapMode(QTextOption::NoWrap);
    option.setUseDesignMetrics(true);
    option.setFlags(QTextOption::IncludeTrailingSpaces);
    QTextLayout intrinsic(layoutText, shapeFont);
    intrinsic.setTextOption(option);
    qreal intrinsicWidth = 0, intrinsicAdvance = 0;
    intrinsic.beginLayout();
    for (;;) {
        auto line = intrinsic.createLine();
        if (!line.isValid()) break;
        line.setLineWidth(1000000);
        const auto metrics = sourceFont ? sourceMetrics(line, layoutText)
            : SourceTextMetrics{line.naturalTextWidth() * ratio, line.naturalTextWidth() * ratio};
        intrinsicAdvance = std::max(intrinsicAdvance, metrics.advance);
        intrinsicWidth = std::max(intrinsicWidth, metrics.width);
    }
    intrinsic.endLayout();
    m_glyphAdvance = intrinsicAdvance;
    const qreal unwrappedWidth = viewWidth(intrinsicWidth);
    if (m_unwrappedWidth != unwrappedWidth) {
        m_unwrappedWidth = unwrappedWidth;
        emit unwrappedWidthChanged();
    }
    // Intrinsic advance stays independent of the offered elision width.
    // Otherwise a newline's ellipsis can change the control's implicit width
    // while its allocated width is being used to configure this renderer.
    if (m_elideWidth >= 0) {
        for (qsizetype i = 0; i < layoutText.size(); ++i) {
            const auto ch = layoutText[i];
            if (ch == QChar::LineSeparator || ch == QChar::ParagraphSeparator
                || ch == QLatin1Char('\r') || ch == QChar(0x0085)) {
                layoutText = layoutText.left(i) + QChar(0x2026);
                break;
            }
        }
    }
    // The intrinsic advance has already been shaped. Converting that exact
    // logical width back to design units can round below QTextLayout's fixed
    // point boundary and wrap a word that fits. Keep explicit newlines, but
    // only enable automatic wrapping when the allocated width is smaller.
    if (m_elideWidth < 0 && m_wrapWidth >= 0 && m_wrapWidth < m_glyphAdvance
        && !qFuzzyCompare(m_wrapWidth, m_glyphAdvance))
        option.setWrapMode(QTextOption::WrapAtWordBoundaryOrAnywhere);
    if (m_elideWidth >= 0)
        layoutText = QFontMetricsF(shapeFont).elidedText(layoutText, Qt::ElideRight, m_elideWidth / ratio);
    QTextLayout layout(layoutText, shapeFont);
    layout.setTextOption(option);
    qreal width = 0, height = 0, baseline = 0;
    if (sourceFont && m_text.isEmpty()) {
        // The pinned empty Text keeps the source's default empty line box,
        // independently of the declared custom font. Components may omit or
        // explicitly size empty content according to their own source contract.
        m_runs.clear(); m_family = original.familyName(); m_style = original.styleName();
        m_height = 14; setImplicitWidth(0); setImplicitHeight(m_height); setBaselineOffset(11);
        update(); emit layoutChanged(); return;
    }
    layout.beginLayout();
    for (;;) {
        auto line = layout.createLine();
        if (!line.isValid()) break;
        line.setLineWidth(m_wrapWidth >= 0 ? std::max(qreal(0.000001), m_wrapWidth / ratio) : 1000000);
        const qreal ascent = sourceFont ? std::round(line.ascent() * ratio) : line.ascent() * ratio;
        const qreal descent = sourceFont ? std::round(line.descent() * ratio) : line.descent() * ratio;
        line.setPosition(QPointF(0, (height + ascent) / ratio - line.ascent()));
        if (height == 0) baseline = ascent;
        width = std::max(width, sourceFont ? sourceMetrics(line, layoutText, m_wrapWidth).width : line.naturalTextWidth() * ratio);
        // Keep the measured logical line box in logical units. A round trip
        // through design units turns an exact 16 into 15.999999999999998.
        height += m_lineHeight > 0 ? m_lineHeight
            : sourceFont ? ascent + descent : line.height() * ratio;
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
    m_height = height;
    setImplicitWidth(viewWidth(width)); setImplicitHeight(m_height);
    setBaselineOffset(baseline);
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
        raw.setPixelSize(m_resolvedPixels);
        QGlyphRun run;
        run.setRawFont(raw); run.setGlyphIndexes(data.glyphs);
        run.setPositions(data.positions); run.setFlags(data.flags);
        painter->drawGlyphRun(QPointF(), run);
    }
}

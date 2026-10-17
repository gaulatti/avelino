#include "buttonlabel.h"
#include "bleeckerfonts.h"
#include <QPainter>
#include <QRawFont>
#include <QTextLayout>
#include <QFontMetricsF>
#include <QtEndian>
#include <QRegularExpression>
#include <QMap>
#include <algorithm>
#include <cmath>

ButtonLabel::ButtonLabel(QQuickItem *parent) : QQuickPaintedItem(parent) {
    setAntialiasing(true);
    connect(&m_layoutMetrics, &PixelAlignment::devicePixelRatioChanged, this, [this] { relayout(); });
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
    m_wrapWidth = width; relayout(true); emit wrapWidthChanged();
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

void ButtonLabel::setHorizontalAlignment(int alignment) {
    if (alignment != Qt::AlignLeft && alignment != Qt::AlignHCenter && alignment != Qt::AlignRight)
        qFatal("Label horizontal alignment must be left, center or right");
    if (m_alignment == alignment) return;
    m_alignment = alignment; relayout(); emit horizontalAlignmentChanged();
}

void ButtonLabel::relayout(bool reuseWrapMeasurements) {
    const auto generation = ++m_layoutGeneration;
    if (!reuseWrapMeasurements) m_wrapMeasurements.clear();
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
    // Qt 6.8.3 can return unusable raw-font family metadata when a system
    // request rounds below one raster pixel. Resolve the same face at one
    // pixel for its tables; shaping and paint retain the requested size.
    const bool tinyLookup = m_resolvedPixels < 0.5;
    if (tinyLookup) lookupFont.setPixelSize(1);
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
    const auto os2 = original.fontTable("OS/2");
    m_capHeight = sourceFont && os2.size() >= 90
        ? qFromBigEndian<qint16>(reinterpret_cast<const uchar *>(os2.constData() + 88)) * ratio
        : original.capHeight() * (tinyLookup ? m_resolvedPixels / original.pixelSize() : 1);
    const qreal dpr = m_layoutMetrics.devicePixelRatio();
    qreal layoutWidth = m_wrapWidth;
    bool reusedMeasurement = false;
    if (sourceFont && m_elideWidth < 0 && m_wrapWidth >= 0) {
        // Native Text preserves measured wraps over the interval between a
        // proposal and its pixel-rounded fitted width. An earlier exact
        // proposal takes precedence over an overlapping interval. Re-shape at
        // the original proposal instead of retaining duplicate glyph buffers.
        const WrapMeasurement *cached = nullptr;
        for (const auto &entry : m_wrapMeasurements)
            if (entry.proposal == m_wrapWidth) { cached = &entry; break; }
        if (!cached) for (const auto &entry : m_wrapMeasurements)
            if (m_wrapWidth >= std::min(entry.proposal, entry.fittedWidth)
                && m_wrapWidth <= std::max(entry.proposal, entry.fittedWidth)) { cached = &entry; break; }
        if (cached) { layoutWidth = cached->proposal; reusedMeasurement = true; }
    }
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
    QMap<int,qreal> contextualEndPositioning;
    struct SourceTextMetrics { qreal advance; qreal width; };
    const auto sourceMetrics = [units, pixels = m_resolvedPixels, tracking = m_tracking, finalSpacing = m_tracking != 0 ? shapeFont.letterSpacing() : 0, &contextualEndPositioning](const QTextLine &line, QStringView text, qreal offeredWidth = -1) -> SourceTextMetrics {
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
        // Explicit multiline Text omits positive trailing tracking from its view
        // bounds; negative tracking retains the measured ink extent.
        const bool explicitLines=text.contains(QChar::LineSeparator) || text.contains(QChar::ParagraphSeparator);
        advance = advance + finalAdvance + (explicitLines && tracking>0 ? 0 : tracking);
        // Natural width retains ink overhang and spaces omitted by Qt's
        // wrapped glyph runs. Both contribute to the measured source box.
        const auto end = line.textStart() + line.textLength();
        const bool trailingSpace=end>0 && text.at(end-1).isSpace();
        // Untracked CoreText retains pair positioning across an emergency soft break.
        // Qt reshapes that final glyph without its next glyph's pair adjustment.
        if(tracking==0 && offeredWidth>=0 && end<text.size() && end>0 && !trailingSpace && !text.at(end).isSpace()) {
            const volatile qreal terminalPositioning=contextualEndPositioning.value(end,0)*(pixels/units);
            advance+=terminalPositioning;
        }
        // Source view bounds use advances, not a positive final ink overhang.
        // Retain the separately measured negative-tracking and trailing-space
        // extents; those are different source contracts.
        const auto missing = trailingSpace || tracking!=0 ? std::max(qreal(0), line.naturalTextWidth()
            - glyphs.last().x - glyphs.last().advance - finalSpacing) * (pixels / units):0;
        qreal width = advance + missing;
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
    struct ContextGlyph {int index;qreal x,advance;};
    QList<ContextGlyph> contextGlyphs;
    for(const auto &run:intrinsic.glyphRuns(0,-1,QTextLayout::RetrieveGlyphIndexes|QTextLayout::RetrieveGlyphPositions|QTextLayout::RetrieveStringIndexes)) {
        if(run.isRightToLeft())continue;
        const auto indexes=run.stringIndexes();const auto positions=run.positions();
        const auto advances=run.rawFont().advancesForGlyphIndexes(run.glyphIndexes());
        for(qsizetype i=0;i<indexes.size();++i)contextGlyphs.append({int(indexes[i]),positions[i].x(),advances[i].x()});
    }
    std::stable_sort(contextGlyphs.begin(),contextGlyphs.end(),[](const auto &a,const auto &b){return a.index<b.index;});
    for(qsizetype i=1;i<contextGlyphs.size();++i) {
        const auto &previous=contextGlyphs[i-1],&current=contextGlyphs[i];
        if(current.index>previous.index)contextualEndPositioning.insert(current.index,current.x-previous.x-previous.advance-(m_tracking!=0 ? shapeFont.letterSpacing():0));
    }
    m_glyphAdvance = intrinsicAdvance;
    const qreal unwrappedWidth = viewWidth(intrinsicWidth);
    if (m_unwrappedWidth != unwrappedWidth) {
        m_unwrappedWidth = unwrappedWidth;
        emit unwrappedWidthChanged();
        // An intrinsic-width binding can synchronously offer a new width and
        // finish a newer layout. Keep that result and its cache entries.
        if (generation != m_layoutGeneration) return;
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
    if (m_elideWidth < 0 && layoutWidth >= 0 && layoutWidth < m_glyphAdvance
        && !qFuzzyCompare(layoutWidth, m_glyphAdvance))
        option.setWrapMode(QTextOption::WrapAtWordBoundaryOrAnywhere);
    if (m_elideWidth >= 0)
        layoutText = QFontMetricsF(shapeFont).elidedText(layoutText, Qt::ElideRight, m_elideWidth / ratio);
    QTextLayout layout(layoutText, shapeFont);
    layout.setTextOption(option);
    // Measured source two-line text can move a short orphan's predecessor to
    // the last line. Compare the remaining prefix with the orphan; merely
    // testing whether the new pair fits also moves short numeric prefixes and
    // misses cases where the moved pair wraps into an additional line.
    // Preserve explicit paragraph breaks and leave
    // earlier lines and their shaping untouched.
    QMap<int,int> paragraphBreaks;
    if (sourceFont && option.wrapMode()!=QTextOption::NoWrap && m_elideWidth<0) {
        QTextLayout greedy(layoutText,shapeFont);greedy.setTextOption(option);
        greedy.beginLayout();
        while (true) {
            auto line=greedy.createLine();if(!line.isValid())break;
            line.setLineWidth(std::max(qreal(0.000001),(layoutWidth+std::max(qreal(0),m_tracking))/ratio));
        }
        greedy.endLayout();
        const QRegularExpression spaces(QStringLiteral("\\s+"));
        for(int i=1;i<greedy.lineCount();++i) {
            const auto last=greedy.lineAt(i),previous=greedy.lineAt(i-1);
            const auto tail=layoutText.mid(last.textStart(),last.textLength());
            const bool paragraphEnd=i==greedy.lineCount()-1 || tail.contains(QChar::LineSeparator) || tail.contains(QChar::ParagraphSeparator);
            const auto before=layoutText.mid(previous.textStart(),previous.textLength());
            const auto finalWord=tail.trimmed();
            const bool shortToken=finalWord.size()<=10;
            bool twoLines=true;
            if(i>=2){const auto earlier=greedy.lineAt(i-2);const auto preceding=layoutText.mid(earlier.textStart(),earlier.textLength());twoLines=preceding.contains(QChar::LineSeparator) || preceding.contains(QChar::ParagraphSeparator);}

            if(!paragraphEnd || !twoLines || !shortToken || before.contains(QChar::LineSeparator) || before.contains(QChar::ParagraphSeparator)
                || tail.trimmed().split(spaces,Qt::SkipEmptyParts).size()!=1
                || before.trimmed().split(spaces,Qt::SkipEmptyParts).size()<2)continue;
            auto trimmedEnd=previous.textStart()+previous.textLength();
            while(trimmedEnd>previous.textStart() && layoutText.at(trimmedEnd-1).isSpace())--trimmedEnd;
            auto wordStart=trimmedEnd;
            while(wordStart>previous.textStart() && !layoutText.at(wordStart-1).isSpace())--wordStart;
            if(wordStart==previous.textStart())continue;
            const auto prefixText=layoutText.mid(previous.textStart(),wordStart-previous.textStart());
            auto single=option;single.setWrapMode(QTextOption::NoWrap);
            const auto measuredWidth=[&](const QString &value) {
                QTextLayout candidate(value,shapeFont);candidate.setTextOption(single);
                candidate.beginLayout();auto line=candidate.createLine();line.setLineWidth(1000000);candidate.endLayout();
                return sourceMetrics(line,value).width;
            };
            if(measuredWidth(prefixText)>=measuredWidth(finalWord))
                paragraphBreaks.insert(previous.textStart(),wordStart-previous.textStart());
        }
    }
    qreal width = 0, height = 0, baseline = 0;
    if (m_text.isEmpty()) {
        // The pinned empty Text keeps the source's default empty line box,
        // independently of the declared custom font. Components may omit or
        // explicitly size empty content according to their own source contract.
        m_runs.clear(); m_linePositions.clear(); m_family = original.familyName(); m_style = original.styleName();
        m_height = 14; setImplicitWidth(0);
        if (generation != m_layoutGeneration) return;
        setImplicitHeight(m_height);
        if (generation != m_layoutGeneration) return;
        setBaselineOffset(11);
        if (generation != m_layoutGeneration) return;
        update(); emit layoutChanged(); return;
    }
    layout.beginLayout();
    for (;;) {
        auto line = layout.createLine();
        if (!line.isValid()) break;
        // Source line fitting excludes positive final tracking. Its resulting
        // glyph extent may reach past the proposal and is cropped by the Text
        // view. Negative tracking is already included in Qt's measured fit.
        const auto lineWidth=layoutWidth>=0 ? std::max(qreal(0.000001),(layoutWidth+std::max(qreal(0),m_tracking))/ratio):1000000;
        if(paragraphBreaks.contains(line.textStart()))line.setNumColumns(paragraphBreaks.value(line.textStart()),lineWidth);
        else line.setLineWidth(lineWidth);
        const qreal ascent = sourceFont ? std::round(line.ascent() * ratio) : line.ascent() * ratio;
        const qreal descent = sourceFont ? std::round(line.descent() * ratio) : line.descent() * ratio;
        line.setPosition(QPointF(0, (height + ascent) / ratio - line.ascent()));
        if (height == 0) baseline = ascent;
        width = std::max(width, sourceFont ? sourceMetrics(line, layoutText, layoutWidth).width : line.naturalTextWidth() * ratio);
        // Keep the measured logical line box in logical units. A round trip
        // through design units turns an exact 16 into 15.999999999999998.
        height += m_lineHeight > 0 ? m_lineHeight
            : sourceFont ? ascent + descent : line.height() * ratio;
    }
    layout.endLayout();
    const auto trimmedAdvance = [&](const QTextLine &line) {
        auto text = layoutText.mid(line.textStart(), line.textLength());
        while (!text.isEmpty() && text.back().isSpace()) text.chop(1);
        QTextLayout trimmed(text, shapeFont);
        QTextOption trimmedOption = option; trimmedOption.setWrapMode(QTextOption::NoWrap);
        trimmed.setTextOption(trimmedOption); trimmed.beginLayout();
        auto trimmedLine = trimmed.createLine();
        qreal advance = 0;
        if (trimmedLine.isValid()) {
            trimmedLine.setLineWidth(1000000);
            advance = sourceFont ? sourceMetrics(trimmedLine, text).advance : trimmedLine.horizontalAdvance() * ratio;
        }
        trimmed.endLayout();
        return advance;
    };
    if (sourceFont && m_alignment != Qt::AlignLeft) {
        // Public Text measures trailing whitespace after centering/right
        // alignment. Align the trimmed lines, then retain each full extent.
        qreal longest = 0;
        QList<qreal> advances;
        for (int i = 0; i < layout.lineCount(); ++i) {
            const auto advance = trimmedAdvance(layout.lineAt(i));
            advances.append(advance); longest = std::max(longest, advance);
        }
        qreal alignedWidth = 0;
        for (int i = 0; i < layout.lineCount(); ++i) {
            const auto offset = (longest - advances[i]) / (m_alignment == Qt::AlignHCenter ? 2 : 1);
            alignedWidth = std::max(alignedWidth, sourceMetrics(layout.lineAt(i), layoutText, layoutWidth).width + offset);
        }
        // Paint against the fitted Text view as well. Using an extent wider
        // than its finite proposal shifts visible right-aligned glyphs into
        // the clip even though the QML view itself has the correct width.
        width = layoutWidth >= 0 ? std::min(alignedWidth, layoutWidth) : alignedWidth;
    }
    m_runs.clear();
    m_linePositions.clear();
    m_family = original.familyName(); m_style = original.styleName();
    const auto appendRun = [&](const QGlyphRun &glyphRun, qreal offset) {
        const auto raw = glyphRun.rawFont();
        Run run{raw.familyName(), raw.styleName(), raw.weight(), glyphRun.glyphIndexes(),
                glyphRun.positions(), glyphRun.flags()};
        for (auto &position : run.positions) { position *= ratio; position.rx() += offset; }
        m_runs.append(run);
    };
    if (m_alignment == Qt::AlignLeft) {
        // Preserve the original aggregate shaping and run ordering exactly.
        for (const auto &glyphRun : layout.glyphRuns()) appendRun(glyphRun, 0);
        for (int i = 0; i < layout.lineCount(); ++i)
            m_linePositions.append(QPointF(0, layout.lineAt(i).y() * ratio));
    } else {
        for (int i = 0; i < layout.lineCount(); ++i) {
            const auto line = layout.lineAt(i);
            const qreal advance = trimmedAdvance(line);
            const qreal offset = (viewWidth(width) - advance) / (m_alignment == Qt::AlignHCenter ? 2 : 1);
            // Keep logical offsets outside QTextLine's design-space QFixed
            // positions so fractional centered origins are not quantized.
            for (const auto &glyphRun : line.glyphRuns()) appendRun(glyphRun, offset);
            m_linePositions.append(QPointF(offset, line.y() * ratio));
        }
    }
    m_height = height;
    if (sourceFont && m_elideWidth < 0 && m_wrapWidth >= 0 && !reusedMeasurement)
        m_wrapMeasurements.append({m_wrapWidth, viewWidth(std::min(width, m_wrapWidth))});
    setImplicitWidth(viewWidth(width));
    if (generation != m_layoutGeneration) return;
    setImplicitHeight(m_height);
    if (generation != m_layoutGeneration) return;
    setBaselineOffset(baseline);
    if (generation != m_layoutGeneration) return;
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

#pragma once
#include <QQuickPaintedItem>
#include <QFont>
#include <QGlyphRun>
#include <QtQml/qqmlregistration.h>
#include "pixelalignment.h"

// Avelino's default button label. Qt shapes Unicode; Avelino preserves the
// requested logical size separately from the measured source font resolution,
// line boxes and intrinsic view bounds before Qt rasterizes each run.
class ButtonLabel : public QQuickPaintedItem {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QString text READ text WRITE setText NOTIFY textChanged)
    Q_PROPERTY(QFont font READ font WRITE setFont NOTIFY fontChanged)
    Q_PROPERTY(QColor color READ color WRITE setColor NOTIFY colorChanged)
    Q_PROPERTY(qreal tracking READ tracking WRITE setTracking NOTIFY trackingChanged)
    Q_PROPERTY(qreal wrapWidth READ wrapWidth WRITE setWrapWidth NOTIFY wrapWidthChanged)
    Q_PROPERTY(qreal lineHeight READ lineHeight WRITE setLineHeight NOTIFY lineHeightChanged)
    Q_PROPERTY(qreal elideWidth READ elideWidth WRITE setElideWidth NOTIFY elideWidthChanged)
    Q_PROPERTY(qreal unwrappedWidth READ unwrappedWidth NOTIFY unwrappedWidthChanged)
    Q_PROPERTY(qreal logicalPixelSize READ logicalPixelSize NOTIFY layoutChanged)
    Q_PROPERTY(qreal resolvedPixelSize READ resolvedPixelSize NOTIFY layoutChanged)
    Q_PROPERTY(qreal glyphAdvance READ glyphAdvance NOTIFY layoutChanged)
    Q_PROPERTY(qreal naturalHeight READ naturalHeight NOTIFY layoutChanged)
    Q_PROPERTY(QString resolvedFamily READ resolvedFamily NOTIFY layoutChanged)
    Q_PROPERTY(QString resolvedStyle READ resolvedStyle NOTIFY layoutChanged)
public:
    explicit ButtonLabel(QQuickItem *parent = nullptr);
    QString text() const { return m_text; }
    void setText(const QString &text);
    QFont font() const { return m_font; }
    void setFont(const QFont &font);
    QColor color() const { return m_color; }
    void setColor(QColor color);
    qreal tracking() const { return m_tracking; }
    void setTracking(qreal tracking);
    qreal wrapWidth() const { return m_wrapWidth; }
    void setWrapWidth(qreal width);
    qreal lineHeight() const { return m_lineHeight; }
    void setLineHeight(qreal height);
    qreal elideWidth() const { return m_elideWidth; }
    void setElideWidth(qreal width);
    qreal unwrappedWidth() const { return m_unwrappedWidth; }
    qreal logicalPixelSize() const { return m_pixels; }
    qreal resolvedPixelSize() const { return m_resolvedPixels; }
    qreal glyphAdvance() const { return m_glyphAdvance; }
    qreal naturalHeight() const { return m_height; }
    QString resolvedFamily() const { return m_family; }
    QString resolvedStyle() const { return m_style; }
    void paint(QPainter *painter) override;
signals:
    void textChanged();
    void fontChanged();
    void colorChanged();
    void trackingChanged();
    void wrapWidthChanged();
    void lineHeightChanged();
    void elideWidthChanged();
    void unwrappedWidthChanged();
    void layoutChanged();
private:
    void relayout();
    struct Run {
        QString family, style;
        int weight;
        QList<quint32> glyphs;
        QList<QPointF> positions;
        QGlyphRun::GlyphRunFlags flags;
    };
    QString m_text, m_family, m_style;
    QFont m_font;
    QColor m_color = Qt::black;
    qreal m_pixels = 14, m_resolvedPixels = 14, m_height = 0, m_glyphAdvance = 0;
    qreal m_tracking = 0;
    qreal m_wrapWidth = -1, m_unwrappedWidth = 0;
    qreal m_lineHeight = 0;
    qreal m_elideWidth = -1;
    QList<Run> m_runs;
    PixelAlignment m_layoutMetrics;
};

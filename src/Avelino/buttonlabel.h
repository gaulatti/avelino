#pragma once
#include <QQuickPaintedItem>
#include <QFont>
#include <QGlyphRun>
#include <QtQml/qqmlregistration.h>

// Avelino's default button label. Qt shapes Unicode; Avelino preserves the
// requested logical size and design advances before Qt rasterizes each run.
class ButtonLabel : public QQuickPaintedItem {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QString text READ text WRITE setText NOTIFY textChanged)
    Q_PROPERTY(QFont font READ font WRITE setFont NOTIFY fontChanged)
    Q_PROPERTY(QColor color READ color WRITE setColor NOTIFY colorChanged)
    Q_PROPERTY(qreal logicalPixelSize READ logicalPixelSize NOTIFY layoutChanged)
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
    qreal logicalPixelSize() const { return m_pixels; }
    qreal naturalHeight() const { return m_height; }
    QString resolvedFamily() const { return m_family; }
    QString resolvedStyle() const { return m_style; }
    void paint(QPainter *painter) override;
signals:
    void textChanged();
    void fontChanged();
    void colorChanged();
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
    qreal m_pixels = 14, m_height = 0;
    QList<Run> m_runs;
};

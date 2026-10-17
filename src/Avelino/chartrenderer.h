#pragma once
#include <QQuickPaintedItem>
#include <QPainterPath>
#include <QVariantList>
#include <QFont>
#include <QSizeF>
#include <QVector>
#include <QtQml/qqmlregistration.h>

// Owned chart rendering; no platform chart library or reference-image input.
// The QML wrapper owns layout. This painted child expands to the actual paint
// bounds so endpoint symbols and strokes keep the source's unclipped behavior.
class ChartRenderer : public QQuickPaintedItem {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QString kind READ kind WRITE setKind NOTIFY configurationChanged)
    Q_PROPERTY(QVariant points READ points WRITE setPoints NOTIFY configurationChanged)
    Q_PROPERTY(QVariant values READ values WRITE setValues NOTIFY configurationChanged)
    Q_PROPERTY(bool area READ area WRITE setArea NOTIFY configurationChanged)
    Q_PROPERTY(qreal innerRadius READ innerRadius WRITE setInnerRadius NOTIFY configurationChanged)
    Q_PROPERTY(QSizeF chartSize READ chartSize WRITE setChartSize NOTIFY configurationChanged)
    Q_PROPERTY(bool mirrored READ mirrored WRITE setMirrored NOTIFY configurationChanged)
    Q_PROPERTY(QColor labelColor READ labelColor WRITE setLabelColor NOTIFY configurationChanged)
    Q_PROPERTY(QColor gridColor READ gridColor WRITE setGridColor NOTIFY configurationChanged)
    Q_PROPERTY(QVariantList colors READ colors WRITE setColors NOTIFY configurationChanged)
    Q_PROPERTY(QString localeName READ localeName WRITE setLocaleName NOTIFY configurationChanged)
    Q_PROPERTY(qreal pixelRatio READ pixelRatio WRITE setPixelRatio NOTIFY configurationChanged)
    Q_PROPERTY(QRectF paintBounds READ paintBounds NOTIFY layoutChanged)
    Q_PROPERTY(QVariantMap measurements READ measurements NOTIFY layoutChanged)
    Q_PROPERTY(QVariantList accessibilityRows READ accessibilityRows NOTIFY layoutChanged)
    Q_PROPERTY(int pointCount READ pointCount NOTIFY layoutChanged)
public:
    explicit ChartRenderer(QQuickItem *parent=nullptr);
    QString kind() const{return m_kind;} void setKind(const QString &);
    QVariant points() const{return m_points;} void setPoints(const QVariant &);
    QVariant values() const{return m_values;} void setValues(const QVariant &);
    bool area() const{return m_area;} void setArea(bool);
    qreal innerRadius() const{return m_innerRadius;} void setInnerRadius(qreal);
    QSizeF chartSize() const{return m_size;} void setChartSize(QSizeF);
    bool mirrored() const{return m_mirrored;} void setMirrored(bool);
    QColor labelColor() const{return m_labelColor;} void setLabelColor(QColor);
    QColor gridColor() const{return m_gridColor;} void setGridColor(QColor);
    QVariantList colors() const{return m_colors;} void setColors(const QVariantList &);
    QString localeName() const{return m_locale;} void setLocaleName(const QString &);
    qreal pixelRatio() const{return m_pixelRatio;} void setPixelRatio(qreal);
    QRectF paintBounds() const{return m_bounds;}
    QVariantMap measurements() const{return m_measurements;}
    QVariantList accessibilityRows() const{return m_accessibility;}
    int pointCount() const{return m_accessibility.size();}
    void paint(QPainter *) override;
signals:
    void configurationChanged();
    void layoutChanged();
protected:
    void componentComplete() override;
private:
    struct Point {QString id,series,label;double x=0,y=0,start=0,end=0;int color=0;};
    struct Draw {QPainterPath path;QColor color;double stroke=0;bool gradient=false;bool dashed=false;};
    void relayout();
    QString m_kind="line",m_locale="en_US";
    QVariant m_points=QVariantList{},m_values=QVariantList{};
    QVariantList m_colors,m_accessibility;
    bool m_area=false,m_mirrored=false,m_complete=false;
    QColor m_labelColor,m_gridColor;
    qreal m_innerRadius=0,m_pixelRatio=1;
    QSizeF m_size{100,100};
    QRectF m_bounds{0,0,100,100},m_plot;
    QVariantMap m_measurements;
    QVector<Draw> m_draws;
};

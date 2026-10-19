#pragma once
#include <QQuickPaintedItem>
#include <QImage>
#include <QtQml/qqmlregistration.h>

class BrandImage : public QQuickPaintedItem {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QColor color READ color WRITE setColor NOTIFY colorChanged)
public:
    explicit BrandImage(QQuickItem *parent=nullptr);
    QColor color() const {return m_color;}
    void setColor(QColor value);
    void paint(QPainter *painter) override;
signals:
    void colorChanged();
private:
    QImage m_source,m_tinted;
    QColor m_color=Qt::black;
};

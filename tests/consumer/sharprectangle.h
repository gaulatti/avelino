#pragma once
#include <QPainter>
#include <QQuickPaintedItem>
#include <QtQml/qqmlregistration.h>

// Fixture-only sharp paint. Keep an alpha-capable texture so the software
// renderer clears the background beside fractionally placed parent items.
class SharpRectangle : public QQuickPaintedItem {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QColor color READ color WRITE setColor NOTIFY colorChanged)
public:
    explicit SharpRectangle(QQuickItem *parent=nullptr):QQuickPaintedItem(parent) {
        setOpaquePainting(false);setAntialiasing(false);setSmooth(false);
    }
    QColor color() const {return m_color;}
    void setColor(const QColor &value) {if(value==m_color)return;m_color=value;update();emit colorChanged();}
    void paint(QPainter *painter) override {painter->fillRect(boundingRect(),m_color);}
signals:
    void colorChanged();
private:
    QColor m_color=Qt::transparent;
};

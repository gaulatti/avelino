#pragma once
#include <QtQuickTemplates2/private/qquickcontrol_p.h>
#include <QtQml/qqmlregistration.h>

// Qt 6.8.3 template adapter: defaults yield to ancestor and caller font fields.
class RadioGroupBase : public QQuickControl {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QFont presentationFont READ presentationFont NOTIFY presentationFontChanged)
    Q_PROPERTY(QColor defaultTextColor READ defaultTextColor WRITE setDefaultTextColor NOTIFY resolvedTextColorChanged)
    Q_PROPERTY(QColor resolvedTextColor READ resolvedTextColor NOTIFY resolvedTextColorChanged)
public:
    explicit RadioGroupBase(QQuickItem *parent=nullptr);
    QFont presentationFont() const;
    QColor defaultTextColor() const{return m_defaultTextColor;}
    void setDefaultTextColor(const QColor &value);
    QColor resolvedTextColor() const;
    Q_INVOKABLE bool isHorizontal(int orientation) const;
    Q_INVOKABLE void cancelPointerPress(QQuickItem *option) const;
signals:
    void resolvedTextColorChanged();
    void presentationFontChanged();
protected:
    QFont defaultFont() const override;
private:
    QColor m_defaultTextColor=Qt::black;
};

class RadioHitMask : public QObject {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QRectF iconRect MEMBER iconRect NOTIFY geometryChanged)
    Q_PROPERTY(QRectF titleRect MEMBER titleRect NOTIFY geometryChanged)
public:
    using QObject::QObject;
    QRectF iconRect,titleRect;
    Q_INVOKABLE bool contains(const QPointF &point) const;
signals:
    void geometryChanged();
};

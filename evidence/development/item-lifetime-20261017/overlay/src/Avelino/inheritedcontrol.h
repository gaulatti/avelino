#pragma once
#include <QtQuickTemplates2/private/qquickcontrol_p.h>
#include <QtQml/qqmlregistration.h>

// Qt 6.8.3 template font/palette inheritance for caller-composed content.
class InheritedControl : public QQuickControl {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QFont presentationFont READ presentationFont NOTIFY presentationFontChanged)
    Q_PROPERTY(QColor defaultTextColor READ defaultTextColor WRITE setDefaultTextColor NOTIFY resolvedTextColorChanged)
    Q_PROPERTY(QColor resolvedTextColor READ resolvedTextColor NOTIFY resolvedTextColorChanged)
public:
    explicit InheritedControl(QQuickItem *parent=nullptr);
    ~InheritedControl() override;
    QFont presentationFont() const;
    QColor defaultTextColor() const{return m_defaultTextColor;}
    void setDefaultTextColor(const QColor &value);
    QColor resolvedTextColor() const;
signals:
    void resolvedTextColorChanged();
    void presentationFontChanged();
protected:
    QFont defaultFont() const override;
private:
    QColor m_defaultTextColor=Qt::black;
};

#pragma once
#include <QtQuickTemplates2/private/qquickbutton_p.h>
#include <QtQml/qqmlregistration.h>

// Preserve Qt's button input/action interface while adding the source's raw
// notification value, which Qt's ordinary push-button interface omits.
class AppTabButton : public QQuickButton {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QString accessibleTitle READ accessibleTitle WRITE setAccessibleTitle NOTIFY accessibleTitleChanged)
    Q_PROPERTY(QString notificationValue READ notificationValue WRITE setNotificationValue NOTIFY notificationValueChanged)
public:
    explicit AppTabButton(QQuickItem *parent=nullptr);
    QString accessibleTitle() const{return m_title;}
    QString notificationValue() const{return m_value;}
    void setAccessibleTitle(const QString &value);
    void setNotificationValue(const QString &value);
signals:
    void accessibleTitleChanged();
    void notificationValueChanged();
private:
    QString m_title,m_value;
};

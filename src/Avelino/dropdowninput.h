#pragma once
#include <QObject>
#include <QPointer>
#include <QQuickWindow>
#include <QtQuickTemplates2/private/qquickmenu_p.h>
#include <QtQml/qqmlregistration.h>

class DropdownInput : public QObject {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QObject* menu READ menu WRITE setMenu NOTIFY menuChanged)
public:
    using QObject::QObject;
    QObject *menu() const{return m_menu;}
    void setMenu(QObject *value);
signals:
    void menuChanged();
protected:
    bool eventFilter(QObject *object,QEvent *event) override;
private:
    void attachWindow(QQuickWindow *window);
    QPointer<QQuickMenu> m_menu;
    QPointer<QQuickWindow> m_window;
    QMetaObject::Connection m_windowChange;
};

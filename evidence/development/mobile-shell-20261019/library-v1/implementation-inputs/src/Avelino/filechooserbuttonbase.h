#pragma once
#include <QtQuickTemplates2/private/qquickbutton_p.h>
#include <QtQuickTemplates2/private/qquickmenu_p.h>
#include <QtQml/qqmlregistration.h>
#include <QPointer>

class FileChooserMenuBase;

// Qt excludes Popup windows from the application's accessible children. The
// owned opener exposes its separate-window menu instead of losing that subtree.
class FileChooserButtonBase : public QQuickButton {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(FileChooserMenuBase *accessibilityMenu READ accessibilityMenu WRITE setAccessibilityMenu NOTIFY accessibilityMenuChanged)
public:
    explicit FileChooserButtonBase(QQuickItem *parent=nullptr);
    FileChooserMenuBase *accessibilityMenu()const;
    void setAccessibilityMenu(FileChooserMenuBase *menu);
signals:
    void accessibilityMenuChanged();
private:
    QPointer<FileChooserMenuBase> m_menu;
    QList<QMetaObject::Connection> m_connections;
};

class FileChooserMenuBase : public QQuickMenu {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(FileChooserButtonBase *opener READ opener WRITE setOpener NOTIFY openerChanged)
public:
    explicit FileChooserMenuBase(QObject *parent=nullptr);
    FileChooserButtonBase *opener()const{return m_opener;}
    void setOpener(FileChooserButtonBase *button);
signals:
    void openerChanged();
private:
    QPointer<FileChooserButtonBase> m_opener;
};

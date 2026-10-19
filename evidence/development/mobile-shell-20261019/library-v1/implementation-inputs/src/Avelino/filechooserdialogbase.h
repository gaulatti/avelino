#pragma once
#include <QtQuickTemplates2/private/qquickdialog_p.h>
#include <QtQml/qqmlregistration.h>
#include <QPointer>

// Keep Qt's popup input/focus machinery while exposing the owned modal state.
class FileChooserDialogBase : public QQuickDialog {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(FileChooserDialogBase *accessibilityDialog READ accessibilityDialog WRITE setAccessibilityDialog NOTIFY accessibilityDialogChanged)
public:
    explicit FileChooserDialogBase(QObject *parent=nullptr);
    FileChooserDialogBase *accessibilityDialog()const{return m_dialog;}
    FileChooserDialogBase *accessibilityParent()const{return m_parent;}
    void setAccessibilityDialog(FileChooserDialogBase *dialog);
signals:
    void accessibilityDialogChanged();
private:
    QPointer<FileChooserDialogBase> m_dialog,m_parent;
    QList<QMetaObject::Connection> m_connections;
};

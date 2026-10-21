#pragma once
#include "filechooserbrowser.h"
#include <QQuickItem>

// Observe the scene in C++, so cancellation still runs after a Loader clears
// the QML creation context but before it deletes the control on a later frame.
class FileChooserHost : public QObject {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QQuickItem *owner READ owner WRITE setOwner NOTIFY ownerChanged)
    Q_PROPERTY(FileChooserBrowser *browser READ browser WRITE setBrowser NOTIFY browserChanged)
public:
    explicit FileChooserHost(QObject *parent=nullptr):QObject(parent){}
    ~FileChooserHost()override;
    QQuickItem *owner()const{return m_owner;}
    FileChooserBrowser *browser()const{return m_browser;}
    void setOwner(QQuickItem *owner);
    void setBrowser(FileChooserBrowser *browser);
signals:
    void ownerChanged();
    void browserChanged();
private:
    void detach();
    void cancel();
    QPointer<QQuickItem> m_owner;
    QPointer<FileChooserBrowser> m_browser;
    QList<QMetaObject::Connection> m_connections;
};

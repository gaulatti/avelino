#pragma once
#include <QObject>
#include <QStringList>
#include <QVariantList>
#include <QtQml/qqmlregistration.h>

class FileChooserPlaces : public QObject {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QVariantList entries READ entries NOTIFY changed)
    Q_PROPERTY(QString error READ error NOTIFY changed)
    Q_PROPERTY(QString lastPathInput READ lastPathInput NOTIFY changed)
    Q_PROPERTY(bool hasPathInput READ hasPathInput NOTIFY changed)
public:
    explicit FileChooserPlaces(QObject *parent=nullptr):QObject(parent){}
    QVariantList entries()const{return m_entries;}
    QString error()const{return m_readError.isEmpty()?m_writeError:m_readError;}
    QString lastPathInput()const{return m_lastPathInput;}
    bool hasPathInput()const{return m_hasPathInput;}
    QString currentFolder()const{return m_currentFolder;}
    void refresh(const QString &currentFolder);
    bool rememberAcceptedFolder(const QString &folder);
    Q_INVOKABLE bool rememberPathInput(const QString &input);
signals:
    void changed();
private:
    bool save(const QString *folder,const QString *input);
    QString m_currentFolder,m_lastPathInput,m_readError,m_writeError;
    QVariantList m_entries;
    bool m_hasPathInput=false;
};

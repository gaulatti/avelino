#pragma once
#include <QObject>
#include <QStringList>
#include <QUrl>
#include <QVariantList>
#include <QtQml/qqmlregistration.h>

class FileChooserPlaces : public QObject {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QVariantList entries READ entries NOTIFY changed)
    Q_PROPERTY(QString error READ error NOTIFY changed)
    Q_PROPERTY(QString lastPathInput READ lastPathInput NOTIFY changed)
    Q_PROPERTY(bool hasPathInput READ hasPathInput NOTIFY changed)
    Q_PROPERTY(QVariantList pathTargets READ pathTargets NOTIFY changed)
public:
    explicit FileChooserPlaces(QObject *parent=nullptr):QObject(parent){}
    QVariantList entries()const{return m_entries;}
    QString error()const{return m_readError.isEmpty()?m_writeError:m_readError;}
    QString lastPathInput()const{return m_lastPathInput;}
    bool hasPathInput()const{return m_hasPathInput;}
    QVariantList pathTargets()const{return m_pathTargets;}
    QString currentFolder()const{return m_currentFolder;}
    void refresh(const QString &currentFolder);
    bool rememberAcceptedFolder(const QString &folder);
    Q_INVOKABLE bool rememberPathInput(const QString &input);
    Q_INVOKABLE bool rememberPathNavigation(const QString &input,const QUrl &target);
signals:
    void changed();
private:
    bool save(const QString *folder,const QString *input,const QString *target=nullptr);
    QString m_currentFolder,m_lastPathInput,m_readError,m_writeError;
    QVariantList m_entries,m_pathTargets;
    bool m_hasPathInput=false;
};

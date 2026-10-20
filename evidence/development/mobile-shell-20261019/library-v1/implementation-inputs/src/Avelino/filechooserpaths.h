#pragma once
#include <QObject>
#include <QUrl>
#include <QVariantList>
#include <QtQml/qqmlregistration.h>

// Raw text and highlighted destinations are deliberately separate. Neither
// browsing suggestions nor cancelling this model mutates chooser selection.
class FileChooserPaths : public QObject {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QString input READ input WRITE setInput NOTIFY inputChanged)
    Q_PROPERTY(QVariantList entries READ entries NOTIFY entriesChanged)
    Q_PROPERTY(int currentIndex READ currentIndex NOTIFY currentIndexChanged)
    Q_PROPERTY(QUrl selectedUrl READ selectedUrl NOTIFY currentIndexChanged)
    Q_PROPERTY(QString error READ error NOTIFY entriesChanged)
public:
    using QObject::QObject;
    QString input()const{return m_input;}
    void setInput(const QString &input);
    QVariantList entries()const{return m_entries;}
    int currentIndex()const{return m_index;}
    QUrl selectedUrl()const;
    QString error()const{return m_error;}
    Q_INVOKABLE void begin(const QString &folder,const QString &input,const QVariantList &targets,const QString &storageError);
    Q_INVOKABLE void refresh();
    Q_INVOKABLE void select(int index);
    Q_INVOKABLE void move(int offset);
    Q_INVOKABLE QString completion()const;
signals:
    void inputChanged();
    void entriesChanged();
    void currentIndexChanged();
private:
    void rebuild();
    QString m_folder,m_input,m_error,m_storageError,m_completion;
    QVariantList m_recent,m_entries;
    int m_index=-1;
};

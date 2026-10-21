#pragma once
#include "filechoosermodel.h"
#include <QPointer>

class FileSearchQuery;

// Searches the existing session index. It never changes indexing locations or
// replaces unavailable indexed search with a filesystem crawl.
class FileChooserSearch : public QAbstractListModel {
    Q_OBJECT
    QML_ANONYMOUS
    Q_PROPERTY(QString query READ query WRITE setQuery NOTIFY changed)
    Q_PROPERTY(QString mode READ mode WRITE setMode NOTIFY changed)
    Q_PROPERTY(bool folderOnly READ folderOnly WRITE setFolderOnly NOTIFY changed)
    Q_PROPERTY(bool active READ active NOTIFY changed)
    Q_PROPERTY(bool busy READ busy NOTIFY changed)
    Q_PROPERTY(QString error READ error NOTIFY changed)
    Q_PROPERTY(int count READ count NOTIFY changed)
    Q_PROPERTY(int currentIndex READ currentIndex NOTIFY changed)
    Q_PROPERTY(bool canOpen READ canOpen NOTIFY changed)
public:
    explicit FileChooserSearch(QObject *parent=nullptr);
    ~FileChooserSearch() override;
    enum Role {NameRole=Qt::UserRole+1,UrlRole,DirectoryRole,EligibleRole,SelectedRole,KindRole,PathRole};
    int rowCount(const QModelIndex &parent={})const override{return parent.isValid()?0:m_rows.size();}
    QVariant data(const QModelIndex &index,int role)const override;
    QHash<int,QByteArray> roleNames()const override;
    QString query()const{return m_query;}
    void setQuery(const QString &value);
    QString mode()const{return m_mode;}
    void setMode(const QString &value);
    bool folderOnly()const{return m_folderOnly;}
    void setFolderOnly(bool value);
    bool active()const{return m_open&&!m_query.isEmpty();}
    bool busy()const{return m_busy;}
    QString error()const{return m_error;}
    int count()const{return m_rows.size();}
    int currentIndex()const;
    bool canOpen()const;
    QVariantList selectedUrls()const;
    void setContext(bool open,const QVariantList &types,const QUrl &folder);
    Q_INVOKABLE void clear();
    Q_INVOKABLE void refresh();
    Q_INVOKABLE QVariantMap entry(int row)const;
    Q_INVOKABLE void select(int row,int modifiers=0);
    Q_INVOKABLE void selectFromInput(int row);
    Q_INVOKABLE void move(int offset,int modifiers=0);
    Q_INVOKABLE void selectAll();
    Q_INVOKABLE void activate(int row);
    Q_INVOKABLE void acceptSelection();
signals:
    void changed();
    void navigateRequested(const QUrl &url);
    void result(const QVariantMap &value);
private:
    void restart(bool retainSelection=false);
    void stop();
    void selectionChanged();
    QVariantList m_rows,m_types;
    FileChooserModel m_validator;
    QList<QPointer<FileSearchQuery>> m_jobs;
    QSet<QString> m_selected;
    QUrl m_folder;
    QString m_query,m_mode="general",m_error,m_current,m_anchor;
    quint64 m_generation=0;
    bool m_open=false,m_folderOnly=false,m_busy=false,m_completing=false;
};

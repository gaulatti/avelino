#pragma once
#include "filechoosermodel.h"
#include <QPointer>

// A visible hierarchy over the same read-only directory/type adapter as Columns.
// Row identities, selection and disclosure survive sorting and model refreshes.
class FileChooserListing : public QAbstractListModel {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(int count READ count NOTIFY changed)
    Q_PROPERTY(int currentIndex READ currentIndex NOTIFY changed)
    Q_PROPERTY(bool treeMode READ treeMode WRITE setTreeMode NOTIFY changed)
    Q_PROPERTY(QString sortKey READ sortKey NOTIFY changed)
    Q_PROPERTY(bool ascending READ ascending NOTIFY changed)
    Q_PROPERTY(QString error READ error NOTIFY changed)
public:
    using QAbstractListModel::QAbstractListModel;
    enum Role {NameRole=Qt::UserRole+1,UrlRole,DirectoryRole,EligibleRole,SelectedRole,
        DepthRole,ExpandedRole,SizeRole,KindRole,ErrorRole};
    int rowCount(const QModelIndex &parent={})const override{return parent.isValid()?0:m_rows.size();}
    int count()const{return m_rows.size();}
    QVariant data(const QModelIndex &index,int role)const override;
    QHash<int,QByteArray> roleNames()const override;
    void setRoot(FileChooserModel *root);
    bool treeMode()const{return m_tree;}
    void setTreeMode(bool tree);
    QString sortKey()const{return m_sort;}
    bool ascending()const{return m_ascending;}
    QString error()const{return m_error;}
    int currentIndex()const;
    QVariantList selection()const;
    void setSelection(const QVariantList &urls);
    QVariantList selectedUrls()const;
    bool canOpen()const;
    Q_INVOKABLE QVariantMap entry(int row)const;
    Q_INVOKABLE void select(int row,int modifiers=0);
    Q_INVOKABLE void selectFromInput(int row);
    Q_INVOKABLE void selectAll();
    Q_INVOKABLE void move(int offset,int modifiers=0);
    Q_INVOKABLE void right();
    Q_INVOKABLE void left();
    Q_INVOKABLE void toggleExpanded(int row);
    Q_INVOKABLE void sortBy(const QString &key);
    Q_INVOKABLE void activate(int row);
    Q_INVOKABLE void acceptSelection();
signals:
    void changed();
    void navigateRequested(const QUrl &url);
    void result(const QVariantMap &value);
private:
    struct Row {QVariantMap value;int depth;QString parent;};
    FileChooserModel *directory(const QUrl &url);
    void appendRows(FileChooserModel *model,int depth,const QString &parent);
    void scheduleRebuild();
    void rebuild();
    void selectionChanged();
    void setExpanded(int row,bool expanded);
    QUrl navigationTarget()const;
    QPointer<FileChooserModel> m_root;
    QMetaObject::Connection m_listingConnection,m_typeConnection,m_destroyConnection;
    QHash<QString,FileChooserModel*> m_children;
    QList<Row> m_rows;
    QSet<QString> m_selected,m_expanded;
    QString m_current,m_anchor,m_sort="name",m_error;
    bool m_tree=true,m_ascending=true,m_queued=false,m_building=false,m_completing=false;
};

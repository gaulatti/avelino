#pragma once
#include <QAbstractListModel>
#include <QtQml/qqmlregistration.h>
#include <QVariantMap>

// Retain each logical token's delegate and accessible object while its query,
// mode or position changes. Document object resources supply stable identity.
class FileChooserSearchTokens:public QAbstractListModel {
    Q_OBJECT
    QML_ANONYMOUS
    Q_PROPERTY(int count READ count NOTIFY countChanged)
public:
    struct Row {QString identity;QVariantMap value;};
    explicit FileChooserSearchTokens(QObject *parent=nullptr):QAbstractListModel(parent){}
    int count()const{return m_rows.size();}
    int rowCount(const QModelIndex &parent={})const override{return parent.isValid()?0:count();}
    QVariant data(const QModelIndex &index,int role)const override;
    QHash<int,QByteArray> roleNames()const override{return {{Qt::UserRole+1,"token"}};}
    bool synchronize(const QList<Row> &rows);
signals:
    void countChanged();
private:
    QList<Row> m_rows;
};

#pragma once
#include <QAbstractListModel>
#include <QJSValue>
#include <QPointer>
#include <QQmlParserStatus>
#include <QQuickItem>
#include <QUuid>
#include <QtQml/qqmlregistration.h>

class BleeckerMenuItem : public QObject {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QString id READ id CONSTANT)
    Q_PROPERTY(QString title READ title WRITE setTitle NOTIFY titleChanged REQUIRED)
    Q_PROPERTY(QVariant systemImage READ systemImage WRITE setSystemImage NOTIFY systemImageChanged)
    Q_PROPERTY(bool destructive READ destructive WRITE setDestructive NOTIFY destructiveChanged)
public:
    using QObject::QObject;
    QString id() const{return m_id;}
    QString title() const{return m_title;}
    QVariant systemImage() const{return m_image;}
    bool destructive() const{return m_destructive;}
    void setTitle(const QString &value){if(value==m_title)return;m_title=value;emit titleChanged();}
    void setSystemImage(const QVariant &value);
    void setDestructive(bool value){if(value==m_destructive)return;m_destructive=value;emit destructiveChanged();}
    Q_INVOKABLE void trigger(){emit triggered();}
signals:
    void titleChanged();
    void systemImageChanged();
    void destructiveChanged();
    void triggered();
private:
    const QString m_id=QUuid::createUuid().toString(QUuid::WithoutBraces);
    QString m_title;
    QVariant m_image;
    bool m_destructive=false;
};

class MenuItems : public QAbstractListModel, public QQmlParserStatus {
    Q_OBJECT
    QML_ELEMENT
    Q_INTERFACES(QQmlParserStatus)
    Q_PROPERTY(QJSValue items READ items WRITE setItems NOTIFY itemsChanged)
    Q_PROPERTY(int count READ count NOTIFY changed)
public:
    using QAbstractListModel::QAbstractListModel;
    enum Role {ItemRole=Qt::UserRole+1,TitleRole,ImageRole,DestructiveRole,KeyRole};
    int rowCount(const QModelIndex &parent={}) const override{return parent.isValid() ? 0:m_rows.size();}
    int count() const{return m_rows.size();}
    QVariant data(const QModelIndex &index,int role) const override;
    QHash<int,QByteArray> roleNames() const override;
    QJSValue items() const{return m_items;}
    void setItems(const QJSValue &value);
    Q_INVOKABLE void cancelPointer(QQuickItem *item) const;
    void classBegin() override{}
    void componentComplete() override{m_complete=true;reconcile();}
signals:
    void itemsChanged();
    void changed();
private:
    void reconcile();
    void refresh(BleeckerMenuItem *item);
    void removeDestroyed();
    QJSValue m_items;
    QList<QPointer<BleeckerMenuItem>> m_rows;
    QList<QMetaObject::Connection> m_connections;
    bool m_complete=false;
};

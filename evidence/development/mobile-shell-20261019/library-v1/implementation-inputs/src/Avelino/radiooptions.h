#pragma once
#include <QAbstractListModel>
#include <QJSValue>
#include <QQmlParserStatus>
#include <QtQml/qqmlregistration.h>

// Stable value-identified rows model the source ForEach across producer snapshots.
class RadioOptions : public QAbstractListModel, public QQmlParserStatus {
    Q_OBJECT
    QML_ELEMENT
    Q_INTERFACES(QQmlParserStatus)
    Q_PROPERTY(QJSValue options READ options WRITE setOptions NOTIFY optionsChanged)
    Q_PROPERTY(QJSValue selection READ selection WRITE setSelection NOTIFY selectionChanged)
    Q_PROPERTY(QJSValue valueIdentity READ valueIdentity WRITE setValueIdentity NOTIFY valueIdentityChanged)
public:
    using QAbstractListModel::QAbstractListModel;
    enum Role {ValueRole=Qt::UserRole+1,LabelRole,DisabledRole,SelectedRole,KeyRole};
    int rowCount(const QModelIndex &parent={}) const override {return parent.isValid() ? 0:m_rows.size();}
    QVariant data(const QModelIndex &index,int role) const override;
    QHash<int,QByteArray> roleNames() const override;
    QJSValue options() const{return m_options;}
    QJSValue selection() const{return m_selection;}
    QJSValue valueIdentity() const{return m_identity;}
    void setOptions(const QJSValue &value);
    void setSelection(const QJSValue &value);
    void setValueIdentity(const QJSValue &value);
    void classBegin() override {}
    void componentComplete() override {m_complete=true;reconcile();}
signals:
    void optionsChanged();
    void selectionChanged();
    void valueIdentityChanged();
private:
    struct Row {QString key,label;bool disabled;QJSValue value;};
    void reconcile();
    QList<Row> m_rows;
    QJSValue m_options,m_selection,m_identity;
    QString m_selected;
    bool m_complete=false,m_selectionReflexive=true;
};

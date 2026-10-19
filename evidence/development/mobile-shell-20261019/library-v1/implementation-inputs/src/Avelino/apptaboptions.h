#pragma once
#include <QAbstractListModel>
#include <QJSValue>
#include <QQmlParserStatus>
#include <QtQml/qqmlregistration.h>

// Values retain the source ForEach identity across caller snapshots.
class AppTabOptions : public QAbstractListModel, public QQmlParserStatus {
    Q_OBJECT
    QML_ELEMENT
    Q_INTERFACES(QQmlParserStatus)
    Q_PROPERTY(QJSValue tabs READ tabs WRITE setTabs NOTIFY tabsChanged)
    Q_PROPERTY(QJSValue selection READ selection WRITE setSelection NOTIFY selectionChanged)
    Q_PROPERTY(QJSValue valueIdentity READ valueIdentity WRITE setValueIdentity NOTIFY valueIdentityChanged)
public:
    using QAbstractListModel::QAbstractListModel;
    enum Role {ValueRole=Qt::UserRole+1,LabelRole,ImageRole,DisabledRole,SelectedRole,KeyRole,
        AccessibilityLabelRole,BadgeTextRole,BadgeVisibleRole,BadgeValueRole};
    int rowCount(const QModelIndex &parent={}) const override {return parent.isValid() ? 0:m_rows.size();}
    QVariant data(const QModelIndex &index,int role) const override;
    QHash<int,QByteArray> roleNames() const override;
    QJSValue tabs() const{return m_tabs;}
    QJSValue selection() const{return m_selection;}
    QJSValue valueIdentity() const{return m_identity;}
    void setTabs(const QJSValue &value);
    void setSelection(const QJSValue &value);
    void setValueIdentity(const QJSValue &value);
    void classBegin() override {}
    void componentComplete() override {m_complete=true;reconcile();}
signals:
    void tabsChanged();
    void selectionChanged();
    void valueIdentityChanged();
private:
    struct Row {QString key,label,image,accessibilityLabel,badgeText,badgeValue;bool disabled,badgeVisible;QJSValue value;};
    void reconcile();
    QList<Row> m_rows;
    QJSValue m_tabs,m_selection,m_identity;
    QString m_selected;
    bool m_complete=false,m_reflexive=true;
};

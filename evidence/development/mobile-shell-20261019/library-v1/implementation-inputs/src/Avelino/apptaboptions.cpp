#include "apptaboptions.h"
#include "selectionidentity.h"
#include "valuetools.h"
#include <QSet>
#include <QVariantList>
#include <cmath>

QVariant AppTabOptions::data(const QModelIndex &index,int role) const {
    if(!index.isValid() ||index.row()<0 ||index.row()>=m_rows.size())return {};
    const auto &r=m_rows[index.row()];
    switch(role) {
    case ValueRole:return QVariant::fromValue(r.value);
    case LabelRole:return r.label;
    case ImageRole:return r.image;
    case DisabledRole:return r.disabled;
    case SelectedRole:return m_reflexive &&r.key==m_selected;
    case KeyRole:return r.key;
    case AccessibilityLabelRole:return r.accessibilityLabel;
    case BadgeTextRole:return r.badgeText;
    case BadgeVisibleRole:return r.badgeVisible;
    case BadgeValueRole:return r.badgeValue;
    default:return {};
    }
}
QHash<int,QByteArray> AppTabOptions::roleNames() const {
    return {{ValueRole,"tabValue"},{LabelRole,"tabLabel"},{ImageRole,"tabSystemImage"},
        {DisabledRole,"tabDisabled"},{SelectedRole,"tabSelected"},{KeyRole,"tabKey"},
        {AccessibilityLabelRole,"tabAccessibilityLabel"},{BadgeTextRole,"tabBadgeText"},
        {BadgeVisibleRole,"tabBadgeVisible"},{BadgeValueRole,"tabBadgeValue"}};
}
void AppTabOptions::setTabs(const QJSValue &value){m_tabs=value;if(m_complete)reconcile();emit tabsChanged();}
void AppTabOptions::setSelection(const QJSValue &value) {
    m_selection=value;
    if(m_complete) {
        m_selected=SelectionIdentity::key(value,m_identity,"AppTabBar");
        m_reflexive=!(value.isNumber() &&std::isnan(value.toNumber()));
        if(!m_rows.isEmpty())emit dataChanged(index(0),index(m_rows.size()-1),{SelectedRole});
    }
    emit selectionChanged();
}
void AppTabOptions::setValueIdentity(const QJSValue &value){m_identity=value;if(m_complete)reconcile();emit valueIdentityChanged();}
void AppTabOptions::reconcile() {
    if(!m_tabs.isArray() &&m_tabs.toVariant().metaType()!=QMetaType::fromType<QVariantList>())qFatal("AppTabBar tabs must be an array");
    const auto count=m_tabs.property("length").toUInt();
    QList<Row> next;QSet<QString> keys;BleeckerValueTools tools;
    for(quint32 i=0;i<count;++i) {
        const auto tab=m_tabs.property(i),value=tab.property("value"),label=tab.property("label"),image=tab.property("systemImage");
        if(!tab.isObject() ||!tab.hasProperty("value") ||!label.isString() ||!image.isString())
            qFatal("AppTabBar tabs require value, string label and string systemImage");
        const auto disabled=tab.property("disabled"),accessible=tab.property("accessibilityLabel"),badge=tab.property("badge");
        if(!disabled.isUndefined() &&!disabled.isBool())qFatal("AppTabBar disabled flags must be Boolean");
        if(!accessible.isUndefined() &&!accessible.isNull() &&!accessible.isString())qFatal("AppTabBar accessibilityLabel must be a string or null");
        const auto key=SelectionIdentity::key(value,m_identity,"AppTabBar");
        if(keys.contains(key))qFatal("AppTabBar tabs require distinct stable value identities");
        keys.insert(key);
        const auto b=badge.isUndefined() ||badge.isNull() ? QVariantMap{}:tools.appTabBadge(QVariant::fromValue(badge));
        next.append({key,label.toString(),image.toString(),accessible.isUndefined() ||accessible.isNull() ? label.toString():accessible.toString(),
            b.value("text").toString(),b.value("accessibilityValue").toString(),disabled.toBool(),b.value("visible").toBool(),value});
    }
    m_selected=SelectionIdentity::key(m_selection,m_identity,"AppTabBar");
    m_reflexive=!(m_selection.isNumber() &&std::isnan(m_selection.toNumber()));
    for(int i=m_rows.size()-1;i>=0;--i)if(!keys.contains(m_rows[i].key)){beginRemoveRows({},i,i);m_rows.removeAt(i);endRemoveRows();}
    for(int i=0;i<next.size();++i) {
        int found=-1;for(int j=i;j<m_rows.size();++j)if(m_rows[j].key==next[i].key){found=j;break;}
        if(found<0){beginInsertRows({},i,i);m_rows.insert(i,next[i]);endInsertRows();}
        else if(found!=i){beginMoveRows({},found,found,{},i);m_rows.move(found,i);endMoveRows();}
        m_rows[i]=next[i];emit dataChanged(index(i),index(i));
    }
}

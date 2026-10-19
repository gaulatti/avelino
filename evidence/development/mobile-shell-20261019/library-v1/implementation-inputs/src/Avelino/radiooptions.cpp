#include "radiooptions.h"
#include "selectionidentity.h"
#include <QSet>
#include <QVariantList>
#include <cmath>

QVariant RadioOptions::data(const QModelIndex &index,int role) const {
    if(!index.isValid() || index.row()<0 || index.row()>=m_rows.size())return {};
    const auto &row=m_rows[index.row()];
    switch(role) {
    case ValueRole:return QVariant::fromValue(row.value);
    case LabelRole:return row.label;
    case DisabledRole:return row.disabled;
    case SelectedRole:return m_selectionReflexive && row.key==m_selected;
    case KeyRole:return row.key;
    default:return {};
    }
}
QHash<int,QByteArray> RadioOptions::roleNames() const {
    return {{ValueRole,"optionValue"},{LabelRole,"optionLabel"},{DisabledRole,"optionDisabled"},{SelectedRole,"optionSelected"},{KeyRole,"optionKey"}};
}
void RadioOptions::setOptions(const QJSValue &value){m_options=value;if(m_complete)reconcile();emit optionsChanged();}
void RadioOptions::setSelection(const QJSValue &value){
    m_selection=value;
    if(m_complete){m_selected=SelectionIdentity::key(value,m_identity);m_selectionReflexive=!(value.isNumber() && std::isnan(value.toNumber()));if(!m_rows.isEmpty())emit dataChanged(index(0),index(m_rows.size()-1),{SelectedRole});}
    emit selectionChanged();
}
void RadioOptions::setValueIdentity(const QJSValue &value){m_identity=value;if(m_complete)reconcile();emit valueIdentityChanged();}
void RadioOptions::reconcile() {
    if(!m_options.isArray() && m_options.toVariant().metaType()!=QMetaType::fromType<QVariantList>())qFatal("RadioGroup options must be an array");
    const auto count=m_options.property(QStringLiteral("length")).toUInt();
    QList<Row> next;QSet<QString> keys;
    for(quint32 i=0;i<count;++i) {
        const auto option=m_options.property(i);
        if(!option.isObject() || !option.hasProperty(QStringLiteral("value")) || !option.property(QStringLiteral("label")).isString())qFatal("RadioGroup options require value and string label");
        const auto disabled=option.property(QStringLiteral("disabled"));
        if(!disabled.isUndefined() && !disabled.isBool())qFatal("RadioGroup disabled flags must be Boolean");
        const auto value=option.property(QStringLiteral("value"));
        const auto key=SelectionIdentity::key(value,m_identity);
        if(keys.contains(key))qFatal("RadioGroup options require distinct stable value identities");
        keys.insert(key);next.append({key,option.property(QStringLiteral("label")).toString(),disabled.toBool(),value});
    }
    m_selected=SelectionIdentity::key(m_selection,m_identity);
    m_selectionReflexive=!(m_selection.isNumber() && std::isnan(m_selection.toNumber()));
    for(int i=m_rows.size()-1;i>=0;--i)if(!keys.contains(m_rows[i].key)) {beginRemoveRows({},i,i);m_rows.removeAt(i);endRemoveRows();}
    for(int i=0;i<next.size();++i) {
        int found=-1;
        for(int j=i;j<m_rows.size();++j)if(m_rows[j].key==next[i].key){found=j;break;}
        if(found<0){beginInsertRows({},i,i);m_rows.insert(i,next[i]);endInsertRows();}
        else if(found!=i){beginMoveRows({},found,found,{},i);m_rows.move(found,i);endMoveRows();}
        m_rows[i]=next[i];emit dataChanged(index(i),index(i));
    }
}

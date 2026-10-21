#include "filechoosersearchtokens.h"
#include <QPointer>

QVariant FileChooserSearchTokens::data(const QModelIndex &index,int role)const{
    if(!index.isValid()||index.row()<0||index.row()>=count()||role!=Qt::UserRole+1)return {};
    return m_rows[index.row()].value;
}
bool FileChooserSearchTokens::synchronize(const QList<Row> &rows){
    const int previous=count();QPointer<FileChooserSearchTokens> guard(this);
    for(int index=0;index<rows.size();++index){
        if(index>=m_rows.size()||m_rows[index].identity!=rows[index].identity){
            int existing=index+1;while(existing<m_rows.size()&&m_rows[existing].identity!=rows[index].identity)++existing;
            if(existing<m_rows.size()){
                beginMoveRows({},existing,existing,{},index);if(!guard)return false;
                m_rows.move(existing,index);endMoveRows();if(!guard)return false;
            }else{
                beginInsertRows({},index,index);if(!guard)return false;
                m_rows.insert(index,rows[index]);endInsertRows();if(!guard)return false;
            }
        }
        if(m_rows[index].value!=rows[index].value){
            m_rows[index]=rows[index];emit dataChanged(this->index(index),this->index(index),{Qt::UserRole+1});if(!guard)return false;
        }
    }
    if(m_rows.size()>rows.size()){
        beginRemoveRows({},rows.size(),m_rows.size()-1);if(!guard)return false;
        m_rows.erase(m_rows.begin()+rows.size(),m_rows.end());endRemoveRows();if(!guard)return false;
    }
    if(previous!=count())emit countChanged();return bool(guard);
}

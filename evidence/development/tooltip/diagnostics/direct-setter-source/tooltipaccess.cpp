#include "tooltipaccess.h"
#include <QtQuick/private/qquickaccessibleattached_p.h>
#include <QtQuick/private/qquickitem_p.h>
#include <QSet>
#include <QTimer>
#include <functional>

static QHash<QQuickAccessibleAttached*,TooltipAccess*> &owners() {
    static QHash<QQuickAccessibleAttached*,TooltipAccess*> value;return value;
}
TooltipAccess::TooltipAccess(QObject *parent):QObject(parent) {}
TooltipAccess::~TooltipAccess() {clear();}
void TooltipAccess::setTarget(QQuickItem *target) {
    if(target==m_target)return;
    clear();disconnect(m_targetDestroyed);m_target=target;
    if(target)m_targetDestroyed=connect(target,&QObject::destroyed,this,[this]{clear();m_target=nullptr;emit targetChanged();});
    emit targetChanged();scheduleRefresh();
}
void TooltipAccess::setText(const QString &text) {
    if(text==m_text)return;m_text=text;m_setting=true;
    for(const auto &node:m_nodes)if(node.object)node.object->setDescription(m_text);
    m_setting=false;emit textChanged();
}
void TooltipAccess::scheduleRefresh() {
    if(m_queued)return;m_queued=true;
    QTimer::singleShot(0,this,[this]{m_queued=false;refresh();});
}
void TooltipAccess::release(QQuickAccessibleAttached *key) {
    auto found=m_nodes.find(key);if(found==m_nodes.end())return;
    const auto node=found.value();m_nodes.erase(found);
    disconnect(node.changed);disconnect(node.destroyed);owners().remove(key);
    if(node.object){m_setting=true;node.object->setDescription(node.original);m_setting=false;}
}
void TooltipAccess::clear() {
    for(const auto &connection:m_structure)disconnect(connection);m_structure.clear();
    const auto keys=m_nodes.keys();for(auto key:keys)release(key);
}
void TooltipAccess::refresh() {
    for(const auto &connection:m_structure)disconnect(connection);m_structure.clear();
    QSet<QQuickAccessibleAttached*> present;
    std::function<void(QQuickItem*)> walk=[&](QQuickItem *item){
        m_structure.append(connect(item,&QQuickItem::childrenChanged,this,&TooltipAccess::scheduleRefresh));
        const auto role=QQuickItemPrivate::get(item)->effectiveAccessibleRole();
        auto attached=QQuickAccessibleAttached::attachedProperties(item);
        if(!attached && role!=QAccessible::NoRole)
            attached=qobject_cast<QQuickAccessibleAttached*>(qmlAttachedPropertiesObject<QQuickAccessibleAttached>(item,true));
        if(attached) {
            m_structure.append(connect(attached,&QQuickAccessibleAttached::roleChanged,this,&TooltipAccess::scheduleRefresh));
            m_structure.append(connect(attached,&QQuickAccessibleAttached::ignoredChanged,this,&TooltipAccess::scheduleRefresh));
            if(!attached->ignored() && role!=QAccessible::NoRole)present.insert(attached);
        }
        for(auto child:item->childItems())walk(child);
    };
    if(m_target)walk(m_target);
    const auto previous=m_nodes.keys();for(auto key:previous)if(!present.contains(key))release(key);
    for(auto attached:present) {
        if(m_nodes.contains(attached))continue;
        if(owners().contains(attached))qFatal("A Tooltip accessible target cannot have multiple help owners");
        owners().insert(attached,this);
        Node node;node.object=attached;node.original=attached->description();
        node.changed=connect(attached,&QQuickAccessibleAttached::descriptionChanged,this,[this,attached]{
            if(m_setting)return;
            auto found=m_nodes.find(attached);if(found==m_nodes.end() || !found->object)return;
            found->original=attached->description();m_setting=true;attached->setDescription(m_text);m_setting=false;
        });
        node.destroyed=connect(attached,&QObject::destroyed,this,[this,attached]{owners().remove(attached);m_nodes.remove(attached);});
        m_nodes.insert(attached,node);m_setting=true;attached->setDescription(m_text);m_setting=false;
    }
}

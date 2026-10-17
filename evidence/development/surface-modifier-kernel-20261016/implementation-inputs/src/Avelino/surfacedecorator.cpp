#include "surfacedecorator.h"
#include "proposalrow.h"
#include <QtQml/qqml.h>
#include <QSet>
#include <functional>

void SurfaceDecorator::setTarget(QQuickItem *item) {
    if(m_target==item)return;
    disconnectObservers();
    while(!m_parts.isEmpty())removePart(m_parts.size()-1);
    m_target=item;emit configurationChanged();schedule();
}
void SurfaceDecorator::setDelegate(QQmlComponent *component) {
    if(m_delegate==component)return;
    m_delegate=component;emit configurationChanged();schedule();
}
void SurfaceDecorator::componentComplete() {
    m_complete=true;
    if(!m_target||!m_delegate)qFatal("Surface decoration requires a target and part component");
    rebuild();
}
void SurfaceDecorator::disconnectObservers() {
    for(const auto &connection:m_connections)disconnect(connection);
    m_connections.clear();
}
void SurfaceDecorator::schedule() {
    if(!m_complete||m_rebuilding||m_queued)return;
    m_queued=true;
    QMetaObject::invokeMethod(this,[this]{m_queued=false;rebuild();},Qt::QueuedConnection);
}
QQuickItem *SurfaceDecorator::callerOf(QQuickItem *wrapper) {
    return wrapper ? qvariant_cast<QQuickItem*>(wrapper->property("callerItem")):nullptr;
}
QQuickItem *SurfaceDecorator::enclosingPart(QQuickItem *item) {
    if(!item)return nullptr;
    const auto host=item->parentItem();
    for(auto ancestor=host;ancestor;ancestor=ancestor->parentItem()) {
        if(qobject_cast<SurfacePartBase*>(ancestor))
            return callerOf(ancestor)==item && qvariant_cast<QQuickItem*>(ancestor->property("contentHost"))==host ? ancestor:nullptr;
    }
    return nullptr;
}
QQuickItem *SurfaceDecorator::logicalParent(QQuickItem *item) {
    while(auto wrapper=enclosingPart(item))item=wrapper;
    return item ? item->parentItem():nullptr;
}
void SurfaceDecorator::removePart(int index) {
    const auto part=m_parts.takeAt(index);
    const auto caller=callerOf(part.wrapper);
    if(caller && caller->parentItem()==part.host) {
        // A surrounding surface may decorate this part too. Remove just our
        // layer, retaining its caller and the other modifier's layer.
        const auto outer=enclosingPart(part.wrapper);
        caller->setParentItem(outer ? part.wrapper->parentItem():part.originalParent.data());
        if(part.wrapper && caller->parentItem()==part.wrapper->parentItem())caller->stackBefore(part.wrapper);
        if(outer)outer->setProperty("callerItem",QVariant::fromValue(caller));
    }
    delete part.wrapper;
}
void SurfaceDecorator::rebuild() {
    if(m_rebuilding||!m_target||!m_delegate)return;
    m_rebuilding=true;disconnectObservers();
    for(int i=m_parts.size()-1;i>=0;--i) {
        const auto &part=m_parts[i];
        const auto caller=callerOf(part.wrapper);
        if(!caller||!part.originalParent||!part.wrapper||!part.host
            ||caller->parentItem()!=part.host
            ||logicalParent(part.wrapper)!=part.originalParent)removePart(i);
    }
    QList<QPointer<QQuickItem>> leaves;
    QSet<QQuickItem*> observed;
    auto observe=[&](QQuickItem *item) {
        if(observed.contains(item))return;
        observed.insert(item);
        m_connections.append(connect(item,&QQuickItem::childrenChanged,this,&SurfaceDecorator::schedule));
        m_connections.append(connect(item,&QQuickItem::parentChanged,this,&SurfaceDecorator::schedule));
        m_connections.append(connect(item,&QObject::destroyed,this,&SurfaceDecorator::schedule));
        auto hint=qobject_cast<BleeckerLayout*>(qmlAttachedPropertiesObject<BleeckerLayout>(item,true));
        m_connections.append(connect(hint,&BleeckerLayout::structureChanged,this,&SurfaceDecorator::schedule));
    };
    bool retry=false;
    std::function<void(QQuickItem*)> append=[&](QQuickItem *item) {
        if(!item)return;
        // An owned wrapper stands for its caller, never for its paint tree.
        for(const auto &part:m_parts)if(part.wrapper==item){append(callerOf(item));return;}
        if(qobject_cast<SurfacePartBase*>(item)) {
            // A later outer modifier can wrap our part in place. Traverse that
            // layer transparently when recovering our original logical tree.
            for(auto caller=callerOf(item);qobject_cast<SurfacePartBase*>(caller);caller=callerOf(caller)) {
                bool owned=false;
                for(const auto &part:m_parts)if(part.wrapper==caller){owned=true;break;}
                if(owned){append(callerOf(item));return;}
            }
        }
        if(item->inherits("QQuickRepeater"))return;
        observe(item);
        if(auto nested=qvariant_cast<SurfaceDecorator*>(item->property("__surfaceDecorator"));nested && nested!=this) {
            if(!nested->m_complete){retry=true;return;}
            nested->rebuild();
        }
        auto hint=qobject_cast<BleeckerLayout*>(qmlAttachedPropertiesObject<BleeckerLayout>(item,true));
        if(!hint->participates)return;
        if(hint->flattenChildren)for(auto nested:item->childItems())append(nested);
        else leaves.append(item);
    };
    observe(m_target);
    for(auto item:m_target->childItems())append(item);
    if(retry){m_rebuilding=false;schedule();return;}
    for(int i=m_parts.size()-1;i>=0;--i)
        if(!leaves.contains(callerOf(m_parts[i].wrapper)))removePart(i);
    for(const auto &caller:leaves) {
        if(!caller)continue;
        bool decorated=false;
        for(const auto &part:m_parts)if(callerOf(part.wrapper)==caller){decorated=true;break;}
        if(decorated)continue;
        auto originalParent=caller->parentItem();
        auto object=m_delegate->createWithInitialProperties({{"callerItem",QVariant::fromValue(caller.data())}},m_delegate->creationContext());
        auto wrapper=qobject_cast<QQuickItem*>(object);
        if(!wrapper)qFatal("Surface part creation failed: %s",qPrintable(m_delegate->errorString()));
        auto host=qvariant_cast<QQuickItem*>(wrapper->property("contentHost"));
        if(!host)qFatal("Surface part must expose its content host");
        wrapper->setParent(this);
        wrapper->setParentItem(originalParent);
        wrapper->stackBefore(caller);
        caller->setParentItem(host);
        m_parts.append({originalParent,wrapper,host});
    }
    m_rebuilding=false;
}

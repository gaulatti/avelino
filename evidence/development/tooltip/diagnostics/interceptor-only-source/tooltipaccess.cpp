#include "tooltipaccess.h"
#include <QtQuick/private/qquickaccessibleattached_p.h>
#include <QtQuick/private/qquickitem_p.h>
#include <QtQml/private/qqmldata_p.h>
#include <QtQml/private/qqmlvmemetaobject_p.h>
#include <QSet>
#include <QTimer>
#include <functional>

static_assert(QT_VERSION==QT_VERSION_CHECK(6,8,3),"Revalidate Tooltip accessibility integration before upgrading Qt");

// Qt's accessibility interface reads description through QObject::property.
// Overlay that read without calling setDescription: that setter permanently
// changes implicit Action proxy state. Original getters, writes and bindings
// continue to use the original descriptor and its original meta-object chain.
class TooltipDescriptionMetaObject final : public QQmlInterceptorMetaObject {
public:
    TooltipDescriptionMetaObject(QQuickAccessibleAttached *object,const QQmlPropertyCache::ConstPtr &cache,bool hadInterceptor)
        :QQmlInterceptorMetaObject(object,cache),m_hadInterceptor(hadInterceptor) {
        // The parent is also an interceptor when it owns an existing Behavior.
        // Keep its property-write dispatch in QQmlInterceptorMetaObject::intercepts.
        if(parent.isT1() && hadInterceptor)parent.setFlagValue(true);
    }
    QPointer<TooltipAccess> owner;
    int metaCall(QObject *object,QMetaObject::Call call,int id,void **arguments) override {
        static const int description=QQuickAccessibleAttached::staticMetaObject.indexOfProperty("description");
        if(call==QMetaObject::ReadProperty && id==description && owner) {
            *static_cast<QString*>(arguments[0])=owner->text();return -1;
        }
        if(intercept(call,id,arguments))return -1;
        if(parent.isT1())return parent.asT1()->metaCall(object,call,id,arguments);
        return object->qt_metacall(call,id,arguments);
    }
    void objectDestroyed(QObject *object) override {
        // QObject owns this layer. Preserve destruction of an earlier dynamic
        // meta-object too; the base interceptor destructor does not own it.
        if(parent.isT1()) {
            auto previous=parent.asT1();QObjectPrivate::get(object)->metaObject=previous;
            if(auto data=QQmlData::get(object))data->hasInterceptorMetaObject=m_hadInterceptor;
            previous->objectDestroyed(object);
        }
        delete this;
    }
private:
    bool m_hadInterceptor;
};

static QHash<QQuickAccessibleAttached*,TooltipAccess*> &owners() {
    static QHash<QQuickAccessibleAttached*,TooltipAccess*> value;return value;
}
static QHash<QQuickAccessibleAttached*,TooltipDescriptionMetaObject*> &overlays() {
    static QHash<QQuickAccessibleAttached*,TooltipDescriptionMetaObject*> value;return value;
}
static TooltipDescriptionMetaObject *descriptionOverlay(QQuickAccessibleAttached *attached) {
    if(auto existing=overlays().value(attached))return existing;
    const auto cache=QQmlData::ensurePropertyCache(attached);
    auto data=QQmlData::get(attached);
    // Accessible is a C++ attached object, not a QML component with VME fields.
    // Stacking an interceptor on a VME would invalidate Qt's typed VME lookup.
    if(data->hasVMEMetaObject)qFatal("Tooltip Accessible descriptor unexpectedly contains QML VME fields");
    auto overlay=new TooltipDescriptionMetaObject(attached,cache,data->hasInterceptorMetaObject);
    overlays().insert(attached,overlay);
    QObject::connect(attached,&QObject::destroyed,[attached]{overlays().remove(attached);owners().remove(attached);});
    return overlay;
}
static void descriptionChanged(QQuickAccessibleAttached *attached) {
    const QPointer<QQuickAccessibleAttached> guard(attached);
    const QPointer<QObject> parent(attached->parent());
    emit attached->descriptionChanged();
    if(guard && parent){QAccessibleEvent event(parent,QAccessible::DescriptionChanged);QAccessible::updateAccessibility(&event);}
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
    if(text==m_text)return;m_text=text;
    const QPointer<TooltipAccess> guard(this);
    const auto keys=m_nodes.keys();
    for(auto key:keys){const auto node=m_nodes.value(key);if(node.object)descriptionChanged(node.object);if(!guard)return;}
    emit textChanged();
}
void TooltipAccess::scheduleRefresh() {
    if(m_queued)return;m_queued=true;
    QTimer::singleShot(0,this,[this]{m_queued=false;refresh();});
}
void TooltipAccess::release(QQuickAccessibleAttached *key) {
    auto found=m_nodes.find(key);if(found==m_nodes.end())return;
    const auto node=found.value();m_nodes.erase(found);
    disconnect(node.destroyed);owners().remove(key);
    if(node.object){node.overlay->owner=nullptr;descriptionChanged(node.object);}
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
        Node node;node.object=attached;node.overlay=descriptionOverlay(attached);node.overlay->owner=this;
        node.destroyed=connect(attached,&QObject::destroyed,this,[this,attached]{m_nodes.remove(attached);});
        m_nodes.insert(attached,node);descriptionChanged(attached);
    }
}

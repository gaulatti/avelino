#include "tooltipaccess.h"
#include <QtQuick/private/qquickaccessibleattached_p.h>
#include <QtQuick/private/qquickitem_p.h>
#include <QtQuick/private/qquicktext_p.h>
#include <QtQuick/private/qquicktextinput_p.h>
#include <QtQuick/private/qquicktextedit_p.h>
#include <QtQml/private/qqmldata_p.h>
#include <QtQml/private/qqmlengine_p.h>
#include <QtQml/private/qv4executablecompilationunit_p.h>
#include <QtQml/private/qqmlvmemetaobject_p.h>
#include <QSet>
#include <QTimer>
#include <functional>

static_assert(QT_VERSION==QT_VERSION_CHECK(6,8,3),"Revalidate Tooltip accessibility integration before upgrading Qt");

// Qt's accessibility interface reads description through QObject::property.
// Overlay that read without calling setDescription: that setter permanently
// changes implicit Action proxy state. Original getters, writes and bindings
// continue to use the original descriptor and its original meta-object chain.
class TooltipDescriptionMetaObject final : public QQmlVMEMetaObject {
public:
    TooltipDescriptionMetaObject(QV4::ExecutionEngine *engine,QQuickAccessibleAttached *object,
                                 const QQmlPropertyCache::ConstPtr &cache)
        :QQmlVMEMetaObject(engine,object,cache,{},-1) {}
    QPointer<TooltipAccess> owner;
    int metaCall(QObject *object,QMetaObject::Call call,int id,void **arguments) override {
        static const int description=QQuickAccessibleAttached::staticMetaObject.indexOfProperty("description");
        if(call==QMetaObject::ReadProperty && id==description && owner) {
            *static_cast<QString*>(arguments[0])=owner->text();return -1;
        }
        return QQmlVMEMetaObject::metaCall(object,call,id,arguments);
    }
};

static QHash<QQuickAccessibleAttached*,TooltipAccess*> &owners() {
    static QHash<QQuickAccessibleAttached*,TooltipAccess*> value;return value;
}
static QHash<QQuickAccessibleAttached*,TooltipDescriptionMetaObject*> &overlays() {
    static QHash<QQuickAccessibleAttached*,TooltipDescriptionMetaObject*> value;return value;
}
static TooltipDescriptionMetaObject *descriptionOverlay(QQuickAccessibleAttached *attached,TooltipAccess *owner) {
    if(auto existing=overlays().value(attached))return existing;
    // An empty VME layer gives Qt's typed VME lookups a valid top-level object.
    // Its offsets follow all original properties/methods, so existing fields,
    // aliases, Behaviors and destruction stay with the original parent layer.
    const auto cache=QQmlData::ensurePropertyCache(attached)->copy();
    auto engine=qmlEngine(owner);
    if(!engine)qFatal("Tooltip accessibility requires its owning QML engine");
    auto overlay=new TooltipDescriptionMetaObject(QQmlEnginePrivate::get(engine)->v4engine(),attached,cache);
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
        // Qt's accessibility interface handles these native text classes even
        // when effectiveAccessibleRole() is NoRole (qaccessiblequickitem.cpp).
        const bool nativeText=qobject_cast<QQuickText*>(item) || qobject_cast<QQuickTextInput*>(item) || qobject_cast<QQuickTextEdit*>(item);
        auto attached=QQuickAccessibleAttached::attachedProperties(item);
        if(!attached && (role!=QAccessible::NoRole || nativeText))
            attached=qobject_cast<QQuickAccessibleAttached*>(qmlAttachedPropertiesObject<QQuickAccessibleAttached>(item,true));
        if(attached) {
            m_structure.append(connect(attached,&QQuickAccessibleAttached::roleChanged,this,&TooltipAccess::scheduleRefresh));
            m_structure.append(connect(attached,&QQuickAccessibleAttached::ignoredChanged,this,&TooltipAccess::scheduleRefresh));
            if(!attached->ignored() && (role!=QAccessible::NoRole || nativeText))present.insert(attached);
        }
        for(auto child:item->childItems())walk(child);
    };
    if(m_target)walk(m_target);
    const auto previous=m_nodes.keys();for(auto key:previous)if(!present.contains(key))release(key);
    for(auto attached:present) {
        if(m_nodes.contains(attached))continue;
        if(owners().contains(attached))qFatal("A Tooltip accessible target cannot have multiple help owners");
        owners().insert(attached,this);
        Node node;node.object=attached;node.overlay=descriptionOverlay(attached,this);node.overlay->owner=this;
        node.destroyed=connect(attached,&QObject::destroyed,this,[this,attached]{m_nodes.remove(attached);});
        m_nodes.insert(attached,node);descriptionChanged(attached);
    }
}

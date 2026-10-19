#include "herocarouselbase.h"
#include "proposalrow.h"
#include "selectionidentity.h"
#include <QQuickWindow>
#include <QSet>
#include <QtQuick/private/qquickitem_p.h>
#include <algorithm>
#include <cmath>
#include <limits>

static_assert(QT_VERSION==QT_VERSION_CHECK(6,8,3),"Revalidate the retained slide integration before upgrading Qt");
namespace {
class HeroCell : public QQuickItem {
public:
    using QQuickItem::QQuickItem;
    QPointer<QQuickItem> caller;
    QPointer<QQmlContext> context;
    ~HeroCell()override{delete caller;delete context;}
};
}
HeroCarouselBase::Entry::~Entry(){if(cell)cell->deleteLater();}
HeroCarouselBase::HeroCarouselBase(QQuickItem *parent):QQuickItem(parent){
    connect(this,&QQuickItem::windowChanged,this,&HeroCarouselBase::attachWindow);
    connect(this,&QQuickItem::visibleChanged,this,[this]{polish();});
}
HeroCarouselBase::~HeroCarouselBase(){
    for(const auto connection:m_windowConnections)disconnect(connection);
    disconnect(this,nullptr,this,nullptr);
    for(auto sender:findChildren<QObject*>())disconnect(sender,nullptr,this,nullptr);
    m_entries.clear();m_retired.clear();
}
void HeroCarouselBase::componentComplete(){QQuickItem::componentComplete();m_complete=true;attachWindow(window());layout();}
void HeroCarouselBase::geometryChange(const QRectF &next,const QRectF &previous){
    QQuickItem::geometryChange(next,previous);if(!m_layingOut)polish();
}
void HeroCarouselBase::setItems(const QJSValue &value){
    if(!value.isArray()&&value.toVariant().metaType()!=QMetaType::fromType<QVariantList>())qFatal("HeroCarousel items must be an array");
    m_items=value;m_initialized=true;m_dirty=true;polish();emit itemsChanged();
}
void HeroCarouselBase::setItemIdentity(const QJSValue &value){
    if(!value.isUndefined()&&!value.isNull()&&!value.isCallable())qFatal("HeroCarousel itemIdentity must be a function or null");
    m_identity=value;m_dirty=true;polish();emit itemsChanged();
}
void HeroCarouselBase::setSlide(QQmlComponent *value){
    if(value==m_slide)return;
    auto previous=m_entries;previous.append(m_retired.values());m_slide=value;m_entries.clear();m_retired.clear();m_dirty=true;polish();
    QPointer<HeroCarouselBase> guard(this);
    for(const auto &entry:previous){setActive(entry,false);if(!guard)return;}
    emit slideChanged();
}
void HeroCarouselBase::setViewport(QQuickItem *value){
    if(value==m_viewportItem)return;m_viewportItem=value;polish();emit viewportChanged();
}
void HeroCarouselBase::setMirrored(bool value){if(value==m_mirrored)return;m_mirrored=value;polish();emit configurationChanged();}
void HeroCarouselBase::reconcile(){
    m_dirty=false;if(!m_initialized)return;
    QPointer<HeroCarouselBase> guard(this);const auto values=m_items,identity=m_identity;
    const auto previousCount=m_entries.size();const auto length=values.property("length").toUInt();
    if(length>unsigned(std::numeric_limits<int>::max()))qFatal("HeroCarousel item count exceeds Qt's index range");
    auto previous=m_retired;for(const auto &entry:m_entries)previous.insert(entry->key,entry);
    QList<EntryPtr> next;QSet<QString> used;
    for(unsigned index=0;index<length;++index){
        const auto data=values.property(index);
        if((identity.isNull()||identity.isUndefined())&&(!data.isObject()||data.isNull()||data.isArray()||!data.hasProperty("id")))qFatal("HeroCarousel items require an id or an itemIdentity function");
        const auto key=SelectionIdentity::key(identity.isCallable()?data:data.property("id"),identity,"HeroCarousel");if(!guard)return;
        if(used.contains(key))qFatal("HeroCarousel item identifiers must be unique");used.insert(key);
        auto entry=previous.take(key);if(!entry){entry=std::make_shared<Entry>();entry->key=key;}
        entry->data=data;next.append(entry);
    }
    for(const auto &entry:previous){setActive(entry,false);if(!guard)return;}
    // The pinned lazy horizontal stack preserves caller state when identifiers
    // disappear and later return, including after an empty-data idle period.
    m_entries=std::move(next);m_retired=std::move(previous);
    for(int index=0;index<m_entries.size();++index){const auto entry=m_entries[index];updateRoles(entry,index);if(!guard)return;}
    if(previousCount!=m_entries.size())emit itemCountChanged();
}
void HeroCarouselBase::updateRoles(const EntryPtr &entry,int index){
    if(!entry->roles)return;
    QPointer<HeroCarouselBase> guard(this);
    entry->roles->data=entry->data;entry->roles->index=index;emit entry->roles->dataChanged();if(!guard)return;
    if(entry->item&&entry->item->metaObject()->indexOfProperty("slideData")>=0)entry->item->setProperty("slideData",QVariant::fromValue(entry->data));
    if(!guard)return;
    if(entry->item&&entry->item->metaObject()->indexOfProperty("slideIndex")>=0)entry->item->setProperty("slideIndex",index);
}
void HeroCarouselBase::instantiate(const EntryPtr &entry,int index){
    if(entry->item)return;
    const QPointer<QQmlComponent> factory=m_slide;
    if(!factory||factory->status()!=QQmlComponent::Ready)qFatal("HeroCarousel slide must be a ready Component");
    auto context=factory->creationContext();if(!context)context=qmlContext(this);
    if(entry->cell)entry->cell->deleteLater();
    auto cell=new HeroCell(this);cell->setVisible(false);entry->cell=cell;cell->setSize(m_viewportItem->size());
    entry->context=new QQmlContext(context);cell->context=entry->context;entry->roles=new HeroSlideContext(entry->context);
    entry->context->setContextObject(entry->roles);entry->roles->data=entry->data;entry->roles->index=index;
    QPointer<HeroCarouselBase> guard(this);
    QObject *object=factory->beginCreate(entry->context);auto item=qobject_cast<QQuickItem*>(object);
    if(!item){if(factory)factory->completeCreate();delete object;qFatal("HeroCarousel slide must create an Item");}
    if(!guard){if(factory)factory->completeCreate();delete object;return;}
    entry->item=item;cell->caller=item;item->setParent(cell);item->setParentItem(cell);
    QVariantMap roles;
    for(const auto &name:QList<QByteArray>{"slideData","slideIndex","slideActive"})if(item->metaObject()->indexOfProperty(name)>=0)
        roles.insert(QString::fromUtf8(name),name=="slideData"?QVariant::fromValue(entry->data):name=="slideIndex"?QVariant(index):QVariant(false));
    factory->setInitialProperties(item,roles);if(!guard||!entry->item){if(factory)factory->completeCreate();return;}factory->completeCreate();
    if(!guard||!entry->item)return;
    if(factory&&factory->isError())qFatal("HeroCarousel slide creation failed: %s",qPrintable(factory->errorString()));
    entry->explicitWidth=QQuickItemPrivate::get(item)->widthValid();entry->explicitHeight=QQuickItemPrivate::get(item)->heightValid();
    auto changed=[this]{if(!m_layingOut)polish();};
    connect(item,&QQuickItem::implicitWidthChanged,this,changed);connect(item,&QQuickItem::implicitHeightChanged,this,changed);
    connect(item,&QQuickItem::widthChanged,this,changed);connect(item,&QQuickItem::heightChanged,this,changed);
    auto hint=qobject_cast<BleeckerLayout*>(qmlAttachedPropertiesObject<BleeckerLayout>(item,true));connect(hint,&BleeckerLayout::metricsChanged,this,changed);
}
void HeroCarouselBase::setActive(const EntryPtr &entry,bool value){
    if(!entry->roles||entry->roles->active==value)return;
    QPointer<HeroCarouselBase> guard(this);entry->roles->active=value;
    if(entry->item&&entry->item->metaObject()->indexOfProperty("slideActive")>=0)entry->item->setProperty("slideActive",value);
    if(!guard||!entry->roles)return;
    emit entry->roles->activeChanged();if(guard&&entry->cell)entry->cell->setVisible(value);
}
void HeroCarouselBase::measure(const EntryPtr &entry,qreal offered){
    QPointer<HeroCarouselBase> guard(this);const QPointer<QQuickItem> item=entry->item;
    entry->cell->setWidth(offered);if(!guard||!item)return;
    entry->cell->setHeight(m_viewportItem->height());if(!guard||!item)return;
    auto hint=qobject_cast<BleeckerLayout*>(qmlAttachedPropertiesObject<BleeckerLayout>(item,true));
    hint->propose(offered);if(!guard||!item)return;
    const auto ideal=hint->idealWidth>=0?hint->idealWidth:entry->explicitWidth?item->width():item->implicitWidth();
    const auto minimum=hint->minimumWidth>=0?hint->minimumWidth:entry->explicitWidth?ideal:0;
    if(!std::isfinite(ideal)||!std::isfinite(minimum)||ideal<0||minimum<0||minimum>ideal)qFatal("HeroCarousel slide requires finite widths with 0 <= minimum <= ideal");
    if(hint->fillsWidth)item->setWidth(std::max(minimum,offered));else if(!entry->explicitWidth)item->setWidth(std::clamp(offered,minimum,ideal));
    if(!guard||!item)return;
    const auto height=entry->explicitHeight?item->height():item->implicitHeight();
    if(!std::isfinite(height)||height<0)qFatal("HeroCarousel slide height must be finite and nonnegative");
    if(!entry->explicitHeight)item->setHeight(height);
    if(!guard||!item)return;
    entry->measuredWidth=item->width();entry->measuredHeight=height;
}
QRectF HeroCarouselBase::visibleRect()const{
    if(!window()||!window()->isVisible()||!isVisible()||!m_viewportItem)return {};
    QRectF result=mapRectFromItem(window()->contentItem(),QRectF(0,0,window()->width(),window()->height()));
    for(auto ancestor=parentItem();ancestor;ancestor=ancestor->parentItem())if(ancestor->clip())result=result.intersected(mapRectFromItem(ancestor,QRectF(0,0,ancestor->width(),ancestor->height())));
    return result;
}
void HeroCarouselBase::attachWindow(QQuickWindow *window){
    for(const auto connection:m_windowConnections)disconnect(connection);m_windowConnections.clear();
    if(window)m_windowConnections={connect(window,&QQuickWindow::afterAnimating,this,&HeroCarouselBase::refreshViewport),connect(window,&QWindow::visibleChanged,this,[this]{polish();})};
    polish();
}
void HeroCarouselBase::refreshViewport(){
    const auto next=visibleRect();const auto origin=mapToScene(QPointF());const auto dpr=window()?window()->devicePixelRatio():1;
    if(next==m_visibleRect&&origin==m_sceneOrigin&&dpr==m_devicePixelRatio)return;
    m_visibleRect=next;m_sceneOrigin=origin;m_devicePixelRatio=dpr;polish();
}
int HeroCarouselBase::instantiatedCount()const{int count=0;for(const auto &entry:m_entries)count+=!entry->item.isNull();return count;}
int HeroCarouselBase::activeCount()const{int count=0;for(const auto &entry:m_entries)count+=entry->roles&&entry->roles->active;return count;}
QQuickItem *HeroCarouselBase::itemAt(int index)const{return index>=0&&index<m_entries.size()?m_entries[index]->item.data():nullptr;}
void HeroCarouselBase::layout(){
    if(!m_complete||m_layingOut)return;m_layingOut=true;QPointer<HeroCarouselBase> guard(this);
    if(m_dirty){reconcile();if(!guard)return;}
    if(!m_viewportItem)qFatal("HeroCarousel requires its scrolling viewport");
    const auto offered=m_viewportItem->width();
    if(!std::isfinite(offered)||offered<0)qFatal("HeroCarousel viewport width must be finite and nonnegative");
    m_documentWidth=m_entries.isEmpty()?0:m_entries.size()*offered+16*std::max(qsizetype(0),m_entries.size()-1);
    m_visibleRect=visibleRect();const auto previousViewport=m_visibleRect;const auto previousSize=m_viewportItem->size();
    const bool explicitHeight=QQuickItemPrivate::get(m_viewportItem)->heightValid();
    if(offered>0&&window()&&window()->isVisible()&&isVisible()&&(!explicitHeight||m_viewportItem->height()>0)){
        const auto dpr=window()->devicePixelRatio();
        for(int index=0;index<m_entries.size();++index){
            const auto entry=m_entries[index];const auto x=m_mirrored?m_documentWidth-offered-index*(offered+16):index*(offered+16);
            const bool active=!m_visibleRect.isEmpty()&&x<m_visibleRect.right()&&x+offered>m_visibleRect.left();
            if(active||(!explicitHeight&&index==0)){instantiate(entry,index);if(!guard)return;}
            if(entry->item){
                measure(entry,offered);if(!guard)return;
                if(entry->item){
                    // Native lazy-stack allocations align their scene origin to
                    // a device pixel before centering the caller within them.
                    // Caller sizes and centering offsets remain fractional.
                    const auto scene=mapToScene(QPointF(x,0));
                    const auto aligned=QPointF(std::floor(scene.x()*dpr+0.5)/dpr,std::floor(scene.y()*dpr+0.5)/dpr);
                    entry->cell->setPosition(mapFromScene(aligned));
                    if(!guard||!entry->item)return;
                    entry->item->setPosition(QPointF((offered-entry->measuredWidth)/2,(m_viewportItem->height()-entry->measuredHeight)/2));if(!guard)return;
                }
            }
            setActive(entry,active);if(!guard)return;
        }
    }else for(const auto &entry:m_entries){setActive(entry,false);if(!guard)return;}
    // Native height fitting continues to use the logical first slide's
    // height even after a taller later slide has appeared and disappeared.
    m_naturalHeight=!m_entries.isEmpty()&&m_entries.first()->item?m_entries.first()->measuredHeight:0;
    setImplicitSize(m_documentWidth,m_naturalHeight);if(!guard)return;
    const bool geometryChanged=previousViewport!=visibleRect()||previousSize!=m_viewportItem->size();
    m_layingOut=false;emit metricsChanged();if(guard&&(m_dirty||geometryChanged))polish();
}
QVariantMap HeroCarouselBase::layoutSnapshot()const{
    QVariantList entries;
    for(int index=0;index<m_entries.size();++index){
        const auto &entry=m_entries[index];QVariantMap row{{"index",index},{"key",entry->key},{"created",!entry->item.isNull()},{"active",entry->roles&&entry->roles->active}};
        if(entry->item)row.insert("frame",QVariantMap{{"x",entry->cell->x()+entry->item->x()},{"y",entry->cell->y()+entry->item->y()},{"width",entry->item->width()},{"height",entry->item->height()}});
        entries.append(row);
    }
    return {{"documentWidth",m_documentWidth},{"naturalHeight",m_naturalHeight},{"entries",entries},{"retiredIdentities",m_retired.size()},{"nativeSizingHistories","pending"},{"nativeLazyTiming","pending"},{"nativeGestureLimit","pending"}};
}

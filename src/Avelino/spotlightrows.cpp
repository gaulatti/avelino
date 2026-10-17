#include "spotlightrows.h"
#include "proposalrow.h"
#include "selectionidentity.h"
#include <QQuickWindow>
#include <QSet>
#include <QtQuick/private/qquickitem_p.h>
#include <algorithm>
#include <cmath>
#include <limits>

namespace {
class SpotlightCell : public QQuickItem {
public:
    using QQuickItem::QQuickItem;
    QPointer<QQuickItem> caller;
    QPointer<QQmlContext> context;
    ~SpotlightCell() override{delete caller;delete context;}
};
}
SpotlightRows::Entry::~Entry(){if(cell)cell->deleteLater();}
SpotlightRows::SpotlightRows(QQuickItem *parent):QQuickItem(parent) {
    connect(this,&QQuickItem::windowChanged,this,&SpotlightRows::attachWindow);
    connect(this,&QQuickItem::visibleChanged,this,[this]{polish();});
    setImplicitHeight(12);
}
SpotlightRows::~SpotlightRows(){disconnect(m_frame);m_entries.clear();m_retired.clear();}
void SpotlightRows::componentComplete(){QQuickItem::componentComplete();m_complete=true;attachWindow(window());reconcile();emit itemsChanged();layout();}
void SpotlightRows::geometryChange(const QRectF &next,const QRectF &previous){QQuickItem::geometryChange(next,previous);if(!m_layingOut)polish();}
void SpotlightRows::setItems(const QJSValue &value) {
    if(!value.isArray()&&value.toVariant().metaType()!=QMetaType::fromType<QVariantList>())qFatal("CommandSpotlight items must be an array");
    m_items=value;m_initialized=true;if(m_complete)reconcile();emit itemsChanged();polish();
}
void SpotlightRows::setItemIdentity(const QJSValue &value) {
    if(!value.isUndefined()&&!value.isNull()&&!value.isCallable())qFatal("CommandSpotlight itemIdentity must be a function or null");
    m_identity=value;if(m_complete)reconcile();emit itemsChanged();polish();
}
void SpotlightRows::setRow(QQmlComponent *value) {
    if(value==m_row)return;
    for(const auto &entry:m_entries)setActive(entry,false);
    m_entries.clear();m_retired.clear();m_row=value;
    if(m_complete)reconcile();emit itemsChanged();emit rowChanged();polish();
}
void SpotlightRows::setMirrored(bool value){if(value==m_mirrored)return;m_mirrored=value;emit presentationChanged();polish();}
void SpotlightRows::setRowFont(const QFont &value){if(value==m_font)return;m_font=value;emit presentationChanged();polish();}
void SpotlightRows::setRowForeground(const QColor &value){if(value==m_foreground)return;m_foreground=value;emit presentationChanged();polish();}
void SpotlightRows::reconcile() {
    if(!m_initialized)return;
    const auto length=m_items.property("length").toUInt();
    if(length>unsigned(std::numeric_limits<int>::max()))qFatal("CommandSpotlight item count exceeds Qt's index range");
    QHash<QString,EntryPtr> previous;for(const auto &entry:m_entries)previous.insert(entry->key,entry);
    QList<EntryPtr> next;QSet<QString> used;
    for(unsigned index=0;index<length;++index) {
        const auto data=m_items.property(index);
        if((m_identity.isNull()||m_identity.isUndefined())&&(!data.isObject()||data.isNull()||data.isArray()||!data.hasProperty("id")))
            qFatal("CommandSpotlight items require an id or itemIdentity function");
        const auto key=SelectionIdentity::key(m_identity.isCallable()?data:data.property("id"),m_identity,"CommandSpotlight");
        if(used.contains(key))qFatal("CommandSpotlight item identifiers must be unique");used.insert(key);
        auto entry=previous.take(key);if(!entry)entry=m_retired.take(key);
        if(!entry){entry=std::make_shared<Entry>();entry->key=key;}
        if(entry->roles&&entry->roles->index!=int(index)&&entry->item&&window()) {
            auto grabbed=window()->mouseGrabberItem();
            if(grabbed&&(grabbed==entry->item||entry->item->isAncestorOf(grabbed)))grabbed->ungrabMouse();
        }
        entry->data=data;next.append(entry);updateRoles(entry,int(index));
    }
    // The recorded native sequences retain removed offscreen state and recreate
    // visible state. Broader eviction and memory-pressure behavior are pending.
    for(const auto &entry:previous) {
        const bool retain=entry->item&&entry->roles&&!entry->roles->active;
        setActive(entry,false);
        if(retain)m_retired.insert(entry->key,entry);
    }
    m_entries=std::move(next);
}
void SpotlightRows::updateRoles(const EntryPtr &entry,int index) {
    if(!entry->roles)return;
    entry->roles->data=entry->data;entry->roles->index=index;emit entry->roles->dataChanged();
    if(entry->roles->font!=m_font||entry->roles->foreground!=m_foreground) {
        entry->roles->font=m_font;entry->roles->foreground=m_foreground;emit entry->roles->presentationChanged();
    }
    if(entry->item)for(const auto &name:QList<QByteArray>{"rowData","rowIndex"})
        if(entry->item->metaObject()->indexOfProperty(name)>=0)entry->item->setProperty(name,name=="rowData"?QVariant::fromValue(entry->data):QVariant(index));
}
void SpotlightRows::instantiate(const EntryPtr &entry,int index) {
    if(entry->item)return;
    if(!m_row||m_row->status()!=QQmlComponent::Ready)qFatal("CommandSpotlight row must be a ready Component");
    auto creation=m_row->creationContext();if(!creation)creation=qmlContext(this);
    auto cell=new SpotlightCell(this);cell->setVisible(false);entry->cell=cell;
    entry->context=new QQmlContext(creation);cell->context=entry->context;entry->roles=new SpotlightRowContext(entry->context);
    entry->context->setContextObject(entry->roles);entry->roles->data=entry->data;entry->roles->index=index;
    entry->roles->font=m_font;entry->roles->foreground=m_foreground;
    auto object=m_row->beginCreate(entry->context);auto item=qobject_cast<QQuickItem*>(object);
    if(!item){m_row->completeCreate();delete object;qFatal("CommandSpotlight row must create an Item");}
    entry->item=item;cell->caller=item;item->setParent(cell);item->setParentItem(cell);
    QVariantMap roles;
    for(const auto &name:QList<QByteArray>{"rowData","rowIndex","rowActive"})if(item->metaObject()->indexOfProperty(name)>=0)
        roles.insert(QString::fromUtf8(name),name=="rowData"?QVariant::fromValue(entry->data):name=="rowIndex"?QVariant(index):QVariant(false));
    m_row->setInitialProperties(item,roles);m_row->completeCreate();
    if(m_row->isError())qFatal("CommandSpotlight row creation failed: %s",qPrintable(m_row->errorString()));
    entry->explicitWidth=QQuickItemPrivate::get(item)->widthValid();entry->explicitHeight=QQuickItemPrivate::get(item)->heightValid();
    auto changed=[this]{if(!m_layingOut)polish();};
    connect(item,&QQuickItem::implicitWidthChanged,this,changed);connect(item,&QQuickItem::implicitHeightChanged,this,changed);
    connect(item,&QQuickItem::widthChanged,this,changed);connect(item,&QQuickItem::heightChanged,this,changed);
    auto hint=qobject_cast<BleeckerLayout*>(qmlAttachedPropertiesObject<BleeckerLayout>(item,true));
    connect(hint,&BleeckerLayout::metricsChanged,this,changed);
}
void SpotlightRows::setActive(const EntryPtr &entry,bool active) {
    if(!entry->roles||entry->roles->active==active)return;
    entry->roles->active=active;
    if(entry->item&&entry->item->metaObject()->indexOfProperty("rowActive")>=0)entry->item->setProperty("rowActive",active);
    emit entry->roles->activeChanged();entry->cell->setVisible(active);
}
void SpotlightRows::measure(const EntryPtr &entry) {
    auto item=entry->item.data();auto hint=qobject_cast<BleeckerLayout*>(qmlAttachedPropertiesObject<BleeckerLayout>(item,true));
    const auto offered=std::max(qreal(0),width()-24);hint->propose(offered);
    const auto ideal=hint->idealWidth>=0?hint->idealWidth:entry->explicitWidth?item->width():item->implicitWidth();
    const auto minimum=hint->minimumWidth>=0?hint->minimumWidth:entry->explicitWidth?ideal:0;
    if(!std::isfinite(ideal)||!std::isfinite(minimum)||minimum<0||ideal<minimum)qFatal("CommandSpotlight row requires finite widths with 0 <= minimum <= ideal");
    if(hint->fillsWidth)item->setWidth(std::max(minimum,offered));
    else if(!entry->explicitWidth)item->setWidth(std::clamp(offered,minimum,ideal));
    const auto height=entry->explicitHeight?item->height():item->implicitHeight();
    if(!std::isfinite(height)||height<0)qFatal("CommandSpotlight row height must be finite and nonnegative");
    if(!entry->explicitHeight)item->setHeight(height);
    entry->measuredWidth=item->width();entry->measuredHeight=height;
}
QRectF SpotlightRows::visibleRect() const {
    if(!window()||!isVisible())return {};
    QRectF result=mapRectFromItem(window()->contentItem(),QRectF(0,0,window()->width(),window()->height()));
    for(auto ancestor=parentItem();ancestor;ancestor=ancestor->parentItem())if(ancestor->clip())
        result=result.intersected(mapRectFromItem(ancestor,QRectF(0,0,ancestor->width(),ancestor->height())));
    return result;
}
void SpotlightRows::attachWindow(QQuickWindow *window) {
    disconnect(m_frame);if(window)m_frame=connect(window,&QQuickWindow::afterAnimating,this,&SpotlightRows::refreshViewport);polish();
}
void SpotlightRows::refreshViewport(){auto rect=visibleRect();if(rect==m_viewport)return;m_viewport=rect;polish();}
int SpotlightRows::instantiatedCount() const{int count=0;for(const auto &e:m_entries)count+=!e->item.isNull();return count;}
int SpotlightRows::activeCount() const{int count=0;for(const auto &e:m_entries)count+=e->roles&&e->roles->active;return count;}
QQuickItem *SpotlightRows::itemAt(int index) const{return index>=0&&index<m_entries.size()?m_entries[index]->item.data():nullptr;}
QQuickItem *SpotlightRows::cellAt(int index) const{return index>=0&&index<m_entries.size()?m_entries[index]->cell.data():nullptr;}
void SpotlightRows::layout() {
    if(!m_complete||m_layingOut)return;m_layingOut=true;
    if(!std::isfinite(width())||width()<0)qFatal("CommandSpotlight row width must be finite and nonnegative");
    const auto viewport=visibleRect();m_viewport=viewport;
    QList<qreal> heights;for(int index=0;index<m_entries.size();++index) {
        const auto &entry=m_entries[index];updateRoles(entry,index);
        if(entry->item)measure(entry);
        heights.append(entry->item?std::max(qreal(38),entry->measuredHeight):m_estimate);
    }
    qreal y=6;bool learned=false;
    for(int index=0;index<m_entries.size();++index) {
        const auto &entry=m_entries[index];
        const bool active=!viewport.isEmpty()&&y<viewport.bottom()&&y+heights[index]>viewport.top();
        if(active&&!entry->item){instantiate(entry,index);measure(entry);heights[index]=std::max(qreal(38),entry->measuredHeight);learned=true;}
        if(entry->item) {
            const auto width=entry->measuredWidth+24;
            entry->cell->setSize(QSizeF(width,heights[index]));
            entry->cell->setPosition(QPointF(m_mirrored?this->width()-width:0,y));
            entry->item->setPosition(QPointF(12,(heights[index]-entry->measuredHeight)/2));
            setActive(entry,active);
        }
        y+=heights[index]+2;
    }
    if(learned) {
        qreal sum=0;int count=0;
        for(int index=0;index<m_entries.size();++index)if(m_entries[index]->item){sum+=heights[index];++count;}
        if(count)m_estimate=sum/count;
    }
    const auto next=m_entries.isEmpty()?qreal(12):y+4;
    if(next!=m_contentHeight){m_contentHeight=next;setImplicitHeight(next);}
    emit metricsChanged();m_layingOut=false;if(learned)polish();
}
QVariantMap SpotlightRows::layoutSnapshot() const {
    QVariantList rows;
    for(int index=0;index<m_entries.size();++index) {
        const auto &entry=m_entries[index];QVariantMap value{{"index",index},{"key",entry->key},{"created",!entry->item.isNull()},{"active",entry->roles&&entry->roles->active}};
        if(entry->item)value.insert("frame",QVariantMap{{"x",entry->cell->x()},{"y",entry->cell->y()},{"width",entry->cell->width()},{"height",entry->cell->height()}});
        rows.append(value);
    }
    return {{"entries",rows},{"contentHeight",m_contentHeight},{"created",instantiatedCount()},{"active",activeCount()},{"retired",cachedCount()},
        {"nativeLazyMeasurementAcceptance","pending"},{"nativeEvictionAcceptance","pending"}};
}

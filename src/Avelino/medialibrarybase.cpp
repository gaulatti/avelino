#include "medialibrarybase.h"
#include "proposalrow.h"
#include "selectionidentity.h"
#include <QQuickWindow>
#include <QSet>
#include <QtQuick/private/qquickitem_p.h>
#include <algorithm>
#include <cmath>
#include <limits>

namespace {
// The context must outlive its caller, including when an action removes the
// tile during signal delivery. Defer the owner as one unit.
class MediaCell : public QQuickItem {
public:
    using QQuickItem::QQuickItem;
    QPointer<QQuickItem> caller;
    QPointer<QQmlContext> context;
    ~MediaCell() override {delete caller;delete context;}
};
}
MediaLibraryBase::Entry::~Entry(){if(cell)cell->deleteLater();}
MediaLibraryBase::MediaLibraryBase(QQuickItem *parent):QQuickItem(parent) {
    connect(this,&QQuickItem::windowChanged,this,&MediaLibraryBase::attachWindow);
    connect(this,&QQuickItem::visibleChanged,this,[this]{polish();});
}
MediaLibraryBase::~MediaLibraryBase(){
    disconnect(m_frameConnection);
    // QQuickItem emits window/geometry changes during its base destructor.
    // Stop callbacks while our derived state and caller contexts still exist.
    disconnect(this,nullptr,this,nullptr);
    for(auto sender:findChildren<QObject*>())disconnect(sender,nullptr,this,nullptr);
    m_entries.clear();
}
void MediaLibraryBase::componentComplete(){QQuickItem::componentComplete();m_complete=true;attachWindow(window());reconcile();layout();}
void MediaLibraryBase::geometryChange(const QRectF &next,const QRectF &previous) {
    QQuickItem::geometryChange(next,previous);if(!m_layingOut)polish();
}
void MediaLibraryBase::setItems(const QJSValue &value) {
    if(!value.isArray() &&value.toVariant().metaType()!=QMetaType::fromType<QVariantList>())qFatal("MediaLibrary items must be an array");
    m_initialized=true;m_items=value;if(m_complete)reconcile();emit itemsChanged();polish();
}
void MediaLibraryBase::setItemIdentity(const QJSValue &value) {
    if(!value.isUndefined()&&!value.isNull()&&!value.isCallable())qFatal("MediaLibrary itemIdentity must be a function or null");
    m_identity=value;if(m_complete)reconcile();emit itemsChanged();polish();
}
void MediaLibraryBase::setTile(QQmlComponent *value) {
    if(value==m_tile)return;
    for(const auto &entry:m_entries)setActive(entry,false);
    m_entries.clear();m_tile=value;if(m_complete)reconcile();emit tileChanged();polish();
}
void MediaLibraryBase::setMinimumTileWidth(qreal value) {
    if(value==m_minimum || (std::isnan(value)&&std::isnan(m_minimum)))return;
    m_minimum=value;emit configurationChanged();polish();
}
void MediaLibraryBase::setMirrored(bool value) {if(value==m_mirrored)return;m_mirrored=value;emit configurationChanged();polish();}
void MediaLibraryBase::reconcile() {
    if(!m_initialized)return;
    const auto length=m_items.property("length").toUInt();
    if(length>unsigned(std::numeric_limits<int>::max()))qFatal("MediaLibrary item count exceeds Qt's index range");
    QHash<QString,EntryPtr> previous;for(const auto &entry:m_entries)previous.insert(entry->key,entry);
    QList<EntryPtr> next;QSet<QString> used;
    for(unsigned index=0;index<length;++index) {
        const auto data=m_items.property(index);
        if((m_identity.isNull()||m_identity.isUndefined()) && (!data.isObject()||data.isNull()||data.isArray()||!data.hasProperty("id")))
            qFatal("MediaLibrary items require an id or an itemIdentity function");
        const auto key=SelectionIdentity::key(m_identity.isCallable() ? data:data.property("id"),m_identity,"MediaLibrary");
        if(used.contains(key))qFatal("MediaLibrary item identifiers must be unique");used.insert(key);
        auto entry=previous.take(key);if(!entry){entry=std::make_shared<Entry>();entry->key=key;}
        entry->data=data;next.append(entry);updateRoles(entry,int(index));
    }
    for(const auto &entry:previous)setActive(entry,false);
    m_entries=std::move(next);
    if(m_entries.isEmpty())m_estimate=40;
}
void MediaLibraryBase::updateRoles(const EntryPtr &entry,int index) {
    if(!entry->roles)return;
    entry->roles->data=entry->data;entry->roles->index=index;emit entry->roles->dataChanged();
    if(entry->item) {
        if(entry->item->metaObject()->indexOfProperty("tileData")>=0)entry->item->setProperty("tileData",QVariant::fromValue(entry->data));
        if(entry->item->metaObject()->indexOfProperty("tileIndex")>=0)entry->item->setProperty("tileIndex",index);
    }
}
void MediaLibraryBase::instantiate(const EntryPtr &entry,int index) {
    if(entry->item)return;
    if(!m_tile || m_tile->status()!=QQmlComponent::Ready)qFatal("MediaLibrary tile must be a ready Component");
    auto context=m_tile->creationContext();if(!context)context=qmlContext(this);
    if(entry->cell)entry->cell->deleteLater();
    auto cell=new MediaCell(this);cell->setVisible(false);entry->cell=cell;
    entry->context=new QQmlContext(context);cell->context=entry->context;entry->roles=new MediaTileContext(entry->context);
    entry->context->setContextObject(entry->roles);entry->roles->data=entry->data;entry->roles->index=index;
    QObject *object=m_tile->beginCreate(entry->context);
    auto item=qobject_cast<QQuickItem*>(object);
    if(!item){m_tile->completeCreate();delete object;qFatal("MediaLibrary tile must create an Item");}
    entry->item=item;cell->caller=item;item->setParent(entry->cell);item->setParentItem(entry->cell);
    QVariantMap roles;
    for(const auto &name:QList<QByteArray>{"tileData","tileIndex","tileActive"})if(item->metaObject()->indexOfProperty(name)>=0)
        roles.insert(QString::fromUtf8(name),name=="tileData" ? QVariant::fromValue(entry->data):name=="tileIndex" ? QVariant(index):QVariant(false));
    m_tile->setInitialProperties(item,roles);m_tile->completeCreate();
    if(m_tile->isError())qFatal("MediaLibrary tile creation failed: %s",qPrintable(m_tile->errorString()));
    entry->explicitWidth=QQuickItemPrivate::get(item)->widthValid();entry->explicitHeight=QQuickItemPrivate::get(item)->heightValid();
    auto changed=[this]{if(!m_layingOut)polish();};
    connect(item,&QQuickItem::implicitWidthChanged,this,changed);connect(item,&QQuickItem::implicitHeightChanged,this,changed);
    connect(item,&QQuickItem::widthChanged,this,changed);connect(item,&QQuickItem::heightChanged,this,changed);
    auto hint=qobject_cast<BleeckerLayout*>(qmlAttachedPropertiesObject<BleeckerLayout>(item,true));
    connect(hint,&BleeckerLayout::metricsChanged,this,changed);
}
void MediaLibraryBase::setActive(const EntryPtr &entry,bool value) {
    if(!entry->roles ||entry->roles->active==value)return;
    entry->roles->active=value;
    if(entry->item &&entry->item->metaObject()->indexOfProperty("tileActive")>=0)entry->item->setProperty("tileActive",value);
    emit entry->roles->activeChanged();entry->cell->setVisible(value);
}
qreal MediaLibraryBase::measure(const EntryPtr &entry,qreal offered) {
    auto item=entry->item.data();auto hint=qobject_cast<BleeckerLayout*>(qmlAttachedPropertiesObject<BleeckerLayout>(item,true));
    entry->cell->setWidth(std::max(qreal(0),offered));
    hint->propose(std::max(qreal(0),offered));
    const auto ideal=hint->idealWidth>=0 ? hint->idealWidth:entry->explicitWidth ? item->width():item->implicitWidth();
    const auto minimum=hint->minimumWidth>=0 ? hint->minimumWidth:entry->explicitWidth ? ideal:0;
    if(!std::isfinite(ideal)||!std::isfinite(minimum)||ideal<0||minimum<0||minimum>ideal)qFatal("MediaLibrary tile requires finite widths with 0 <= minimum <= ideal");
    if(hint->fillsWidth)item->setWidth(std::max(minimum,std::max(qreal(0),offered)));
    else if(!entry->explicitWidth)item->setWidth(std::clamp(offered,minimum,ideal));
    const auto height=entry->explicitHeight ? item->height():item->implicitHeight();
    if(!std::isfinite(height)||height<0)qFatal("MediaLibrary tile height must be finite and nonnegative");
    if(!entry->explicitHeight)item->setHeight(height);
    entry->measuredWidth=item->width();entry->measuredHeight=height;entry->measured=true;return height;
}
QRectF MediaLibraryBase::visibleRect() const {
    if(!window() ||!isVisible())return {};
    QRectF result=mapRectFromItem(window()->contentItem(),QRectF(0,0,window()->width(),window()->height()));
    for(auto ancestor=parentItem();ancestor;ancestor=ancestor->parentItem())if(ancestor->clip())
        result=result.intersected(mapRectFromItem(ancestor,QRectF(0,0,ancestor->width(),ancestor->height())));
    return result;
}
void MediaLibraryBase::attachWindow(QQuickWindow *window) {
    disconnect(m_frameConnection);
    if(window)m_frameConnection=connect(window,&QQuickWindow::afterAnimating,this,&MediaLibraryBase::refreshViewport);
    polish();
}
void MediaLibraryBase::refreshViewport() {
    const auto viewport=visibleRect();if(viewport==m_viewport)return;m_viewport=viewport;polish();
}
int MediaLibraryBase::instantiatedCount() const {int count=0;for(const auto &e:m_entries)count+=!e->item.isNull();return count;}
int MediaLibraryBase::activeCount() const {int count=0;for(const auto &e:m_entries)count+=e->roles &&e->roles->active;return count;}
QQuickItem *MediaLibraryBase::itemAt(int index) const {return index>=0 &&index<m_entries.size() ? m_entries[index]->item.data():nullptr;}
void MediaLibraryBase::layout() {
    if(!m_complete ||m_layingOut)return;m_layingOut=true;
    const auto viewport=visibleRect();m_viewport=viewport;
    if(!QQuickItemPrivate::get(this)->widthValid() &&!m_entries.isEmpty() &&window()) {
        instantiate(m_entries[0],0);auto item=m_entries[0]->item.data();auto hint=qobject_cast<BleeckerLayout*>(qmlAttachedPropertiesObject<BleeckerLayout>(item,true));
        m_naturalWidth=hint->idealWidth>=0 ? hint->idealWidth:m_entries[0]->explicitWidth ? item->width():item->implicitWidth();setImplicitWidth(m_naturalWidth);
    }
    if(width()<=0 ||m_entries.isEmpty() ||!window()) {
        for(const auto &entry:m_entries)setActive(entry,false);
        const auto previousHeight=m_contentHeight;
        m_columns=0;m_columnWidth=0;m_contentHeight=0;
        if(m_entries.isEmpty()){m_naturalWidth=0;setImplicitWidth(0);}
        setImplicitHeight(0);if(previousHeight!=m_contentHeight)emit contentHeightChanged();
        emit metricsChanged();m_layingOut=false;return;
    }
    if(!std::isfinite(width()))qFatal("MediaLibrary layout width must be finite");
    if(m_minimum==-16)qFatal("MediaLibrary minimumTileWidth -16 produces an undefined native adaptive column count");
    const auto proposed=std::isfinite(m_minimum) ? std::floor((width()+16)/(m_minimum+16)):1;
    if(proposed>std::numeric_limits<int>::max())qFatal("MediaLibrary column count exceeds Qt's index range");
    m_columns=proposed>=1 ? int(proposed):1;m_columnWidth=(width()-16.0*(m_columns-1))/m_columns;
    const auto rows=(m_entries.size()+m_columns-1)/m_columns;
    QList<qreal> heights;QList<bool> known;heights.reserve(rows);
    for(int row=0;row<rows;++row) {
        qreal rowHeight=0;bool complete=true;
        for(int index=row*m_columns;index<std::min(qsizetype(row+1)*m_columns,m_entries.size());++index) {
            const auto &entry=m_entries[index];complete&=!entry->item.isNull();if(entry->item)rowHeight=std::max(rowHeight,measure(entry,m_columnWidth));
        }
        known.append(complete);heights.append(complete ? rowHeight:m_estimate);
    }
    qreal provisional=std::max(qsizetype(0),rows-1)*16;for(auto rowHeight:heights)provisional+=rowHeight;
    const auto offset=QQuickItemPrivate::get(this)->heightValid() ? (height()-provisional)/2:0;
    QList<bool> active(rows,false);qreal y=0;bool learned=false;
    for(int row=0;row<rows;++row) {
        const bool visible=!viewport.isEmpty() && y+offset<=viewport.bottom() &&y+offset+std::max(qreal(1),heights[row])>=viewport.top();
        active[row]=visible;
        if(visible) {
            qreal rowHeight=0;
            for(int index=row*m_columns;index<std::min(qsizetype(row+1)*m_columns,m_entries.size());++index){instantiate(m_entries[index],index);rowHeight=std::max(rowHeight,measure(m_entries[index],m_columnWidth));}
            learned|=!known[row];known[row]=true;heights[row]=rowHeight;
        }
        y+=heights[row]+16;
    }
    if(learned) {
        qreal sum=0;int count=0;for(int row=0;row<rows;++row)if(known[row]){sum+=heights[row];++count;}
        if(count)m_estimate=sum/count;
        for(int row=0;row<rows;++row)if(!known[row])heights[row]=m_estimate;
    }
    const auto previousHeight=m_contentHeight;
    m_contentHeight=std::max(qsizetype(0),rows-1)*16;for(auto h:heights)m_contentHeight+=h;
    if(!m_entries.isEmpty() &&m_entries[0]->item){auto item=m_entries[0]->item.data();auto hint=qobject_cast<BleeckerLayout*>(qmlAttachedPropertiesObject<BleeckerLayout>(item,true));m_naturalWidth=hint->idealWidth>=0 ? hint->idealWidth:m_entries[0]->explicitWidth ? item->width():item->implicitWidth();}
    setImplicitSize(m_naturalWidth,m_contentHeight);
    if(previousHeight!=m_contentHeight)emit contentHeightChanged();
    // Auto-height callers can recenter synchronously when the grid publishes
    // its measured size. A viewport calculated before that change is stale;
    // keep existing activity until the next polish uses the settled geometry.
    const bool viewportStable=visibleRect()==viewport;
    QList<qreal> columnOrigins;qreal span=0;
    for(int column=0;column<m_columns;++column){if(column<m_entries.size())columnOrigins.append(span);span+=m_columnWidth+16;}
    span-=16;const auto horizontal=(width()-span)/2,vertical=(height()-m_contentHeight)/2;y=0;
    for(int row=0;row<rows;++row) {
        for(int index=row*m_columns;index<std::min(qsizetype(row+1)*m_columns,m_entries.size());++index) {
            const auto &entry=m_entries[index];if(!entry->item)continue;
            const auto column=index%m_columns;
            const auto left=horizontal+columnOrigins[column]+(m_columnWidth-entry->measuredWidth)/2;
            const auto x=m_mirrored ? width()-left-entry->measuredWidth:left;
            entry->cell->setPosition(QPointF(x,vertical+y+(heights[row]-entry->measuredHeight)/2));entry->cell->setSize(entry->item->size());
            if(viewportStable)setActive(entry,active[row]);
        }
        y+=heights[row]+16;
    }
    emit metricsChanged();m_layingOut=false;
    if((learned &&m_contentHeight!=provisional) ||!viewportStable)polish();
}
QVariantMap MediaLibraryBase::layoutSnapshot() const {
    QVariantList entries;
    for(int index=0;index<m_entries.size();++index) {
        const auto &entry=m_entries[index];QVariantMap row{{"index",index},{"key",entry->key},{"created",!entry->item.isNull()},{"active",entry->roles &&entry->roles->active}};
        if(entry->item)row.insert("frame",QVariantMap{{"x",entry->cell->x()},{"y",entry->cell->y()},{"width",entry->item->width()},{"height",entry->item->height()}});
        entries.append(row);
    }
    return {{"columns",m_columns},{"columnWidth",m_columnWidth},{"contentHeight",m_contentHeight},{"naturalWidth",m_naturalWidth},{"entries",entries},{"nativeSizingAcceptance","pending"},{"nativeLazyTimingAcceptance","pending"},{"nativeRasterAcceptance","pending"}};
}

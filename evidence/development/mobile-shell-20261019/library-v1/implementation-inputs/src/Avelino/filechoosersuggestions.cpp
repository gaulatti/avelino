#include "filechoosersuggestions.h"
#include "filechooserpathinput.h"
#include <QtQuick/private/qaccessiblequickitem_p.h>
#include <QAccessible>
#include <QCoreApplication>
#include <QQuickWindow>
#include <QTimer>

static_assert(QT_VERSION==QT_VERSION_CHECK(6,8,3),"Revalidate owned suggestion selection accessibility before upgrading Qt");
namespace {
class SuggestionsAccessible final : public QAccessibleQuickItem,public QAccessibleSelectionInterface {
    FileChooserSuggestions *view()const{return qobject_cast<FileChooserSuggestions*>(object());}
    FileChooserPaths *model()const{return view()?view()->pathModel():nullptr;}
    int choiceIndex(QAccessibleInterface *item)const{
        const auto row=item?qobject_cast<FileChooserSuggestionRow*>(item->object()):nullptr;
        if(!row||!model()||QAccessibleQuickItem::indexOfChild(item)<0)return -1;
        const int index=row->m_choiceIndex;
        const auto entries=model()->entries();
        return index>=0&&index<entries.size()&&entries[index].toMap()["available"].toBool()&&row->isEnabled()?index:-1;
    }
public:
    using QAccessibleQuickItem::QAccessibleQuickItem;
    void *interface_cast(QAccessible::InterfaceType type)override{
        if(type==QAccessible::SelectionInterface)return static_cast<QAccessibleSelectionInterface*>(this);
        return QAccessibleQuickItem::interface_cast(type);
    }
    int selectedItemCount()const override{return selectedItems().size();}
    QList<QAccessibleInterface*> selectedItems()const override{
        if(!model()||model()->currentIndex()<0)return {};
        for(int i=0;i<childCount();++i)if(auto item=child(i);choiceIndex(item)==model()->currentIndex())return {item};
        return {};
    }
    bool select(QAccessibleInterface *item)override{
        const int index=choiceIndex(item);const QPointer<FileChooserPaths> paths=model();if(index<0||!paths)return false;
        paths->select(index);return paths&&paths->currentIndex()==index;
    }
    // The existing chooser model exposes one highlighted proposal and no
    // command to deselect it. Do not invent multi-selection or clearing rules.
    bool unselect(QAccessibleInterface*)override{return false;}
    bool selectAll()override{return false;}
    bool clear()override{return !model()||model()->currentIndex()<0;}
};
QAccessibleInterface *suggestionsFactory(const QString &,QObject *object){
    if(auto view=qobject_cast<FileChooserSuggestions*>(object))return new SuggestionsAccessible(view);
    return nullptr;
}
}
FileChooserSuggestions::FileChooserSuggestions(QQuickItem *parent):QQuickListView(parent){
    static const bool registered=[] {QAccessible::installFactory(suggestionsFactory);return true;}();Q_UNUSED(registered);
    connect(this,&QQuickListView::currentItemChanged,this,&FileChooserSuggestions::scheduleSelectionUpdate);
    connect(this,&QQuickItem::visibleChanged,this,&FileChooserSuggestions::scheduleSelectionUpdate);
}
FileChooserSuggestions::~FileChooserSuggestions(){
    // QQuickItemView emits currentItemChanged from its base destructor, after
    // this class's fields and type are gone. Disconnect before that phase.
    disconnect(this,nullptr,this,nullptr);
    for(const auto connection:m_connections)disconnect(connection);
    QCoreApplication::removePostedEvents(this,QEvent::MetaCall);
}
void FileChooserSuggestions::setPathModel(FileChooserPaths *model){
    if(m_model==model)return;
    for(const auto connection:m_connections)disconnect(connection);m_connections.clear();m_model=model;
    if(model)m_connections={
        connect(model,&FileChooserPaths::currentIndexChanged,this,&FileChooserSuggestions::scheduleSelectionUpdate),
        connect(model,&FileChooserPaths::entriesChanged,this,&FileChooserSuggestions::scheduleSelectionUpdate),
        connect(model,&QObject::destroyed,this,[this]{scheduleSelectionUpdate();emit pathModelChanged();})};
    scheduleSelectionUpdate();emit pathModelChanged();
}
void FileChooserSuggestions::scheduleSelectionUpdate(){
    if(m_scheduled)return;m_scheduled=true;
    // Run after QML has applied currentIndex/highlighted/Accessible.selected.
    QTimer::singleShot(0,this,&FileChooserSuggestions::updateSelection);
}
void FileChooserSuggestions::updateSelection(){
    m_scheduled=false;
    if(!isVisible()||!window()||!window()->isVisible()){m_previous=nullptr;m_previousPath.clear();return;}
    QPointer<QQuickItem> next;
    if(auto row=qobject_cast<FileChooserSuggestionRow*>(currentItem());row&&m_model&&row->isEnabled()&&row->m_choiceIndex==m_model->currentIndex())next=row;
    const auto path=next?m_model->selectedUrl().toString():QString();
    if(m_previous==next&&m_previousPath==path)return;
    const auto previous=m_previous;m_previous=next;m_previousPath=path;
    QPointer<FileChooserSuggestions> guard(this);
    if(previous&&previous!=next){
        QAccessibleEvent event(previous,QAccessible::SelectionRemove);QAccessible::updateAccessibility(&event);
        if(!guard||!isVisible()||!window()||!window()->isVisible())return;
    }
    // Qt 6.8.3's AT-SPI adaptor forwards Selection events, but ignores the
    // selected bit in StateChanged and ignores ActiveDescendantChanged.
    if(next){QAccessibleEvent event(next,QAccessible::Selection);QAccessible::updateAccessibility(&event);}
    else{
        QAccessibleEvent event(this,QAccessible::SelectionWithin);QAccessible::updateAccessibility(&event);
        if(!guard||!isVisible()||!window()||!window()->isVisible())return;
        // Orca's selection handler leaves its logical focus on the old row
        // when the list becomes empty. Report the real, still-focused editor
        // after the clearing notification so subsequent input has a live target.
        if(auto editor=qobject_cast<FileChooserPathInput*>(window()->activeFocusItem());editor&&editor->hasActiveFocus()){
            QAccessibleEvent focus(editor,QAccessible::Focus);QAccessible::updateAccessibility(&focus);
        }
    }
}

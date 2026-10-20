#include "filechooserbuttonbase.h"
#include <QtQuick/private/qaccessiblequickitem_p.h>
#include <QtGui/private/qguiapplication_p.h>
#include <QtQuickTemplates2/private/qquickpopupwindow_p_p.h>
#include <QQuickWindow>
#include <QAccessible>

static_assert(QT_VERSION==QT_VERSION_CHECK(6,8,3),"Revalidate owned menu accessibility before upgrading Qt");
namespace {
class ButtonAccessible final : public QAccessibleQuickItem {
    FileChooserButtonBase *button()const{return qobject_cast<FileChooserButtonBase*>(object());}
    QAccessibleInterface *openMenu()const{
        const auto owner=button();const auto menu=owner?owner->accessibilityMenu():nullptr;
        return menu&&menu->isVisible()?QAccessible::queryAccessibleInterface(menu->popupItem()):nullptr;
    }
public:
    using QAccessibleQuickItem::QAccessibleQuickItem;
    int childCount()const override{return QAccessibleQuickItem::childCount()+(openMenu()?1:0);}
    QAccessibleInterface *child(int index)const override{
        return index==QAccessibleQuickItem::childCount()?openMenu():QAccessibleQuickItem::child(index);
    }
    int indexOfChild(const QAccessibleInterface *child)const override{
        if(!child)return -1;
        const auto menu=openMenu();
        return child&&menu&&child->object()==menu->object()?QAccessibleQuickItem::childCount():QAccessibleQuickItem::indexOfChild(child);
    }
    QAccessibleInterface *childAt(int x,int y)const override{
        if(const auto menu=openMenu();menu&&menu->rect().contains(x,y)){
            if(const auto child=menu->childAt(x,y))return child;
            return menu;
        }
        return QAccessibleQuickItem::childAt(x,y);
    }
    QAccessibleInterface *focusChild()const override{
        if(const auto menu=openMenu())return menu->focusChild()?menu->focusChild():menu;
        return QAccessibleQuickItem::focusChild();
    }
    QAccessible::State state()const override{
        auto result=QAccessibleQuickItem::state();
        if(button()&&button()->accessibilityMenu()){
            result.hasPopup=true;result.expandable=true;
            result.expanded=bool(openMenu());result.collapsed=!result.expanded;
        }
        return result;
    }
};
class MenuAccessible final : public QAccessibleQuickItem {
public:
    using QAccessibleQuickItem::QAccessibleQuickItem;
    QAccessibleInterface *parent()const override{
        const auto menu=object()?qobject_cast<FileChooserMenuBase*>(object()->parent()):nullptr;
        return menu&&menu->opener()?QAccessible::queryAccessibleInterface(menu->opener()):QAccessibleQuickItem::parent();
    }
};
QAccessibleInterface *menuFactory(const QString &,QObject *object){
    if(auto button=qobject_cast<FileChooserButtonBase*>(object))return new ButtonAccessible(button);
    if(auto menu=qobject_cast<FileChooserMenuBase*>(object->parent()))
        if(menu->popupItem()==object)return new MenuAccessible(menu->popupItem());
    return nullptr;
}
void installFactory(){static const bool registered=[] {QAccessible::installFactory(menuFactory);return true;}();Q_UNUSED(registered);}
}
FileChooserButtonBase::FileChooserButtonBase(QQuickItem *parent):QQuickButton(parent){installFactory();}
FileChooserMenuBase *FileChooserButtonBase::accessibilityMenu()const{return m_menu;}
void FileChooserButtonBase::setAccessibilityMenu(FileChooserMenuBase *menu){
    if(menu==m_menu)return;
    for(const auto connection:m_connections)disconnect(connection);m_connections.clear();
    m_menu=menu;
    if(menu)m_connections={
        connect(menu,&QQuickPopup::visibleChanged,this,[this]{
            QAccessibleEvent reordered(this,QAccessible::ObjectReorder);QAccessible::updateAccessibility(&reordered);
            QAccessible::State changed;changed.expanded=true;changed.collapsed=true;
            QAccessibleStateChangeEvent state(this,changed);QAccessible::updateAccessibility(&state);
        }),
        connect(menu,&QObject::destroyed,this,[this]{m_menu=nullptr;emit accessibilityMenuChanged();})};
    emit accessibilityMenuChanged();
}
FileChooserMenuBase::FileChooserMenuBase(QObject *parent):QQuickMenu(parent){
    installFactory();
    if(!QGuiApplication::platformName().startsWith("wayland"))return;
    // An assistive action has no Wayland input serial. Qt 6.8.3 otherwise
    // creates a toplevel before the first input, or grabs with an old serial.
    // Its ToolTip surface path creates an anchored, non-grabbing xdg_popup.
    // Once mapped, restore the logical Popup type and Qt's popup input stack.
    // This keeps the owned menu window, accessibility subtree and key routing.
    connect(popupItem(),&QQuickItem::windowChanged,this,[this](QQuickWindow *window){
        const auto owned=qobject_cast<QQuickPopupWindow*>(window);
        if(!owned||owned->popup()!=this)return;
        const auto flags=int(window->flags());
        window->setFlags(Qt::WindowFlags((flags&~int(Qt::WindowType_Mask))|int(Qt::ToolTip)));
    });
    connect(this,&QQuickPopup::aboutToShow,this,[this]{
        if(const auto window=qobject_cast<QQuickPopupWindow*>(popupItem()->window());window&&window->popup()==this){
            const auto flags=int(window->flags());
            window->setFlags(Qt::WindowFlags((flags&~int(Qt::WindowType_Mask))|int(Qt::Popup)));
            QGuiApplicationPrivate::activatePopup(window);
        }
    });
    connect(this,&QQuickPopup::opened,this,[this]{
        // A non-grabbing surface leaves native keyboard focus on its parent.
        // Give Qt's popup delivery agent an explicit focused menu item.
        for(int index=0;index<count();++index){
            if(auto item=itemAt(index);item&&item->isEnabled()){
                setCurrentIndex(index);item->forceActiveFocus(Qt::PopupFocusReason);return;
            }
        }
        popupItem()->forceActiveFocus(Qt::PopupFocusReason);
    });
    connect(qGuiApp,&QGuiApplication::applicationStateChanged,this,[this](Qt::ApplicationState state){
        if(isVisible()&&state!=Qt::ApplicationActive)close();
    });
}
void FileChooserMenuBase::setOpener(FileChooserButtonBase *button){
    if(button==m_opener)return;m_opener=button;emit openerChanged();
}

#include "filechooserbrowser.h"
#include "filechooserpaths.h"
#include <QAccessible>
#include <QDir>
#include <QFile>
#include <QJSValue>
#include <QImage>
#include <QQmlEngine>
#include <QQuickItem>
#include <QQuickView>
#include <QRegularExpression>
#include <QSettings>
#include <QTemporaryDir>
#include <QtTest>
#include <functional>

class FileInputAnnouncementCapture {
    QAccessible::UpdateHandler previous;
    static void receive(QAccessibleEvent *event){
        if(event->type()!=QAccessible::Announcement)return;
        auto announcement=static_cast<QAccessibleAnnouncementEvent*>(event);
        messages.append({announcement->message(),announcement->politeness(),event->object()});
    }
public:
    struct Message {QString text;QAccessible::AnnouncementPoliteness politeness;QPointer<QObject> source;};
    inline static QList<Message> messages;
    FileInputAnnouncementCapture(){messages.clear();previous=QAccessible::installUpdateHandler(receive);}
    ~FileInputAnnouncementCapture(){QAccessible::installUpdateHandler(previous);}
};

class FileInputSelectionCapture {
    QAccessible::UpdateHandler previous;
    static void receive(QAccessibleEvent *event){
        if(event->type()!=QAccessible::Selection&&event->type()!=QAccessible::SelectionRemove&&event->type()!=QAccessible::SelectionWithin&&event->type()!=QAccessible::Focus)return;
        const auto accessible=event->accessibleInterface();
        events.append({event->type(),accessible?accessible->text(QAccessible::Name):QString(),event->object()?event->object()->objectName():QString(),accessible&&accessible->state().selected,accessible&&accessible->state().focused});
        const auto observer=callback;if(observer)observer(event);
    }
public:
    struct Event {QAccessible::Event type;QString name,objectName;bool selected,focused;};
    inline static QList<Event> events;
    inline static std::function<void(QAccessibleEvent*)> callback;
    static bool saw(QAccessible::Event type,const QString &name,bool selected){
        for(const auto &event:events)if(event.type==type&&event.name==name&&event.selected==selected)return true;return false;
    }
    static int suggestionEvents(){
        int count=0;for(const auto &event:events)if(event.objectName=="bleeckerFileChooserGoToTargets"||event.objectName.startsWith("bleeckerFileChooserGoToTarget_"))++count;return count;
    }
    static bool focusFollowsClearedSuggestions(){
        bool cleared=false;for(const auto &event:events){
            if(event.type==QAccessible::SelectionWithin&&event.objectName=="bleeckerFileChooserGoToTargets")cleared=true;
            if(cleared&&event.type==QAccessible::Focus&&event.objectName=="bleeckerFileChooserGoToPath"&&event.focused)return true;
        }return false;
    }
    FileInputSelectionCapture(){events.clear();callback={};previous=QAccessible::installUpdateHandler(receive);}
    ~FileInputSelectionCapture(){callback={};QAccessible::installUpdateHandler(previous);}
};

class FileInputUiTests:public QObject {
    Q_OBJECT
    QTemporaryDir config;
    void put(const QString &path){QFile f(path);QVERIFY(f.open(QIODevice::WriteOnly));QVERIFY(f.write("Avelino owned UI fixture\n")>0);}
    QQuickItem *find(QQuickItem *root,const QString &name){
        if(!root)return nullptr;
        if(root->objectName()==name)return root;
        for(auto child:root->childItems())if(auto result=find(child,name))return result;
        return nullptr;
    }
    QQuickItem *findVisible(const QString &name){
        for(auto window:QGuiApplication::topLevelWindows())if(auto quick=qobject_cast<QQuickWindow*>(window);quick&&quick->isVisible())
            if(auto item=find(quick->contentItem(),name);item&&item->isVisible())return item;
        return nullptr;
    }
    int row(FileChooserModel *model,const QString &name){
        for(int i=0;i<model->count();++i)if(model->entry(i)["name"]==name)return i;
        return -1;
    }
    int listed(FileChooserListing *model,const QString &name){
        for(int i=0;i<model->count();++i)if(model->entry(i)["name"]==name)return i;
        return -1;
    }
    void click(QQuickItem *item,Qt::KeyboardModifiers modifiers={}){
        QVERIFY(item);QVERIFY(item->window());
        QTest::mouseClick(item->window(),Qt::LeftButton,modifiers,item->mapToScene(item->boundingRect().center()).toPoint());
    }
    void typeText(QWindow *window,const QString &text){for(const auto character:text.toLatin1())QTest::keyClick(window,character);}
    QVariantList results(QQuickItem *root){return root->property("results").value<QJSValue>().toVariant().toList();}
    void capture(QQuickWindow *window,const QString &name){
        QVERIFY(window);QTest::qWait(40);
        const auto image=window->grabWindow();QVERIFY(!image.isNull());
        QDir directory(AVELINO_FILE_INPUT_EVIDENCE_DIR);QVERIFY(directory.mkpath("."));
        QVERIFY(image.save(directory.filePath(name+"-dpr"+QString::number(window->devicePixelRatio())+".png")));
    }
    bool load(QQuickView &view,const QTemporaryDir &root){
        view.engine()->addImportPath(AVELINO_FILE_INPUT_IMPORT_PATH);
        view.setInitialProperties({{"fixtureRoot",QUrl::fromLocalFile(root.path())}});
        view.setSource(QUrl("qrc:/file-input-tests/fileinput-fixture.qml"));
        if(view.status()!=QQuickView::Ready){
            const auto error=view.errors().isEmpty()?QStringLiteral("FileInput fixture did not load"):view.errors().first().toString();
            QTest::qFail(qPrintable(error),__FILE__,__LINE__);return false;
        }
        view.show();return QTest::qWaitForWindowExposed(&view);
    }
private slots:
    void initTestCase(){QAccessible::setActive(true);QVERIFY(config.isValid());QSettings::setPath(QSettings::NativeFormat,QSettings::UserScope,config.path());}
    void init(){QTest::failOnWarning(QRegularExpression(".*(FileInput requires|Unable to assign|should be coerced|ReferenceError|TypeError).*"));QSettings settings("Avelino","FileChooser");settings.clear();settings.sync();}
    void actualLocationMenuSelectionHistoryRecentAndRemoval(){
        QTemporaryDir directory;QDir root(directory.path());QVERIFY(root.mkpath("Parent/Start"));put(root.filePath("Parent/Start/Alpha.txt"));
        const auto start=root.filePath("Parent/Start"),parent=root.filePath("Parent");
        QQuickView view;QVERIFY(load(view,directory));auto fixture=view.rootObject();fixture->setProperty("fixtureRoot",QUrl::fromLocalFile(start));
        auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);auto browser=control->property("browser").value<FileChooserBrowser*>();
        auto chooser=control->property("chooser").value<QObject*>();click(control->property("inputItem").value<QQuickItem*>());QTRY_VERIFY(chooser->property("visible").toBool());
        auto content=chooser->property("contentItem").value<QQuickItem*>();QVERIFY(content);
        const auto chooserWindowFlags=content->window()->flags();
        auto chooseMenu=[&](int index,bool accessibleAction){
            auto button=find(content,"bleeckerFileChooserLocation");QVERIFY(button);
            auto interface=QAccessible::queryAccessibleInterface(button);QVERIFY(interface&&interface->actionInterface());
            QCOMPARE(interface->role(),QAccessible::ButtonMenu);QCOMPARE(interface->text(QAccessible::Name),QString("Where:"));
            QVERIFY(interface->actionInterface()->actionNames().contains(QAccessibleActionInterface::pressAction()));
            if(accessibleAction)interface->actionInterface()->doAction(QAccessibleActionInterface::pressAction());else click(button);
            QQuickItem *entry=nullptr;QTRY_VERIFY((entry=findVisible("bleeckerFileChooserLocation_"+QString::number(index))));
            QVERIFY(entry->window()!=content->window());QVERIFY(QTest::qWaitForWindowExposed(entry->window()));
            QCOMPARE(content->window()->flags(),chooserWindowFlags);
            auto accessible=QAccessible::queryAccessibleInterface(entry);QVERIFY(accessible);QCOMPARE(accessible->role(),QAccessible::MenuItem);
            QVERIFY(interface->state().expanded);QVERIFY(interface->state().hasPopup);
            QAccessibleInterface *menu=nullptr;
            for(int i=0;i<interface->childCount();++i){const auto child=interface->child(i);if(child&&child->role()==QAccessible::PopupMenu)menu=child;}
            QVERIFY2(menu,"The opener must expose its separate-window menu in the accessible tree");
            QCOMPARE(menu->parent(),interface);QVERIFY(interface->indexOfChild(menu)>=0);
            bool reachable=false;
            auto visit=[&](auto &&self,QAccessibleInterface *node)->void {
                if(node->object()==entry)reachable=true;
                for(int i=0;i<node->childCount();++i)if(auto child=node->child(i))self(self,child);
            };
            visit(visit,menu);QVERIFY(reachable);
            capture(entry->window(),"location-menu-"+QString::number(index));
            if(accessibleAction)accessible->actionInterface()->doAction(QAccessibleActionInterface::pressAction());else click(entry);
            QTRY_VERIFY(!findVisible("bleeckerFileChooserLocation_"+QString::number(index)));
        };
        click(find(content,"bleeckerFileChooserRow0_"+QString::number(row(browser->modelAt(0),"Alpha.txt"))));
        const auto selected=browser->selectedUrls();chooseMenu(0,true);QCOMPARE(browser->selectedUrls(),selected);QVERIFY(!browser->canGoBack());QVERIFY(results(fixture).isEmpty());
        chooseMenu(1,false);QTRY_COMPARE(browser->folderPath(),parent);QVERIFY(browser->selectedUrls().isEmpty());QVERIFY(browser->canGoBack());QVERIFY(results(fixture).isEmpty());
        click(find(content,"bleeckerFileChooserBack"));QTRY_COMPARE(browser->folderPath(),start);QVERIFY(browser->selectedUrls().isEmpty());
        click(find(content,"bleeckerFileChooserLocation"));QQuickItem *first=nullptr;QTRY_VERIFY((first=findVisible("bleeckerFileChooserLocation_0")));
        QTest::keyClick(first->window(),Qt::Key_Escape);QTRY_VERIFY(!findVisible("bleeckerFileChooserLocation_0"));QVERIFY(browser->active());
        click(find(content,"bleeckerFileChooserLocation"));QTRY_VERIFY(findVisible("bleeckerFileChooserLocation_0"));
        click(find(content,"bleeckerFileChooserError"));
        QTRY_VERIFY(!findVisible("bleeckerFileChooserLocation_0"));QVERIFY(browser->active());QVERIFY(results(fixture).isEmpty());
        click(find(content,"bleeckerFileChooserRow0_"+QString::number(row(browser->modelAt(0),"Alpha.txt"))));click(find(content,"bleeckerFileChooserOpen"));QTRY_COMPARE(results(fixture).size(),1);
        fixture->setProperty("mounted",false);QTRY_VERIFY(!fixture->findChild<QQuickItem*>("fileInput"));fixture->setProperty("mounted",true);
        QTRY_VERIFY((control=fixture->findChild<QQuickItem*>("fileInput")));browser=control->property("browser").value<FileChooserBrowser*>();chooser=control->property("chooser").value<QObject*>();
        click(control->property("inputItem").value<QQuickItem*>());QTRY_VERIFY(chooser->property("visible").toBool());content=chooser->property("contentItem").value<QQuickItem*>();
        browser->refreshPlaces();int recent=-1;const auto entries=browser->places()->entries();
        for(int i=0;i<entries.size();++i){const auto value=entries[i].toMap();if(value["recent"].toBool()&&value["url"].toUrl()==QUrl::fromLocalFile(start)){recent=i;break;}}
        QVERIFY(recent>=0);chooseMenu(recent,false);QCOMPARE(results(fixture).size(),1);QVERIFY(browser->selectedUrls().isEmpty());
        click(find(content,"bleeckerFileChooserLocation"));QTRY_VERIFY(findVisible("bleeckerFileChooserLocation_0"));
        fixture->setProperty("mounted",false);QTRY_VERIFY(!findVisible("bleeckerFileChooserLocation_0"));QVERIFY(!fixture->findChild<QQuickItem*>("fileInput"));
    }
    void actualViewMenuListDisclosureAndIconsNavigation(){
        QTemporaryDir directory;QDir root(directory.path());QVERIFY(root.mkdir("Folder"));
        put(root.filePath("Alpha.txt"));put(root.filePath("Bravo.txt"));put(root.filePath("Folder/Child.txt"));put(root.filePath("blocked.png"));
        QQuickView view;QVERIFY(load(view,directory));auto fixture=view.rootObject();auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
        auto browser=control->property("browser").value<FileChooserBrowser*>();auto chooser=control->property("chooser").value<QObject*>();
        click(control->property("inputItem").value<QQuickItem*>());QTRY_VERIFY(chooser->property("visible").toBool());
        auto content=chooser->property("contentItem").value<QQuickItem*>();QTRY_VERIFY(content&&content->window());
        int viewChanges=0;
        auto selectView=[&](const QString &mode){
            auto viewButton=find(content,"bleeckerFileChooserViewOptions");QVERIFY(viewButton);
            auto viewAccessible=QAccessible::queryAccessibleInterface(viewButton);QVERIFY(viewAccessible&&viewAccessible->actionInterface());
            QVERIFY(viewAccessible->actionInterface()->actionNames().contains(QAccessibleActionInterface::pressAction()));
            if(!viewChanges)viewAccessible->actionInterface()->doAction(QAccessibleActionInterface::pressAction());else click(viewButton);
            QQuickItem *option=nullptr;QTRY_VERIFY((option=find(content->window()->contentItem(),"bleeckerFileChooserView_"+mode))&&option->isVisible());
            if(!viewChanges){
                QTest::keyClick(content->window(),Qt::Key_Escape);QTRY_VERIFY(!option->isVisible());QVERIFY(browser->active());
                viewAccessible->actionInterface()->doAction(QAccessibleActionInterface::pressAction());QTRY_VERIFY(option->isVisible());
            }
            auto menuAccessible=QAccessible::queryAccessibleInterface(option);QVERIFY(menuAccessible);
            QCOMPARE(menuAccessible->role(),QAccessible::MenuItem);
            QVERIFY(menuAccessible->actionInterface()&&menuAccessible->actionInterface()->actionNames().contains(QAccessibleActionInterface::pressAction()));
            QCOMPARE(menuAccessible->text(QAccessible::Name),mode=="list"?QString("List"):mode=="icons"?QString("Icons"):QString("Columns"));
            capture(content->window(),"view-menu-"+QString::number(++viewChanges)+"-"+mode);
            if(viewChanges==1)menuAccessible->actionInterface()->doAction(QAccessibleActionInterface::pressAction());else click(option);
            QTRY_COMPARE(browser->viewMode(),mode);
            QVERIFY(option->property("checked").toBool());QVERIFY(menuAccessible->state().checked);
        };
        selectView("list");selectView("list");auto listing=browser->listing();QTRY_VERIFY(listing->count()==4);
        click(find(content,"bleeckerFileChooserListRow_"+QString::number(listed(listing,"Alpha.txt"))));
        const auto selectedBeforeSort=browser->selectedUrls();
        click(find(content,"bleeckerFileChooserSort_name"));QVERIFY(!listing->ascending());QCOMPARE(browser->selectedUrls(),selectedBeforeSort);
        click(find(content,"bleeckerFileChooserSort_size"));QCOMPARE(listing->sortKey(),QString("size"));QCOMPARE(browser->selectedUrls(),selectedBeforeSort);
        click(find(content,"bleeckerFileChooserSort_name"));QVERIFY(listing->ascending());QCOMPARE(browser->selectedUrls(),selectedBeforeSort);
        auto treeInterface=QAccessible::queryAccessibleInterface(find(content,"bleeckerFileChooserList"));QVERIFY(treeInterface);
        auto table=treeInterface->tableInterface();QVERIFY(table);QCOMPARE(table->columnCount(),4);QCOMPARE(table->rowCount(),4);
        QVERIFY(treeInterface->state().multiSelectable);QVERIFY(treeInterface->selectionInterface());QCOMPARE(table->selectedCellCount(),4);
        const auto alpha=listed(listing,"Alpha.txt");
        auto nameCell=table->cellAt(alpha,0);QVERIFY(nameCell&&nameCell->tableCellInterface());
        QCOMPARE(nameCell->tableCellInterface()->table(),treeInterface);QCOMPARE(nameCell->tableCellInterface()->rowIndex(),alpha);
        const QStringList headers={"Name","Size","Kind","Date Added"};
        for(int column=0;column<headers.size();++column){
            const auto cell=table->cellAt(alpha,column);QVERIFY(cell&&cell->tableCellInterface());
            const auto actual=cell->tableCellInterface()->columnHeaderCells();QCOMPARE(actual.size(),1);
            QCOMPARE(actual.first()->text(QAccessible::Name),headers[column]);
        }
        auto sizeCell=table->cellAt(alpha,1);QVERIFY(sizeCell&&sizeCell->tableCellInterface());
        QCOMPARE(sizeCell->text(QAccessible::Name),listing->entry(alpha)["size"].toString());QCOMPARE(sizeCell->tableCellInterface()->columnIndex(),1);
        QVERIFY(!sizeCell->rect().isEmpty());QCOMPARE(treeInterface->childAt(sizeCell->rect().center().x(),sizeCell->rect().center().y()),sizeCell);
        QCOMPARE(table->cellAt(alpha,3)->text(QAccessible::Description),QString("Date Added is unavailable"));
        const auto oldSizeId=QAccessible::uniqueId(sizeCell);
        auto folder=listed(listing,"Folder");QVERIFY(folder>=0);
        QTRY_VERIFY(find(content,"bleeckerFileChooserListRow_"+QString::number(folder)));
        auto folderItem=find(content,"bleeckerFileChooserListRow_"+QString::number(folder));
        auto accessible=QAccessible::queryAccessibleInterface(folderItem);QVERIFY(accessible);QCOMPARE(accessible->role(),QAccessible::TreeItem);QVERIFY(accessible->state().focusable);QVERIFY(accessible->state().expandable);QVERIFY(accessible->state().collapsed);
        auto actions=accessible->actionInterface();QVERIFY(actions);QVERIFY(actions->actionNames().contains(QAccessibleActionInterface::toggleAction()));
        actions->doAction(QAccessibleActionInterface::toggleAction());QTRY_VERIFY(listed(listing,"Child.txt")>=0);
        QCOMPARE(table->rowCount(),5);QVERIFY(!QAccessible::accessibleInterface(oldSizeId));
        const auto childCell=table->cellAt(listed(listing,"Child.txt"),0);QVERIFY(childCell&&childCell->attributesInterface());
        QCOMPARE(childCell->attributesInterface()->attributeValue(QAccessible::Attribute::Level).toInt(),2);
        auto expandedItem=find(content,"bleeckerFileChooserListRow_"+QString::number(listed(listing,"Folder")));
        QVERIFY(expandedItem);QVERIFY(QAccessible::queryAccessibleInterface(expandedItem)->state().expanded);
        const auto child=listed(listing,"Child.txt");QTRY_VERIFY(find(content,"bleeckerFileChooserListRow_"+QString::number(child)));
        click(find(content,"bleeckerFileChooserListRow_"+QString::number(child)));
        QTest::keyPress(content->window(),Qt::Key_Control);
        click(find(content,"bleeckerFileChooserListRow_"+QString::number(listed(listing,"Alpha.txt"))),Qt::ControlModifier);
        QTest::keyRelease(content->window(),Qt::Key_Control);QCOMPARE(browser->selectedUrls().size(),2);capture(content->window(),"list-root-and-child");
        selectView("icons");QTRY_COMPARE(browser->selectedUrls().size(),1);QVERIFY(results(fixture).isEmpty());
        auto gridInterface=QAccessible::queryAccessibleInterface(find(content,"bleeckerFileChooserIcons"));QVERIFY(gridInterface&&gridInterface->selectionInterface());
        QVERIFY(gridInterface->state().multiSelectable);QCOMPARE(gridInterface->selectionInterface()->selectedItemCount(),1);
        folder=listed(listing,"Folder");QTRY_VERIFY(find(content,"bleeckerFileChooserIcon_"+QString::number(folder)));
        click(find(content,"bleeckerFileChooserIcon_"+QString::number(folder)));QVERIFY(browser->selectedUrls().isEmpty());QVERIFY(browser->canAccept());
        capture(content->window(),"icons-folder-navigation");click(find(content,"bleeckerFileChooserOpen"));
        QTRY_COMPARE(browser->folderPath(),root.filePath("Folder"));QVERIFY(browser->active());QVERIFY(results(fixture).isEmpty());QVERIFY(!browser->canAccept());
        click(find(content,"bleeckerFileChooserBack"));QTRY_COMPARE(browser->folderPath(),directory.path());QVERIFY(browser->selectedUrls().isEmpty());
        selectView("list");QTRY_VERIFY(listed(listing,"Child.txt")>=0);folder=listed(listing,"Folder");
        click(find(content,"bleeckerFileChooserListRow_"+QString::number(folder)));QTest::keyClick(content->window(),Qt::Key_Left);
        QTRY_COMPARE(listed(listing,"Child.txt"),-1);QTest::keyClick(content->window(),Qt::Key_Right);QTRY_VERIFY(listed(listing,"Child.txt")>=0);
        QTest::keyClick(content->window(),Qt::Key_Down);QCOMPARE(listing->entry(listing->currentIndex())["name"].toString(),QString("Child.txt"));
        QTest::keyClick(content->window(),Qt::Key_Return);QTRY_VERIFY(!browser->active());QCOMPARE(results(fixture).size(),1);
        QCOMPARE(results(fixture)[0].toMap()["urls"].toList(),QVariantList{QUrl::fromLocalFile(root.filePath("Folder/Child.txt"))});
    }
    void removingListOwnerDuringAccessibleAccept(){
        QTemporaryDir directory;QDir root(directory.path());QVERIFY(root.mkdir("Folder"));put(root.filePath("Folder/Child.txt"));
        QQuickView view;QVERIFY(load(view,directory));auto fixture=view.rootObject();fixture->setProperty("removeOnResult",true);
        auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
        QPointer<FileChooserBrowser> browser=control->property("browser").value<FileChooserBrowser*>();
        QPointer<QObject> chooser=control->property("chooser").value<QObject*>();QPointer<FileChooserListing> listing=browser->listing();
        click(control->property("inputItem").value<QQuickItem*>());browser->setViewMode("list");
        auto content=chooser->property("contentItem").value<QQuickItem*>();QTRY_VERIFY(content&&content->window());
        const auto folder=listed(listing,"Folder");QTRY_VERIFY(find(content,"bleeckerFileChooserDisclosure_"+QString::number(folder)));
        click(find(content,"bleeckerFileChooserDisclosure_"+QString::number(folder)));
        const auto child=listed(listing,"Child.txt");QVERIFY(child>=0);QTRY_VERIFY(find(content,"bleeckerFileChooserListRow_"+QString::number(child)));
        click(find(content,"bleeckerFileChooserListRow_"+QString::number(child)));
        auto tree=QAccessible::queryAccessibleInterface(find(content,"bleeckerFileChooserList"));QVERIFY(tree&&tree->tableInterface());
        auto cachedCell=tree->tableInterface()->cellAt(child,1);QVERIFY(cachedCell);const auto cachedId=QAccessible::uniqueId(cachedCell);
        auto open=QAccessible::queryAccessibleInterface(find(content,"bleeckerFileChooserOpen"));QVERIFY(open&&open->actionInterface());
        open->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
        QTRY_VERIFY(browser.isNull());QVERIFY(chooser.isNull());QVERIFY(listing.isNull());QVERIFY(fixture->property("visibleAtCallback").toBool());
        QTRY_VERIFY(!QAccessible::accessibleInterface(cachedId));
        QCOMPARE(results(fixture).size(),1);capture(&view,"list-removed-in-result");
    }
    void actualClicksMultiSelectionCancelAndReopen(){
        QTemporaryDir directory;QDir root(directory.path());put(root.filePath("a.txt"));put(root.filePath("b.txt"));put(root.filePath("photo.png"));
        QQuickView view;QVERIFY(load(view,directory));auto fixture=view.rootObject();QVERIFY(fixture);
        fixture->setProperty("types",QVariantList{QStringLiteral("text/plain")});
        auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
        auto browser=control->property("browser").value<FileChooserBrowser*>();QVERIFY(browser);
        auto chooser=control->property("chooser").value<QObject*>();QVERIFY(chooser);
        auto input=control->property("inputItem").value<QQuickItem*>();QTRY_VERIFY(input);
        capture(&view,"closed");
        click(input);QTRY_VERIFY(browser->active());QTRY_VERIFY(chooser->property("visible").toBool());
        auto content=chooser->property("contentItem").value<QQuickItem*>();QVERIFY(content);QTRY_VERIFY(content->window());
        const auto a=row(browser->modelAt(0),"a.txt"),b=row(browser->modelAt(0),"b.txt"),photo=row(browser->modelAt(0),"photo.png");
        QTRY_VERIFY(find(content,"bleeckerFileChooserRow0_"+QString::number(a)));
        click(find(content,"bleeckerFileChooserRow0_"+QString::number(a)));QCOMPARE(browser->selectedUrls().size(),1);
        click(find(content,"bleeckerFileChooserRow0_"+QString::number(photo)));QCOMPARE(browser->selectedUrls().size(),1);
        QTest::keyPress(content->window(),Qt::Key_Control);
        click(find(content,"bleeckerFileChooserRow0_"+QString::number(b)),Qt::ControlModifier);
        QTest::keyRelease(content->window(),Qt::Key_Control);QCOMPARE(browser->selectedUrls().size(),2);
        capture(content->window(),"multiple-files");
        click(find(content,"bleeckerFileChooserOpen"));QTRY_VERIFY(!browser->active());QCOMPARE(results(fixture).size(),1);
        QVERIFY(fixture->property("visibleAtCallback").toBool());
        const auto value=results(fixture)[0].toMap();QCOMPARE(value["kind"],QVariant("success"));QCOMPARE(value["urls"].toList().size(),2);
        QTRY_VERIFY(input->hasActiveFocus());
        click(input);QTRY_VERIFY(browser->active());QTRY_VERIFY(chooser->property("visible").toBool());
        QTRY_VERIFY(content->window());click(find(content,"bleeckerFileChooserCancel"));QTRY_VERIFY(!browser->active());QCOMPARE(results(fixture).size(),1);
        QTRY_VERIFY(input->hasActiveFocus());QTest::keyClick(&view,Qt::Key_Space);
        QTRY_VERIFY(browser->active());QTRY_VERIFY(content->window());
        QTest::keyClick(content->window(),Qt::Key_Escape);QTRY_VERIFY(!browser->active());QCOMPARE(results(fixture).size(),1);
        QTRY_VERIFY(input->hasActiveFocus());
    }
    void actualColumnNavigationAndCallbackRemoval(){
        QTemporaryDir directory;QDir root(directory.path());QVERIFY(root.mkdir("folder"));put(root.filePath("folder/child.txt"));
        QQuickView view;QVERIFY(load(view,directory));auto fixture=view.rootObject();fixture->setProperty("removeOnResult",true);
        auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
        QPointer<FileChooserBrowser> browser=control->property("browser").value<FileChooserBrowser*>();QVERIFY(browser);
        QPointer<QObject> chooser=control->property("chooser").value<QObject*>();
        click(control->property("inputItem").value<QQuickItem*>());QTRY_VERIFY(browser->active());
        auto content=chooser->property("contentItem").value<QQuickItem*>();QTRY_VERIFY(content&&content->window());
        const auto folder=row(browser->modelAt(0),"folder");QTRY_VERIFY(find(content,"bleeckerFileChooserRow0_"+QString::number(folder)));
        click(find(content,"bleeckerFileChooserRow0_"+QString::number(folder)));QTRY_COMPARE(browser->count(),2);QVERIFY(!browser->canAccept());
        capture(content->window(),"directory-columns");
        QTRY_VERIFY(find(content,"bleeckerFileChooserRow1_0"));click(find(content,"bleeckerFileChooserRow1_0"));QVERIFY(browser->canAccept());
        auto open=find(content,"bleeckerFileChooserOpen");QVERIFY(open);
        auto accessible=QAccessible::queryAccessibleInterface(open);QVERIFY(accessible);QCOMPARE(accessible->role(),QAccessible::Button);QCOMPARE(accessible->text(QAccessible::Name),QString("Open"));
        click(open);QTRY_COMPARE(results(fixture).size(),1);QVERIFY(fixture->property("visibleAtCallback").toBool());
        QTRY_VERIFY(browser.isNull());QTRY_VERIFY(chooser.isNull());QVERIFY(!fixture->findChild<QQuickItem*>("fileInput"));
        capture(&view,"removed-in-result");
    }
    void accessibleRowsSelectThroughTheChooser(){
        QTemporaryDir directory;QDir root(directory.path());put(root.filePath("one.txt"));put(root.filePath("photo.png"));
        QQuickView view;QVERIFY(load(view,directory));auto fixture=view.rootObject();auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
        auto browser=control->property("browser").value<FileChooserBrowser*>();auto chooser=control->property("chooser").value<QObject*>();
        click(control->property("inputItem").value<QQuickItem*>());QTRY_VERIFY(browser->active());
        auto content=chooser->property("contentItem").value<QQuickItem*>();QTRY_VERIFY(content&&content->window());
        auto files=find(content,"bleeckerFileChooserColumn0");QVERIFY(files);
        auto list=QAccessible::queryAccessibleInterface(files);QVERIFY(list);QCOMPARE(list->role(),QAccessible::List);QVERIFY(list->state().focusable);
        auto one=find(content,"bleeckerFileChooserRow0_"+QString::number(row(browser->modelAt(0),"one.txt")));QVERIFY(one);
        auto item=QAccessible::queryAccessibleInterface(one);QVERIFY(item);QCOMPARE(item->role(),QAccessible::ListItem);
        QVERIFY(item->state().focusable);QVERIFY(item->state().selectable);QVERIFY(!item->state().selected);
        auto action=item->actionInterface();QVERIFY(action);QVERIFY(action->actionNames().contains(QAccessibleActionInterface::pressAction()));
        action->doAction(QAccessibleActionInterface::pressAction());QTRY_VERIFY(item->state().selected);QVERIFY(browser->canAccept());
        QCOMPARE(browser->selectedUrls(),QVariantList{QUrl::fromLocalFile(root.filePath("one.txt"))});
        auto photo=find(content,"bleeckerFileChooserRow0_"+QString::number(row(browser->modelAt(0),"photo.png")));QVERIFY(photo);
        auto unavailable=QAccessible::queryAccessibleInterface(photo);QVERIFY(unavailable);
        QVERIFY(!unavailable->state().focusable);QVERIFY(!unavailable->state().selectable);
        QCOMPARE(unavailable->text(QAccessible::Description),QString("Unavailable for selected file types"));
        auto accept=QAccessible::queryAccessibleInterface(find(content,"bleeckerFileChooserOpen"));QVERIFY(accept&&accept->actionInterface());
        accept->actionInterface()->doAction(QAccessibleActionInterface::pressAction());QTRY_COMPARE(results(fixture).size(),1);QVERIFY(!browser->active());
        QCOMPARE(results(fixture)[0].toMap()["urls"].toList(),QVariantList{QUrl::fromLocalFile(root.filePath("one.txt"))});
    }
    void actualGoToInvalidCancelClearSuggestionsAndPathSelectedFile(){
        FileInputAnnouncementCapture announcements;
        QTemporaryDir directory;QDir root(directory.path());put(root.filePath("one.txt"));put(root.filePath("Other.png"));
        QVERIFY(root.mkpath("Alpha/Child"));QVERIFY(root.mkdir("Alphabet"));QVERIFY(root.mkdir("Alpine"));
        QQuickView view;QVERIFY(load(view,directory));auto fixture=view.rootObject();auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
        auto browser=control->property("browser").value<FileChooserBrowser*>();auto chooser=control->property("chooser").value<QObject*>();
        click(control->property("inputItem").value<QQuickItem*>());QTRY_VERIFY(browser->active());
        auto content=chooser->property("contentItem").value<QQuickItem*>();QTRY_VERIFY(content&&content->window());
        auto prompt=chooser->property("goToDialog").value<QObject*>();QVERIFY(prompt);auto path=chooser->property("pathInput").value<QQuickItem*>();QVERIFY(path);
        auto suggestions=prompt->property("suggestions").value<FileChooserPaths*>();QVERIFY(suggestions);
        click(find(content,"bleeckerFileChooserRow0_"+QString::number(row(browser->modelAt(0),"one.txt"))));const auto before=browser->selectedUrls();
        QTest::keyClick(content->window(),Qt::Key_G,Qt::ControlModifier|Qt::ShiftModifier);QTRY_VERIFY(prompt->property("visible").toBool());QTRY_VERIFY(path->hasActiveFocus());
        QVERIFY(path->window()!=content->window());auto promptContent=prompt->property("contentItem").value<QQuickItem*>();QVERIFY(promptContent);
        auto accessible=QAccessible::queryAccessibleInterface(promptContent->parentItem());QVERIFY(accessible);QCOMPARE(accessible->role(),QAccessible::Dialog);QCOMPARE(accessible->text(QAccessible::Name),QString("Go to Folder"));QVERIFY(accessible->state().modal);
        auto outer=QAccessible::queryAccessibleInterface(content->parentItem());QVERIFY(outer);QAccessibleInterface *reachable=nullptr;
        for(int i=0;i<outer->childCount();++i)if(auto child=outer->child(i);child&&child->object()==accessible->object())reachable=child;
        QVERIFY2(reachable,"The nested GoTo window must remain reachable through its owning dialog");QCOMPARE(reachable->parent()->object(),outer->object());QVERIFY(outer->indexOfChild(reachable)>=0);
        auto enter=[&](const QString &text){QTest::keyClick(path->window(),Qt::Key_A,Qt::ControlModifier);typeText(path->window(),text);};
        enter(root.filePath("missing"));QCOMPARE(path->property("text").toString(),root.filePath("missing"));QTest::keyClick(path->window(),Qt::Key_Return);
        QVERIFY(prompt->property("visible").toBool());QCOMPARE(browser->selectedUrls(),before);QCOMPARE(browser->folderPath(),directory.path());QVERIFY(browser->error().isEmpty());QVERIFY(results(fixture).isEmpty());QVERIFY(announcements.messages.isEmpty());
        capture(path->window(),"go-to-missing");QTest::keyClick(path->window(),Qt::Key_Escape);QTRY_VERIFY(!prompt->property("visible").toBool());QVERIFY(browser->active());QCOMPARE(browser->selectedUrls(),before);
        QTRY_VERIFY(find(content,"bleeckerFileChooserColumn0")->hasActiveFocus());
        QTRY_VERIFY(find(content,"bleeckerFileChooserColumn0")->hasActiveFocus());
        QTest::keyClick(content->window(),Qt::Key_L,Qt::ControlModifier);QTRY_VERIFY(prompt->property("visible").toBool());QCOMPARE(path->property("text").toString(),directory.path());
        click(find(promptContent,"bleeckerFileChooserGoToClear"));QVERIFY(prompt->property("visible").toBool());QVERIFY(path->property("text").toString().isEmpty());
        click(find(promptContent,"bleeckerFileChooserGoToClear"));QTRY_VERIFY(!prompt->property("visible").toBool());QVERIFY(browser->active());QCOMPARE(browser->selectedUrls(),before);
        QTRY_VERIFY(find(content,"bleeckerFileChooserColumn0")->hasActiveFocus());
        QTest::keyClick(content->window(),Qt::Key_L,Qt::ControlModifier);QTRY_VERIFY(prompt->property("visible").toBool());
        const auto prefix=root.filePath("Al");enter(prefix);QTRY_COMPARE(suggestions->entries().size(),4);QTRY_VERIFY(!find(promptContent,"bleeckerFileChooserGoToScrollBar")->isVisible());capture(path->window(),"go-to-prefix");
        QTest::keyClick(path->window(),Qt::Key_Tab);QCOMPARE(path->property("text").toString(),prefix+"p");
        enter(prefix);QTest::keyClick(path->window(),Qt::Key_Down);QCOMPARE(suggestions->selectedUrl(),QUrl::fromLocalFile(root.filePath("Alpine")));QCOMPARE(path->property("text").toString(),prefix);
        QTest::keyClick(path->window(),Qt::Key_Return);QTRY_VERIFY(!prompt->property("visible").toBool());QCOMPARE(browser->folderPath(),root.filePath("Alpine"));QVERIFY(results(fixture).isEmpty());
        QCOMPARE(browser->places()->lastPathInput(),prefix);QCOMPARE(browser->places()->pathTargets().first().toMap()["url"].toUrl(),QUrl::fromLocalFile(root.filePath("Alpine")));
        for(const auto &value:browser->places()->entries())QVERIFY(!value.toMap()["recent"].toBool());
        QTRY_VERIFY(find(content,"bleeckerFileChooserColumn0")->hasActiveFocus());
        QTest::keyClick(content->window(),Qt::Key_L,Qt::ControlModifier);QTRY_VERIFY(prompt->property("visible").toBool());QCOMPARE(path->property("text").toString(),prefix);
        enter(root.filePath("Other.png"));capture(path->window(),"go-to-file-proposal");QTest::keyClick(path->window(),Qt::Key_Return);QTRY_VERIFY(!prompt->property("visible").toBool());
        QCOMPARE(browser->selectedUrls(),QVariantList{QUrl::fromLocalFile(root.filePath("Other.png"))});QVERIFY(browser->canAccept());QVERIFY(results(fixture).isEmpty());
        QVERIFY(!browser->modelAt(0)->entry(row(browser->modelAt(0),"Other.png"))["eligible"].toBool());capture(content->window(),"go-to-file-selected");
        click(find(content,"bleeckerFileChooserOpen"));QTRY_COMPARE(results(fixture).size(),1);QVERIFY(!browser->active());QVERIFY(fixture->property("visibleAtCallback").toBool());
        QCOMPARE(results(fixture)[0].toMap()["urls"].toList(),QVariantList{QUrl::fromLocalFile(root.filePath("Other.png"))});
    }
    void actualGoToAccessibleTextEditingUpdatesSuggestionsAndKeepsUndo(){
        QTemporaryDir directory;QDir root(directory.path());QVERIFY(root.mkdir("Alpha"));QVERIFY(root.mkdir(QString::fromUtf8("Café")));
        QQuickView view;QVERIFY(load(view,directory));auto fixture=view.rootObject();auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
        auto browser=control->property("browser").value<FileChooserBrowser*>();auto chooser=control->property("chooser").value<QObject*>();
        click(control->property("inputItem").value<QQuickItem*>());QTRY_VERIFY(browser->active());
        auto content=chooser->property("contentItem").value<QQuickItem*>();QTest::keyClick(content->window(),Qt::Key_L,Qt::ControlModifier);
        auto prompt=chooser->property("goToDialog").value<QObject*>();QTRY_VERIFY(prompt->property("visible").toBool());
        auto path=chooser->property("pathInput").value<QQuickItem*>();auto suggestions=prompt->property("suggestions").value<FileChooserPaths*>();QVERIFY(path&&suggestions);
        auto accessible=QAccessible::queryAccessibleInterface(path);QVERIFY(accessible&&accessible->textInterface()&&accessible->editableTextInterface());
        auto editable=accessible->editableTextInterface();auto text=accessible->textInterface();const auto prefix=root.filePath("Al");
        editable->replaceText(0,text->characterCount(),prefix);QTRY_COMPARE(suggestions->input(),prefix);QCOMPARE(suggestions->selectedUrl(),QUrl::fromLocalFile(root.filePath("Alpha")));
        QTest::keyClick(path->window(),Qt::Key_Z,Qt::ControlModifier);QTRY_COMPARE(suggestions->input(),directory.path());
        QTest::keyClick(path->window(),Qt::Key_Z,Qt::ControlModifier|Qt::ShiftModifier);QTRY_COMPARE(suggestions->input(),prefix);
        editable->insertText(text->characterCount(),"p");QTRY_COMPARE(suggestions->input(),prefix+"p");
        editable->deleteText(prefix.size(),prefix.size()+1);QTRY_COMPARE(suggestions->input(),prefix);
        editable->replaceText(-1,1,"invalid");editable->deleteText(0,text->characterCount()+1);editable->insertText(text->characterCount()+1,"invalid");QCOMPARE(suggestions->input(),prefix);
        path->setProperty("readOnly",true);editable->replaceText(0,text->characterCount(),"blocked");QCOMPARE(suggestions->input(),prefix);path->setProperty("readOnly",false);
        path->setEnabled(false);editable->replaceText(0,text->characterCount(),"blocked");QCOMPARE(suggestions->input(),prefix);path->setEnabled(true);
        capture(path->window(),"go-to-accessible-prefix");
        const auto unicode=root.filePath(QString::fromUtf8("Café"));editable->replaceText(0,text->characterCount(),unicode);
        QTRY_COMPARE(suggestions->input(),unicode);QCOMPARE(text->text(0,text->characterCount()),unicode);QCOMPARE(suggestions->selectedUrl(),QUrl::fromLocalFile(unicode));
        QVERIFY(results(fixture).isEmpty());QCOMPARE(browser->folderPath(),directory.path());
        path->forceActiveFocus();QTest::keyClick(path->window(),Qt::Key_Return);QTRY_VERIFY(!prompt->property("visible").toBool());QCOMPARE(browser->folderPath(),unicode);QVERIFY(results(fixture).isEmpty());
        click(find(content,"bleeckerFileChooserCancel"));QTRY_VERIFY(!browser->active());QVERIFY(results(fixture).isEmpty());
    }
    void actualGoToAccessibleSelectionEventsKeepTextFocusAndRespectSingleChoice(){
        FileInputSelectionCapture events;QTemporaryDir directory;QDir root(directory.path());
        for(const auto name:{"Alpha","Alphabet","Alpine"})QVERIFY(root.mkdir(name));
        QQuickView view;QVERIFY(load(view,directory));auto fixture=view.rootObject();auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
        auto browser=control->property("browser").value<FileChooserBrowser*>();auto chooser=control->property("chooser").value<QObject*>();
        click(control->property("inputItem").value<QQuickItem*>());auto content=chooser->property("contentItem").value<QQuickItem*>();
        QTest::keyClick(content->window(),Qt::Key_L,Qt::ControlModifier);auto prompt=chooser->property("goToDialog").value<QObject*>();QTRY_VERIFY(prompt->property("visible").toBool());
        auto path=chooser->property("pathInput").value<QQuickItem*>();auto suggestions=prompt->property("suggestions").value<FileChooserPaths*>();
        auto list=find(prompt->property("contentItem").value<QQuickItem*>(),"bleeckerFileChooserGoToTargets");QVERIFY(list);
        auto accessible=QAccessible::queryAccessibleInterface(list);QVERIFY(accessible&&accessible->selectionInterface());auto selection=accessible->selectionInterface();
        auto text=QAccessible::queryAccessibleInterface(path);QVERIFY(text&&text->editableTextInterface());const auto prefix=root.filePath("Al");
        text->editableTextInterface()->replaceText(0,text->textInterface()->characterCount(),prefix);
        auto choice=[&](const QString &name)->QAccessibleInterface*{for(int i=0;i<accessible->childCount();++i)if(auto child=accessible->child(i);child&&child->text(QAccessible::Name)==name)return child;return nullptr;};
        QTRY_VERIFY(choice(root.filePath("Alpha")));QTRY_VERIFY(FileInputSelectionCapture::saw(QAccessible::Selection,root.filePath("Alpha"),true));
        QCOMPARE(selection->selectedItemCount(),1);QCOMPARE(selection->selectedItem(0)->text(QAccessible::Name),root.filePath("Alpha"));
        FileInputSelectionCapture::events.clear();QTest::keyClick(path->window(),Qt::Key_Down);
        QTRY_VERIFY(FileInputSelectionCapture::saw(QAccessible::Selection,root.filePath("Alpine"),true));
        QVERIFY(FileInputSelectionCapture::saw(QAccessible::SelectionRemove,root.filePath("Alpha"),false));
        QCOMPARE(selection->selectedItem(0)->text(QAccessible::Name),root.filePath("Alpine"));QCOMPARE(path->property("text").toString(),prefix);QVERIFY(path->hasActiveFocus());
        QVERIFY(selection->select(choice(root.filePath("Alphabet"))));QTRY_VERIFY(FileInputSelectionCapture::saw(QAccessible::Selection,root.filePath("Alphabet"),true));
        QCOMPARE(selection->selectedItemCount(),1);QCOMPARE(selection->selectedItem(0)->text(QAccessible::Name),root.filePath("Alphabet"));
        QVERIFY(!selection->select(choice("Go to:")));QVERIFY(!selection->selectAll());QVERIFY(!selection->clear());QVERIFY(!selection->unselect(selection->selectedItem(0)));
        QCOMPARE(path->property("text").toString(),prefix);QVERIFY(path->hasActiveFocus());QVERIFY(results(fixture).isEmpty());capture(path->window(),"go-to-accessible-selection");
        FileInputSelectionCapture::events.clear();auto clear=QAccessible::queryAccessibleInterface(find(prompt->property("contentItem").value<QQuickItem*>(),"bleeckerFileChooserGoToClear"));QVERIFY(clear&&clear->actionInterface());
        clear->actionInterface()->doAction(QAccessibleActionInterface::pressAction());QTRY_COMPARE(selection->selectedItemCount(),0);QVERIFY(selection->clear());QTRY_VERIFY(FileInputSelectionCapture::focusFollowsClearedSuggestions());
        QTest::keyClick(path->window(),Qt::Key_Escape);QTRY_VERIFY(!prompt->property("visible").toBool());FileInputSelectionCapture::events.clear();
        suggestions->setInput(prefix);QTest::qWait(30);QCOMPARE(FileInputSelectionCapture::suggestionEvents(),0);
        QTRY_VERIFY(find(content,"bleeckerFileChooserColumn0")->hasActiveFocus());QTest::keyClick(content->window(),Qt::Key_L,Qt::ControlModifier);QTRY_VERIFY(prompt->property("visible").toBool());
        text->editableTextInterface()->replaceText(0,text->textInterface()->characterCount(),prefix);QTRY_VERIFY(choice(root.filePath("Alphabet")));QVERIFY(selection->select(choice(root.filePath("Alphabet"))));
        QTest::keyClick(path->window(),Qt::Key_Return);QTRY_VERIFY(!prompt->property("visible").toBool());QCOMPARE(browser->folderPath(),root.filePath("Alphabet"));QVERIFY(results(fixture).isEmpty());
        click(find(content,"bleeckerFileChooserCancel"));QTRY_VERIFY(!browser->active());QVERIFY(results(fixture).isEmpty());
    }
    void closingGoToDuringSelectionNotificationKeepsOwner(){
        FileInputSelectionCapture events;QTemporaryDir directory;QDir root(directory.path());QVERIFY(root.mkdir("Alpha"));QVERIFY(root.mkdir("Alpine"));
        QQuickView view;QVERIFY(load(view,directory));auto fixture=view.rootObject();auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
        auto browser=control->property("browser").value<FileChooserBrowser*>();auto chooser=control->property("chooser").value<QObject*>();click(control->property("inputItem").value<QQuickItem*>());auto content=chooser->property("contentItem").value<QQuickItem*>();
        QTest::keyClick(content->window(),Qt::Key_L,Qt::ControlModifier);auto prompt=chooser->property("goToDialog").value<QObject*>();QTRY_VERIFY(prompt->property("visible").toBool());
        auto path=chooser->property("pathInput").value<QQuickItem*>();auto suggestions=prompt->property("suggestions").value<FileChooserPaths*>();
        auto text=QAccessible::queryAccessibleInterface(path);QVERIFY(text&&text->editableTextInterface());text->editableTextInterface()->replaceText(0,text->textInterface()->characterCount(),root.filePath("Al"));
        QTRY_VERIFY(FileInputSelectionCapture::saw(QAccessible::Selection,root.filePath("Alpha"),true));FileInputSelectionCapture::events.clear();bool closed=false;
        FileInputSelectionCapture::callback=[&](QAccessibleEvent *event){if(!closed&&event->type()==QAccessible::SelectionRemove&&event->object()&&event->object()->objectName().startsWith("bleeckerFileChooserGoToTarget_")){closed=true;QMetaObject::invokeMethod(prompt,"close");}};
        suggestions->select(2);QTRY_VERIFY(closed);QTRY_VERIFY(!prompt->property("visible").toBool());QTest::qWait(30);
        QVERIFY(!FileInputSelectionCapture::saw(QAccessible::Selection,root.filePath("Alpine"),true));QVERIFY(browser->active());QVERIFY(results(fixture).isEmpty());
        click(find(content,"bleeckerFileChooserCancel"));QTRY_VERIFY(!browser->active());
    }
    void removingGoToOwnerDuringSelectionNotification(){
        FileInputSelectionCapture events;QTemporaryDir directory;QDir root(directory.path());QVERIFY(root.mkdir("Alpha"));QVERIFY(root.mkdir("Alpine"));
        QQuickView view;QVERIFY(load(view,directory));auto fixture=view.rootObject();auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
        auto chooser=control->property("chooser").value<QObject*>();click(control->property("inputItem").value<QQuickItem*>());auto content=chooser->property("contentItem").value<QQuickItem*>();
        QTest::keyClick(content->window(),Qt::Key_L,Qt::ControlModifier);QPointer<QObject> prompt=chooser->property("goToDialog").value<QObject*>();QTRY_VERIFY(prompt->property("visible").toBool());
        auto path=chooser->property("pathInput").value<QQuickItem*>();auto suggestions=prompt->property("suggestions").value<FileChooserPaths*>();
        QPointer<QQuickItem> list=find(prompt->property("contentItem").value<QQuickItem*>(),"bleeckerFileChooserGoToTargets");
        auto text=QAccessible::queryAccessibleInterface(path);QVERIFY(text&&text->editableTextInterface());text->editableTextInterface()->replaceText(0,text->textInterface()->characterCount(),root.filePath("Al"));
        QTRY_VERIFY(FileInputSelectionCapture::saw(QAccessible::Selection,root.filePath("Alpha"),true));bool removed=false;
        FileInputSelectionCapture::callback=[&](QAccessibleEvent *event){if(!removed&&event->type()==QAccessible::SelectionRemove&&event->object()&&event->object()->objectName().startsWith("bleeckerFileChooserGoToTarget_")){removed=true;fixture->setProperty("mounted",false);}};
        suggestions->select(2);QTRY_VERIFY(removed);QTRY_VERIFY(prompt.isNull());QTRY_VERIFY(list.isNull());QVERIFY(results(fixture).isEmpty());
    }
    void removingOwnerClosesGoToWindow(){
        QTemporaryDir directory;QQuickView view;QVERIFY(load(view,directory));auto fixture=view.rootObject();auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
        auto chooser=control->property("chooser").value<QObject*>();click(control->property("inputItem").value<QQuickItem*>());QTRY_VERIFY(chooser->property("visible").toBool());
        auto content=chooser->property("contentItem").value<QQuickItem*>();QPointer<QObject> prompt=chooser->property("goToDialog").value<QObject*>();QVERIFY(prompt);
        QTest::keyClick(content->window(),Qt::Key_G,Qt::ControlModifier|Qt::ShiftModifier);QTRY_VERIFY(prompt->property("visible").toBool());
        QPointer<QQuickWindow> popup=chooser->property("pathInput").value<QQuickItem*>()->window();
        fixture->setProperty("mounted",false);QTRY_VERIFY(prompt.isNull());QTRY_VERIFY(popup.isNull()||!popup->isVisible());QVERIFY(results(fixture).isEmpty());
    }
    void initialLocationErrorAndClosedAnnouncement(){
        FileInputAnnouncementCapture announcements;QTemporaryDir directory;
        QQuickView view;QVERIFY(load(view,directory));auto fixture=view.rootObject();
        const auto missing=QUrl::fromLocalFile(directory.path()+"/missing");fixture->setProperty("fixtureRoot",missing);
        auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
        auto browser=control->property("browser").value<FileChooserBrowser*>();QVERIFY(browser);
        click(control->property("inputItem").value<QQuickItem*>());QTRY_VERIFY(browser->active());
        QTRY_COMPARE(announcements.messages.size(),1);QCOMPARE(announcements.messages[0].text,browser->error());
        QVERIFY(browser->navigatePath(directory.path()));QVERIFY(browser->error().isEmpty());
        QVERIFY(!browser->navigatePath(missing.toLocalFile()));browser->cancel();QTest::qWait(30);
        QCOMPARE(announcements.messages.size(),1);
        click(control->property("inputItem").value<QQuickItem*>());QTRY_VERIFY(browser->active());
        QTRY_COMPARE(announcements.messages.size(),2);QCOMPARE(announcements.messages[1].text,browser->error());
        QVERIFY(results(fixture).isEmpty());
    }
    void actualNewFolderValidationNestedEscapeAndHistory(){
        QTemporaryDir directory;QDir root(directory.path());QVERIFY(root.mkdir("untitled folder"));put(root.filePath("one.txt"));
        QQuickView view;QVERIFY(load(view,directory));auto fixture=view.rootObject();auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
        auto browser=control->property("browser").value<FileChooserBrowser*>();auto chooser=control->property("chooser").value<QObject*>();
        click(control->property("inputItem").value<QQuickItem*>());QTRY_VERIFY(browser->active());
        auto content=chooser->property("contentItem").value<QQuickItem*>();QTRY_VERIFY(content&&content->window());
        auto prompt=chooser->property("newFolderDialog").value<QObject*>();QVERIFY(prompt);
        auto outer=QAccessible::queryAccessibleInterface(content->parentItem());QVERIFY(outer);QCOMPARE(outer->role(),QAccessible::Dialog);QCOMPARE(outer->text(QAccessible::Name),QString("Open"));QVERIFY(outer->state().modal);
        click(find(content,"bleeckerFileChooserRow0_"+QString::number(row(browser->modelAt(0),"one.txt"))));QCOMPARE(browser->selectedUrls().size(),1);
        click(find(content,"bleeckerFileChooserNewFolder"));QTRY_VERIFY(prompt->property("visible").toBool());
        auto promptContent=prompt->property("contentItem").value<QQuickItem*>();QVERIFY(promptContent);
        auto modal=QAccessible::queryAccessibleInterface(promptContent->parentItem());QVERIFY(modal);QCOMPARE(modal->role(),QAccessible::Dialog);QCOMPARE(modal->text(QAccessible::Name),QString("New Folder"));QVERIFY(modal->state().modal);
        auto name=prompt->property("nameInput").value<QQuickItem*>();auto create=prompt->property("createInput").value<QQuickItem*>();QVERIFY(name&&create);
        QCOMPARE(name->property("text").toString(),QString("untitled folder 2"));QVERIFY(name->hasActiveFocus());QVERIFY(create->isEnabled());
        typeText(name->window(),"one.txt");QTRY_VERIFY(!create->isEnabled());QCOMPARE(prompt->property("error").toString(),QString("This name is already taken."));
        capture(content->window(),"new-folder-conflict");
        QTest::keyClick(name->window(),Qt::Key_A,Qt::ControlModifier);QTest::keyClick(name->window(),Qt::Key_Backspace);QVERIFY(!create->isEnabled());
        QTest::keyClick(name->window(),Qt::Key_Escape);QTRY_VERIFY(!prompt->property("visible").toBool());QVERIFY(browser->active());QVERIFY(results(fixture).isEmpty());
        QVERIFY(!QFileInfo(root.filePath("untitled folder 2")).exists());
        QTRY_VERIFY(find(content,"bleeckerFileChooserColumn0")->hasActiveFocus());
        QTest::keyClick(content->window(),Qt::Key_N,Qt::ControlModifier|Qt::ShiftModifier);QTRY_VERIFY(prompt->property("visible").toBool());
        typeText(name->window(),"Created by Qt");QVERIFY(create->isEnabled());
        auto accessible=QAccessible::queryAccessibleInterface(create);QVERIFY(accessible&&accessible->actionInterface());
        QCOMPARE(accessible->text(QAccessible::Name),QString("Create"));accessible->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
        QTRY_VERIFY(!prompt->property("visible").toBool());QCOMPARE(browser->folderPath(),root.filePath("Created by Qt"));QVERIFY(QFileInfo(browser->folderPath()).isDir());QVERIFY(browser->active());QVERIFY(!browser->canAccept());QVERIFY(results(fixture).isEmpty());
        auto createdRow=find(content,"bleeckerFileChooserRow0_"+QString::number(row(browser->modelAt(0),"Created by Qt")));QVERIFY(createdRow);
        auto createdNavigation=QAccessible::queryAccessibleInterface(createdRow);QVERIFY(createdNavigation);QTRY_VERIFY(createdNavigation->state().selected);
        capture(content->window(),"new-folder-created");
        click(find(content,"bleeckerFileChooserBack"));QCOMPARE(browser->folderPath(),directory.path());QVERIFY(browser->canGoForward());QVERIFY(browser->selectedUrls().isEmpty());QVERIFY(!browser->canAccept());
        click(find(content,"bleeckerFileChooserForward"));QCOMPARE(browser->folderPath(),root.filePath("Created by Qt"));
        click(find(content,"bleeckerFileChooserCancel"));QTRY_VERIFY(!browser->active());QVERIFY(results(fixture).isEmpty());
    }
    void removingOwnerClosesNestedFolderPrompt(){
        QTemporaryDir directory;QQuickView view;QVERIFY(load(view,directory));auto fixture=view.rootObject();auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
        QPointer<FileChooserBrowser> browser=control->property("browser").value<FileChooserBrowser*>();
        QPointer<QObject> chooser=control->property("chooser").value<QObject*>();
        click(control->property("inputItem").value<QQuickItem*>());QTRY_VERIFY(browser->active());
        auto content=chooser->property("contentItem").value<QQuickItem*>();QTRY_VERIFY(content&&content->window());
        QPointer<QObject> prompt=chooser->property("newFolderDialog").value<QObject*>();QVERIFY(prompt);
        click(find(content,"bleeckerFileChooserNewFolder"));QTRY_VERIFY(prompt->property("visible").toBool());
        fixture->setProperty("mounted",false);QTRY_VERIFY(browser.isNull());QTRY_VERIFY(chooser.isNull());QTRY_VERIFY(prompt.isNull());QVERIFY(results(fixture).isEmpty());
        QVERIFY(QDir(directory.path()).entryList(QDir::NoDotAndDotDot|QDir::AllEntries).isEmpty());
    }
    void actualBackClearsSelectionAndStartsFreshShiftRange(){
        QTemporaryDir directory;QDir root(directory.path());QVERIFY(root.mkdir("folder"));
        for(const auto &name:{"a.txt","b.txt","c.txt"})put(root.filePath(name));
        QQuickView view;QVERIFY(load(view,directory));auto fixture=view.rootObject();auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
        auto browser=control->property("browser").value<FileChooserBrowser*>();auto chooser=control->property("chooser").value<QObject*>();
        click(control->property("inputItem").value<QQuickItem*>());QTRY_VERIFY(browser->active());
        auto content=chooser->property("contentItem").value<QQuickItem*>();QTRY_VERIFY(content&&content->window());
        click(find(content,"bleeckerFileChooserRow0_"+QString::number(row(browser->modelAt(0),"b.txt"))));
        click(find(content,"bleeckerFileChooserRow0_"+QString::number(row(browser->modelAt(0),"folder"))));QCOMPARE(browser->count(),2);
        auto folder=find(content,"bleeckerFileChooserRow0_"+QString::number(row(browser->modelAt(0),"folder")));QVERIFY(folder);
        auto navigation=QAccessible::queryAccessibleInterface(folder);QVERIFY(navigation&&navigation->state().selected&&navigation->state().selectable);QVERIFY(!browser->canAccept());
        click(find(content,"bleeckerFileChooserBack"));QVERIFY(browser->selectedUrls().isEmpty());QVERIFY(!browser->canAccept());
        QTest::keyPress(content->window(),Qt::Key_Shift);
        click(find(content,"bleeckerFileChooserRow0_"+QString::number(row(browser->modelAt(0),"c.txt"))),Qt::ShiftModifier);
        QTest::keyRelease(content->window(),Qt::Key_Shift);
        QCOMPARE(browser->selectedUrls(),(QVariantList{QUrl::fromLocalFile(root.filePath("a.txt")),QUrl::fromLocalFile(root.filePath("b.txt")),QUrl::fromLocalFile(root.filePath("c.txt"))}));
        capture(content->window(),"history-cleared-then-shift-range");
    }
    void directoryFilterKeepsReturnInsideNewFolderPrompt(){
        QTemporaryDir directory;QQuickView view;QVERIFY(load(view,directory));auto fixture=view.rootObject();fixture->setProperty("types",QVariantList{QStringLiteral("inode/directory")});
        auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);auto browser=control->property("browser").value<FileChooserBrowser*>();auto chooser=control->property("chooser").value<QObject*>();
        click(control->property("inputItem").value<QQuickItem*>());QTRY_VERIFY(browser->active());QVERIFY(browser->canAccept());
        auto content=chooser->property("contentItem").value<QQuickItem*>();QTRY_VERIFY(content&&content->window());
        auto prompt=chooser->property("newFolderDialog").value<QObject*>();QVERIFY(prompt);click(find(content,"bleeckerFileChooserNewFolder"));QTRY_VERIFY(prompt->property("visible").toBool());
        auto name=prompt->property("nameInput").value<QQuickItem*>();QVERIFY(name);
        QTest::keyClick(name->window(),Qt::Key_Backspace);QTest::keyClick(name->window(),Qt::Key_Return);QTest::qWait(30);
        QVERIFY(prompt->property("visible").toBool());QVERIFY(results(fixture).isEmpty());QVERIFY(browser->active());
        typeText(name->window(),"created");QTest::keyClick(name->window(),Qt::Key_Return);QTRY_VERIFY(!prompt->property("visible").toBool());
        QVERIFY(browser->active());QVERIFY(browser->canAccept());QVERIFY(results(fixture).isEmpty());QCOMPARE(browser->folderPath(),directory.path()+"/created");
        click(find(content,"bleeckerFileChooserOpen"));QTRY_COMPARE(results(fixture).size(),1);QVERIFY(fixture->property("visibleAtCallback").toBool());
        QCOMPARE(results(fixture)[0].toMap()["urls"].toList(),QVariantList{QUrl::fromLocalFile(directory.path()+"/created/")});
    }
    void typedCustomEmptyAndMixedFiltersReachActualControls(){
        QTemporaryDir directory;QDir root(directory.path());put(root.filePath("one.txt"));QVERIFY(root.mkdir("folder"));
        QQuickView view;QVERIFY(load(view,directory));auto fixture=view.rootObject();
        fixture->setProperty("types",QVariantList{QVariantMap{{"identifier",QStringLiteral("org.avelino.fixture")},{"filenameExtensions",QVariantList{}}}});
        auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
        auto browser=control->property("browser").value<FileChooserBrowser*>();auto chooser=control->property("chooser").value<QObject*>();
        click(control->property("inputItem").value<QQuickItem*>());QTRY_VERIFY(browser->active());
        auto content=chooser->property("contentItem").value<QQuickItem*>();QTRY_VERIFY(content&&content->window());
        QVERIFY(browser->error().isEmpty());QVERIFY(browser->modelAt(0)->canChooseFiles());QVERIFY(!browser->canAccept());
        click(find(content,"bleeckerFileChooserRow0_"+QString::number(row(browser->modelAt(0),"one.txt"))));QVERIFY(browser->selectedUrls().isEmpty());
        fixture->setProperty("types",QVariantList{});QVERIFY(!browser->modelAt(0)->canChooseFiles());QVERIFY(!browser->modelAt(0)->canChooseDirectories());QVERIFY(!browser->canAccept());
        fixture->setProperty("types",QVariantList{QStringLiteral("inode/directory"),QStringLiteral("text/plain")});
        QVERIFY(browser->modelAt(0)->canChooseFiles());QVERIFY(browser->modelAt(0)->canChooseDirectories());
        click(find(content,"bleeckerFileChooserRow0_"+QString::number(row(browser->modelAt(0),"one.txt"))));
        QTest::keyPress(content->window(),Qt::Key_Control);
        click(find(content,"bleeckerFileChooserRow0_"+QString::number(row(browser->modelAt(0),"folder"))),Qt::ControlModifier);
        QTest::keyRelease(content->window(),Qt::Key_Control);QCOMPARE(browser->selectedUrls().size(),2);
        capture(content->window(),"mixed-directory-file");click(find(content,"bleeckerFileChooserOpen"));
        QTRY_COMPARE(results(fixture).size(),1);QCOMPARE(results(fixture)[0].toMap()["urls"].toList().size(),2);
    }
};
QTEST_MAIN(FileInputUiTests)
#include "fileinput-ui.moc"

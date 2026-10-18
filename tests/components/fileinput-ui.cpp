#include "filechooserbrowser.h"
#include <QAccessible>
#include <QDir>
#include <QFile>
#include <QJSValue>
#include <QImage>
#include <QQmlEngine>
#include <QQuickItem>
#include <QQuickView>
#include <QRegularExpression>
#include <QTemporaryDir>
#include <QtTest>

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

class FileInputUiTests:public QObject {
    Q_OBJECT
    void put(const QString &path){QFile f(path);QVERIFY(f.open(QIODevice::WriteOnly));QVERIFY(f.write("Avelino owned UI fixture\n")>0);}
    QQuickItem *find(QQuickItem *root,const QString &name){
        if(!root)return nullptr;
        if(root->objectName()==name)return root;
        for(auto child:root->childItems())if(auto result=find(child,name))return result;
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
    void load(QQuickView &view,const QTemporaryDir &root){
        view.engine()->addImportPath(AVELINO_FILE_INPUT_IMPORT_PATH);
        view.setInitialProperties({{"fixtureRoot",QUrl::fromLocalFile(root.path())}});
        view.setSource(QUrl("qrc:/file-input-tests/fileinput-fixture.qml"));
        QVERIFY2(view.status()==QQuickView::Ready,qPrintable(view.errors().isEmpty()?QStringLiteral("FileInput fixture did not load"):view.errors().first().toString()));
        view.show();QVERIFY(QTest::qWaitForWindowExposed(&view));
    }
private slots:
    void initTestCase(){QAccessible::setActive(true);}
    void init(){QTest::failOnWarning(QRegularExpression(".*(FileInput requires|Unable to assign|should be coerced|ReferenceError|TypeError).*"));}
    void actualViewMenuListDisclosureAndIconsNavigation(){
        QTemporaryDir directory;QDir root(directory.path());QVERIFY(root.mkdir("Folder"));
        put(root.filePath("Alpha.txt"));put(root.filePath("Bravo.txt"));put(root.filePath("Folder/Child.txt"));put(root.filePath("blocked.png"));
        QQuickView view;load(view,directory);auto fixture=view.rootObject();auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
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
        QQuickView view;load(view,directory);auto fixture=view.rootObject();fixture->setProperty("removeOnResult",true);
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
        QQuickView view;load(view,directory);auto fixture=view.rootObject();QVERIFY(fixture);
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
        QQuickView view;load(view,directory);auto fixture=view.rootObject();fixture->setProperty("removeOnResult",true);
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
        QQuickView view;load(view,directory);auto fixture=view.rootObject();auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
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
    void actualLocationErrorRecoveryAndKeyboardAccept(){
        FileInputAnnouncementCapture announcements;
        QTemporaryDir directory;QDir root(directory.path());put(root.filePath("one.txt"));
        QQuickView view;load(view,directory);auto fixture=view.rootObject();auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
        auto browser=control->property("browser").value<FileChooserBrowser*>();auto chooser=control->property("chooser").value<QObject*>();
        click(control->property("inputItem").value<QQuickItem*>());QTRY_VERIFY(browser->active());
        auto content=chooser->property("contentItem").value<QQuickItem*>();QTRY_VERIFY(content&&content->window());
        auto path=chooser->property("pathInput").value<QQuickItem*>();QVERIFY(path);
        auto enterPath=[&](const QString &text){
            QTest::keyClick(content->window(),Qt::Key_L,Qt::ControlModifier);QVERIFY(path->hasActiveFocus());
            QTest::keyClick(content->window(),Qt::Key_A,Qt::ControlModifier);
            for(const auto character:text.toLatin1())QTest::keyClick(content->window(),character);
            QTest::keyClick(content->window(),Qt::Key_Return);QTest::qWait(30);
        };
        enterPath(directory.path()+"/missing");QVERIFY(browser->active());QVERIFY(!browser->error().isEmpty());QVERIFY(!browser->canAccept());QVERIFY(results(fixture).isEmpty());
        QTRY_COMPARE(announcements.messages.size(),1);
        QCOMPARE(announcements.messages[0].text,browser->error());
        QVERIFY(announcements.messages[0].politeness==QAccessible::AnnouncementPoliteness::Assertive);
        QVERIFY(announcements.messages[0].source);QCOMPARE(announcements.messages[0].source->objectName(),QString("bleeckerFileChooserError"));
        browser->modelAt(0)->refresh();QTest::qWait(30);QCOMPARE(announcements.messages.size(),1);
        enterPath(directory.path()+"/missing");QTRY_COMPARE(announcements.messages.size(),2);
        QCOMPARE(announcements.messages[1].text,browser->error());
        capture(content->window(),"location-error");
        enterPath(directory.path());QVERIFY(browser->error().isEmpty());QTRY_VERIFY(find(content,"bleeckerFileChooserRow0_0"));
        QCOMPARE(announcements.messages.size(),2);
        click(find(content,"bleeckerFileChooserRow0_0"));QVERIFY(browser->canAccept());QTest::keyClick(content->window(),Qt::Key_Return);
        QTRY_COMPARE(results(fixture).size(),1);QVERIFY(!browser->active());QVERIFY(fixture->property("visibleAtCallback").toBool());
    }
    void initialLocationErrorAndClosedAnnouncement(){
        FileInputAnnouncementCapture announcements;QTemporaryDir directory;
        QQuickView view;load(view,directory);auto fixture=view.rootObject();
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
        QQuickView view;load(view,directory);auto fixture=view.rootObject();auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
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
        QTemporaryDir directory;QQuickView view;load(view,directory);auto fixture=view.rootObject();auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
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
        QQuickView view;load(view,directory);auto fixture=view.rootObject();auto control=fixture->findChild<QQuickItem*>("fileInput");QVERIFY(control);
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
        QTemporaryDir directory;QQuickView view;load(view,directory);auto fixture=view.rootObject();fixture->setProperty("types",QVariantList{QStringLiteral("inode/directory")});
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
        QQuickView view;load(view,directory);auto fixture=view.rootObject();
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

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
    void click(QQuickItem *item,Qt::KeyboardModifiers modifiers={}){
        QVERIFY(item);QVERIFY(item->window());
        QTest::mouseClick(item->window(),Qt::LeftButton,modifiers,item->mapToScene(item->boundingRect().center()).toPoint());
    }
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
    void init(){QTest::failOnWarning(QRegularExpression(".*(FileInput requires|Unable to assign|should be coerced).*"));}
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
        capture(content->window(),"location-error");
        enterPath(directory.path());QVERIFY(browser->error().isEmpty());QTRY_VERIFY(find(content,"bleeckerFileChooserRow0_0"));
        click(find(content,"bleeckerFileChooserRow0_0"));QVERIFY(browser->canAccept());QTest::keyClick(content->window(),Qt::Key_Return);
        QTRY_COMPARE(results(fixture).size(),1);QVERIFY(!browser->active());QVERIFY(fixture->property("visibleAtCallback").toBool());
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

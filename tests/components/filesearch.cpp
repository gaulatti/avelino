#include "filechooserbrowser.h"
#include <QAccessible>
#include <QDir>
#include <QFile>
#include <QJSValue>
#include <QQmlEngine>
#include <QQuickItem>
#include <QQuickItemGrabResult>
#include <QQuickView>
#include <QRegularExpression>
#include <QSettings>
#include <QSignalSpy>
#include <QTemporaryDir>
#include <QtTest>

class FileSearchTests:public QObject {
    Q_OBJECT
    QString m_root,m_captures;
    bool m_unavailable;
    QTemporaryDir m_config;
    const QString token="avelinoulnacerulean";
    QQuickItem *find(QQuickItem *item,const QString &name){
        if(!item)return nullptr;if(item->objectName()==name)return item;
        for(auto child:item->childItems())if(auto found=find(child,name))return found;return nullptr;
    }
    QQuickItem *visible(const QString &name){
        for(auto window:QGuiApplication::topLevelWindows())if(auto quick=qobject_cast<QQuickWindow*>(window);quick&&quick->isVisible())
            if(auto item=find(quick->contentItem(),name);item&&item->isVisible())return item;return nullptr;
    }
    void click(QQuickItem *item){QVERIFY(item);QVERIFY(item->window());QTest::mouseClick(item->window(),Qt::LeftButton,{},item->mapToScene(item->boundingRect().center()).toPoint());}
    void type(QWindow *window,const QString &text){for(auto character:text.toLatin1())QTest::keyClick(window,character);}
    bool load(QQuickView &view){
        view.engine()->addImportPath(AVELINO_FILE_INPUT_IMPORT_PATH);
        view.setInitialProperties({{"fixtureRoot",QUrl::fromLocalFile(m_root)}});
        view.setSource(QUrl("qrc:/file-input-tests/fileinput-fixture.qml"));
        if(view.status()!=QQuickView::Ready){for(auto error:view.errors())qWarning().noquote()<<error.toString();return false;}
        view.show();return QTest::qWaitForWindowExposed(&view);
    }
    FileChooserBrowser *open(QQuickView &view){
        auto control=view.rootObject()->findChild<QQuickItem*>("fileInput");if(!control)return nullptr;
        click(control->property("inputItem").value<QQuickItem*>());
        return control->property("browser").value<FileChooserBrowser*>();
    }
    int row(FileChooserSearch *search,const QString &name){for(int i=0;i<search->count();++i)if(search->entry(i)["name"]==name)return i;return -1;}
    QVariantList results(QQuickItem *fixture){return fixture->property("results").value<QJSValue>().toVariant().toList();}
    void put(const QString &path,const QByteArray &data){QFile file(path);QVERIFY(file.open(QIODevice::WriteOnly));QCOMPARE(file.write(data),qint64(data.size()));}
    void capture(QQuickItem *item,const QString &name){
        auto result=item->window()->contentItem()->grabToImage();QVERIFY(result);QSignalSpy ready(result.data(),&QQuickItemGrabResult::ready);
        if(result->image().isNull())QVERIFY(ready.wait(5000));
        QDir output(m_captures);QVERIFY(output.mkpath("."));
        const auto path=output.filePath(name+"-dpr"+QString::number(item->window()->devicePixelRatio())+".png");
        QVERIFY(!QFile::exists(path));QVERIFY(result->image().save(path));
    }
public:
    FileSearchTests(QString root,bool unavailable):m_root(std::move(root)),m_unavailable(unavailable){}
private slots:
    void init(){QTest::failOnWarning(QRegularExpression(".*(ReferenceError|TypeError|Unable to assign|should be coerced).*"));}
    void initTestCase(){QVERIFY(QFileInfo(m_root).isDir());QAccessible::setActive(true);
        QDir parent(AVELINO_FILE_SEARCH_EVIDENCE_DIR);QVERIFY(parent.mkpath("."));QTemporaryDir captures(parent.filePath("run-XXXXXX"));QVERIFY(captures.isValid());m_captures=captures.path();captures.setAutoRemove(false);qInfo().noquote()<<"FILE_SEARCH_CAPTURES"<<m_captures;
        QSettings::setPath(QSettings::NativeFormat,QSettings::UserScope,m_config.path());}
    void actualInputModesScopesAndOwner(){
        QQuickView view;QVERIFY(load(view));auto browser=open(view);QVERIFY(browser);QTRY_VERIFY(browser->active());
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);click(editor);type(editor->window(),token);
        auto location=visible("bleeckerFileChooserLocation");QVERIFY(location);
        QVERIFY(!editor->mapRectToScene(editor->boundingRect()).intersects(location->mapRectToScene(location->boundingRect())));
        auto search=browser->search();QTRY_VERIFY_WITH_TIMEOUT(!search->busy()&&row(search,"pine-only.txt")>=0,15000);
        QVERIFY(search->error().isEmpty());QCOMPARE(search->mode(),"general");QVERIFY(!search->folderOnly());
        QTRY_VERIFY_WITH_TIMEOUT(row(search,token+"-outside.txt")>=0&&row(search,"pine-peer.txt")>=0,15000);
        capture(editor,"general-global");
        click(visible("bleeckerFileChooserSearchFolder"));QTRY_VERIFY(search->folderOnly());
        QTRY_VERIFY(!search->busy()&&row(search,token+"-outside.txt")<0&&row(search,"pine-peer.txt")<0&&row(search,token+"-child.txt")>=0);
        click(editor);QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Return);
        QTRY_COMPARE(search->mode(),"filename");QTRY_VERIFY(!search->busy()&&row(search,"pine-only.txt")<0&&row(search,token+"-name.txt")>=0);
        capture(editor,"filename-folder");
        click(visible("bleeckerFileChooserSearchToken"));QTRY_VERIFY(visible("bleeckerFileChooserSearchMode_everything"));
        capture(editor,"token-menu");
        click(visible("bleeckerFileChooserSearchMode_everything"));QTRY_COMPARE(search->mode(),"everything");
        QTRY_VERIFY(!search->busy()&&row(search,"pine-only.txt")>=0&&row(search,token+"-name.txt")>=0);
        const auto index=row(search,"pine-only.txt");auto item=visible("bleeckerFileChooserSearchRow_"+QString::number(index));QVERIFY(item);
        auto accessible=QAccessible::queryAccessibleInterface(item);QVERIFY(accessible&&accessible->actionInterface());
        accessible->actionInterface()->doAction(QAccessibleActionInterface::pressAction());QTRY_VERIFY(browser->canAccept());
        QCOMPARE(browser->selectedUrls(),QVariantList{QUrl::fromLocalFile(m_root+"/pine-only.txt")});
        capture(editor,"everything-selected");click(visible("bleeckerFileChooserOpen"));
        QTRY_COMPARE(results(view.rootObject()).size(),1);QVERIFY(view.rootObject()->property("visibleAtCallback").toBool());QVERIFY(!browser->active());
        QCOMPARE(results(view.rootObject())[0].toMap()["urls"].toList(),QVariantList{QUrl::fromLocalFile(m_root+"/pine-only.txt")});
    }
    void liveIndexUpdatesAndTypeRevalidation(){
        FileChooserBrowser browser;browser.setAllowedContentTypes({"text/plain"});QVERIFY(browser.open(QUrl::fromLocalFile(m_root)));
        auto search=browser.search();search->setFolderOnly(true);search->setQuery(token);
        QTRY_VERIFY_WITH_TIMEOUT(!search->busy()&&row(search,"pine-only.txt")>=0,15000);
        const auto path=m_root+"/live-body.txt";put(path,("Live content "+token+"\n").toUtf8());
        QTRY_VERIFY_WITH_TIMEOUT(row(search,"live-body.txt")>=0,15000);
        QVERIFY(QFile::remove(path));QTRY_VERIFY_WITH_TIMEOUT(row(search,"live-body.txt")<0,15000);
        search->select(row(search,"pine-only.txt"));QVERIFY(browser.canAccept());QSignalSpy owner(&browser,&FileChooserBrowser::result);
        browser.setAllowedContentTypes({"image/*"});browser.acceptSelection();QVERIFY(owner.isEmpty());
        QTRY_VERIFY(!search->busy()&&!browser.canAccept());
        QVERIFY(!search->entry(row(search,"pine-only.txt"))["eligible"].toBool());
        search->select(row(search,token+"-image.png"));QVERIFY(browser.canAccept());
        const auto image=m_root+"/"+token+"-image.png";QVERIFY(QFile::remove(image));browser.acceptSelection();
        QVERIFY(owner.isEmpty());QVERIFY(!browser.error().isEmpty());put(image,"Controlled filename/type association.\n");browser.cancel();
    }
    void escapeBackForwardAndNewQueryBranch(){
        QQuickView view;QVERIFY(load(view));auto browser=open(view);QVERIFY(browser);
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);click(editor);type(editor->window(),token);
        auto search=browser->search();QTRY_VERIFY_WITH_TIMEOUT(!search->busy()&&row(search,"pine-only.txt")>=0,15000);
        click(visible("bleeckerFileChooserSearchFolder"));click(editor);
        QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Return);
        QTRY_COMPARE(search->mode(),"everything");QTRY_VERIFY(search->folderOnly()&&!search->busy());
        QTest::keyClick(editor->window(),Qt::Key_Escape);QTRY_VERIFY(!search->active());QVERIFY(browser->canGoForward());QVERIFY(!browser->canGoBack());QCOMPARE(browser->folderPath(),m_root);
        click(visible("bleeckerFileChooserForward"));QTRY_VERIFY(search->active());QCOMPARE(search->query(),token);QCOMPARE(search->mode(),"everything");QVERIFY(search->folderOnly());
        QTRY_VERIFY(!search->busy()&&row(search,"pine-only.txt")>=0&&row(search,token+"-outside.txt")<0);
        click(visible("bleeckerFileChooserBack"));QTRY_VERIFY(!search->active());QVERIFY(browser->canGoForward());
        click(editor);type(editor->window(),"another-control");QTRY_VERIFY(search->active());QVERIFY(!browser->canGoForward());QVERIFY(results(view.rootObject()).isEmpty());browser->cancel();
    }
    void literalQuotesAndFolderNavigation(){
        FileChooserBrowser browser;browser.setAllowedContentTypes({"text/plain"});QVERIFY(browser.open(QUrl::fromLocalFile(m_root)));
        auto search=browser.search();search->setFolderOnly(true);const auto name=token+"-quote\".txt";const auto path=m_root+"/"+name;
        put(path,"Controlled quoted filename.\n");search->setQuery(name);
        QTRY_VERIFY_WITH_TIMEOUT(!search->busy()&&row(search,name)>=0,15000);QVERIFY(search->error().isEmpty());
        QVERIFY(QFile::remove(path));
        const auto folder=m_root+"/"+token+"-folder";QVERIFY(QDir().mkdir(folder));search->setQuery(token+"-folder");
        QTRY_VERIFY_WITH_TIMEOUT(!search->busy()&&row(search,token+"-folder")>=0,15000);
        search->select(row(search,token+"-folder"));QVERIFY(browser.canAccept());QSignalSpy owner(&browser,&FileChooserBrowser::result);
        browser.acceptSelection();QCOMPARE(browser.folderPath(),folder);QVERIFY(!search->active());QVERIFY(owner.isEmpty());browser.cancel();QVERIFY(QDir().rmdir(folder));
    }
    void cancellationReopenAndOwnerRemoval(){
        QQuickView view;QVERIFY(load(view));QPointer<FileChooserBrowser> browser=open(view);QVERIFY(browser);
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);click(editor);type(editor->window(),token);
        click(visible("bleeckerFileChooserCancel"));QTRY_VERIFY(!browser->active());QVERIFY(!browser->search()->active());
        browser=open(view);QVERIFY(browser);browser->search()->setQuery("previous-nonmatching-query");browser->search()->setQuery(token);browser->search()->setFolderOnly(true);
        QTRY_VERIFY_WITH_TIMEOUT(!browser->search()->busy()&&row(browser->search(),"pine-only.txt")>=0,15000);
        view.rootObject()->setProperty("mounted",false);QTRY_VERIFY(!browser);QTest::qWait(100);
        view.rootObject()->setProperty("mounted",true);QTRY_VERIFY(view.rootObject()->findChild<QQuickItem*>("fileInput"));browser=open(view);QVERIFY(browser);
        browser->search()->setFolderOnly(true);browser->search()->setQuery(token);
        QTRY_VERIFY_WITH_TIMEOUT(!browser->search()->busy()&&row(browser->search(),"pine-only.txt")>=0,15000);
        view.rootObject()->setProperty("removeOnResult",true);browser->search()->select(row(browser->search(),"pine-only.txt"));browser->acceptSelection();
        QTRY_VERIFY(!browser);QCOMPARE(results(view.rootObject()).size(),1);QVERIFY(view.rootObject()->property("visibleAtCallback").toBool());QTest::qWait(100);
    }
    void unavailableIndexIsVisibleAndCancels(){
        if(!m_unavailable)QSKIP("Executed separately on a real session bus without an index provider");
        QQuickView view;QVERIFY(load(view));auto browser=open(view);QVERIFY(browser);auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);
        click(editor);type(editor->window(),token);QTRY_VERIFY_WITH_TIMEOUT(!browser->search()->busy()&&!browser->error().isEmpty(),15000);
        QVERIFY(browser->error().startsWith("Indexed search is unavailable:"));QCOMPARE(browser->search()->count(),0);QVERIFY(!browser->canAccept());
        auto message=visible("bleeckerFileChooserError");QVERIFY(message);QCOMPARE(message->property("text").toString(),QStringLiteral("Indexed search is unavailable. Clear the search to browse folders."));
        click(visible("bleeckerFileChooserCancel"));QTRY_VERIFY(!browser->active());QVERIFY(results(view.rootObject()).isEmpty());
    }
};

int main(int argc,char **argv){
    QGuiApplication application(argc,argv);auto arguments=application.arguments();
    const int at=arguments.indexOf("--file-input-search-root");if(at<0||at+1>=arguments.size())return 2;
    const auto root=arguments[at+1];arguments.removeAt(at+1);arguments.removeAt(at);
    const bool unavailable=arguments.removeAll("--file-input-search-no-index")>0;
    FileSearchTests tests(root,unavailable);return QTest::qExec(&tests,arguments);
}

#include "filesearch.moc"

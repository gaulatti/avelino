#include "filechooserbrowser.h"
#include <QDir>
#include <QFile>
#include <QPointer>
#include <QSignalSpy>
#include <QTemporaryDir>
#include <QtTest>

class BrowserTests:public QObject {
    Q_OBJECT
    void put(const QString &path){QFile file(path);QVERIFY(file.open(QIODevice::WriteOnly));QVERIFY(file.write("Avelino owned fixture\n")>0);}
    int row(FileChooserModel *model,const QString &name){
        for(int i=0;i<model->count();++i)if(model->entry(i)["name"]==name)return i;
        return -1;
    }
private slots:
    void columnNavigationAndSelectionAreSeparate(){
        QTemporaryDir root;QDir directory(root.path());QVERIFY(directory.mkdir("folder"));
        put(directory.filePath("one.txt"));put(directory.filePath("folder/child.txt"));put(directory.filePath("fake.png"));
        FileChooserBrowser browser;browser.setAllowedContentTypes({"inode/directory","text/plain"});
        QSignalSpy result(&browser,&FileChooserBrowser::result);QVERIFY(browser.open(QUrl::fromLocalFile(root.path())));
        auto parent=browser.modelAt(0);QVERIFY(parent);const auto folder=row(parent,"folder"),one=row(parent,"one.txt");
        browser.choose(0,folder);QCOMPARE(browser.count(),2);QCOMPARE(browser.focusedColumn(),0);QCOMPARE(browser.selectionColumn(),0);
        QCOMPARE(browser.folderPath(),directory.filePath("folder"));QVERIFY(browser.canAccept());
        QCOMPARE(browser.selectedUrls(),QVariantList{QUrl::fromLocalFile(directory.filePath("folder")+'/')});
        browser.choose(0,one,Qt::ControlModifier);QCOMPARE(browser.count(),1);QCOMPARE(browser.selectedUrls().size(),2);
        browser.choose(0,row(parent,"fake.png"));QCOMPARE(browser.selectedUrls().size(),2);
        browser.choose(0,folder);browser.focusRight();QCOMPARE(browser.focusedColumn(),1);
        browser.choose(1,row(browser.modelAt(1),"child.txt"));QCOMPARE(browser.selectionColumn(),1);
        QVERIFY(!parent->entry(folder)["selected"].toBool());QCOMPARE(browser.selectedUrls().size(),1);
        QCOMPARE(browser.selectedUrls()[0].toUrl(),QUrl::fromLocalFile(directory.filePath("folder/child.txt")));
        bool activeAtResult=false;connect(&browser,&FileChooserBrowser::result,this,[&]{activeAtResult=browser.active();});
        browser.acceptSelection();QCOMPARE(result.count(),1);QVERIFY(activeAtResult);QVERIFY(!browser.active());
        QVERIFY(browser.open(QUrl::fromLocalFile(root.path())));QCOMPARE(browser.folderPath(),directory.filePath("folder"));
        QVERIFY(browser.selectedUrls().isEmpty());browser.cancel();QCOMPARE(result.count(),1);
    }
    void fileOnlyNavigationAndLiveTypes(){
        QTemporaryDir root;QDir directory(root.path());QVERIFY(directory.mkdir("folder"));put(directory.filePath("folder/a.txt"));put(directory.filePath("folder/b.png"));
        FileChooserBrowser browser;browser.setAllowedContentTypes({"text/plain"});QVERIFY(browser.open(QUrl::fromLocalFile(root.path())));
        browser.choose(0,row(browser.modelAt(0),"folder"));QCOMPARE(browser.count(),2);QVERIFY(!browser.canAccept());
        browser.focusRight();browser.move(1);QVERIFY(browser.canAccept());QCOMPARE(browser.selectedUrls().size(),1);
        browser.setAllowedContentTypes({});QVERIFY(!browser.canAccept());QVERIFY(browser.selectedUrls().isEmpty());
        browser.setAllowedContentTypes({"image/*"});browser.selectAll();QCOMPARE(browser.selectedUrls().size(),1);
        QVERIFY(browser.selectedUrls()[0].toUrl().fileName()=="b.png");
        browser.focusLeft();QCOMPARE(browser.focusedColumn(),0);QVERIFY(browser.goUp());QCOMPARE(browser.count(),1);QCOMPARE(browser.folderPath(),root.path());
    }
    void historyRestoresLocationsAndClearsSelection(){
        QTemporaryDir root;QDir directory(root.path());QVERIFY(directory.mkdir("folder"));QVERIFY(directory.mkdir("other"));
        for(const auto &name:{"a.txt","b.txt","c.txt","folder/child.txt"})put(directory.filePath(name));
        FileChooserBrowser browser;browser.setAllowedContentTypes({"text/plain"});QVERIFY(browser.open(QUrl::fromLocalFile(root.path())));
        QVERIFY(!browser.canGoBack());QVERIFY(!browser.canGoForward());
        browser.choose(0,row(browser.modelAt(0),"a.txt"));browser.choose(0,row(browser.modelAt(0),"b.txt"),Qt::ControlModifier);
        QCOMPARE(browser.selectedUrls().size(),2);
        browser.choose(0,row(browser.modelAt(0),"folder"));QCOMPARE(browser.count(),2);QVERIFY(browser.canGoBack());
        browser.focusRight();browser.choose(1,0);QCOMPARE(browser.selectedUrls().size(),1);
        browser.goBack();QCOMPARE(browser.count(),1);QCOMPARE(browser.folderPath(),root.path());QVERIFY(browser.selectedUrls().isEmpty());QVERIFY(!browser.canAccept());
        auto model=browser.modelAt(0);model->select(row(model,"c.txt"),Qt::ShiftModifier);
        QCOMPARE(browser.selectedUrls(),(QVariantList{QUrl::fromLocalFile(directory.filePath("a.txt")),QUrl::fromLocalFile(directory.filePath("b.txt")),QUrl::fromLocalFile(directory.filePath("c.txt"))}));
        browser.goForward();QCOMPARE(browser.count(),2);QCOMPARE(browser.focusedColumn(),1);QVERIFY(browser.selectedUrls().isEmpty());QVERIFY(!browser.canAccept());
        browser.goBack();QVERIFY(browser.navigatePath(directory.filePath("other")));QVERIFY(!browser.canGoForward());
    }
    void newFolderValidationCreationAndHistory(){
        QTemporaryDir root;QDir directory(root.path());QVERIFY(directory.mkdir("untitled folder"));QVERIFY(directory.mkdir("untitled folder 2"));put(directory.filePath("one.txt"));
        FileChooserBrowser browser;browser.setAllowedContentTypes({"text/plain"});QSignalSpy result(&browser,&FileChooserBrowser::result);
        QVERIFY(browser.open(QUrl::fromLocalFile(root.path())));QVERIFY(browser.canCreateFolder());QCOMPARE(browser.suggestedFolderName(),QString("untitled folder 3"));
        QCOMPARE(browser.folderNameError("one.txt"),QString("This name is already taken."));
        QCOMPARE(browser.folderNameError("untitled folder"),QString("This name is already taken."));
        for(const auto &name:{QString(),QString(".."),QString("../escape"),QString("a/b"),QString("bad")+QChar::Null}){
            QVERIFY(!browser.createFolder(name,root.path()));QVERIFY(!browser.newFolderError().isEmpty());QCOMPARE(browser.folderPath(),root.path());
        }
        QVERIFY(!browser.createFolder("one.txt",root.path()));QFile existing(directory.filePath("one.txt"));QVERIFY(existing.open(QIODevice::ReadOnly));QCOMPARE(existing.readAll(),QByteArray("Avelino owned fixture\n"));
        browser.choose(0,row(browser.modelAt(0),"one.txt"));QCOMPARE(browser.selectedUrls().size(),1);
        const QString name=QString::fromUtf8(" Å new folder ");QVERIFY(browser.createFolder(name,root.path()));
        QCOMPARE(browser.folderPath(),directory.filePath(name));QVERIFY(QFileInfo(browser.folderPath()).isDir());QVERIFY(browser.active());QVERIFY(!browser.canAccept());QVERIFY(browser.newFolderError().isEmpty());QVERIFY(result.isEmpty());
        browser.goBack();QCOMPARE(browser.folderPath(),root.path());QVERIFY(browser.selectedUrls().isEmpty());QVERIFY(!browser.canAccept());QVERIFY(browser.canGoForward());
        browser.goForward();QCOMPARE(browser.folderPath(),directory.filePath(name));QVERIFY(browser.selectedUrls().isEmpty());
        browser.setAllowedContentTypes({"inode/directory"});QVERIFY(browser.canAccept());browser.acceptSelection();QCOMPARE(result.count(),1);
        QCOMPARE(result[0][0].toMap()["urls"].toList(),QVariantList{QUrl::fromLocalFile(directory.filePath(name)+'/')});
    }
    void newFolderRejectsUnavailableAndChangedParents(){
        QTemporaryDir root;QDir directory(root.path());QVERIFY(directory.mkdir("parent"));
        FileChooserBrowser browser;browser.setAllowedContentTypes({"text/plain"});QSignalSpy result(&browser,&FileChooserBrowser::result);
        QVERIFY(browser.open(QUrl::fromLocalFile(directory.filePath("parent"))));
        QVERIFY(!browser.createFolder("wrong parent",root.path()));QVERIFY(!QFileInfo(directory.filePath("wrong parent")).exists());
        QVERIFY(directory.rmdir("parent"));QVERIFY(!browser.canCreateFolder());QVERIFY(!browser.createFolder("child",directory.filePath("parent")));
        QVERIFY(!QFileInfo(directory.filePath("parent/child")).exists());QVERIFY(result.isEmpty());browser.cancel();
        QVERIFY(!browser.canCreateFolder());QVERIFY(browser.suggestedFolderName().isEmpty());
    }
    void ownerCanRemoveAllColumnsDuringResult(){
        QTemporaryDir root;QDir directory(root.path());QVERIFY(directory.mkdir("folder"));put(directory.filePath("folder/a.txt"));
        QPointer<FileChooserBrowser> browser=new FileChooserBrowser;browser->setAllowedContentTypes({"text/plain"});QVERIFY(browser->open(QUrl::fromLocalFile(root.path())));
        browser->choose(0,row(browser->modelAt(0),"folder"));browser->choose(1,0);
        QPointer<FileChooserModel> parent=browser->modelAt(0),child=browser->modelAt(1);
        connect(browser.data(),&FileChooserBrowser::result,this,[&]{delete browser.data();});browser->acceptSelection();
        QVERIFY(browser.isNull());QVERIFY(parent.isNull());QVERIFY(child.isNull());
    }
};
QTEST_GUILESS_MAIN(BrowserTests)
#include "filechooserbrowser.moc"

#include "filechoosermodel.h"
#include <QDir>
#include <QFile>
#include <QPointer>
#include <QRegularExpression>
#include <QSignalSpy>
#include <QTemporaryDir>
#include <QtTest>

class FileChooserTests:public QObject {
    Q_OBJECT
    int row(FileChooserModel &model,const QString &name){
        for(int i=0;i<model.count();++i)if(model.entry(i)["name"]==name)return i;
        return -1;
    }
    void put(const QString &path,const QByteArray &contents="Avelino controlled fixture\n"){
        QFile file(path);QVERIFY(file.open(QIODevice::WriteOnly));QCOMPARE(file.write(contents),contents.size());
    }
private slots:
    void init(){QTest::failOnWarning(QRegularExpression("Broken filename passed to function"));}
    void filtersSelectionAndLifecycle(){
        QTemporaryDir root;QVERIFY(root.isValid());QDir directory(root.path());
        put(directory.filePath("one.txt"));put(directory.filePath("two.txt"));
        put(directory.filePath("fake.png"));put(directory.filePath("no-extension"),QByteArray::fromHex("89504e470d0a1a0a"));
        put(directory.filePath(".hidden.txt"));QVERIFY(directory.mkdir("folder"));
        put(directory.filePath("folder/child.txt"));
        FileChooserModel model;model.setAllowedContentTypes({"text/plain"});
        QCOMPARE(model.count(),0);QSignalSpy result(&model,&FileChooserModel::result);
        const auto url=QUrl::fromLocalFile(root.path());QVERIFY(model.open(url));
        QVERIFY(!model.open(url));QCOMPARE(model.count(),5);QCOMPARE(row(model,".hidden.txt"),-1);
        QVERIFY(model.canChooseFiles());QVERIFY(!model.canChooseDirectories());QVERIFY(!model.canAccept());
        const auto one=row(model,"one.txt"),two=row(model,"two.txt");QVERIFY(one>=0&&two>=0);
        model.select(row(model,"fake.png"));QVERIFY(model.selectedUrls().isEmpty());
        model.select(two);model.select(one,Qt::ControlModifier);
        QCOMPARE(model.selectedUrls(),QVariantList({QUrl::fromLocalFile(directory.filePath("one.txt")),QUrl::fromLocalFile(directory.filePath("two.txt"))}));
        bool activeAtCallback=false;connect(&model,&FileChooserModel::result,this,[&]{activeAtCallback=model.active();});
        model.acceptSelection();QCOMPARE(result.count(),1);QVERIFY(activeAtCallback);QVERIFY(!model.active());
        const auto callback=result.takeFirst().first().toMap();QCOMPARE(callback["kind"],QVariant("success"));QCOMPARE(callback["urls"].toList().size(),2);
        QVERIFY(model.open(url));QVERIFY(model.selectedUrls().isEmpty());model.cancel();QCOMPARE(result.count(),0);
        model.setAllowedContentTypes({"image/*"});QVERIFY(model.open(url));
        QVERIFY(model.entry(row(model,"fake.png"))["eligible"].toBool());QVERIFY(!model.entry(row(model,"no-extension"))["eligible"].toBool());
        model.setAllowedContentTypes({});QVERIFY(!model.canChooseFiles());QVERIFY(!model.canChooseDirectories());QVERIFY(!model.canAccept());
        model.setAllowedContentTypes({QVariantMap{{"identifier","org.avelino.fixture"},{"filenameExtensions",QVariantList{}}}});
        QVERIFY(model.canChooseFiles());model.selectAll();QVERIFY(model.selectedUrls().isEmpty());
        model.setAllowedContentTypes({QVariantMap{{"identifier","org.avelino.text"},{"filenameExtensions",QVariantList{"txt"}}}});
        model.selectAll();QCOMPARE(model.selectedUrls().size(),2);
    }
    void directoriesNavigationAndUrlEncoding(){
        QTemporaryDir root;QDir directory(root.path());QVERIFY(directory.mkdir("folder"));
        put(directory.filePath("one.txt"));put(directory.filePath(QString::fromUtf8("unicodé 日本語.txt")));put(directory.filePath("spaces in name.txt"));
        FileChooserModel model;model.setAllowedContentTypes({"inode/directory","text/plain"});
        QVERIFY(model.open(QUrl::fromLocalFile(root.path())));QVERIFY(model.canChooseFiles());QVERIFY(model.canChooseDirectories());
        QVERIFY(model.canAccept());model.select(row(model,"one.txt"));model.select(row(model,"folder"),Qt::ControlModifier);
        const auto urls=model.selectedUrls();QCOMPARE(urls.size(),2);QVERIFY(urls[0].toUrl().toString().endsWith("/folder/"));
        model.activate(row(model,"folder"));QCOMPARE(model.folderPath(),directory.filePath("folder"));QCOMPARE(model.count(),0);QVERIFY(model.canAccept());
        QVERIFY(model.goUp());model.select(row(model,"spaces in name.txt"));QVERIFY(model.selectedUrls()[0].toUrl().toEncoded().contains("spaces%20in%20name.txt"));
        model.select(row(model,QString::fromUtf8("unicodé 日本語.txt")));QVERIFY(model.selectedUrls()[0].toUrl().toEncoded().contains("unicod%C3%A9%20"));
        model.setAllowedContentTypes({"*/*"});QVERIFY(!model.canChooseDirectories());QVERIFY(model.canChooseFiles());
        QVERIFY(!model.entry(row(model,"folder"))["eligible"].toBool());model.activate(row(model,"folder"));QCOMPARE(model.count(),0);
        QCOMPARE(model.folderPath(),directory.filePath("folder"));
    }
    void aliasesAndDisappearingSelection(){
        QTemporaryDir root;QDir directory(root.path());put(directory.filePath("one.txt"));
        QVERIFY(QFile::link(directory.filePath("one.txt"),directory.filePath("symlink.txt")));
        FileChooserModel model;model.setAllowedContentTypes({"text/plain"});QVERIFY(model.open(QUrl::fromLocalFile(root.path())));
        model.select(row(model,"symlink.txt"));QCOMPARE(model.selectedUrls(),QVariantList{QUrl::fromLocalFile(directory.filePath("one.txt"))});
        QSignalSpy result(&model,&FileChooserModel::result);QVERIFY(QFile::remove(directory.filePath("one.txt")));model.acceptSelection();
        QCOMPARE(result.count(),0);QVERIFY(model.active());QVERIFY(!model.error().isEmpty());
        model.refresh();QVERIFY(model.selectedUrls().isEmpty());QVERIFY(!model.canAccept());
        put(directory.filePath("two.txt"));model.refresh();QVERIFY(row(model,"two.txt")>=0);
    }
    void invalidLocationNeverReturnsAnEmptySuccess(){
        QTemporaryDir root;FileChooserModel model;model.setAllowedContentTypes({"text/plain"});
        QSignalSpy result(&model,&FileChooserModel::result);
        QVERIFY(model.open(QUrl::fromLocalFile(root.path()+"/missing")));QVERIFY(!model.error().isEmpty());QVERIFY(!model.canAccept());model.acceptSelection();QCOMPARE(result.count(),0);
        QVERIFY(!model.navigate(QUrl("https://example.invalid/")));QVERIFY(!model.canAccept());
        QVERIFY(!model.goUp());QCOMPARE(model.folder(),QUrl("https://example.invalid/"));
        QVERIFY(model.navigate(QUrl::fromLocalFile(root.path())));QVERIFY(model.error().isEmpty());QVERIFY(!model.canAccept());
    }
    void invalidTypeUpdateCannotRetainThePreviousAllFilesRule(){
        QTemporaryDir root;QDir directory(root.path());put(directory.filePath("one.txt"));
        FileChooserModel model;model.setAllowedContentTypes({"*/*"});QVERIFY(model.open(QUrl::fromLocalFile(root.path())));
        model.selectAll();QCOMPARE(model.selectedUrls().size(),1);
        QTest::ignoreMessage(QtWarningMsg,"Unknown file content MIME type: application/x-avelino-type-not-registered-20261017");
        model.setAllowedContentTypes({"application/x-avelino-type-not-registered-20261017"});
        QVERIFY(!model.canAccept());QVERIFY(model.selectedUrls().isEmpty());QVERIFY(!model.error().isEmpty());
        model.refresh();QVERIFY(!model.error().isEmpty());QVERIFY(!model.canAccept());
        model.setAllowedContentTypes({"text/plain"});QVERIFY(model.error().isEmpty());model.selectAll();QCOMPARE(model.selectedUrls().size(),1);
    }
    void resultOwnerCanDestroyTheModel(){
        QTemporaryDir root;QDir directory(root.path());put(directory.filePath("one.txt"));
        QPointer<FileChooserModel> model=new FileChooserModel;model->setAllowedContentTypes({"text/plain"});QVERIFY(model->open(QUrl::fromLocalFile(root.path())));
        model->select(row(*model,"one.txt"));connect(model,&FileChooserModel::result,this,[&]{delete model.data();});model->acceptSelection();QVERIFY(model.isNull());
    }
    void rangeToggleAndFilterUpdates(){
        QTemporaryDir root;QDir directory(root.path());put(directory.filePath("a.txt"));put(directory.filePath("b.png"));put(directory.filePath("c.txt"));
        FileChooserModel model;model.setAllowedContentTypes({"*/*"});QVERIFY(model.open(QUrl::fromLocalFile(root.path())));
        model.select(0);model.select(2,Qt::ShiftModifier);QCOMPARE(model.selectedUrls().size(),3);
        model.select(1,Qt::ControlModifier);QCOMPARE(model.selectedUrls().size(),2);
        model.setAllowedContentTypes({"image/*"});QVERIFY(model.selectedUrls().isEmpty());model.moveCurrent(1);model.selectAll();QCOMPARE(model.selectedUrls().size(),1);
    }
};
QTEST_GUILESS_MAIN(FileChooserTests)
#include "filechoosermodel.moc"

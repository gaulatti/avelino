#include "filechooserplaces.h"
#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QProcess>
#include <QSettings>
#include <QTemporaryDir>
#include <QtTest>

static QStringList recentPaths(FileChooserPlaces &places){
    QStringList result;
    for(const auto &value:places.entries()){
        const auto row=value.toMap();
        if(row["recent"].toBool()&&!row["heading"].toBool())result.append(row["url"].toUrl().toLocalFile());
    }
    return result;
}
class PlacesTests:public QObject {
    Q_OBJECT
    QTemporaryDir config;
private slots:
    void initTestCase(){QVERIFY(config.isValid());QSettings::setPath(QSettings::NativeFormat,QSettings::UserScope,config.path());}
    void init(){QSettings settings("Avelino","FileChooser");settings.clear();settings.sync();QCOMPARE(settings.status(),QSettings::NoError);}
    void ancestorUrlsAndMissingLocations(){
        QTemporaryDir root;const auto child=root.filePath("Parent Folder/日本");QVERIFY(QDir().mkpath(child));
        FileChooserPlaces places;places.refresh(child);QVERIFY(places.error().isEmpty());
        auto entries=places.entries();QVERIFY(entries.size()>=3);
        QCOMPARE(entries[0].toMap()["label"].toString(),QString::fromUtf8("日本"));
        QCOMPARE(entries[0].toMap()["url"].toUrl(),QUrl::fromLocalFile(child));
        QCOMPARE(entries[1].toMap()["url"].toUrl(),QUrl::fromLocalFile(root.filePath("Parent Folder")));
        QCOMPARE(entries.last().toMap()["url"].toUrl(),QUrl::fromLocalFile("/"));
        places.refresh(root.filePath("missing"));QVERIFY(!places.entries()[0].toMap()["available"].toBool());
        QCOMPARE(places.entries()[1].toMap()["url"].toUrl(),QUrl::fromLocalFile(root.path()));
    }
    void tenMostRecentCanonicalFoldersAndUnavailableEntries(){
        QTemporaryDir root;FileChooserPlaces places;QStringList expected;
        for(int i=0;i<12;++i){const auto folder=root.filePath(QString::number(i));QVERIFY(QDir().mkdir(folder));QVERIFY(places.rememberAcceptedFolder(folder));expected.prepend(folder);}
        expected.resize(10);QCOMPARE(recentPaths(places),expected);
        const auto older=expected[4];QVERIFY(places.rememberAcceptedFolder(older));expected.removeAll(older);expected.prepend(older);QCOMPARE(recentPaths(places),expected);
        const auto alias=root.filePath("alias");QVERIFY(QFile::link(older,alias));QVERIFY(places.rememberAcceptedFolder(alias));QCOMPARE(recentPaths(places),expected);
        QVERIFY(QDir(older).removeRecursively());places.refresh(root.path());QCOMPARE(recentPaths(places),expected);
        bool unavailable=false;for(const auto &value:places.entries()){const auto row=value.toMap();if(row["recent"].toBool()&&row["url"].toUrl()==QUrl::fromLocalFile(older))unavailable=!row["available"].toBool();}QVERIFY(unavailable);
    }
    void explicitEmptyInputAndIndependentConsumerProcesses(){
        QTemporaryDir root;const auto folder=root.filePath("Folder space");QVERIFY(QDir().mkdir(folder));
        FileChooserPlaces places;places.refresh(root.path());QVERIFY(!places.hasPathInput());
        QVERIFY(places.rememberPathInput(""));QVERIFY(places.hasPathInput());QVERIFY(places.lastPathInput().isEmpty());
        QProcess process;process.start(QCoreApplication::applicationFilePath(),{"--place-helper",config.path(),folder,"/typed but missing"});QVERIFY(process.waitForFinished());QCOMPARE(process.exitCode(),0);
        places.refresh(root.path());QCOMPARE(recentPaths(places),QStringList{folder});QCOMPARE(places.lastPathInput(),QString("/typed but missing"));
        const auto second=root.filePath("Second");QVERIFY(QDir().mkdir(second));
        QProcess first,other;
        first.start(QCoreApplication::applicationFilePath(),{"--place-helper",config.path(),folder,"/first"});
        other.start(QCoreApplication::applicationFilePath(),{"--place-helper",config.path(),second,"/second"});
        QVERIFY(first.waitForFinished());QVERIFY(other.waitForFinished());QCOMPARE(first.exitCode(),0);QCOMPARE(other.exitCode(),0);
        places.refresh(root.path());auto actual=recentPaths(places);actual.sort();auto expected=QStringList{folder,second};expected.sort();QCOMPARE(actual,expected);QVERIFY(places.error().isEmpty());
    }
    void unsupportedStorageIsReportedAndPreserved(){
        QTemporaryDir root;QSettings settings("Avelino","FileChooser");settings.setValue("version",99);settings.setValue("recentFolders",QStringList{"file:///not-a-fixture"});settings.sync();
        QFile file(settings.fileName());QVERIFY(file.open(QIODevice::ReadOnly));const auto before=file.readAll();file.close();
        FileChooserPlaces places;places.refresh(root.path());QVERIFY(!places.error().isEmpty());QVERIFY(!places.rememberAcceptedFolder(root.path()));
        QVERIFY(file.open(QIODevice::ReadOnly));QCOMPARE(file.readAll(),before);QVERIFY(recentPaths(places).isEmpty());
    }
};
int main(int argc,char **argv){
    QCoreApplication app(argc,argv);const auto args=app.arguments();
    if(args.value(1)=="--place-helper"){
        if(args.size()!=5)return 2;
        QSettings::setPath(QSettings::NativeFormat,QSettings::UserScope,args[2]);FileChooserPlaces places;
        return places.rememberAcceptedFolder(args[3])&&places.rememberPathInput(args[4])?0:1;
    }
    PlacesTests tests;return QTest::qExec(&tests,argc,argv);
}
#include "filechooserplaces.moc"

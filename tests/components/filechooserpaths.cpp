#include "filechooserpaths.h"
#include <QDir>
#include <QFile>
#include <QTemporaryDir>
#include <QtTest>

class PathsTests:public QObject {
    Q_OBJECT
    void put(const QString &path){QFile file(path);QVERIFY(file.open(QIODevice::WriteOnly));QVERIFY(file.write("Controlled path fixture\n")>0);}
private slots:
    void proposalsKeepRawInputSeparateFromNavigationAndCompletion(){
        QTemporaryDir root;QVERIFY(QDir().mkpath(root.filePath("Alpha/Child")));QVERIFY(QDir().mkdir(root.filePath("Alphabet")));QVERIFY(QDir().mkdir(root.filePath("Alpine")));
        put(root.filePath("Other.png"));FileChooserPaths paths;const auto prefix=root.filePath("Al");paths.begin(root.path(),prefix,{},{});
        QCOMPARE(paths.input(),prefix);QCOMPARE(paths.entries().size(),4);QCOMPARE(paths.selectedUrl(),QUrl::fromLocalFile(root.filePath("Alpha")));
        QCOMPARE(paths.entries()[2].toMap()["path"].toString(),root.filePath("Alpine"));QCOMPARE(paths.entries()[3].toMap()["path"].toString(),root.filePath("Alphabet"));
        paths.move(1);QCOMPARE(paths.selectedUrl(),QUrl::fromLocalFile(root.filePath("Alpine")));QCOMPARE(paths.input(),prefix);QCOMPARE(paths.completion(),prefix+"p");
        paths.setInput(root.filePath("Other.png"));QCOMPARE(paths.selectedUrl(),QUrl::fromLocalFile(root.filePath("Other.png")));
        paths.setInput(root.filePath("Missing"));QVERIFY(paths.entries().isEmpty());QVERIFY(paths.selectedUrl().isEmpty());
    }
    void observedCurrentLocationAndIndependentRecentTargets(){
        QTemporaryDir root;QVERIFY(QDir().mkpath(root.filePath("Alpha/Child")));put(root.filePath("Alpha/Child/Child.txt"));
        QVariantList recent{QVariantMap{{"path",root.filePath("Alpha")},{"available",true}},QVariantMap{{"path",root.filePath("missing")},{"available",false}}};
        FileChooserPaths paths;paths.begin(root.filePath("Alpha"),"Child",recent,{});QCOMPARE(paths.selectedUrl(),QUrl::fromLocalFile(root.filePath("Alpha/Child")));
        paths.begin(root.filePath("Alpha/Child"),"Child",recent,{});QCOMPARE(paths.selectedUrl(),QUrl::fromLocalFile(root.filePath("Alpha/Child/Child.txt")));
        paths.setInput("..");QVERIFY(paths.entries().isEmpty());paths.setInput("../");QCOMPARE(paths.selectedUrl(),QUrl::fromLocalFile(root.filePath("Alpha/Child")));
        paths.setInput("../A.txt");QVERIFY(paths.selectedUrl().isEmpty());paths.setInput("");QVERIFY(paths.selectedUrl().isEmpty());QCOMPARE(paths.entries().size(),3);
        paths.move(1);QCOMPARE(paths.selectedUrl(),QUrl::fromLocalFile(root.filePath("Alpha")));paths.move(1);QCOMPARE(paths.selectedUrl(),QUrl::fromLocalFile(root.filePath("Alpha")));
    }
};
QTEST_GUILESS_MAIN(PathsTests)
#include "filechooserpaths.moc"

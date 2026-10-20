#include "inheritedcontrol.h"
#include "radiogroupbase.h"
#include "proposalrow.h"
#include "proposalcolumn.h"
#include "proposaloverlay.h"
#include "apptabrow.h"
#include "chartrenderer.h"
#include "spotlightrows.h"
#include "medialibrarybase.h"
#include "softwarecontentmask.h"
#include <QQmlComponent>
#include <QQmlEngine>
#include <QQuickWindow>
#include <QtTest>

class ItemLifetimeTests:public QObject {
    Q_OBJECT
private slots:
    void attachedItemCanBeDestroyed_data() {
        QTest::addColumn<QString>("kind");QTest::addColumn<bool>("disabled");QTest::addColumn<bool>("child");
        for(const auto &kind:QStringList{"inherited","radio","row","column","overlay","tabs","charts","spotlight","media","mask"})
            for(bool disabled:{false,true})for(bool child:{false,true})
                QTest::newRow(qPrintable(kind+QString("-disabled%1-child%2").arg(disabled).arg(child)))<<kind<<disabled<<child;
    }
    void attachedItemCanBeDestroyed() {
        QFETCH(QString,kind);QFETCH(bool,disabled);QFETCH(bool,child);
        QQmlEngine engine;engine.addImportPath(AVELINO_LIFETIME_IMPORT_PATH);
        QQmlComponent registration(&engine);
        registration.setData("import QtQuick; import Avelino; Item {}",QUrl());
        QScopedPointer<QObject> root(registration.create());QVERIFY2(root,qPrintable(registration.errorString()));
        QQuickWindow window;QQuickControl parent(window.contentItem());parent.setEnabled(!disabled);
        auto font=parent.font();font.setPointSizeF(28);parent.setFont(font);
        QQuickItem *item=nullptr;
        if(kind=="inherited")item=new InheritedControl(&parent);
        else if(kind=="radio")item=new RadioGroupBase(&parent);
        else if(kind=="row")item=new ProposalRow(&parent);
        else if(kind=="column")item=new ProposalColumn(&parent);
        else if(kind=="overlay")item=new ProposalOverlay(&parent);
        else if(kind=="tabs")item=new AppTabRow(&parent);
        else if(kind=="charts")item=new ChartRenderer(&parent);
        else if(kind=="spotlight")item=new SpotlightRows(&parent);
        else if(kind=="media")item=new MediaLibraryBase(&parent);
        else if(kind=="mask")item=new SoftwareContentMask(&parent);
        QVERIFY(item);QCOMPARE(item->isEnabled(),!disabled);
        QScopedPointer<QSignalSpy> styleNotifications;
        if(kind=="inherited"||kind=="radio") {
            styleNotifications.reset(new QSignalSpy(item,SIGNAL(resolvedTextColorChanged())));
            QVERIFY(styleNotifications->isValid());
        }
        QPointer<QQuickItem> observer(item),childObserver;
        if(child)childObserver=new QQuickItem(item);
        delete item;QVERIFY(observer.isNull());QVERIFY(childObserver.isNull());
        if(styleNotifications)QCOMPARE(styleNotifications->count(),0);
    }
};
QTEST_MAIN(ItemLifetimeTests)
#include "itemlifetime.moc"

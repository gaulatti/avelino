#include "herocarouselbase.h"
#include <QQmlEngine>
#include <QQuickView>
#include <QTest>
#include <cmath>

class HeroCarouselTests:public QObject {
    Q_OBJECT
    bool load(QQuickView &view,bool fitHeight=false,bool publicView=false){
        view.engine()->addImportPath(QStringLiteral(AVELINO_HERO_IMPORT_PATH));
        view.setSource(QUrl("qrc:/hero-carousel-tests/herocarousel-fixture.qml"));
        if(view.status()!=QQuickView::Ready){qWarning()<<view.errors();return false;}
        if(publicView)view.rootObject()->setProperty("publicView",true);
        if(fitHeight)viewport(view)->resetHeight();
        view.resize(640,400);view.show();return QTest::qWaitForWindowExposed(&view);
    }
    HeroCarouselBase *presenter(QQuickView &view){return view.rootObject()->property("presenter").value<HeroCarouselBase*>();}
    QQuickItem *viewport(QQuickView &view){return view.rootObject()->property("viewport").value<QQuickItem*>();}
private slots:
    void viewportAllocationAndLazyCallerLifetime(){
        QQuickView view;QVERIFY(load(view));auto model=presenter(view);QVERIFY(model);
        QTRY_COMPARE(model->activeCount(),1);QCOMPARE(model->itemCount(),3);QCOMPARE(model->documentWidth(),1043);
        QCOMPARE(model->instantiatedCount(),1);QCOMPARE(model->itemAt(0)->width(),337);QCOMPARE(model->itemAt(0)->height(),80);
        QCOMPARE(model->itemAt(0)->mapToItem(model,QPointF()),QPointF(0,50));
        QPointer<QQuickItem> first=model->itemAt(0);const auto token=first->property("token").toInt();
        viewport(view)->setProperty("contentX",706);QTRY_VERIFY(model->itemAt(2));QTRY_COMPARE(model->activeCount(),1);
        QCOMPARE(model->itemAt(2)->mapToItem(model,QPointF()),QPointF(706,30));QVERIFY(!first->property("slideActive").toBool());
        viewport(view)->setProperty("contentX",0);QTRY_VERIFY(first->property("slideActive").toBool());
        QCOMPARE(model->itemAt(0),first.data());QCOMPARE(first->property("token").toInt(),token);
        viewport(view)->setWidth(160);QTRY_COMPARE(model->documentWidth(),512);QTRY_COMPARE(first->width(),160);
        viewport(view)->setWidth(0);QTRY_COMPARE(model->activeCount(),0);QVERIFY(first);viewport(view)->setWidth(337);QTRY_COMPARE(model->activeCount(),1);QCOMPARE(model->itemAt(0),first.data());
    }
    void fixedContentCentersInsideViewportAllocation(){
        QQuickView view;QVERIFY(load(view));view.rootObject()->setProperty("fixedSlides",true);auto model=presenter(view);
        QTRY_COMPARE(model->activeCount(),1);QTRY_COMPARE(model->itemAt(0)->width(),91);
        QCOMPARE(model->itemAt(0)->mapToItem(model,QPointF()),QPointF(123,50));
        viewport(view)->setWidth(37);QTRY_COMPARE(model->documentWidth(),143);QTRY_COMPARE(model->itemAt(0)->mapToItem(model,QPointF()).x(),-27);
    }
    void allocationOriginTracksFractionalScenePlacement(){
        QQuickView view;QVERIFY(load(view));auto model=presenter(view);QTRY_COMPARE(model->activeCount(),1);
        auto control=viewport(view);control->setPosition(QPointF(20.5,20.5));
        const auto origin=view.devicePixelRatio()==1?21.0:20.5;
        QTRY_COMPARE(model->itemAt(0)->mapToScene(QPointF()),QPointF(origin,origin+50));
        control->setPosition(QPointF(21,21));QTRY_COMPARE(model->itemAt(0)->mapToScene(QPointF()),QPointF(21,71));
    }
    void identitiesSurviveEditsReorderAndEmptyRestore(){
        QQuickView view;QVERIFY(load(view));auto model=presenter(view);QTRY_COMPARE(model->activeCount(),1);
        QPointer<QQuickItem> first=model->itemAt(0);viewport(view)->setProperty("contentX",706);QTRY_VERIFY(model->itemAt(2));QPointer<QQuickItem> last=model->itemAt(2);
        viewport(view)->setProperty("contentX",0);
        auto values=view.engine()->evaluate("[{id:'c',width:91,height:120},{id:'a',width:91,height:80},{id:'b',width:91,height:100}]");view.rootObject()->setProperty("rows",QVariant::fromValue(values));
        QTRY_COMPARE(model->itemAt(0),last.data());QCOMPARE(model->itemAt(1),first.data());
        values=view.engine()->evaluate("[{id:'c',width:91,height:170},{id:'a',width:91,height:80},{id:'b',width:91,height:100}]");view.rootObject()->setProperty("rows",QVariant::fromValue(values));QTRY_COMPARE(last->height(),170);
        view.rootObject()->setProperty("rows",QVariant::fromValue(view.engine()->evaluate("[]")));QTRY_COMPARE(model->itemCount(),0);QTRY_COMPARE(model->documentWidth(),0);QCOMPARE(model->activeCount(),0);QTest::qWait(50);QVERIFY(first);QVERIFY(last);QVERIFY(!first->property("slideActive").toBool());QVERIFY(!last->property("slideActive").toBool());
        view.rootObject()->setProperty("rows",QVariant::fromValue(view.engine()->evaluate("[{id:'a',width:91,height:80},{id:'b',width:91,height:100},{id:'c',width:91,height:120}]")));QTRY_COMPARE(model->itemCount(),3);QTRY_COMPARE(model->itemAt(0),first.data());QCOMPARE(model->itemAt(2),last.data());QTRY_VERIFY(first->property("slideActive").toBool());
    }
    void zeroViewportDoesNotCreateCallerState(){
        QQuickView view;QVERIFY(load(view));auto model=presenter(view);QTRY_COMPARE(model->activeCount(),1);
        view.rootObject()->setProperty("rows",QVariant::fromValue(view.engine()->evaluate("[]")));QTRY_COMPARE(model->itemCount(),0);
        viewport(view)->setWidth(0);view.rootObject()->setProperty("rows",QVariant::fromValue(view.engine()->evaluate("[{id:'fresh',height:80}]")));QTRY_COMPARE(model->itemCount(),1);QTest::qWait(30);QCOMPARE(model->instantiatedCount(),0);
        viewport(view)->setHeight(0);viewport(view)->setWidth(337);QTest::qWait(30);QCOMPARE(model->instantiatedCount(),0);
        viewport(view)->setHeight(180);QTRY_COMPARE(model->activeCount(),1);
    }
    void rightToLeftPlacesLogicalFirstAtDocumentEnd(){
        QQuickView view;QVERIFY(load(view));auto model=presenter(view);QTRY_COMPARE(model->activeCount(),1);QPointer<QQuickItem> first=model->itemAt(0);
        model->setMirrored(true);viewport(view)->setProperty("contentX",706);QTRY_VERIFY(first->property("slideActive").toBool());
        QTRY_COMPARE(first->mapToItem(model,QPointF()).x(),706);QCOMPARE(model->itemAt(0),first.data());
        viewport(view)->setProperty("contentX",0);QTRY_VERIFY(model->itemAt(2));QTRY_COMPARE(model->itemAt(2)->mapToItem(model,QPointF()).x(),0);
    }
    void explicitIdentityFunctionPreservesCallerAcrossValueChanges(){
        QQuickView view;QVERIFY(load(view));auto model=presenter(view);QTRY_COMPARE(model->activeCount(),1);
        view.rootObject()->setProperty("identity",QVariant::fromValue(view.engine()->evaluate("(function(value){return value.code;})")));
        view.rootObject()->setProperty("rows",QVariant::fromValue(view.engine()->evaluate("[{code:1,height:80},{code:2,height:100}]")));QTRY_COMPARE(model->itemCount(),2);QTRY_VERIFY(model->itemAt(0));
        QPointer<QQuickItem> first=model->itemAt(0);const auto token=first->property("token").toInt();
        view.rootObject()->setProperty("rows",QVariant::fromValue(view.engine()->evaluate("[{code:1,height:140},{code:2,height:100}]")));QTRY_COMPARE(first->height(),140);QCOMPARE(model->itemAt(0),first.data());QCOMPARE(first->property("token").toInt(),token);
    }
    void fittedHeightFollowsFirstSlideRatherThanLargestVisitedSlide(){
        QQuickView view;QVERIFY(load(view,true));auto model=presenter(view);QTRY_COMPARE(model->activeCount(),1);QTRY_COMPARE(viewport(view)->height(),80);
        viewport(view)->setProperty("contentX",706);QTRY_VERIFY(model->itemAt(2));QCOMPARE(viewport(view)->height(),80);QCOMPARE(model->itemAt(2)->height(),120);
        viewport(view)->setProperty("contentX",0);view.rootObject()->setProperty("rows",QVariant::fromValue(view.engine()->evaluate("[{id:'a',width:91,height:80},{id:'b',width:91,height:100},{id:'c',width:91,height:200}]")));QTest::qWait(30);QCOMPARE(viewport(view)->height(),80);
        view.rootObject()->setProperty("rows",QVariant::fromValue(view.engine()->evaluate("[{id:'c',width:91,height:200},{id:'a',width:91,height:80},{id:'b',width:91,height:100}]")));QTRY_COMPARE(viewport(view)->height(),200);
    }
    void publicViewOwnsTargetsAndKeepsCallerState(){
        QQuickView view;QVERIFY(load(view,false,true));auto model=presenter(view);auto control=viewport(view);QVERIFY(model&&control);
        QTRY_COMPARE(model->activeCount(),1);QTRY_COMPARE(control->property("contentWidth").toReal(),1043);
        QPointer<QQuickItem> first=model->itemAt(0);const auto token=first->property("token").toInt();
        QVERIFY(QMetaObject::invokeMethod(control,"positionViewAtEnd"));QTRY_VERIFY(model->itemAt(2));QTRY_VERIFY(model->itemAt(2)->property("slideActive").toBool());
        QCOMPARE(model->itemAt(2)->mapToItem(control,QPointF()).x(),0);
        QVERIFY(QMetaObject::invokeMethod(control,"positionViewAtBeginning"));QTRY_VERIFY(first->property("slideActive").toBool());QCOMPARE(first->mapToItem(control,QPointF()).x(),0);QCOMPARE(first->property("token").toInt(),token);
    }
    void publicViewHeightFit(){
        QQuickView view;QVERIFY(load(view,true,true));auto model=presenter(view);auto control=viewport(view);QTRY_COMPARE(model->activeCount(),1);QTRY_COMPARE(control->height(),80);
        QVERIFY(QMetaObject::invokeMethod(control,"positionViewAtEnd"));QTRY_VERIFY(model->itemAt(2));QCOMPARE(control->height(),80);
        QVERIFY(QMetaObject::invokeMethod(control,"positionViewAtBeginning"));
    }
    void publicRightToLeftKeepsLogicalOrderAndTargets(){
        QQuickView view;QVERIFY(load(view,false,true));auto model=presenter(view);auto control=viewport(view);
        QTRY_COMPARE(model->activeCount(),1);QPointer<QQuickItem> first=model->itemAt(0);
        view.rootObject()->setProperty("mirrored",true);QTRY_VERIFY(model->mirrored());
        QTRY_VERIFY(first->property("slideActive").toBool());QTRY_COMPARE(first->mapToItem(control,QPointF()).x(),0);
        QVERIFY(QMetaObject::invokeMethod(control,"positionViewAtEnd"));QTRY_VERIFY(model->itemAt(2));
        QTRY_VERIFY(model->itemAt(2)->property("slideActive").toBool());QCOMPARE(model->itemAt(2)->mapToItem(control,QPointF()).x(),0);
        QVERIFY(QMetaObject::invokeMethod(control,"positionViewAtBeginning"));QTRY_VERIFY(first->property("slideActive").toBool());
        QCOMPARE(first->mapToItem(control,QPointF()).x(),0);QCOMPARE(model->itemAt(0),first.data());
    }
    void publicPointerReleaseSettlesOnAViewBoundary(){
        QQuickView view;QVERIFY(load(view,false,true));auto model=presenter(view);auto control=viewport(view);QTRY_COMPARE(model->activeCount(),1);
        QTest::mousePress(&view,Qt::LeftButton,Qt::NoModifier,QPoint(300,110));
        for(int x=280;x>=40;x-=20){QTest::mouseMove(&view,QPoint(x,110),16);}
        QTest::mouseRelease(&view,Qt::LeftButton,Qt::NoModifier,QPoint(40,110));
        QTRY_VERIFY(!control->property("moving").toBool());const auto offset=control->property("contentX").toReal();
        QVERIFY2(offset>0,qPrintable(QString::number(offset)));QCOMPARE(std::fmod(offset,353.0),0);
    }
    void ownerRemovalDuringActivityCallback(){
        QQuickView view;QVERIFY(load(view));QPointer<HeroCarouselBase> model=presenter(view);QTRY_COMPARE(model->activeCount(),1);
        view.rootObject()->setProperty("removeOnInactive",true);viewport(view)->setProperty("contentX",706);QTRY_VERIFY(model.isNull());
    }
    void ownerRemovalDuringDataCallback(){
        QQuickView view;QVERIFY(load(view));QPointer<HeroCarouselBase> model=presenter(view);QTRY_COMPARE(model->activeCount(),1);
        view.rootObject()->setProperty("removeOnData",true);view.rootObject()->setProperty("rows",QVariant::fromValue(view.engine()->evaluate("[{id:'a',width:91,height:160}]")));QTRY_VERIFY(model.isNull());
    }
};
QTEST_MAIN(HeroCarouselTests)
#include "herocarousel.moc"

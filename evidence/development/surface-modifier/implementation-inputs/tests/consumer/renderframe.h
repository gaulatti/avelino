#pragma once
#include <QCoreApplication>
#include <QElapsedTimer>
#include <QImage>
#include <QQuickItem>
#include <QQuickWindow>
#include <QSignalSpy>
#include <QVariant>
#include <functional>

// Async Shape paths may still describe the previous geometry after a frame was
// displayed. Ready path/geometry can also precede the first complete outline
// readback on GL. Require unchanged ready observations and two byte-identical
// window readbacks; this never changes an expected image or comparison tolerance.
static bool waitForShapeFrame(QQuickWindow *window,int timeout=5000) {
    QElapsedTimer elapsed;elapsed.start();
    QList<QVariantList> previous;
    QImage previousPixels;
    bool previousReady=false;
    while(elapsed.elapsed()<timeout) {
        QSignalSpy swapped(window,&QQuickWindow::frameSwapped);
        window->update();
        if(swapped.isEmpty() && !swapped.wait(qMax(1,timeout-int(elapsed.elapsed()))))return false;
        QCoreApplication::processEvents();
        QList<QVariantList> observed;
        bool processing=false;
        std::function<void(QQuickItem*)> visit=[&](QQuickItem *item){
            if(!item->isVisible())return;
            if(item->inherits("QQuickShape") && item->width()>0 && item->height()>0) {
                const int status=item->property("status").toInt();
                processing|=item->property("asynchronous").toBool() && status==2;
                observed.append(QVariantList{QVariant::fromValue(qulonglong(quintptr(item))),
                    item->x(),item->y(),item->width(),item->height(),status,
                    item->property("outerPath"),item->property("borderPath")});
            }
            for(auto child:item->childItems())visit(child);
        };
        visit(window->contentItem());
        const auto pixels=processing ? QImage():window->grabWindow();
        if(!pixels.isNull() && previousReady && observed==previous && pixels==previousPixels)return true;
        previousReady=!pixels.isNull();previous=observed;previousPixels=pixels;
    }
    return false;
}

#pragma once
#include <QCoreApplication>
#include <QElapsedTimer>
#include <QQuickItem>
#include <QQuickWindow>
#include <QSignalSpy>
#include <QVariant>
#include <functional>

// Async Shape paths may still describe the previous geometry after a frame was
// displayed. Observe processing on the visual tree, then require two displayed
// frames with unchanged ready path/geometry observations before capturing it.
static bool waitForShapeFrame(QQuickWindow *window,int timeout=5000) {
    QElapsedTimer elapsed;elapsed.start();
    QList<QVariantList> previous;
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
        if(!processing && previousReady && observed==previous)return true;
        previousReady=!processing;previous=observed;
    }
    return false;
}

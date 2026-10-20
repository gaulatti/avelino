#pragma once
#include <QJSValue>
#include <QHash>
#include <QPointer>
#include <QQmlComponent>
#include <QQmlContext>
#include <QQuickItem>
#include <QtQml/qqmlregistration.h>
#include <memory>

class HeroSlideContext : public QObject {
    Q_OBJECT
    Q_PROPERTY(QJSValue slideData READ slideData NOTIFY dataChanged)
    Q_PROPERTY(int slideIndex READ slideIndex NOTIFY dataChanged)
    Q_PROPERTY(bool slideActive READ slideActive NOTIFY activeChanged)
public:
    using QObject::QObject;
    QJSValue slideData()const{return data;}
    int slideIndex()const{return index;}
    bool slideActive()const{return active;}
    QJSValue data;
    int index=0;
    bool active=false;
signals:
    void dataChanged();
    void activeChanged();
};

// The viewport owns scrolling; this item owns caller identity and presentation.
class HeroCarouselBase : public QQuickItem {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QJSValue items READ items WRITE setItems NOTIFY itemsChanged)
    Q_PROPERTY(QJSValue itemIdentity READ itemIdentity WRITE setItemIdentity NOTIFY itemsChanged)
    Q_PROPERTY(QQmlComponent* slide READ slide WRITE setSlide NOTIFY slideChanged REQUIRED)
    Q_PROPERTY(QQuickItem* viewport READ viewport WRITE setViewport NOTIFY viewportChanged REQUIRED)
    Q_PROPERTY(bool mirrored READ mirrored WRITE setMirrored NOTIFY configurationChanged)
    Q_PROPERTY(qreal documentWidth READ documentWidth NOTIFY metricsChanged)
    Q_PROPERTY(qreal naturalHeight READ naturalHeight NOTIFY metricsChanged)
    Q_PROPERTY(int itemCount READ itemCount NOTIFY itemCountChanged)
    Q_PROPERTY(int instantiatedCount READ instantiatedCount NOTIFY metricsChanged)
    Q_PROPERTY(int activeCount READ activeCount NOTIFY metricsChanged)
public:
    explicit HeroCarouselBase(QQuickItem *parent=nullptr);
    ~HeroCarouselBase()override;
    QJSValue items()const{return m_items;}
    QJSValue itemIdentity()const{return m_identity;}
    QQmlComponent *slide()const{return m_slide;}
    QQuickItem *viewport()const{return m_viewportItem;}
    bool mirrored()const{return m_mirrored;}
    qreal documentWidth()const{return m_documentWidth;}
    qreal naturalHeight()const{return m_naturalHeight;}
    int itemCount()const{return int(m_entries.size());}
    int instantiatedCount()const;
    int activeCount()const;
    void setItems(const QJSValue &value);
    void setItemIdentity(const QJSValue &value);
    void setSlide(QQmlComponent *value);
    void setViewport(QQuickItem *value);
    void setMirrored(bool value);
    Q_INVOKABLE void layout();
    Q_INVOKABLE QQuickItem *itemAt(int index)const;
    Q_INVOKABLE QVariantMap layoutSnapshot()const;
signals:
    void itemsChanged();
    void itemCountChanged();
    void slideChanged();
    void viewportChanged();
    void configurationChanged();
    void metricsChanged();
protected:
    void componentComplete()override;
    void geometryChange(const QRectF &next,const QRectF &previous)override;
    void updatePolish()override{layout();}
private:
    struct Entry {
        QString key;
        QJSValue data;
        QPointer<QQuickItem> cell,item;
        QPointer<QQmlContext> context;
        QPointer<HeroSlideContext> roles;
        bool explicitWidth=false,explicitHeight=false;
        qreal measuredWidth=0,measuredHeight=0;
        ~Entry();
    };
    using EntryPtr=std::shared_ptr<Entry>;
    void reconcile();
    void instantiate(const EntryPtr &entry,int index);
    void updateRoles(const EntryPtr &entry,int index);
    void setActive(const EntryPtr &entry,bool value);
    void measure(const EntryPtr &entry,qreal offered);
    QRectF visibleRect()const;
    void attachWindow(QQuickWindow *window);
    void refreshViewport();
    QJSValue m_items,m_identity;
    QPointer<QQmlComponent> m_slide;
    QPointer<QQuickItem> m_viewportItem;
    QList<EntryPtr> m_entries;
    QHash<QString,EntryPtr> m_retired;
    QList<QMetaObject::Connection> m_windowConnections;
    QRectF m_visibleRect;
    QPointF m_sceneOrigin;
    qreal m_devicePixelRatio=0;
    qreal m_documentWidth=0,m_naturalHeight=0;
    bool m_mirrored=false,m_layingOut=false,m_complete=false,m_initialized=false,m_dirty=false;
};

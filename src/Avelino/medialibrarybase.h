#pragma once
#include <QJSValue>
#include <QPointer>
#include <QQmlComponent>
#include <QQmlContext>
#include <QQuickItem>
#include <QtQml/qqmlregistration.h>
#include <memory>

class MediaTileContext : public QObject {
    Q_OBJECT
    Q_PROPERTY(QJSValue tileData READ tileData NOTIFY dataChanged)
    Q_PROPERTY(int tileIndex READ tileIndex NOTIFY dataChanged)
    Q_PROPERTY(bool tileActive READ tileActive NOTIFY activeChanged)
public:
    using QObject::QObject;
    QJSValue tileData() const{return data;}
    int tileIndex() const{return index;}
    bool tileActive() const{return active;}
    QJSValue data;
    int index=0;
    bool active=false;
signals:
    void dataChanged();
    void activeChanged();
};

// Owns retained caller tiles; viewport changes activate existing objects.
class MediaLibraryBase : public QQuickItem {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QJSValue items READ items WRITE setItems NOTIFY itemsChanged)
    Q_PROPERTY(QJSValue itemIdentity READ itemIdentity WRITE setItemIdentity NOTIFY itemsChanged)
    Q_PROPERTY(QQmlComponent* tile READ tile WRITE setTile NOTIFY tileChanged REQUIRED)
    Q_PROPERTY(qreal minimumTileWidth READ minimumTileWidth WRITE setMinimumTileWidth NOTIFY configurationChanged)
    Q_PROPERTY(bool mirrored READ mirrored WRITE setMirrored NOTIFY configurationChanged)
    Q_PROPERTY(qreal naturalWidth READ naturalWidth NOTIFY metricsChanged)
    Q_PROPERTY(qreal contentHeight READ contentHeight NOTIFY metricsChanged)
    Q_PROPERTY(int columns READ columns NOTIFY metricsChanged)
    Q_PROPERTY(qreal columnWidth READ columnWidth NOTIFY metricsChanged)
    Q_PROPERTY(int itemCount READ itemCount NOTIFY itemsChanged)
    Q_PROPERTY(int instantiatedCount READ instantiatedCount NOTIFY metricsChanged)
    Q_PROPERTY(int activeCount READ activeCount NOTIFY metricsChanged)
public:
    explicit MediaLibraryBase(QQuickItem *parent=nullptr);
    ~MediaLibraryBase() override;
    QJSValue items() const{return m_items;}
    QJSValue itemIdentity() const{return m_identity;}
    QQmlComponent *tile() const{return m_tile;}
    qreal minimumTileWidth() const{return m_minimum;}
    bool mirrored() const{return m_mirrored;}
    qreal naturalWidth() const{return m_naturalWidth;}
    qreal contentHeight() const{return m_contentHeight;}
    int columns() const{return m_columns;}
    qreal columnWidth() const{return m_columnWidth;}
    int itemCount() const{return int(m_entries.size());}
    int instantiatedCount() const;
    int activeCount() const;
    void setItems(const QJSValue &value);
    void setItemIdentity(const QJSValue &value);
    void setTile(QQmlComponent *value);
    void setMinimumTileWidth(qreal value);
    void setMirrored(bool value);
    Q_INVOKABLE void layout();
    Q_INVOKABLE QQuickItem *itemAt(int index) const;
    Q_INVOKABLE QVariantMap layoutSnapshot() const;
signals:
    void itemsChanged();
    void tileChanged();
    void configurationChanged();
    void metricsChanged();
protected:
    void componentComplete() override;
    void geometryChange(const QRectF &next,const QRectF &previous) override;
    void updatePolish() override{layout();}
private:
    struct Entry {
        QString key;
        QJSValue data;
        QPointer<QQuickItem> cell,item;
        QPointer<QQmlContext> context;
        QPointer<MediaTileContext> roles;
        bool explicitWidth=false,explicitHeight=false,measured=false;
        qreal measuredWidth=0,measuredHeight=0;
        ~Entry();
    };
    using EntryPtr=std::shared_ptr<Entry>;
    void reconcile();
    void instantiate(const EntryPtr &entry,int index);
    void updateRoles(const EntryPtr &entry,int index);
    void setActive(const EntryPtr &entry,bool value);
    qreal measure(const EntryPtr &entry,qreal offered);
    QRectF visibleRect() const;
    void attachWindow(QQuickWindow *window);
    void refreshViewport();
    QJSValue m_items,m_identity;
    QPointer<QQmlComponent> m_tile;
    QList<EntryPtr> m_entries;
    QMetaObject::Connection m_frameConnection;
    QRectF m_viewport;
    qreal m_minimum=160,m_naturalWidth=0,m_contentHeight=0,m_columnWidth=0,m_estimate=40;
    int m_columns=0;
    bool m_mirrored=false,m_layingOut=false,m_complete=false,m_initialized=false;
};

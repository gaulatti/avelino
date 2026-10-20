#pragma once
#include <QJSValue>
#include <QPointer>
#include <QQmlComponent>
#include <QQmlContext>
#include <QQuickItem>
#include <QFont>
#include <QColor>
#include <QtQml/qqmlregistration.h>
#include <memory>

class SpotlightRowContext : public QObject {
    Q_OBJECT
    Q_PROPERTY(QJSValue rowData READ rowData NOTIFY dataChanged)
    Q_PROPERTY(int rowIndex READ rowIndex NOTIFY dataChanged)
    Q_PROPERTY(bool rowActive READ rowActive NOTIFY activeChanged)
    Q_PROPERTY(QFont rowFont READ rowFont NOTIFY presentationChanged)
    Q_PROPERTY(QColor rowForeground READ rowForeground NOTIFY presentationChanged)
public:
    using QObject::QObject;
    QJSValue rowData() const{return data;}
    int rowIndex() const{return index;}
    bool rowActive() const{return active;}
    QFont rowFont() const{return font;}
    QColor rowForeground() const{return foreground;}
    QJSValue data;
    QFont font;
    QColor foreground;
    int index=0;
    bool active=false;
signals:
    void dataChanged();
    void activeChanged();
    void presentationChanged();
};

class SpotlightRows : public QQuickItem {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QJSValue items READ items WRITE setItems NOTIFY itemsChanged)
    Q_PROPERTY(QJSValue itemIdentity READ itemIdentity WRITE setItemIdentity NOTIFY itemsChanged)
    Q_PROPERTY(QQmlComponent* row READ row WRITE setRow NOTIFY rowChanged REQUIRED)
    Q_PROPERTY(bool mirrored READ mirrored WRITE setMirrored NOTIFY presentationChanged)
    Q_PROPERTY(QFont rowFont READ rowFont WRITE setRowFont NOTIFY presentationChanged)
    Q_PROPERTY(QColor rowForeground READ rowForeground WRITE setRowForeground NOTIFY presentationChanged)
    Q_PROPERTY(qreal contentHeight READ contentHeight NOTIFY metricsChanged)
    Q_PROPERTY(int count READ count NOTIFY itemsChanged)
    Q_PROPERTY(int instantiatedCount READ instantiatedCount NOTIFY metricsChanged)
    Q_PROPERTY(int activeCount READ activeCount NOTIFY metricsChanged)
    Q_PROPERTY(int cachedCount READ cachedCount NOTIFY metricsChanged)
public:
    explicit SpotlightRows(QQuickItem *parent=nullptr);
    ~SpotlightRows() override;
    QJSValue items() const{return m_items;}
    QJSValue itemIdentity() const{return m_identity;}
    QQmlComponent *row() const{return m_row;}
    bool mirrored() const{return m_mirrored;}
    QFont rowFont() const{return m_font;}
    QColor rowForeground() const{return m_foreground;}
    qreal contentHeight() const{return m_contentHeight;}
    int count() const{return int(m_entries.size());}
    int instantiatedCount() const;
    int activeCount() const;
    int cachedCount() const{return int(m_retired.size());}
    void setItems(const QJSValue &value);
    void setItemIdentity(const QJSValue &value);
    void setRow(QQmlComponent *value);
    void setMirrored(bool value);
    void setRowFont(const QFont &value);
    void setRowForeground(const QColor &value);
    Q_INVOKABLE void layout();
    Q_INVOKABLE QQuickItem *itemAt(int index) const;
    Q_INVOKABLE QQuickItem *cellAt(int index) const;
    Q_INVOKABLE QVariantMap layoutSnapshot() const;
signals:
    void itemsChanged();
    void rowChanged();
    void presentationChanged();
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
        QPointer<SpotlightRowContext> roles;
        bool explicitWidth=false,explicitHeight=false;
        qreal measuredWidth=0,measuredHeight=0;
        ~Entry();
    };
    using EntryPtr=std::shared_ptr<Entry>;
    void reconcile();
    void instantiate(const EntryPtr &entry,int index);
    void updateRoles(const EntryPtr &entry,int index);
    void setActive(const EntryPtr &entry,bool active);
    void measure(const EntryPtr &entry);
    QRectF visibleRect() const;
    void attachWindow(QQuickWindow *window);
    void refreshViewport();
    QJSValue m_items,m_identity;
    QPointer<QQmlComponent> m_row;
    QList<EntryPtr> m_entries;
    QHash<QString,EntryPtr> m_retired;
    QMetaObject::Connection m_frame;
    QRectF m_viewport;
    QFont m_font;
    QColor m_foreground;
    qreal m_contentHeight=12,m_estimate=38;
    bool m_mirrored=false,m_complete=false,m_initialized=false,m_layingOut=false;
};

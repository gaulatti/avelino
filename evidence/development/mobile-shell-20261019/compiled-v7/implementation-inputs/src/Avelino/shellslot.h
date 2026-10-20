#pragma once
#include <QPointer>
#include <QQuickItem>
#include <QQmlComponent>
#include <QtQml/qqmlregistration.h>

// A retained caller slot. Unlike a Loader with an explicit size, the wrapper's
// allocated rectangle does not overwrite a fixed child rectangle.
class ShellSlot : public QQuickItem {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QQmlComponent *sourceComponent READ sourceComponent WRITE setSourceComponent NOTIFY sourceComponentChanged)
    Q_PROPERTY(QQuickItem *item READ item NOTIFY itemChanged)
    Q_PROPERTY(qreal minimumWidth READ minimumWidth NOTIFY metricsChanged)
    Q_PROPERTY(qreal minimumHeight READ minimumHeight NOTIFY metricsChanged)
    Q_PROPERTY(bool fillsHeight READ fillsHeight NOTIFY metricsChanged)
public:
    explicit ShellSlot(QQuickItem *parent = nullptr);
    QQmlComponent *sourceComponent() const { return m_component; }
    void setSourceComponent(QQmlComponent *component);
    QQuickItem *item() const { return m_item; }
    qreal minimumWidth() const { return m_minimumWidth; }
    qreal minimumHeight() const { return m_minimumHeight; }
    bool fillsHeight() const { return m_fillsHeight; }
    Q_INVOKABLE void layout();
signals:
    void sourceComponentChanged();
    void itemChanged();
    void metricsChanged();
protected:
    void componentComplete() override;
    void updatePolish() override { layout(); }
private:
    void createItem();
    QPointer<QQmlComponent> m_component;
    QPointer<QQuickItem> m_item;
    QList<QMetaObject::Connection> m_connections;
    QMetaObject::Connection m_statusConnection;
    qreal m_fixedWidth = 0, m_fixedHeight = 0;
    qreal m_minimumWidth = 0, m_minimumHeight = 0;
    bool m_fillsHeight = false, m_layingOut = false;
    bool m_explicitWidth = false, m_explicitHeight = false;
};

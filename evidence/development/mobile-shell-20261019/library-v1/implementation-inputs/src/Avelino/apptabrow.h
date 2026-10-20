#pragma once
#include <QQuickItem>
#include <QPointer>
#include <QtQml/qqmlregistration.h>

class AppTabRow : public QQuickItem {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QQuickItem *proposalOwner READ proposalOwner WRITE setProposalOwner NOTIFY configurationChanged)
    Q_PROPERTY(qreal proposedWidth READ proposedWidth WRITE setProposedWidth NOTIFY configurationChanged)
    Q_PROPERTY(bool mirrored READ mirrored WRITE setMirrored NOTIFY configurationChanged)
    Q_PROPERTY(qreal naturalWidth READ naturalWidth NOTIFY metricsChanged)
    Q_PROPERTY(qreal minimumWidth READ minimumWidth NOTIFY metricsChanged)
public:
    explicit AppTabRow(QQuickItem *parent=nullptr);
    QQuickItem *proposalOwner() const{return m_owner;}
    void setProposalOwner(QQuickItem *value){if(value==m_owner)return;m_owner=value;emit configurationChanged();polish();}
    qreal proposedWidth() const{return m_proposal;}
    bool mirrored() const{return m_mirrored;}
    qreal naturalWidth() const{return m_natural;}
    qreal minimumWidth() const{return m_minimum;}
    void setProposedWidth(qreal value);
    void setMirrored(bool value);
    Q_INVOKABLE void layout();
    Q_INVOKABLE void validateIcon(QObject *object) {
        if(!qobject_cast<QQuickItem*>(object))qFatal("AppTabBar icon must create an Item");
    }
    Q_INVOKABLE void validateComponent(QObject *object,int count) {
        if(isComponentComplete() &&count>0&&!object)qFatal("AppTabBar requires an icon Component");
    }
    Q_INVOKABLE void cancelPress(QQuickItem *item) {if(item)item->ungrabMouse();}
signals:
    void configurationChanged();
    void metricsChanged();
protected:
    void componentComplete() override;
    void updatePolish() override {layout();}
private:
    void childrenUpdated();
    QList<QMetaObject::Connection> m_connections;
    QPointer<QQuickItem> m_owner;
    qreal m_proposal=-1,m_natural=0,m_minimum=0;
    bool m_mirrored=false,m_layingOut=false;
};

#pragma once
#include "proposalrow.h"

// Overlay proposal owner for caller-composed content. A surrounding proposal
// layout may own the same flattened views; this overlay then only measures.
class ProposalOverlay : public QQuickItem {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(qreal maximumWidth READ maximumWidth WRITE setMaximumWidth NOTIFY configurationChanged)
    Q_PROPERTY(qreal naturalWidth READ naturalWidth NOTIFY metricsChanged)
    Q_PROPERTY(qreal minimumWidth READ minimumWidth NOTIFY metricsChanged)
    Q_PROPERTY(int count READ count NOTIFY itemsChanged)
    Q_PROPERTY(bool containsTextBaseline READ containsTextBaseline NOTIFY baselineMetricsChanged)
public:
    explicit ProposalOverlay(QQuickItem *parent=nullptr);
    qreal maximumWidth() const {return m_maximum;}
    void setMaximumWidth(qreal value);
    qreal naturalWidth() const {return m_natural;}
    qreal minimumWidth() const {return m_minimum;}
    int count() const {return layoutItems().size();}
    bool containsTextBaseline() const {return m_containsTextBaseline;}
    Q_INVOKABLE QQuickItem *itemAt(int index) const;
    Q_INVOKABLE void layout();
signals:
    void configurationChanged();
    void metricsChanged();
    void itemsChanged();
    void baselineMetricsChanged();
protected:
    void componentComplete() override;
    void updatePolish() override {layout();}
private:
    void childrenUpdated();
    QList<QQuickItem*> layoutItems() const;
    bool delegated() const;
    QList<QMetaObject::Connection> m_connections;
    qreal m_maximum=-1,m_natural=0,m_minimum=0;
    bool m_layingOut=false,m_containsTextBaseline=false;
};

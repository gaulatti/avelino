#pragma once
#include "proposalrow.h"

// A vertical proposal adapter. Padding belongs to each flattened child, so an
// absent child contributes nothing while a zero-size child retains its padding.
class ProposalColumn : public QQuickItem {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(qreal maximumWidth READ maximumWidth WRITE setMaximumWidth NOTIFY configurationChanged)
    Q_PROPERTY(qreal padding READ padding WRITE setPadding NOTIFY configurationChanged)
    Q_PROPERTY(qreal spacing READ spacing WRITE setSpacing NOTIFY configurationChanged)
    Q_PROPERTY(qreal naturalWidth READ naturalWidth NOTIFY metricsChanged)
    Q_PROPERTY(qreal minimumWidth READ minimumWidth NOTIFY metricsChanged)
    Q_PROPERTY(bool containsTextBaseline READ containsTextBaseline NOTIFY baselineMetricsChanged)
public:
    explicit ProposalColumn(QQuickItem *parent=nullptr);
    qreal maximumWidth() const {return m_maximum;}
    qreal padding() const {return m_padding;}
    qreal spacing() const {return m_spacing;}
    qreal naturalWidth() const {return m_natural;}
    qreal minimumWidth() const {return m_minimum;}
    bool containsTextBaseline() const {return m_containsTextBaseline;}
    void setMaximumWidth(qreal value);
    void setPadding(qreal value);
    void setSpacing(qreal value);
    Q_INVOKABLE void layout();
signals:
    void configurationChanged();
    void metricsChanged();
    void baselineMetricsChanged();
protected:
    void componentComplete() override;
    void updatePolish() override {layout();}
private:
    void childrenUpdated();
    QList<QQuickItem*> layoutItems() const;
    QList<QMetaObject::Connection> m_connections;
    qreal m_maximum=-1,m_padding=0,m_spacing=0,m_natural=0,m_minimum=0;
    bool m_layingOut=false,m_containsTextBaseline=false;
};

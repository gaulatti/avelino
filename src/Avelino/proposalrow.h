#pragma once
#include <QQuickItem>
#include <QtQml/qqmlregistration.h>
#include "pixelalignment.h"
#include <limits>

// Qt layout adapter: content keeps its objects and reports its fitted size after
// receiving a width proposal. Fixed items need no attached properties.
class BleeckerLayout : public QObject {
    Q_OBJECT
    QML_ELEMENT
    QML_UNCREATABLE("Attached content layout metrics")
    QML_ATTACHED(BleeckerLayout)
    Q_PROPERTY(qreal minimumWidth MEMBER minimumWidth NOTIFY metricsChanged)
    Q_PROPERTY(qreal idealWidth MEMBER idealWidth NOTIFY metricsChanged)
    Q_PROPERTY(bool fillsWidth MEMBER fillsWidth NOTIFY metricsChanged)
    Q_PROPERTY(bool flattenChildren MEMBER flattenChildren NOTIFY structureChanged)
    Q_PROPERTY(bool participates MEMBER participates NOTIFY structureChanged)
    Q_PROPERTY(qreal proposedWidth READ proposedWidth NOTIFY proposalChanged)
    // NaN means the view's implicit guide. Explicit guides may be negative.
    Q_PROPERTY(qreal firstBaseline MEMBER firstBaseline NOTIFY metricsChanged)
public:
    explicit BleeckerLayout(QObject *parent=nullptr):QObject(parent){}
    static BleeckerLayout *qmlAttachedProperties(QObject *object) {return new BleeckerLayout(object);}
    qreal minimumWidth=-1,idealWidth=-1;
    qreal firstBaseline=std::numeric_limits<qreal>::quiet_NaN();
    struct Baseline {qreal offset;bool containsText;};
    static Baseline baselineFor(QQuickItem *item);
    bool fillsWidth=false;
    bool flattenChildren=false,participates=true;
    qreal proposedWidth() const {return m_proposal;}
    Q_INVOKABLE void propose(qreal value) {if(m_proposal!=value){m_proposal=value;emit proposalChanged();}}
signals:
    void metricsChanged();
    void proposalChanged();
    void structureChanged();
private:
    qreal m_proposal=-1;
};
QML_DECLARE_TYPEINFO(BleeckerLayout,QML_HAS_ATTACHED_PROPERTIES)

class ProposalRow : public QQuickItem {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(qreal spacing READ spacing WRITE setSpacing NOTIFY configurationChanged)
    Q_PROPERTY(qreal maximumWidth READ maximumWidth WRITE setMaximumWidth NOTIFY configurationChanged)
    Q_PROPERTY(Qt::Alignment verticalAlignment READ verticalAlignment WRITE setVerticalAlignment NOTIFY configurationChanged)
    Q_PROPERTY(bool mirrored READ mirrored WRITE setMirrored NOTIFY configurationChanged)
    Q_PROPERTY(bool cancelPointerOnReflow MEMBER m_cancelPointerOnReflow NOTIFY configurationChanged)
    Q_PROPERTY(qreal naturalWidth READ naturalWidth NOTIFY metricsChanged)
    Q_PROPERTY(qreal minimumWidth READ minimumWidth NOTIFY metricsChanged)
    Q_PROPERTY(bool containsTextBaseline READ containsTextBaseline NOTIFY baselineMetricsChanged)
public:
    explicit ProposalRow(QQuickItem *parent=nullptr);
    qreal spacing() const {return m_spacing;}
    qreal maximumWidth() const {return m_maximum;}
    bool mirrored() const {return m_mirrored;}
    qreal naturalWidth() const {return m_natural;}
    qreal minimumWidth() const {return m_minimum;}
    bool containsTextBaseline() const {return m_containsTextBaseline;}
    void setSpacing(qreal value);
    void setMaximumWidth(qreal value);
    void setMirrored(bool value);
    Qt::Alignment verticalAlignment() const {return m_verticalAlignment;}
    void setVerticalAlignment(Qt::Alignment value);
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
    qreal m_spacing=0,m_maximum=-1,m_natural=0,m_minimum=0;
    bool m_mirrored=false,m_layingOut=false,m_cancelPointerOnReflow=false,m_containsTextBaseline=false;
    Qt::Alignment m_verticalAlignment=Qt::AlignVCenter;
    PixelAlignment m_metrics;
};

#pragma once
#include <QObject>
#include <QPointer>
#include <QQuickItem>
#include <QtQml/qqmlregistration.h>

class QQuickAccessibleAttached;
class TooltipDescriptionMetaObject;

// Qt 6.8.3 help adapter. Caller items retain their layout and input.
class TooltipAccess : public QObject {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QQuickItem *target READ target WRITE setTarget NOTIFY targetChanged)
    Q_PROPERTY(QString text READ text WRITE setText NOTIFY textChanged)
public:
    explicit TooltipAccess(QObject *parent=nullptr);
    ~TooltipAccess() override;
    QQuickItem *target() const {return m_target;}
    void setTarget(QQuickItem *target);
    QString text() const {return m_text;}
    void setText(const QString &text);
private:
    struct Node {
        QPointer<QQuickAccessibleAttached> object;
        TooltipDescriptionMetaObject *overlay=nullptr;
        QMetaObject::Connection destroyed;
    };
    void scheduleRefresh();
    void refresh();
    void release(QQuickAccessibleAttached *key);
    void clear();
    QPointer<QQuickItem> m_target;
    QString m_text;
    QHash<QQuickAccessibleAttached*,Node> m_nodes;
    QList<QMetaObject::Connection> m_structure;
    QMetaObject::Connection m_targetDestroyed;
    bool m_queued=false;
signals:
    void targetChanged();
    void textChanged();
};

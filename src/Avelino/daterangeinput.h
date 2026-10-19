#pragma once
#include <QtQuickTemplates2/private/qquicktextfield_p.h>
#include <QtQml/qqmlregistration.h>
#include <QVariantList>
#include <memory>
#include <vector>

// One Qt template retains the logical text, focus, selection and composition.
// Each calendar field has an independent, fixed reservation in its presentation.
class DateRangeInput : public QQuickTextField {
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(QVariantList fields READ fields WRITE setFields NOTIFY fieldsChanged)
    Q_PROPERTY(QVariantList reservedWidths READ reservedWidths WRITE setReservedWidths NOTIFY reservedWidthsChanged)
    Q_PROPERTY(int activeSegment READ activeSegment WRITE setActiveSegment NOTIFY activeSegmentChanged)
    Q_PROPERTY(QRectF cursorRectangle READ fieldCursorRectangle NOTIFY fieldGeometryChanged)
public:
    explicit DateRangeInput(QQuickItem *parent=nullptr);
    QVariantList fields()const{return m_fields;}
    QVariantList reservedWidths()const{return m_widths;}
    int activeSegment()const{return m_activeSegment;}
    void setFields(const QVariantList &value);
    void setReservedWidths(const QVariantList &value);
    void setActiveSegment(int value);
    Q_INVOKABLE int positionAt(qreal x,qreal y,CursorPosition mode=CursorBetweenCharacters)const;
    Q_INVOKABLE QRectF positionToRectangle(int position)const;
    Q_INVOKABLE QVariant inputMethodQuery(Qt::InputMethodQuery query,const QVariant &argument)const;
    QVariant inputMethodQuery(Qt::InputMethodQuery query)const override;
    QRectF fieldCursorRectangle()const;
    QRectF characterRectangle(int position)const;
signals:
    void fieldsChanged();
    void reservedWidthsChanged();
    void activeSegmentChanged();
    void fieldGeometryChanged();
    void fieldActivated(int position);
    void fieldSelectionRequested();
protected:
    QSGNode *updatePaintNode(QSGNode *oldNode,UpdatePaintNodeData *data)override;
    void mousePressEvent(QMouseEvent *event)override;
    void mouseReleaseEvent(QMouseEvent *event)override;
private:
    struct FieldLayout;
    using Layouts=std::vector<std::unique_ptr<FieldLayout>>;
    Layouts layouts()const;
    void invalidateFields();
    bool isLiteralAt(const QPointF &point)const;
    bool preeditMouseEvent(QMouseEvent *event);
    QVariantList m_fields,m_widths;
    int m_activeSegment=0;
};

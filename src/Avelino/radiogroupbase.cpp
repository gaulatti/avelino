#include "radiogroupbase.h"
#include "bleeckerfonts.h"
#include <QtQuick/private/qquickitem_p.h>
#include <QtQuick/private/qquickpalette_p.h>

RadioGroupBase::RadioGroupBase(QQuickItem *parent):QQuickControl(parent) {
    BleeckerFonts fonts;
    connect(this,&QQuickControl::fontChanged,this,&RadioGroupBase::presentationFontChanged);
    connect(this,&QQuickItem::paletteChanged,this,&RadioGroupBase::resolvedTextColorChanged);
    connect(this,&QQuickItem::enabledChanged,this,&RadioGroupBase::resolvedTextColorChanged);
}
RadioGroupBase::~RadioGroupBase(){disconnect(this,nullptr,this,nullptr);}
void RadioGroupBase::cancelPointerPress(QQuickItem *option) const {
    if(option)option->ungrabMouse();
}
bool RadioGroupBase::isHorizontal(int orientation) const {
    if(orientation!=Qt::Horizontal && orientation!=Qt::Vertical)qFatal("RadioGroup orientation must be Qt.Horizontal or Qt.Vertical");
    return orientation==Qt::Horizontal;
}
QFont RadioGroupBase::presentationFont() const {
    auto resolved=font();
    resolved.setResolveMask(QFont::AllPropertiesResolved);
    return resolved;
}
QFont RadioGroupBase::defaultFont() const {
    QFont font;
    font.setFamily(QStringLiteral("Encode Sans"));
    font.setPointSizeF(13*72/BleeckerFonts::logicalFontDpi());
    return font;
}
void RadioGroupBase::setDefaultTextColor(const QColor &value) {
    if(value==m_defaultTextColor)return;
    m_defaultTextColor=value;emit resolvedTextColorChanged();
}
QColor RadioGroupBase::resolvedTextColor() const {
    const auto palette=QQuickItemPrivate::get(const_cast<RadioGroupBase*>(this))->palette()->toQPalette();
    const auto current=palette.currentColorGroup();
    if(palette.isBrushSet(current,QPalette::WindowText))return palette.color(current,QPalette::WindowText);
    if(palette.isBrushSet(QPalette::Active,QPalette::WindowText))return palette.color(QPalette::Active,QPalette::WindowText);
    return m_defaultTextColor;
}
bool RadioHitMask::contains(const QPointF &point) const {
    const auto inside=[&](const QRectF &rect){return rect.width()>0 && rect.height()>0 && point.x()>=rect.left() && point.x()<rect.right() && point.y()>=rect.top() && point.y()<rect.bottom();};
    return inside(iconRect)||inside(titleRect);
}

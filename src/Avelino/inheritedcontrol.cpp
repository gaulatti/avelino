#include "inheritedcontrol.h"
#include "bleeckerfonts.h"
#include <QtQuick/private/qquickitem_p.h>
#include <QtQuick/private/qquickpalette_p.h>

InheritedControl::InheritedControl(QQuickItem *parent):QQuickControl(parent) {
    BleeckerFonts fonts;
    connect(this,&QQuickControl::fontChanged,this,&InheritedControl::presentationFontChanged);
    connect(this,&QQuickItem::paletteChanged,this,&InheritedControl::resolvedTextColorChanged);
    connect(this,&QQuickItem::enabledChanged,this,&InheritedControl::resolvedTextColorChanged);
}
QFont InheritedControl::presentationFont() const {
    auto resolved=font();resolved.setResolveMask(QFont::AllPropertiesResolved);return resolved;
}
QFont InheritedControl::defaultFont() const {
    QFont font;font.setFamily(QStringLiteral("Encode Sans"));
    font.setPointSizeF(13*72/BleeckerFonts::logicalFontDpi());return font;
}
void InheritedControl::setDefaultTextColor(const QColor &value) {
    if(value==m_defaultTextColor)return;m_defaultTextColor=value;emit resolvedTextColorChanged();
}
QColor InheritedControl::resolvedTextColor() const {
    const auto palette=QQuickItemPrivate::get(const_cast<InheritedControl*>(this))->palette()->toQPalette();
    const auto current=palette.currentColorGroup();
    if(palette.isBrushSet(current,QPalette::WindowText))return palette.color(current,QPalette::WindowText);
    if(palette.isBrushSet(QPalette::Active,QPalette::WindowText))return palette.color(QPalette::Active,QPalette::WindowText);
    return m_defaultTextColor;
}

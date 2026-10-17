#include "dropdownlabel.h"
#include <QMetaMethod>
#include <QMetaProperty>
#include <QFontDatabase>
#include <QSet>
#include <QtQuick/private/qquickimagebase_p.h>
#include <QtQuick/private/qquickitem_p.h>
#include <QtQuick/private/qquickpalette_p.h>
#include <QtQuick/private/qquicktext_p.h>
#include <QtQuickTemplates2/private/qquickabstractbutton_p.h>

void DropdownLabel::setRoot(QObject *value) {
    const auto item=qobject_cast<QQuickItem*>(value);
    if(value&&!item)qFatal("DropdownMenu label must create an Item");
    if(item==m_root)return;m_root=item;emit rootChanged();polish();
}
void DropdownLabel::setDefaultFont(const QFont &value){if(value==m_defaultFont)return;m_defaultFont=value;emit defaultFontChanged();polish();}
QFont DropdownLabel::systemFont(int pixelSize) const {
    if(pixelSize<=0)qFatal("DropdownMenu system font size must be positive");
    auto font=QFontDatabase::systemFont(QFontDatabase::GeneralFont);
    font.setPixelSize(pixelSize);font.setWeight(QFont::Normal);font.setStyleName(QString());
    font.setItalic(false);font.setUnderline(false);font.setStrikeOut(false);font.setOverline(false);
    font.setResolveMask(QFont::AllPropertiesResolved);return font;
}
int DropdownLabel::controlFontSize(const QString &size) const {
    if(size=="mini")return 9;
    if(size=="small")return 11;
    if(size=="regular"||size=="large")return 13;
    qFatal("Unknown DropdownMenu control size");
}
void DropdownLabel::observe(QQuickItem *item) {
    const auto slot=metaObject()->method(metaObject()->indexOfSlot("scheduleRefresh()"));
    QSet<int> signalIndexes;
    for(const auto &name:{"text","font","presentationFont","color","textFormat","source","status","width","height","implicitWidth","implicitHeight","visible","children"}) {
        const auto index=item->metaObject()->indexOfProperty(name);if(index<0)continue;
        const auto property=item->metaObject()->property(index);
        if(property.hasNotifySignal()&&!signalIndexes.contains(property.notifySignalIndex())) {
            signalIndexes.insert(property.notifySignalIndex());
            m_connections.append(QObject::connect(item,property.notifySignal(),this,slot));
        }
    }
    m_connections.append(connect(item,&QObject::destroyed,this,&DropdownLabel::scheduleRefresh));
}
void DropdownLabel::visit(QQuickItem *item) {
    if(!item)return;observe(item);
    // The native metadata visitor omits hidden values but retains opacity-zero
    // values. Ancestor visibility must not erase the label's intrinsic metadata.
    if(!QQuickItemPrivate::get(item)->explicitVisible)return;
    if(item->property("bleeckerTextContent").toBool()) {
        if(!m_hasText){m_hasText=true;m_text=item->property("text").toString();m_font=item->property("presentationFont").value<QFont>();m_color=item->property("color").value<QColor>();m_format=item->property("textFormat").toInt();}
        return;
    }
    if(const auto text=qobject_cast<QQuickText*>(item)) {
        if(!m_hasText){m_hasText=true;m_text=text->text();m_font=text->font().resolve(m_defaultFont);m_color=text->color();m_format=int(text->textFormat());}
        return;
    }
    if(const auto image=qobject_cast<QQuickImageBase*>(item)) {
        if(m_image.isEmpty()&&image->status()==QQuickImageBase::Ready&&!image->source().isEmpty()) {
            m_image=image->source();
            m_imageWidth=image->implicitWidth();m_imageHeight=image->implicitHeight();
        }
        return;
    }
    if(const auto button=qobject_cast<QQuickAbstractButton*>(item)) {
        if(!m_hasText){m_hasText=true;m_text=button->text();m_font=button->font().resolve(m_defaultFont);m_color=QQuickItemPrivate::get(button)->palette()->toQPalette().color(QPalette::WindowText);}
    }
    for(const auto child:item->childItems())visit(child);
}
void DropdownLabel::refresh() {
    for(const auto &connection:m_connections)disconnect(connection);m_connections.clear();
    const auto oldText=m_text;const auto oldFont=m_font;const auto oldColor=m_color;
    const auto oldImage=m_image;const auto oldWidth=m_imageWidth,oldHeight=m_imageHeight;
    const auto oldFormat=m_format;const auto oldHasText=m_hasText;
    m_text.clear();m_font=m_defaultFont;m_color=Qt::black;m_format=0;m_hasText=false;
    m_image.clear();m_imageWidth=m_imageHeight=0;
    visit(m_root);
    if(m_text!=oldText||m_font!=oldFont||m_color!=oldColor||m_image!=oldImage||m_imageWidth!=oldWidth||m_imageHeight!=oldHeight||m_format!=oldFormat||m_hasText!=oldHasText)emit metadataChanged();
}

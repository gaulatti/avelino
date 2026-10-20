#include "daterangeinput.h"
#include <QtQuick/private/qquicktextinput_p_p.h>
#include <QtQuick/private/qaccessiblequickitem_p.h>
#include <QAccessible>
#include <QCoreApplication>
#include <QFontMetricsF>
#include <QGuiApplication>
#include <QInputMethod>
#include <QInputMethodEvent>
#include <QMouseEvent>
#include <QPointer>
#include <QQuickWindow>
#include <QSGClipNode>
#include <QSGGeometry>
#include <QSGSimpleRectNode>
#include <QSGTextNode>
#include <QTextLayout>
#include <algorithm>
#include <limits>

static_assert(QT_VERSION==QT_VERSION_CHECK(6,8,3),"Revalidate segmented template input before upgrading Qt");
namespace {
class DateInputAccessible final : public QAccessibleQuickItem,public QAccessibleEditableTextInterface {
public:
    using QAccessibleQuickItem::QAccessibleQuickItem;
    void *interface_cast(QAccessible::InterfaceType type)override{
        if(type==QAccessible::EditableTextInterface)return static_cast<QAccessibleEditableTextInterface*>(this);
        return QAccessibleQuickItem::interface_cast(type);
    }
    QRect characterRect(int offset)const override{
        const auto input=qobject_cast<DateRangeInput*>(object());if(!input)return {};
        const auto rectangle=input->characterRectangle(offset);if(rectangle.isEmpty())return {};
        return QRectF(input->mapToGlobal(rectangle.topLeft()),input->mapToGlobal(rectangle.bottomRight())).toAlignedRect();
    }
    int offsetAtPoint(const QPoint &point)const override{
        const auto input=qobject_cast<DateRangeInput*>(object());if(!input)return -1;
        const auto local=input->mapFromGlobal(point);if(!input->contains(local))return -1;
        return input->positionAt(local.x(),local.y(),QQuickTextInput::CursorOnCharacter);
    }
    void deleteText(int start,int end)override{replaceText(start,end,{});}
    void insertText(int offset,const QString &text)override{replaceText(offset,offset,text);}
    void replaceText(int start,int end,const QString &text)override{
        const auto input=qobject_cast<DateRangeInput*>(object());
        if(!input||input->isReadOnly()||!input->isEnabled()||start<0||end<start||end>input->text().size())return;
        input->select(start,start);QInputMethodEvent event;event.setCommitString(text,0,end-start);
        QCoreApplication::sendEvent(input,&event);
    }
    void setText(QAccessible::Text kind,const QString &text)override{
        if(kind==QAccessible::Value)replaceText(0,characterCount(),text);else QAccessibleQuickItem::setText(kind,text);
    }
};
QAccessibleInterface *dateInputFactory(const QString &,QObject *object){
    if(auto input=qobject_cast<DateRangeInput*>(object))return new DateInputAccessible(input);
    return nullptr;
}
QSGClipNode *fieldClipNode(const QRectF &rectangle){
    auto node=new QSGClipNode;node->setIsRectangular(true);node->setClipRect(rectangle);
    auto geometry=new QSGGeometry(QSGGeometry::defaultAttributes_Point2D(),4);
    QSGGeometry::updateRectGeometry(geometry,rectangle);node->setGeometry(geometry);node->setFlag(QSGNode::OwnsGeometry);
    return node;
}
}
struct DateRangeInput::FieldLayout {
    int first=0,last=0,preeditPosition=-1;
    QRectF reservation;
    QPointF origin;
    QTextLayout text;
};
DateRangeInput::DateRangeInput(QQuickItem *parent):QQuickTextField(parent){
    static const bool registered=[] {QAccessible::installFactory(dateInputFactory);return true;}();Q_UNUSED(registered);
    connect(this,&DateRangeInput::fieldsChanged,this,&DateRangeInput::invalidateFields);
    connect(this,&DateRangeInput::reservedWidthsChanged,this,&DateRangeInput::invalidateFields);
    connect(this,&DateRangeInput::activeSegmentChanged,this,&DateRangeInput::invalidateFields);
    connect(this,&QQuickTextInput::textChanged,this,&DateRangeInput::invalidateFields);
    connect(this,&QQuickTextInput::preeditTextChanged,this,&DateRangeInput::invalidateFields);
    connect(this,&QQuickTextInput::cursorRectangleChanged,this,&DateRangeInput::invalidateFields);
    connect(this,&QQuickTextInput::fontChanged,this,&DateRangeInput::invalidateFields);
    connect(this,&QQuickTextInput::horizontalAlignmentChanged,this,&DateRangeInput::invalidateFields);
    connect(this,&QQuickTextInput::verticalAlignmentChanged,this,&DateRangeInput::invalidateFields);
    connect(this,&QQuickTextInput::leftPaddingChanged,this,&DateRangeInput::invalidateFields);
    connect(this,&QQuickTextInput::rightPaddingChanged,this,&DateRangeInput::invalidateFields);
    connect(this,&QQuickTextInput::topPaddingChanged,this,&DateRangeInput::invalidateFields);
    connect(this,&QQuickTextInput::bottomPaddingChanged,this,&DateRangeInput::invalidateFields);
    connect(this,&QQuickItem::widthChanged,this,&DateRangeInput::invalidateFields);
    connect(this,&QQuickItem::heightChanged,this,&DateRangeInput::invalidateFields);
}
void DateRangeInput::setFields(const QVariantList &value){if(value==m_fields)return;m_fields=value;emit fieldsChanged();}
void DateRangeInput::setReservedWidths(const QVariantList &value){if(value==m_widths)return;m_widths=value;emit reservedWidthsChanged();}
void DateRangeInput::setActiveSegment(int value){if(value==m_activeSegment)return;m_activeSegment=value;emit activeSegmentChanged();}
void DateRangeInput::invalidateFields(){
    update();emit fieldGeometryChanged();
    if(hasActiveFocus())QGuiApplication::inputMethod()->update(Qt::ImCursorRectangle|Qt::ImAnchorRectangle);
}
DateRangeInput::Layouts DateRangeInput::layouts()const{
    Layouts result;if(m_fields.size()!=m_widths.size()||m_fields.isEmpty())return result;
    const auto d=static_cast<const QQuickTextInputPrivate*>(QQuickItemPrivate::get(this));
    const bool rtl=hAlign()==AlignRight;const auto string=text();const QFontMetricsF metrics(font());
    int expected=0,editable=0,active=-1;
    
    for(qsizetype index=0;index<m_fields.size();++index){
        const auto field=m_fields[index].toMap();expected+=field["text"].toString().size();
        if(field["kind"]!="literal"&&editable++==m_activeSegment)active=int(index);
    }
    const int delta=int(string.size())-expected;int offset=0;qreal advance=0;
    for(qsizetype index=0;index<m_fields.size();++index){
        auto field=std::make_unique<FieldLayout>();const qreal reserved=m_widths[index].toReal();
        const int length=std::max(0,int(m_fields[index].toMap()["text"].toString().size())+(index==active ? delta:0));
        field->first=std::min(offset,int(string.size()));field->last=std::min(offset+length,int(string.size()));offset+=length;
        field->text.setText(string.mid(field->first,field->last-field->first));field->text.setFont(font());
        QTextOption option;option.setWrapMode(QTextOption::NoWrap);option.setTextDirection(rtl ? Qt::RightToLeft:Qt::LeftToRight);
        option.setAlignment(rtl ? Qt::AlignRight:Qt::AlignLeft);field->text.setTextOption(option);
        if(int(index)==active&&!preeditText().isEmpty()){
            field->preeditPosition=std::clamp(d->m_textLayout.preeditAreaPosition()-field->first,0,field->last-field->first);
            field->text.setPreeditArea(field->preeditPosition,preeditText());
            auto formats=d->m_textLayout.formats();
            for(auto &format:formats)format.start-=field->first;
            field->text.setFormats(formats);
        }
        field->text.beginLayout();auto line=field->text.createLine();if(line.isValid())line.setLineWidth(reserved);field->text.endLayout();
        const qreal x=rtl ? width()-rightPadding()-advance-reserved:leftPadding()+advance;
        field->reservation=QRectF(x,topPadding(),reserved,std::max(qreal(0),height()-topPadding()-bottomPadding()));
        qreal top=topPadding();
        if(vAlign()==AlignVCenter)top+=(field->reservation.height()-metrics.height())/2;
        else if(vAlign()==AlignBottom)top+=field->reservation.height()-metrics.height();
        field->origin=QPointF(x,top+metrics.ascent()-(line.isValid()?line.ascent():metrics.ascent()));
        advance+=reserved;result.push_back(std::move(field));
    }
    return result;
}
QRectF DateRangeInput::positionToRectangle(int position)const{
    const auto pieces=layouts();position=std::clamp(position,0,int(text().size()));
    for(qsizetype index=0;index<qsizetype(pieces.size());++index){
        const auto &field=*pieces[index];if(position>=field.last&&index+1<qsizetype(pieces.size()))continue;
        if(!field.text.lineCount())return {};const auto line=field.text.lineAt(0);if(!line.isValid())return {};
        const qreal x=field.origin.x()+line.cursorToX(position-field.first);
        return QRectF(x,field.origin.y(),1,line.height());
    }
    return {};
}
int DateRangeInput::positionAt(qreal x,qreal y,CursorPosition mode)const{
    Q_UNUSED(y);const auto pieces=layouts();const FieldLayout *nearest=nullptr;qreal distance=std::numeric_limits<qreal>::max();
    for(const auto &field:pieces){
        const qreal gap=std::max({field->reservation.left()-x,x-field->reservation.right(),qreal(0)});
        if(gap<distance){nearest=field.get();distance=gap;}
    }
    if(!nearest||nearest->text.lineCount()==0)return 0;
    const int local=nearest->text.lineAt(0).xToCursor(x-nearest->origin.x(),mode==CursorOnCharacter ? QTextLine::CursorOnCharacter:QTextLine::CursorBetweenCharacters);
    return nearest->first+std::clamp(local,0,nearest->last-nearest->first);
}
QRectF DateRangeInput::fieldCursorRectangle()const{
    const auto pieces=layouts();
    if(!preeditText().isEmpty())for(const auto &field:pieces)if(field->preeditPosition>=0&&field->text.lineCount()){
        const auto d=static_cast<const QQuickTextInputPrivate*>(QQuickItemPrivate::get(this));const auto line=field->text.lineAt(0);
        const auto x=field->origin.x()+line.cursorToX(field->preeditPosition+d->m_preeditCursor);
        return QRectF(std::clamp(x,field->reservation.left(),field->reservation.right()),field->origin.y(),1,line.height());
    }
    auto rectangle=positionToRectangle(cursorPosition());
    for(const auto &field:pieces)if(cursorPosition()>=field->first&&cursorPosition()<=field->last){
        rectangle.moveLeft(std::clamp(rectangle.x(),field->reservation.left(),field->reservation.right()));break;
    }
    return rectangle;
}
QRectF DateRangeInput::characterRectangle(int position)const{
    for(const auto &field:layouts())if(position>=field->first&&position<field->last&&field->text.lineCount()){
        const auto line=field->text.lineAt(0);const qreal first=line.cursorToX(position-field->first),last=line.cursorToX(position-field->first+1);
        return QRectF(field->origin.x()+std::min(first,last),field->origin.y(),std::max(qreal(1),std::abs(last-first)),line.height()).intersected(field->reservation);
    }
    return {};
}
QVariant DateRangeInput::inputMethodQuery(Qt::InputMethodQuery query)const{return inputMethodQuery(query,{});}
QVariant DateRangeInput::inputMethodQuery(Qt::InputMethodQuery query,const QVariant &argument)const{
    if(query==Qt::ImCursorRectangle)return fieldCursorRectangle();
    if(query==Qt::ImAnchorRectangle){
        const int anchor=QQuickTextField::inputMethodQuery(Qt::ImAnchorPosition).toInt();auto rectangle=positionToRectangle(anchor);
        for(const auto &field:layouts())if(anchor>=field->first&&anchor<=field->last){
            rectangle.moveLeft(std::clamp(rectangle.x(),field->reservation.left(),field->reservation.right()));break;
        }
        return rectangle;
    }
    if(query==Qt::ImCursorPosition&&argument.canConvert<QPointF>()){
        const auto point=argument.toPointF();return positionAt(point.x(),point.y());
    }
    return QQuickTextField::inputMethodQuery(query,argument);
}
bool DateRangeInput::preeditMouseEvent(QMouseEvent *event){
    if(preeditText().isEmpty())return false;
    for(const auto &field:layouts())if(field->preeditPosition>=0&&field->reservation.contains(event->position())&&field->text.lineCount()){
        const int position=field->text.lineAt(0).xToCursor(event->position().x()-field->origin.x())-field->preeditPosition;
        if(position>=0&&position<=preeditText().size()){
            if(event->type()==QEvent::MouseButtonRelease)QGuiApplication::inputMethod()->invokeAction(QInputMethod::Click,position);
            event->accept();return true;
        }
    }
    return false;
}
bool DateRangeInput::isLiteralAt(const QPointF &point)const{
    const auto pieces=layouts();
    for(qsizetype index=0;index<qsizetype(pieces.size());++index){
        const auto &rectangle=pieces[index]->reservation;
        if(point.x()>=rectangle.left()&&point.x()<rectangle.right()
            &&point.y()>=rectangle.top()&&point.y()<=rectangle.bottom())
            return m_fields[index].toMap()["kind"]=="literal";
    }
    return false;
}
void DateRangeInput::mousePressEvent(QMouseEvent *event){
    if(preeditMouseEvent(event))return;
    const QPointer<DateRangeInput> guard=this;
    if(!preeditText().isEmpty())static_cast<QQuickTextInputPrivate*>(QQuickItemPrivate::get(this))->commitPreedit();
    if(!guard)return;
    QQuickTextField::mousePressEvent(event);
    // The template's internal mouse path uses its joined layout. Apply the
    // calendar selection after that path, using the actual visible field.
    // Native literals can take focus but do not activate the calendar. Use the
    // reservation: RTL marks can map a literal hit to the next editable cursor.
    if(guard&&event->button()==Qt::LeftButton&&!isLiteralAt(event->position()))
        emit fieldActivated(positionAt(event->position().x(),event->position().y(),CursorOnCharacter));
}
void DateRangeInput::mouseReleaseEvent(QMouseEvent *event){
    if(preeditMouseEvent(event))return;
    const QPointer<DateRangeInput> guard=this;QQuickTextField::mouseReleaseEvent(event);
    if(guard&&event->button()==Qt::LeftButton)emit fieldSelectionRequested();
}
QSGNode *DateRangeInput::updatePaintNode(QSGNode *oldNode,UpdatePaintNodeData *){
    delete oldNode;auto root=new QSGNode;const auto pieces=layouts();
    const auto d=static_cast<const QQuickTextInputPrivate*>(QQuickItemPrivate::get(this));
    const QRectF content(leftPadding(),topPadding(),std::max(qreal(0),width()-leftPadding()-rightPadding()),std::max(qreal(0),height()-topPadding()-bottomPadding()));
    for(const auto &field:pieces){
        auto clipping=fieldClipNode(field->reservation.intersected(content));root->appendChildNode(clipping);
        auto node=window()->createTextNode();node->setColor(color());node->setSelectionColor(selectionColor());node->setSelectionTextColor(selectedTextColor());
        node->setRenderType(QSGTextNode::RenderType(renderType()));node->setFiltering(smooth()?QSGTexture::Linear:QSGTexture::Nearest);
        const int first=std::max(selectionStart(),field->first)-field->first,last=std::min(selectionEnd(),field->last)-field->first;
        // Qt 6.8.3's actual node consumes an inclusive selection end, as its
        // TextInput does, despite the public header naming it selectionCount.
        node->addTextLayout(field->origin,&field->text,first<last ? first:-1,first<last ? last-1:-1);clipping->appendChildNode(node);
    }
    if(!isReadOnly()&&!d->cursorItem&&isCursorVisible()&&d->m_blinkStatus){
        auto clipping=fieldClipNode(content);clipping->appendChildNode(new QSGSimpleRectNode(fieldCursorRectangle(),color()));root->appendChildNode(clipping);
    }
    return root;
}

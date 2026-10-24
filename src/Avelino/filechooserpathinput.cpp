#include "filechooserpathinput.h"
#include "assistivetextinput_p.h"
#include <QtQuick/private/qaccessiblequickitem_p.h>
#include <QAccessible>
#include <QCoreApplication>
#include <QInputMethodEvent>

static_assert(QT_VERSION==QT_VERSION_CHECK(6,8,3),"Revalidate owned path editing accessibility before upgrading Qt");
namespace {
class PathInputAccessible final : public QAccessibleQuickItem, public QAccessibleEditableTextInterface {
public:
    using QAccessibleQuickItem::QAccessibleQuickItem;
    void *interface_cast(QAccessible::InterfaceType type)override{
        if(type==QAccessible::EditableTextInterface)return static_cast<QAccessibleEditableTextInterface*>(this);
        return QAccessibleQuickItem::interface_cast(type);
    }
    void deleteText(int start,int end)override{replaceText(start,end,{});}
    void insertText(int offset,const QString &text)override{replaceText(offset,offset,text);}
    void replaceText(int start,int end,const QString &text)override{
        QPointer<FileChooserPathInput> input=qobject_cast<FileChooserPathInput*>(object());
        if(!input||input->isReadOnly()||!input->isEnabled()||start<0||end<start||end>input->text().size())return;
        // A Qt input-method commit preserves the field's normal validation,
        // length limit, text signals and undo history for one replacement.
        const auto original=input->text();
        if(!AvelinoPrivate::finishAssistiveOperation(input,[&]{input->select(start,start);}))return;
        if(input->isReadOnly()||!input->isEnabled()||input->text()!=original
            ||input->cursorPosition()!=start||input->selectionStart()!=input->selectionEnd())return;
        QInputMethodEvent event;
        event.setCommitString(text,0,end-start);
        AvelinoPrivate::finishAssistiveOperation(input,[&]{QCoreApplication::sendEvent(input,&event);});
    }
    void setText(QAccessible::Text kind,const QString &text)override{
        if(kind==QAccessible::Value)replaceText(0,characterCount(),text);
        else QAccessibleQuickItem::setText(kind,text);
    }
};
QAccessibleInterface *pathInputFactory(const QString &,QObject *object){
    if(auto input=qobject_cast<FileChooserPathInput*>(object))return new PathInputAccessible(input);
    return nullptr;
}
}
FileChooserPathInput::FileChooserPathInput(QQuickItem *parent):QQuickTextField(parent){
    static const bool registered=[] {QAccessible::installFactory(pathInputFactory);return true;}();
    Q_UNUSED(registered);
}

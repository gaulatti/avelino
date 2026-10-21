#include "filechoosersearchtext.h"
#include <QtQuick/private/qquicktextinput_p_p.h>
#include <QInputMethodEvent>
#include <QKeyEvent>
#include <QKeySequence>
#include <QPointer>
#include <QQmlEngine>

static_assert(QT_VERSION==QT_VERSION_CHECK(6,8,3),"Revalidate search token metadata against Qt's undo cursor before upgrading");

FileChooserSearchText::FileChooserSearchText(QQuickItem *parent):FileChooserPathInput(parent){
    remember();
    connect(this,&QQuickTextInput::textChanged,this,&FileChooserSearchText::observeTextChange);
}
FileChooserSearchText::State FileChooserSearchText::editState()const{
    const auto control=QQuickTextInputPrivate::get(const_cast<FileChooserSearchText*>(this));
    int cursor=control->m_undoState;
    // Qt can stop on either side of separator/selection commands. Neither
    // changes the text or its token, so both identify the same metadata state.
    while(cursor>0&&(control->m_history[cursor-1].type==QQuickTextInputPrivate::Separator
        ||control->m_history[cursor-1].type==QQuickTextInputPrivate::SetSelection))--cursor;
    return {cursor,text(),m_mode};
}
void FileChooserSearchText::remember(){m_modes[editState().cursor]=m_mode;}
void FileChooserSearchText::setTokenMode(const QString &mode){
    if(mode==m_mode)return;
    if(mode!="general"&&mode!="filename"&&mode!="everything"){
        if(auto engine=qjsEngine(this))engine->throwError(QStringLiteral("Search token mode must be general, filename or everything"));
        else qWarning("Search token mode must be general, filename or everything");
        return;
    }
    m_mode=mode;
    if(!m_editDepth){
        // Qt6.8.3's private separate() is exactly this flag. Leave command
        // creation and grouping within each literal edit to Qt itself.
        if(mode!="general")QQuickTextInputPrivate::get(this)->m_separator=true;
        remember();
    }
    emit tokenModeChanged();
}
void FileChooserSearchText::observeTextChange(){
    if(m_editDepth)return;
    const auto current=editState();const auto control=QQuickTextInputPrivate::get(this);
    if(control->m_history.isEmpty()){
        // An external setText clears Qt's undo history. Never attach an old
        // token to an unrelated programmatic query with the same text.
        m_modes.clear();remember();return;
    }
    const auto found=m_modes.constFind(current.cursor);
    if(found!=m_modes.cend())setTokenMode(*found);
    else remember();
}
void FileChooserSearchText::finishEdit(const State &before,bool wholeReplacement,bool replay){
    const auto current=editState();
    const bool edited=current.text!=before.text||current.cursor!=before.cursor;
    if(!replay&&edited){
        m_modes.erase(m_modes.upperBound(before.cursor),m_modes.end());
        m_modes[before.cursor]=before.mode;
    }
    QPointer<FileChooserSearchText> guard(this);
    if(replay){
        const auto found=m_modes.constFind(current.cursor);
        if(found!=m_modes.cend())setTokenMode(*found);
    }else if(wholeReplacement&&edited)setTokenMode("general");
    if(guard)remember();
}
void FileChooserSearchText::keyPressEvent(QKeyEvent *event){
    const auto before=editState();
    const bool replay=event->matches(QKeySequence::Undo)||event->matches(QKeySequence::Redo);
    const bool replacing=event->matches(QKeySequence::Cut)||event->matches(QKeySequence::Paste)
        ||event->key()==Qt::Key_Backspace||event->key()==Qt::Key_Delete
        ||(!event->text().isEmpty()&&event->text().front().isPrint());
    const bool whole=replacing&&!before.text.isEmpty()&&selectionStart()==0&&selectionEnd()==before.text.size();
    const bool outer=m_editDepth++==0;QPointer<FileChooserSearchText> guard(this);
    FileChooserPathInput::keyPressEvent(event);
    if(!guard)return;
    --m_editDepth;if(outer)finishEdit(before,whole,replay);
}
void FileChooserSearchText::inputMethodEvent(QInputMethodEvent *event){
    const auto before=editState();const int replacementStart=cursorPosition()+event->replacementStart();
    const bool replacing=!event->commitString().isEmpty()||event->replacementLength()>0;
    const bool whole=replacing&&!before.text.isEmpty()&&((selectionStart()==0&&selectionEnd()==before.text.size())
        ||(replacementStart==0&&event->replacementLength()>=before.text.size()));
    const bool outer=m_editDepth++==0;QPointer<FileChooserSearchText> guard(this);
    FileChooserPathInput::inputMethodEvent(event);
    if(!guard)return;
    --m_editDepth;if(outer)finishEdit(before,whole,false);
}

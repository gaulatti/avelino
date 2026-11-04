#pragma once
#include <QtQuick/private/qquicktextinput_p_p.h>
#include <QPointer>
#include <QSignalBlocker>

static_assert(QT_VERSION==QT_VERSION_CHECK(6,8,3),"Revalidate assistive text-input notifications and Qt Undo cursor before upgrading Qt");
namespace AvelinoPrivate {
struct AssistiveTextInputState {
    QString text,display,preedit,selected;
    int cursor,start,end,undoState;
    QRectF rectangle;
    QSizeF content;
    bool undo,redo,acceptable,composing,cursorVisible;
    explicit AssistiveTextInputState(QQuickTextInput *input):
        text(input->text()),display(input->displayText()),preedit(input->preeditText()),selected(input->selectedText()),
        cursor(input->cursorPosition()),start(input->selectionStart()),end(input->selectionEnd()),
        undoState(static_cast<QQuickTextInputPrivate*>(QQuickItemPrivate::get(input))->m_undoState),
        rectangle(input->QQuickTextInput::cursorRectangle()),content(input->contentWidth(),input->contentHeight()),
        undo(input->canUndo()),redo(input->canRedo()),acceptable(input->hasAcceptableInput()),
        composing(input->isInputMethodComposing()),cursorVisible(input->isCursorVisible()){}
};
template<typename Operation>
bool finishAssistiveOperation(QQuickTextInput *input,const Operation &operation){
    const AssistiveTextInputState before(input);QPointer<QQuickTextInput> guard(input);QSignalBlocker blocker(input);
    operation();if(!guard){blocker.dismiss();return false;}
    const AssistiveTextInputState after(input);blocker.unblock();
    // Qt's selection and IME paths continue using their private state after
    // notifying observers. Publish only after that path has fully returned:
    // an owner may synchronously remove the input from any notification.
    if(before.preedit!=after.preedit)emit input->preeditTextChanged();if(!guard)return false;
    if(before.content!=after.content)emit input->contentSizeChanged();if(!guard)return false;
    if(before.display!=after.display)emit input->displayTextChanged();if(!guard)return false;
    if(before.rectangle!=after.rectangle)emit input->cursorRectangleChanged();if(!guard)return false;
    if(before.cursor!=after.cursor)emit input->cursorPositionChanged();if(!guard)return false;
    if(before.selected!=after.selected)emit input->selectedTextChanged();if(!guard)return false;
    if(before.start!=after.start)emit input->selectionStartChanged();if(!guard)return false;
    if(before.end!=after.end)emit input->selectionEndChanged();if(!guard)return false;
    if(before.text!=after.text||before.undoState!=after.undoState)emit input->textEdited();if(!guard)return false;
    if(before.text!=after.text)emit input->textChanged();if(!guard)return false;
    if(before.acceptable!=after.acceptable)emit input->acceptableInputChanged();if(!guard)return false;
    if(before.undo!=after.undo)emit input->canUndoChanged();if(!guard)return false;
    if(before.redo!=after.redo)emit input->canRedoChanged();if(!guard)return false;
    if(before.composing!=after.composing)emit input->inputMethodComposingChanged();if(!guard)return false;
    if(before.cursorVisible!=after.cursorVisible)emit input->cursorVisibleChanged(after.cursorVisible);
    return bool(guard);
}
}

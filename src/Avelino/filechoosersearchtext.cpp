#include "filechoosersearchtext.h"
#include "filechooserexpression.h"
#include <QtQuick/private/qaccessiblequickitem_p.h>
#include <QAccessible>
#include <QCoreApplication>
#include <QFontMetricsF>
#include <QImage>
#include <QInputMethodEvent>
#include <QKeyEvent>
#include <QKeySequence>
#include <QPointer>
#include <QQmlEngine>
#include <QQuickTextDocument>
#include <QSignalBlocker>
#include <QTextCursor>
#include <QTextDocument>
#include <algorithm>

static_assert(QT_VERSION==QT_VERSION_CHECK(6,8,3),"Revalidate atomic search document editing and accessibility before upgrading Qt");
namespace {
QString tokenLabel(const QString &mode,const QString &query){return (mode=="filename"?QStringLiteral("Filename: "):QStringLiteral("Everything: "))+query;}
QString tokenModeLabel(const QString &mode){return mode=="filename"?QStringLiteral("NAME"):QStringLiteral("ANY");}
qreal tokenModeWidth(const QFont &font,const QString &mode){
    auto captionFont=font;captionFont.setPixelSize(9);captionFont.setWeight(QFont::Normal);
    return QFontMetricsF(captionFont).horizontalAdvance(tokenModeLabel(mode))+14;
}
constexpr qreal TokenGap=6,TokenHeight=15;
class SearchTextAccessible final:public QAccessibleQuickItem,public QAccessibleEditableTextInterface {
public:
    using QAccessibleQuickItem::QAccessibleQuickItem;
    void *interface_cast(QAccessible::InterfaceType type)override{
        if(type==QAccessible::EditableTextInterface)return static_cast<QAccessibleEditableTextInterface*>(this);
        return QAccessibleQuickItem::interface_cast(type);
    }
    void deleteText(int start,int end)override{replaceText(start,end,{});}
    void insertText(int offset,const QString &text)override{replaceText(offset,offset,text);}
    void replaceText(int start,int end,const QString &text)override{
        QPointer<FileChooserSearchText> editor=qobject_cast<FileChooserSearchText*>(object());
        if(!editor||editor->isReadOnly()||!editor->isEnabled()||start<0||end<start||end>characterCount())return;
        editor->select(start,end);if(!editor)return;
        if(text.isEmpty()){editor->remove(start,end);return;}
        QInputMethodEvent event;event.setCommitString(text);QCoreApplication::sendEvent(editor,&event);
    }
    void setText(QAccessible::Text kind,const QString &text)override{
        if(kind==QAccessible::Value)replaceText(0,characterCount(),text);
        else QAccessibleQuickItem::setText(kind,text);
    }
};
}
FileChooserSearchText::FileChooserSearchText(QQuickItem *parent):QQuickTextArea(parent),m_tokens(new FileChooserSearchTokens(this)){
    static const bool registered=[] {QAccessible::installFactory(+[](const QString &,QObject *object)->QAccessibleInterface*{
        if(auto editor=qobject_cast<FileChooserSearchText*>(object))return new SearchTextAccessible(editor);
        return nullptr;
    });return true;}();Q_UNUSED(registered);
    setTextFormat(PlainText);setWrapMode(NoWrap);setTextMargin(0);
    setSelectByMouse(true);setSelectByKeyboard(true);
    connect(editDocument(),&QTextDocument::contentsChanged,this,&FileChooserSearchText::documentChanged);
    connect(this,&QQuickTextEdit::cursorPositionChanged,this,&FileChooserSearchText::markDraftChanged);
    connect(this,&QQuickTextEdit::selectedTextChanged,this,&FileChooserSearchText::markDraftChanged);
    connect(this,&QQuickTextEdit::contentSizeChanged,this,&FileChooserSearchText::markLayoutChanged);
    connect(this,&QQuickItem::heightChanged,this,&FileChooserSearchText::markLayoutChanged);
}
QTextDocument *FileChooserSearchText::editDocument()const{return const_cast<FileChooserSearchText*>(this)->textDocument()->textDocument();}
QTextCharFormat FileChooserSearchText::formatAt(int position)const{
    QTextCursor cursor(editDocument());cursor.setPosition(position);cursor.setPosition(position+1,QTextCursor::KeepAnchor);return cursor.charFormat();
}
bool FileChooserSearchText::tokenAt(int position)const{
    return position>=0&&position<editDocument()->characterCount()-1
        &&editDocument()->characterAt(position)==QChar::ObjectReplacementCharacter
        &&formatAt(position).isImageFormat()&&formatAt(position).hasProperty(ModeProperty);
}
QTextImageFormat FileChooserSearchText::tokenFormat(const QString &mode,const QString &query,const QString &identity){
    const auto resource=identity.isEmpty()?QStringLiteral("avelino-search-token:%1").arg(++m_resource):identity;
    QImage image(1,1,QImage::Format_ARGB32_Premultiplied);image.fill(Qt::transparent);
    editDocument()->addResource(QTextDocument::ImageResource,QUrl(resource),image);
    QTextImageFormat format;format.setName(resource);
    // The gap belongs to the inline object, outside its painted two-part cell.
    // Keep the full query width so Qt scrolls the document instead of eliding it.
    format.setWidth(tokenModeWidth(font(),mode)+QFontMetricsF(font()).horizontalAdvance(query)+8+TokenGap);format.setHeight(TokenHeight);
    format.setProperty(ModeProperty,mode);format.setProperty(QueryProperty,query);return format;
}
QVariantList FileChooserSearchText::expression()const{
    QVariantList result;QString raw;
    const auto flush=[&]{if(!raw.isEmpty()){result.append(QVariantMap{{"kind","text"},{"text",raw}});raw.clear();}};
    for(int position=0;position<editDocument()->characterCount()-1;++position){
        if(tokenAt(position)){
            flush();const auto format=formatAt(position);
            result.append(QVariantMap{{"kind","token"},{"mode",format.property(ModeProperty)},{"query",format.property(QueryProperty)}});
        }else{
            const auto character=editDocument()->characterAt(position);raw+=character==QChar::ParagraphSeparator?QChar('\n'):character;
        }
    }
    flush();return result;
}
QList<FileChooserSearchTokens::Row> FileChooserSearchText::tokenRows()const{
    QList<FileChooserSearchTokens::Row> result;
    for(int position=0;position<editDocument()->characterCount()-1;++position)if(tokenAt(position)){
        const auto format=formatAt(position).toImageFormat();const auto rectangle=positionToRectangle(position);
        const auto mode=format.property(ModeProperty).toString(),query=format.property(QueryProperty).toString();
        result.append({format.name(),QVariantMap{{"position",position},{"mode",mode},{"query",query},{"label",tokenLabel(mode,query)},
            {"modeLabel",tokenModeLabel(mode)},{"modeWidth",tokenModeWidth(font(),mode)},
            {"x",rectangle.x()},{"y",rectangle.y()+(rectangle.height()-format.height())/2},{"width",format.width()-TokenGap},{"height",format.height()}}});
    }
    return result;
}
QPair<int,int> FileChooserSearchText::draftRange()const{
    for(int position=selectionStart();position<selectionEnd();++position)if(tokenAt(position))return {-1,-1};
    int start=cursorPosition(),end=start;
    while(start>0&&!tokenAt(start-1))--start;
    while(end<editDocument()->characterCount()-1&&!tokenAt(end))++end;
    return start==end?QPair<int,int>{-1,-1}:QPair<int,int>{start,end};
}
QString FileChooserSearchText::draft()const{
    const auto range=draftRange();return range.first<0?QString():editDocument()->toPlainText().mid(range.first,range.second-range.first);
}
void FileChooserSearchText::reportError(const QString &message){if(auto engine=qjsEngine(this))engine->throwError(message);else qWarning().noquote()<<message;}
void FileChooserSearchText::setText(const QString &value){setExpression(value.isEmpty()?QVariantList{}:QVariantList{QVariantMap{{"kind","text"},{"text",value}}});}
void FileChooserSearchText::setExpression(const QVariantList &value){
    if(value==expression())return;
    const auto error=fileSearchExpressionError(value);if(!error.isEmpty()){reportError(error);return;}
    performTokenEdit([this,value]{
        QPointer<FileChooserSearchText> guard(this);QQuickTextArea::setText({});if(!guard)return;
        QTextCursor cursor(editDocument());cursor.beginEditBlock();
        for(const auto &part:value){
            const auto row=part.toMap();
            if(row.value("kind")=="token")cursor.insertImage(tokenFormat(row.value("mode").toString(),row.value("query").toString()));
            else cursor.insertText(row.value("text").toString());
        }
        cursor.endEditBlock();if(!guard)return;
        setCursorPosition(editDocument()->characterCount()-1);if(!guard)return;
        m_selections.clear();editDocument()->clearUndoRedoStacks();
    });
}
void FileChooserSearchText::commitDraft(const QString &mode){
    if(isReadOnly()||!isEnabled())return;
    if(mode!="filename"&&mode!="everything"){reportError("Search tokens require Filename or Everything mode");return;}
    const auto range=draftRange();if(range.first<0)return;
    const auto query=draft();
    performTokenEdit([this,mode,query,range]{
        QPointer<FileChooserSearchText> guard(this);QTextCursor cursor(editDocument());cursor.setPosition(range.first);cursor.setPosition(range.second,QTextCursor::KeepAnchor);
        cursor.beginEditBlock();cursor.removeSelectedText();cursor.insertImage(tokenFormat(mode,query));cursor.endEditBlock();if(!guard)return;
        setCursorPosition(editDocument()->characterCount()-1);if(!guard)return;
        m_selections.clear();editDocument()->clearUndoRedoStacks();
    });
}
void FileChooserSearchText::setTokenModeAt(int position,const QString &mode){
    if(isReadOnly()||!isEnabled())return;
    if(mode!="filename"&&mode!="everything"){reportError("Search tokens require Filename or Everything mode");return;}
    if(!tokenAt(position)){reportError("Search token position is no longer valid");return;}
    const auto previous=formatAt(position);if(previous.property(ModeProperty)==mode)return;
    const auto query=previous.property(QueryProperty).toString(),identity=previous.toImageFormat().name();
    performTokenEdit([this,position,mode,query,identity]{
        QPointer<FileChooserSearchText> guard(this);QTextCursor cursor(editDocument());cursor.setPosition(position);cursor.setPosition(position+1,QTextCursor::KeepAnchor);
        cursor.setCharFormat(tokenFormat(mode,query,identity));if(!guard)return;
        m_selections.clear();editDocument()->clearUndoRedoStacks();
    });
}
void FileChooserSearchText::selectTokenAt(int position){
    if(!isEnabled())return;
    if(!tokenAt(position)){reportError("Search token position is no longer valid");return;}
    const auto identity=formatAt(position).toImageFormat().name();QPointer<FileChooserSearchText> guard(this);
    forceActiveFocus(Qt::MouseFocusReason);if(!guard||!isEnabled())return;
    if(!tokenAt(position)||formatAt(position).toImageFormat().name()!=identity)return;
    select(position,position+1);
}
void FileChooserSearchText::editTokenAt(int position){
    if(isReadOnly()||!isEnabled())return;
    if(!tokenAt(position)){reportError("Search token position is no longer valid");return;}
    const auto identity=formatAt(position).toImageFormat().name();QPointer<FileChooserSearchText> guard(this);
    forceActiveFocus(Qt::MouseFocusReason);if(!guard||isReadOnly()||!isEnabled())return;
    if(!tokenAt(position)||formatAt(position).toImageFormat().name()!=identity)return;
    const auto query=formatAt(position).property(QueryProperty).toString();
    const bool before=position>0&&!tokenAt(position-1);
    const bool after=position+1<editDocument()->characterCount()-1&&!tokenAt(position+1);
    const auto insertion=(before?QStringLiteral(" "):QString())+query+(after?QStringLiteral(" "):QString());
    // Native expansion preserves existing raw spaces and adds a separator at
    // each raw boundary. Qt owns the replacement and its single Undo command.
    performTokenEdit([this,position,query,insertion,before]{
        select(position,position+1);const auto selected=editState();
        QPointer<FileChooserSearchText> alive(this);QInputMethodEvent event;event.setCommitString(insertion);
        QQuickTextArea::inputMethodEvent(&event);if(!alive)return;
        finishHistory(selected,false);
        const int start=position+(before?1:0);select(start,start+query.size());
    });
}
FileChooserSearchText::QtState FileChooserSearchText::qtState()const{
    return {text(),selectedText(),cursorPosition(),selectionStart(),selectionEnd(),lineCount(),cursorRectangle(),QSizeF(contentWidth(),contentHeight()),canUndo(),canRedo()};
}
bool FileChooserSearchText::publishQtChanges(const QtState &before){
    const auto after=qtState();QPointer<FileChooserSearchText> guard(this);
    // Token commits publish only their settled document and Undo baseline.
    // Guard each signal: an observer may synchronously remove this control.
    if(before.text!=after.text)emit textChanged();if(!guard)return false;
    if(before.content!=after.content)emit contentSizeChanged();if(!guard)return false;
    if(before.lines!=after.lines)emit lineCountChanged();if(!guard)return false;
    if(before.cursor!=after.cursor)emit cursorPositionChanged();if(!guard)return false;
    if(before.start!=after.start)emit selectionStartChanged();if(!guard)return false;
    if(before.end!=after.end)emit selectionEndChanged();if(!guard)return false;
    if(before.selected!=after.selected)emit selectedTextChanged();if(!guard)return false;
    if(before.rectangle!=after.rectangle)emit cursorRectangleChanged();if(!guard)return false;
    if(before.undo!=after.undo)emit canUndoChanged();if(!guard)return false;
    if(before.redo!=after.redo)emit canRedoChanged();return bool(guard);
}
void FileChooserSearchText::performTokenEdit(const std::function<void()> &operation){
    const auto before=qtState();QPointer<FileChooserSearchText> guard(this);QSignalBlocker blocker(this);++m_editDepth;
    operation();if(!guard){blocker.dismiss();return;}
    m_contentsDirty=m_tokensDirty=m_draftDirty=true;blocker.unblock();
    if(!publishQtChanges(before))return;
    --m_editDepth;publishChanges();
}
FileChooserSearchText::EditState FileChooserSearchText::editState()const{
    bool selected=false;for(int position=selectionStart();position<selectionEnd();++position)selected=selected||tokenAt(position);
    return {editDocument()->availableUndoSteps(),editDocument()->revision(),selectionStart(),selectionEnd(),cursorPosition(),selected};
}
void FileChooserSearchText::finishHistory(const EditState &before,bool replay){
    if(replay){
        const auto found=m_selections.constFind(editDocument()->availableUndoSteps());
        if(found!=m_selections.cend()){
            const auto value=found.value();
            if(std::min(value.start,value.end)>=0&&std::max(value.start,value.end)<editDocument()->characterCount())select(value.start,value.end);
        }
        return;
    }
    if(before.revision==editDocument()->revision())return;
    auto later=m_selections.upperBound(before.undo);while(later!=m_selections.end())later=m_selections.erase(later);
    if(before.selectedToken)m_selections.insert(before.undo,before.cursor==before.start?Selection{before.end,before.start}:Selection{before.start,before.end});
    else m_selections.remove(before.undo);
}
void FileChooserSearchText::performEdit(const std::function<void()> &operation,bool replay){
    const auto before=editState();QPointer<FileChooserSearchText> guard(this);const bool outer=m_editDepth++==0;
    operation();if(!guard)return;
    if(outer)finishHistory(before,replay);if(!guard)return;
    --m_editDepth;if(outer)publishChanges();
}
void FileChooserSearchText::undo(){performEdit([this]{QQuickTextArea::undo();},true);}
void FileChooserSearchText::redo(){performEdit([this]{QQuickTextArea::redo();},true);}
void FileChooserSearchText::cut(){performEdit([this]{QQuickTextArea::cut();});}
void FileChooserSearchText::paste(){performEdit([this]{QQuickTextArea::paste();});}
void FileChooserSearchText::insert(int position,const QString &text){performEdit([this,position,text]{QQuickTextArea::insert(position,text);});}
void FileChooserSearchText::remove(int start,int end){performEdit([this,start,end]{QQuickTextArea::remove(start,end);});}
void FileChooserSearchText::append(const QString &text){performEdit([this,text]{QQuickTextArea::append(text);});}
void FileChooserSearchText::clear(){performEdit([this]{QQuickTextArea::clear();});}
void FileChooserSearchText::keyPressEvent(QKeyEvent *event){
    if(!isReadOnly()&&event->modifiers()==Qt::NoModifier&&selectionStart()==selectionEnd()){
        const int position=cursorPosition();
        if((event->key()==Qt::Key_Backspace||event->key()==Qt::Key_Left)&&tokenAt(position-1)){select(position-1,position);event->accept();return;}
        if(event->key()==Qt::Key_Right&&tokenAt(position)){select(position,position+1);event->accept();return;}
    }
    const bool replay=event->matches(QKeySequence::Undo)||event->matches(QKeySequence::Redo);
    performEdit([this,event]{QQuickTextArea::keyPressEvent(event);},replay);
}
void FileChooserSearchText::inputMethodEvent(QInputMethodEvent *event){performEdit([this,event]{QQuickTextArea::inputMethodEvent(event);});}
void FileChooserSearchText::documentChanged(){
    if(!m_editDepth)m_selections.clear();m_contentsDirty=m_tokensDirty=m_draftDirty=true;if(!m_editDepth)publishChanges();
}
void FileChooserSearchText::markLayoutChanged(){m_tokensDirty=true;if(!m_editDepth)publishChanges();}
void FileChooserSearchText::markDraftChanged(){m_draftDirty=true;if(!m_editDepth)publishChanges();}
void FileChooserSearchText::publishChanges(){
    if(m_publishing||m_editDepth)return;
    m_publishing=true;QPointer<FileChooserSearchText> guard(this);
    while(m_contentsDirty||m_tokensDirty||m_draftDirty){
        const auto value=expression();const bool changed=value!=m_reportedExpression,tokens=m_tokensDirty,draft=m_draftDirty;
        m_reportedExpression=value;m_contentsDirty=m_tokensDirty=m_draftDirty=false;
        if(tokens&&!m_tokens->synchronize(tokenRows()))return;
        if(!guard)return;
        if(changed)emit expressionChanged();if(!guard)return;
        if(tokens)emit tokenLayoutChanged();if(!guard)return;
        if(draft)emit draftChanged();if(!guard)return;
    }
    m_publishing=false;
}

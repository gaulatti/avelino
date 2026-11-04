#include <QtQuickTemplates2/private/qquicktextarea_p.h>
#include <QQuickTextDocument>
#include <QAccessible>
#include <QtQuick/private/qaccessiblequickitem_p.h>
#include <QInputMethodEvent>
#include <QMap>
#include <QPointer>
#include <QFile>
#include <QFontMetrics>
#include <QGuiApplication>
#include <QImage>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QKeyEvent>
#include <QPainter>
#include <QQuickItemGrabResult>
#include <QQuickWindow>
#include <QQuickView>
#include <QQmlEngine>
#include <QtQml/qqml.h>
#include <QSignalSpy>
#include <QTextCursor>
#include <QTextDocument>
#include <QTextImageFormat>
#include <QtTest>
#include <stdexcept>

static_assert(QT_VERSION==QT_VERSION_CHECK(6,8,3));
static void require(bool value,const char *message){if(!value)throw std::runtime_error(message);}
class AtomicEditor:public QQuickTextArea {
    Q_OBJECT
    int nextResource=0;
    struct EditState {int undo,revision,start,end,cursor;bool selectedToken;};
    struct TokenSelection {int start,end;};
    QMap<int,TokenSelection> restoredSelections;
    EditState editState(){
        bool selected=false;
        for(int i=selectionStart();i<selectionEnd();++i)selected=selected||tokenAt(i);
        return {document()->availableUndoSteps(),document()->revision(),selectionStart(),selectionEnd(),cursorPosition(),selected};
    }
    void finishEdit(const EditState &before,bool replay){
        if(replay){
            const auto found=restoredSelections.constFind(document()->availableUndoSteps());
            if(found!=restoredSelections.cend()){
                const auto selection=found.value();
                if(selection.start>=0&&selection.end<=document()->characterCount()-1)
                    select(selection.start,selection.end);
            }
            return;
        }
        if(before.revision==document()->revision())return;
        auto later=restoredSelections.upperBound(before.undo);
        while(later!=restoredSelections.end())later=restoredSelections.erase(later);
        if(before.selectedToken)restoredSelections.insert(before.undo,
            before.cursor==before.start?TokenSelection{before.end,before.start}:TokenSelection{before.start,before.end});
        else restoredSelections.remove(before.undo);
    }
public:
    static void installAccessibleFactory();
    enum {ModeProperty=QTextFormat::UserProperty+1,QueryProperty};
    explicit AtomicEditor(QQuickItem *parent=nullptr):QQuickTextArea(parent){
        installAccessibleFactory();
        setWidth(340);setHeight(36);setTextMargin(0);setWrapMode(NoWrap);
        setSelectByMouse(true);setSelectByKeyboard(true);
        QFont value=QGuiApplication::font();value.setPixelSize(13);setFont(value);
        setColor(Qt::black);setSelectionColor(QColor("#a6cef5"));setSelectedTextColor(Qt::black);
    }
    QTextDocument *document(){return textDocument()->textDocument();}
    QTextCharFormat formatAt(int position){
        QTextCursor cursor(document());cursor.setPosition(position);cursor.setPosition(position+1,QTextCursor::KeepAnchor);
        return cursor.charFormat();
    }
    bool tokenAt(int position){return position>=0&&position<document()->characterCount()-1
        &&document()->characterAt(position)==QChar::ObjectReplacementCharacter
        &&formatAt(position).isImageFormat()&&formatAt(position).hasProperty(ModeProperty);}
    void commit(const QString &mode,int start,int end){
        QTextCursor cursor(document());cursor.setPosition(start);cursor.setPosition(end,QTextCursor::KeepAnchor);
        const auto query=cursor.selectedText();require(!query.isEmpty(),"Empty commit range");
        const auto label=(mode=="filename"?QStringLiteral("Filename: "):QStringLiteral("Everything: "))+query;
        const int width=QFontMetrics(font()).horizontalAdvance(label)+14;
        QImage image(width,22,QImage::Format_ARGB32_Premultiplied);image.fill(QColor("#eeeeee"));
        {QPainter painter(&image);painter.setPen(Qt::black);painter.setFont(font());painter.drawText(QRect(7,0,width-14,22),Qt::AlignVCenter,label);}
        const auto name=QStringLiteral("token:%1").arg(++nextResource);
        document()->addResource(QTextDocument::ImageResource,QUrl(name),image);
        QTextImageFormat format;format.setName(name);format.setWidth(width);format.setHeight(22);
        format.setProperty(ModeProperty,mode);format.setProperty(QueryProperty,query);
        cursor.beginEditBlock();cursor.removeSelectedText();cursor.insertImage(format);cursor.endEditBlock();
        setCursorPosition(document()->characterCount()-1);document()->clearUndoRedoStacks();restoredSelections.clear();
    }
    QJsonArray segments(){
        QJsonArray result;QString raw;
        const auto flush=[&]{if(!raw.isEmpty()){result.append(QJsonObject{{"kind","text"},{"text",raw}});raw.clear();}};
        for(int i=0;i<document()->characterCount()-1;++i){
            if(tokenAt(i)){flush();const auto format=formatAt(i);result.append(QJsonObject{{"kind","token"},
                {"mode",format.property(ModeProperty).toString()},{"query",format.property(QueryProperty).toString()}});}
            else raw+=document()->characterAt(i);
        }
        flush();return result;
    }
    Q_INVOKABLE void undo(){
        const auto before=editState();QPointer<AtomicEditor> guard(this);
        QQuickTextArea::undo();if(guard)finishEdit(before,true);
    }
    Q_INVOKABLE void redo(){
        const auto before=editState();QPointer<AtomicEditor> guard(this);
        QQuickTextArea::redo();if(guard)finishEdit(before,true);
    }
protected:
    void inputMethodEvent(QInputMethodEvent *event)override{
        const auto before=editState();QPointer<AtomicEditor> guard(this);
        QQuickTextArea::inputMethodEvent(event);if(guard)finishEdit(before,false);
    }
    void keyPressEvent(QKeyEvent *event)override{
        if(!isReadOnly()&&event->modifiers()==Qt::NoModifier&&selectionStart()==selectionEnd()){
            const int position=cursorPosition();
            if((event->key()==Qt::Key_Backspace||event->key()==Qt::Key_Left)&&tokenAt(position-1)){
                select(position-1,position);event->accept();return;
            }
            if(event->key()==Qt::Key_Right&&tokenAt(position)){
                select(position,position+1);event->accept();return;
            }
        }
        const auto before=editState();QPointer<AtomicEditor> guard(this);
        const bool replay=event->matches(QKeySequence::Undo)||event->matches(QKeySequence::Redo);
        QQuickTextArea::keyPressEvent(event);if(guard)finishEdit(before,replay);
    }
};
class AtomicAccessible final:public QAccessibleQuickItem,public QAccessibleEditableTextInterface {
public:
    using QAccessibleQuickItem::QAccessibleQuickItem;
    void *interface_cast(QAccessible::InterfaceType type)override{
        if(type==QAccessible::EditableTextInterface)return static_cast<QAccessibleEditableTextInterface*>(this);
        return QAccessibleQuickItem::interface_cast(type);
    }
    void deleteText(int start,int end)override{replaceText(start,end,{});}
    void insertText(int offset,const QString &text)override{replaceText(offset,offset,text);}
    void replaceText(int start,int end,const QString &text)override{
        QPointer<AtomicEditor> editor=qobject_cast<AtomicEditor*>(object());
        if(!editor||editor->isReadOnly()||!editor->isEnabled()||start<0||end<start||end>characterCount())return;
        editor->select(start,end);if(!editor)return;
        QInputMethodEvent event;event.setCommitString(text);QCoreApplication::sendEvent(editor,&event);
    }
    void setText(QAccessible::Text kind,const QString &text)override{
        if(kind==QAccessible::Value)replaceText(0,characterCount(),text);
        else QAccessibleQuickItem::setText(kind,text);
    }
};
void AtomicEditor::installAccessibleFactory(){
    static const bool registered=[] {QAccessible::installFactory(+[](const QString &,QObject *object)->QAccessibleInterface*{
        if(auto editor=qobject_cast<AtomicEditor*>(object))return new AtomicAccessible(editor);
        return nullptr;
    });return true;}();Q_UNUSED(registered);
}
static void type(QWindow *window,const QString &value){for(auto c:value.toLatin1())QTest::keyClick(window,c);}
int main(int argc,char **argv){
    QGuiApplication app(argc,argv);QAccessible::setActive(true);
    qmlRegisterType<AtomicEditor>("Prototype.Atomic",1,0,"AtomicEditor");
    QJsonArray variants;QString failure;int code=0;
    try{
        for(const auto &variant:QStringList{"plain","rich"}){
            QQuickView window;window.setColor(Qt::white);
            window.setSource(QUrl::fromLocalFile("/prototype/fixture.qml"));
            if(window.status()!=QQuickView::Ready)for(const auto &error:window.errors())qWarning().noquote()<<error.toString();
            require(window.status()==QQuickView::Ready,"QML host failed");
            auto *instance=window.rootObject()->findChild<AtomicEditor *>("editor");require(instance,"QML editor missing");
            auto &editor=*instance;
            auto *viewport=window.rootObject()->findChild<QQuickItem *>("viewport");require(viewport,"Viewport missing");
            editor.setTextFormat(variant=="plain"?QQuickTextEdit::PlainText:QQuickTextEdit::RichText);
            window.show();require(QTest::qWaitForWindowExposed(&window),"Window not exposed");
            window.requestActivate();require(QTest::qWaitForWindowActive(&window),"Window not active");editor.forceActiveFocus();
            require(editor.hasActiveFocus(),"Editor not focused");
            QJsonArray observations;
            const auto observe=[&](const QString &phase){
                QCoreApplication::processEvents();
                auto accessible=QAccessible::queryAccessibleInterface(&editor);
                auto text=accessible?accessible->textInterface():nullptr;
                observations.append(QJsonObject{{"viewportWidth",viewport->width()},{"scrollX",viewport->property("contentX").toReal()},
                    {"cursorSceneX",editor.mapToScene(editor.cursorRectangle().topLeft()).x()},
                    {"viewportSceneLeft",viewport->mapToScene(QPointF(0,0)).x()},
                    {"phase",phase},{"plainText",editor.document()->toPlainText()},
                    {"propertyText",editor.text()},{"selectedText",editor.selectedText()},
                    {"cursorPosition",editor.cursorPosition()},{"canUndo",editor.canUndo()},{"canRedo",editor.canRedo()},
                    {"segments",editor.segments()},{"position0x",editor.positionToRectangle(0).x()},{"availableUndoSteps",editor.document()->availableUndoSteps()},{"availableRedoSteps",editor.document()->availableRedoSteps()},{"cursorX",editor.cursorRectangle().x()},{"controlWidth",editor.width()},{"contentWidth",editor.contentWidth()},
                    {"position1x",editor.positionToRectangle(1).x()},
                    {"accessibleExists",accessible!=nullptr},{"accessibleRole",accessible?int(accessible->role()):-1},
                    {"accessibleCharacterCount",text?text->characterCount():-1},
                    {"accessibleText",text?text->text(0,text->characterCount()):QString()},
                    {"accessibleEditable",accessible&&accessible->editableTextInterface()!=nullptr}});
            };
            const QString query="avelinoulnacerulean";type(&window,query);observe("raw");
            editor.commit("filename",0,query.size());observe("committed");
            require(!editor.canUndo()&&!editor.canRedo(),"Commit did not clear Qt document history");
            QTest::keyClick(&window,Qt::Key_Backspace);observe("first-backspace");
            require(editor.selectedText()==QString(QChar::ObjectReplacementCharacter),"First Backspace did not select object");
            QTest::keyClick(&window,Qt::Key_Backspace);observe("second-backspace");
            require(editor.document()->toPlainText().isEmpty(),"Second Backspace did not delete object");
            QTest::keyClick(&window,Qt::Key_Z,Qt::ControlModifier);observe("deletion-undo");
            require(editor.segments().size()==1&&editor.segments()[0].toObject()["query"]==query,"Undo lost token metadata");
            require(editor.canRedo(),"Undo lost Redo");
            require(editor.selectedText()==QString(QChar::ObjectReplacementCharacter),"Undo did not restore deleted token selection");
            QTest::keyClick(&window,Qt::Key_Right);type(&window,"x");observe("trailing-draft");
            require(editor.document()->toPlainText()==QString(QChar::ObjectReplacementCharacter)+"x","Trailing draft changed token");
            editor.commit("filename",1,2);observe("two-tokens");
            require(editor.segments().size()==2,"Second token not distinct");
            editor.setCursorPosition(0);type(&window,"y");observe("leading-draft");
            require(editor.document()->toPlainText()=="y"+QString(2,QChar::ObjectReplacementCharacter),"Leading draft changed tokens");
            editor.commit("everything",0,1);observe("leading-token");
            const auto cursorScene=editor.mapToScene(editor.cursorRectangle().topLeft());
            const auto viewportScene=viewport->mapToScene(QPointF(0,0));
            require(viewport->property("contentX").toReal()>0,"Long token document did not scroll");
            require(cursorScene.x()>=viewportScene.x()&&cursorScene.x()+editor.cursorRectangle().width()<=viewportScene.x()+viewport->width()+0.01,"Long document cursor outside viewport");
            editor.setCursorPosition(0);observe("scroll-to-start");
            require(viewport->property("contentX").toReal()==0,"Beginning of document not reachable");
            editor.setCursorPosition(1);type(&window,"z");observe("middle-draft");
            QTest::keyClick(&window,Qt::Key_Delete);observe("forward-delete");
            require(editor.segments().size()==3&&editor.segments()[2].toObject()["query"]=="x","Forward Delete removed wrong object");
            editor.select(0,1);type(&window,"name");observe("replacement");
            QTest::keyClick(&window,Qt::Key_Z,Qt::ControlModifier);observe("replacement-undo");
            require(editor.segments()[0].toObject()["query"]=="y","Replacement Undo lost first token");
            require(editor.selectedText()==QString(QChar::ObjectReplacementCharacter),"Replacement Undo did not select restored object");
            QTest::keyClick(&window,Qt::Key_Z,Qt::ControlModifier|Qt::ShiftModifier);observe("replacement-redo");
            require(editor.segments()[0].toObject()["text"].toString().startsWith("name"),"Replacement Redo failed");
            editor.setText(query);editor.commit("everything",0,query.size());
            type(&window,"pine");editor.commit("filename",1,5);
            auto accessible=QAccessible::queryAccessibleInterface(&editor);
            auto editable=accessible?accessible->editableTextInterface():nullptr;
            require(editable,"Editable accessibility interface missing");
            editable->replaceText(0,1,"name");observe("assistive-replacement");
            require(editor.document()->toPlainText()=="name"+QString(QChar::ObjectReplacementCharacter),"Assistive replacement changed other token");
            editor.undo();observe("assistive-undo");
            require(editor.segments().size()==2&&editor.segments()[0].toObject()["query"]==query,"Assistive Undo lost token metadata");
            require(editor.selectedText()==QString(QChar::ObjectReplacementCharacter),"Assistive Undo did not select restored token");
            editor.redo();observe("assistive-redo");
            require(editor.document()->toPlainText()=="name"+QString(QChar::ObjectReplacementCharacter),"Assistive Redo failed");
            editor.setReadOnly(true);editable->replaceText(0,4,"blocked");observe("assistive-readonly");
            require(editor.document()->toPlainText()=="name"+QString(QChar::ObjectReplacementCharacter),"Read-only assistive write accepted");
            editor.setReadOnly(false);editor.setEnabled(false);editable->deleteText(0,4);observe("assistive-disabled");
            require(editor.document()->toPlainText()=="name"+QString(QChar::ObjectReplacementCharacter),"Disabled assistive write accepted");
            editor.setEnabled(true);editor.undo();editor.setCursorPosition(1);
            QInputMethodEvent preedit(QString::fromUtf8("かな"),{});QCoreApplication::sendEvent(&editor,&preedit);observe("ime-preedit");
            require(editor.document()->toPlainText()==QString(2,QChar::ObjectReplacementCharacter),"Preedit entered committed query");
            QInputMethodEvent commit;commit.setCommitString(QString::fromUtf8("かな"));QCoreApplication::sendEvent(&editor,&commit);observe("ime-commit-between-tokens");
            require(editor.document()->toPlainText()==QString(QChar::ObjectReplacementCharacter)+QString::fromUtf8("かな")+QString(QChar::ObjectReplacementCharacter),"IME changed surrounding tokens");
            require(editor.segments()[0].toObject()["query"]==query&&editor.segments()[2].toObject()["query"]=="pine","IME lost token metadata");
            editor.undo();observe("ime-undo");require(editor.segments().size()==2,"IME Undo did not retain two tokens");
            editor.redo();observe("ime-redo");require(editor.segments().size()==3,"IME Redo failed");
            auto capture=window.contentItem()->grabToImage();require(bool(capture),"Capture unavailable");
            QSignalSpy ready(capture.data(),&QQuickItemGrabResult::ready);
            if(capture->image().isNull())require(ready.wait(5000),"Capture timed out");
            require(capture->image().save("/output/"+variant+".png"),"Capture save failed");
            variants.append(QJsonObject{{"variant",variant},{"observations",observations}});
        }
    }catch(const std::exception &error){code=1;failure=QString::fromUtf8(error.what());}
    const QJsonObject report{{"exitCode",code},{"failure",failure},{"variants",variants},{"qt",qVersion()},
        {"registeredInAvelino",false},{"nativeMatchingAccepted",false},{"physicalInput",false},{"accepted",false}};
    QFile output("/output/runtime.json");if(!output.open(QIODevice::WriteOnly))return 2;
    output.write(QJsonDocument(report).toJson());qInfo().noquote()<<QJsonDocument(report).toJson(QJsonDocument::Compact);return code;
}

#include "main.moc"

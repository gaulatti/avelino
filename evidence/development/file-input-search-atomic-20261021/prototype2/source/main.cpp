#include <QtQuickTemplates2/private/qquicktextarea_p.h>
#include <QQuickTextDocument>
#include <QAccessible>
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
public:
    enum {ModeProperty=QTextFormat::UserProperty+1,QueryProperty};
    explicit AtomicEditor(QQuickItem *parent=nullptr):QQuickTextArea(parent){
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
        setCursorPosition(document()->characterCount()-1);document()->clearUndoRedoStacks();
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
protected:
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
        QQuickTextArea::keyPressEvent(event);
    }
};
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
            editor.setTextFormat(variant=="plain"?QQuickTextEdit::PlainText:QQuickTextEdit::RichText);
            window.show();require(QTest::qWaitForWindowExposed(&window),"Window not exposed");
            window.requestActivate();require(QTest::qWaitForWindowActive(&window),"Window not active");editor.forceActiveFocus();
            require(editor.hasActiveFocus(),"Editor not focused");
            QJsonArray observations;
            const auto observe=[&](const QString &phase){
                auto accessible=QAccessible::queryAccessibleInterface(&editor);
                auto text=accessible?accessible->textInterface():nullptr;
                observations.append(QJsonObject{{"phase",phase},{"plainText",editor.document()->toPlainText()},
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
            QTest::keyClick(&window,Qt::Key_Right);type(&window,"x");observe("trailing-draft");
            require(editor.document()->toPlainText()==QString(QChar::ObjectReplacementCharacter)+"x","Trailing draft changed token");
            editor.commit("filename",1,2);observe("two-tokens");
            require(editor.segments().size()==2,"Second token not distinct");
            editor.setCursorPosition(0);type(&window,"y");observe("leading-draft");
            require(editor.document()->toPlainText()=="y"+QString(2,QChar::ObjectReplacementCharacter),"Leading draft changed tokens");
            editor.commit("everything",0,1);observe("leading-token");
            editor.setCursorPosition(1);type(&window,"z");observe("middle-draft");
            QTest::keyClick(&window,Qt::Key_Delete);observe("forward-delete");
            require(editor.segments().size()==3&&editor.segments()[2].toObject()["query"]=="x","Forward Delete removed wrong object");
            editor.select(0,1);type(&window,"name");observe("replacement");
            QTest::keyClick(&window,Qt::Key_Z,Qt::ControlModifier);observe("replacement-undo");
            require(editor.segments()[0].toObject()["query"]=="y","Replacement Undo lost first token");
            QTest::keyClick(&window,Qt::Key_Z,Qt::ControlModifier|Qt::ShiftModifier);observe("replacement-redo");
            require(editor.segments()[0].toObject()["text"].toString().startsWith("name"),"Replacement Redo failed");
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

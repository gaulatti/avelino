#include "filechooserbrowser.h"
#include <QAccessible>
#include <QDir>
#include <QFile>
#include <QImage>
#include <QInputMethodEvent>
#include <QJSValue>
#include <QQmlEngine>
#include <QQmlComponent>
#include <QJsonDocument>
#include <QQuickItem>
#include <QQuickItemGrabResult>
#include <QQuickView>
#include <QRegularExpression>
#include <QSettings>
#include <QScopeGuard>
#include <QSignalSpy>
#include <QTemporaryDir>
#include <QtTest>

class SearchEditorDestroyer:public QObject {
    Q_OBJECT
public:
    QPointer<QObject> target;
public slots:
    void destroy(){delete target.data();}
};

class FileSearchTests:public QObject {
    Q_OBJECT
    QString m_root,m_captures;
    bool m_unavailable;
    QTemporaryDir m_config;
    const QString token="avelinoulnacerulean";
    QQuickItem *find(QQuickItem *item,const QString &name){
        if(!item)return nullptr;if(item->objectName()==name)return item;
        for(auto child:item->childItems())if(auto found=find(child,name))return found;return nullptr;
    }
    QQuickItem *visible(const QString &name){
        for(auto window:QGuiApplication::topLevelWindows())if(auto quick=qobject_cast<QQuickWindow*>(window);quick&&quick->isVisible())
            if(auto item=find(quick->contentItem(),name);item&&item->isVisible())return item;return nullptr;
    }
    void click(QQuickItem *item){QVERIFY(item);QVERIFY(item->window());QTest::mouseClick(item->window(),Qt::LeftButton,{},item->mapToScene(item->boundingRect().center()).toPoint());}
    void type(QWindow *window,const QString &text){for(auto character:text.toLatin1())QTest::keyClick(window,character);}
    bool load(QQuickView &view){
        view.engine()->addImportPath(AVELINO_FILE_INPUT_IMPORT_PATH);
        view.setInitialProperties({{"fixtureRoot",QUrl::fromLocalFile(m_root)}});
        view.setSource(QUrl("qrc:/file-input-tests/fileinput-fixture.qml"));
        if(view.status()!=QQuickView::Ready){for(auto error:view.errors())qWarning().noquote()<<error.toString();return false;}
        view.show();return QTest::qWaitForWindowExposed(&view);
    }
    FileChooserBrowser *open(QQuickView &view){
        auto control=view.rootObject()->findChild<QQuickItem*>("fileInput");if(!control)return nullptr;
        click(control->property("inputItem").value<QQuickItem*>());
        return control->property("browser").value<FileChooserBrowser*>();
    }
    int row(FileChooserSearch *search,const QString &name){for(int i=0;i<search->count();++i)if(search->entry(i)["name"]==name)return i;return -1;}
    static QVariantList raw(const QString &text){return text.isEmpty()?QVariantList{}:QVariantList{QVariantMap{{"kind","text"},{"text",text}}};}
    static QVariantList committed(const QString &mode,const QString &query){return {QVariantMap{{"kind","token"},{"mode",mode},{"query",query}}};}
    static void setRaw(FileChooserSearch *search,const QString &text){search->setExpression(raw(text));}
    static QString singleTermText(FileChooserSearch *search){
        const auto value=search->expression();if(value.size()!=1)return {};
        const auto row=value[0].toMap();return row.value(row.value("kind")=="token"?"query":"text").toString();
    }
    static QString singleTermMode(FileChooserSearch *search){
        const auto value=search->expression();if(value.size()!=1)return {};
        const auto row=value[0].toMap();return row.value("kind")=="token"?row.value("mode").toString():QStringLiteral("general");
    }
    QString indexState(FileChooserSearch *search){
        QStringList names;for(int i=0;i<search->count();++i)names.append(search->entry(i)["name"].toString());
        return QString("busy=%1 error=%2 expression=%3 folderOnly=%4 names=[%5]").arg(search->busy()).arg(search->error()).arg(QString::fromUtf8(QJsonDocument::fromVariant(search->expression()).toJson(QJsonDocument::Compact))).arg(search->folderOnly()).arg(names.join(", "));
    }
    QVariantList results(QQuickItem *fixture){return fixture->property("results").value<QJSValue>().toVariant().toList();}
    void put(const QString &path,const QByteArray &data){QFile file(path);QVERIFY(file.open(QIODevice::WriteOnly));QCOMPARE(file.write(data),qint64(data.size()));}
    void capture(QQuickItem *item,const QString &name){
        auto result=item->window()->contentItem()->grabToImage();QVERIFY(result);QSignalSpy ready(result.data(),&QQuickItemGrabResult::ready);
        if(result->image().isNull())QVERIFY(ready.wait(5000));
        QDir output(m_captures);QVERIFY(output.mkpath("."));
        const auto path=output.filePath(name+"-dpr"+QString::number(item->window()->devicePixelRatio())+".png");
        QVERIFY(!QFile::exists(path));QVERIFY(result->image().save(path));
    }
public:
    FileSearchTests(QString root,bool unavailable):m_root(std::move(root)),m_unavailable(unavailable){}
private slots:
    void init(){QTest::failOnWarning(QRegularExpression(".*(ReferenceError|TypeError|Unable to assign|should be coerced).*"));}
    void initTestCase(){QVERIFY(QFileInfo(m_root).isDir());QAccessible::setActive(true);
        QDir parent(AVELINO_FILE_SEARCH_EVIDENCE_DIR);QVERIFY(parent.mkpath("."));QTemporaryDir captures(parent.filePath("run-XXXXXX"));QVERIFY(captures.isValid());m_captures=captures.path();captures.setAutoRemove(false);qInfo().noquote()<<"FILE_SEARCH_CAPTURES"<<m_captures;
        QSettings::setPath(QSettings::NativeFormat,QSettings::UserScope,m_config.path());}
    void actualInputModesScopesAndOwner(){
        QQuickView view;QVERIFY(load(view));auto browser=open(view);QVERIFY(browser);QTRY_VERIFY(browser->active());
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);click(editor);type(editor->window(),token);
        auto location=visible("bleeckerFileChooserLocation");QVERIFY(location);
        QVERIFY(!editor->mapRectToScene(editor->boundingRect()).intersects(location->mapRectToScene(location->boundingRect())));
        auto search=browser->search();QTRY_VERIFY_WITH_TIMEOUT(!search->busy()&&row(search,"pine-only.txt")>=0,15000);
        QVERIFY(search->error().isEmpty());QCOMPARE(singleTermMode(search),"general");QVERIFY(!search->folderOnly());
        QTRY_VERIFY_WITH_TIMEOUT(row(search,token+"-outside.txt")>=0&&row(search,"pine-peer.txt")>=0,15000);
        capture(editor,"general-global");
        click(visible("bleeckerFileChooserSearchFolder"));QTRY_VERIFY(search->folderOnly());
        QTRY_VERIFY(!search->busy()&&row(search,token+"-outside.txt")<0&&row(search,"pine-peer.txt")<0&&row(search,token+"-child.txt")>=0);
        click(editor);QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Return);
        QTRY_COMPARE(singleTermMode(search),"filename");QTRY_VERIFY(!search->busy()&&row(search,"pine-only.txt")<0&&row(search,token+"-name.txt")>=0);
        capture(editor,"filename-folder");
        auto tokenControl=visible("bleeckerFileChooserSearchToken");QVERIFY(tokenControl);
        auto tokenAccessible=QAccessible::queryAccessibleInterface(tokenControl);QVERIFY(tokenAccessible&&tokenAccessible->actionInterface());
        QCOMPARE(tokenAccessible->role(),QAccessible::ButtonMenu);QVERIFY(tokenAccessible->state().hasPopup);
        QVERIFY(tokenAccessible->actionInterface()->actionNames().contains(QAccessibleActionInterface::pressAction()));
        tokenAccessible->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
        QTRY_VERIFY(visible("bleeckerFileChooserSearchMode_everything"));QVERIFY(tokenAccessible->state().expanded);
        QVERIFY(visible("bleeckerFileChooserSearchMode_filename"));
        QVERIFY2(!visible("bleeckerFileChooserSearchMode_general"),"The native token menu offers only Filename and Everything");
        capture(editor,"token-menu");
        auto everythingAccessible=QAccessible::queryAccessibleInterface(visible("bleeckerFileChooserSearchMode_everything"));
        QVERIFY(everythingAccessible&&everythingAccessible->actionInterface());QCOMPARE(everythingAccessible->role(),QAccessible::MenuItem);
        everythingAccessible->actionInterface()->doAction(QAccessibleActionInterface::pressAction());QTRY_COMPARE(singleTermMode(search),"everything");
        QTRY_VERIFY(!search->busy()&&row(search,"pine-only.txt")>=0&&row(search,token+"-name.txt")>=0);
        QCOMPARE(visible("bleeckerFileChooserSearchToken"),tokenControl);
        tokenAccessible->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
        QTRY_VERIFY(visible("bleeckerFileChooserSearchMode_everything"));
        QVERIFY(visible("bleeckerFileChooserSearchMode_filename"));
        QVERIFY(!visible("bleeckerFileChooserSearchMode_general"));
        everythingAccessible=QAccessible::queryAccessibleInterface(visible("bleeckerFileChooserSearchMode_everything"));
        QVERIFY(everythingAccessible&&everythingAccessible->state().checked);
        everythingAccessible->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
        QTRY_VERIFY(!visible("bleeckerFileChooserSearchMode_everything"));QCOMPARE(singleTermMode(search),"everything");
        const auto index=row(search,"pine-only.txt");auto item=visible("bleeckerFileChooserSearchRow_"+QString::number(index));QVERIFY(item);
        auto accessible=QAccessible::queryAccessibleInterface(item);QVERIFY(accessible&&accessible->actionInterface());
        accessible->actionInterface()->doAction(QAccessibleActionInterface::pressAction());QTRY_VERIFY(browser->canAccept());
        QCOMPARE(browser->selectedUrls(),QVariantList{QUrl::fromLocalFile(m_root+"/pine-only.txt")});
        capture(editor,"everything-selected");click(visible("bleeckerFileChooserOpen"));
        QTRY_COMPARE(results(view.rootObject()).size(),1);QVERIFY(view.rootObject()->property("visibleAtCallback").toBool());QVERIFY(!browser->active());
        QCOMPARE(results(view.rootObject())[0].toMap()["urls"].toList(),QVariantList{QUrl::fromLocalFile(m_root+"/pine-only.txt")});
    }
    void liveIndexUpdatesAndTypeRevalidation(){
        FileChooserBrowser browser;browser.setAllowedContentTypes({"text/plain"});QVERIFY(browser.open(QUrl::fromLocalFile(m_root)));
        auto search=browser.search();search->setFolderOnly(true);setRaw(search,token);
        QTRY_VERIFY_WITH_TIMEOUT(!search->busy()&&row(search,"pine-only.txt")>=0,15000);
        const auto path=m_root+"/live-body.txt";put(path,("Live content "+token+"\n").toUtf8());
        QTRY_VERIFY_WITH_TIMEOUT(row(search,"live-body.txt")>=0,15000);
        QVERIFY(QFile::remove(path));QTRY_VERIFY_WITH_TIMEOUT(row(search,"live-body.txt")<0,15000);
        search->select(row(search,"pine-only.txt"));QVERIFY(browser.canAccept());QSignalSpy owner(&browser,&FileChooserBrowser::result);
        browser.setAllowedContentTypes({"image/*"});browser.acceptSelection();QVERIFY(owner.isEmpty());
        QTRY_VERIFY(!search->busy()&&!browser.canAccept());
        QVERIFY(!search->entry(row(search,"pine-only.txt"))["eligible"].toBool());
        search->select(row(search,token+"-image.png"));QVERIFY(browser.canAccept());
        // Keep the shared ineligible image intact for later selection checks.
        // Exercise a vanished indexed selection with this test's own image.
        const auto imageName=token+"-live-image.png";const auto image=m_root+"/"+imageName;
        QImage pixels(1,1,QImage::Format_ARGB32);pixels.fill(Qt::blue);QVERIFY(pixels.save(image));
        QTRY_VERIFY2_WITH_TIMEOUT(!search->busy()&&row(search,imageName)>=0,qPrintable(indexState(search)),15000);
        search->select(row(search,imageName));QVERIFY(browser.canAccept());
        QVERIFY(QFile::remove(image));browser.acceptSelection();
        QVERIFY(owner.isEmpty());QVERIFY(!browser.error().isEmpty());browser.cancel();
    }
    void accessibleResultSelectionAndOffscreenRows(){
        QQuickView view;QVERIFY(load(view));auto browser=open(view);QVERIFY(browser);
        auto search=browser->search();setRaw(search,token);
        QTRY_VERIFY2_WITH_TIMEOUT(!search->busy()&&row(search,"pine-only.txt")>=0&&row(search,"pine-peer.txt")>=0
            &&row(search,token+"-image.png")>=0&&row(search,token+"-name.txt")>=0,qPrintable(indexState(search)),15000);
        auto rows=visible("bleeckerFileChooserSearchResults");QVERIFY(rows);
        auto accessible=QAccessible::queryAccessibleInterface(rows);QVERIFY(accessible);
        QCOMPARE(accessible->role(),QAccessible::List);
        auto selection=accessible->selectionInterface();QVERIFY2(selection,"Search results must expose the same assistive selection operations as the chooser's other result views");
        QCOMPARE(accessible->childCount(),search->count());QCOMPARE(selection->selectedItemCount(),0);
        auto body=accessible->child(row(search,"pine-only.txt"));QVERIFY(body);
        QVERIFY(selection->select(body));QCOMPARE(selection->selectedItemCount(),1);
        QCOMPARE(selection->selectedItem(0)->text(QAccessible::Name),QString("pine-only.txt"));
        QVERIFY(browser->canAccept());
        auto filename=accessible->child(row(search,token+"-name.txt"));QVERIFY(filename);
        QVERIFY(selection->select(filename));QCOMPARE(selection->selectedItemCount(),2);
        auto image=accessible->child(row(search,token+"-image.png"));QVERIFY(image);
        QVERIFY(!selection->select(image));QCOMPARE(selection->selectedItemCount(),2);
        QVERIFY(selection->unselect(filename));QCOMPARE(selection->selectedItemCount(),1);
        QVERIFY(selection->clear());QCOMPARE(selection->selectedItemCount(),0);QVERIFY(!browser->canAccept());
        rows->setProperty("cacheBuffer",0);rows->setHeight(1);QTest::qWait(50);
        auto peer=accessible->child(row(search,"pine-peer.txt"));QVERIFY(peer);
        QCOMPARE(peer->text(QAccessible::Name),QString("pine-peer.txt"));
        QVERIFY(peer->state().offscreen);QVERIFY(selection->select(peer));
        QCOMPARE(selection->selectedItemCount(),1);QCOMPARE(selection->selectedItem(0)->text(QAccessible::Name),QString("pine-peer.txt"));
        setRaw(search,"no-matching-controlled-result");QTRY_VERIFY(!search->busy());
        QCOMPARE(accessible->childCount(),0);QCOMPARE(selection->selectedItemCount(),0);QVERIFY(results(view.rootObject()).isEmpty());browser->cancel();
    }
    void assistiveEditingUsesTheNormalQueryAndUndo(){
        QQuickView view;QVERIFY(load(view));auto browser=open(view);QVERIFY(browser);
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);click(editor);
        auto accessible=QAccessible::queryAccessibleInterface(editor);QVERIFY(accessible);
        auto editable=accessible->editableTextInterface();QVERIFY2(editable,"Assistive clients must be able to edit the search query");
        auto text=accessible->textInterface();QVERIFY(text);
        editable->replaceText(0,text->characterCount(),token);
        auto search=browser->search();QTRY_COMPARE(singleTermText(search),token);
        QTRY_VERIFY_WITH_TIMEOUT(!search->busy()&&row(search,"pine-only.txt")>=0,15000);
        editable->replaceText(0,text->characterCount(),token+"x");QTRY_COMPARE(singleTermText(search),token+"x");
        // Qt may group consecutive input-method replacements. Preserve that
        // grouping and require the exact redo round trip through the query.
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
        QTRY_COMPARE(singleTermText(search),editor->property("text").toString());QVERIFY(singleTermText(search)!=token+"x");
        QTRY_VERIFY(editor->hasActiveFocus());
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier|Qt::ShiftModifier);QTRY_COMPARE(singleTermText(search),token+"x");
        editor->setProperty("readOnly",true);editable->replaceText(0,text->characterCount(),"blocked");QCOMPARE(singleTermText(search),token+"x");
        editor->setProperty("readOnly",false);editable->deleteText(0,text->characterCount());QTRY_VERIFY(!search->active());
        QVERIFY(results(view.rootObject()).isEmpty());browser->cancel();
    }
    void committedTokensDoNotUndoEarlierLiteralEdits_data(){
        QTest::addColumn<QString>("mode");
        QTest::newRow("Filename")<<QStringLiteral("filename");
        QTest::newRow("Everything")<<QStringLiteral("everything");
    }
    void committedTokensDoNotUndoEarlierLiteralEdits(){
        QFETCH(QString,mode);
        QQuickView view;QVERIFY(load(view));auto browser=open(view);QVERIFY(browser);
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);click(editor);
        QTRY_VERIFY(editor->hasActiveFocus());type(editor->window(),token);
        auto search=browser->search();QTRY_COMPARE(singleTermText(search),token);
        QVERIFY(editor->property("canUndo").toBool());
        QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Return);
        QTRY_COMPARE(singleTermMode(search),"filename");
        if(mode=="everything"){
            auto tokenAccessible=QAccessible::queryAccessibleInterface(visible("bleeckerFileChooserSearchToken"));
            QVERIFY(tokenAccessible&&tokenAccessible->actionInterface());
            tokenAccessible->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
            QTRY_VERIFY(visible("bleeckerFileChooserSearchMode_everything"));
            auto choice=QAccessible::queryAccessibleInterface(visible("bleeckerFileChooserSearchMode_everything"));
            QVERIFY(choice&&choice->actionInterface());choice->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
            QTRY_COMPARE(singleTermMode(search),mode);
            editor->window()->requestActivate();
            QVERIFY(QTest::qWaitForWindowActive(editor->window()));
            auto host=visible("bleeckerFileChooserSearchHost");QVERIFY(host);QTest::mouseClick(editor->window(),Qt::LeftButton,{},host->mapToScene(QPointF(1,host->height()/2)).toPoint());
            QTRY_VERIFY(editor->hasActiveFocus());
        }
        QCOMPARE(singleTermText(search),token);
        QVERIFY2(!editor->property("canUndo").toBool(),"Committing a native search token makes earlier literal edits unavailable to Undo");
        QVERIFY(!editor->property("canRedo").toBool());
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
        QCOMPARE(singleTermText(search),token);QCOMPARE(singleTermMode(search),mode);
        browser->cancel();
    }
    void wholeTokenReplacementAndUndo(){
        QQuickView view;QVERIFY(load(view));auto browser=open(view);QVERIFY(browser);
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);click(editor);
        const auto previous=token+"-name";type(editor->window(),previous);
        QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Return);
        auto search=browser->search();QTRY_COMPARE(singleTermMode(search),"filename");
        QTest::keyClick(editor->window(),Qt::Key_A,Qt::ControlModifier);type(editor->window(),token);
        QTRY_COMPARE(singleTermText(search),token);QTRY_COMPARE(singleTermMode(search),"general");
        QVERIFY(!visible("bleeckerFileChooserSearchToken"));QVERIFY(visible("bleeckerFileChooserSearchSuggestion_0"));
        QVERIFY(visible("bleeckerFileChooserSearchSuggestion_1"));
        // Qt owns grouping; a replacement can have separate insertion/removal
        // undo steps. The recovered token must retain its original mode.
        for(int i=0;i<6&&singleTermText(search)!=previous;++i)QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
        QTRY_COMPARE(singleTermText(search),previous);QCOMPARE(singleTermMode(search),"filename");
        for(int i=0;i<6&&singleTermText(search)!=token;++i)QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier|Qt::ShiftModifier);
        QTRY_COMPARE(singleTermText(search),token);QCOMPARE(singleTermMode(search),"general");
        browser->cancel();
    }
    void assistiveTokenReplacementUndoAndReadOnly(){
        QQuickView view;QVERIFY(load(view));auto browser=open(view);QVERIFY(browser);
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);click(editor);
        const auto previous=token+"-name";type(editor->window(),previous);
        auto search=browser->search();QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Return);QTRY_COMPARE(editor->property("expression").toList(),committed("everything",previous));
        auto accessible=QAccessible::queryAccessibleInterface(editor);QVERIFY(accessible&&accessible->editableTextInterface()&&accessible->textInterface());
        auto editable=accessible->editableTextInterface();auto text=accessible->textInterface();
        editor->setProperty("readOnly",true);editable->replaceText(0,text->characterCount(),token);
        QCOMPARE(singleTermText(search),previous);QCOMPARE(singleTermMode(search),"everything");
        editor->setProperty("readOnly",false);editable->replaceText(0,text->characterCount(),token);
        QTRY_COMPARE(singleTermText(search),token);QCOMPARE(singleTermMode(search),"general");
        for(int i=0;i<6&&singleTermText(search)!=previous;++i)QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
        QTRY_COMPARE(singleTermText(search),previous);QCOMPARE(singleTermMode(search),"everything");
        editable->replaceText(0,text->characterCount(),previous);
        QCOMPARE(singleTermText(search),previous);QCOMPARE(singleTermMode(search),"general");
        for(int i=0;i<6&&singleTermMode(search)!="everything";++i)QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
        QCOMPARE(singleTermText(search),previous);QCOMPARE(singleTermMode(search),"everything");
        QTest::keyClick(editor->window(),Qt::Key_A,Qt::ControlModifier);QTest::keyClick(editor->window(),Qt::Key_Left);
        QCOMPARE(singleTermMode(search),"everything");
        QTest::keyClick(editor->window(),Qt::Key_A,Qt::ControlModifier);type(editor->window(),token+"-branch");
        QTRY_COMPARE(singleTermMode(search),"general");QVERIFY(!editor->property("canRedo").toBool());
        search->setExpression(committed("filename","external-query"));QTRY_COMPARE(editor->property("text").toString(),QString(QChar::ObjectReplacementCharacter));
        QVERIFY(!editor->property("canUndo").toBool());QCOMPARE(singleTermMode(search),"filename");
        browser->cancel();
    }
    void atomicTokensAndCompoundIndexedResults(){
        QQuickView view;QVERIFY(load(view));auto browser=open(view);QVERIFY(browser);
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);click(editor);type(editor->window(),token);
        click(visible("bleeckerFileChooserSearchFolder"));click(editor);
        QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Return);
        const QString object(QChar::ObjectReplacementCharacter);
        QCOMPARE(editor->property("text").toString(),object);
        QTest::keyClick(editor->window(),Qt::Key_Backspace);
        QCOMPARE(editor->property("selectedText").toString(),object);QVERIFY(browser->search()->active());
        QTest::keyClick(editor->window(),Qt::Key_Right);type(editor->window(),"pine");
        QCOMPARE(editor->property("text").toString(),object+"pine");
        QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Return);
        QCOMPARE(editor->property("text").toString(),object+object);
        const QVariantList compound{QVariantMap{{"kind","token"},{"mode","everything"},{"query",token}},QVariantMap{{"kind","token"},{"mode","filename"},{"query","pine"}}};
        auto search=browser->search();QTRY_COMPARE(search->property("expression").toList(),compound);
        QTRY_VERIFY2_WITH_TIMEOUT(!search->busy()&&search->count()==1&&row(search,"pine-only.txt")==0,qPrintable(indexState(search)),15000);
        auto second=visible("bleeckerFileChooserSearchToken_1");QVERIFY(second);
        auto accessible=QAccessible::queryAccessibleInterface(second);QVERIFY(accessible&&accessible->actionInterface());
        QCOMPARE(accessible->text(QAccessible::Name),QString("Filename: pine"));accessible->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
        QTRY_VERIFY(visible("bleeckerFileChooserSearchMode_everything_1"));
        auto everything=QAccessible::queryAccessibleInterface(visible("bleeckerFileChooserSearchMode_everything_1"));QVERIFY(everything&&everything->actionInterface());
        everything->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
        auto both=compound;auto last=both[1].toMap();last["mode"]="everything";both[1]=last;
        QTRY_COMPARE(search->property("expression").toList(),both);
        QTRY_VERIFY(!search->busy()&&search->count()==1&&row(search,"pine-only.txt")==0);
        search->select(0);QVERIFY(browser->canAccept());browser->acceptSelection();
        QTRY_COMPARE(results(view.rootObject()).size(),1);
        QCOMPARE(results(view.rootObject())[0].toMap()["urls"].toList(),QVariantList{QUrl::fromLocalFile(m_root+"/pine-only.txt")});
        QVERIFY(view.rootObject()->property("visibleAtCallback").toBool());
    }
    void tokenCaptionsKeepFullAccessibleNames_data(){
        QTest::addColumn<bool>("dark");QTest::newRow("light")<<false;QTest::newRow("dark")<<true;
    }
    void tokenCaptionsKeepFullAccessibleNames(){
        QFETCH(bool,dark);QQuickView view;QVERIFY(load(view));
        auto theme=view.engine()->singletonInstance<QObject*>("Avelino","BleeckerTheme");QVERIFY(theme);
        const auto previous=theme->property("dark");const auto restore=qScopeGuard([theme,previous]{theme->setProperty("dark",previous);});
        theme->setProperty("dark",dark);auto browser=open(view);QVERIFY(browser);
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);click(editor);
        browser->search()->setExpression(committed("filename","pine"));
        auto chip=visible("bleeckerFileChooserSearchToken");QVERIFY(chip);
        auto caption=chip->property("contentItem").value<QQuickItem*>();QVERIFY(caption);
        // The native visual caption is a separate compact mode and query;
        // its menu still exposes the complete accessibility name.
        QCOMPARE(caption->property("text").toString(),QString("pine"));
        auto mode=find(chip,"bleeckerFileChooserSearchTokenMode");QVERIFY(mode);
        QCOMPARE(mode->property("text").toString(),QString("NAME"));
        auto accessible=QAccessible::queryAccessibleInterface(chip);QVERIFY(accessible&&accessible->actionInterface());
        QCOMPARE(accessible->text(QAccessible::Name),QString("Filename: pine"));
        auto glyph=visible("bleeckerFileChooserSearchGlyph");QVERIFY(glyph);
        auto viewport=visible("bleeckerFileChooserSearchViewport");QVERIFY(viewport);
        QVERIFY(viewport->x()>=glyph->x()+glyph->width());
        const auto glyphPosition=glyph->position(),viewportPosition=viewport->position();
        const auto identity=accessible->object();
        accessible->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
        auto option=visible("bleeckerFileChooserSearchMode_everything");QVERIFY(option);click(option);
        QTRY_COMPARE(mode->property("text").toString(),QString("ANY"));
        QCOMPARE(QAccessible::queryAccessibleInterface(chip)->object(),identity);
        QCOMPARE(accessible->text(QAccessible::Name),QString("Everything: pine"));
        QCOMPARE(caption->property("text").toString(),QString("pine"));
        QVERIFY(editor->property("contentWidth").toDouble()<=viewport->width());
        QCOMPARE(viewport->property("contentX").toDouble(),0.0);
        // Compact toolbars have a wider search field. Use a query that really
        // overflows either layout, and prove that precondition before scrolling.
        const auto overflowQuery=token.repeated(8);
        const QVariantList compound{QVariantMap{{"kind","token"},{"mode","everything"},{"query",overflowQuery}},QVariantMap{{"kind","token"},{"mode","filename"},{"query","pine"}}};
        browser->search()->setExpression(compound);
        qInfo().noquote()<<"TOKEN_PRESENTATION_VIEWPORT"<<QJsonDocument(QJsonObject{
            {"dpr",editor->window()->devicePixelRatio()},
            {"hostWidth",visible("bleeckerFileChooserSearchHost")->width()},
            {"viewportWidth",viewport->width()},{"contentWidth",editor->property("contentWidth").toDouble()},
            {"contentX",viewport->property("contentX").toDouble()}}).toJson(QJsonDocument::Compact);
        QVERIFY(editor->property("contentWidth").toDouble()>viewport->width());
        QTRY_VERIFY(viewport->property("contentX").toDouble()>0);
        chip=visible("bleeckerFileChooserSearchToken");QVERIFY(chip);
        caption=chip->property("contentItem").value<QQuickItem*>();QVERIFY(caption);
        QCOMPARE(glyph->position(),glyphPosition);QVERIFY(glyph->isVisible());
        QCOMPARE(viewport->position(),viewportPosition);
        auto second=visible("bleeckerFileChooserSearchToken_1");QVERIFY(second);
        QVERIFY(second->x()>chip->x()+chip->width());
        QCOMPARE(caption->property("text").toString(),overflowQuery);
        QTest::keyClick(editor->window(),Qt::Key_Home);
        QTRY_COMPARE(viewport->property("contentX").toDouble(),0.0);
        QVERIFY(glyph->isVisible());
        capture(editor,dark?"token-cells-leading-dark":"token-cells-leading-light");
        QTest::keyClick(editor->window(),Qt::Key_End);
        QTRY_VERIFY(viewport->property("contentX").toDouble()>0);
        capture(editor,dark?"token-cells-trailing-dark":"token-cells-trailing-light");
        browser->search()->clear();
        QCOMPARE(editor->property("placeholderText").toString(),QString("Search"));
        QVERIFY(glyph->isVisible());QCOMPARE(viewport->position(),viewportPosition);
        browser->cancel();QVERIFY(results(view.rootObject()).isEmpty());
    }
    void queryPointerSelectionAndExpansion_data(){
        QTest::addColumn<bool>("dark");QTest::newRow("light")<<false;QTest::newRow("dark")<<true;
    }
    void queryPointerSelectionAndExpansion(){
        QFETCH(bool,dark);QQuickView view;QVERIFY(load(view));
        auto theme=view.engine()->singletonInstance<QObject*>("Avelino","BleeckerTheme");QVERIFY(theme);
        const auto previous=theme->property("dark");const auto restore=qScopeGuard([theme,previous]{theme->setProperty("dark",previous);});
        theme->setProperty("dark",dark);auto browser=open(view);QVERIFY(browser);
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);
        browser->search()->setExpression(committed("filename","pine"));
        auto chip=visible("bleeckerFileChooserSearchToken");QVERIFY(chip);
        auto caption=chip->property("contentItem").value<QQuickItem*>();QVERIFY(caption);
        const auto queryLeft=caption->property("leftPadding").toDouble();
        QVERIFY(queryLeft>0&&queryLeft<chip->width());
        const auto queryPoint=chip->mapToScene(QPointF((queryLeft+chip->width()-4)/2,chip->height()/2)).toPoint();
        QTest::mouseClick(editor->window(),Qt::LeftButton,{},queryPoint);
        capture(editor,dark?"token-query-click-dark":"token-query-click-light");
        QCOMPARE(editor->property("selectedText").toString(),QString(QChar::ObjectReplacementCharacter));
        QVERIFY(!visible("bleeckerFileChooserSearchMode_filename"));
        const auto modePoint=chip->mapToScene(QPointF(queryLeft/2,chip->height()/2)).toPoint();
        QTest::mouseClick(editor->window(),Qt::LeftButton,{},modePoint);
        auto mode=visible("bleeckerFileChooserSearchMode_filename");QVERIFY(mode);click(mode);
        QTest::mouseDClick(editor->window(),Qt::LeftButton,{},queryPoint);
        QCOMPARE(editor->property("text").toString(),QString("pine"));
        QCOMPARE(editor->property("selectedText").toString(),QString("pine"));
        QCOMPARE(browser->search()->expression(),raw("pine"));
        QVERIFY(!visible("bleeckerFileChooserSearchToken"));
        capture(editor,dark?"token-query-expanded-dark":"token-query-expanded-light");
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
        QCOMPARE(browser->search()->expression(),committed("filename","pine"));
        QCOMPARE(editor->property("selectedText").toString(),QString(QChar::ObjectReplacementCharacter));
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier|Qt::ShiftModifier);
        QCOMPARE(editor->property("text").toString(),QString("pine"));
        QCOMPARE(editor->property("selectedText").toString(),QString());
        QCOMPARE(editor->property("cursorPosition").toInt(),4);
        browser->cancel();QVERIFY(results(view.rootObject()).isEmpty());
    }
    void tokenExpansionPreservesNativeBoundariesAndUndo_data(){
        QTest::addColumn<QVariantList>("original");QTest::addColumn<int>("position");
        QTest::addColumn<QVariantList>("expanded");QTest::addColumn<QString>("expandedText");
        QTest::addColumn<int>("selectedStart");QTest::addColumn<int>("redoCursor");
        const QVariantMap filename{{"kind","token"},{"mode","filename"},{"query","pine"}};
        const QVariantMap everything{{"kind","token"},{"mode","everything"},{"query","pine"}};
        const auto text=[](const QString &value){return QVariantMap{{"kind","text"},{"text",value}};};
        const QString object(QChar::ObjectReplacementCharacter);
        QTest::newRow("filename")<<QVariantList{filename}<<0<<raw("pine")<<QString("pine")<<0<<4;
        QTest::newRow("everything")<<QVariantList{everything}<<0<<raw("pine")<<QString("pine")<<0<<4;
        QTest::newRow("token-before")<<QVariantList{filename,everything}<<1<<QVariantList{filename,text("pine")}<<(object+"pine")<<1<<-1;
        QTest::newRow("token-after")<<QVariantList{filename,everything}<<0<<QVariantList{text("pine"),everything}<<(QString("pine")+object)<<0<<4;
        QTest::newRow("raw-before")<<QVariantList{text("pine"),everything}<<4<<raw("pine pine")<<QString("pine pine")<<5<<-1;
        QTest::newRow("raw-after")<<QVariantList{filename,text("cedar")}<<0<<raw("pine cedar")<<QString("pine cedar")<<0<<5;
        QTest::newRow("space-before")<<QVariantList{text("oak "),filename}<<4<<raw("oak  pine")<<QString("oak  pine")<<5<<5;
        QTest::newRow("spaces-both")<<QVariantList{text("oak "),filename,text(" cedar")}<<4<<raw("oak  pine  cedar")<<QString("oak  pine  cedar")<<5<<10;
    }
    void tokenExpansionPreservesNativeBoundariesAndUndo(){
        QFETCH(QVariantList,original);QFETCH(int,position);QFETCH(QVariantList,expanded);
        QFETCH(QString,expandedText);QFETCH(int,selectedStart);QFETCH(int,redoCursor);
        QQuickView view;QVERIFY(load(view));auto browser=open(view);QVERIFY(browser);
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);
        browser->search()->setExpression(original);
        QTRY_COMPARE(editor->property("expression").toList(),original);
        const QByteArray caseName(QTest::currentDataTag());QPointer<QQuickItem> neighbor;
        QAccessibleInterface *neighborAccessible=nullptr;
        if(caseName=="token-before"||caseName=="token-after"){
            neighbor=visible(caseName=="token-before"?"bleeckerFileChooserSearchToken":"bleeckerFileChooserSearchToken_1");
            QVERIFY(neighbor);neighborAccessible=QAccessible::queryAccessibleInterface(neighbor);QVERIFY(neighborAccessible);
        }
        QVERIFY(!editor->property("canUndo").toBool());
        QSignalSpy changed(editor,SIGNAL(expressionChanged()));
        QVERIFY(QMetaObject::invokeMethod(editor,"editTokenAt",Q_ARG(int,position)));
        QCOMPARE(editor->property("text").toString(),expandedText);
        QCOMPARE(browser->search()->expression(),expanded);
        QCOMPARE(editor->property("selectedText").toString(),QString("pine"));
        QCOMPARE(editor->property("selectionStart").toInt(),selectedStart);
        QCOMPARE(editor->property("selectionEnd").toInt(),selectedStart+4);
        QCOMPARE(changed.size(),1);QVERIFY(editor->property("canUndo").toBool());
        if(neighborAccessible){QVERIFY(neighbor);QCOMPARE(QAccessible::queryAccessibleInterface(neighbor),neighborAccessible);}
        capture(editor,"token-expanded-"+QString::fromLatin1(QTest::currentDataTag()));
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
        const bool rawBoth=caseName=="spaces-both";
        QCOMPARE(browser->search()->expression(),rawBoth?raw("oak pine cedar"):original);
        QCOMPARE(editor->property("selectedText").toString(),rawBoth?QString():QString(QChar::ObjectReplacementCharacter));
        if(!rawBoth)QCOMPARE(editor->property("selectionStart").toInt(),position);
        QVERIFY(!editor->property("canUndo").toBool());
        if(neighborAccessible){QVERIFY(neighbor);QCOMPARE(QAccessible::queryAccessibleInterface(neighbor),neighborAccessible);}
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier|Qt::ShiftModifier);
        QCOMPARE(browser->search()->expression(),expanded);
        QCOMPARE(editor->property("selectedText").toString(),QString());
        if(redoCursor>=0)QCOMPARE(editor->property("cursorPosition").toInt(),redoCursor);
        if(neighborAccessible){QVERIFY(neighbor);QCOMPARE(QAccessible::queryAccessibleInterface(neighbor),neighborAccessible);}
        if(caseName=="raw-after"){
            type(editor->window(),"X");
            QCOMPARE(editor->property("text").toString(),QString("pine Xcedar"));
        }
        browser->cancel();QVERIFY(results(view.rootObject()).isEmpty());
    }
    void rawBoundaryExpansionMatchesNativeTypingHistory(){
        QQuickView view;QVERIFY(load(view));auto browser=open(view);QVERIFY(browser);
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);click(editor);
        type(editor->window(),"pine");QTest::keyClick(editor->window(),Qt::Key_Down);
        QTest::keyClick(editor->window(),Qt::Key_Return);
        QTRY_COMPARE(browser->search()->expression(),committed("filename","pine"));
        QTest::keyClick(editor->window(),Qt::Key_Home);type(editor->window(),"oak ");
        QTest::keyClick(editor->window(),Qt::Key_End);type(editor->window()," cedar");
        QCOMPARE(editor->property("text").toString(),QString("oak ")+QChar::ObjectReplacementCharacter+" cedar");
        QVERIFY(editor->property("canUndo").toBool());
        auto query=visible("bleeckerFileChooserSearchTokenQuery");QVERIFY(query);
        capture(editor,"native-raw-boundary-before");
        QTest::mouseDClick(editor->window(),Qt::LeftButton,{},query->mapToScene(query->boundingRect().center()).toPoint());
        QCOMPARE(editor->property("text").toString(),QString("oak  pine  cedar"));
        QCOMPARE(editor->property("selectedText").toString(),QString("pine"));
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
        // A fresh pinned native process leaves raw text at the first Undo when
        // raw runs border both sides; it retains the earlier typing history.
        QCOMPARE(editor->property("text").toString(),QString("oak pine cedar"));
        QCOMPARE(browser->search()->expression(),raw("oak pine cedar"));
        QCOMPARE(editor->property("selectedText").toString(),QString());
        QVERIFY(editor->property("canUndo").toBool());
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier|Qt::ShiftModifier);
        QCOMPARE(editor->property("text").toString(),QString("oak  pine  cedar"));
        QCOMPARE(editor->property("cursorPosition").toInt(),10);
        type(editor->window(),"X");
        QCOMPARE(editor->property("text").toString(),QString("oak  pine X cedar"));
        for(const auto &text:QStringList{"oak  pine  cedar","oak pine cedar","oak pdar"}){
            QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
            QCOMPARE(editor->property("text").toString(),text);
        }
        for(const auto &text:QStringList{"oak pine cedar","oak  pine  cedar","oak  pine X cedar"}){
            QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier|Qt::ShiftModifier);
            QCOMPARE(editor->property("text").toString(),text);
        }
        // Revisit the commands created during Redo, then branch with new input.
        // This is a history integrity guard, beyond the recorded native trace.
        for(const auto &text:QStringList{"oak  pine  cedar","oak pine cedar","oak pdar"}){
            QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
            QCOMPARE(editor->property("text").toString(),text);
        }
        for(const auto &text:QStringList{"oak pine cedar","oak  pine  cedar","oak  pine X cedar"}){
            QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier|Qt::ShiftModifier);
            QCOMPARE(editor->property("text").toString(),text);
        }
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
        QTest::keyClick(editor->window(),Qt::Key_End);type(editor->window(),"Y");
        QCOMPARE(editor->property("text").toString(),QString("oak  pine  cedarY"));
        QVERIFY(!editor->property("canRedo").toBool());
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
        QCOMPARE(editor->property("text").toString(),QString("oak  pine  cedar"));
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier|Qt::ShiftModifier);
        QCOMPARE(editor->property("text").toString(),QString("oak  pine  cedarY"));
        capture(editor,"native-raw-boundary-history-redo");
        browser->cancel();QVERIFY(results(view.rootObject()).isEmpty());
    }
    void prefixExpansionRedoUsesNativeCaret(){
        QQuickView view;QVERIFY(load(view));auto browser=open(view);QVERIFY(browser);
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);click(editor);
        type(editor->window(),"pine");QTest::keyClick(editor->window(),Qt::Key_Down);
        QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Return);
        QTRY_COMPARE(browser->search()->expression(),committed("everything","pine"));
        QTest::keyClick(editor->window(),Qt::Key_Home);type(editor->window(),"oak ");
        auto query=visible("bleeckerFileChooserSearchTokenQuery");QVERIFY(query);
        QTest::mouseDClick(editor->window(),Qt::LeftButton,{},query->mapToScene(query->boundingRect().center()).toPoint());
        QCOMPARE(editor->property("text").toString(),QString("oak  pine"));
        QCOMPARE(editor->property("selectedText").toString(),QString("pine"));
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
        QCOMPARE(editor->property("text").toString(),QString("oak ")+QChar::ObjectReplacementCharacter);
        QCOMPARE(editor->property("selectedText").toString(),QString(QChar::ObjectReplacementCharacter));
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier|Qt::ShiftModifier);
        QCOMPARE(editor->property("text").toString(),QString("oak  pine"));
        QCOMPARE(editor->property("selectedText").toString(),QString());
        QCOMPARE(editor->property("cursorPosition").toInt(),5);
        type(editor->window(),"X");QCOMPARE(editor->property("text").toString(),QString("oak  Xpine"));
        capture(editor,"native-prefix-redo-caret");browser->cancel();
    }
    void committedUnicodeQueryExpansion_data(){
        QTest::addColumn<QString>("query");
        QTest::newRow("combining")<<QStringLiteral("avelinoe\u0301");
        QTest::newRow("supplementary")<<QStringLiteral("avelino\U0001f426");
    }
    void committedUnicodeQueryExpansion(){
        QFETCH(QString,query);QQuickView view;QVERIFY(load(view));auto browser=open(view);QVERIFY(browser);
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);click(editor);
        QInputMethodEvent commit;commit.setCommitString(query);QCoreApplication::sendEvent(editor,&commit);
        QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Return);
        QTRY_COMPARE(browser->search()->expression(),committed("filename",query));
        auto hit=visible("bleeckerFileChooserSearchTokenQuery");QVERIFY(hit);
        QTest::mouseDClick(editor->window(),Qt::LeftButton,{},hit->mapToScene(hit->boundingRect().center()).toPoint());
        QCOMPARE(editor->property("text").toString(),query);
        QCOMPARE(editor->property("selectedText").toString(),query);
        QCOMPARE(editor->property("selectionStart").toInt(),0);
        QCOMPARE(editor->property("selectionEnd").toInt(),query.size());
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
        QCOMPARE(browser->search()->expression(),committed("filename",query));
        QCOMPARE(editor->property("selectedText").toString(),QString(QChar::ObjectReplacementCharacter));
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier|Qt::ShiftModifier);
        QCOMPARE(editor->property("text").toString(),query);
        QCOMPARE(editor->property("selectedText").toString(),QString());
        QCOMPARE(editor->property("cursorPosition").toInt(),query.size());
        type(editor->window(),"X");QCOMPARE(editor->property("text").toString(),query+"X");
        capture(editor,"native-unicode-"+QString::fromLatin1(QTest::currentDataTag()));browser->cancel();
    }
    void rawBoundaryHistoryKeepsTheOtherTokenObject(){
        QQuickView view;QVERIFY(load(view));auto browser=open(view);QVERIFY(browser);
        const QVariantMap peer{{"kind","token"},{"mode","everything"},{"query",token}};
        const QVariantList original{peer,QVariantMap{{"kind","text"},{"text","oak "}},
            committed("filename","pine").first(),QVariantMap{{"kind","text"},{"text"," cedar"}}};
        browser->search()->setExpression(original);
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);
        QPointer<QQuickItem> other=visible("bleeckerFileChooserSearchToken");QVERIFY(other);
        auto accessible=QAccessible::queryAccessibleInterface(other);QVERIFY(accessible);
        QVERIFY(QMetaObject::invokeMethod(editor,"editTokenAt",Q_ARG(int,5)));
        const auto checkPeer=[&]{
            QVERIFY(other);QCOMPARE(visible("bleeckerFileChooserSearchToken"),other.data());
            QCOMPARE(QAccessible::queryAccessibleInterface(other),accessible);
            QCOMPARE(browser->search()->expression().first().toMap(),peer);
        };
        checkPeer();QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);checkPeer();
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier|Qt::ShiftModifier);checkPeer();
        browser->cancel();
    }
    void rawBoundaryHistoryNotificationsAllowSynchronousDestruction_data(){
        QTest::addColumn<QString>("phase");QTest::addColumn<QByteArray>("notification");
        for(const auto &phase:QStringList{"expand","undo","redo"}){
            for(const auto &notification:QList<QByteArray>{"textChanged()","selectedTextChanged()","canUndoChanged()","expressionChanged()"}){
                if(phase=="redo"&&notification=="selectedTextChanged()")continue;
                QTest::newRow((phase+"-"+QString::fromLatin1(notification)).toLatin1().constData())<<phase<<notification;
            }
        }
    }
    void rawBoundaryHistoryNotificationsAllowSynchronousDestruction(){
        QFETCH(QString,phase);QFETCH(QByteArray,notification);
        QQmlEngine engine;engine.addImportPath(AVELINO_FILE_INPUT_IMPORT_PATH);QQmlComponent component(&engine);
        component.setData("import QtQuick\nimport Avelino\nFileChooserSearchText {}",QUrl());
        QPointer<QObject> editor=component.create();QVERIFY2(editor,qPrintable(component.errorString()));
        const QVariantList original{QVariantMap{{"kind","text"},{"text","oak "}},
            committed("filename","pine").first(),QVariantMap{{"kind","text"},{"text"," cedar"}}};
        QVERIFY(editor->setProperty("expression",original));
        if(phase!="expand")QVERIFY(QMetaObject::invokeMethod(editor,"editTokenAt",Q_ARG(int,4)));
        if(phase=="redo")QVERIFY(QMetaObject::invokeMethod(editor,"undo"));
        SearchEditorDestroyer destroyer;destroyer.target=editor;QSignalSpy destroyed(editor,&QObject::destroyed);
        const int index=editor->metaObject()->indexOfSignal(notification);QVERIFY(index>=0);
        const auto signal=editor->metaObject()->method(index);
        const auto slot=destroyer.metaObject()->method(destroyer.metaObject()->indexOfSlot("destroy()"));
        QVERIFY(QObject::connect(editor,signal,&destroyer,slot,Qt::DirectConnection));
        if(phase=="expand")QVERIFY(QMetaObject::invokeMethod(editor,"editTokenAt",Q_ARG(int,4)));
        else QVERIFY(QMetaObject::invokeMethod(editor,phase.toLatin1().constData()));
        QVERIFY(!editor);QCOMPARE(destroyed.size(),1);
    }
    void tokenExpansionReadOnlyDisabledAndExternalReset(){
        QQuickView view;QVERIFY(load(view));auto browser=open(view);QVERIFY(browser);
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);
        const auto original=committed("everything","pine");browser->search()->setExpression(original);
        editor->setProperty("readOnly",true);
        QVERIFY(QMetaObject::invokeMethod(editor,"editTokenAt",Q_ARG(int,0)));
        QCOMPARE(browser->search()->expression(),original);QVERIFY(!editor->property("canUndo").toBool());
        editor->setProperty("readOnly",false);editor->setEnabled(false);
        QVERIFY(QMetaObject::invokeMethod(editor,"selectTokenAt",Q_ARG(int,0)));
        QVERIFY(QMetaObject::invokeMethod(editor,"editTokenAt",Q_ARG(int,0)));
        QCOMPARE(browser->search()->expression(),original);QCOMPARE(editor->property("selectedText").toString(),QString());
        editor->setEnabled(true);QVERIFY(QMetaObject::invokeMethod(editor,"editTokenAt",Q_ARG(int,0)));
        QCOMPARE(browser->search()->expression(),raw("pine"));
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
        QCOMPARE(browser->search()->expression(),original);
        browser->search()->setExpression(raw("external-query"));
        QTRY_COMPARE(editor->property("text").toString(),QString("external-query"));
        QVERIFY(!editor->property("canUndo").toBool());QVERIFY(!editor->property("canRedo").toBool());
        type(editor->window(),"x");QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
        QCOMPARE(editor->property("text").toString(),QString("external-query"));
        QCOMPARE(editor->property("selectedText").toString(),QString());browser->cancel();
    }
    void tokenPointerFocusCannotTargetAReplacementToken(){
        QQmlEngine engine;engine.addImportPath(AVELINO_FILE_INPUT_IMPORT_PATH);QQmlComponent component(&engine);
        component.setData("import QtQuick\nimport Avelino\nFileChooserSearchText {}",QUrl());
        QScopedPointer<QObject> editor(component.create());QVERIFY2(editor,qPrintable(component.errorString()));
        QVERIFY(editor->setProperty("expression",committed("filename","pine")));
        auto item=qobject_cast<QQuickItem*>(editor.data());QVERIFY(item);QVERIFY(!item->hasFocus());
        const auto replacement=committed("everything","external-query");
        auto connection=connect(item,&QQuickItem::focusChanged,&engine,[&]{editor->setProperty("expression",replacement);});
        QVERIFY(QMetaObject::invokeMethod(editor.data(),"selectTokenAt",Q_ARG(int,0)));
        QCOMPARE(editor->property("expression").toList(),replacement);
        QCOMPARE(editor->property("selectedText").toString(),QString());
        disconnect(connection);
    }
    void queryMenuCloseCannotSelectAReplacementToken(){
        QQuickView view;QVERIFY(load(view));auto browser=open(view);QVERIFY(browser);
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);
        browser->search()->setExpression(committed("filename","pine"));
        auto chip=visible("bleeckerFileChooserSearchToken");QVERIFY(chip);
        auto caption=chip->property("contentItem").value<QQuickItem*>();QVERIFY(caption);
        const auto queryLeft=caption->property("leftPadding").toDouble();
        const auto point=chip->mapToScene(QPointF((queryLeft+chip->width()-4)/2,chip->height()/2)).toPoint();
        auto accessible=QAccessible::queryAccessibleInterface(chip);QVERIFY(accessible&&accessible->actionInterface());
        accessible->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
        QTRY_VERIFY(visible("bleeckerFileChooserSearchMode_filename"));
        const auto replacement=committed("everything","external-query");bool replaced=false;
        auto connection=connect(editor,&QQuickItem::activeFocusChanged,&view,[&]{
            if(editor->hasActiveFocus()&&!replaced){replaced=true;browser->search()->setExpression(replacement);}
        });
        QTest::mouseClick(editor->window(),Qt::LeftButton,{},point);
        QTRY_VERIFY(replaced);QCOMPARE(browser->search()->expression(),replacement);
        QCOMPARE(editor->property("selectedText").toString(),QString());
        QVERIFY(!visible("bleeckerFileChooserSearchMode_filename"));
        disconnect(connection);browser->cancel();
    }
    void expansionNotificationsAllowSynchronousControlDestruction_data(){
        QTest::addColumn<QByteArray>("notification");
        QTest::newRow("text")<<QByteArray("textChanged()");
        QTest::newRow("selection")<<QByteArray("selectedTextChanged()");
        QTest::newRow("Undo")<<QByteArray("canUndoChanged()");
        QTest::newRow("expression")<<QByteArray("expressionChanged()");
    }
    void expansionNotificationsAllowSynchronousControlDestruction(){
        QFETCH(QByteArray,notification);QQmlEngine engine;engine.addImportPath(AVELINO_FILE_INPUT_IMPORT_PATH);
        QQmlComponent component(&engine);component.setData("import QtQuick\nimport Avelino\nFileChooserSearchText {}",QUrl());
        QPointer<QObject> editor=component.create();QVERIFY2(editor,qPrintable(component.errorString()));
        QVERIFY(editor->setProperty("expression",committed("filename","pine")));
        SearchEditorDestroyer destroyer;destroyer.target=editor;QSignalSpy destroyed(editor,&QObject::destroyed);
        const auto signal=editor->metaObject()->method(editor->metaObject()->indexOfSignal(notification));
        const auto slot=destroyer.metaObject()->method(destroyer.metaObject()->indexOfSlot("destroy()"));
        QVERIFY(QObject::connect(editor,signal,&destroyer,slot,Qt::DirectConnection));
        QVERIFY(QMetaObject::invokeMethod(editor,"editTokenAt",Q_ARG(int,0)));
        QVERIFY(!editor);QCOMPARE(destroyed.size(),1);
    }
    void atomicReplacementSelectionUndoAndHistory_data(){
        QTest::addColumn<bool>("dark");QTest::newRow("light")<<false;QTest::newRow("dark")<<true;
    }
    void atomicReplacementSelectionUndoAndHistory(){
        QFETCH(bool,dark);QQuickView view;QVERIFY(load(view));
        auto theme=view.engine()->singletonInstance<QObject*>("Avelino","BleeckerTheme");QVERIFY(theme);
        const auto previous=theme->property("dark");const auto restore=qScopeGuard([theme,previous]{theme->setProperty("dark",previous);});
        theme->setProperty("dark",dark);auto browser=open(view);QVERIFY(browser);
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);click(editor);type(editor->window(),token);
        QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Return);
        const QString object(QChar::ObjectReplacementCharacter);QCOMPARE(editor->property("text").toString(),object);
        type(editor->window(),"pine");QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Return);
        auto search=browser->search();const auto compound=search->property("expression").toList();QCOMPARE(compound.size(),2);
        QTest::keyClick(editor->window(),Qt::Key_Home);QTest::keyClick(editor->window(),Qt::Key_Right);
        QCOMPARE(editor->property("selectedText").toString(),object);type(editor->window(),"name");
        QCOMPARE(editor->property("text").toString(),"name"+object);
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
        QCOMPARE(editor->property("text").toString(),object+object);QCOMPARE(editor->property("selectedText").toString(),object);
        QCOMPARE(search->property("expression").toList(),compound);
        auto selectedToken=visible("bleeckerFileChooserSearchToken");QVERIFY(selectedToken);
        auto caption=selectedToken->property("contentItem").value<QQuickItem*>();QVERIFY(caption);
        QCOMPARE(caption->property("color").value<QColor>(),editor->property("selectedTextColor").value<QColor>());
        capture(editor,dark?"atomic-selected-dark":"atomic-selected-light");
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier|Qt::ShiftModifier);
        QCOMPARE(editor->property("text").toString(),"name"+object);
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
        click(visible("bleeckerFileChooserBack"));QTRY_VERIFY(!search->active());QVERIFY(browser->canGoForward());
        click(visible("bleeckerFileChooserForward"));QTRY_COMPARE(search->property("expression").toList(),compound);
        QCOMPARE(editor->property("text").toString(),object+object);QVERIFY(!editor->property("canUndo").toBool());
        browser->cancel();QVERIFY(results(view.rootObject()).isEmpty());
    }
    void atomicAssistiveCompositionAndExternalReset(){
        QQuickView view;QVERIFY(load(view));auto browser=open(view);QVERIFY(browser);
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);click(editor);type(editor->window(),token);
        QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Return);
        const QString object(QChar::ObjectReplacementCharacter);QCOMPARE(editor->property("text").toString(),object);
        type(editor->window(),"pine");QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Return);
        auto search=browser->search();const auto compound=search->property("expression").toList();QCOMPARE(compound.size(),2);
        auto accessible=QAccessible::queryAccessibleInterface(editor);QVERIFY(accessible&&accessible->editableTextInterface()&&accessible->textInterface());
        auto editable=accessible->editableTextInterface();editable->replaceText(0,1,"name");
        QCOMPARE(editor->property("text").toString(),"name"+object);
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
        QCOMPARE(search->property("expression").toList(),compound);QCOMPARE(editor->property("selectedText").toString(),object);
        editable->deleteText(0,1);QCOMPARE(editor->property("text").toString(),object);
        QCOMPARE(search->property("expression").toList(),QVariantList{compound[1]});
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
        QCOMPARE(search->property("expression").toList(),compound);QCOMPARE(editor->property("selectedText").toString(),object);
        QTest::keyClick(editor->window(),Qt::Key_Right);
        QInputMethodEvent preedit(QString::fromUtf8("かな"),{});QCoreApplication::sendEvent(editor,&preedit);
        QCOMPARE(search->property("expression").toList(),compound);
        QInputMethodEvent commit;commit.setCommitString(QString::fromUtf8("かな"));QCoreApplication::sendEvent(editor,&commit);
        QCOMPARE(editor->property("text").toString(),object+QString::fromUtf8("かな")+object);
        QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);QCOMPARE(search->property("expression").toList(),compound);
        const QVariantList external{QVariantMap{{"kind","text"},{"text","external-query"}}};
        QVERIFY(search->setProperty("expression",external));QTRY_COMPARE(editor->property("text").toString(),"external-query");
        QVERIFY(!editor->property("canUndo").toBool());QVERIFY(!editor->property("canRedo").toBool());
        type(editor->window(),"x");QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
        QCOMPARE(editor->property("text").toString(),"external-query");QCOMPARE(editor->property("selectedText").toString(),QString());
        browser->cancel();QVERIFY(results(view.rootObject()).isEmpty());
    }
    void adjacentRawSegmentsAreRejectedWithoutReplacingTheExpression(){
        FileChooserBrowser browser;QVERIFY(browser.open(QUrl::fromLocalFile(m_root)));auto search=browser.search();setRaw(search,token);
        const auto before=search->expression();QSignalSpy changed(search,&FileChooserSearch::changed);
        QTest::ignoreMessage(QtWarningMsg,"Adjacent raw search segments must be one text segment");
        search->setExpression({QVariantMap{{"kind","text"},{"text","a"}},QVariantMap{{"kind","text"},{"text","b"}}});
        QCOMPARE(search->expression(),before);QVERIFY(changed.isEmpty());browser.cancel();
    }
    void tokenNotificationsAllowSynchronousControlDestruction_data(){
        QTest::addColumn<QByteArray>("notification");
        QTest::newRow("Undo")<<QByteArray("canUndoChanged()");
        QTest::newRow("Redo")<<QByteArray("canRedoChanged()");
        QTest::newRow("Expression")<<QByteArray("expressionChanged()");
    }
    void tokenNotificationsAllowSynchronousControlDestruction(){
        QFETCH(QByteArray,notification);QQmlEngine engine;engine.addImportPath(AVELINO_FILE_INPUT_IMPORT_PATH);
        QQmlComponent component(&engine);component.setData("import QtQuick\nimport Avelino\nFileChooserSearchText {}",QUrl());
        QPointer<QObject> editor=component.create();QVERIFY2(editor,qPrintable(component.errorString()));
        QVERIFY(editor->setProperty("expression",raw(token)));
        if(notification!="expressionChanged()"){
            QVERIFY(QMetaObject::invokeMethod(editor,"insert",Q_ARG(int,token.size()),Q_ARG(QString,QStringLiteral("x"))));
            QVERIFY(editor->property("canUndo").toBool());
            if(notification=="canRedoChanged()"){
                QVERIFY(QMetaObject::invokeMethod(editor,"undo"));QVERIFY(editor->property("canRedo").toBool());
            }
        }
        SearchEditorDestroyer destroyer;destroyer.target=editor;QSignalSpy destroyed(editor,&QObject::destroyed);
        const auto signal=editor->metaObject()->method(editor->metaObject()->indexOfSignal(notification));
        const auto slot=destroyer.metaObject()->method(destroyer.metaObject()->indexOfSlot("destroy()"));
        QVERIFY(QObject::connect(editor,signal,&destroyer,slot,Qt::DirectConnection));
        QVERIFY(QMetaObject::invokeMethod(editor,"commitDraft",Q_ARG(QString,QStringLiteral("filename"))));
        QVERIFY(!editor);QCOMPARE(destroyed.size(),1);
    }
    void selectionCanSynchronouslyRemoveItsOwner(){
        for(const auto &operation:QStringList{"selection","press","activate"}){
            QQuickView view;QVERIFY(load(view));QPointer<FileChooserBrowser> browser=open(view);QVERIFY(browser);
            auto search=browser->search();setRaw(search,token);
            QTRY_VERIFY_WITH_TIMEOUT(!search->busy()&&row(search,"pine-only.txt")>=0,15000);
            const auto index=row(search,"pine-only.txt");
            QSignalSpy owner(browser,&FileChooserBrowser::result);
            // The fixture's Loader owns the QML control. Remove it through the
            // Loader rather than leaving its item pointer dangling with delete.
            connect(search,&QAbstractItemModel::dataChanged,&view,[&view]{view.rootObject()->setProperty("mounted",false);});
            if(operation=="selection"){
                auto resultsAccessible=QAccessible::queryAccessibleInterface(visible("bleeckerFileChooserSearchResults"));
                QVERIFY(resultsAccessible&&resultsAccessible->selectionInterface());
                auto child=resultsAccessible->child(index);QVERIFY(child);
                resultsAccessible->selectionInterface()->select(child);
            }else if(operation=="press"){
                auto item=visible("bleeckerFileChooserSearchRow_"+QString::number(index));QVERIFY(item);
                auto accessible=QAccessible::queryAccessibleInterface(item);QVERIFY(accessible&&accessible->actionInterface());
                accessible->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
            }else search->activate(index);
            QTRY_VERIFY(!browser);QVERIFY2(owner.isEmpty(),qPrintable(operation));QVERIFY(results(view.rootObject()).isEmpty());QTest::qWait(30);
        }
    }
    void coreSelectionCanSynchronouslyDestroyItsBrowser(){
        QPointer<FileChooserBrowser> browser=new FileChooserBrowser;
        browser->setAllowedContentTypes({"text/plain"});QVERIFY(browser->open(QUrl::fromLocalFile(m_root)));
        auto search=browser->search();setRaw(search,token);
        QTRY_VERIFY_WITH_TIMEOUT(!search->busy()&&row(search,"pine-only.txt")>=0,15000);
        const auto index=row(search,"pine-only.txt");QSignalSpy owner(browser,&FileChooserBrowser::result);
        connect(search,&QAbstractItemModel::dataChanged,this,[&browser]{delete browser.data();});
        search->activate(index);QVERIFY(!browser);QVERIFY(owner.isEmpty());QTest::qWait(30);
    }
    void escapeBackForwardAndNewQueryBranch(){
        QQuickView view;QVERIFY(load(view));auto browser=open(view);QVERIFY(browser);
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);click(editor);type(editor->window(),token);
        auto search=browser->search();QTRY_VERIFY_WITH_TIMEOUT(!search->busy()&&row(search,"pine-only.txt")>=0,15000);
        click(visible("bleeckerFileChooserSearchFolder"));click(editor);
        QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Return);
        QTRY_COMPARE(singleTermMode(search),"everything");QTRY_VERIFY(search->folderOnly()&&!search->busy());
        QTest::keyClick(editor->window(),Qt::Key_Escape);QTRY_VERIFY(!search->active());QVERIFY(browser->canGoForward());QVERIFY(!browser->canGoBack());QCOMPARE(browser->folderPath(),m_root);
        click(visible("bleeckerFileChooserForward"));QTRY_VERIFY(search->active());QCOMPARE(singleTermText(search),token);QCOMPARE(singleTermMode(search),"everything");QVERIFY(search->folderOnly());
        QTRY_VERIFY(!search->busy()&&row(search,"pine-only.txt")>=0&&row(search,token+"-outside.txt")<0);
        click(visible("bleeckerFileChooserBack"));QTRY_VERIFY(!search->active());QVERIFY(browser->canGoForward());
        click(editor);type(editor->window(),"another-control");QTRY_VERIFY(search->active());QVERIFY(!browser->canGoForward());QVERIFY(results(view.rootObject()).isEmpty());browser->cancel();
    }
    void literalQuotesAndFolderNavigation(){
        FileChooserBrowser browser;browser.setAllowedContentTypes({"text/plain"});QVERIFY(browser.open(QUrl::fromLocalFile(m_root)));
        auto search=browser.search();search->setFolderOnly(true);const auto name=token+"-quote\".txt";const auto path=m_root+"/"+name;
        put(path,"Controlled quoted filename.\n");setRaw(search,name);
        QTRY_VERIFY_WITH_TIMEOUT(!search->busy()&&row(search,name)>=0,15000);QVERIFY(search->error().isEmpty());
        QVERIFY(QFile::remove(path));
        const auto folder=m_root+"/"+token+"-folder";QVERIFY(QDir().mkdir(folder));setRaw(search,token+"-folder");
        QTRY_VERIFY_WITH_TIMEOUT(!search->busy()&&row(search,token+"-folder")>=0,15000);
        search->select(row(search,token+"-folder"));QVERIFY(browser.canAccept());QSignalSpy owner(&browser,&FileChooserBrowser::result);
        browser.acceptSelection();QCOMPARE(browser.folderPath(),folder);QVERIFY(!search->active());QVERIFY(owner.isEmpty());browser.cancel();QVERIFY(QDir().rmdir(folder));
    }
    void cancellationReopenAndOwnerRemoval(){
        QQuickView view;QVERIFY(load(view));QPointer<FileChooserBrowser> browser=open(view);QVERIFY(browser);
        auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);click(editor);type(editor->window(),token);
        click(visible("bleeckerFileChooserCancel"));QTRY_VERIFY(!browser->active());QVERIFY(!browser->search()->active());
        browser=open(view);QVERIFY(browser);setRaw(browser->search(),"previous-nonmatching-query");setRaw(browser->search(),token);browser->search()->setFolderOnly(true);
        QTRY_VERIFY_WITH_TIMEOUT(!browser->search()->busy()&&row(browser->search(),"pine-only.txt")>=0,15000);
        view.rootObject()->setProperty("mounted",false);QTRY_VERIFY(!browser);QTest::qWait(100);
        view.rootObject()->setProperty("mounted",true);QTRY_VERIFY(view.rootObject()->findChild<QQuickItem*>("fileInput"));browser=open(view);QVERIFY(browser);
        browser->search()->setFolderOnly(true);setRaw(browser->search(),token);
        QTRY_VERIFY_WITH_TIMEOUT(!browser->search()->busy()&&row(browser->search(),"pine-only.txt")>=0,15000);
        view.rootObject()->setProperty("removeOnResult",true);browser->search()->select(row(browser->search(),"pine-only.txt"));browser->acceptSelection();
        QTRY_VERIFY(!browser);QCOMPARE(results(view.rootObject()).size(),1);QVERIFY(view.rootObject()->property("visibleAtCallback").toBool());QTest::qWait(100);
    }
    void unavailableIndexIsVisibleAndCancels(){
        if(!m_unavailable)QSKIP("Executed separately on a real session bus without an index provider");
        QQuickView view;QVERIFY(load(view));auto browser=open(view);QVERIFY(browser);auto editor=visible("bleeckerFileChooserSearch");QVERIFY(editor);
        click(editor);type(editor->window(),token);QTRY_VERIFY_WITH_TIMEOUT(!browser->search()->busy()&&!browser->error().isEmpty(),15000);
        QVERIFY(browser->error().startsWith("Indexed search is unavailable:"));QCOMPARE(browser->search()->count(),0);QVERIFY(!browser->canAccept());
        auto message=visible("bleeckerFileChooserError");QVERIFY(message);QCOMPARE(message->property("text").toString(),QStringLiteral("Indexed search is unavailable. Clear the search to browse folders."));
        click(visible("bleeckerFileChooserCancel"));QTRY_VERIFY(!browser->active());QVERIFY(results(view.rootObject()).isEmpty());
    }
};

int main(int argc,char **argv){
    QGuiApplication application(argc,argv);auto arguments=application.arguments();
    const int at=arguments.indexOf("--file-input-search-root");if(at<0||at+1>=arguments.size())return 2;
    const auto root=arguments[at+1];arguments.removeAt(at+1);arguments.removeAt(at);
    const bool unavailable=arguments.removeAll("--file-input-search-no-index")>0;
    FileSearchTests tests(root,unavailable);return QTest::qExec(&tests,arguments);
}

#include "filesearch.moc"

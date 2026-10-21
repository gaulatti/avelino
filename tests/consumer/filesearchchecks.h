#pragma once
#include <QAbstractItemModel>
#include <QAccessibleActionInterface>
#include <QElapsedTimer>
#include <QQuickItemGrabResult>
#include <functional>

// Independent consumer: only public QML properties, invokables and real input.
static void runFileInputSearchConsumer(QQuickWindow *window,QGuiApplication &app,const QCommandLineParser &parser){
    auto check=[&](bool value,const char *message){if(!value){qCritical("FileInput search: %s",message);app.exit(99);}return value;};
    const auto root=parser.value("file-input-search-root"),token=QStringLiteral("avelinoulnacerulean");
    if(!check(QDir::isAbsolutePath(root)&&QFileInfo(root).isDir(),"Controlled indexed root is required"))return;
    const auto prefix=parser.isSet("evidence")?parser.value("evidence"):parser.value("file-input-report");
    if(!prefix.isEmpty()&&!check(!QFile::exists(prefix+".json"),"Report already exists"))return;
    if(!prefix.isEmpty())QDir().mkpath(QFileInfo(prefix).absolutePath());
    auto fixture=[&]{return window->property("primaryFixture").value<QQuickItem*>();};
    auto control=[&]{return fixture()?fixture()->property("control").value<QQuickItem*>():nullptr;};
    auto browser=[&]{return control()?control()->property("browser").value<QObject*>():nullptr;};
    auto search=[&]{return browser()?browser()->property("search").value<QObject*>():nullptr;};
    auto expression=[&]{return search()?search()->property("expression").toList():QVariantList{};};
    auto singleTermText=[&]{const auto parts=expression();if(parts.size()!=1)return QString();const auto part=parts[0].toMap();return part.value(part.value("kind")=="token"?"query":"text").toString();};
    auto singleTermMode=[&]{const auto parts=expression();if(parts.size()!=1)return QString();const auto part=parts[0].toMap();return part.value("kind")=="token"?part.value("mode").toString():QStringLiteral("general");};
    const QString object(QChar::ObjectReplacementCharacter);
    std::function<QQuickItem*(QQuickItem*,const QString&)> find=[&](QQuickItem *item,const QString &name)->QQuickItem*{
        if(!item)return nullptr;if(item->objectName()==name)return item;
        for(auto child:item->childItems())if(auto found=find(child,name))return found;return nullptr;
    };
    auto visible=[&](const QString &name)->QQuickItem*{
        for(auto candidate:QGuiApplication::topLevelWindows())if(auto quick=qobject_cast<QQuickWindow*>(candidate);quick&&quick->isVisible())
            if(auto item=find(quick->contentItem(),name);item&&item->isVisible())return item;return nullptr;
    };
    auto wait=[&](const std::function<bool()> &condition,const char *message){
        QElapsedTimer timer;timer.start();while(!condition()&&timer.elapsed()<15000)QTest::qWait(20);
        if(!condition()&&search())qWarning()<<"FileInput search diagnostic"<<expression()
            <<search()->property("folderOnly")<<search()->property("busy")<<search()->property("error")<<search()->property("count");
        return check(condition(),message);
    };
    auto click=[&](QQuickItem *item,Qt::KeyboardModifiers modifiers=Qt::NoModifier){
        if(!check(item&&item->window(),"Input target is missing"))return false;
        QTest::mouseClick(item->window(),Qt::LeftButton,modifiers,item->mapToScene(item->boundingRect().center()).toPoint());return true;
    };
    auto row=[&](const QString &name){
        auto model=qobject_cast<QAbstractItemModel*>(search());if(!model)return -1;
        const int role=model->roleNames().key("fileName",-1);if(role<0)return -1;
        for(int i=0;i<model->rowCount();++i)if(model->data(model->index(i,0),role).toString()==name)return i;return -1;
    };
    auto popupPixels=[&](QQuickWindow *target){
        if(!target||!target->isExposed())return QImage();
        auto capture=target->contentItem()->grabToImage();if(!capture)return QImage();
        QSignalSpy ready(capture.data(),&QQuickItemGrabResult::ready);
        if(capture->image().isNull()&&!ready.wait(5000))return QImage();
        const auto pixels=capture->image();
        if(pixels.size()!=QSize(qRound(target->width()*target->devicePixelRatio()),qRound(target->height()*target->devicePixelRatio())))return QImage();
        return pixels;
    };
    auto popupReady=[&](QQuickWindow *target){
        QElapsedTimer elapsed;elapsed.start();QImage previous;
        while(elapsed.elapsed()<5000){
            const auto pixels=popupPixels(target);
            if(!pixels.isNull()&&pixels==previous)return true;
            previous=pixels;QTest::qWait(16);
        }
        return false;
    };
    auto type=[&](QQuickItem *editor){
        if(!check(editor&&editor->window()&&QTest::qWaitForWindowExposed(editor->window(),5000)
            &&popupReady(editor->window()),"Search window did not expose a stable frame")||!click(editor))return false;
        if(!wait([&]{return editor->hasActiveFocus()&&editor->window()->isActive();},"Search editor did not gain keyboard focus"))return false;
        for(auto character:token.toLatin1())QTest::keyClick(editor->window(),character);
        return check(editor->property("text").toString()==token,"Search editor did not receive every typed character");
    };
    QJsonArray phases;
    auto observe=[&](const QString &phase){
        qInfo().noquote()<<"FileInput search phase:"<<phase;
        auto model=qobject_cast<QAbstractItemModel*>(search());QJsonArray names;
        if(model){const auto role=model->roleNames().key("fileName",-1);for(int i=0;i<model->rowCount();++i)names.append(model->data(model->index(i,0),role).toString());}
        auto editor=visible("bleeckerFileChooserSearch");
        phases.append(QJsonObject{{"phase",phase},{"expression",QJsonArray::fromVariantList(expression())},
            {"editorText",editor?editor->property("text").toString():QString()},
            {"selectedText",editor?editor->property("selectedText").toString():QString()},
            {"folderOnly",search()&&search()->property("folderOnly").toBool()},
            {"error",search()?search()->property("error").toString():QString()},
            {"busy",search()&&search()->property("busy").toBool()},{"names",names},{"state",chartMap(fixture(),"state")}});
    };
    auto save=[&](QQuickItem *item,const QString &phase){
        if(prefix.isEmpty())return true;
        const auto path=prefix+"-"+phase+".png";if(!check(item&&item->window()&&!QFile::exists(path),"Capture missing or already present"))return false;
        const auto pixels=popupPixels(item->window());
        return check(!pixels.isNull()&&pixels.save(path),"Capture could not be saved");
    };
    auto report=[&]{
        if(!prefix.isEmpty()){
            QFile file(prefix+".json");if(!check(file.open(QIODevice::WriteOnly|QIODevice::NewOnly),"Report could not be created"))return false;
            file.write(QJsonDocument(QJsonObject{{"accepted",false},{"fixture","file-input-search"},{"qt",qVersion()},
                {"platform",QGuiApplication::platformName()},{"dpr",window->devicePixelRatio()},
                {"graphicsApi",int(window->rendererInterface()->graphicsApi())},
                {"appearance",parser.isSet("dark")?"dark":"light"},{"textScale",parser.value("text-scale").toDouble()},
                {"structuralChecks","passed"},
                {"providerUnavailable",parser.isSet("file-input-search-no-index")},{"phases",phases},
                {"nativeRasterAccepted",false},{"readerAcceptance",false},{"physicalInput",false}}).toJson());
        }
        return true;
    };
    window->setProperty("fixtureFolder",QUrl::fromLocalFile(root));
    if(!check(waitForShapeFrame(window)&&control(),"Caller fixture is missing"))return;
    if(!click(control()->property("inputItem").value<QQuickItem*>())||!wait([&]{return visible("bleeckerFileChooserSearch");},"Search editor did not open"))return;
    auto editor=visible("bleeckerFileChooserSearch");if(!type(editor))return;
    if(parser.isSet("file-input-search-no-index")){
        if(!wait([&]{return !search()->property("busy").toBool()&&!search()->property("error").toString().isEmpty();},"Missing provider did not become an error"))return;
        if(!check(visible("bleeckerFileChooserError")&&visible("bleeckerFileChooserError")->property("text").toString()=="Indexed search is unavailable. Clear the search to browse folders."
            &&!browser()->property("canAccept").toBool()&&search()->property("count").toInt()==0,"Provider error is not visible or search silently fell back"))return;
        observe("missing-provider");if(!save(editor,"missing-provider")||!click(visible("bleeckerFileChooserCancel")))return;
        if(!check(!browser()->property("active").toBool()&&chartMap(fixture(),"state")["results"].toArray().isEmpty(),"Cancellation sent a result"))return;
        if(report())app.exit(0);return;
    }
    if(!wait([&]{return !search()->property("busy").toBool()&&row("pine-only.txt")>=0&&row(token+"-outside.txt")>=0&&row("pine-peer.txt")>=0;},"Global filename/content results did not arrive"))return;
    observe("global");if(!save(editor,"global")||!click(visible("bleeckerFileChooserSearchFolder")))return;
    if(!wait([&]{return !search()->property("busy").toBool()&&row(token+"-outside.txt")<0&&row("pine-peer.txt")<0&&row(token+"-child.txt")>=0;},"Recursive folder scope did not exclude the peer"))return;
    observe("folder");if(!click(editor))return;QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Return);
    if(!wait([&]{return singleTermMode()=="filename"&&!search()->property("busy").toBool()&&row("pine-only.txt")<0&&row(token+"-name.txt")>=0;},"Filename suggestion did not change the actual results"))return;
    observe("filename");if(!save(editor,"filename"))return;
    auto fieldHost=visible("bleeckerFileChooserSearchHost");if(!check(fieldHost,"Search field host is missing"))return;
    QTest::mouseClick(editor->window(),Qt::LeftButton,{},fieldHost->mapToScene(QPointF(1,fieldHost->height()/2)).toPoint());
    if(!wait([&]{return editor->hasActiveFocus()&&editor->window()->isActive();},"Token query did not gain keyboard focus")){
        observe("token-replacement-focus-failure");save(editor,"token-replacement-focus-failure");report();return;
    }
    QTest::keyClick(editor->window(),Qt::Key_A,Qt::ControlModifier);
    if(!check(editor->property("selectedText").toString()==object,"Select All did not select the complete token query")){
        observe("token-replacement-selection-failure");save(editor,"token-replacement-selection-failure");report();return;
    }
    const auto replacement=token+"-name";
    for(auto character:replacement.toLatin1())QTest::keyClick(editor->window(),character);
    if(!wait([&]{return singleTermText()==replacement&&singleTermMode()=="general"&&!search()->property("busy").toBool()
        &&!visible("bleeckerFileChooserSearchToken")&&visible("bleeckerFileChooserSearchSuggestion_0");},"Replacing the complete token did not restore raw search")){
        qWarning()<<"Token replacement field"<<editor->metaObject()->className()<<editor->property("expression")<<editor->hasActiveFocus()<<editor->window()->isActive();
        observe("token-replacement-failure");save(editor,"token-replacement-failure");report();return;
    }
    observe("token-replacement");if(!save(editor,"token-replacement"))return;
    for(int i=0;i<6&&singleTermText()!=token;++i)QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
    if(!wait([&]{return singleTermText()==token&&singleTermMode()=="filename"&&!search()->property("busy").toBool();},"Undo did not restore the original Filename token"))return;
    if(!check(editor->property("selectedText").toString()==object,"Undo restored contents without selecting the token"))return;
    observe("token-undo");if(!save(editor,"token-undo"))return;
    for(int i=0;i<6&&singleTermText()!=replacement;++i)QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier|Qt::ShiftModifier);
    if(!wait([&]{return singleTermText()==replacement&&singleTermMode()=="general"&&!search()->property("busy").toBool();},"Redo did not restore the raw replacement"))return;
    observe("token-redo");if(!save(editor,"token-redo"))return;
    QTest::keyClick(editor->window(),Qt::Key_A,Qt::ControlModifier);
    for(auto character:token.toLatin1())QTest::keyClick(editor->window(),character);
    QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Return);
    if(!wait([&]{return singleTermMode()=="filename"&&!search()->property("busy").toBool()&&row("pine-only.txt")<0;},"Filename search did not settle after token editing"))return;
    if(!click(visible("bleeckerFileChooserSearchToken"))
        ||!wait([&]{return visible("bleeckerFileChooserSearchMode_everything");},"Search token menu is missing")
        ||!save(editor,"token-menu")||!click(visible("bleeckerFileChooserSearchMode_everything")))return;
    if(!wait([&]{return singleTermMode()=="everything"&&!search()->property("busy").toBool()&&row("pine-only.txt")>=0&&row(token+"-name.txt")>=0;},"Everything token did not restore content and filename matches"))return;
    if(!wait([&]{return editor->hasActiveFocus();},"Token menu did not return focus to Search"))return;
    QTest::keyClick(editor->window(),Qt::Key_End);
    for(auto character:QByteArray("pine"))QTest::keyClick(editor->window(),character);
    if(!check(editor->property("text").toString()==object+"pine","Trailing draft changed the committed token"))return;
    QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Return);
    const QVariantList compound{QVariantMap{{"kind","token"},{"mode","everything"},{"query",token}},QVariantMap{{"kind","token"},{"mode","filename"},{"query","pine"}}};
    if(!wait([&]{return expression()==compound&&!search()->property("busy").toBool()&&search()->property("count").toInt()==1&&row("pine-only.txt")==0;},"Compound Filename term did not narrow the indexed results"))return;
    observe("compound-mixed");if(!save(editor,"compound-mixed"))return;
    auto second=visible("bleeckerFileChooserSearchToken_1");auto secondAccessible=second?QAccessible::queryAccessibleInterface(second):nullptr;
    if(!check(secondAccessible&&secondAccessible->actionInterface()&&secondAccessible->text(QAccessible::Name)=="Filename: pine","Second token has no independent accessible menu"))return;
    secondAccessible->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
    if(!wait([&]{return visible("bleeckerFileChooserSearchMode_everything_1");},"Second token mode menu did not open"))return;
    auto choice=QAccessible::queryAccessibleInterface(visible("bleeckerFileChooserSearchMode_everything_1"));
    if(!check(choice&&choice->actionInterface(),"Second token Everything action is missing"))return;
    choice->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
    auto both=compound;auto last=both[1].toMap();last["mode"]="everything";both[1]=last;
    if(!wait([&]{return expression()==both&&!search()->property("busy").toBool()&&search()->property("count").toInt()==1&&row("pine-only.txt")==0;},"Independent Everything term did not retain conjunction"))return;
    observe("compound-everything");if(!save(editor,"compound-everything"))return;
    QTest::keyClick(editor->window(),Qt::Key_Home);QTest::keyClick(editor->window(),Qt::Key_Right);
    if(!check(editor->property("selectedText").toString()==object,"Right from the start did not select the first token"))return;
    for(auto character:QByteArray("name"))QTest::keyClick(editor->window(),character);
    if(!check(editor->property("text").toString()=="name"+object&&expression().size()==2&&expression()[1].toMap()==both[1].toMap(),"Replacing one token changed another"))return;
    if(!wait([&]{return !search()->property("busy").toBool();},"Replacement query did not settle"))return;
    observe("compound-replacement");if(!save(editor,"compound-replacement"))return;
    QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
    if(!wait([&]{return expression()==both&&editor->property("selectedText").toString()==object&&!search()->property("busy").toBool();},"Compound Undo lost token metadata or selection"))return;
    observe("compound-undo");if(!save(editor,"compound-undo"))return;
    QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier|Qt::ShiftModifier);
    if(!wait([&]{return editor->property("text").toString()=="name"+object&&!search()->property("busy").toBool();},"Compound Redo did not restore the draft"))return;
    observe("compound-redo");if(!save(editor,"compound-redo"))return;
    QTest::keyClick(editor->window(),Qt::Key_Z,Qt::ControlModifier);
    if(!wait([&]{return expression()==both&&!search()->property("busy").toBool()&&row("pine-only.txt")==0;},"Compound owner selection did not recover"))return;
    auto selected=visible("bleeckerFileChooserSearchRow_"+QString::number(row("pine-only.txt")));
    auto accessible=selected?QAccessible::queryAccessibleInterface(selected):nullptr;
    if(!check(accessible&&accessible->actionInterface(),"Search row accessibility action is missing"))return;
    accessible->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
    if(!check(browser()->property("canAccept").toBool(),"Accessible row selection did not enable Open"))return;
    auto resultsAccessible=QAccessible::queryAccessibleInterface(visible("bleeckerFileChooserSearchResults"));
    auto selection=resultsAccessible?resultsAccessible->selectionInterface():nullptr;
    if(!check(selection&&selection->selectedItemCount()==1&&selection->selectedItem(0)->text(QAccessible::Name)=="pine-only.txt",
        "Result view does not report the selected row through the accessibility selection interface"))return;
    observe("selected");if(!save(editor,"selected")||!click(visible("bleeckerFileChooserOpen")))return;
    if(!wait([&]{return !browser()->property("active").toBool()&&!visible("bleeckerFileChooserSearch");},"Successful chooser did not finish closing"))return;
    const auto state=chartMap(fixture(),"state");const auto results=state["results"].toArray();
    if(!check(results.size()==1&&state["visibleAtCallback"]==true
        &&results[0].toObject()["urls"].toArray()==QJsonArray{QUrl::fromLocalFile(root+"/pine-only.txt").toString()},"Owner result or callback-before-dismissal order changed"))return;
    observe("owner-result");
    if(!click(control()->property("inputItem").value<QQuickItem*>())||!wait([&]{return visible("bleeckerFileChooserSearch");},"Reopen failed"))return;
    if(!check(!search()->property("active").toBool()&&expression().isEmpty()&&!search()->property("folderOnly").toBool(),"Search context survived reopening"))return;
    editor=visible("bleeckerFileChooserSearch");if(!type(editor)||!click(visible("bleeckerFileChooserCancel")))return;
    if(!check(!browser()->property("active").toBool()&&chartMap(fixture(),"state")["results"].toArray().size()==1,"Cancellation changed the owner result"))return;
    if(!wait([&]{return !visible("bleeckerFileChooserSearch");},"Cancelled chooser did not finish closing"))return;
    observe("cancelled-query");
    if(!parser.isSet("evidence")){if(report())app.exit(0);return;}
    // Keep a real selected search surface mapped until the external compositor
    // capture acknowledges it through the existing consumer evidence protocol.
    if(!click(control()->property("inputItem").value<QQuickItem*>())||!wait([&]{return visible("bleeckerFileChooserSearch");},"Session chooser did not reopen"))return;
    editor=visible("bleeckerFileChooserSearch");if(!type(editor)||!click(visible("bleeckerFileChooserSearchFolder")))return;
    if(!click(editor))return;
    QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Down);QTest::keyClick(editor->window(),Qt::Key_Return);
    if(!wait([&]{return singleTermMode()=="everything"&&search()->property("folderOnly").toBool()
        &&!search()->property("busy").toBool()&&row("pine-only.txt")>=0&&row("pine-peer.txt")<0;},"Session search did not settle"))return;
    selected=visible("bleeckerFileChooserSearchRow_"+QString::number(row("pine-only.txt")));
    accessible=selected?QAccessible::queryAccessibleInterface(selected):nullptr;
    if(!check(accessible&&accessible->actionInterface(),"Session search row accessibility action is missing"))return;
    accessible->actionInterface()->doAction(QAccessibleActionInterface::pressAction());
    if(!check(browser()->property("canAccept").toBool(),"Session selection did not enable Open"))return;
    observe("session-selected");
    // Use the existing chooser's asynchronous scene readback: native-window GL
    // readback invalidates Wayland popup surfaces in the pinned Qt SDK.
    if(!save(editor,"session-selected")||!check(popupReady(editor->window())&&popupPixels(editor->window()).save(prefix+".png"),"Session popup scene capture failed")||!report())return;
    auto timer=new QTimer(&app);
    QObject::connect(timer,&QTimer::timeout,&app,[&app,prefix]{if(QFile::exists(prefix+".captured"))app.exit(0);});timer->start(100);
    QTimer::singleShot(10000,&app,[&app]{app.exit(93);});
}

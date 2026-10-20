#pragma once
#include <QAbstractItemModel>
#include <QDir>
#include <QQuickItemGrabResult>
#include <QTemporaryDir>

static void runFileInputConsumer(QQuickWindow *window,QGuiApplication &app,const QCommandLineParser &parser,double textScale){
    auto check=[&](bool value,const char *message){if(!value){qCritical("FileInput: %s",message);app.exit(99);}return value;};
    QFile reference(":/avelino/fixtures/native-file-input-witnesses.json");
    if(!check(reference.open(QIODevice::ReadOnly),"Native observations missing"))return;
    const auto native=QJsonDocument::fromJson(reference.readAll()).object();
    if(!check(native["reference"]=="fe8a1d462fbd793d883fb92086a16aa2947e32c9"&&native["accepted"]==false
        &&native["closed"].toArray().size()==256&&native["sizing"].toArray().size()==256,"Incomplete native source matrix"))return;
    const auto prefix=parser.isSet("evidence")?parser.value("evidence"):parser.value("file-input-report");
    if(!prefix.isEmpty()&&!check(!QFile::exists(prefix+".json"),"Report path already exists"))return;
    auto fixture=[&]{return window->property("primaryFixture").value<QQuickItem*>();};
    auto control=[&]{return fixture()?fixture()->property("control").value<QQuickItem*>():nullptr;};
    auto browser=[&]{return control()?control()->property("browser").value<QObject*>():nullptr;};
    auto chooser=[&]{return control()?control()->property("chooser").value<QObject*>():nullptr;};
    auto content=[&]{return chooser()?chooser()->property("contentItem").value<QQuickItem*>():nullptr;};
    auto state=[&]{return chartMap(fixture(),"state");};
    auto selected=[&](const QJsonObject &row){return row["appearance"]==(parser.isSet("dark")?"dark":"light")
        &&row["textScale"].toDouble()==textScale&&row["dpr"].toDouble()==window->devicePixelRatio();};
    auto configure=[&](const QJsonObject &configuration,const QJsonArray &types){
        fixture()->setProperty("mounted",false);if(!check(waitForShapeFrame(window),"Unmounted frame missing"))return false;
        if(!check(QMetaObject::invokeMethod(window,"configure",Q_ARG(QVariant,configuration.toVariantMap()),Q_ARG(QVariant,types.toVariantList())),"Configuration did not reach the caller"))return false;
        return check(waitForShapeFrame(window)&&control(),"Configured FileInput missing");
    };
    auto popupPixels=[&](QQuickWindow *target){
        if(!target||!target->isExposed())return QImage();
        // Capture the complete owned popup scene through Qt's asynchronous item
        // API. Direct native-window GL readback invalidates the Wayland popup
        // surface in the pinned SDK; external compositor captures are separate.
        auto result=target->contentItem()->grabToImage();if(!result)return QImage();
        QSignalSpy ready(result.data(),&QQuickItemGrabResult::ready);
        if(result->image().isNull()&&!ready.wait(5000))return QImage();
        const auto pixels=result->image();
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
    auto save=[&](QQuickWindow *target,const QString &name){
        if(prefix.isEmpty())return true;
        if(!check(target&&!QFile::exists(prefix+"-"+name+".png"),"Capture already exists or window missing"))return false;
        const auto pixels=target==window?target->grabWindow():popupPixels(target);
        return check(!pixels.isNull()&&pixels.save(prefix+"-"+name+".png"),"Capture failed");
    };
    int frames=0,states=0,pointers=0,keys=0;QJsonArray closed,sizing,actions,accessibility;QJsonObject standard;
    for(const auto &value:native["closed"].toArray()){
        const auto row=value.toObject();if(!selected(row))continue;
        const auto configuration=row["configuration"].toObject();if(!configure(configuration,row["linuxContentTypes"].toArray()))return;
        const auto actual=state(),frame=chartMap(fixture(),"frame");
        const auto expectedTitle=configuration["title"].isString()?configuration["title"].toString():QString::fromUtf8("Choose file…");
        const bool frameMatch=frame==row["frames"];
        const bool stateMatch=actual["mounted"]==true&&actual["title"]==expectedTitle
            &&actual["enabled"].toBool()==!configuration["disabled"].toBool()&&actual["results"]==QJsonArray{}
            &&actual["pickerVisible"]==false&&actual["sourceTypes"]==configuration["types"];
        frames+=frameMatch;states+=stateMatch;
        closed.append(QJsonObject{{"configuration",configuration},{"linuxContentTypes",row["linuxContentTypes"]},{"reference",row["reference"]},
            {"frames",frame},{"nativeFrames",row["frames"]},{"nativeState",row["nativeState"]},{"state",actual},{"nativeCompleteFramesMatch",frameMatch},{"nativeContractStateMatch",stateMatch}});
        if(!save(window,configuration["id"].toString()))return;
        if(configuration["id"]=="default")standard=configuration;
    }
    for(const auto &value:native["sizing"].toArray()){
        const auto row=value.toObject();if(!selected(row))continue;
        if(!configure(row["configuration"].toObject(),row["linuxContentTypes"].toArray()))return;
        sizing.append(QJsonObject{{"configuration",row["configuration"]},{"nativeProposals",row["proposals"]},
            {"qtImplicitSize",QJsonObject{{"width",control()->implicitWidth()},{"height",control()->implicitHeight()}}},
            {"status","Direct Qt/native proposal equivalence pending"}});
    }
    if(!check(closed.size()==32&&sizing.size()==32&&!standard.isEmpty()&&states==32,"Incomplete selected native context or changed contract state"))return;
    QTemporaryDir root;if(!check(root.isValid(),"Controlled fixture directory unavailable"))return;
    QDir directory(root.path());
    for(const auto &name:{"one.txt","two.txt","photo.png","spaces in name.txt"}){
        QFile file(directory.filePath(name));if(!check(file.open(QIODevice::WriteOnly)&&file.write("Avelino controlled file-input fixture\n")>0,"Controlled fixture write failed"))return;
    }
    if(!check(directory.mkdir("folder")&&directory.mkdir("untitled folder"),"Controlled folder missing"))return;
    {QFile file(directory.filePath("folder/child.txt"));if(!check(file.open(QIODevice::WriteOnly)&&file.write("Avelino child fixture\n")>0,"Controlled child missing"))return;}
    if(!check(QFile::link(directory.filePath("one.txt"),directory.filePath("symlink.txt")),"Controlled alias missing"))return;
    window->setProperty("fixtureFolder",QUrl::fromLocalFile(root.path()));
    auto click=[&](QQuickItem *item,Qt::KeyboardModifiers modifiers=Qt::NoModifier){
        if(!check(item&&item->window(),"Pointer target missing"))return false;
        QTest::mouseClick(item->window(),Qt::LeftButton,modifiers,item->mapToScene(item->boundingRect().center()).toPoint());++pointers;
        QTest::qWait(40);return true;
    };
    auto open=[&]{
        if(!click(control()->property("inputItem").value<QQuickItem*>()))return false;
        QElapsedTimer timer;timer.start();while(timer.elapsed()<1000&&(!content()||!content()->window()||!chooser()->property("visible").toBool()))QTest::qWait(10);
        if(!check(content()&&content()->window()!=window&&chooser()->property("visible").toBool(),"Owned chooser window missing"))return false;
        // A popup's QQuickWindow can exist before Wayland configures its native
        // surface. Do not request GL frame readbacks from an unexposed window.
        auto popup=content()->window();
        if(!check(QTest::qWaitForWindowExposed(popup,5000),"Owned chooser window did not become exposed"))return false;
        return check(popupReady(popup),"Owned chooser frame did not stabilize");
    };
    auto row=[&](int column,const QString &name){
        auto columns=qobject_cast<QAbstractItemModel*>(browser());if(!columns)return -1;
        const auto role=columns->roleNames().key("directoryModel",-1);
        auto model=qobject_cast<QAbstractItemModel*>(columns->data(columns->index(column,0),role).value<QObject*>());if(!model)return -1;
        const auto nameRole=model->roleNames().key("fileName",-1);
        for(int i=0;i<model->rowCount();++i)if(model->data(model->index(i,0),nameRole).toString()==name)return i;
        return -1;
    };
    auto selectRow=[&](int column,const QString &name,Qt::KeyboardModifiers modifiers=Qt::NoModifier){
        const auto index=row(column,name);if(!check(index>=0,"Controlled row not listed"))return false;
        return click(findVisualItem(content(),"bleeckerFileChooserRow"+QString::number(column)+"_"+QString::number(index)),modifiers);
    };
    auto record=[&](const QString &phase){actions.append(QJsonObject{{"phase",phase},{"state",state()},{"browserActive",browser()?browser()->property("active").toBool():false}});};
    auto typeText=[&](QQuickWindow *target,const QString &value){for(const auto character:value.toLatin1()){QTest::keyClick(target,character);++keys;}};
    if(!configure(standard,QJsonArray{"text/plain"})||!open()||!selectRow(0,"one.txt"))return;
    if(!selectRow(0,"photo.png")||!check(browser()->property("selectedUrls").toList().size()==1,"Ineligible file changed selection"))return;
    QTest::keyPress(content()->window(),Qt::Key_Control);++keys;
    if(!selectRow(0,"two.txt",Qt::ControlModifier))return;
    QTest::keyRelease(content()->window(),Qt::Key_Control);++keys;
    if(!check(browser()->property("selectedUrls").toList().size()==2,"Actual modifier did not reach multiple selection")||!save(content()->window(),"multiple-files"))return;
    auto accept=findVisualItem(content(),"bleeckerFileChooserOpen");auto accessible=QAccessible::queryAccessibleInterface(accept);
    if(!check(accessible&&accessible->role()==QAccessible::Button&&accessible->text(QAccessible::Name)=="Open","Open accessibility interface missing"))return;
    accessibility.append(QJsonObject{{"name",accessible->text(QAccessible::Name)},{"role",int(accessible->role())},{"readerAcceptance","pending"}});
    if(!click(accept)||!check(state()["results"].toArray().size()==1&&state()["visibleAtCallback"]==true&&!browser()->property("active").toBool(),"Owner multiple-selection callback failed"))return;
    const auto urls=state()["results"].toArray()[0].toObject()["urls"].toArray();
    if(!check(urls.size()==2&&QUrl(urls[0].toString()).toLocalFile()==directory.filePath("one.txt")&&QUrl(urls[1].toString()).toLocalFile()==directory.filePath("two.txt"),"Owner URL order changed"))return;
    record("multiple-owner-result");
    if(!open()||!click(findVisualItem(content(),"bleeckerFileChooserCancel"))||!check(state()["results"].toArray().size()==1,"Cancel called the owner"))return;record("cancel-no-result");
    if(!open())return;QTest::keyClick(content()->window(),Qt::Key_Escape);++keys;QTest::qWait(40);
    if(!check(!browser()->property("active").toBool()&&state()["results"].toArray().size()==1,"Escape did not cancel without result"))return;record("escape-no-result");
    if(!configure(standard,QJsonArray{"text/plain"})||!open()||!selectRow(0,"symlink.txt")||!click(findVisualItem(content(),"bleeckerFileChooserOpen")))return;
    if(!check(QUrl(state()["results"].toArray()[0].toObject()["urls"].toArray()[0].toString()).toLocalFile()==directory.filePath("one.txt"),"Alias URL was not resolved"))return;record("alias-result");
    if(!configure(standard,QJsonArray{"text/plain"})||!open()||!selectRow(0,"one.txt")||!click(findVisualItem(content(),"bleeckerFileChooserNewFolder")))return;
    auto folderPrompt=chooser()->property("newFolderDialog").value<QObject*>();
    if(!check(folderPrompt&&folderPrompt->property("visible").toBool(),"Owned New Folder prompt missing"))return;
    auto folderName=folderPrompt->property("nameInput").value<QQuickItem*>();
    auto folderCreate=folderPrompt->property("createInput").value<QQuickItem*>();
    if(!check(folderName&&folderCreate&&folderName->hasActiveFocus()&&folderName->property("text").toString()=="untitled folder 2","Native observed default folder name/focus missing"))return;
    if(!save(content()->window(),"new-folder-prompt"))return;
    typeText(folderName->window(),"one.txt");QTest::qWait(40);
    if(!check(!folderCreate->isEnabled()&&folderPrompt->property("error").toString()=="This name is already taken.","Existing name did not disable Create")||!save(content()->window(),"new-folder-conflict"))return;
    record("new-folder-conflict");
    QTest::keyClick(folderName->window(),Qt::Key_Escape);++keys;QTest::qWait(40);
    if(!check(!folderPrompt->property("visible").toBool()&&browser()->property("active").toBool()&&state()["results"].toArray().isEmpty()&&!QFileInfo::exists(directory.filePath("untitled folder 2")),"Nested Escape changed the owner or created a folder"))return;
    record("new-folder-nested-escape");
    QTest::keyClick(content()->window(),Qt::Key_N,Qt::ControlModifier|Qt::ShiftModifier);++keys;QTest::qWait(40);
    if(!check(folderPrompt->property("visible").toBool()&&folderName->hasActiveFocus(),"New Folder keyboard shortcut failed"))return;
    typeText(folderName->window(),"Created by consumer");
    QTest::keyClick(folderName->window(),Qt::Key_Return);++keys;QTest::qWait(40);
    const auto created=directory.filePath("Created by consumer");
    if(!check(!folderPrompt->property("visible").toBool()&&browser()->property("folderPath").toString()==created&&QFileInfo(created).isDir()
        &&!browser()->property("canAccept").toBool()&&state()["results"].toArray().isEmpty(),"New Folder did not create/navigate without an owner result")||!save(content()->window(),"new-folder-created"))return;
    record("new-folder-created");
    if(!click(findVisualItem(content(),"bleeckerFileChooserBack"))||!check(browser()->property("folderPath").toString()==root.path()&&browser()->property("canGoForward").toBool()
        &&browser()->property("selectedUrls").toList().isEmpty()&&!browser()->property("canAccept").toBool(),"Back did not restore the parent with cleared native selection"))return;
    record("history-back");
    if(!click(findVisualItem(content(),"bleeckerFileChooserForward"))||!check(browser()->property("folderPath").toString()==created,"Forward did not restore the created folder"))return;
    record("history-forward");
    if(!click(findVisualItem(content(),"bleeckerFileChooserCancel"))||!check(state()["results"].toArray().isEmpty(),"Folder creation called the owner"))return;
    record("new-folder-cancel-no-result");
    // Exercise the installed view menu, hierarchy and selection without Avelino
    // C++ headers or library sources in this independent consumer.
    if(!configure(standard,QJsonArray{"text/plain"})||!open()||!selectRow(0,"one.txt"))return;
    auto viewMenu=[&](const QString &mode){
        if(!click(findVisualItem(content(),"bleeckerFileChooserViewOptions")))return false;
        auto item=findVisualItem(content()->window()->contentItem(),"bleeckerFileChooserView_"+mode);
        if(!check(item&&item->isVisible(),"Owned view menu item missing")||!click(item))return false;
        return check(browser()->property("viewMode").toString()==mode,"View menu did not change presentation");
    };
    auto listing=[&]{return qobject_cast<QAbstractItemModel*>(browser()->property("listing").value<QObject*>());};
    auto listingRow=[&](const QString &name){
        auto model=listing();if(!model)return -1;const auto role=model->roleNames().key("fileName",-1);
        for(int i=0;i<model->rowCount();++i)if(model->data(model->index(i,0),role).toString()==name)return i;
        return -1;
    };
    auto listedItem=[&](const QString &name){
        const auto index=listingRow(name);
        return findVisualItem(content(),(browser()->property("viewMode").toString()=="icons"?"bleeckerFileChooserIcon_":"bleeckerFileChooserListRow_")+QString::number(index));
    };
    if(!viewMenu("list")||!check(browser()->property("selectedUrls").toList().size()==1,"List did not retain the column file selection")||!save(content()->window(),"list-root-selection"))return;
    record("view-list-root-selection");
    const auto folderRow=listingRow("folder");
    if(!check(folderRow>=0,"List folder missing")||!click(findVisualItem(content(),"bleeckerFileChooserDisclosure_"+QString::number(folderRow)))
        ||!check(listingRow("child.txt")>=0,"List disclosure did not enumerate child rows")||!click(listedItem("child.txt")))return;
    QTest::keyPress(content()->window(),Qt::Key_Control);++keys;
    if(!click(listedItem("one.txt"),Qt::ControlModifier))return;
    QTest::keyRelease(content()->window(),Qt::Key_Control);++keys;
    if(!check(browser()->property("selectedUrls").toList().size()==2,"List selection did not span root and child")||!save(content()->window(),"list-root-and-child"))return;
    record("view-list-expanded-selection");
    if(!viewMenu("icons")||!check(listingRow("child.txt")==-1&&browser()->property("selectedUrls").toList().size()==1
        &&state()["results"].toArray().isEmpty(),"Icons did not prune the hidden child selection")||!save(content()->window(),"icons-root-retained"))return;
    record("view-icons-prunes-child");
    if(!click(listedItem("folder"))||!check(browser()->property("selectedUrls").toList().isEmpty()&&browser()->property("canAccept").toBool(),"Icons folder did not enable navigation Open")
        ||!click(findVisualItem(content(),"bleeckerFileChooserOpen"))||!check(browser()->property("folderPath").toString()==directory.filePath("folder")
        &&state()["results"].toArray().isEmpty()&&browser()->property("active").toBool(),"Icons folder Open submitted an owner result"))return;
    record("view-icons-folder-navigation");
    if(!click(findVisualItem(content(),"bleeckerFileChooserBack"))||!check(browser()->property("folderPath").toString()==root.path()
        &&browser()->property("selectedUrls").toList().isEmpty()&&!browser()->property("canAccept").toBool(),"View history retained file selection"))return;
    record("view-history-clears-selection");
    if(!viewMenu("list")||!check(listingRow("child.txt")>=0,"List did not retain disclosure state")||!click(listedItem("folder")))return;
    QTest::keyClick(content()->window(),Qt::Key_Left);++keys;QTest::qWait(40);
    if(!check(listingRow("child.txt")==-1,"List Left did not collapse"))return;
    QTest::keyClick(content()->window(),Qt::Key_Right);++keys;QTest::qWait(40);
    if(!check(listingRow("child.txt")>=0,"List Right did not expand"))return;
    QTest::keyClick(content()->window(),Qt::Key_Down);++keys;QTest::qWait(40);
    if(!check(browser()->property("selectedUrls").toList()==QVariantList{QUrl::fromLocalFile(directory.filePath("folder/child.txt"))},"List Down did not select the child")||!save(content()->window(),"list-keyboard-child"))return;
    record("view-list-keyboard-child");
    QTest::keyClick(content()->window(),Qt::Key_Return);++keys;QTest::qWait(40);
    if(!check(!browser()->property("active").toBool()&&state()["results"].toArray().size()==1,"List keyboard acceptance failed"))return;
    record("view-child-owner-result");
    if(!open()||!check(browser()->property("viewMode").toString()=="list"&&browser()->property("selectedUrls").toList().isEmpty()
        &&!browser()->property("canGoBack").toBool(),"Reopened List did not clear selection/history")||!click(findVisualItem(content(),"bleeckerFileChooserCancel")))return;
    record("view-retained-cancel");
    // The location menu is a separate owned popup window. Exercise its actual
    // items through the installed module, including a newly mounted consumer.
    auto visibleLocationEntry=[&](int index)->QQuickItem*{
        const auto name="bleeckerFileChooserLocation_"+QString::number(index);
        for(auto candidate:QGuiApplication::topLevelWindows())if(auto quick=qobject_cast<QQuickWindow*>(candidate);quick&&quick->isVisible())
            if(auto item=findVisualItem(quick->contentItem(),name);item&&item->isVisible())return item;
        return nullptr;
    };
    auto openLocations=[&]{
        if(!click(findVisualItem(content(),"bleeckerFileChooserLocation")))return false;
        QElapsedTimer timer;timer.start();while(timer.elapsed()<5000&&!visibleLocationEntry(0))QTest::qWait(10);
        const auto entry=visibleLocationEntry(0);
        return check(entry&&entry->window()&&QTest::qWaitForWindowExposed(entry->window(),5000)&&popupReady(entry->window()),"Location menu did not become exposed and stable");
    };
    auto placeEntries=[&]{auto places=browser()->property("places").value<QObject*>();return places?places->property("entries").toList():QVariantList{};};
    if(!configure(standard,QJsonArray{"text/plain"})||!open()||!selectRow(0,"folder")||!selectRow(1,"child.txt"))return;
    const auto selectedBeforeLocation=browser()->property("selectedUrls").toList();
    if(!openLocations()||!save(visibleLocationEntry(0)->window(),"location-current-menu")||!click(visibleLocationEntry(0))
        ||!check(browser()->property("selectedUrls").toList()==selectedBeforeLocation&&state()["results"].toArray().isEmpty(),"Current location changed file selection or called the owner"))return;
    record("location-current-keeps-selection");
    if(!openLocations()||!click(visibleLocationEntry(1))||!check(browser()->property("folderPath").toString()==root.path()
        &&browser()->property("selectedUrls").toList().isEmpty()&&state()["results"].toArray().isEmpty(),"Ancestor did not navigate with cleared selection")
        ||!click(findVisualItem(content(),"bleeckerFileChooserBack"))||!check(browser()->property("folderPath").toString()==directory.filePath("folder"),"Ancestor navigation did not enter history"))return;
    record("location-ancestor-clears-selection");
    if(!openLocations())return;QTest::keyClick(visibleLocationEntry(0)->window(),Qt::Key_Escape);++keys;QTest::qWait(40);
    if(!check(browser()->property("active").toBool()&&!visibleLocationEntry(0),"Location menu Escape closed the chooser or left the menu visible")||!openLocations())return;
    int recentRoot=-1;const auto placesBeforeNavigation=placeEntries();
    for(int i=0;i<placesBeforeNavigation.size();++i){const auto entry=placesBeforeNavigation[i].toMap();if(entry["recent"].toBool()&&entry["url"].toUrl()==QUrl::fromLocalFile(root.path())){recentRoot=i;break;}}
    if(!check(recentRoot>=0,"Successful containing folder missing from shared recent places")||!click(visibleLocationEntry(recentRoot))
        ||!check(browser()->property("folderPath").toString()==root.path()&&state()["results"].toArray().isEmpty(),"Recent-place navigation submitted an owner result"))return;
    record("location-recent-does-not-submit");
    if(!selectRow(0,"one.txt")||!click(findVisualItem(content(),"bleeckerFileChooserOpen"))||!check(state()["results"].toArray().size()==1,"Location flow acceptance failed"))return;
    fixture()->setProperty("mounted",false);if(!check(waitForShapeFrame(window),"Unmounted location consumer did not settle"))return;
    fixture()->setProperty("mounted",true);if(!check(waitForShapeFrame(window)&&control(),"New location consumer did not mount")||!open()||!openLocations())return;
    const auto persistedPlaces=placeEntries();QUrl firstRecent;
    for(const auto &value:persistedPlaces){const auto entry=value.toMap();if(entry["recent"].toBool()&&!entry["heading"].toBool()){firstRecent=entry["url"].toUrl();break;}}
    if(!check(firstRecent==QUrl::fromLocalFile(root.path()),"Fresh consumer did not load the last successful location")||!save(visibleLocationEntry(0)->window(),"location-recent-persisted"))return;
    QTest::keyClick(visibleLocationEntry(0)->window(),Qt::Key_Escape);++keys;QTest::qWait(40);
    if(!click(findVisualItem(content(),"bleeckerFileChooserCancel"))||!check(state()["results"].toArray().size()==1,"Location cancellation changed the owner"))return;
    record("location-history-owner-and-cancel");
    if(!configure(standard,QJsonArray{"text/plain"})||!open()||!selectRow(0,"folder")||!check(browser()->property("count").toInt()==2&&!browser()->property("canAccept").toBool(),"Directory navigation selected an ineligible directory")||!selectRow(1,"child.txt"))return;
    if(!save(content()->window(),"directory-columns"))return;
    record("child-selected");
    fixture()->setProperty("removeOnResult",true);QPointer<QObject> oldBrowser=browser(),oldChooser=chooser();
    if(!click(findVisualItem(content(),"bleeckerFileChooserOpen"))||!check(waitForShapeFrame(window),"Removed-owner frame missing"))return;
    if(!check(!control()&&oldBrowser.isNull()&&oldChooser.isNull()&&state()["results"].toArray().size()==1,"Callback removal left an owned chooser alive"))return;record("removed-in-result");
    if(!save(window,"removed-in-result"))return;
    QJsonObject report{{"accepted",false},{"reference",native["reference"]},{"fixture","file-input"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},
        {"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"width",window->width()},{"height",window->height()},
        {"popupCaptureMethod","QQuickItem::grabToImage of the entire popup window content item at native DPR; no cropping or resizing"},
        {"structuralChecks","passed"},{"images",44},{"closedImages",32},{"popupImages",11},{"ownerResultImages",1},
        {"appearance",parser.isSet("dark")?"dark":"light"},{"textScale",textScale},{"dpr",window->devicePixelRatio()},
        {"closed",closed},{"sizing",sizing},{"nativeCompleteFramesMatch",frames},{"nativeContractStatesMatch",states},
        {"applicationActive",QGuiApplication::applicationState()==Qt::ApplicationActive},{"windowActive",window->isActive()},
        {"observationOnly",parser.isSet("file-input-observe")},
        {"nativeRasterAcceptance","pending"},{"physicalInputAcceptance","pending"},{"readerAcceptance","pending"},{"nativeAccessibilityAcceptance","unobserved"},
        {"nativeFrameComparisonStatus",frames==32?"passed":"failed"},
        {"actions",actions},{"accessibility",accessibility},{"pointerEvents",pointers},{"keyEvents",keys},
        {"inputMethod","QTest actual owned controls; physical input and reader acceptance pending"}};
    if(parser.isSet("evidence")&&!check(window->grabWindow().save(prefix+".png"),"Session window capture failed"))return;
    if(!prefix.isEmpty()){QFile output(prefix+".json");if(!check(output.open(QIODevice::WriteOnly|QIODevice::NewOnly),"Report destination unavailable"))return;output.write(QJsonDocument(report).toJson());}
    if(!parser.isSet("file-input-observe")&&frames!=32){qCritical("FileInput native frame parity remains pending");app.exit(99);return;}
    qInfo("Installed FileInput: 32 native closed contexts, %lld owner/input traces; frames %d/32, states %d/32; acceptance pending",qlonglong(actions.size()),frames,states);
    if(parser.isSet("evidence")){
        auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,prefix]{if(QFile::exists(prefix+".captured"))app.exit(0);});timer->start(100);
        QTimer::singleShot(10000,&app,[&app]{app.exit(93);});return;
    }
    app.exit(0);
}

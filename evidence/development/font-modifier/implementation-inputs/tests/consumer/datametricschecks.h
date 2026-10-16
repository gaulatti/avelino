#pragma once
static void runDataMetricsConsumer(QQuickWindow *window,QGuiApplication &app,const QCommandLineParser &parser,double textScale,QQmlEngine &engine) {
    if(parser.isSet("format-diagnostics")) {
        QFile source(QStringLiteral(":/avelino/fixtures/native-metric-formatting.json"));if(!source.open(QIODevice::ReadOnly)){qCritical("Metric formatter source resource missing");app.exit(240);return;}
        const auto native=QJsonDocument::fromJson(source.readAll()).object();QJsonArray results;int matched=0;
        const auto tools=engine.singletonInstance<QObject*>(qmlTypeId("Avelino",0,1,"BleeckerNumberTools"));
        if(!tools){qCritical("Metric formatter singleton missing");app.exit(241);return;}
        for(const auto &v:native.value("cases").toArray()) {
            auto row=v.toObject();double value=0;
            if(row.contains("bits")) {
                static_assert(sizeof(double)==sizeof(quint64) && std::numeric_limits<double>::is_iec559);
                const auto input=row.value("bits").toString();bool valid=false;const quint64 bits=input.toULongLong(&valid,16);
                if(!valid||input.size()!=16){qCritical("Invalid native Double bits");app.exit(240);return;}
                std::memcpy(&value,&bits,sizeof(value));
            }else {
                const auto input=row.value("value").toString();bool valid=true;
                value=input=="nan" ? std::numeric_limits<double>::quiet_NaN():input=="infinity" ? std::numeric_limits<double>::infinity():input=="-infinity" ? -std::numeric_limits<double>::infinity():input.toDouble(&valid);
                if(!valid){qCritical("Invalid native Double description");app.exit(240);return;}
            }
            QString output;const bool invoked=QMetaObject::invokeMethod(tools,"format",Qt::DirectConnection,Q_RETURN_ARG(QString,output),Q_ARG(double,value),Q_ARG(QString,row.value("format").toString()),Q_ARG(QString,row.value("currencyCode").toString()),Q_ARG(QLocale,QLocale(row.value("processLocale").toString())),Q_ARG(bool,row.value("signedPercent").toBool()));
            if(!invoked){app.exit(242);return;}
            const bool equal=output==row.value("text").toString();matched+=equal;row.insert("candidate",output);row.insert("status",equal ? "passed":"failed; unaccepted");results.append(row);
        }
        QJsonObject record{{"reference",native.value("reference")},{"sourceFiles",native.value("sourceFiles")},{"groups",native.value("groups")},{"qt",qVersion()},{"cases",results.size()},{"matches",matched},{"mismatches",results.size()-matched},{"status",matched==results.size() ? "passed":"failed; unaccepted"},{"accepted",false},{"results",results}};
        QFile output(parser.value("format-diagnostics"));if(!output.open(QIODevice::WriteOnly)){app.exit(243);return;}output.write(QJsonDocument(record).toJson());output.close();app.exit(matched==results.size() ? 0:244);return;
    }
    auto item=[window](const QString &name){return findVisualItem(window->contentItem(),name);};
    auto check=[&app](bool ok,const char *message){if(!ok){qCritical("Installed data metrics: %s",message);app.exit(245);}return ok;};
    auto metric=item("consumerMetric"),card=item("consumerStatCard"),key=item("consumerKeyLabel"),field=item("metricsOutsideField"),button=item("metricsUpdateButton");
    if(!check(metric&&card&&key&&field&&button,"missing controls"))return;
    auto value=findVisualItem(metric,"bleeckerMetricValue"),label=findVisualItem(metric,"bleeckerMetricLabel"),delta=findVisualItem(card,"bleeckerStatCardDelta");
    auto ax=QAccessible::queryAccessibleInterface(value);
    if(!check(ax&&ax->role()==QAccessible::StaticText&&ax->text(QAccessible::Name)=="12,345.6789","actual metric text interface"))return;
    QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,field->mapToScene(QPointF(20,20)).toPoint());QTest::keyClick(window,Qt::Key_X);
    window->setProperty("metricLabel","Producer readers");window->setProperty("metricValue",1234.56789);window->setProperty("metricFormat","currency");window->setProperty("cardLocale","de_DE");QTest::qWait(40);
    if(!check(field->hasActiveFocus()&&field->property("text").toString()=="x"&&findVisualItem(metric,"bleeckerMetricValue")==value&&ax->text(QAccessible::Name)=="$1,234.57"&&delta->property("text").toString()==QString::fromUtf8("+12,345679 %"),"producer identity/focus and separate locale ownership"))return;
    window->setProperty("showDelta",false);if(!check(QTest::qWaitFor([&]{return !delta->isVisible()&&card->property("presentationItem").value<QQuickItem*>()->height()==94;},2000),"absent delta removes its gap after layout settles"))return;
    window->setProperty("showDelta",true);window->setProperty("cardDelta",0);QTest::qWait(20);if(!check(delta->property("text").toString()==QString::fromUtf8("+0 %"),"zero delta remains present"))return;
    QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,button->mapToScene(QPointF(button->width()/2,button->height()/2)).toPoint());QTest::qWait(40);
    if(!check(window->property("updates").toInt()==1&&metric->property("formattedValue").toString()=="12.345679%"&&key->property("key").toString()=="Enter"&&delta->property("text").toString()==QString::fromUtf8("-5 %"),"normal Qt update action"))return;
    auto rtl=item("consumerRtlStatCard"),row=findVisualItem(rtl,"bleeckerStatCardRow"),badge=findVisualItem(rtl,"bleeckerStatCardBadge"),rtlMetric=rtl->property("metricItem").value<QQuickItem*>();
    if(!check(row&&badge&&rtlMetric&&rtlMetric->x()>badge->parentItem()->x(),"RTL row order"))return;
    if(!check(item("consumerPrimaryBadge")->property("presentationItem").value<QQuickItem*>()->width()==36&&item("consumerOutlinedBadge")->property("presentationItem").value<QQuickItem*>()->width()==48,"fixed badge sizes"))return;
    auto keyAx=QAccessible::queryAccessibleInterface(findVisualItem(key,"bleeckerKbdKey"));if(!check(keyAx&&keyAx->role()==QAccessible::StaticText&&keyAx->text(QAccessible::Name)=="Enter","updated key accessibility"))return;
    QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,field->mapToScene(QPointF(20,20)).toPoint());QTest::keyClick(window,Qt::Key_Y);if(!check(field->property("text").toString()=="xy","continued editing"))return;
    qInfo("Installed data metrics: producer identity, formatting/locale ownership, optional/zero/signed delta, fixed badges, RTL, key updates, normal actions/editing and actual Qt accessibility passed");
    if(!parser.isSet("evidence")){app.exit(0);return;}
    const auto path=parser.value("evidence");if(!window->grabWindow().save(path+".png")){app.exit(246);return;}
    QJsonObject record{{"fixture","data-metrics"},{"qt",qVersion()},{"platform",QGuiApplication::platformName()},{"compiler",QString::fromUtf8(__VERSION__)},{"width",window->width()},{"height",window->height()},{"dpr",window->devicePixelRatio()},{"graphicsApi",int(window->rendererInterface()->graphicsApi())},{"requestedGraphicsBackend",qEnvironmentVariable("QSG_RHI_BACKEND")},{"quickBackend",qEnvironmentVariable("QT_QUICK_BACKEND")},{"appearance",parser.isSet("dark") ? "dark":"light"},{"textScale",textScale},{"inputMethod","QTest synthetic pointer/keyboard and actual Qt accessibility interfaces"},{"windowCaptureMethod","QQuickWindow::grabWindow; full output captured separately"},{"dataMetricsChecks","passed"},{"focusChecks","passed"},{"qtAccessibilityChecks","passed"},{"updates",1},{"formattedValue","12.345679%"},{"deltaLocale","de_DE"},{"acceptance","pending; fonts, symbols, locale/raster differences, animation, physical sessions and actual reader output"}};
    QFile file(path+".json");if(!file.open(QIODevice::WriteOnly)){app.exit(247);return;}file.write(QJsonDocument(record).toJson());file.close();
    auto timer=new QTimer(&app);QObject::connect(timer,&QTimer::timeout,&app,[&app,path]{if(QFile::exists(path+".captured"))app.exit(0);});timer->start(100);QTimer::singleShot(10000,&app,[&app]{app.exit(248);});
}

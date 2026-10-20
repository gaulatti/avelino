#include <QGuiApplication>
#include "apptabfixtures.h"
#include "commandspotlightfixtures.h"
#include "dropdownmenufixtures.h"
#include "fileinputfixtures.h"
#include "herocarouselfixtures.h"
#include <QLocale>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QQuickWindow>
#include <QTimer>
#include <QElapsedTimer>
#include <QCommandLineParser>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QMap>
#include <QFile>
#include <QDir>
#include <QSysInfo>
#include <QFont>
#include <QRawFont>
#include <QQuickItem>
#include <QJSValue>
#include <QMouseEvent>
#include <QTest>
#include <QSGRendererInterface>
#include <cmath>

static QQuickItem *findVisual(QQuickItem *root, const QString &name) {
    if (root->objectName() == name) return root;
    for (auto child : root->childItems()) if (auto found = findVisual(child, name)) return found;
    return nullptr;
}

static void recordLabels(QQuickItem *root, QJsonArray &labels) {
    const auto fontProperty = root->property("font");
    if (root->isVisible() && fontProperty.isValid() && root->property("text").isValid()) {
        const auto font = fontProperty.value<QFont>();
        const auto raw = QRawFont::fromFont(font);
        // Qt 6.8.3 can return a nominally valid placeholder with pixelSize -1
        // for a subpixel request; familyName() then dereferences an empty list.
        const bool validRawFont=raw.isValid() && raw.pixelSize()>0;
        const bool rendererReportsFont=root->property("resolvedFamily").isValid();
        const QJsonValue family=validRawFont ? QJsonValue(raw.familyName()):rendererReportsFont ? QJsonValue(root->property("resolvedFamily").toString()):QJsonValue(QJsonValue::Null);
        const QJsonValue style=validRawFont ? QJsonValue(raw.styleName()):rendererReportsFont ? QJsonValue(root->property("resolvedStyle").toString()):QJsonValue(QJsonValue::Null);
        const auto position = root->mapToScene(QPointF(0, 0));
        QJsonObject record{{"role", root->objectName()}, {"text", root->property("text").toString()},
            {"family", family}, {"style", style}, {"weight", int(font.weight())},
            {"requestedPointSize", font.pointSizeF()}, {"requestedPixelSize", font.pixelSize()},
            {"width", root->width()}, {"height", root->height()}, {"x", position.x()}, {"y", position.y()},
            {"sceneBaseline", root->mapToScene(QPointF(0, root->baselineOffset())).y()}};
        if(!validRawFont) {
            record.insert("fontResolutionStatus",rendererReportsFont ? "renderer-reported":"unavailable; template does not render its text");
            record.insert("requestedFontFamily",font.family());
        }
        if (root->property("resolvedPixelSize").isValid()) {
            record.insert("requestedLogicalPixelSize",root->property("logicalPixelSize").toDouble());
            record.insert("resolvedGlyphPixelSize",root->property("resolvedPixelSize").toDouble());
            record.insert("glyphAdvance",root->property("glyphAdvance").toDouble());
        }
        labels.append(record);
    }
    for (auto child : root->childItems()) recordLabels(child, labels);
}

#include "../../tests/consumer/buttonstyleframes.h"
#include "../../tests/consumer/fontmodifierframes.h"
#include "../../tests/consumer/surfacemodifierframes.h"
#include "../../tests/consumer/renderframe.h"
int main(int argc, char *argv[]) {
    QGuiApplication app(argc, argv);
    QCommandLineParser parser;
    parser.addHelpOption();
    parser.addOptions({QCommandLineOption("capture", "Save the displayed fixture to PNG and exit", "path"),
                       QCommandLineOption("dark", "Use dark reference appearance"),
                       QCommandLineOption("fixture", "Render a fixture (button, foundations, surfaces, data-display, controls, composition, selection, checkbox, secure-field, search-field, collection-filters, slider, tabs, pagination, pagination-integers, accordion, presentation-states, spinner, alert, clipping, navigation, sidebar-brand, data-metrics, stepper, radio-group, otp-input, activity-item, modal, tooltip, button-style, font-modifier, surface-modifier, pill-modifier, charts, date-range, hero-carousel, media-library, app-tabs, mobile-shell, command-spotlight, dropdown-menu, file-input or reference-case)", "name"),
                       QCommandLineOption("case", "Isolated reference fixture identifier", "id"),
                       QCommandLineOption("file-input-folder", "Initial absolute folder for the FileInput gallery", "path"),
                       QCommandLineOption("case-definitions", "JSON file containing the isolated fixture definitions", "path"),
                       QCommandLineOption("variant", "Button variant", "name", "primary"),
                       QCommandLineOption("size", "Button size", "name", "md"),
                       QCommandLineOption("disabled", "Disable the fixture control"),
                       QCommandLineOption("text-scale", "Use a positive logical text scale", "factor", "1")});
    parser.process(app);
    bool validScale = false;
    const qreal textScale = parser.value("text-scale").toDouble(&validScale);
    if (!validScale || !std::isfinite(textScale) || textScale <= 0) return 5;
    const auto fixture = parser.value("fixture");
    const bool isolated = fixture == "reference-case";
    QJsonObject definition;
    if (isolated) {
        if (!parser.isSet("case") || !parser.isSet("case-definitions")) return 6;
        QFile file(parser.value("case-definitions"));
        if (!file.open(QIODevice::ReadOnly)) return 6;
        QJsonParseError error;
        const auto definitions = QJsonDocument::fromJson(file.readAll(), &error).object().value("fixtures").toArray();
        if (error.error != QJsonParseError::NoError) return 6;
        int matches = 0;
        for (const auto &value : definitions) {
            const auto entry = value.toObject();
            if (entry.value("fixture").toString() == parser.value("case")) { definition = entry; ++matches; }
        }
        if (matches != 1 || definition.value("width").toDouble() <= 0 || definition.value("height").toDouble() <= 0) return 6;
        if(definition["api"]=="BleeckerButtonGroup" && definition.contains("expectedEmpty")
            && !definition["expectedEmpty"].isBool())return 6;
        if(definition["api"]=="BleeckerDropdownMenu"&&!validDropdownMenuFixture(definition))return 6;
        if(definition["api"]=="BleeckerFileInput"&&!validFileInputFixture(definition))return 6;
        if(definition["api"]=="BleeckerHeroCarousel"&&!validHeroCarouselFixture(definition))return 6;
        if(definition["api"]=="BleeckerCommandSpotlight"&&!validCommandSpotlightFixture(definition))return 6;
        if(definition["api"]=="BleeckerAppTabBar"&&!validAppTabFixture(definition))return 6;
        if(definition.value("api").toString()=="BleeckerMediaLibrary") {
            const auto numeric=[](QJsonValue value){return (value.isDouble()&&std::isfinite(value.toDouble())) ||QStringList{"__native_nan__","__native_positive_infinity__","__native_negative_infinity__"}.contains(value.toString());};
            const auto nonnegative=[](QJsonValue value){return value.isDouble()&&std::isfinite(value.toDouble())&&value.toDouble()>=0;};
            if(definition.keys()!=QStringList{"api","disabled","fixture","height","id","items","libraryHeight","libraryWidth","minimumTileWidth","parentFont","parentRed","rtl","scroll","slot","source","width"}
                ||definition.value("source").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9"
                ||!definition.value("id").isString()||definition.value("id").toString().isEmpty()
                ||definition.value("fixture").toString()!="media-"+definition.value("id").toString()
                ||!definition.value("items").isArray()||!numeric(definition.value("libraryWidth"))
                ||(!definition.value("libraryHeight").isNull()&&!numeric(definition.value("libraryHeight")))
                ||!numeric(definition.value("minimumTileWidth"))
                ||!QStringList{"fill","fixed","text","button"}.contains(definition.value("slot").toString())
                ||!definition.value("disabled").isBool()||!definition.value("parentFont").isBool()||!definition.value("parentRed").isBool()||!definition.value("rtl").isBool()||!definition.value("scroll").isBool()
                ||definition.value("width").toDouble()!=640||definition.value("height").toDouble()!=400)return 6;
            for(const auto &value:definition.value("items").toArray()) {
                if(!value.isObject())return 6;const auto item=value.toObject();
                const auto color=item["color"].toDouble(-1);
                if(item.keys()!=QStringList{"color","height","id","title","width"}||!item["id"].isString()||!item["title"].isString()
                    ||!nonnegative(item["width"])||!nonnegative(item["height"])||!item["color"].isDouble()||color<0||color>3||std::floor(color)!=color)return 6;
            }
        }
        const QMap<QString,QString> chartApis{{"BleeckerLineChart","line"},{"BleeckerBarChart","bar"},{"BleeckerPieChart","pie"},{"BleeckerScatterChart","scatter"},{"BleeckerSparkline","sparkline"}};
        if(chartApis.contains(definition.value("api").toString())) {
            const auto numeric=[](QJsonValue value){return (value.isDouble()&&std::isfinite(value.toDouble())) ||QStringList{"__native_nan__","__native_positive_infinity__","__native_negative_infinity__"}.contains(value.toString());};
            if(definition.keys()!=QStringList{"api","area","chartHeight","chartWidth","disabled","fixture","height","id","innerRadius","kind","parentFont","parentRed","points","rtl","source","values","width"}
                ||definition.value("source").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9"
                ||definition.value("kind").toString()!=chartApis[definition.value("api").toString()]
                ||!definition.value("id").isString()||definition.value("id").toString().isEmpty()
                ||definition.value("fixture").toString()!="chart-"+definition.value("id").toString()
                ||!definition.value("points").isArray() ||!definition.value("values").isArray()
                ||!definition.value("area").isBool() ||!definition.value("disabled").isBool() ||!definition.value("parentFont").isBool() ||!definition.value("parentRed").isBool() ||!definition.value("rtl").isBool()
                ||!numeric(definition.value("innerRadius")) ||definition.value("width").toDouble()!=640 ||definition.value("height").toDouble()!=400)return 6;
            for(const auto *key:{"chartWidth","chartHeight"})if(!definition.value(key).isDouble()||!std::isfinite(definition.value(key).toDouble())||definition.value(key).toDouble()<0)return 6;
            for(const auto &point:definition.value("points").toArray()) {
                if(!point.isObject())return 6;const auto row=point.toObject();
                if(row.keys()!=QStringList{"id","label","series","x","y"}||!row["id"].isString()||!row["label"].isString()||!row["series"].isString()||!numeric(row["x"])||!numeric(row["y"]))return 6;
            }
            for(const auto &value:definition.value("values").toArray())if(!numeric(value))return 6;
        }
        if(definition.value("api").toString()=="Text.bleeckerPill") {
            const auto finite=[](QJsonValue value){return value.isDouble() && std::isfinite(value.toDouble());};
            const auto offer=definition.value("offer"),lines=definition.value("lineLimit");
            if(definition.keys()!=QStringList{"api","disabled","fixture","height","hidden","id","lineLimit","offer","parentFont","parentLayout","parentRed","rtl","source","style","text","width"}
                || definition.value("source").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9"
                || !definition.value("fixture").toString().startsWith("pill-")
                || definition.value("fixture").toString()!="pill-"+definition.value("id").toString()
                || !definition.value("text").isString()
                || (!offer.isNull() && (!finite(offer) || offer.toDouble()<0))
                || (!lines.isNull() && (!finite(lines) || lines.toDouble()<1 || lines.toDouble()>2147483647 || std::floor(lines.toDouble())!=lines.toDouble()))
                || !QStringList{"plain","primary19","secondary19","mono3","mono32","system32","red","style-red","bold","italic","underline","strike","tracking","kerning","baseline5","concat","attributed","markdown","image","image-text"}.contains(definition.value("style").toString())
                || !QStringList{"center","hstack","vstack","baseline"}.contains(definition.value("parentLayout").toString())
                || !definition.value("parentFont").isBool() || !definition.value("parentRed").isBool() || !definition.value("rtl").isBool()
                || !definition.value("hidden").isBool() || !definition.value("disabled").isBool()
                || definition.value("width").toDouble()!=640 || definition.value("height").toDouble()!=400)return 6;
        }
        if(definition.value("api").toString()=="BleeckerSurfaceModifier") {
            const auto finite=[](QJsonValue value){return value.isDouble() && std::isfinite(value.toDouble());};
            const auto radius=definition.value("radius"),offer=definition.value("offer");
            if(definition.keys()!=QStringList{"api","content","expectedEmpty","fixture","height","offer","parentFont","parentLayout","parentRed","radius","resolvedRadius","rtl","source","text","width"}
                || definition.value("source").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9"
                || !definition.value("fixture").toString().startsWith("surface-")
                || (!radius.isNull() && !finite(radius)) || !finite(definition.value("resolvedRadius"))
                || definition.value("resolvedRadius").toDouble()!=(radius.isNull() ? 12:radius.toDouble())
                || (!offer.isNull() && (!finite(offer) || offer.toDouble()<0))
                || !QStringList{"clear","rectangle","fractional","opaque","overflow","hidden","empty","zero","wide","text","own-font","system-font","red","button","multi","hstack","vstack"}.contains(definition.value("content").toString())
                || !QStringList{"zstack","hstack","vstack"}.contains(definition.value("parentLayout").toString())
                || !definition.value("parentFont").isBool() || !definition.value("parentRed").isBool() || !definition.value("rtl").isBool()
                || !definition.value("text").isString() || !definition.value("expectedEmpty").isBool()
                || definition.value("expectedEmpty").toBool()!=(definition.value("content").toString()=="empty")
                || definition.value("width").toDouble()!=640 || definition.value("height").toDouble()!=400)return 6;
        }
        if(definition.value("api").toString()=="View.bleeckerFont") {
            if(definition.keys()!=QStringList{"api","baselineParent","content","expectedEmpty","family","fixture","height","offer","outerFontModifier","outerSystem","parentFont","parentLayout","rtl","size","source","text","weight","width"}
                || definition.value("source").toString()!="fe8a1d462fbd793d883fb92086a16aa2947e32c9")return 6;
            const auto finite=[](QJsonValue value){return value.isDouble() && std::isfinite(value.toDouble());};
            const auto offer=definition.value("offer");
            if(!QStringList{"primary","secondary","mono"}.contains(definition.value("family").toString())
                || !QStringList{"ultraLight","thin","light","regular","medium","semibold","bold","heavy","black"}.contains(definition.value("weight").toString())
                || !finite(definition.value("size")) || (!offer.isNull() && (!finite(offer) || offer.toDouble()<0))
                || !QStringList{"text","empty-view","zero","rectangle","hidden","own-font","system-font","nil-font","red","bold","italic","attributed","nested-font","scaled-subtree","inner-scale","multi","vstack","hstack"}.contains(definition.value("content").toString())
                || !QStringList{"zstack","hstack","vstack"}.contains(definition.value("parentLayout").toString())
                || !definition.value("text").isString() || !definition.value("parentFont").isBool()
                || !definition.value("outerSystem").isBool() || !definition.value("outerFontModifier").isBool()
                || !definition.value("rtl").isBool() || !definition.value("baselineParent").isBool()
                || !definition.value("expectedEmpty").isBool()
                || definition.value("expectedEmpty").toBool()!=(definition.value("content").toString()=="empty-view")
                || definition.value("width").toDouble()!=640 || definition.value("height").toDouble()!=400)return 6;
        }
        if(definition.value("api").toString()=="BleeckerButtonStyle") {
            const auto nonnegative=[](QJsonValue value){return value.isDouble() && std::isfinite(value.toDouble()) && value.toDouble()>=0;};
            const auto offer=definition.value("offer");
            if(!offer.isNull() && !nonnegative(offer))return 6;
            if(!QStringList{"primary","secondary","outline","subtle","ghost","link","destructive"}.contains(definition.value("variant").toString())
                || !QStringList{"xs","sm","md","lg"}.contains(definition.value("size").toString())
                || !QStringList{"text","counter","rectangle","zero","empty","hidden","wide","own-font","system-font","own-red","multi","vstack","hstack","overflow"}.contains(definition.value("content").toString())
                || !QStringList{"zstack","hstack","vstack"}.contains(definition.value("parentLayout").toString())
                || !definition.value("text").isString() || !nonnegative(definition.value("parentFont"))
                || !definition.value("disabled").isBool() || !definition.value("rtl").isBool()
                || !definition.value("parentRed").isBool() || !definition.value("destructiveRole").isBool()
                || !definition.value("expectedEmpty").isBool()
                || definition.value("expectedEmpty").toBool()!=(definition.value("content").toString()=="empty")
                || definition.value("width").toInt()!=640 || definition.value("height").toInt()!=400)return 6;
        }
        if(definition.value("api").toString()=="BleeckerTooltip") {
            const auto font=definition.value("parentFont");
            const auto content=definition.value("content").toString();
            if(!definition.value("hint").isString() || !definition.value("disabled").isBool() || !definition.value("rtl").isBool()
                || !definition.value("parentRed").isBool() || !font.isDouble() || !std::isfinite(font.toDouble()) || font.toDouble()<0
                || !definition.value("helpAttached").isBool() || !definition.value("expectedEmpty").isBool()
                || definition.value("expectedEmpty").toBool()!=QStringList{"empty","zero","hidden"}.contains(content)
                || !QStringList{"button","rectangle","zero","empty","hidden","wide","text","inherited","multi","vstack","hstack","wide-button"}.contains(content))return 6;
        }
        if(definition.value("api").toString()=="BleeckerModal") {
            const auto width=definition.value("modalWidth"),offer=definition.value("outerOffer");
            const auto nonnegative=[](QJsonValue value){return value.isDouble() && std::isfinite(value.toDouble()) && value.toDouble()>=0;};
            if(!nonnegative(width) || (!offer.isNull() && !nonnegative(offer))
                || !definition.value("expectedEmpty").isBool() || definition.value("expectedEmpty").toBool()!=(width.toDouble()==0)
                || !definition.value("title").isString() || !definition.value("disabled").isBool() || !definition.value("rtl").isBool()
                || !definition.value("parentRed").isBool() || !nonnegative(definition.value("parentFont"))
                || !QStringList{"rectangle","empty","zero","hidden","tall","wide","fills","text","text-empty","text-lines","inherited","multi","vstack","hstack","counter","editor","wide-button"}.contains(definition.value("content").toString()))return 6;
        }
    } else if (parser.isSet("case") || parser.isSet("case-definitions")) return 6;
    QQmlApplicationEngine engine;
    installAppTabFixtureMetrics(engine);
    engine.addImportPath(QDir(QCoreApplication::applicationDirPath()).filePath(
        QStringLiteral(AVELINO_QML_IMPORT_FROM_BIN)));
    engine.rootContext()->setContextProperty("captureDark", parser.isSet("dark"));
    engine.rootContext()->setContextProperty("captureVariant", parser.value("variant"));
    engine.rootContext()->setContextProperty("captureSize", parser.value("size"));
    engine.rootContext()->setContextProperty("captureDisabled", parser.isSet("disabled"));
    engine.rootContext()->setContextProperty("captureTextScale", textScale);
    if(fixture=="file-input" || (isolated&&definition["api"]=="BleeckerFileInput") || fixture=="button-style" || fixture=="stepper" || fixture=="data-metrics")QLocale::setDefault(QLocale("en_US"));
    if(isolated && definition.contains("processLocale"))QLocale::setDefault(QLocale(definition.value("processLocale").toString()));
    engine.rootContext()->setContextProperty("captureDefinition", definition.toVariantMap());
    engine.rootContext()->setContextProperty("fileInputFolder",parser.isSet("file-input-folder") ? QUrl::fromLocalFile(parser.value("file-input-folder")):QUrl());
    QObject::connect(&engine, &QQmlApplicationEngine::objectCreationFailed, &app, [] { QCoreApplication::exit(1); }, Qt::QueuedConnection);
    if (parser.isSet("fixture") && fixture != "button" && fixture != "foundations" && fixture != "surfaces" && fixture != "data-display" && fixture != "controls" && fixture != "composition" && fixture != "selection" && fixture != "checkbox" && fixture != "secure-field" && fixture != "search-field" && fixture != "collection-filters" && fixture != "slider" && fixture != "tabs" && fixture != "pagination" && fixture != "pagination-integers" && fixture != "accordion" && fixture != "presentation-states" && fixture != "spinner" && fixture != "alert" && fixture != "clipping" && fixture != "navigation" && fixture != "sidebar-brand" && fixture != "data-metrics" && fixture != "stepper" && fixture != "radio-group" && fixture != "otp-input" && fixture != "activity-item" && fixture != "modal" && fixture != "tooltip" && fixture != "button-style" && fixture != "font-modifier" && fixture != "surface-modifier" && fixture != "pill-modifier" && fixture != "charts" && fixture != "date-range" && fixture != "hero-carousel" && fixture != "media-library" && fixture != "mobile-shell" && fixture != "app-tabs" && fixture != "command-spotlight" && fixture != "dropdown-menu" && fixture != "file-input" && !isolated) return 4;
    engine.loadFromModule("AvelinoCatalog", isolated ? "ReferenceCaseFixture" : fixture == "mobile-shell" ? "MobileShell" : fixture == "date-range" ? "DateRangePicker" : fixture == "hero-carousel" ? "HeroCarousel" : fixture == "file-input" ? "FileInput" : fixture == "dropdown-menu" ? "DropdownMenu" : fixture == "command-spotlight" ? "CommandSpotlight" : fixture == "app-tabs" ? "AppTabs" : fixture == "media-library" ? "MediaLibrary" : fixture == "charts" ? "Charts" : fixture == "pill-modifier" ? "PillModifier" : fixture == "surface-modifier" ? "SurfaceModifier" : fixture == "font-modifier" ? "FontModifier" : fixture == "button-style" ? "ButtonStyle" : fixture == "tooltip" ? "Tooltip" : fixture == "modal" ? "Modal" : fixture == "activity-item" ? "ActivityItem" : fixture == "otp-input" ? "OTPInput" : fixture == "radio-group" ? "RadioGroup" : fixture == "stepper" ? "Stepper" : fixture == "data-metrics" ? "DataMetrics" : fixture == "sidebar-brand" ? "SidebarBrand" : fixture == "navigation" ? "Navigation" : fixture == "clipping" ? "Clipping" : fixture == "alert" ? "AlertFixture" : fixture == "spinner" ? "SpinnerFixture" : fixture == "presentation-states" ? "PresentationStatesFixture" : fixture == "accordion" ? "AccordionFixture" : fixture == "pagination-integers" ? "PaginationIntegerFixture" : fixture == "pagination" ? "PaginationFixture" : fixture == "tabs" ? "TabsFixture" : fixture == "slider" ? "SliderFixture" : fixture == "collection-filters" ? "CollectionFiltersFixture" : fixture == "search-field" ? "SearchFieldFixture" : fixture == "secure-field" ? "SecureFieldFixture" : fixture == "checkbox" ? "CheckboxFixture" : fixture == "selection" ? "SelectionFixture" : fixture == "composition" ? "CompositionFixture" : fixture == "controls" ? "ControlsFixture" : fixture == "data-display" ? "DataDisplayFixture" : fixture == "surfaces" ? "SurfacesFixture" : fixture == "foundations" ? "FoundationsFixture"
        : fixture == "button" ? "ButtonFixture" : "Main");
    if (parser.isSet("capture")) {
        const auto path = parser.value("capture");
        if (isolated && definition.value("fixture").toString().startsWith("search-") && definition.value("variant").toString()=="cleared") {
            QTimer::singleShot(150,&app,[&engine,&app] {
                const auto window=qobject_cast<QQuickWindow *>(engine.rootObjects().value(0));
                const auto field=window ? findVisual(window->contentItem(),"referenceCaseComponent") : nullptr;
                const auto action=field ? findVisual(field,"bleeckerSearchClear") : nullptr;
                if (!action || !QMetaObject::invokeMethod(action,"click") || !field->property("text").toString().isEmpty()) { app.exit(10); return; }
                // Native proposal captures are defocused after the action.
                // Interactive consumers separately verify restored editing focus.
                field->setFocus(false);
            });
        }
        if (isolated && (definition.value("api").toString()=="BleeckerIconButton" || definition.value("api").toString()=="BleeckerPagination")) {
            QTimer::singleShot(150,&app,[&engine,&app,definition] {
                const auto window=qobject_cast<QQuickWindow *>(engine.rootObjects().value(0));
                const auto component=window ? findVisual(window->contentItem(),"referenceCaseComponent") : nullptr;
                if (!component) {app.exit(15);return;}
                const auto fixture=definition.value("fixture").toString(),variant=definition.value("variant").toString();
                QQuickItem *input=nullptr;
                if (definition.value("api").toString()=="BleeckerIconButton" && (fixture.endsWith("-clicked") || fixture.endsWith("-disabled-click") || fixture.endsWith("-pressed")))
                    input=component->property("inputItem").value<QQuickItem*>();
                if (definition.value("api").toString()=="BleeckerPagination" && (fixture.startsWith("pagination-action-") || fixture.startsWith("pagination-i64-action-"))) {
                    const bool previous=(QStringList{"previous","lower-bound","above-last-prev"}.contains(variant) || variant.startsWith("previous-"));
                    const auto button=findVisual(component,previous ? "bleeckerPreviousPage" : "bleeckerNextPage");
                    input=button ? button->property("inputItem").value<QQuickItem*>() : nullptr;
                    if (!input) {app.exit(15);return;}
                }
                if (input) {
                    if (fixture.endsWith("-pressed")) {
                        const auto point=input->mapToScene(QPointF(input->width()/2,input->height()/2));
                        QTest::mousePress(window,Qt::LeftButton,Qt::NoModifier,point.toPoint());
                        if (!input->property("down").toBool()) {app.exit(15);return;}
                    } else if (!QMetaObject::invokeMethod(input,"click")) {app.exit(15);return;}
                    if (variant=="external") {
                        if (fixture.startsWith("pagination-i64-")) window->setProperty("integerPage",QStringLiteral("9223372036854775805"));
                        else window->setProperty("pageValue",7);
                    }
                    if (variant=="shrink-count") {
                        if (fixture.startsWith("pagination-i64-")) window->setProperty("integerCount",QStringLiteral("-9223372036854775808"));
                        else window->setProperty("pageTotal",3);
                    }
                    if (!fixture.endsWith("-pressed")) input->setFocus(false);
                }
            });
        }
        if (isolated && definition.value("api").toString()=="BleeckerAccordion" && definition.value("fixture").toString().startsWith("accordion-action-")) {
            QTimer::singleShot(150,&app,[&engine,&app,definition] {
                const auto window=qobject_cast<QQuickWindow *>(engine.rootObjects().value(0));
                const auto component=window ? findVisual(window->contentItem(),"referenceCaseComponent") : nullptr;
                const auto input=component ? component->property("inputItem").value<QQuickItem*>() : nullptr;
                if(!input){app.exit(17);return;}
                const auto action=definition.value("variant").toString();
                const auto point=[component,input](const QString &kind) {
                    auto target=findVisual(component,kind=="glyph" ? "bleeckerAccordionChevron":"bleeckerAccordionTitle");
                    return kind=="spacer" ? input->mapToScene(QPointF(input->width()/2,7)) : target->mapToScene(QPointF(kind=="glyph" ? target->width()/2:5,target->height()/2));
                };
                const auto click=[window](const QPointF &position){QTest::mouseClick(window,Qt::LeftButton,Qt::NoModifier,position.toPoint());};
                if(action=="initial-update") component->setProperty("initiallyExpanded",true);
                else if(action=="body-update") window->setProperty("accordionBodyText",QStringLiteral("Updated body copy"));
                else if(action=="retitle" || action=="reopen") {
                    const auto counter=findVisual(component,"referenceAccordionCounter");
                    if(!counter){app.exit(17);return;}
                    click(counter->mapToScene(QPointF(counter->width()/2,counter->height()/2)));
                    if(action=="retitle") window->setProperty("accordionTitle",QStringLiteral("Updated title"));
                    else {click(point("title"));QCoreApplication::processEvents();click(point("title"));}
                } else if(action=="pressed") {
                    QTest::mousePress(window,Qt::LeftButton,Qt::NoModifier,point("title").toPoint());
                    if(!input->property("down").toBool()){app.exit(17);return;}
                } else if(action=="outside-release") {
                    const auto start=point("title"),end=input->mapToScene(QPointF(input->width()+30,7));
                    QTest::mousePress(window,Qt::LeftButton,Qt::NoModifier,start.toPoint());QTest::mouseMove(window,end.toPoint());QTest::mouseRelease(window,Qt::LeftButton,Qt::NoModifier,end.toPoint());
                } else click(point(action=="open-spacer" ? "spacer":action=="open-glyph" ? "glyph":"title"));
                if(action!="pressed") input->setFocus(false);
            });
        }
        if (isolated && (definition.value("api").toString()=="BleeckerTabs" || definition.value("fixture").toString().startsWith("segments-bound-"))) {
            QTimer::singleShot(150,&app,[&engine,&app,definition] {
                const auto window=qobject_cast<QQuickWindow *>(engine.rootObjects().value(0));
                const auto body=window ? findVisual(window->contentItem(),"bleeckerBoundSelectionBody") : nullptr;
                if (!body) { app.exit(14);return; }
                const auto variant=definition.value("variant").toString();
                if (QStringList{"activated","reselected","disabled-click","disabled-group-action","external"}.contains(variant)) {
                    const auto button=findVisual(body,variant=="disabled-click" ? "bleeckerSegment1" : "bleeckerSegment2");
                    if (!button) {app.exit(14);return;}
                    if (!QMetaObject::invokeMethod(button,"click")) {app.exit(14);return;}
                    if (variant=="external") window->setProperty("boundSelection",QStringLiteral("a"));
                    const bool rejected=variant=="disabled-click" || variant=="disabled-group-action";
                    const auto expected=(rejected || variant=="external") ? QStringLiteral("a") : QStringLiteral("c");
                    if (body->property("selection").toString()!=expected || window->property("boundActivations").toInt()!=int(!rejected)) {app.exit(14);return;}
                    button->setFocus(false);
                }
            });
        }
        if (isolated && definition.value("api").toString()=="BleeckerSlider") {
            QTimer::singleShot(150,&app,[&engine,&app,definition] {
                const auto window=qobject_cast<QQuickWindow *>(engine.rootObjects().value(0));
                const auto slider=window ? findVisual(window->contentItem(),"referenceCaseComponent") : nullptr;
                if (!slider) { app.exit(13);return; }
                const auto variant=definition.value("variant").toString();
                if (variant.startsWith("clicked-")) {
                    const auto point=slider->mapToScene(QPointF(variant.endsWith("upper") ? slider->width()-1 : 1,slider->height()/2));
                    const auto global=QPointF(window->mapToGlobal(point.toPoint()));
                    QMouseEvent down(QEvent::MouseButtonPress,point,global,Qt::LeftButton,Qt::LeftButton,Qt::NoModifier);
                    QMouseEvent up(QEvent::MouseButtonRelease,point,global,Qt::LeftButton,Qt::NoButton,Qt::NoModifier);
                    QCoreApplication::sendEvent(window,&down);QCoreApplication::sendEvent(window,&up);
                }
                if (variant=="dragged") {
                    const auto start=slider->mapToScene(QPointF(10+0.35*(slider->width()-20),8));
                    const auto end=slider->mapToScene(QPointF(10+0.75*(slider->width()-20),8));
                    QMouseEvent down(QEvent::MouseButtonPress,start,QPointF(window->mapToGlobal(start.toPoint())),Qt::LeftButton,Qt::LeftButton,Qt::NoModifier);
                    QMouseEvent move(QEvent::MouseMove,end,QPointF(window->mapToGlobal(end.toPoint())),Qt::NoButton,Qt::LeftButton,Qt::NoModifier);
                    QMouseEvent up(QEvent::MouseButtonRelease,end,QPointF(window->mapToGlobal(end.toPoint())),Qt::LeftButton,Qt::NoButton,Qt::NoModifier);
                    QCoreApplication::sendEvent(window,&down);QCoreApplication::sendEvent(window,&move);QCoreApplication::sendEvent(window,&up);
                }
                if (variant=="external") window->setProperty("sliderValue",0.8);
                slider->setFocus(false);
            });
        }
        if (isolated && definition.value("api").toString()=="BleeckerCollectionFilters") {
            QTimer::singleShot(150, &app, [&engine,&app,definition] {
                const auto window=qobject_cast<QQuickWindow *>(engine.rootObjects().value(0));
                const auto filters=window ? findVisual(window->contentItem(),"referenceCaseComponent") : nullptr;
                const auto variant=definition.value("variant").toString();
                const QString actionName=variant=="cleared" ? "bleeckerSearchClear" : variant=="removed" ? "bleeckerFilterRemove" : variant=="activated" ? "bleeckerFilterAction" : "";
                if (!actionName.isEmpty()) {
                    const auto action=filters ? findVisual(filters,actionName) : nullptr;
                    if (!action || !QMetaObject::invokeMethod(action,"click")) { app.exit(12); return; }
                }
                if (filters) if (const auto search=findVisual(filters,"bleeckerCollectionSearch")) search->setFocus(false);
            });
        }
        if (fixture == "secure-field" || (isolated && definition.value("api").toString()=="BleeckerSecureField"
            && definition.value("variant").toString().startsWith("revealed-"))) {
            QTimer::singleShot(150, &app, [&engine,&app,isolated] {
                const auto window=qobject_cast<QQuickWindow *>(engine.rootObjects().value(0));
                const auto field=window ? findVisual(window->contentItem(),isolated ? "referenceCaseComponent" : "galleryRevealedField") : nullptr;
                const auto action=field ? findVisual(field,"bleeckerSecureReveal") : nullptr;
                if (!action || !QMetaObject::invokeMethod(action,"click") || !field->property("revealed").toBool()) app.exit(9);
            });
        }
        QTimer::singleShot(700, &app, [&engine, &app, &parser, path, isolated, definition] {
            const auto window = qobject_cast<QQuickWindow *>(engine.rootObjects().value(0));
            if (!window) { app.exit(2); return; }
            const auto component = isolated ? findVisual(window->contentItem(), "referenceCaseComponent") : nullptr;
            const bool expectedEmpty = definition.value("expectedEmpty").toBool();
            QObject *selectorPopup=nullptr;
            QQuickItem *selectorPopupContent=nullptr;
            if (parser.value("fixture")=="selection") {
                const auto selector=findVisual(window->contentItem(),"selectorCandidate");
                if (selector) selectorPopup=selector->property("popup").value<QObject*>();
                if (selectorPopup) selectorPopupContent=selectorPopup->property("contentItem").value<QQuickItem*>();
                if (!selectorPopup || !selectorPopupContent || !selectorPopup->property("visible").toBool()
                    || selectorPopup->property("popupType").toInt()!=0) { app.exit(7); return; }
            }
            const bool openSelector=isolated && definition.value("api").toString()=="BleeckerSelect"
                && definition.value("variant").toString().startsWith("open-");
            if (openSelector && component) {
                selectorPopup=component->property("popup").value<QObject*>();
                if (selectorPopup) selectorPopupContent=selectorPopup->property("contentItem").value<QQuickItem*>();
                if (!selectorPopup || !selectorPopupContent || !selectorPopup->property("visible").toBool()
                    || selectorPopup->property("popupType").toInt()!=0) { app.exit(7); return; }
            }
            const auto api=definition.value("api").toString(),variant=definition.value("variant").toString();
            const bool brandEmpty=expectedEmpty && api=="BleeckerBrandMark" && (definition.value("size").toString().toDouble()==0 || definition.value("size").toString().toDouble()==1);
            const bool navigationEmpty=expectedEmpty && ((api=="BleeckerBreadcrumb" && (variant=="empty" || variant=="single-empty")) || (api=="BleeckerPageHeader" && variant=="empty-labels"));
            const bool radioEmpty=expectedEmpty && api=="BleeckerRadioGroup" && definition.value("options").isArray() && definition.value("options").toArray().isEmpty();
            const bool gridEmpty=expectedEmpty && api=="BleeckerDashboardGrid" && variant=="empty";
            const bool modalEmpty=expectedEmpty && api=="BleeckerModal" && definition.value("modalWidth").toDouble()==0;
            const bool tooltipEmpty=expectedEmpty && api=="BleeckerTooltip" && QStringList{"empty","zero","hidden"}.contains(definition.value("content").toString());
            const bool surfaceEmpty=expectedEmpty && api=="BleeckerSurfaceModifier" && definition.value("content").toString()=="empty";
            const bool fontEmpty=expectedEmpty && api=="View.bleeckerFont" && definition.value("content").toString()=="empty-view";
            const bool buttonStyleEmpty=expectedEmpty && api=="BleeckerButtonStyle" && definition.value("content").toString()=="empty";
            const bool buttonGroupEmpty=expectedEmpty && api=="BleeckerButtonGroup"
                && QStringList{"absent","empty-group","zero","conditional-absent"}.contains(variant);
            const auto geometryItem=api=="BleeckerTooltip" && component ? component->property("control").value<QQuickItem*>():(api=="BleeckerButtonGroup" || api=="BleeckerModal" || api=="BleeckerOTPInput" || api=="BleeckerActivityItem") && component ? component->property("presentationItem").value<QQuickItem*>():component;
            if (isolated && (!component || !geometryItem || component->width()<0 || component->height()<0
                || geometryItem->width()<0 || geometryItem->height()<0
                || ((geometryItem->width()==0 || geometryItem->height()==0) && !expectedEmpty)
                || (expectedEmpty && !navigationEmpty && !gridEmpty && !brandEmpty && !radioEmpty && !modalEmpty && !tooltipEmpty && !buttonStyleEmpty && !fontEmpty && !surfaceEmpty && !buttonGroupEmpty)
                || (buttonGroupEmpty && (geometryItem->width()!=0 || geometryItem->height()!=0))
                || (modalEmpty && (geometryItem->width()!=0 || geometryItem->height()<=0))
                || (gridEmpty && component->height()!=0)
                || (radioEmpty && (component->width()!=0 || component->height()!=0)))) {qCritical("Invalid isolated geometry or expected-empty contract");app.exit(6);return;}
            const bool surfaceCapture=api=="BleeckerSurfaceModifier" || parser.value("fixture")=="surface-modifier";
            if(surfaceCapture && !waitForShapeFrame(window)){qCritical("Surface capture did not reach displayed ready geometry");app.exit(96);return;}
            if(api=="Text.bleeckerPill" || parser.value("fixture")=="pill-modifier") {
                const auto pill=isolated ? component:window->property("primaryFixture").value<QQuickItem*>();
                QElapsedTimer timer;timer.start();bool ready=false;
                do {
                    if(!waitForShapeFrame(window)){app.exit(96);return;}
                    const auto label=pill ? pill->property("label").value<QQuickItem*>():nullptr;
                    if(!label || !QMetaObject::invokeMethod(label,"resourcesReady",Q_RETURN_ARG(bool,ready))){app.exit(96);return;}
                }while(!ready && timer.elapsed()<5000);
                if(!ready){qCritical("Pill text resources did not finish");app.exit(96);return;}
            }
            if (!window->grabWindow().save(path)) { app.exit(2); return; }
            QJsonObject meta{{"qt", qVersion()}, {"os", QSysInfo::prettyProductName()},
                {"compiler", QString::fromUtf8(__VERSION__)}, {"environmentRecord", "environment.json"},
                {"architecture", QSysInfo::currentCpuArchitecture()}, {"platform", QGuiApplication::platformName()},
                {"captureMethod", "QQuickWindow::grabWindow (single window; not compositor overlay evidence)"},
                {"width", window->width()}, {"height", window->height()}, {"dpr", window->devicePixelRatio()},
                {"graphicsApi", int(window->rendererInterface()->graphicsApi())},
                {"requestedGraphicsBackend", qEnvironmentVariable("QSG_RHI_BACKEND")},
                {"quickBackend", qEnvironmentVariable("QT_QUICK_BACKEND")}};
            QFont font("Encode Sans"); font.setPixelSize(14); font.setWeight(QFont::Medium);
            const auto raw = QRawFont::fromFont(font);
            meta.insert("resolvedFontFamily", raw.familyName());
            meta.insert("resolvedFontStyle", raw.styleName());
            const auto surface = window->findChild<QQuickItem *>("bleeckerButtonSurface");
            if (surface) {
                meta.insert("surfaceWidth", surface->width());
                meta.insert("surfaceHeight", surface->height());
                const auto surfaceOrigin = surface->mapToScene(QPointF(0, 0));
                meta.insert("surfaceX", surfaceOrigin.x());
                meta.insert("surfaceY", surfaceOrigin.y());
                meta.insert("surfaceRadius", surface->property("radius").toDouble());
                meta.insert("surfaceRendererType", surface->property("rendererType").toInt());
                meta.insert("surfaceOuterPath", surface->property("outerPath").toString());
                meta.insert("surfaceBorderPath", surface->property("borderPath").toString());
            }
            const auto label = window->findChild<QQuickItem *>("bleeckerButtonLabel");
            if (label) {
                const auto labelFont = label->property("font").value<QFont>();
                meta.insert("labelFontFamily", label->property("resolvedFamily").toString());
                meta.insert("labelFontStyle", label->property("resolvedStyle").toString());
                meta.insert("labelFontWeight", int(labelFont.weight()));
                meta.insert("labelFontHintingPreference", int(labelFont.hintingPreference()));
                meta.insert("labelRenderer", "QQuickPaintedItem/QPainter glyph runs at logical font size");
                meta.insert("labelPixelSize", label->property("logicalPixelSize").toDouble());
                meta.insert("labelFontPointSize", labelFont.pointSizeF());
                meta.insert("labelWidth", label->width());
                meta.insert("labelHeight", label->height());
                meta.insert("labelBaseline", label->baselineOffset());
                const auto origin = label->mapToScene(QPointF(0, 0));
                meta.insert("labelX", origin.x()); meta.insert("labelY", origin.y());
                meta.insert("labelSceneBaseline", label->mapToScene(QPointF(0, label->baselineOffset())).y());
                const auto content = label->parentItem();
                meta.insert("labelLocalX", label->x()); meta.insert("labelLocalY", label->y());
                meta.insert("contentX", content->x()); meta.insert("contentY", content->y());
                meta.insert("contentWidth", content->width()); meta.insert("contentHeight", content->height());
                meta.insert("contentImplicitHeight", content->implicitHeight());
            }
            meta.insert("fixture", parser.value("fixture"));
            meta.insert("textScale", window->property("fixtureTextScale").toDouble());
            meta.insert("variant", parser.value("variant"));
            meta.insert("size", parser.value("size"));
            meta.insert("state", parser.isSet("disabled") ? "disabled" : "enabled");
            meta.insert("appearance", parser.isSet("dark") ? "dark" : "light");
            if (selectorPopup) {
                const auto origin=selectorPopupContent->mapToScene(QPointF(0,0));
                meta.insert("popoverGeometry",QJsonObject{{"x",origin.x()-selectorPopup->property("leftPadding").toDouble()},
                    {"y",origin.y()-selectorPopup->property("topPadding").toDouble()},
                    {"width",selectorPopup->property("width").toDouble()},{"height",selectorPopup->property("height").toDouble()}});
                meta.insert("popupVisible",true); meta.insert("popupType",selectorPopup->property("popupType").toInt());
                meta.insert("popupContentOrigin",QJsonObject{{"x",origin.x()},{"y",origin.y()}});
                meta.insert("popupContentSize",QJsonObject{{"width",selectorPopupContent->width()},{"height",selectorPopupContent->height()}});
                meta.insert("overlayCoverage","Open owned Popup.Item is inside the captured window; compositor/session evidence is separate");
                meta.insert("symbolAcceptance","pending; original chevron/checkmark candidates");
                QJsonArray labels; recordLabels(window->contentItem(),labels); meta.insert("labels",labels);
            }
            if(api=="BleeckerFileInput" || parser.value("fixture")=="file-input") {
                const auto input=isolated ? component:window->property("primaryFixture").value<QQuickItem*>();
                if(!input){app.exit(96);return;}
                meta.insert("fileInputFrame",surfaceModifierMap(input,"frame"));
                meta.insert("fileInputState",surfaceModifierMap(input,"state"));
            }
            if(api=="BleeckerDropdownMenu" || parser.value("fixture")=="dropdown-menu") {
                const auto dropdown=isolated ? component:window->property("primaryFixture").value<QQuickItem*>();
                if(!dropdown){app.exit(96);return;}
                meta.insert("dropdownMenuFrame",surfaceModifierMap(dropdown,"frame"));
                meta.insert("dropdownMenuState",surfaceModifierMap(dropdown,"state"));
            }
            if(api=="BleeckerCommandSpotlight" || parser.value("fixture")=="command-spotlight") {
                const auto spotlight=isolated ? component:window->property("primaryFixture").value<QQuickItem*>();
                if(!spotlight){app.exit(96);return;}
                meta.insert("commandSpotlightFrame",surfaceModifierMap(spotlight,"frame"));
                meta.insert("commandSpotlightState",surfaceModifierMap(spotlight,"state"));
            }
            if(api=="BleeckerAppTabBar" || parser.value("fixture")=="app-tabs") {
                const auto tabs=isolated ? component:window->property("primaryFixture").value<QQuickItem*>();
                if(!tabs){app.exit(96);return;}
                meta.insert("appTabFrame",surfaceModifierMap(tabs,"frame"));
                meta.insert("appTabState",surfaceModifierMap(tabs,"state"));
                meta.insert("appTabSelection",surfaceModifierMap(tabs,"selectionState"));
            }
            if(api=="BleeckerDateRangePicker" || parser.value("fixture")=="date-range") {
                const auto date=isolated ? component:window->property("primaryFixture").value<QQuickItem*>();
                if(!date){app.exit(96);return;}
                meta.insert("dateRange",surfaceModifierMap(date,"snapshot"));
            }
            if(api=="BleeckerHeroCarousel" || parser.value("fixture")=="hero-carousel") {
                const auto hero=isolated ? component:window->property("primaryFixture").value<QQuickItem*>();
                if(!hero){app.exit(96);return;}
                meta.insert("heroFrame",surfaceModifierMap(hero,"frame"));
                meta.insert("heroState",surfaceModifierMap(hero,"state"));
                meta.insert("heroMetrics",surfaceModifierMap(hero,"measurements"));
            }
            if(api=="BleeckerMediaLibrary" || parser.value("fixture")=="media-library") {
                const auto media=isolated ? component:window->property("primaryFixture").value<QQuickItem*>();
                if(!media){app.exit(96);return;}
                meta.insert("mediaFrame",surfaceModifierMap(media,"frame"));
                meta.insert("mediaState",surfaceModifierMap(media,"state"));
                meta.insert("mediaMetrics",surfaceModifierMap(media,"measurements"));
            }
            if (isolated) {
                if (definition.value("api").toString()=="BleeckerSecureField") {
                    const bool revealed=component->property("revealed").toBool();
                    if (revealed!=definition.value("variant").toString().startsWith("revealed-")
                        || component->property("text").toString()!=definition.value("text").toString()
                        || (!revealed && !component->property("text").toString().isEmpty()
                            && component->property("displayText")==component->property("text"))) { app.exit(9); return; }
                    meta.insert("revealed",revealed); meta.insert("sourceValuePreserved",true);
                }
                if (definition.value("fixture").toString().startsWith("search-"))
                    meta.insert("sourceValueAfterAction",component->property("text").toString());
                if (definition.value("api").toString()=="BleeckerIconButton" || definition.value("api").toString()=="BleeckerPagination") {
                    const auto fixture=definition.value("fixture").toString();
                    const bool icon=definition.value("api").toString()=="BleeckerIconButton";
                    const auto action=icon ? fixture.endsWith("-disabled-click") ? QStringLiteral("disabled-click") : fixture.endsWith("-clicked") ? QStringLiteral("clicked") : fixture.endsWith("-pressed") ? QStringLiteral("pressed") : QStringLiteral("none")
                        : (fixture.startsWith("pagination-action-") || fixture.startsWith("pagination-i64-action-")) ? definition.value("variant").toString() : QStringLiteral("none");
                    meta.insert("sourceAction",action);
                    meta.insert("sourceActivations",window->property(icon ? "iconCalls" : fixture.startsWith("pagination-i64-") ? "integerCalls" : "pageRequests").toInt());
                    if (!icon) {
                        if (fixture.startsWith("pagination-i64-")) {
                            meta.insert("sourcePageAfterActionDecimal",window->property("integerPage").toString());
                            meta.insert("sourcePageCountAfterActionDecimal",window->property("integerCount").toString());
                            const auto requested=window->property("integerRequested");
                            meta.insert("sourceRequestedPageDecimal",requested.isNull() ? QJsonValue(QJsonValue::Null) : QJsonValue(requested.toString()));
                        } else {
                        meta.insert("sourcePageAfterAction",window->property("pageValue").toInt());
                        meta.insert("sourcePageCountAfterAction",window->property("pageTotal").toInt());
                        const auto requested=window->property("lastPageRequest");
                        if (requested.isNull()) meta.insert("sourceRequestedPage",QJsonValue(QJsonValue::Null));
                        else {
                            bool valid=false;const auto exact=requested.toLongLong(&valid);
                            if (!valid) {app.exit(15);return;}
                            meta.insert("sourceRequestedPage",QJsonValue(exact));
                        }
                        }
                        const auto row=findVisual(component,"bleeckerPaginationContent");
                        if (!row) {app.exit(15);return;}
                        meta.insert("bodySize",QJsonObject{{"width",row->width()},{"height",row->height()}});
                    } else {
                        const bool down=component->property("down").toBool();
                        meta.insert("linuxPressedAtCapture",down);
                        if (action=="pressed" && !down) {app.exit(15);return;}
                    }
                }
                if (definition.value("api").toString()=="BleeckerTabs" || definition.value("fixture").toString().startsWith("segments-bound-")) {
                    const auto body=findVisual(component,"bleeckerBoundSelectionBody");
                    if (!body) {app.exit(14);return;}
                    meta.insert("sourceSelectionAfterAction",QJsonValue::fromVariant(body->property("selection")));
                    meta.insert("sourceActivations",window->property("boundActivations").toInt());
                    meta.insert("bodySize",QJsonObject{{"width",body->width()},{"height",body->height()}});
                }
                if(definition.value("api").toString()=="BleeckerAccordion") {
                    meta.insert("sourceAction",definition.value("fixture").toString().startsWith("accordion-action-") ? definition.value("variant"):QJsonValue("none"));
                    const auto surface=findVisual(component,"bleeckerAccordionSurface");
                    const auto header=component->property("inputItem").value<QQuickItem*>();
                    if(!surface || !header){app.exit(17);return;}
                    meta.insert("accordionSurface",QJsonObject{{"radius",surface->property("radius").toDouble()},{"outerPath",surface->property("outerPath").toString()},{"borderPath",surface->property("borderPath").toString()},{"rendererType",surface->property("rendererType").toInt()}});
                    meta.insert("accordionRoundedClipping",component->property("roundedContentClipping").toBool());
                    meta.insert("accordionHeaderDown",header->property("down").toBool());
                    meta.insert("sourceExpandedAfterAction",component->property("expanded").toBool());
                    meta.insert("sourceMounts",window->property("accordionMounts").toInt());
                    meta.insert("sourceUnmounts",window->property("accordionUnmounts").toInt());
                    meta.insert("sourceCounterValue",window->property("accordionCounterValue").toInt());
                    meta.insert("sourceTitleAfterAction",component->property("title").toString());
                    meta.insert("sourceInitialAfterAction",component->property("initiallyExpanded").toBool());
                    meta.insert("sourceContentTextAfterAction",window->property("accordionBodyText").toString());
                }
                if (definition.value("api").toString()=="BleeckerSlider") {
                    meta.insert("sourceMinimum",component->property("from").toDouble());
                    meta.insert("sourceMaximum",component->property("to").toDouble());
                    meta.insert("sourceStep",component->property("stepSize").toDouble());
                    meta.insert("sourceValueAfterAction",component->property("value").toDouble());
                    meta.insert("linuxModelEdits",window->property("sliderEdits").toInt());
                    meta.insert("sourceBindingUpdated",window->property("sliderEdits").toInt()>0);
                    meta.insert("sourceControlActiveState","active");
                }
                if (definition.value("api").toString()=="BleeckerCollectionFilters") {
                    meta.insert("sourceQueryAfterAction",component->property("query").toString());
                    meta.insert("sourceContentAfterAction",window->property("collectionHasChip").toBool());
                    meta.insert("sourceSelectedAfterAction",window->property("collectionSelected").toBool());
                    meta.insert("sourceActionCounts",QJsonObject{{"activations",window->property("collectionActivations").toInt()},{"removals",window->property("collectionRemovals").toInt()}});
                }
                for (auto it = definition.begin(); it != definition.end(); ++it) meta.insert(it.key(), it.value());
                meta.insert("caseDefinitions", parser.value("case-definitions"));
                if(QStringList{"BleeckerLineChart","BleeckerBarChart","BleeckerPieChart","BleeckerScatterChart","BleeckerSparkline"}.contains(api)) {
                    meta.insert("chartFrame",surfaceModifierMap(component,"frame"));
                    meta.insert("chartMetrics",surfaceModifierMap(component,"measurements"));
                    meta.insert("chartState",surfaceModifierMap(component,"state"));
                }
                if(api=="Text.bleeckerPill") {
                    meta.insert("pillParts",surfaceModifierMap(component,"frames"));
                    meta.insert("pillBaselines",surfaceModifierMap(component,"baselines"));
                    meta.insert("pillState",QJsonObject{{"appearances",component->property("appearances").toInt()},{"disappearances",component->property("disappearances").toInt()},{"callerInstances",component->property("callerInstances").toInt()}});
                    meta.insert("asyncTextResourceChecks","passed");
                }
                if(api=="BleeckerSurfaceModifier") {
                    const auto observation=surfaceModifierObservation(component);
                    for(auto it=observation.begin();it!=observation.end();++it)meta.insert(it.key(),it.value());
                    meta.insert("asyncShapeFrameChecks","passed");
                }
                if(api=="View.bleeckerFont") {
                    const auto observation=fontModifierObservation(component);
                    for(auto it=observation.begin();it!=observation.end();++it)meta.insert(it.key(),it.value());
                }
                if(api=="BleeckerButtonStyle") {
                    const auto control=component->property("control").value<QQuickItem*>();
                    if(!control){app.exit(18);return;}
                    const int count=control->property("partCount").toInt();
                    const auto kind=definition.value("content").toString();
                    if(count!=(kind=="empty" ? 0:kind=="multi" ? 2:1)){app.exit(18);return;}
                    meta.insert("renderedVariant",control->property("variant").toString());
                    meta.insert("renderedSize",control->property("size").toString());
                    meta.insert("renderedDisabled",!control->isEnabled());
                    meta.insert("renderedRtl",control->property("mirrored").toBool());
                    meta.insert("renderedWidthOffer",control->property("widthOffer").toDouble());
                    meta.insert("renderedMaximumWidth",control->property("maximumWidth").toDouble());
                    meta.insert("buttonStylePartInstances",buttonStyleFrames(component));
                    meta.insert("buttonStyleState",QJsonObject{{"count",component->property("localValue").toInt()},
                        {"calls",buttonStyleList(component->property("calls"))},{"mountValues",buttonStyleList(component->property("mountValues"))}});
                    meta.insert("qtDestroyedCount",component->property("destroyedCount").toInt());
                    QJsonArray labels;
                    for(int index=0;index<count;++index){
                        const auto label=buttonStylePart(control,index)->property("labelItem").value<QQuickItem*>();
                        if(!label){app.exit(18);return;}
                        QJsonObject row{{"objectName",label->objectName()},{"visible",label->isVisible()}};
                        if(label->property("text").isValid())row.insert("text",label->property("text").toString());
                        if(label->property("font").isValid()){
                            const auto font=label->property("font").value<QFont>();
                            row.insert("font",QJsonObject{{"family",font.family()},{"pointSize",font.pointSizeF()},{"weight",int(font.weight())}});
                        }
                        labels.append(row);
                    }
                    meta.insert("renderedLabelObjects",labels);
                    meta.insert("sourceCaptureMethodScope","Closed body and live per-part frames; input, raster and reader acceptance remain separate");
                }
                if(api=="BleeckerTooltip") {
                    const auto caller=component->property("control").value<QQuickItem*>();
                    const auto help=component->property("help").value<QObject*>();
                    if(!caller || !help){app.exit(18);return;}
                    meta.insert("renderedHint",help->property("text").toString());
                    meta.insert("renderedContent",definition.value("content"));
                    meta.insert("renderedDisabled",!caller->isEnabled());
                    meta.insert("renderedRtl",component->property("mirrored").toBool());
                    meta.insert("tooltipVisible",help->property("visible").toBool());
                    meta.insert("helpAttached",component->property("helpAttached").toBool());
                    meta.insert("counterValue",component->property("localValue").toInt());
                    const auto values=component->property("mountValues");
                    meta.insert("mountValues",QJsonArray::fromVariantList(values.metaType()==QMetaType::fromType<QJSValue>() ? values.value<QJSValue>().toVariant().toList():values.toList()));
                    meta.insert("qtDestroyedCount",component->property("destroyedCount").toInt());
                    QJsonObject parts;
                    auto rect=[&](const QString &key,QQuickItem *item){if(!item)qFatal("Tooltip caller witness missing");const auto p=item->mapToScene(QPointF());parts.insert(key,QJsonObject{{"x",p.x()},{"y",p.y()},{"width",item->width()},{"height",item->height()}});};
                    const auto kind=definition.value("content").toString();
                    if(kind!="empty") {
                        rect("root",caller);
                        if(kind=="multi"){rect("first",findVisual(caller,"tooltipCallerFirst"));rect("second",findVisual(caller,"tooltipCallerSecond"));}
                        else rect(kind=="inherited" || kind=="text" ? "text":kind,caller);
                    }
                    meta.insert("tooltipCallerRects",parts);
                    meta.insert("sourceCaptureMethodScope","Closed body only; no shown-popup, compositor or screen-reader equivalence claim");
                }
                if(api=="BleeckerModal") {
                    const auto control=component->property("control").value<QQuickItem*>();
                    const auto body=component->property("presentationItem").value<QQuickItem*>();
                    if(!control || !body){app.exit(18);return;}
                    meta.insert("renderedTitle",control->property("title").toString());
                    meta.insert("renderedModalWidth",control->property("modalWidth").toDouble());
                    meta.insert("renderedContent",definition.value("content"));
                    meta.insert("renderedDisabled",!control->isEnabled());meta.insert("renderedRtl",control->property("mirrored").toBool());
                    QJsonObject parts,painted;
                    const QMap<QString,QString> names{{"title","bleeckerModalTitle"},{"close","bleeckerModalClose"},
                        {"spacer","bleeckerModalSpacer"},{"header-row","bleeckerModalHeaderRow"},{"separator","bleeckerModalSeparator"},
                        {"content-rectangle","modalContent-rectangle"},{"content-zero","modalContent-zero"},
                        {"content-hidden","modalContent-hidden"},{"content-tall","modalContent-tall"},{"content-wide","modalContent-wide"},
                        {"content-fills","modalContent-fills"},{"content-text","modalContent-text"},
                        {"content-first","modalContent-first"},{"content-second","modalContent-second"},
                        {"content-vstack","modalContent-vstack"},{"content-hstack","modalContent-hstack"},
                        {"content-counter","modalContent-counter"},{"content-editor","modalContent-editor"},
                        {"content-wide-button","modalContent-wide-button"}};
                    for(auto it=names.begin();it!=names.end();++it) {
                        const auto item=findVisual(component,it.value());if(!item)continue;
                        QPointF point;for(auto parent=item;parent && parent!=window->contentItem();parent=parent->parentItem())point+=parent->position();
                        parts.insert(it.key(),QJsonObject{{"x",point.x()},{"y",point.y()},{"width",item->width()},{"height",item->height()}});
                        const auto paint=item->mapToScene(QPointF());
                        painted.insert(it.key(),QJsonObject{{"x",paint.x()},{"y",paint.y()},{"width",item->width()},{"height",item->height()}});
                    }
                    const auto origin=body->mapToScene(QPointF());
                    parts.insert("root",QJsonObject{{"x",origin.x()},{"y",origin.y()},{"width",body->width()},{"height",body->height()}});
                    const auto row=parts.value("header-row").toObject();
                    parts.insert("header",QJsonObject{{"x",row.value("x").toDouble()-20},{"y",row.value("y").toDouble()-20},
                        {"width",row.value("width").toDouble()+40},{"height",row.value("height").toDouble()+40}});
                    meta.insert("layoutWitnessRects",parts);meta.insert("paintedWitnessRects",painted);
                    meta.insert("layoutWitnessMethod","Layout positions exclude text paint translations; header is padded row; raw painted frames retained separately");
                    meta.insert("fontSymbolAcceptance","pending; inherited platform font and original cross candidate, no approved exception");
                    meta.insert("sourceCaptureMethodScope","Original hosted source captures; sheet editor body proxy frames excluded; physical/session and reader gates separate");
                }
                if(api=="BleeckerActivityItem") {
                    const auto control=component->property("control").value<QQuickItem*>();
                    const auto body=component->property("presentationItem").value<QQuickItem*>();
                    if(!control || !body){app.exit(18);return;}
                    meta.insert("renderedTitle",control->property("title").toString());
                    meta.insert("renderedDetail",control->property("detail").toString());
                    meta.insert("renderedTimestamp",control->property("timestamp").toString());
                    meta.insert("renderedActionMode",component->property("actionMode").toString());
                    meta.insert("renderedDisabled",!control->isEnabled());
                    meta.insert("renderedRtl",control->property("mirrored").toBool());
                    QJsonObject parts,painted;
                    const QMap<QString,QString> names{{"badge","bleeckerActivityBadge"},{"row","bleeckerActivityRow"},
                        {"text-column","bleeckerActivityLabels"},{"title","bleeckerActivityTitle"},
                        {"detail","bleeckerActivityDetail"},{"timestamp","bleeckerActivityTimestamp"},
                        {"spacer","bleeckerActivitySpacer"},{"action-review","activityActionReview"},
                        {"action-archive","activityActionArchive"},{"action-nested","activityActionNested"},
                        {"action-plain","activityActionPlain"},{"action-rect","activityActionRect"},
                        {"action-tall","activityActionTall"},{"action-zero","activityActionZero"},{"action-counter","activityActionCounter"}};
                    for(auto it=names.begin();it!=names.end();++it) {
                        const auto item=findVisual(component,it.value());if(!item)continue;
                        QPointF point;
                        for(auto parent=item;parent && parent!=window->contentItem();parent=parent->parentItem())point+=parent->position();
                        parts.insert(it.key(),QJsonObject{{"x",point.x()},{"y",point.y()},{"width",item->width()},{"height",item->height()}});
                        const auto paint=item->mapToScene(QPointF());
                        painted.insert(it.key(),QJsonObject{{"x",paint.x()},{"y",paint.y()},{"width",item->width()},{"height",item->height()}});
                    }
                    const auto origin=body->mapToScene(QPointF());
                    parts.insert("root",QJsonObject{{"x",origin.x()},{"y",origin.y()},{"width",body->width()},{"height",body->height()}});
                    meta.insert("layoutWitnessRects",parts);meta.insert("paintedWitnessRects",painted);
                    meta.insert("layoutWitnessMethod","Layout x/y positions exclude text paint-only pixel translations; painted frames retained separately");
                    meta.insert("actionLocalValue",component->property("localValue").toInt());
                    meta.insert("actionAppears",component->property("appears").toInt());
                    meta.insert("fontSymbolAcceptance","pending; inherited platform font and original clock/fixture artwork, no approved exception");
                }
                if(api=="BleeckerOTPInput") {
                    const auto control=component->property("control").value<QQuickItem*>();
                    const auto editor=control ? control->property("editor").value<QQuickItem*>():nullptr;
                    if(!control || !editor){app.exit(18);return;}
                    meta.insert("renderedCode",control->property("code").toString());
                    meta.insert("renderedLength",control->property("length").toDouble());
                    meta.insert("renderedPlaceholder",editor->property("placeholderText").toString());
                    meta.insert("renderedFieldValue",editor->property("text").toString());
                    meta.insert("renderedDisabled",!editor->isEnabled());
                    meta.insert("renderedCenterAligned",editor->property("horizontalAlignment").toInt()==Qt::AlignHCenter);
                    const auto font=editor->property("font").value<QFont>();
                    meta.insert("editorFont",QJsonObject{{"family",font.family()},{"pointSize",font.pointSizeF()},{"weight",font.weight()}});
                    meta.insert("editorMaximumLength",editor->property("maximumLength").toInt());
                    const auto point=editor->mapToScene(QPointF());
                    meta.insert("layoutWitnessRects",QJsonObject{{"qtTextField",QJsonObject{{"x",point.x()},{"y",point.y()},{"width",editor->width()},{"height",editor->height()}}}});
                    meta.insert("nativeLifecycleAcceptance","pending; source callback counts, selection and native keyloop differ");
                    meta.insert("fontAcceptance","pending; Linux fixed font is not the native system monospace face");
                }
                if(api=="BleeckerRadioGroup") {
                    const auto control=component->property("control").value<QQuickItem*>();
                    if(!control){app.exit(18);return;}
                    auto selection=control->property("selection");if(selection.metaType()==QMetaType::fromType<QJSValue>())selection=selection.value<QJSValue>().toVariant();
                    meta.insert("selection",QJsonValue::fromVariant(selection));
                    meta.insert("renderedOrientation",control->property("orientation").toInt()==Qt::Horizontal ? "horizontal":"vertical");
                    meta.insert("renderedDisabled",!control->isEnabled());
                    QJsonArray options;QJsonObject parts;
                    const int count=control->property("count").toInt();
                    for(int i=0;i<count;++i) {
                        const auto button=findVisual(control,"bleeckerRadioOption"+QString::number(i));
                        if(!button){app.exit(18);return;}
                        auto value=button->property("optionValue");if(value.metaType()==QMetaType::fromType<QJSValue>())value=value.value<QJSValue>().toVariant();
                        options.append(QJsonObject{{"value",QJsonValue::fromVariant(value)},{"label",button->property("text").toString()},{"disabled",button->property("optionDisabled").toBool()},{"enabled",button->isEnabled()},{"selected",button->property("selected").toBool()}});
                        auto record=[&parts,i](const QString &part,QQuickItem *item){if(!item)qFatal("RadioGroup witness Item missing");const auto p=item->mapToScene(QPointF());parts.insert("option-"+QString::number(i)+"-"+part,QJsonObject{{"x",p.x()},{"y",p.y()},{"width",item->width()},{"height",item->height()}});};
                        record("button",button);record("label",button->property("contentItem").value<QQuickItem*>());
                        record("title",button->property("titleItem").value<QQuickItem*>());record("icon",button->property("iconItem").value<QQuickItem*>());
                    }
                    meta.insert("renderedOptions",options);meta.insert("layoutWitnessRects",parts);
                    meta.insert("fontSymbolAcceptance","pending; default font and original circle geometry are unapproved candidates");
                }
                if(api=="BleeckerStepper") {
                    const auto control=component->property("control").value<QQuickItem*>();
                    const auto minus=findVisual(component,"bleeckerStepperDecrement"),plus=findVisual(component,"bleeckerStepperIncrement"),label=findVisual(component,"bleeckerStepperLabel"),value=findVisual(component,"bleeckerStepperValue");
                    if(!control || !minus || !plus || !label || !value){app.exit(18);return;}
                    auto stateValue=control->property("valueState");
                    if(stateValue.metaType()==QMetaType::fromType<QJSValue>())stateValue=stateValue.value<QJSValue>().toVariant();
                    const auto state=stateValue.toMap();
                    if(!state.contains("value") || !state.contains("displayValue")){app.exit(18);return;}
                    meta.insert("value",state.value("value").toString());meta.insert("formattedValue",value->property("text").toString());
                    meta.insert("displayValue",state.value("displayValue").toString());
                    meta.insert("decrementEnabled",minus->isEnabled());meta.insert("incrementEnabled",plus->isEnabled());
                    meta.insert("qtWindowActive",window->isActive());
                    QJsonObject parts;
                    auto rect=[&parts](const QString &key,QQuickItem *item){if(!item)qFatal("Stepper witness Item missing");const auto point=item->mapToScene(QPointF());parts.insert(key,QJsonObject{{"x",point.x()},{"y",point.y()},{"width",item->width()},{"height",item->height()}});};
                    rect("label",label->parentItem());rect("label-text",label);rect("divider",findVisual(component,"bleeckerStepperDivider"));
                    rect("minus-button",minus);rect("plus-button",plus);rect("minus-image",minus->property("contentItem").value<QQuickItem*>());rect("plus-image",plus->property("contentItem").value<QQuickItem*>());
                    rect("value",value->parentItem());rect("value-text",value);meta.insert("layoutWitnessRects",parts);
                    meta.insert("fontSymbolAcceptance","pending; fixed system monospace and original plus/minus candidate artwork, no approved font/symbol exception");
                    meta.insert("sourceCaptureMethodScope","Hosted native source investigation compared with Qt single-window capture; no equivalence to old ImageRenderer baseline or physical-session acceptance");
                }
                auto measuredComponent=component;
                if(api=="BleeckerTooltip")measuredComponent=component->property("control").value<QQuickItem*>();
                if (api=="BleeckerButtonGroup" || api=="BleeckerModal" || api=="BleeckerActivityItem" || api=="BleeckerOTPInput" || api=="BleeckerRadioGroup" || api=="BleeckerStepper" || api=="BleeckerMetric" || api=="BleeckerStatCard" || api=="BleeckerKbd" || api=="BleeckerIconBadge" || api=="BleeckerSidebarItem" || api=="BleeckerBrandMark" || api=="BleeckerBrandLockup" || api=="BleeckerPageHeader" || api=="BleeckerBreadcrumb" || definition.value("api").toString()=="BleeckerAlert" || definition.value("api").toString()=="BleeckerEmptyState" || definition.value("api").toString()=="BleeckerErrorState") {
                    measuredComponent=component->property("presentationItem").value<QQuickItem*>();
                    if(!measuredComponent){app.exit(18);return;}
                    const auto offered=api=="BleeckerModal" ? component->property("control").value<QQuickItem*>():component;
                    if(!offered){app.exit(18);return;}
                    meta.insert("offeredFrameSize",QJsonObject{{"width",offered->width()},{"height",offered->height()}});
                    meta.insert("componentGeometryMethod","actual fitted presentation Item before the caller's offered frame, matching the source probe");
                }
                meta.insert("componentSize", QJsonObject{{"width", measuredComponent->width()}, {"height", measuredComponent->height()}});
                const auto position = measuredComponent->mapToScene(QPointF(0, 0));
                meta.insert("componentOrigin", QJsonObject{{"x", position.x()}, {"y", position.y()}});
                if(api=="BleeckerFooter" || api=="BleeckerButtonGroup") {
                    QJsonObject frames;
                    const auto record=[&frames](const QString &name,QQuickItem *item) {
                        const auto point=item->mapToScene(QPointF());
                        frames.insert(name,QJsonObject{{"x",point.x()},{"y",point.y()},
                            {"width",item->width()},{"height",item->height()}});
                    };
                    record("component",measuredComponent);
                    for(const auto &name:QStringList{"first","second"}) {
                        if(const auto child=findVisual(component,name)) {
                            record(name,child);
                            if(api=="BleeckerButtonGroup")
                                if(const auto label=findVisual(child,"bleeckerButtonLabel"))record(name+"Text",label);
                        }
                    }
                    meta.insert(api=="BleeckerFooter" ? "footerFrames":"buttonGroupFrames",frames);
                }
                QJsonArray labels;
                recordLabels(component, labels);
                meta.insert("labels", labels);
                meta.insert("dynamicStateTiming", "700 ms settlement; reduced motion; no matched native animation phase");
                meta.insert("referenceAcceptance", "proposed reference; diagnostic comparison only");
            }
            if (isolated && definition.value("api").toString()=="BleeckerIconButton" && definition.value("fixture").toString().endsWith("-pressed")) {
                const auto component=findVisual(window->contentItem(),"referenceCaseComponent");
                const auto input=component ? component->property("inputItem").value<QQuickItem*>() : nullptr;
                if (!input) {app.exit(15);return;}
                QTest::mouseRelease(window,Qt::LeftButton,Qt::NoModifier,input->mapToScene(QPointF(input->width()/2,input->height()/2)).toPoint());
                const auto calls=window->property("iconCalls").toInt();
                meta.insert("linuxReleaseActivations",calls);
                if (calls!=1) {app.exit(15);return;}
            }
            QFile file(path + ".json");
            if (!file.open(QIODevice::WriteOnly)) { app.exit(3); return; }
            file.write(QJsonDocument(meta).toJson());
            app.exit(0);
        });
    }
    return app.exec();
}

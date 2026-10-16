import QtQuick
import QtQuick.Templates as T
import QtQuick.Layouts
import QtQuick.Templates as T
import Avelino

Window {
    id: window
    readonly property var definition: captureDefinition
    property bool collectionSelected: definition.variant === "selected"
    property bool collectionHasChip: definition.variant !== "empty"
    property int collectionActivations: 0
    property int collectionRemovals: 0
    property real sliderValue: definition.api === "BleeckerSlider" ? Number(definition.text) : 0
    property int sliderEdits: 0
    property int pageValue: definition.api === "BleeckerPagination" && !definition.fixture.startsWith("pagination-i64-") ? Number(definition.text) : 0
    property int pageTotal: definition.value
    property string integerPage: definition.fixture.startsWith("pagination-i64-") ? definition.text : "0"
    property string integerCount: definition.fixture.startsWith("pagination-i64-") ? definition.size : "0"
    property var integerRequested: null
    property int integerCalls: 0
    property int pageRequests: 0
    property var lastPageRequest: null
    property string accordionTitle: definition.text
    property string accordionBodyText: definition.variant === "long-body" ? "Keep selected editions available for review" : "Body copy"
    property int accordionMounts:0
    property int accordionUnmounts:0
    property int accordionCounterValue:0
    property int iconCalls: 0
    property var boundSelection: definition.text
    property int boundActivations: 0
    readonly property real fixtureTextScale: BleeckerTheme.textScale
    width: definition.width; height: definition.height; visible: true
    color: BleeckerTheme.palette.background
    title: "Avelino reference case — " + definition.fixture
    Component.onCompleted: {
        BleeckerTheme.dark = captureDark
        BleeckerTheme.textScale = captureTextScale
        BleeckerTheme.reducedMotion = true
    }
    Loader {
        id: loader
        anchors.centerIn: parent
        anchors.alignWhenCentered: false
        sourceComponent: {
            const components = {
                "BleeckerButton": button, "BleeckerStepper":stepperCase, "BleeckerLoadingSpinner": spinner,
                "BleeckerSidebarItem":sidebarBrandCase, "BleeckerMetric":dataMetricsCase, "BleeckerStatCard":dataMetricsCase, "BleeckerKbd":dataMetricsCase, "BleeckerIconBadge":dataMetricsCase,"BleeckerBrandMark":sidebarBrandCase,"BleeckerBrandLockup":sidebarBrandCase,"BleeckerPageHeader":navigationCase,"BleeckerBreadcrumb":navigationCase,"BleeckerAlert":alert,"BleeckerEmptyState":emptyState,"BleeckerErrorState":errorState,"BleeckerLoadingOverlay":loadingOverlay,
                "BleeckerTextField": textField, "BleeckerTextArea": textArea,
                "BleeckerField": field, "BleeckerSwitchStyle": switchControl,
                "BleeckerToggleStyle": toggle, "BleeckerSegmentedControl": segments,
                "BleeckerSeparator": separator, "BleeckerSkeleton": skeleton,
                "BleeckerBauhausBackground": bauhaus, "BleeckerProgress": progress,
                "BleeckerButtonGroup": buttonGroup, "BleeckerHeader": header,
                "BleeckerPanelLayout": panelLayout, "BleeckerCard": card,
                "BleeckerPanel": panel, "BleeckerAttentionSurface": attention,
                "BleeckerStatusBadge": status, "BleeckerNotificationBadge": notification,
                "Text.bleeckerEyebrow": eyebrow, "BleeckerAvatar": avatar,
                "BleeckerDataList": dataList, "BleeckerTimelineItem": timeline,
                "View.bleeckerSurface": surface,
                "BleeckerSectionHeader": sectionHeader, "BleeckerDashboardSection": dashboardSection,
                "BleeckerDashboardGrid": dashboardGrid, "BleeckerAppShell": appShell,
                "BleeckerFooter": footer, "BleeckerFeedItem": feed, "BleeckerProgressStack": progressStack,
                "BleeckerSelect": select, "BleeckerCheckbox": checkbox, "BleeckerSecureField": secureField, "BleeckerSearchField": searchField, "BleeckerFilterChip": filterChip, "BleeckerCollectionFilters": collectionFilters, "BleeckerSlider": slider, "BleeckerTabs": boundSelectionFrame, "BleeckerPagination": paginationFrame, "BleeckerIconButton": iconButton, "BleeckerAccordion": accordion
            }
            if (definition.fixture.startsWith("pagination-i64-")) return paginationIntegerFrame
            if (definition.fixture.startsWith("segments-bound-")) return boundSelectionFrame
            if (definition.api === "BleeckerTextField" && definition.fixture.startsWith("search-text-")) return searchField
            if (!components[definition.api]) throw new Error("Unimplemented reference API: " + definition.api)
            return components[definition.api]
        }
        onLoaded: item.objectName = "referenceCaseComponent"
    }
    Component {id:stepperCase;StepperCase {definition:window.definition}}
    Component {id:dataMetricsCase;DataMetricsCase {definition:window.definition}}
    Component {id:sidebarBrandCase;SidebarBrandCase {definition:window.definition}}
    Component {id:navigationCase;NavigationCase {definition:window.definition}}
    Component {
        id:alert
        BleeckerAlert {
            title:definition.title;type:definition.alertType;enabled:!definition.flag
            maximumWidth:definition.variant==="intrinsic" ? -1:Number(definition.size)
            LayoutMirroring.enabled:definition.variant==="rtl";LayoutMirroring.childrenInherit:true
            content:definition.contentMode==="empty" ? null:definition.contentMode==="zero" ? stateZero:definition.contentMode==="button" ? stateAction:definition.contentMode==="tall" ? alertTall:definition.contentMode==="overflow" ? alertOverflow:alertText
            Component.onCompleted:if(definition.variant==="symbol-font20")icon=alertLargeIcon
        }
    }
    Component {
        id:alertText
        ButtonLabel {
            text:definition.text;font.family:parent.font.family
            font.pointSize:definition.contentMode==="custom-font" ? BleeckerFonts.pointSizeForPixels(18):parent.font.pointSize
            font.weight:definition.contentMode==="custom-font" ? Font.DemiBold:Font.Normal
            color:definition.contentMode==="custom-font" ? BleeckerTheme.nativeRed:parent.foregroundColor
            wrapWidth:parent.availableWidth
            horizontalAlignment:definition.variant==="rtl" ? Qt.AlignRight:Qt.AlignLeft
        }
    }
    Component {id:alertTall;Rectangle {implicitWidth:72;implicitHeight:90;color:BleeckerTheme.nativeRed}}
    Component {id:alertOverflow;Item {implicitWidth:72;implicitHeight:90;Rectangle {x:-40;y:-40;width:72;height:90;color:BleeckerTheme.nativeRed}}}
    Component {id:alertLargeIcon;AlertGlyph {color:BleeckerTheme.palette.sea;PixelAlignment {id:alertIconMetrics;target:parent} implicitWidth:alertIconMetrics.devicePixelRatio<2 ? 24:23;implicitHeight:implicitWidth}}
    Component {
        id:emptyState
        BleeckerEmptyState {
            width:definition.variant==="intrinsic" ? implicitWidth : Number(definition.size)
            title:definition.title;message:definition.text;enabled:!definition.flag
            LayoutMirroring.enabled:definition.variant==="rtl";LayoutMirroring.childrenInherit:true
            actions:definition.actionsMode==="empty" ? null : definition.actionsMode==="zero" ? stateZero : definition.actionsMode==="two" ? stateTwo : stateAction
            Component.onCompleted:{if(definition.variant==="custom-icon")icon=stateArchive}
        }
    }
    Component {
        id:errorState
        BleeckerErrorState {
            width:definition.variant==="intrinsic" ? implicitWidth : Number(definition.size)
            title:definition.title;message:definition.text;enabled:!definition.flag
            LayoutMirroring.enabled:definition.variant==="rtl";LayoutMirroring.childrenInherit:true
            actions:definition.actionsMode==="empty" ? null : definition.actionsMode==="zero" ? stateZero : definition.actionsMode==="two" ? stateTwo : stateAction
        }
    }
    Component {id:stateZero;Item {implicitWidth:0;implicitHeight:0}}
    Component {id:stateAction;BleeckerButton {text:"Create 0";maximumWidth:definition.variant==="intrinsic" ? -1 : parent.availableWidth}}
    Component {id:stateTwo;Row {spacing:12;BleeckerButton {text:"Create"} BleeckerButton {text:"Import";variant:"secondary"}}}
    Component {
        id:stateArchive
        Item {
            PixelAlignment {id:archiveMetrics;target:parent}
            implicitWidth:archiveMetrics.devicePixelRatio<2 ? 34 : 34.5;implicitHeight:archiveMetrics.devicePixelRatio<2 ? 30 : 30.5
            Canvas {
                anchors.fill:parent
                onPaint:{const c=getContext("2d");c.reset();c.strokeStyle=BleeckerTheme.palette.sea;c.lineWidth=1.8;c.strokeRect(width*0.18,height*0.30,width*0.64,height*0.56);c.strokeRect(width*0.12,height*0.15,width*0.76,height*0.15);c.beginPath();c.moveTo(width*0.40,height*0.48);c.lineTo(width*0.60,height*0.48);c.stroke()}
            }
        }
    }
    Component {
        id:loadingOverlay
        BleeckerLoadingOverlay {
            width:definition.variant==="intrinsic" ? implicitWidth : Number(definition.size)
            height:definition.variant==="intrinsic" ? implicitHeight : 300
            message:definition.text
            LayoutMirroring.enabled:definition.variant==="rtl";LayoutMirroring.childrenInherit:true
        }
    }
    Component {
        id:accordion
        BleeckerAccordion {
            width:definition.variant === "intrinsic" ? implicitWidth : Number(definition.size)
            title:window.accordionTitle;initiallyExpanded:definition.value===1;enabled:!definition.flag
            LayoutMirroring.enabled:definition.variant === "rtl";LayoutMirroring.childrenInherit:true
            content:definition.variant === "empty-content" ? null : definition.variant === "zero-content" ? accordionZero
                : definition.variant === "two-rows" ? accordionTwo : definition.variant === "counter" || (definition.fixture.startsWith("accordion-action-") && definition.variant !== "body-update") ? accordionCounter : accordionCopy
        }
    }
    Component {
        id:accordionCopy
        AccordionText {
            text:window.accordionBodyText;wrapWidth:parent.availableWidth
            Component.onCompleted:window.accordionMounts++
            Component.onDestruction:window.accordionUnmounts++
        }
    }
    Component {
        id:accordionZero
        Item {
            implicitWidth:0;implicitHeight:0
            Component.onCompleted:window.accordionMounts++
            Component.onDestruction:window.accordionUnmounts++
        }
    }
    Component {
        id:accordionTwo
        Column {
            spacing:10
            AccordionText {text:"First row"}
            AccordionText {text:"Second row"}
            Component.onCompleted:window.accordionMounts++
            Component.onDestruction:window.accordionUnmounts++
        }
    }
    Component {
        id:accordionCounter
        T.Button {
            id:button
            objectName:"referenceAccordionCounter"
            property int count:0
            implicitWidth:label.implicitWidth;implicitHeight:label.height
            padding:0;background:null;opacity:!enabled ? 0.5 : down ? 0.75 : 1
            text:"Counter "+count
            contentItem:AccordionText {id:label;text:button.text}
            onClicked:{count++;window.accordionCounterValue=count}
            Component.onCompleted:{window.accordionMounts++;window.accordionCounterValue=count}
            Component.onDestruction:window.accordionUnmounts++
        }
    }
    Component {
        id: searchField
        BleeckerSearchField { width: definition.value; size: definition.size; error: definition.variant === "error"; text: definition.text; placeholderText: "Search editions"; enabled: !definition.flag }
    }
    Component {
        id: filterChip
        BleeckerFilterChip {
            text: definition.text; selected: definition.flag
            removable: definition.variant.startsWith("removable")
            enabled: !definition.variant.endsWith("disabled")
            width: definition.value > 0 ? definition.value : implicitWidth
        }
    }
    Component {
        id: collectionFilters
        BleeckerCollectionFilters {
            width: definition.value; query: definition.text; enabled: !definition.flag
            content: definition.variant === "tall" ? collectionTall : window.collectionHasChip ? collectionChip : null
        }
    }
    Component { id: collectionTall; Rectangle { implicitWidth: 100; implicitHeight: 84; color: BleeckerTokens.colors.light.sea } }
    Component {
        id: collectionChip
        BleeckerFilterChip {
            text: "Edition"; selected: window.collectionSelected; removable: true
            onClicked: { window.collectionActivations++; window.collectionSelected=!window.collectionSelected }
            onRemoveRequested: { window.collectionRemovals++; window.collectionHasChip=false }
        }
    }
    Component {
        id: slider
        BleeckerSlider {
            width: definition.value; value: window.sliderValue; enabled: !definition.flag
            from: definition.size === "signed" ? -5 : definition.size === "shifted" ? 10 : 0
            to: definition.size === "signed" ? 5 : definition.size === "shifted" ? 22 : definition.size === "decimal" ? 0.3 : 1
            stepSize: {
                const steps={unit:0,signed:0.5,shifted:3,quarter:0.25,dense:0.01,tiny:0.000001,odd:0.3,odd2:0.26,decimal:0.1}
                if (!(definition.size in steps)) throw new Error("Unknown slider range fixture: "+definition.size)
                return steps[definition.size]
            }
            onMoved: { window.sliderValue=value;window.sliderEdits++ }
        }
    }
    function boundOptions() {
        if (definition.variant === "empty") return []
        const labels=["long","narrow"].includes(definition.variant) ? ["Morning edition","Evening edition","Weekend edition"]
            : definition.variant === "multiline" ? ["First\nline","Disabled","Last\nline"] : ["Alpha","Disabled","Gamma"]
        return [{value:"a",label:labels[0],disabled:definition.variant === "all-disabled"},{value:"b",label:labels[1],disabled:true},{value:"c",label:labels[2],disabled:definition.variant === "all-disabled"}]
    }
    Component {
        id: boundSelectionFrame
        Item {
            id: frame
            enabled: !definition.flag
            implicitWidth: definition.value > 0 ? definition.value : body.item ? body.item.implicitWidth : 0
            implicitHeight: body.item ? body.item.implicitHeight : 0
            LayoutMirroring.enabled: definition.variant === "rtl"
            LayoutMirroring.childrenInherit: true
            Item {
                width: body.width; height: body.height
                anchors.centerIn: parent; anchors.alignWhenCentered: false
                Loader {
                    id: body
                    width: item ? Math.min(frame.width,item.implicitWidth) : 0
                    sourceComponent: definition.api === "BleeckerTabs" ? tabsBody : segmentsBody
                    onLoaded: item.objectName="bleeckerBoundSelectionBody"
                }
            }
        }
    }
    Component {
        id: tabsBody
        BleeckerTabs {
            selection: window.boundSelection; options: window.boundOptions()
            onActivated: value => { window.boundSelection=value;window.boundActivations++ }
        }
    }
    Component {
        id: segmentsBody
        BleeckerSegmentedControl {
            selection: window.boundSelection; options: window.boundOptions()
            onActivated: value => { window.boundSelection=value;window.boundActivations++ }
        }
    }
    Component {
        id: iconButton
        BleeckerIconButton {
            id: icon
            size: definition.size;variant:definition.variant;enabled:!definition.flag
            accessibilityLabel: "Continue"
            icon: NavigationIcon {
                direction: {
                    if (definition.text === "chevron.left") return "left"
                    if (definition.text === "chevron.right") return "right"
                    throw new Error("Unknown icon fixture symbol: "+definition.text)
                }
                color:icon.foregroundColor;pixelSize:icon.glyphPixelSize
            }
            onClicked: window.iconCalls++
        }
    }
    Component {
        id: paginationIntegerFrame
        Item {
            id: frame
            enabled: !definition.flag
            implicitWidth: definition.variant === "narrow" ? 260 : pager.naturalWidth
            implicitHeight: pager.implicitHeight
            LayoutMirroring.enabled: definition.variant === "rtl";LayoutMirroring.childrenInherit: true
            BleeckerPagination {
                id: pager
                objectName: "bleeckerPaginationBody"
                anchors.centerIn:parent;anchors.alignWhenCentered:false
                width: Math.min(frame.width,naturalWidth)
                page: window.integerPage;pageCount:window.integerCount;locale:Qt.locale("en_US")
                onPageRequested: page => {
                    window.integerCalls++;window.integerRequested=page
                    if (definition.variant !== "no-handler") window.integerPage=page
                }
            }
        }
    }
    Component {
        id: paginationFrame
        Item {
            id: frame
            enabled: !definition.flag
            implicitWidth: definition.variant === "narrow" ? 140 : definition.variant === "wide" ? 400 : pager.naturalWidth
            implicitHeight: pager.implicitHeight
            LayoutMirroring.enabled: definition.variant === "rtl";LayoutMirroring.childrenInherit: true
            BleeckerPagination {
                id: pager
                objectName: "bleeckerPaginationBody"
                anchors.centerIn: parent;anchors.alignWhenCentered: false
                width: Math.min(frame.width,naturalWidth)
                page: window.pageValue;pageCount:window.pageTotal;locale:Qt.locale("en_US")
                onPageRequested: page => {
                    window.pageRequests++;window.lastPageRequest=page
                    if (definition.variant !== "no-handler") window.pageValue=page
                }
            }
        }
    }
    Component { id: button; BleeckerButton { text: "Publish" } }
    Component {
        id: secureField
        BleeckerSecureField {
            width: definition.value; placeholderText: "Passphrase"; text: definition.text
            enabled: !definition.flag || (definition.variant.startsWith("revealed-") && !revealed)
        }
    }
    Component {
        id: checkbox
        BleeckerCheckbox {
            size: definition.size; checked: definition.flag; text: definition.text
            enabled: !definition.variant.endsWith("disabled")
            width: definition.value > 0 ? definition.value : implicitWidth
        }
    }
    Component { id: searchGlyph; SearchGlyph {} }
    Component {
        id: select
        BleeckerSelect {
            width: definition.value; selection: definition.text; enabled: !definition.flag
            leading: definition.variant === "leading" ? searchGlyph : null
            options: {
                if (definition.variant === "empty") return []
                if (definition.variant === "open-long") {
                    const rows=[];for(let i=0;i<40;i++) rows.push({value:String(i),label:"Edition "+i,disabled:i===39});return rows
                }
                const label=definition.variant === "newline" ? "First line\nSecond line" : definition.variant === "constrained" ? "A substantially longer choice needs truncation" : "Morning edition"
                return [{value:"a",label:label},{value:"b",label:"Disabled edition",disabled:true},{value:"c",label:"Evening edition"}]
            }
            Component.onCompleted: if (definition.variant.startsWith("open-")) Qt.callLater(() => popup.open())
        }
    }
    Component { id: sectionAction; Rectangle { width: 80; height: 24; color: BleeckerTheme.palette.live } }
    Component {
        id: sectionHeader
        BleeckerSectionHeader {
            title: definition.text; width: definition.value
            subtitle: definition.variant === "empty" ? "" : "Ready for review"
            hasSubtitle: definition.variant !== "omitted"; actions: sectionAction
        }
    }
    Component {
        id: dashboardSection
        BleeckerDashboardSection {
            title: definition.text; width: definition.value
            subtitle: definition.variant === "empty" ? "" : "Ready for review"
            hasSubtitle: definition.variant !== "omitted"; actions: sectionAction
            Rectangle { width: 180; height: 40; color: BleeckerTheme.palette.sea }
        }
    }
    Component {
        id: dashboardGrid
        BleeckerDashboardGrid {
            width: definition.value; minimumColumnWidth: definition.size === "sm" ? 200 : 260
            tiles: definition.variant === "empty" ? [] : [{id:1,height:30,color:BleeckerTheme.palette.sea},{id:2,height:50,color:BleeckerTheme.palette.desert},{id:3,height:40,color:BleeckerTheme.palette.live}]
            tile: Rectangle { implicitHeight: tileData.height; color: tileData.color }
        }
    }
    Component {
        id: appShell
        BleeckerAppShell {
            width: 700; height: 300; sidebarWidth: definition.value
            sidebar: Rectangle { implicitHeight: 80; color: BleeckerTheme.palette.sea }
            header: Rectangle { implicitHeight: definition.flag ? 90 : 30; color: BleeckerTheme.palette.desert }
            content: Rectangle { color: BleeckerTheme.palette.live }
        }
    }
    Component {
        id: footer
        BleeckerFooter {
            width: 300
            Loader {
                anchors.horizontalCenter: parent.horizontalCenter
                sourceComponent: definition.variant === "block" ? footerBlock : footerText
            }
        }
    }
    Component { id: footerBlock; Rectangle { width: 180; height: 40; color: BleeckerTheme.palette.sea } }
    Component { id: footerText; T.Label { text: definition.text; color: palette.windowText } }
    Component {
        id: feed
        BleeckerFeedItem {
            width: definition.value; author: definition.text; timestamp: "12 Oct"
            Rectangle { width: 180; height: 40; color: BleeckerTheme.palette.sea }
        }
    }
    Component {
        id: progressStack
        BleeckerProgressStack {
            width: 240; height: definition.value
            segments: [{id:"a",value:definition.variant === "negative" ? -1 : definition.variant === "overflow" ? 0.7 : definition.variant === "zero" ? 0 : 0.25,color:BleeckerTheme.palette.sea},
                {id:"b",value:definition.variant === "overflow" ? 0.7 : 0.25,color:BleeckerTheme.palette.live}]
        }
    }
    Component { id: spinner; BleeckerLoadingSpinner { size: definition.size } }
    Component {
        id: textField
        BleeckerTextField {
            width: 240; placeholderText: "Title"; text: definition.text
            size: definition.size; error: definition.flag
            enabled: definition.variant !== "disabled"
        }
    }
    Component { id: textArea; BleeckerTextArea { width: 240; height: 120; minimumHeight: 120; text: definition.text } }
    Component {
        id: field
        BleeckerField {
            id: referenceField
            width: 240; label: "Title"
            readonly property string mode: definition.variant
            optional: mode === "optional"
            hasDescription: ["description", "both", "optional", "empty-present"].indexOf(mode) >= 0
            hasError: ["error", "both", "empty-present"].indexOf(mode) >= 0
            description: mode === "empty-present" ? "" : "Visible helper text"
            error: mode === "empty-present" ? "" : "Enter a title"
            BleeckerTextField { width: parent.width; placeholderText: "Title"; text: definition.text; error: referenceField.hasError }
        }
    }
    Component { id: switchControl; BleeckerSwitch { text: "Notifications"; checked: definition.flag; enabled: definition.variant !== "disabled" } }
    Component {
        id: toggle
        BleeckerToggleButton {
            text: "Pin"; selected: definition.flag
            variant: definition.variant === "inherited" ? "default" : definition.variant
            // The inherited source system font remains an unresolved proposed exception.
        }
    }
    Component {
        id: segments
        BleeckerSegmentedControl {
            selection: definition.text
            options: [{value: "a", label: "One"}, {value: "b", label: "Skip", disabled: true}, {value: "c", label: "Three"}]
        }
    }
    Component { id: separator; BleeckerSeparator { vertical: definition.flag; width: definition.flag ? 1 : 240; height: definition.flag ? 100 : 1 } }
    Component { id: skeleton; BleeckerSkeleton { width: 180; height: 24; radius: definition.value } }
    Component { id: bauhaus; BleeckerBauhausBackground { width: 240; height: 120 } }
    Component { id: progress; BleeckerProgress { width: 240; value: definition.value; size: definition.size; variant: definition.variant } }
    Component {
        id: buttonGroup
        BleeckerButtonGroup { BleeckerButton { size: "xs"; text: "Short" } BleeckerButton { size: "lg"; text: "Tall" } }
    }
    Component {
        id: header
        BleeckerHeader {
            width: 460
            leading: Component { Rectangle { width: 32; height: 20; color: BleeckerTheme.palette.sea } }
            center: Component { Rectangle { width: 160; height: 24; color: BleeckerTheme.palette.desert } }
            trailing: Component { Rectangle { width: 90; height: 16; color: BleeckerTheme.palette.live } }
        }
    }
    Component {
        id: panelLayout
        BleeckerPanelLayout {
            width: 460; height: 92; leadingWidth: 100; trailingWidth: 120
            leading: Component { Rectangle { color: BleeckerTheme.palette.muted } }
            content: Component { BleeckerBauhausBackground {} }
            trailing: Component { Rectangle { color: BleeckerTheme.palette.card } }
        }
    }
    Component {
        id: card
        BleeckerCard { paddingSize: definition.size; variant: definition.variant; Rectangle { width: 80; height: 32; color: BleeckerTheme.palette.sea } }
    }
    Component {
        id: panel
        BleeckerPanel {
            title: definition.variant === "present" ? "Titled panel" : ""
            hasTitle: definition.variant !== "omitted"
            Rectangle { width: 180; height: 32; color: BleeckerTheme.palette.sea }
        }
    }
    Component { id: attention; BleeckerAttentionSurface { hue: 210; intensity: definition.value; Rectangle { width: 180; height: 32; color: BleeckerTheme.palette.sea } } }
    Component { id: status; BleeckerStatusBadge { text: definition.variant; variant: definition.variant } }
    Component { id: notification; BleeckerNotificationBadge { count: definition.value } }
    Component { id: eyebrow; BleeckerEyebrow { text: "Cards and badges" } }
    Component {
        id: avatar
        BleeckerAvatar {
            size: definition.size
            name: definition.variant === "image" ? "Emoji Developer" : definition.text
            source: definition.variant === "image" ? "qrc:/avelino/fixtures/avatar-wide.ppm" : ""
        }
    }
    Component {
        id: dataList
        BleeckerDataList {
            width: 240
            rows: [{id: 1, label: "First row"}, {id: 2, label: "Second row"}, {id: 3, label: "Final row"}]
            rowContent: Component {
                T.Label {
                    text: parent.row.label; width: parent.width
                    font.family: BleeckerTheme.secondaryFont
                    font.pointSize: BleeckerFonts.pointSizeForPixels(13)
                    color: BleeckerTheme.palette.textSecondary
                }
            }
        }
    }
    Component {
        id: timeline
        BleeckerTimelineItem {
            width: 300; title: definition.text; date: "12 Oct"; last: definition.flag
            // The source's non-final connector fills the offered vertical allocation.
            height: definition.flag ? implicitHeight : definition.height
            T.Label { text: "Bulletin ready"; color: palette.windowText }
        }
    }
    Component { id: surface; BleeckerSurface { width: 240; height: 100; radius: definition.value; Rectangle { anchors.fill: parent; color: BleeckerTheme.palette.sea } } }
}

import QtQuick
import QtQuick.Layouts
import QtQuick.Templates as T
import Avelino

Window {
    id: window
    readonly property var definition: captureDefinition
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
                "BleeckerButton": button, "BleeckerLoadingSpinner": spinner,
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
                "BleeckerFooter": footer, "BleeckerFeedItem": feed, "BleeckerProgressStack": progressStack
            }
            if (!components[definition.api]) throw new Error("Unimplemented reference API: " + definition.api)
            return components[definition.api]
        }
        onLoaded: item.objectName = "referenceCaseComponent"
    }
    Component { id: button; BleeckerButton { text: "Publish" } }
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

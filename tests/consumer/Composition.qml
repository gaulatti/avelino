import QtQuick
import QtQuick.Templates as T
import Avelino

Window {
    id: window
    width: 840; height: 560; visible: true
    title: "Avelino — composition consumer"
    property int reviewInvocations: 0
    readonly property real fixtureTextScale: BleeckerTheme.textScale
    Component.onCompleted: { BleeckerTheme.dark = consumerDark; BleeckerTheme.textScale = consumerTextScale; BleeckerTheme.reducedMotion = true }
    BleeckerAppShell {
        anchors.fill: parent
        objectName: "appShell"
        sidebar: Column {
            spacing: 16
            T.Label { text: "Newsroom"; font.family: BleeckerTheme.primaryFont; font.pointSize: BleeckerFonts.pointSizeForPixels(18); color: palette.windowText }
            BleeckerButton { text: "Overview"; variant: "subtle"; width: 240 }
            BleeckerButton { text: "Library"; variant: "ghost"; width: 240 }
        }
        header: T.Label { text: "Workspace"; color: palette.windowText; font.pointSize: BleeckerFonts.pointSizeForPixels(17) }
        content: Item {
            BleeckerDashboardSection {
                id: section
                objectName: "dashboardSection"
                width: parent.width; title: "Editorial desk"; subtitle: "Your current edition"
                actions: BleeckerButton { objectName: "reviewAction"; text: "Review"; size: "xs"; onClicked: window.reviewInvocations++ }
                BleeckerDashboardGrid {
                    objectName: "dashboardGrid"
                    width: parent.width; minimumColumnWidth: 200
                    tiles: [{title:"Morning bulletin",author:"Jane Doe",progress:0.4},{title:"Evening bulletin",author:"Alex Reed",progress:0.7}]
                    tile: BleeckerCard {
                        paddingSize: "sm"
                        Column {
                            width: parent.width; spacing: 12
                            T.Label { text: tileData.title; font.family: BleeckerTheme.primaryFont; font.pointSize: BleeckerFonts.pointSizeForPixels(14); color: palette.windowText }
                            BleeckerProgressStack {
                                width: parent.width
                                segments: [{id:"draft",value:tileData.progress,color:BleeckerTheme.palette.sea},{id:"review",value:0.15,color:BleeckerTheme.palette.live}]
                            }
                        }
                    }
                }
            }
            BleeckerFeedItem {
                objectName: "feedItem"
                y: section.height + 24; width: parent.width
                author: "Jane Doe"; timestamp: "12 Oct"
                T.Label { text: "Edition ready for review"; color: palette.windowText; font.family: BleeckerTheme.secondaryFont; font.pointSize: BleeckerFonts.pointSizeForPixels(13) }
            }
            BleeckerFooter {
                objectName: "footer"
                anchors.bottom: parent.bottom; width: parent.width
                T.Label { text: "Bleecker • Avelino"; color: palette.windowText; anchors.horizontalCenter: parent.horizontalCenter }
            }
        }
    }
}

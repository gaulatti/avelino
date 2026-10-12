import QtQuick
import Avelino

Window {
    id: window
    width: 840
    height: 600
    visible: true
    title: "Avelino — mirror workbench"
    color: BleeckerTheme.palette.background
    Component.onCompleted: { BleeckerTheme.dark = captureDark; BleeckerTheme.reducedMotion = true }
    Text { x: 32; y: 24; text: "Actions and editing"; font.family: BleeckerTheme.primaryFont; font.pixelSize: 24; font.weight: Font.DemiBold; color: BleeckerTheme.palette.textPrimary }
    Text { x: 32; y: 62; text: "Mirror fixtures — verification pending"; font.family: BleeckerTheme.secondaryFont; font.pixelSize: 13; color: BleeckerTheme.palette.textSecondary }
    Column {
        x: 32; y: 104; spacing: 12
        Repeater {
            model: ["primary", "secondary", "outline", "subtle", "ghost", "link", "destructive"]
            Row {
                required property string modelData
                spacing: 12
                Repeater {
                    model: ["xs", "sm", "md", "lg"]
                    BleeckerButton {
                        required property string modelData
                        size: modelData
                        variant: parent.modelData
                        text: "Publish"
                        onClicked: feedback.text = variant + " action invoked"
                    }
                }
            }
        }
        Row {
            spacing: 12
            BleeckerButton { text: "Disabled"; enabled: false }
            BleeckerButton { text: "Loading"; loading: true }
        }
    }
    Column {
        x: 500; y: 104; spacing: 20
        BleeckerTextField { placeholderText: "Title"; objectName: "titleField" }
        BleeckerTextField { placeholderText: "Error"; error: true; text: "Review required" }
        BleeckerTextField { placeholderText: "Disabled field"; enabled: false }
        Text { id: feedback; text: "Invoke a button or edit a field"; font.family: BleeckerTheme.secondaryFont; font.pixelSize: 12; color: BleeckerTheme.palette.textSecondary }
    }
}

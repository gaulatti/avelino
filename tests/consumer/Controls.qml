import QtQuick
import Avelino

Window {
    property int toggleInvocations: 0
    width: 680; height: 448; visible: true
    title: "Avelino installed controls"
    color: BleeckerTheme.palette.background
    Component.onCompleted: {
        BleeckerTheme.dark = consumerDark
        BleeckerTheme.textScale = consumerTextScale
        BleeckerTheme.reducedMotion = true
    }
    Column {
        x: 24; y: 24; width: 280; spacing: 20
        BleeckerField {
            objectName: "formField"
            width: parent.width; label: "Title"; optional: true; description: "Visible helper text"
            BleeckerTextField { objectName: "formInput"; width: parent.width; placeholderText: "Title" }
        }
        BleeckerTextArea { objectName: "textArea"; width: parent.width; minimumHeight: 120; accessibleName: "Notes" }
        BleeckerSwitch { objectName: "switch"; text: "Notifications" }
        BleeckerToggleButton {
            objectName: "toggle"; text: "Pin"; variant: "outline"
            onClicked: { selected = !selected; toggleInvocations++ }
        }
    }
    Column {
        x: 340; y: 24; width: 316; spacing: 24
        BleeckerEyebrow { text: "Choose a view" }
        BleeckerSegmentedControl {
            objectName: "segments"
            options: [{value:"a",label:"One"},{value:"b",label:"Skip",disabled:true},{value:"c",label:"Three"}]
            selection: "a"
        }
        BleeckerField {
            width: parent.width; label: "Required title"; error: "Enter a title"
            BleeckerTextField { width: parent.width; error: true; placeholderText: "Required" }
        }
        BleeckerSwitch { text: "Already enabled"; checked: true }
        BleeckerToggleButton { text: "Selected"; selected: true }
    }
}

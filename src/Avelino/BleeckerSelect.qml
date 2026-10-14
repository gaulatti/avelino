import QtQuick
import QtQuick.Templates as T

T.Button {
    id: control
    required property var selection
    property var options: []
    property string placeholder: "Select…"
    property Component leading
    readonly property string displayText: {
        const option=options.find(option => option.value === selection)
        return option ? option.label : placeholder
    }
    readonly property bool presented: choicePopup.visible
    readonly property var popup: choicePopup
    signal activated(var value)
    implicitWidth: label.unwrappedWidth+leftPadding+rightPadding+43+(leadingSlot.item ? leadingSlot.width+10 : 0)
    implicitHeight: Math.max(40,implicitContentHeight)
    leftPadding: 14; rightPadding: 14; topPadding: 0; bottomPadding: 0
    font.family: BleeckerTheme.primaryFont
    font.pointSize: BleeckerFonts.pointSizeForPixels(14*BleeckerTheme.textScale)
    opacity: enabled ? 1 : 0.6
    focusPolicy: Qt.StrongFocus
    Accessible.role: Accessible.ComboBox
    Accessible.name: displayText
    onClicked: choicePopup.visible ? choicePopup.close() : choicePopup.open()
    onEnabledChanged: if (!enabled && choicePopup) choicePopup.close()
    onOptionsChanged: {
        if (!choicePopup || !choicePopup.visible) return
        Qt.callLater(() => {
            if (!choicePopup.visible) return
            choices.currentIndex=enabledIndex(0,1)
            choices.forceActiveFocus()
        })
    }
    function enabledIndex(start, step) {
        for (let i=start; i>=0 && i<options.length; i+=step)
            if (!options[i].disabled) return i
        return -1
    }
    function choose(index) {
        if (!enabled || index<0 || index>=options.length || options[index].disabled) return
        activated(options[index].value)
        choicePopup.close()
    }
    contentItem: Item {
        implicitHeight: Math.max(label.height,leadingSlot.height,chevron.height)
        Loader { id: leadingSlot; sourceComponent: control.leading; y: (parent.height-height)/2 }
        OwnedText {
            id: label
            objectName: "bleeckerSelectLabel"
            text: control.displayText; font: control.font
            x: leadingSlot.item ? leadingSlot.width+10 : 0
            elideWidth: Math.max(0,control.width-control.leftPadding-control.rightPadding-x-43)
            width: elideWidth
            y: (parent.height-height)/2
        }
        SelectionGlyph {
            id: chevron
            objectName: "bleeckerSelectChevron"
            symbol: "chevronDown"; x: parent.width-width; y: (parent.height-height)/2
        }
    }
    background: ContinuousSurface {
        objectName: "bleeckerSelectSurface"
        radius: BleeckerTokens.radii.ui; color: BleeckerTheme.palette.card
        borderColor: control.presented ? BleeckerTheme.alpha(BleeckerTheme.palette.sea,0.75) : BleeckerTheme.palette.border
    }
    ContinuousSurface {
        anchors.fill: parent; color: "transparent"; radius: BleeckerTokens.radii.ui
        borderColor: BleeckerTheme.alpha(BleeckerTheme.palette.ring,0.75)
        visible: control.visualFocus; Accessible.ignored: true
    }
    T.Popup {
        id: choicePopup
        objectName: "bleeckerSelectPopup"
        popupType: T.Popup.Item
        readonly property real chromeInset: 13
        x: (control.width-width)/2; y: control.height; width: 220+chromeInset*2
        implicitHeight: Math.min(288,choices.contentHeight)+chromeInset*2
        padding: chromeInset; margins: 8; focus: true; modal: false; dim: false
        enabled: control.enabled
        closePolicy: T.Popup.CloseOnEscape | T.Popup.CloseOnPressOutside
        onOpened: {
            choices.currentIndex=control.enabledIndex(0,1)
            choices.positionViewAtBeginning()
            choices.keyboardNavigationActive=false
            choices.forceActiveFocus()
        }
        onClosed: if (control.enabled && control.visible) control.forceActiveFocus()
        background: ContinuousSurface {
            objectName: "bleeckerSelectPopupSurface"
            color: BleeckerTheme.palette.popover; radius: BleeckerTokens.radii.ui
            borderColor: BleeckerTheme.palette.border
        }
        contentItem: ListView {
            id: choices
            objectName: "bleeckerSelectChoices"
            property bool keyboardNavigationActive: false
            clip: true; spacing: 2; boundsBehavior: Flickable.StopAtBounds
            model: control.options; keyNavigationEnabled: false
            header: Item { height: 4 }
            footer: Item { height: 4 }
            function move(start, step) {
                const index=control.enabledIndex(start,step)
                if (index>=0) { keyboardNavigationActive=true; currentIndex=index; positionViewAtIndex(index,ListView.Contain); forceActiveFocus() }
            }
            Keys.onPressed: event => {
                if (event.key===Qt.Key_Down) move(currentIndex+1,1)
                else if (event.key===Qt.Key_Up) move(currentIndex<0 ? count-1 : currentIndex-1,-1)
                else if (event.key===Qt.Key_Home) move(0,1)
                else if (event.key===Qt.Key_End) move(count-1,-1)
                else if (event.key===Qt.Key_Return || event.key===Qt.Key_Enter || event.key===Qt.Key_Space) control.choose(currentIndex)
                else { event.accepted=false; return }
                event.accepted=true
            }
            delegate: Item {
                id: row
                required property var modelData
                required property int index
                width: choices.width; height: optionButton.implicitHeight
                enabled: !modelData.disabled
              T.ItemDelegate {
                id: optionButton
                readonly property var modelData: row.modelData
                readonly property int index: row.index
                objectName: "bleeckerSelectOption"+index
                readonly property bool selected: modelData.value === control.selection
                text: modelData.label; enabled: !modelData.disabled
                x: 4; width: Math.max(0,choices.width-8); implicitHeight: Math.max(36,optionLabel.height)
                leftPadding: 12; rightPadding: 12; topPadding: 0; bottomPadding: 0
                font: control.font; focusPolicy: Qt.TabFocus
                opacity: enabled ? 1 : 0.5
                Accessible.name: text
                Accessible.description: selected ? qsTr("Selected") : ""
                onActiveFocusChanged: if (activeFocus) choices.currentIndex=index
                onVisualFocusChanged: if (visualFocus) choices.keyboardNavigationActive=true
                onClicked: control.choose(index)
                contentItem: Item {
                    implicitHeight: optionLabel.height
                    OwnedText {
                        id: optionLabel
                        text: optionButton.text; font: optionButton.font
                        elideWidth: Math.max(0,optionButton.width-optionButton.leftPadding-optionButton.rightPadding-28)
                        width: elideWidth
                        y: (parent.height-height)/2
                        color: optionButton.selected ? BleeckerTheme.palette.sea : BleeckerTheme.palette.textPrimary
                    }
                    SelectionGlyph {
                        symbol: "checkmark"; visible: optionButton.selected
                        color: BleeckerTheme.palette.sea; x: parent.width-width; y: (parent.height-height)/2
                    }
                }
                background: ContinuousSurface {
                    radius: BleeckerTokens.radii.button; borderWidth: 0
                    color: choices.keyboardNavigationActive && optionButton.index===choices.currentIndex ? BleeckerTheme.palette.muted : "transparent"
                }
              }
            }
            T.ScrollBar.vertical: T.ScrollBar {
                objectName: "bleeckerSelectScrollBar"
                width: 6; minimumSize: 0.08
                opacity: active || hovered ? 1 : 0
                contentItem: Rectangle { radius: 3; color: BleeckerTheme.alpha(BleeckerTheme.palette.textSecondary,0.5) }
                background: null
            }
        }
    }
}

import QtQuick
import QtQuick.Window
import QtQuick.Templates as T

// Qt presentation adapter. The Modal stays a content view; this owner manages
// dismissal, a separate popup window and the lifetime of caller-created content.
T.Popup {
    id:dialog
    required property string title
    property real modalWidth:480
    property Component content
    readonly property Item modalItem:slot.item
    readonly property Window presentationWindow:modalItem ? modalItem.Window.window:null
    popupType:T.Popup.Window;modal:true;dim:false;focus:true
    closePolicy:T.Popup.NoAutoClose
    padding:0;margins:0;background:null
    width:modalWidth;implicitWidth:modalWidth
    implicitHeight:slot.item ? slot.item.implicitHeight:77
    height:implicitHeight
    enter:null;exit:null
    contentItem:Loader {
        id:slot;active:dialog.visible
        sourceComponent:Component {
            BleeckerModal {
                id:modal;title:dialog.title;modalWidth:dialog.modalWidth;font:dialog.font
                dismissAction:function(){dialog.close()}
                Loader {
                    sourceComponent:dialog.content
                    BleeckerLayout.flattenChildren:true
                    BleeckerLayout.participates:item!==null
                    readonly property font font:modal.presentationFont
                    readonly property color foregroundColor:modal.foreground
                }
            }
        }
    }
}

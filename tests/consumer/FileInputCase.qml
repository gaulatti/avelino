import QtQuick
import Avelino

Item {
    id:fixture;width:600;height:300
    property var configuration:({id:"default",types:["public.plain-text"],disabled:false,rtl:false,parentFont:false,parentRed:false,controlSize:"regular"})
    property var linuxContentTypes:["text/plain"]
    property url fixtureFolder:""
    property var results:[]
    property bool removeOnResult:false
    property bool visibleAtCallback:false
    property bool mounted:true
    readonly property Item control:slot.item
    LayoutMirroring.enabled:configuration.rtl;LayoutMirroring.childrenInherit:true
    function frame():var {
        function measure(item){const point=item.mapToItem(fixture,0,0);return {x:point.x,y:point.y,width:item.width,height:item.height}}
        return control&&control.presentationItem ? {body:measure(control.presentationItem),caller:measure(control)}:{}
    }
    function state():var {
        return {mounted:mounted,title:control ? control.title:null,enabled:control ? control.enabled:false,
            results:results,pickerVisible:control ? control.chooser.visible:false,sourceTypes:configuration.types,visibleAtCallback:visibleAtCallback}
    }
    component Input:BleeckerFileInput {
        widthOffer:fixture.configuration.width===undefined||fixture.configuration.width===null ? -1:fixture.configuration.width
        heightOffer:fixture.configuration.height===undefined||fixture.configuration.height===null ? -1:fixture.configuration.height
        maximumWidth:fixture.width
        maximumHeight:fixture.height
        width:widthOffer<0 ? implicitWidth:widthOffer
        height:heightOffer<0 ? implicitHeight:heightOffer
        allowedContentTypes:fixture.linuxContentTypes
        initialFolder:fixture.fixtureFolder.toString().length ? fixture.fixtureFolder:browser.defaultFolder()
        enabled:!fixture.configuration.disabled
        onResult:value=>{fixture.visibleAtCallback=chooser.visible;fixture.results=fixture.results.concat([value]);if(fixture.removeOnResult)fixture.mounted=false}
    }
    Component {id:defaultInput;Input {}}
    Component {id:namedInput;Input {title:fixture.configuration.title}}
    InheritedControl {
        anchors.fill:parent;padding:0;background:null;contentItem:null;focusPolicy:Qt.NoFocus;Accessible.ignored:true
        font.pixelSize:fixture.configuration.parentFont ? 28:13
        font.weight:fixture.configuration.parentFont ? Font.Bold:Font.Normal
        palette.windowText:fixture.configuration.parentRed ? BleeckerTheme.nativeRed:BleeckerTheme.nativeTextPrimary
        Loader {
            id:slot;active:fixture.mounted;anchors.centerIn:parent;anchors.alignWhenCentered:false
            sourceComponent:fixture.configuration.title===undefined||fixture.configuration.title===null ? defaultInput:namedInput
        }
    }
}

import QtQuick
import Avelino
Window {
    id:window;width:840;height:560;visible:true;color:BleeckerTheme.palette.background
    title:"Avelino installed spinner presentation"
    property bool reduced:true
    property bool showMedium:true
    property bool busy:true
    property bool loading:true
    property int actions:0
    onReducedChanged:BleeckerTheme.reducedMotion=reduced
    Component.onCompleted:{BleeckerTheme.dark=consumerDark;BleeckerTheme.textScale=consumerTextScale;BleeckerTheme.reducedMotion=reduced}
    BleeckerEyebrow {x:24;y:24;text:"Loading indicators"}
    BleeckerLoadingSpinner {objectName:"spinnerSmall";x:48;y:80;size:"sm"}
    BleeckerLoadingSpinner {objectName:"spinnerMedium";x:128;y:72;visible:window.showMedium;running:window.busy}
    BleeckerLoadingSpinner {objectName:"spinnerLarge";x:224;y:72;size:"lg"}
    BleeckerLoadingSpinner {objectName:"spinnerWide";x:40;y:150;width:96;height:72}
    BleeckerLoadingSpinner {objectName:"spinnerNarrow";x:224;y:180;width:12;height:12}
    BleeckerLoadingSpinner {objectName:"spinnerCustom";x:320;y:72;color:"#d63d3d"}
    BleeckerButton {objectName:"spinnerLoadingButton";x:40;y:280;text:"Publish";loading:window.loading;onClicked:window.actions++}
    BleeckerTextField {objectName:"spinnerNextField";x:40;y:360;width:320;placeholderText:"Continue editing"}
}

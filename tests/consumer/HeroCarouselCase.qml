import QtQuick
import Avelino

Item {
    id:root
    required property var definition
    property bool mounted:true
    property int appearances:0
    property int disappearances:0
    property int callerInstances:0
    property var firstKeys:Object.create(null)
    property var slideInstances:Object.create(null)
    property var slideAppearances:Object.create(null)
    property var slideDisappearances:Object.create(null)
    property var activeSlideStates:Object.create(null)
    property var actions:[]
    readonly property Item control:body.item ? body.item.control:null
    width:640;height:400;clip:true
    function nativeNumber(value) {return value==="__native_nan__" ? NaN:value==="__native_positive_infinity__" ? Infinity:value==="__native_negative_infinity__" ? -Infinity:value}
    function keyFor(id) {
        const canonical=BleeckerSelectionTools.canonicalString(String(id))
        if(firstKeys[canonical]===undefined)firstKeys[canonical]=String(id)
        return firstKeys[canonical]
    }
    function newInstance(key) {const next=(slideInstances[key]||0)+1;slideInstances[key]=next;return next}
    function appeared(key,ordinal) {slideAppearances[key]=(slideAppearances[key]||0)+1;activeSlideStates[key]=[ordinal]}
    function disappeared(key,ordinal,currentId) {
        // Swift dictionaries retain the spelling first inserted into each map.
        // A first disappearance can arrive after an NFC-to-NFD data update.
        const spelling=Object.keys(slideDisappearances).find(value=>BleeckerSelectionTools.stringsEqual(value,currentId))
        const eventKey=spelling===undefined ? String(currentId):spelling
        slideDisappearances[eventKey]=(slideDisappearances[eventKey]||0)+1;activeSlideStates[key]=[]
    }
    function recordAction(id) {actions=actions.concat(id)}
    function resetCounters() {appearances=0;disappearances=0;callerInstances=0;firstKeys=Object.create(null);slideInstances=Object.create(null);slideAppearances=Object.create(null);slideDisappearances=Object.create(null);activeSlideStates=Object.create(null);actions=[]}
    function rect(item) {
        const a=item.mapToItem(root,0,0),b=item.mapToItem(root,item.width,item.height)
        return {x:a.x,y:a.y,width:b.x-a.x,height:b.y-a.y}
    }
    function frame() {
        if(!control)return {}
        const slides=Object.create(null)
        for(let i=0;i<control.itemCount;++i){const item=control.slideAt(i);if(item &&item.slideActive)slides[item.lifecycleKey]=rect(item)}
        return {carousel:rect(control),caller:rect(body.item.caller),slides:slides}
    }
    function state() {return {appearances:appearances,disappearances:disappearances,wrapperInstances:callerInstances,slideInstances:slideInstances,slideAppearances:slideAppearances,slideDisappearances:slideDisappearances,activeSlideStates:activeSlideStates,actions:actions}}
    function measurements() {return control ? control.layoutSnapshot():{}}
    function scrollTo(id) {
        if(!control)return
        const index=definition.items.findIndex(value=>BleeckerSelectionTools.stringsEqual(value.id,id))
        if(index<0)throw new Error("Unknown HeroCarousel scroll target")
        control.positionViewAtIndex(index,ListView.Beginning)
    }
    InheritedControl {
        anchors.fill:parent;padding:0;background:null;contentItem:null;Accessible.ignored:true
        font.family:root.definition.parentFont ? Qt.application.font.family:BleeckerFonts.primary
        font.pointSize:BleeckerFonts.pointSizeForPixels(root.definition.parentFont ? 28:13)
        font.weight:root.definition.parentFont ? Font.Bold:Font.Normal
        palette.windowText:root.definition.parentRed ? BleeckerTheme.nativeRed:BleeckerTheme.palette.textPrimary
        Loader {
            id:body;anchors.fill:parent;active:root.mounted
            onLoaded:{root.appearances++;root.callerInstances++}
            onActiveChanged:if(!active &&root.callerInstances>0)root.disappearances++
            sourceComponent:Component {
                Item {
                    id:scene
                    readonly property alias control:carousel
                    readonly property alias caller:caller
                    readonly property real offeredWidth:root.nativeNumber(root.definition.width)
                    readonly property real offeredHeight:root.definition.height===undefined ||root.definition.height===null ? NaN:root.nativeNumber(root.definition.height)
                    Item {
                        id:caller
                        x:(root.width-width)/2;y:(root.height-height)/2
                        width:scene.offeredWidth
                        height:root.definition.fitHeight ? carousel.height:root.definition.height===undefined ||root.definition.height===null ? root.height:scene.offeredHeight
                        BleeckerHeroCarousel {
                            id:carousel;width:caller.width
                            items:root.definition.items
                            enabled:!root.definition.disabled
                            LayoutMirroring.enabled:root.definition.rtl;LayoutMirroring.childrenInherit:true
                            slide:Component {HeroCarouselSlide {fixture:root}}
                        }
                        Binding {target:carousel;property:"height";value:caller.height;when:!root.definition.fitHeight}

                    }
                }
            }
        }
    }
}

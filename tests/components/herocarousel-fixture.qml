import QtQuick
import QtQuick.Templates as T
import Avelino

Item {
    id:fixture;width:640;height:400
    property bool mounted:true
    property bool publicView:false
    property bool mirrored:false
    property bool fixedSlides:false
    property bool removeOnInactive:false
    property bool removeOnData:false
    property int nextToken:0
    property var rows:[{id:"a",width:91,height:80},{id:"b",width:91,height:100},{id:"c",width:91,height:120}]
    property var identity:null
    readonly property var viewport:mount.item ? mount.item.viewport:null
    readonly property var presenter:mount.item ? mount.item.presenter:null
    Component {
        id:fill
        Rectangle {
            required property var slideData
            required property int slideIndex
            required property bool slideActive
            property int token:0
            implicitWidth:10;implicitHeight:slideData ? slideData.height:0
            BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:10;BleeckerLayout.fillsWidth:true
            color:"#2f5880"
            Component.onCompleted:token=++fixture.nextToken
            onSlideActiveChanged:if(!slideActive&&fixture.removeOnInactive)fixture.mounted=false
            onSlideDataChanged:if(token&&fixture.removeOnData)fixture.mounted=false
        }
    }
    Component {
        id:fixed
        Rectangle {
            required property var slideData
            required property bool slideActive
            property int token:0
            width:slideData ? slideData.width:0;height:slideData ? slideData.height:0
            color:"#2f5880"
            Component.onCompleted:token=++fixture.nextToken
        }
    }
    Component {
        id:publicViewport
        Item {
            readonly property alias viewport:carousel
            readonly property alias presenter:carousel.presenter
            BleeckerHeroCarousel {
                id:carousel;x:20;y:20;width:337;height:180
                items:fixture.rows;itemIdentity:fixture.identity
                LayoutMirroring.enabled:fixture.mirrored
                slide:fixture.fixedSlides ? fixed:fill
            }
        }
    }
    Loader {
        id:mount;anchors.fill:parent;active:fixture.mounted
        sourceComponent:fixture.publicView ? publicViewport:privateViewport
    }
    Component {
        id:privateViewport
            Item {
                readonly property alias viewport:view
                readonly property alias presenter:slides
                Flickable {
                    id:view;x:20;y:20;width:337;height:180;implicitHeight:slides.naturalHeight;clip:true
                    contentWidth:slides.documentWidth;contentHeight:height
                    HeroCarouselBase {
                        id:slides;viewport:view;width:view.width;height:view.height
                        items:fixture.rows;itemIdentity:fixture.identity
                        slide:fixture.fixedSlides ? fixed:fill
                    }
                }
            }
    }
}

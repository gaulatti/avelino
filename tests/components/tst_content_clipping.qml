import QtQuick
import QtTest
import Avelino

Item {
    id: root
    width: 800; height: 600
    PixelAlignment { id: displayAlignment; target: root }
    Component {
        id: fixture
        Rectangle {
            id: host
            width: 200; height: 160; color: "#123456"
            property alias card: card
            property alias ink: ink
            property alias stable: stable
            property int clicks: 0
            BleeckerCard {
                id: card; x: 20; y: 20; width: 120; height: 100
                paddingSize: "none"; variant: "transparent"
                Rectangle {
                    id: ink; x: -20; y: -20; width: 160; height: 140; color: "#ff0000"
                    MouseArea { anchors.fill: parent; onClicked: host.clicks++ }
                }
                Rectangle { id:stable;x:80;y:70;width:10;height:10;color:"yellow";visible:false }
            }
        }
    }
    Component {
        id: alertFixture
        Rectangle {
            width: 300; height: 180; color: "#123456"
            property alias alert: alert
            BleeckerAlert {
                id: alert; x: 20; y: 20; title: "Clipping"
                content: Item {
                    implicitWidth: 140; implicitHeight: 70
                    Rectangle { x: -200; y: -200; width: 600; height: 600; color: "red" }
                }
            }
        }
    }
    Component {
        id: chipFixture
        Rectangle {
            width: 240; height: 120; color: "#123456"
            property alias chip: chip
            BleeckerFilterChip { id: chip; x: 20; y: 20; text: "Capsule" }
        }
    }
    Component {
        id: nestedFixture
        Rectangle {
            width: 200; height: 160; color: "#123456"
            BleeckerCard {
                x: 20; y: 20; width: 120; height: 100; paddingSize: "none"; variant: "transparent"
                Rectangle { anchors.fill: parent; color: "red" }
                BleeckerCard {
                    objectName: "inner"; x: 40; y: 40; width: 60; height: 50
                    paddingSize: "none"; variant: "transparent"
                    Rectangle { x: -30; y: -30; width: 120; height: 110; color: "blue" }
                }
            }
        }
    }
    Component {
        id: textFixture
        Rectangle {
            id: textHost
            width:400;height:220;color:"#123456"
            property bool masked:false
            property real offset:0
            property real cardWidth:220
            property string buttonVariant:"primary"
            BleeckerButton {
                x:40+parent.offset;y:40+parent.offset;visible:!parent.masked
                text:"Raster preservation";variant:parent.buttonVariant
            }
            BleeckerCard {
                objectName:"rasterCard";x:20+parent.offset;y:20+parent.offset;width:parent.cardWidth;height:100
                visible:parent.masked;paddingSize:"none";variant:"transparent"
                BleeckerButton {objectName:"rasterButton";x:20;y:20;text:"Raster preservation";variant:textHost.buttonVariant}
            }
        }
    }
    TestCase {
        name: "GenericContentClipping"
        when: windowShown
        function init() { BleeckerTheme.dark=false; BleeckerTheme.textScale=1; BleeckerTheme.reducedMotion=true }
        // QuickTest's software item grab retains DPR pixels but crops to logical
        // dimensions. Capture a larger root and sample at actual device scale.
        function picture(item) { wait(30); return grabImage(root) }
        function colorAt(image,item,x,y) {
            const point=item.mapToItem(root,x,y),dpr=displayAlignment.devicePixelRatio
            return image.pixel(Math.floor(point.x*dpr),Math.floor(point.y*dpr))
        }
        function test_continuous_overflow_and_live_updates() {
            const host=createTemporaryObject(fixture,parent);verify(host)
            const image=picture(host)
            verify(host.card.roundedContentClipping)
            compare(colorAt(image,host,20,20),Qt.rgba(18/255,52/255,86/255,1))
            compare(colorAt(image,host,19,70),Qt.rgba(18/255,52/255,86/255,1))
            compare(colorAt(image,host,80,70),Qt.rgba(1,0,0,1))
            host.ink.color="blue"
            compare(colorAt(picture(host),host,80,70),Qt.rgba(0,0,1,1))
            host.card.width=80;host.card.height=60
            const resized=picture(host)
            compare(colorAt(resized,host,99,79),Qt.rgba(18/255,52/255,86/255,1))
            compare(colorAt(resized,host,110,70),Qt.rgba(18/255,52/255,86/255,1))
            compare(colorAt(resized,host,60,50),Qt.rgba(0,0,1,1))
            host.card.visible=false
            compare(colorAt(picture(host),host,60,50),Qt.rgba(18/255,52/255,86/255,1))
            host.card.visible=true
            compare(colorAt(picture(host),host,60,50),Qt.rgba(0,0,1,1))
        }
        function test_translucent_content_and_parent_opacity() {
            const host=createTemporaryObject(fixture,parent);host.ink.color="#80ff0000"
            const image=picture(host),pixel=colorAt(image,host,80,70)
            compare(colorAt(image,host,20,20),Qt.rgba(18/255,52/255,86/255,1))
            verify(pixel.r>0.52 && pixel.r<0.55)
            verify(pixel.g>0.09 && pixel.g<0.11)
            host.card.opacity=0.5
            const faded=colorAt(picture(host),host,80,70)
            verify(faded.r>0.29 && faded.r<0.32)
            verify(faded.g>0.14 && faded.g<0.16)
        }
        function test_sparse_opaque_content_keeps_empty_regions_transparent() {
            const host=createTemporaryObject(fixture,parent)
            host.ink.x=20;host.ink.y=20;host.ink.width=40;host.ink.height=40
            const image=picture(host)
            compare(colorAt(image,host,30,70),Qt.rgba(18/255,52/255,86/255,1))
            compare(colorAt(image,host,60,50),Qt.rgba(1,0,0,1))
            host.ink.x=60
            compare(colorAt(picture(host),host,60,50),Qt.rgba(18/255,52/255,86/255,1))
            compare(colorAt(picture(host),host,100,50),Qt.rgba(1,0,0,1))
        }
        function test_initially_empty_source_and_later_child_visibility() {
            const host=createTemporaryObject(fixture,parent)
            host.ink.visible=false
            compare(colorAt(picture(host),host,60,50),Qt.rgba(18/255,52/255,86/255,1))
            host.ink.visible=true
            compare(colorAt(picture(host),host,60,50),Qt.rgba(1,0,0,1))
            host.ink.visible=false
            compare(colorAt(picture(host),host,60,50),Qt.rgba(18/255,52/255,86/255,1))
        }
        function test_unchanged_islands_survive_other_content_updates() {
            const host=createTemporaryObject(fixture,parent);host.stable.visible=true
            compare(colorAt(picture(host),host,105,95),Qt.rgba(1,1,0,1))
            host.ink.color="blue"
            const image=picture(host)
            compare(colorAt(image,host,60,50),Qt.rgba(0,0,1,1))
            compare(colorAt(image,host,105,95),Qt.rgba(1,1,0,1))
        }
        function test_software_interior_text_pixels_data() {
            const rows=[]
            for(const offset of [0,0.25,0.5,0.75])
                for(const width of [220,220.5])
                    for(const variant of ["primary","ghost"])
                        rows.push({tag:offset+"-"+width+"-"+variant,offset:offset,width:width,variant:variant})
            return rows
        }
        function sameInteriorText(host,masked,plain) {
            const label=findChild(findChild(host,"rasterButton"),"bleeckerButtonLabel")
            const point=label.mapToItem(root,0,0),dpr=displayAlignment.devicePixelRatio
            // This boundary covers glyphs and the surrounding interior. Button
            // outline compositing stays in the separate zero-tolerance audit.
            for(let y=Math.floor(point.y*dpr)-1;y<Math.ceil((point.y+label.height)*dpr)+1;y++)
                for(let x=Math.floor(point.x*dpr)-1;x<Math.ceil((point.x+label.width)*dpr)+1;x++)
                    compare(masked.pixel(x,y),plain.pixel(x,y),"Unchanged interior text pixel "+x+","+y)
            if(host.buttonVariant==="ghost")verify(masked.equals(plain),"Transparent text-only content stays byte-identical")
        }
        function test_software_interior_text_pixels(data) {
            if(root.GraphicsInfo.api!==GraphicsInfo.Software) {
                skip("Software mask pixel preservation; existing RHI texture raster acceptance remains pending")
                return
            }
            mouseMove(root,790,590)
            const host=createTemporaryObject(textFixture,parent,{offset:data.offset,cardWidth:data.width,buttonVariant:data.variant})
            const plain=picture(host)
            host.masked=true
            sameInteriorText(host,picture(host),plain)
            host.masked=false;host.offset+=0.25
            const moved=picture(host)
            host.masked=true
            sameInteriorText(host,picture(host),moved)
        }
        function test_fractional_and_zero_sizes() {
            const host=createTemporaryObject(fixture,parent)
            host.card.width=80.5;host.card.height=60.5
            compare(colorAt(picture(host),host,60,50),Qt.rgba(1,0,0,1))
            host.card.width=0
            compare(colorAt(picture(host),host,60,50),Qt.rgba(18/255,52/255,86/255,1))
            host.card.width=80.5;host.card.height=0
            compare(colorAt(picture(host),host,60,50),Qt.rgba(18/255,52/255,86/255,1))
            host.card.height=60.5
            compare(colorAt(picture(host),host,60,50),Qt.rgba(1,0,0,1))
        }
        function test_visual_mask_preserves_existing_rectangular_pointer_delivery() {
            const host=createTemporaryObject(fixture,parent);picture(host)
            // Qt traverses clipped descendants using clipRect, not containmentMask.
            // Preserve current delivery; native transparent-corner parity is open.
            mouseClick(host,20,20);compare(host.clicks,1)
            mouseClick(host,80,70);compare(host.clicks,2)
            mouseClick(host,19,70);compare(host.clicks,2)
            host.ink.enabled=false;mouseClick(host,80,70);compare(host.clicks,2)
        }
        function test_nested_masks_have_independent_outlines_and_updates() {
            const host=createTemporaryObject(nestedFixture,parent);const image=picture(host)
            compare(colorAt(image,host,20,20),Qt.rgba(18/255,52/255,86/255,1))
            compare(colorAt(image,host,60,60),Qt.rgba(1,0,0,1))
            compare(colorAt(image,host,85,85),Qt.rgba(0,0,1,1))
            const inner=findChild(host,"inner");inner.visible=false
            compare(colorAt(picture(host),host,85,85),Qt.rgba(1,0,0,1))
            inner.visible=true
            compare(colorAt(picture(host),host,85,85),Qt.rgba(0,0,1,1))
        }
        function test_circular_alert_overflow() {
            const host=createTemporaryObject(alertFixture,parent);const image=picture(host)
            verify(host.alert.roundedContentClipping)
            compare(colorAt(image,host,20,20),Qt.rgba(18/255,52/255,86/255,1))
            compare(colorAt(image,host,25,60),Qt.rgba(1,0,0,1))
        }
        function test_capsule_content_overflow() {
            const host=createTemporaryObject(chipFixture,parent)
            const action=findChild(host.chip,"bleeckerFilterAction")
            const ink=Qt.createQmlObject('import QtQuick; Rectangle { x:-100;y:-100;width:400;height:400;color:"red" }',action.parent)
            verify(ink);const image=picture(host)
            verify(host.chip.roundedContentClipping)
            compare(colorAt(image,host,20,20),Qt.rgba(18/255,52/255,86/255,1))
            compare(colorAt(image,host,40,34),Qt.rgba(1,0,0,1))
            ink.destroy()
        }
    }
}

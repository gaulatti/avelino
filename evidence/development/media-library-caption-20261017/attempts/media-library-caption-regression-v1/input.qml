import QtQuick
import QtTest
import Avelino

Item {
    id:root;width:640;height:400
    Component {
        id:factory
        Item {
            id:scope;width:320;height:64
            property real offered:101+1/3
            property string sample:"Tile 2"
            property int alignment:Qt.AlignRight
            readonly property alias caption:label
            Rectangle {anchors.fill:parent;color:"white"}
            BleeckerText {
                id:label;width:scope.offered;text:scope.sample;color:"black"
                font.family:BleeckerFonts.primary;font.pointSize:BleeckerFonts.pointSizeForPixels(13)
                maximumLineCount:2;horizontalAlignment:scope.alignment
            }
        }
    }
    TestCase {
        name:"FormattedTextReflow";when:windowShown
        function init(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1;BleeckerTheme.reducedMotion=true;failOnWarning(/Binding loop/)}
        function make(width,sample,alignment){
            const scope=createTemporaryObject(factory,root,{offered:width,sample:sample,alignment:alignment})
            verify(scope);scope.caption.BleeckerLayout.propose(width);wait(30);return scope
        }
        function test_fractional_growth_matches_fresh_pixels_data(){
            const data=[]
            for(const alignment of [Qt.AlignRight,Qt.AlignHCenter])for(let number=1;number<=7;++number)
                data.push({tag:alignment+"-tile"+number,alignment:alignment,sample:"Tile "+number})
            return data
        }
        function test_fractional_growth_matches_fresh_pixels(data){
            const retained=make(101+1/3,data.sample,data.alignment)
            for(const width of [103,222,103,101+1/3,222]){
                retained.offered=width;retained.caption.BleeckerLayout.propose(width);wait(30)
                const fresh=make(width,data.sample,data.alignment)
                const actual=grabImage(retained),expected=grabImage(fresh)
                verify(actual.equals(expected),data.sample+" alignment "+data.alignment+" at width "+width)
                fresh.destroy();wait(1)
            }
        }
    }
}

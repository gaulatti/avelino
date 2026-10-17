import QtQuick
import QtTest
import Avelino

Item {
    id:root;width:640;height:400
    Component {
        id:factory
        BleeckerPill {
            property alias label:text
            BleeckerText {id:text;text:"Ready"}
        }
    }
    Component {
        id:inlineFactory
        BleeckerPill {
            property alias label:text
            BleeckerText {
                id:text;textFormat:Text.RichText
                text:'<img src="data:image/svg+xml;utf8,'+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="9" height="9"><rect width="9" height="9" fill="#0000ff"/></svg>')+'" width="9" height="9"/>'
            }
        }
    }
    Component {
        id:limitedFactory
        ProposalOverlay {
            property alias pill:pill
            maximumWidth:45
            BleeckerPill {id:pill;property alias label:text;BleeckerText {id:text;text:"Ready"}}
        }
    }
    Component {
        id:ownedFactory
        BleeckerPill {
            property alias label:text
            BleeckerText {
                id:text;text:"Ready";color:"red"
                font.family:BleeckerFonts.primary
                font.pointSize:BleeckerFonts.pointSizeForPixels(19)
                font.weight:Font.Normal
            }
        }
    }
    Component {
        id:richFactory
        BleeckerPill {
            property alias label:text
            BleeckerText {id:text;textFormat:Text.RichText;text:"<span style=\"font-family:'Encode Sans';font-size:17px;font-weight:400\">Status </span><b style=\"color:red\">Ready</b>"}
        }
    }
    TestCase {
        name:"PillModifier";when:windowShown
        function init():void {BleeckerTheme.dark=false;BleeckerTheme.textScale=1}
        function test_paddingFontColorAndBaseline():void {
            const pill=createTemporaryObject(factory,root)
            verify(pill);tryCompare(pill,"partCount",1)
            const caller=pill.label,part=pill.partAt(0)
            tryCompare(part,"implicitWidth",caller.implicitWidth+14)
            compare(part.implicitHeight,caller.implicitHeight+8)
            compare(part.baselineOffset,caller.baselineOffset+4)
            compare(caller.font.family,BleeckerFonts.monospace)
            compare(caller.font.weight,Font.Bold)
            compare(caller.font.pointSize,BleeckerFonts.pointSizeForPixels(9))
            compare(caller.color,BleeckerTheme.palette.sea)
            compare(pill.focusPolicy,Qt.NoFocus)
        }
        function test_callerAndPartSurviveTextThemeAndScale():void {
            const pill=createTemporaryObject(factory,root)
            tryCompare(pill,"partCount",1)
            const caller=pill.label,part=pill.partAt(0),owner=caller.parent
            caller.text="Ready revised";BleeckerTheme.dark=true;BleeckerTheme.textScale=1.5
            tryCompare(caller,"color",BleeckerTheme.palette.sea)
            compare(pill.label,caller);compare(pill.partAt(0),part);compare(caller.parent,owner)
            compare(caller.font.pointSize,BleeckerFonts.pointSizeForPixels(9))
            compare(caller.Accessible.name,"Ready revised")
        }
        function test_explicitCallerFontAndColorSurvive():void {
            const pill=createTemporaryObject(ownedFactory,root)
            tryCompare(pill,"partCount",1)
            compare(pill.label.font.family,BleeckerFonts.primary)
            compare(pill.label.font.weight,Font.Normal)
            compare(pill.label.font.pointSize,BleeckerFonts.pointSizeForPixels(19))
            compare(pill.label.color,"#ff0000")
        }
        function test_richRunsAndAccessibleText():void {
            const pill=createTemporaryObject(richFactory,root)
            tryCompare(pill,"partCount",1)
            verify(pill.label.formattedLayout)
            tryCompare(pill.label,"accessibleText","Status Ready")
            verify(pill.label.implicitWidth>60)
            compare(pill.partAt(0).callerItem,pill.label)
        }
        function test_emptyUsesNativeEmptyLineBox():void {
            const pill=createTemporaryObject(factory,root)
            tryCompare(pill,"partCount",1)
            pill.label.text=""
            tryCompare(pill.label,"implicitHeight",14)
            tryCompare(pill.partAt(0),"implicitHeight",22)
            compare(pill.label.baselineOffset,11)
        }
        function test_baselineShiftPreservesPadding():void {
            const pill=createTemporaryObject(factory,root)
            tryCompare(pill,"partCount",1)
            const height=pill.label.implicitHeight,baseline=pill.label.baselineOffset
            tryCompare(pill.partAt(0),"baselineOffset",baseline+4)
            pill.label.baselineShift=5
            tryCompare(pill.label,"implicitHeight",height+5)
            compare(pill.label.baselineOffset,baseline+5)
            tryCompare(pill.partAt(0),"baselineOffset",pill.label.baselineOffset+4)
        }
        function test_limitedTextAndFormattingStayOnCaller():void {
            const host=createTemporaryObject(limitedFactory,root),pill=host.pill
            tryCompare(pill,"partCount",1)
            const caller=pill.label,part=pill.partAt(0)
            caller.text="A retained caller across formatting changes"
            caller.maximumLineCount=1
            tryCompare(caller.textRenderer,"truncated",true)
            compare(caller.textRenderer.lineCount,1)
            caller.maximumLineCount=2147483647
            caller.textFormat=Text.MarkdownText;caller.text="**Ready** *now*"
            tryCompare(caller,"accessibleText","Ready now")
            compare(part.callerItem,caller);compare(pill.partAt(0),part)
            caller.textFormat=Text.PlainText;caller.text="Ready"
            tryCompare(caller,"formattedLayout",false)
            compare(caller.Accessible.name,"Ready")
        }
        function test_negativeBaselineShiftKeepsCaller():void {
            const pill=createTemporaryObject(factory,root)
            tryCompare(pill,"partCount",1)
            const caller=pill.label,height=caller.implicitHeight,baseline=caller.baselineOffset
            caller.baselineShift=-5
            tryCompare(caller,"implicitHeight",height+5)
            compare(caller.baselineOffset,baseline)
            compare(caller.textRenderer.y,5)
            compare(pill.partAt(0).callerItem,caller)
        }
        function test_inlineImageIsLoadedBeforeCapture():void {
            const pill=createTemporaryObject(inlineFactory,root)
            tryCompare(pill,"partCount",1)
            tryVerify(()=>pill.label.resourcesReady())
            tryVerify(()=>{
                const image=grabImage(root),point=pill.label.mapToItem(root,0,0),dpr=image.width/root.width
                for(let y=Math.max(0,Math.floor((point.y-1)*dpr));y<Math.min(image.height,Math.ceil((point.y+pill.label.height+1)*dpr));y++)
                    for(let x=Math.max(0,Math.floor((point.x-1)*dpr));x<Math.min(image.width,Math.ceil((point.x+pill.label.width+1)*dpr));x++)
                        if(image.blue(x,y)>230 &&image.red(x,y)<25)return true
                return false
            },5000,"The inline image must reach actual displayed window pixels")
        }
    }
}

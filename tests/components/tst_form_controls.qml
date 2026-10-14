import QtQuick
import QtTest
import Avelino

Item {
    id: root
    width: 900; height: 650
    property int calls: 0
    Component { id: fieldFactory; BleeckerField { label: "Name"; width: 260; Rectangle { objectName: "slot"; width: 240; height: 40 } } }
    Component { id: editableFieldFactory; BleeckerField { label: "Name"; width: 260; BleeckerTextField { objectName: "input"; width: parent.width; placeholderText: "Enter a name" } } }
    Component { id: areaFactory; BleeckerTextArea { accessibleName: "Notes"; width: 260 } }
    Component { id: switchFactory; BleeckerSwitch { text: "Notifications" } }
    Component { id: toggleFactory; BleeckerToggleButton { text: "Pin"; onClicked: root.calls++ } }
    Component { id: segmentsFactory; BleeckerSegmentedControl { options: [{value:"a",label:"Alpha"},{value:"b",label:"Beta",disabled:true},{value:"c",label:"Gamma"}]; selection: "a" } }
    TestCase {
        name: "FormControlContracts"
        when: windowShown
        function init() { BleeckerTheme.dark = false; BleeckerTheme.textScale = 1; BleeckerTheme.reducedMotion = true; root.calls = 0; failOnWarning(/Binding loop/) }
        function cleanup() { BleeckerTheme.dark = false; BleeckerTheme.textScale = 1 }
        function test_field_data() {
            const rows = []
            for (const dark of [false,true]) for (const mode of ["label","description","error","both","optional","empty-present"])
                rows.push({tag:dark+"-"+mode,dark:dark,mode:mode})
            return rows
        }
        function test_field(data) {
            BleeckerTheme.dark = data.dark
            const item = createTemporaryObject(fieldFactory,root)
            if (["description","both"].indexOf(data.mode)>=0) item.description = "Visible helper"
            if (["error","both"].indexOf(data.mode)>=0) item.error = "Required value"
            item.optional = data.mode === "optional"
            if (data.mode === "empty-present") { item.hasDescription = true; item.hasError = true }
            const label = findChild(item,"bleeckerFieldLabel"), optional = findChild(item,"bleeckerFieldOptional")
            const host = findChild(item,"bleeckerFieldContent"), desc = findChild(item,"bleeckerFieldDescription"), error = findChild(item,"bleeckerFieldError")
            compare(findChild(item,"slot").parent,host); compare(host.y,label.height+10)
            compare(optional.visible,item.optional)
            if (item.optional) compare(optional.y+optional.baselineOffset,label.baselineOffset)
            compare(desc.visible,item.hasDescription); compare(error.visible,item.hasError)
            compare(desc.resolvedFamily,"Libre Franklin"); compare(error.color.toString(),BleeckerTheme.palette.destructive.toString())
            compare(label.logicalPixelSize,13); compare(desc.logicalPixelSize,12)
            BleeckerTheme.textScale = 1.5; compare(label.logicalPixelSize,19.5); compare(desc.logicalPixelSize,18)
            item.label = "A long field label wraps inside its allocated width"; item.width = 140
            tryVerify(() => label.height>25)
        }
        function test_composed_editable_field_paints_and_accepts_pointer() {
            const item = createTemporaryObject(editableFieldFactory,root)
            const input = findChild(item,"input"), placeholder = findChild(input,"bleeckerTextFieldPlaceholder")
            verify(input.visible); compare(input.width,260); compare(input.height,40); verify(placeholder.visible)
            waitForRendering(input)
            const picture = grabImage(input)
            // The field border must remain painted in the software renderer too.
            verify(picture.pixel(0,Math.floor(input.height/2)).a>0)
            const hint = grabImage(placeholder)
            let ink = false
            for (let y=0;y<hint.height && !ink;y++) for (let x=0;x<hint.width;x++) if (hint.pixel(x,y).a>0) { ink = true; break }
            verify(ink,"Placeholder must contain painted glyphs")
            mouseClick(input,input.width/2,input.height/2); verify(input.activeFocus)
            keyClick(Qt.Key_A); compare(input.text,"a"); verify(!placeholder.visible)
            input.text = ""; verify(placeholder.visible)
        }
        function test_switch_data() {
            const rows = []
            for (const dark of [false,true]) for (const checked of [false,true]) for (const scale of [1,1.5])
                rows.push({tag:dark+"-"+checked+"-"+scale,dark:dark,checked:checked,scale:scale})
            return rows
        }
        function test_switch(data) {
            BleeckerTheme.dark = data.dark; BleeckerTheme.textScale = data.scale
            const item = createTemporaryObject(switchFactory,root,{checked:data.checked})
            const track = findChild(item,"bleeckerSwitchTrack"), thumb = findChild(item,"bleeckerSwitchThumb"), label = findChild(item,"bleeckerSwitchLabel")
            compare(track.width,36); compare(track.height,20); compare(thumb.width,16); compare(thumb.y,2)
            compare(thumb.x,data.checked ? 18 : 2); compare(label.x,48); compare(label.logicalPixelSize,14*data.scale)
            compare(track.color.toString(),(data.checked ? BleeckerTheme.palette.sea : BleeckerTheme.palette.muted).toString())
            mouseClick(item,item.width/2,item.height/2); compare(item.checked,!data.checked)
            item.forceActiveFocus(); keyClick(Qt.Key_Space); compare(item.checked,data.checked)
            item.enabled = false; mouseClick(item,item.width/2,item.height/2); compare(item.checked,data.checked)
        }
        function test_switch_intrinsic_width_keeps_words_on_one_line() {
            const item = createTemporaryObject(switchFactory,root,{text:"Already enabled"})
            const label = findChild(item,"bleeckerSwitchLabel")
            for (const scale of [1,1.5]) {
                BleeckerTheme.textScale = scale
                compare(label.naturalHeight,scale === 1 ? 17 : 27)
                fuzzyCompare(label.width,label.unwrappedWidth,0.000001)
            }
            item.width = 48+label.unwrappedWidth/2
            tryVerify(() => label.naturalHeight>=54)
        }
        function test_toggle_data() {
            const rows = []
            for (const dark of [false,true]) for (const selected of [false,true]) for (const variant of ["default","outline"])
                rows.push({tag:dark+"-"+selected+"-"+variant,dark:dark,selected:selected,variant:variant})
            return rows
        }
        function test_toggle(data) {
            BleeckerTheme.dark = data.dark
            const item = createTemporaryObject(toggleFactory,root,{selected:data.selected,variant:data.variant})
            const label = findChild(item,"bleeckerToggleLabel")
            compare(item.height,34); compare(label.y,(item.contentItem.height-label.height)/2)
            compare(item.background.radius,7)
            compare(item.background.borderColor.toString(),(data.variant === "outline" ? BleeckerTheme.palette.border : Qt.rgba(0,0,0,0)).toString())
            mousePress(item,item.width/2,item.height/2)
            compare(item.background.color.toString(),(data.selected ? BleeckerTheme.palette.primary : BleeckerTheme.palette.muted).toString())
            mouseRelease(item,item.width/2,item.height/2); compare(root.calls,1)
            // The style does not own the caller's selection state.
            compare(item.selected,data.selected)
            item.enabled = false; mouseClick(item,item.width/2,item.height/2); compare(root.calls,1)
        }
        function test_segments_selection_disabled_order_and_empty() {
            const item = createTemporaryObject(segmentsFactory,root)
            const a = findChild(item,"bleeckerSegment0"), b = findChild(item,"bleeckerSegment1"), c = findChild(item,"bleeckerSegment2")
            verify(a.selected); verify(!b.enabled); compare(b.x,a.width+2); compare(c.x,a.width+b.width+4)
            mouseClick(b,b.width/2,b.height/2); compare(item.selection,"a")
            mouseClick(c,c.width/2,c.height/2); compare(item.selection,"c"); verify(c.selected); verify(!a.selected)
            a.forceActiveFocus(); keyClick(Qt.Key_Space); compare(item.selection,"a")
            keyClick(Qt.Key_Tab); verify(c.activeFocus); keyClick(Qt.Key_Space); compare(item.selection,"c")
            compare(item.height,40); item.options = []; tryCompare(item,"width",8); compare(item.height,8)
        }
        function test_text_area_edit_selection_wrapping_scroll_and_readonly() {
            const item = createTemporaryObject(areaFactory,root)
            const editor = findChild(item,"bleeckerTextAreaInput"), viewport = findChild(item,"bleeckerTextAreaViewport")
            compare(item.height,96); compare(viewport.x,10); compare(viewport.width,240); compare(viewport.height,76)
            compare(editor.Accessible.name,"Notes"); compare(editor.wrapMode,TextEdit.Wrap)
            item.forceActiveFocus(); keyClick(Qt.Key_A); keyClick(Qt.Key_Return); keyClick(Qt.Key_B)
            compare(item.text,"a\nb"); keyClick(Qt.Key_A,Qt.ControlModifier); compare(item.selectedText,"a\nb")
            keyClick(Qt.Key_C); compare(item.text,"c")
            item.readOnly = true; keyClick(Qt.Key_D); compare(item.text,"c")
            item.readOnly = false; item.text = Array(30).fill("Wrapped multiline content").join("\n")
            tryVerify(() => viewport.contentHeight>viewport.height)
            verify(findChild(item,"bleeckerTextAreaScrollBar").size<1)
            item.minimumHeight = 160; compare(item.height,160)
        }
    }
}

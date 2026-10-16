import QtQuick
import QtTest
import Avelino
Item {
    id: root
    width: 400
    height: 400
    // Native Medium-21 source bounds; no raster or complete component acceptance.
    // evidence/development/data-metrics/native-action-text.json sha256 017ae740add7c21d6cc691c8aab9088cda428a1a3bcc4ee6bd35594a01c2a92b
    readonly property var nativeRows: [
        {"text":"Create 0","dpr":1,"proposal":50,"rect":{"width":50,"height":54}},
        {"text":"Create 0","dpr":1,"proposal":51,"rect":{"width":50,"height":54}},
        {"text":"Create 0","dpr":1,"proposal":80,"rect":{"width":80,"height":27}},
        {"text":"Create 0","dpr":1,"proposal":240,"rect":{"width":80,"height":27}},
        {"text":"Create 0","dpr":2,"proposal":50,"rect":{"width":50,"height":54}},
        {"text":"Create 0","dpr":2,"proposal":51,"rect":{"width":50,"height":54}},
        {"text":"Create 0","dpr":2,"proposal":80,"rect":{"width":80,"height":27}},
        {"text":"Create 0","dpr":2,"proposal":240,"rect":{"width":80,"height":27}},
        {"text":"Retry 0","dpr":1,"proposal":50,"rect":{"width":41,"height":54}},
        {"text":"Retry 0","dpr":1,"proposal":51,"rect":{"width":41,"height":54}},
        {"text":"Retry 0","dpr":1,"proposal":80,"rect":{"width":71,"height":27}},
        {"text":"Retry 0","dpr":1,"proposal":240,"rect":{"width":71,"height":27}},
        {"text":"Retry 0","dpr":2,"proposal":50,"rect":{"width":41,"height":54}},
        {"text":"Retry 0","dpr":2,"proposal":51,"rect":{"width":41,"height":54}},
        {"text":"Retry 0","dpr":2,"proposal":80,"rect":{"width":71,"height":27}},
        {"text":"Retry 0","dpr":2,"proposal":240,"rect":{"width":71,"height":27}},
        {"text":"Create","dpr":1,"proposal":50,"rect":{"width":50,"height":54}},
        {"text":"Create","dpr":1,"proposal":51,"rect":{"width":50,"height":54}},
        {"text":"Create","dpr":1,"proposal":80,"rect":{"width":62,"height":27}},
        {"text":"Create","dpr":1,"proposal":240,"rect":{"width":62,"height":27}},
        {"text":"Create","dpr":2,"proposal":50,"rect":{"width":50,"height":54}},
        {"text":"Create","dpr":2,"proposal":51,"rect":{"width":50,"height":54}},
        {"text":"Create","dpr":2,"proposal":80,"rect":{"width":61.5,"height":27}},
        {"text":"Create","dpr":2,"proposal":240,"rect":{"width":61.5,"height":27}},
        {"text":"Retry","dpr":1,"proposal":50,"rect":{"width":41,"height":54}},
        {"text":"Retry","dpr":1,"proposal":51,"rect":{"width":41,"height":54}},
        {"text":"Retry","dpr":1,"proposal":80,"rect":{"width":53,"height":27}},
        {"text":"Retry","dpr":1,"proposal":240,"rect":{"width":53,"height":27}},
        {"text":"Retry","dpr":2,"proposal":50,"rect":{"width":41,"height":54}},
        {"text":"Retry","dpr":2,"proposal":51,"rect":{"width":41,"height":54}},
        {"text":"Retry","dpr":2,"proposal":80,"rect":{"width":52.5,"height":27}},
        {"text":"Retry","dpr":2,"proposal":240,"rect":{"width":52.5,"height":27}},
        {"text":"0","dpr":1,"proposal":50,"rect":{"width":14,"height":27}},
        {"text":"0","dpr":1,"proposal":51,"rect":{"width":14,"height":27}},
        {"text":"0","dpr":1,"proposal":80,"rect":{"width":14,"height":27}},
        {"text":"0","dpr":1,"proposal":240,"rect":{"width":14,"height":27}},
        {"text":"0","dpr":2,"proposal":50,"rect":{"width":13.5,"height":27}},
        {"text":"0","dpr":2,"proposal":51,"rect":{"width":13.5,"height":27}},
        {"text":"0","dpr":2,"proposal":80,"rect":{"width":13.5,"height":27}},
        {"text":"0","dpr":2,"proposal":240,"rect":{"width":13.5,"height":27}},
        {"text":"f","dpr":1,"proposal":50,"rect":{"width":8,"height":27}},
        {"text":"f","dpr":1,"proposal":51,"rect":{"width":8,"height":27}},
        {"text":"f","dpr":1,"proposal":80,"rect":{"width":8,"height":27}},
        {"text":"f","dpr":1,"proposal":240,"rect":{"width":8,"height":27}},
        {"text":"f","dpr":2,"proposal":50,"rect":{"width":8,"height":27}},
        {"text":"f","dpr":2,"proposal":51,"rect":{"width":8,"height":27}},
        {"text":"f","dpr":2,"proposal":80,"rect":{"width":8,"height":27}},
        {"text":"f","dpr":2,"proposal":240,"rect":{"width":8,"height":27}},
        {"text":"ff","dpr":1,"proposal":50,"rect":{"width":15,"height":27}},
        {"text":"ff","dpr":1,"proposal":51,"rect":{"width":15,"height":27}},
        {"text":"ff","dpr":1,"proposal":80,"rect":{"width":15,"height":27}},
        {"text":"ff","dpr":1,"proposal":240,"rect":{"width":15,"height":27}},
        {"text":"ff","dpr":2,"proposal":50,"rect":{"width":15,"height":27}},
        {"text":"ff","dpr":2,"proposal":51,"rect":{"width":15,"height":27}},
        {"text":"ff","dpr":2,"proposal":80,"rect":{"width":15,"height":27}},
        {"text":"ff","dpr":2,"proposal":240,"rect":{"width":15,"height":27}},
        {"text":"office","dpr":1,"proposal":50,"rect":{"width":42,"height":54}},
        {"text":"office","dpr":1,"proposal":51,"rect":{"width":42,"height":54}},
        {"text":"office","dpr":1,"proposal":80,"rect":{"width":53,"height":27}},
        {"text":"office","dpr":1,"proposal":240,"rect":{"width":53,"height":27}},
        {"text":"office","dpr":2,"proposal":50,"rect":{"width":42,"height":54}},
        {"text":"office","dpr":2,"proposal":51,"rect":{"width":42,"height":54}},
        {"text":"office","dpr":2,"proposal":80,"rect":{"width":53,"height":27}},
        {"text":"office","dpr":2,"proposal":240,"rect":{"width":53,"height":27}}
    ]
    PixelAlignment { id: metrics; target: root }
    Component { id: labelFactory; ButtonLabel {
        font.family: BleeckerFonts.primary
        font.pointSize: BleeckerFonts.pointSizeForPixels(21)
        font.weight: Font.Medium
    } }
    Component { id: actionFactory; BleeckerButton {
        text: "Create 0"
        maximumWidth: 86
        property int requests: 0
        onClicked: requests++
    } }
    TestCase {
        name: "NativeActionText"
        when: windowShown
        function init() { BleeckerTheme.dark = false; BleeckerTheme.textScale = 1 }
        function cleanup() { BleeckerTheme.textScale = 1 }
        function test_source_line_bounds_data() {
            return root.nativeRows.filter(r => r.dpr === metrics.devicePixelRatio).map((r,i) => ({tag: String(i), row: r}))
        }
        function test_source_line_bounds(data) {
            const r=data.row
            const label=createTemporaryObject(labelFactory,root,{text:r.text,wrapWidth:r.proposal})
            verify(label)
            tryCompare(label,"implicitWidth",r.rect.width)
            tryCompare(label,"implicitHeight",r.rect.height)
        }
        function test_narrow_action() {
            BleeckerTheme.textScale=1.5
            const action=createTemporaryObject(actionFactory,root)
            verify(action)
            tryCompare(action,"implicitWidth",86)
            tryCompare(action,"implicitHeight",54)
            const label=findChild(action,"bleeckerButtonLabel")
            verify(label)
            compare(label.width,50)
            compare(label.height,54)
            mouseClick(action,action.width/2,action.height/2)
            compare(action.requests,1)
        }
    }
}

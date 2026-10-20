import QtQuick
import QtTest
import Avelino
import "inputs.js" as Inputs
Item {
    id: root
    width: 1100; height: 700
    Component { id: factory; SourceColourCase {} }
    TestCase {
        name: "AdminSourceColourPrototype"
        when: windowShown
        function test_profiles_data() { return Inputs.native.profiles.map(row => Object.assign({tag:row.name},row)) }
        function test_profiles(row) {
            BleeckerTheme.dark = row.dark
            const fixture = createTemporaryObject(factory, root, {definition:row.definition,initial:row.initial,sourceDark:row.dark})
            verify(fixture);wait(40)
            const actual=fixture.snapshot()
            for(const key of ["navigation","requests","pending","displayedNavigation","columnWidth"]) compare(actual[key],row.state[key],row.name+" "+key)
            compare(Object.keys(actual.frames).sort(),Object.keys(row.state.frames).sort())
            for(const key of Object.keys(row.state.frames))for(const axis of ["x","y","width","height"])compare(actual.frames[key][axis],row.state.frames[key][axis],row.name+" "+key+" "+axis)
            let finished=false, saved=false
            verify(fixture.grabToImage(function(result) {saved=result.saveToFile("/probe/raw/"+row.name+".png");finished=true}))
            tryVerify(function(){return finished},5000)
            verify(saved)
        }
    }
}

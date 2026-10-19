import QtQuick

Item {
    id:root
    property string __kind:"line"
    property var __points:[]
    property var __values:[]
    property bool __area:false
    property real __innerRadius:0
    property var locale:Qt.locale()
    property string accessibleName:__kind==="sparkline" ? "Trend":__kind.charAt(0).toUpperCase()+__kind.slice(1)+" chart"
    readonly property ChartRenderer __chart:renderer
    readonly property var measurements:renderer.measurements
    implicitWidth:100;implicitHeight:100
    BleeckerLayout.minimumWidth:1
    BleeckerLayout.idealWidth:100
    BleeckerLayout.fillsWidth:true
    LayoutMirroring.childrenInherit:true
    Accessible.role:Accessible.Graphic
    Accessible.name:accessibleName
    Accessible.description:renderer.pointCount+" data points"
    ChartRenderer {
        id:renderer
        kind:root.__kind;points:root.__points;values:root.__values
        area:root.__area;innerRadius:root.__innerRadius
        chartSize:Qt.size(Math.max(1,root.width),Math.max(1,root.height))
        x:(root.width-chartSize.width)/2+paintBounds.x
        y:(root.height-chartSize.height)/2+paintBounds.y
        width:paintBounds.width;height:paintBounds.height
        mirrored:root.LayoutMirroring.enabled
        labelColor:BleeckerTheme.nativeChartLabel
        gridColor:BleeckerTheme.nativeChartGrid
        colors:[BleeckerTheme.palette.sea,BleeckerTheme.palette.desert,BleeckerTheme.palette.terracotta,BleeckerTheme.palette.accentGold,BleeckerTheme.palette.accentOxblood]
        localeName:root.locale.name
        pixelRatio:root.Screen.devicePixelRatio
        Accessible.ignored:true
    }
    Repeater {
        model:renderer.pointCount
        Item {
            required property int index
            objectName:"bleeckerChartData"+index
            readonly property var row:renderer.accessibilityRows[index] || ({name:"",bounds:{x:0,y:0,width:0,height:0}})
            x:row.bounds.x;y:row.bounds.y
            width:Math.max(1,row.bounds.width);height:Math.max(1,row.bounds.height)
            Accessible.role:Accessible.StaticText
            Accessible.name:row.name
        }
    }
}

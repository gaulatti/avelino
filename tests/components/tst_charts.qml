import QtQuick
import QtTest
import Avelino

TestCase {
    id:testCase;name:"Charts";when:windowShown
    width:700;height:450
    property bool mirrored:false
    Item {id:scene;anchors.fill:parent;LayoutMirroring.enabled:testCase.mirrored;LayoutMirroring.childrenInherit:true}
    Component {id:line;BleeckerLineChart {}}
    Component {id:bar;BleeckerBarChart {}}
    Component {id:pie;BleeckerPieChart {}}
    Component {id:scatter;BleeckerScatterChart {}}
    Component {id:spark;BleeckerSparkline {}}
    function points(values) {return values.map((y,i)=>({id:String(i),series:"Value",label:String(i+1),x:i,y:y}))}
    function init(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1;mirrored=false}
    function test_public_types_and_empty() {
        for(const component of [line,bar,pie,scatter,spark]) {
            const chart=createTemporaryObject(component,scene)
            verify(chart!==null);compare(chart.implicitWidth,100);compare(chart.implicitHeight,100)
            compare(chart.measurements.seriesDomain.length,0);compare(chart.__chart.pointCount,0)
            compare(chart.measurements.plotSize.width,100);compare(chart.measurements.plotSize.height,100)
        }
    }
    function test_native_continuous_domains() {
        const chart=createTemporaryObject(line,scene,{width:460,height:260,points:points([10,18,14,26,23,31,39])})
        compare(chart.measurements.xDomain,[0,6]);compare(chart.measurements.yDomain,[0,40])
        chart.points=points([-9,7,0,17,-2]);compare(chart.measurements.yDomain,[-10,20])
        chart.points=points([0,0,0,0]);compare(chart.measurements.yDomain,[0,0])
        compare(chart.measurements.points[0].yPosition,chart.measurements.plotSize.height/2)
    }
    function test_bar_signed_stack_and_categorical_order() {
        const data=[10,-7,4,-15,12,-8,13,-11,6].map((y,i)=>({id:String(i),series:"Series "+(i%3+1),label:"Day "+(Math.floor(i/3)+1),x:i,y:y}))
        const chart=createTemporaryObject(bar,scene,{width:460,height:260,points:data})
        compare(chart.measurements.xDomain,["Day 1","Day 2","Day 3"]);compare(chart.measurements.yDomain,[-40,20])
        compare(chart.measurements.seriesDomain,["Series 1","Series 2","Series 3"])
    }
    function test_native_category_band_rounding() {
        const chart=createTemporaryObject(bar,scene,{width:0,height:0,points:points([10,18,14,26,23,31,39])})
        compare(chart.measurements.points[5].xRange,[0.7142857142857142,0.857142857142857])
        compare(chart.measurements.points[5].xPosition,0.7857142857142856)
    }
    function test_finite_extreme_domains_stay_finite() {
        const chart=createTemporaryObject(scatter,scene,{width:460,height:260})
        for(const values of [[5e-324,1e-323],[-1.7e308,1.7e308]]) {
            chart.points=points(values)
            for(const value of chart.measurements.yDomain)verify(isFinite(value))
            for(const row of chart.measurements.points) {
                verify(isFinite(row.yPosition));verify(isFinite(row.bounds.x));verify(isFinite(row.bounds.y))
                verify(isFinite(row.bounds.width));verify(isFinite(row.bounds.height))
            }
        }
    }
    function test_area_and_live_restoration() {
        const data=[10,7,4,15,12,8,13,11,6].map((y,i)=>({id:String(i),series:"Series "+(i%3+1),label:"",x:Math.floor(i/3),y:y}))
        const chart=createTemporaryObject(line,scene,{width:460,height:260,points:data})
        const renderer=chart.__chart;compare(chart.measurements.yDomain,[0,15])
        chart.area=true;compare(chart.measurements.yDomain,[0,40]);compare(chart.__chart,renderer)
        chart.area=false;compare(chart.measurements.yDomain,[0,15]);compare(chart.__chart,renderer)
    }
    function test_sparkline_keeps_legend_and_hides_axes() {
        const chart=createTemporaryObject(spark,scene,{width:220,height:62,values:[10,18,14,26,23,31,39]})
        compare(chart.measurements.xDomain,[0,6]);compare(chart.measurements.yDomain,[0,39])
        compare(chart.measurements.legend.length,1);compare(chart.measurements.legend[0].series,"Value")
        compare(chart.measurements.plotSize.width,220)
        compare(chart.measurements.plotSize.height,chart.__chart.pixelRatio===2 ? 44.1796875:43.6796875)
        compare(chart.accessibleName,"Trend")
    }
    function test_native_reciprocal_point_and_inverse_values() {
        // Exact native DPR-one logical plot geometry. DPR-dependent caption
        // spacing remains a separate open measurement/acceptance problem.
        const chart=createTemporaryObject(spark,scene,{width:220,height:62,values:[10,18,14,26,23,31,39]})
        chart.__chart.pixelRatio=1
        compare(chart.measurements.points[0].yPosition,32.47976762820513)
        compare(chart.measurements.points[1].yPosition,23.519831730769234)
        compare(chart.measurements.points[5].xPosition,183.33333333333331)
        compare(chart.measurements.yValues,[39,19.357002325165446,-0.2859953496691111])
        compare(chart.measurements.yValuesAtPlotSize,[39,19.5,0])
    }
    function test_minimum_plot_and_unclipped_legend() {
        for(const component of [line,bar,pie,scatter,spark]) {
            const chart=createTemporaryObject(component,scene,{width:0,height:0})
            if(component===spark)chart.values=[10,18,14]
            else chart.points=points([10,18,14])
            compare(chart.measurements.plotSize.width,1);compare(chart.measurements.plotSize.height,1)
            compare(chart.measurements.legend[0].text,"Value")
        }
    }
    function test_native_sector_inverse_and_rtl() {
        const chart=createTemporaryObject(pie,scene,{width:460,height:260,points:points([10,18,14,26,23,31,39])})
        compare(chart.measurements.angleValues,[0,40.25,80.5,120.75000000000001,161])
        const first=chart.measurements.sectors[0].bounds
        mirrored=true
        compare(chart.measurements.angleValues,[161,120.75000000000001,80.5,40.25,0])
        verify(chart.measurements.sectors[0].bounds.x<first.x)
        chart.points=[]
        // Qt exposes absent QVariant numbers as undefined; the published
        // JSON observation preserves the source's five optional nulls.
        compare(JSON.stringify(chart.measurements.angleValues),"[null,null,null,null,null]")
        chart.points=points([0,0]);compare(chart.measurements.angleValues,[0,0,0,0,0])
    }
    function test_nonfinite_rows_keep_independent_channels() {
        const chart=createTemporaryObject(scatter,scene,{width:460,height:260,points:[{x:0,y:NaN},{x:1,y:Infinity},{x:2,y:-Infinity}]})
        compare(chart.measurements.xDomain,[0,2]);compare(chart.measurements.yDomain,[])
        compare(chart.measurements.seriesDomain,["Value"]);compare(chart.__chart.pointCount,3)
        for(const row of chart.measurements.points)compare(row.rendered,false)
    }
    function test_pie_signed_values_and_radius_endpoints() {
        const chart=createTemporaryObject(pie,scene,{width:460,height:260,points:points([-9,7,0,17,-2])})
        verify(chart.measurements.sectors[0].rendered);verify(chart.measurements.sectors[1].rendered)
        compare(chart.measurements.sectors[2].rendered,false)
        chart.innerRadius=1;for(const p of chart.measurements.sectors)compare(p.rendered,false)
        chart.innerRadius=NaN;for(const p of chart.measurements.sectors)compare(p.rendered,false)
        chart.innerRadius=-Infinity;verify(chart.measurements.sectors[0].rendered)
    }
    function test_theme_custom_scale_and_disabled() {
        const chart=createTemporaryObject(line,scene,{width:460,height:260,points:points([10,18,14])})
        const original=chart.measurements.plotSize;const renderer=chart.__chart
        BleeckerTheme.textScale=1.5;compare(chart.measurements.plotSize,original)
        chart.enabled=false;compare(chart.measurements.plotSize,original);compare(chart.__chart,renderer)
        BleeckerTheme.dark=true;compare(chart.measurements.plotSize,original)
    }
}

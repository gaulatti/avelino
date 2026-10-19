import QtQuick

Item {
    id: control
    property real minimumColumnWidth: 260
    property real spacing: BleeckerTokens.spacing.component
    property var tiles: []
    required property Component tile
    readonly property int columns: Math.max(1, Math.floor((width + spacing) / (minimumColumnWidth + spacing)))
    readonly property real columnWidth: Math.max(0, (width - (columns - 1) * spacing) / columns)
    property var rowHeights: []
    implicitWidth: minimumColumnWidth
    implicitHeight: rowHeights.reduce((sum, height) => sum + height, 0) + Math.max(0, rowHeights.length - 1) * spacing
    onColumnsChanged: Qt.callLater(updateRowHeights)
    function updateRowHeights() {
        const heights = Array(Math.ceil(cells.count / columns)).fill(0)
        for (let i = 0; i < cells.count; ++i) {
            const cell = cells.itemAt(i), row = Math.floor(i / columns)
            if (cell) heights[row] = Math.max(heights[row], cell.implicitHeight)
        }
        rowHeights = heights
    }
    function rowOrigin(row) {
        let origin = 0
        for (let i = 0; i < row; ++i) origin += (rowHeights[i] || 0) + spacing
        return origin
    }
    Repeater {
        id: cells
        model: control.tiles
        onItemAdded: Qt.callLater(control.updateRowHeights)
        onItemRemoved: Qt.callLater(control.updateRowHeights)
        Loader {
            required property int index
            required property var modelData
            readonly property int tileIndex: index
            readonly property var tileData: modelData
            readonly property int rowIndex: Math.floor(index / control.columns)
            objectName: "bleeckerDashboardTile" + tileIndex
            x: (index % control.columns) * (control.columnWidth + control.spacing)
            y: control.rowOrigin(rowIndex) + ((control.rowHeights[rowIndex] || implicitHeight) - height) / 2
            width: control.columnWidth
            sourceComponent: control.tile
            onImplicitHeightChanged: Qt.callLater(control.updateRowHeights)
        }
    }
}

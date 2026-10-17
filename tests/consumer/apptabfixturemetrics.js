.pragma library
function metric(symbol,selected,dpr,records) {
    for(const row of records)if(row.symbol===symbol &&row.selected===selected &&row.dpr===dpr)return row
    throw new Error("No measured app-tab fixture dimensions for "+symbol+" selected="+selected+" DPR="+dpr)
}

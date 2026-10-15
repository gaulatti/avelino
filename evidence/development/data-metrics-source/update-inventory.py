from pathlib import Path
import json
p=Path('docs/parity-inventory.json');j=json.loads(p.read_text());counts={'BleeckerIconBadge':184,'BleeckerMetric':416,'BleeckerStatCard':344,'BleeckerKbd':96}
for e in j['desktop']['entries']:
 if e['id'] not in counts:continue
 assert e['status']=='pending' and e['implementation']==[]
 e['caseDiscovery']='Partial native source investigation: all recorded public/instrumented/layout PNG identities and clean replay verified. Qt implementation, numeric transition frames, broader composition, native assets and all complete runtime/visual acceptance remain pending.'
 e['cases']=[{'id':'native-data-display-source','status':'pending','evidence':['evidence/reference-investigations/data-metrics-20261015/investigation.json','docs/data-metrics.md'],'notes':'Source evidence only; no Qt implementation or complete acceptance. Fixed/intrinsic/narrow/RTL geometry, fonts and locale ownership measured separately from native raster equivalence.'}]
 e['sourceInvestigation']={'status':'sealed public source evidence; Qt implementation remains pending','evidence':'evidence/reference-investigations/data-metrics-20261015/investigation.json','captures':counts[e['id']],'localeFormatterWitnesses':1330 if e['id'] in ['BleeckerMetric','BleeckerStatCard'] else 0,'integrityCheck':'scripts/verify-data-metrics-source.py','contractTests':'tests/contracts/test_data_metrics_source.py','contract':'docs/data-metrics.md'}
p.write_text(json.dumps(j,indent=2)+'\n')

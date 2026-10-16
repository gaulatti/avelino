from pathlib import Path
import json
p=Path('docs/parity-inventory.json');j=json.loads(p.read_text());cases=json.loads(Path('evidence/reference-proposals/data-metrics-20261015/captures.json').read_text())['captures']
for e in j['desktop']['entries']:
 api=e['id']
 if api not in ['BleeckerIconBadge','BleeckerMetric','BleeckerStatCard','BleeckerKbd']:continue
 assert e['status']=='pending';e['status']='verification-pending'
 e['implementation']=['src/Avelino/'+api+'.qml','assets/data-metrics-presentation.json']
 if api in ['BleeckerMetric','BleeckerStatCard']:e['implementation']+=['src/Avelino/numbertools.h','src/Avelino/numbertools.cpp','src/Avelino/buttonlabel.cpp']
 if api=='BleeckerStatCard':e['implementation']+=['src/Avelino/BleeckerCard.qml','src/Avelino/proposalrow.cpp']
 if api=='BleeckerKbd':e['implementation']+=['src/Avelino/bleeckerfonts.cpp']
 e['caseDiscovery']='Partial; Qt fitted/narrow/intrinsic/RTL, fixed styles, caller updates, locale ownership, delta presence, icon slots and native-static-text interfaces have candidate checks. Native mono/SF assets, remaining Japanese/Arabic formatter differences, exact pixels, numeric transition frames, broader compositions, physical sessions and actual readers remain pending.'
 e['cases'] += [{'id':'qt-data-display-candidate','status':'pending','evidence':['evidence/development/data-metrics/candidate.json','docs/data-metrics.md'],'notes':'Candidate runtime/package, source geometry and strict comparison remain distinct from complete mirror acceptance.'},{'id':'caller-state-locale-and-input','status':'pending','evidence':['tests/components/tst_data_metrics.qml','tests/consumer/datametricschecks.h','evidence/development/data-metrics/sessions/environment.json'],'notes':'Producer identity/focus, separate process/control locale, optional/zero/signed delta, fixed badges, key updates and real Qt accessibility. Actual readers, physical input and source motion remain unverified.'}]
 e['tests']=['tests/components/tst_data_metrics.qml','tests/components/check-invalid-data-metrics.py','tests/consumer/datametricschecks.h','tests/contracts/test_data_metrics_adapters.py','scripts/verify-data-metrics-source.py','scripts/verify-data-metrics-inputs.py']
 e['captures']=['evidence/development/data-metrics/captures/'+c['path'] for c in cases if c['api']==api]
 e['comparisonResults']=['evidence/development/data-metrics/comparison/comparison.json','evidence/development/data-metrics/native-child-bounds.json','evidence/development/data-metrics/number-formatting.json','evidence/development/data-metrics/regressions.json']
 for gate in e['runtimeGates'].values():
  assert gate['status']=='pending';gate['evidence']=['evidence/development/data-metrics/candidate.json','tests/consumer/datametricschecks.h','docs/data-metrics.md'];gate['notes']='Qt candidate evidence does not accept native mono/SF assets, remaining locale/pixel differences, source motion, physical displays/input or actual reader behavior.'
 e['sourceInvestigation']['status']='sealed public source evidence; Qt candidate verification recorded separately';e['sourceInvestigation']['widthInputEvidence']='evidence/reference-investigations/data-metrics-inputs-20261015/provenance.json'
p.write_text(json.dumps(j,indent=2)+'\n')
p=Path('README.md');p.write_text(p.read_text().replace('Fifty-two of the 80 discovered desktop','Fifty-six of the 80 discovered desktop'))

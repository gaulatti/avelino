from pathlib import Path
import collections,json,re
R=Path('/Users/gaulatti/source/gaulatti/avelino');D=R/'evidence/development/charts-20261017';report=json.loads((D/'candidate.json').read_text());assert report['validation']['fullQtTargets']==31 and report['validation']['virtualProfiles']==40
relative=str(D.relative_to(R));p=R/'docs/parity-inventory.json';inventory=json.loads(p.read_text());apis=['BleeckerLineChart','BleeckerBarChart','BleeckerPieChart','BleeckerScatterChart','BleeckerSparkline']
assert collections.Counter(e['status'] for e in inventory['desktop']['entries'])==dict(pending=14,**{'verification-pending':66})
for e in inventory['desktop']['entries']:
 if e['id'] not in apis:continue
 e['status']='verification-pending';e['implementation']=['src/Avelino/'+e['id']+'.qml','src/Avelino/ChartBase.qml','src/Avelino/chartrenderer.cpp','src/Avelino/chartrenderer.h','src/Avelino/BleeckerTheme.qml']
 e['caseDiscovery']='All named closed/edge source cases and eight retained-history steps are preserved in the 1744-image Linux matrix, without dropping native NaN-bar initialization differences. Complete native geometry, font/raster, non-finite behavior, input timing, physical displays and readers remain pending.'
 for c in e['cases']:
  source=c['sourceInvestigationCapture'];name=Path(source).name.split('-light-text1.0-dpr1.0')[0];candidate=relative+'/captures/light-text1-dpr1-'+('edge-' if '/edges/' in source else '')+name+'.png'
  assert (R/candidate).exists(),candidate
  c['status']='verification-pending';c['candidateCapture']=candidate;c['candidateMetadata']=candidate+'.json';c['evidence'].append(relative+'/candidate.json');c['notes']='The Linux candidate preserves this named source case and all eight contexts. Strict native pixel/metric differences remain recorded. No native geometry/raster, non-finite determinism, input timing, physical display or reader acceptance.'
 e['tests'] += ['tests/components/tst_charts.qml','tests/components/check-invalid-charts.py','tests/components/check-charts-catalog.py','tests/consumer/chartchecks.h','scripts/generate-chart-witnesses.py','scripts/capture-charts.py','scripts/compare-chart-captures.py','scripts/verify-chart-candidate.py','tests/contracts/test_chart_adapters.py','tests/contracts/test_chart_candidate.py']
 e['captures']=[relative+'/captures/capture-results.json',relative+'/catalogs/catalog-results.json'];e['comparisonResults']=[relative+'/comparison/comparison.json']
 for gate in e['runtimeGates'].values():gate.update(status='verification-pending',evidence=['docs/charts.md',relative+'/candidate.json'],notes='Package, Qt data-row interfaces, synthetic read-only input, virtual X11/Wayland profiles and actual gallery toolbar checks pass as candidate evidence. Native geometry/font/raster/non-finite behavior, input timing, physical displays/input and actual readers remain pending.')
p.write_text(json.dumps(inventory,indent=2,ensure_ascii=False)+'\n')
p=R/'README.md';t=p.read_text();assert t.count('Desktop candidate coverage is 66/80')==1;t=t.replace('Desktop candidate coverage is 66/80','Desktop candidate coverage is 71/80')
a='preserved. Linux chart implementation and reader acceptance remain pending.';assert a in t;t=t.replace(a,'preserved. The five Linux chart candidates retain every closed/edge input and\nhistory step in 1,744 strict comparisons: 32 complete matches, all empty charts.\nNative geometry, fonts/raster, non-finite behavior, physical input and readers\nremain pending.');p.write_text(t)
p=R/'docs/charts.md';t=p.read_text();assert 'Current Linux evidence passes all 31 Qt targets' not in t
counts=re.findall(r'Totals:\s+(\d+) passed', (D/'qt/LastTest.log').read_text());assert counts[:2]==['5341','5569'],counts[:3]
t+='''
Current Linux evidence passes all 31 Qt targets, including 5,341 component checks
at DPR one and 5,569 at DPR two. The installed package passes 33 modes and 135
catalog captures; all 131 earlier PNGs and their complete metadata are unchanged.
Forty virtual profiles cover base, font, surface, pill and chart fixtures across
X11/Wayland, software/OpenGL and two display/text scales. This includes eight
complete chart profiles. Actual XTest input reaches all 14 gallery controls over
24 clicks and 25 states, with each entire caller viewport equal to a separate
installed isolated Qt fixture. These are virtual implementation checks.

The strict 1,744-case comparison has 32 complete matches, all empty line/bar/
scatter/sparkline charts. All 40 empty-chart pixels match, including pie, but
pie metrics still differ. All 1,744 layout/state observations and all 1,344 native
outer-frame sets match; 120 complete native metric sets match. Zero nonempty or
retained-history cases pass the complete strict comparison. No acceptance follows
from these counts.

The [sealed candidate](../evidence/development/charts-20261017/candidate.json)
preserves every warning-producing earlier attempt, frozen source inputs,
installed executables, runtime captures, arithmetic diagnostics and raw pixel
differences. A read-only arithmetic experiment reproduces 2,696 continuous x/y
positions exactly using a precomputed reciprocal. A separate native measurement
finds a 0.5-point DPR-two plot-height change in 110 nonempty/nonzero cases. Both
remain named geometry corrections after this captured implementation; the
candidate and its expectations are preserved. Run
`python3 scripts/verify-chart-candidate.py` to recompute the published evidence.
Desktop coverage is 71/80 candidates and zero accepted entries.
''';p.write_text(t)
print('Ledger: 71/80 desktop candidates, nine pending and zero accepted')

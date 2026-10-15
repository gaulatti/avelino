import json
from pathlib import Path
p=Path('docs/parity-inventory.json');inventory=json.loads(p.read_text());captures=json.loads(Path('evidence/reference-proposals/sidebar-brand-20261015/captures.json').read_text())['captures']
for entry in inventory['desktop']['entries']:
 api=entry['id']
 if api not in ['BleeckerSidebarItem','BleeckerBrandMark','BleeckerBrandLockup']:continue
 assert entry['status']=='pending'
 entry['status']='verification-pending';entry['implementation']=['src/Avelino/'+api+'.qml','src/Avelino/valuetools.cpp']
 entry['implementation']+=['src/Avelino/proposalrow.cpp','assets/sidebar-symbols.json'] if api=='BleeckerSidebarItem' else ['src/Avelino/brandimage.h','src/Avelino/brandimage.cpp','assets/brand/BleeckerLogo.png','assets/brand-presentation.json']
 entry['caseDiscovery']='Partial; source-derived fitted/intrinsic/narrow/RTL layout, fixed fonts, caller-owned state/actions and pinned template asset implemented. Exact symbol/font/tint/interpolation/raster, source keyboard/focus, broader scripts/composition, physical sessions and actual readers remain pending.'
 entry['cases']=[{'id':'native-sidebar-brand','status':'pending','evidence':['evidence/reference-proposals/sidebar-brand-20261015/proposal.json','evidence/development/sidebar-brand/candidate.json','docs/sidebar-brand.md'],'notes':'Source component/child bounds and Qt input/asset behavior checked separately from exact native pixels and full acceptance.'},{'id':'caller-state-and-installed-input','status':'pending','evidence':['tests/components/tst_sidebar_brand.qml','tests/consumer/sidebarbrandchecks.h','evidence/development/sidebar-brand/sessions/environment.json'],'notes':'Candidate pointer/keyboard/Qt accessibility, source rectangular sidebar hits, caller selection/title/name/size updates and disabled/canceled actions. Actual readers and native focus correspondence remain unverified.'}]
 entry['tests']=['tests/components/tst_sidebar_brand.qml','tests/components/check-invalid-sidebar-brand.py','tests/consumer/sidebarbrandchecks.h','scripts/verify-sidebar-brand-source.py','tests/contracts/test_sidebar_brand_source.py']
 entry['captures']=['evidence/development/sidebar-brand/captures/'+c['path'] for c in captures if c['api']==api]
 entry['comparisonResults']=['evidence/development/sidebar-brand/comparison/comparison.json','evidence/development/sidebar-brand/native-child-bounds.json','evidence/development/sidebar-brand/regressions.json']
 for gate in entry['runtimeGates'].values():
  assert gate['status']=='pending';gate['evidence']=['evidence/development/sidebar-brand/candidate.json','tests/consumer/sidebarbrandchecks.h','docs/sidebar-brand.md'];gate['notes']='Virtual Qt candidate evidence remains distinct from native pixels, source keyboard/focus, physical display/input and actual reader acceptance.'
 entry['sourceInvestigation']={'status':'sealed public source evidence; Qt candidate verification recorded separately','evidence':'evidence/reference-investigations/sidebar-brand-20261015/investigation.json','captures':sum(c['api']==api for c in captures),'nativePointerCases':36 if api=='BleeckerSidebarItem' else 0,'integrityCheck':'scripts/verify-sidebar-brand-source.py','contract':'docs/sidebar-brand.md'}
p.write_text(json.dumps(inventory,indent=2)+'\n')
p=Path('README.md');p.write_text(p.read_text().replace('Forty-nine of the 80 discovered desktop','Fifty-two of the 80 discovered desktop'))

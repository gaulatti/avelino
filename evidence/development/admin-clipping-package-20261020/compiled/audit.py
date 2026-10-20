from pathlib import Path
import json,hashlib,re,subprocess
P=Path(__file__).resolve().parent
ROOT=Path('/Users/gaulatti/source/gaulatti/avelino')
OUT=ROOT/'artifacts/resumed-avelino-20261016/admin-clipping-compiled-v1/output'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
result=json.loads((P/'result.json').read_text());assert result['exitCode']==0
inputs=json.loads((P/'inputs.json').read_text());commands=json.loads((P/'commands.json').read_text());clone=json.loads((P/'clone-inputs.json').read_text())
assert len(commands)==9 and all(r['exitCode']==0 for r in commands)
tests={}
for api,count in [('admin',266),('mobile',40)]:
 for dpr in [1,2]:
  name=f'{api}-dpr{dpr}';matches=re.findall(r'Totals: (\d+) passed, (\d+) failed, (\d+) skipped, (\d+) blacklisted',(P/(name+'.log')).read_text())
  assert len(matches)==1 and tuple(map(int,matches[0]))==(count,0,0,0),(name,matches)
  tests[name]={'passed':count,'failed':0,'skipped':0,'blacklisted':0}
assert all(sha(ROOT/n)==h for n,h in inputs['sourceFiles'].items())
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();assert head==inputs['sourceRevision']
old=Path(clone['preservedOriginalRoot']);preserved={n:sha(old/n) for n in clone['originalArtifactHashes']};assert preserved==clone['originalArtifactHashes']
current={n:sha(OUT/n) for n in clone['originalArtifactHashes']}
audit={'sourceRevision':head,'commandCount':9,'allCommandExitsZero':True,'tests':tests,'sourceInputsRechecked':len(inputs['sourceFiles']),'sourceInputsUnchanged':True,'preservedOriginalArtifactHashes':preserved,'originalCriticalArtifactsUnchanged':True,'currentArtifactHashes':current,'installedConsumerExecuted':False,'accepted':False}
with (P/'completion-audit.json').open('x') as f:json.dump(audit,f,indent=2);f.write('\n')
artifacts={**current,'consumerSha256':current['package/consumer-build/InstalledConsumer'],'librarySha256':current['package/install/lib/qml/Avelino/libAvelino.so'],'accepted':False}
with (P/'artifacts.json').open('x') as f:json.dump(artifacts,f,indent=2);f.write('\n')
print(json.dumps(audit,indent=2))

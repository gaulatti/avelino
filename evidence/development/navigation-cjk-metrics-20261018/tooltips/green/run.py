from pathlib import Path
import hashlib,json,shutil,subprocess,time
p=Path(__file__).resolve().parent;b=p.parent;r=p.parents[2]
red=b/'tooltip-remount-red-v1';qt=b/'navigation-cjk-qt-v5'
assert (red/'result.json').is_file()
red_commands=json.loads((red/'commands.json').read_text())
assert all(row['exitCode']==0 for row in red_commands[:2])
assert any(row['exitCode']!=0 for row in red_commands[2:])
qt_commands=json.loads((qt/'commands.json').read_text())
assert [row['name']for row in qt_commands[:4]]==['activate-inputs','configure','date-build','install']
assert all(row['exitCode']==0 for row in qt_commands[:4])
core=json.loads((qt/'inputs.json').read_text())['files']
consumer=json.loads((red/'inputs.json').read_text())['consumerFiles']
assert len(core)==604 and len(consumer)==149
for name,value in consumer.items():assert core['tests/consumer/'+name]==value
assert 'setPersistent'not in (red/'consumer/tooltipchecks.h').read_text()
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
runtime=p/'runtime';assert not runtime.exists();runtime.mkdir()
shutil.copytree(qt/'install',runtime/'install');(runtime/'consumer-build').mkdir()
shutil.copy2(red/'runtime/consumer-build/InstalledConsumer',runtime/'consumer-build/InstalledConsumer')
shutil.copy2(b/'navigation-cjk-tooltip-repro-v1/new/check.sh',runtime/'check.sh')
inputs=dict(accepted=False,libraryProducer=qt.name,consumerCompilationProducer=red.name,
            consumerFiles=consumer,consumerSha256=sha(runtime/'consumer-build/InstalledConsumer'),
            packageFiles={str(f.relative_to(runtime/'install')):sha(f)for f in (runtime/'install').rglob('*')if f.is_file()},
            originalDriverSha256=sha(r/'scripts/check-display-sessions.sh'),diagnosticDriverSha256=sha(runtime/'check.sh'))
(p/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
(runtime/'environment.json').write_text(json.dumps(dict(accepted=False,sameElfAsRed=True,consumerSha256=inputs['consumerSha256']),indent=2)+'\n')
steps=[]
for attempt in range(1,21):
    command=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0',
             '-v',str(runtime)+':/display-check','-w','/display-check',
             'avelino-toolchain:recovered-weston13-cjk-v1-20261018-qt6.8.3',
             'bash','check.sh','/display-check/attempt'+str(attempt)]
    started=time.monotonic()
    with(p/f'attempt{attempt}.log').open('w')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
    steps.append(dict(attempt=attempt,command=command,exitCode=result.returncode,seconds=time.monotonic()-started))
    (p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print('green',attempt,result.returncode,flush=True)
(p/'result.json').write_text(json.dumps(dict(accepted=False,steps=steps,
    scope='Same20-remount consumer ELF as red, new library only; full304 display gate remains separately required'),indent=2)+'\n')

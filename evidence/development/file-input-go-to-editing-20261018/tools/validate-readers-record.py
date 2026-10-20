from pathlib import Path
import hashlib,json
b=Path(__file__).resolve().parent
for n in [9,10]:
 p=b/f'file-input-go-to-reader-v{n}'
 result=json.loads((p/'operator-controls-v1/result.json').read_text())
 exercise=json.loads((p/'exercise-result.json').read_text());session=json.loads((p/'session-result.json').read_text());collect=json.loads((p/'collect-result.json').read_text())
 assert exercise['code']==collect['code']==0 and session['waitCode']==0 and session['containerExit']=='0'
 assert result['status']=='passed' and result['directAssistiveTextEdit']=='passed' and len(result['phases'])==20
 speech=(p/'orca-debug.log').read_text();outputs=[x for x in speech.splitlines()if 'SPEECH OUTPUT:'in x];commands=[x for x in speech.splitlines()if 'SPEECH DISPATCHER: Speaking'in x]
 assert any('Go to Folder'in x for x in outputs)and any('Go to Folder'in x for x in commands)
 server=(p/'speech-dispatcher-logs/speech-dispatcher.log').read_text(errors='replace')
 protocol=[x for x in server.splitlines()if 'SPEAK'in x]
 phases={x['phase']:x for x in result['phases']}
 begin=phases['go-to-native-prefix']['time'];end=phases['go-to-native-arrows-preserve-input']['time']
 events=[json.loads(x)for x in(p/'events.jsonl').read_text().splitlines()]
 selection=[e for e in events if begin<=e['time']<=end and ('selected'in e['event']or 'selection'in e['event'])]
 value=dict(accepted=False,profile=result['profile'],phases=len(result['phases']),nativeKeyFlow='passed',directAssistiveTextEdit='passed',exerciseExit=0,collectionExit=0,sessionExit='0',orcaSpeechOutputs=len(outputs),orcaSpeechDispatcherCommands=len(commands),speechServerProtocolLines=len(protocol),speechServerProtocolSamples=protocol[:8],orcaLogSha256=hashlib.sha256((p/'orca-debug.log').read_bytes()).hexdigest(),arrowSelectionEvents=selection,suggestionAnnouncementComparison='pending',nativeReaderComparison='pending',nativeHierarchy='pending',speechEngineAudioVerification='pending',physicalInput=False,physicalListening=False)
 (p/'validation.json').write_text(json.dumps(value,indent=2)+'\n')
 print(n,'phases',len(result['phases']),'Orca outputs',len(outputs),'backend commands',len(commands),'server protocol lines',len(protocol),'arrow selection events',len(selection))

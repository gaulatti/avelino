"""Check actual event and speech windows without declaring native parity."""
from pathlib import Path
import hashlib,json

base=Path(__file__).resolve().parent
for number in (13,14):
    directory=base/f'file-input-go-to-reader-v{number}'
    read=lambda name:json.loads((directory/name).read_text())
    result=read('operator-controls-v1/result.json')
    exercise,collect,session=map(read,('exercise-result.json','collect-result.json','session-result.json'))
    assert exercise['code']==collect['code']==session['waitCode']==0 and session['containerExit']=='0'
    assert result['status']=='passed' and len(result['phases'])==21
    assert result['nativeKeyFlow']==result['directAssistiveTextEdit']=='passed'
    phases={p['phase']:p for p in result['phases']}
    speech=(directory/'orca-debug.log').read_bytes()
    events=[json.loads(line)for line in(directory/'events.jsonl').read_text().splitlines()]
    windows={}
    for name,offset,target in [
        ('go-to-native-arrows-preserve-input','arrowReaderStartBytes','Alpine'),
        ('go-to-assistive-selection-keeps-input','readerStartBytes','Alphabet')]:
        phase=phases[name];observation=phase['observations']
        assert observation['raw']=='/probe/fixtures/Al' and observation['pathHasKeyboardFocus'] is True
        assert observation['assistiveSelected']==['/probe/fixtures/'+target]
        start=observation[offset];end=phase['readerLogBytes'];assert 0<=start<end<=len(speech)
        lines=speech[start:end].decode().splitlines()
        outputs=[line for line in lines if "SPEECH OUTPUT: '/probe/fixtures/"+target+".'"in line]
        commands=[line for line in lines if "SPEECH DISPATCHER: Speaking '/probe/fixtures/"+target+".'"in line]
        assert outputs and commands,(number,name)
        windows[name]=dict(startBytes=start,endBytes=end,sha256=hashlib.sha256(speech[start:end]).hexdigest(),target=target,outputLines=outputs,backendLines=commands)
    arrows=phases['go-to-native-arrows-preserve-input']
    begin=arrows['observations']['arrowStartTime'];end=arrows['time']
    assert 0<end-begin<10
    selection=[e for e in events if begin<=e['time']<=end and ('selected'in e['event']or 'selection'in e['event'])]
    assert any(e['event']=='object:state-changed:selected'and e['name']=='/probe/fixtures/Alpha'and e['detail1']==0 for e in selection)
    assert any(e['event']=='object:state-changed:selected'and e['name']=='/probe/fixtures/Alpine'and e['detail1']==1 for e in selection)
    assert any(e['event']=='object:selection-changed'and e['name']=='Folder suggestions'for e in selection)
    assistive=phases['go-to-assistive-selection-keeps-input'];assert assistive['observations']['owner']==''
    assert assistive['observations']['method']=='AT-SPI Selection.selectChild'
    assert phases['go-to-return-navigates-without-owner']['observations']['owner']==''
    decoded=speech.decode();server=(directory/'speech-dispatcher-logs/speech-dispatcher.log').read_text(errors='replace')
    value=dict(accepted=False,producer='file-input-qt-v64',profile=result['profile'],phases=21,nativeKeyFlow='passed',directAssistiveTextEdit='passed',singleSelectionQuery='passed',exerciseExit=0,collectionExit=0,sessionExit='0',arrowIntervalSeconds=end-begin,arrowSelectionEvents=selection,speechWindows=windows,orcaLogSha256=hashlib.sha256(speech).hexdigest(),orcaSpeechOutputs=decoded.count('SPEECH OUTPUT:'),orcaSpeechDispatcherCommands=decoded.count('SPEECH DISPATCHER: Speaking'),speechServerProtocolLines=sum('SPEAK'in line for line in server.splitlines()),orcaNoSuchObjectMentions=decoded.count('NoSuchObject'),nativeReaderComparison='pending',nativeHierarchy='pending',nativeTiming='pending',speechEngineAudioVerification='pending',physicalInput=False,physicalListening=False,speechPolicyChanged=False,diagnosticLogging='Flush original Orca debug file after original speech output and backend command messages')
    (directory/'validation.json').write_text(json.dumps(value,indent=2)+'\n')
    print(number,'21 phases; selection transport and real output/backend windows verified;',len(selection),'arrow events;',round(end-begin,3),'seconds; native gates pending')

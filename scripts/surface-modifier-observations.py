"""Exact closed surface observations; empty baseline maps do not accept guides."""
import math

def bounds(expected,actual):
    if not isinstance(actual,dict) or set(actual)!=set(expected) or any(type(actual[k]) not in [int,float] or not math.isfinite(actual[k]) for k in expected):
        return dict(status='failed',reference=expected,candidate=actual,error='Missing, extra or nonfinite bounds')
    delta={k:actual[k]-expected[k] for k in expected}
    return dict(status='passed' if all(v==0 for v in delta.values()) else 'failed',reference=expected,candidate=actual,delta=delta)

def observations(row,meta):
    source=row['source'];expected=source['states'][1];actual=meta.get('surfaceModifierParts',{})
    valid=isinstance(actual,dict) and all(isinstance(v,list) for v in actual.values())
    measured={k:[bounds(rect,actual.get(k,[])[i] if valid and i<len(actual.get(k,[])) else None) for i,rect in enumerate(values)] for k,values in expected['partInstances'].items()}
    passed=valid and set(actual)==set(expected['partInstances']) and all(len(actual[k])==len(v) for k,v in expected['partInstances'].items()) and all(r['status']=='passed' for v in measured.values() for r in v)
    f=source['configuration']
    state={'renderedRadius':f['resolvedRadius'],'renderedRtl':f['rtl'],'renderedTextScale':source['textScale'],
        'surfaceModifierState':{k:expected[k] for k in ['appearances','disappearances','callerInstances','actions','counter']}}
    errors={k:{'reference':v,'candidate':meta.get(k)} for k,v in state.items() if meta.get(k)!=v}
    if type(meta.get('renderedRadius')) not in [int,float] or not math.isfinite(meta.get('renderedRadius',math.nan)):
        errors['renderedRadius']={'reference':f['resolvedRadius'],'candidate':meta.get('renderedRadius')}
    actual_state=meta.get('surfaceModifierState')
    if not isinstance(actual_state,dict) or set(actual_state)!=set(state['surfaceModifierState']) or any(type(actual_state[k]) is not int for k in state['surfaceModifierState']):
        errors['surfaceModifierState']={'reference':state['surfaceModifierState'],'candidate':actual_state}
    if type(meta.get('renderedRtl')) is not bool:errors['renderedRtl']={'reference':f['rtl'],'candidate':meta.get('renderedRtl')}
    if type(meta.get('renderedTextScale')) not in [int,float] or not math.isfinite(meta.get('renderedTextScale',math.nan)):
        errors['renderedTextScale']={'reference':source['textScale'],'candidate':meta.get('renderedTextScale')}
    baseline=meta.get('surfaceModifierBaselines')
    status='not-requested' if expected['baselines']=={} and baseline=={} else 'passed' if baseline==expected['baselines'] else 'failed'
    return dict(partFrames=measured,partFramesStatus='passed' if passed else 'failed',baselineStatus=status,
        baselineReference=expected['baselines'],baselineCandidate=baseline,stateErrors=errors,stateStatus='failed' if errors else 'passed')

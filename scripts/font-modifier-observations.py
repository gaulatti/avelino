"""Pure metadata comparison; pixel tooling is loaded only for a pixel comparison."""
import math
def bounds(expected,actual):
    if not isinstance(actual,dict) or set(actual)!=set(expected) or any(type(actual[k]) not in [int,float] or not math.isfinite(actual[k]) for k in expected):
        return dict(status='failed',reference=expected,candidate=actual,error='Missing or extra bounds')
    delta={k:actual[k]-expected[k] for k in expected}
    return dict(status='passed' if all(abs(v)<=1e-6 for v in delta.values()) else 'failed',reference=expected,candidate=actual,delta=delta)

def observations(row,meta):
    source=row['source'];expected=source['states'][1];actual=meta.get('fontModifierParts',{})
    measured={k:[bounds(rect,actual.get(k,[])[i] if i<len(actual.get(k,[])) else None) for i,rect in enumerate(values)] for k,values in expected['partInstances'].items()}
    passed=set(actual)==set(expected['partInstances']) and all(len(actual[k])==len(v) for k,v in expected['partInstances'].items()) and all(r['status']=='passed' for v in measured.values() for r in v)
    f=source['configuration'];requested=f['size']*source['textScale']
    resolved=12 if requested<=0 else requested if f['family']=='mono' else int(requested+.5) or 12
    state={'renderedFamily':f['family'],'renderedSize':f['size'],'renderedWeight':f['weight'],'renderedTextScale':source['textScale'],
        'renderedResolvedPixelSize':resolved,'renderedRtl':f['rtl'],
        'fontModifierState':{k:expected[k] for k in ['appearances','disappearances','callerInstances']}}
    errors={k:{'reference':v,'candidate':meta.get(k)} for k,v in state.items() if meta.get(k)!=v}
    baseline=meta.get('fontModifierBaselines')
    return dict(partFrames=measured,partFramesStatus='passed' if passed else 'failed',
        baselineStatus='passed' if baseline==expected['baselines'] else 'failed',
        baselineReference=expected['baselines'],baselineCandidate=baseline,stateErrors=errors,stateStatus='failed' if errors else 'passed')

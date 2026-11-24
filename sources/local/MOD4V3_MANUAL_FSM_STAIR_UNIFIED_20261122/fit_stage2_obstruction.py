"""Fit a causal three-frame obstruction branch; archived labels stay offline."""
from itertools import product
import json
import numpy as np
from fsm_paths import HERE
from fsm_io import put


def main():
    negatives=[]; positives=[]
    impulse_negatives=[];impulse_positives=[]
    sources=[]
    folder=HERE/'evidence/stair_r9_009m_contract'
    rows=json.loads((folder/'RESULT.json').read_text())['rows']
    sources.extend((r,folder/'traces'/(r['id']+'.npz')) for r in rows if not r.get('force_at_s'))
    folder=HERE/'evidence/stage2_initial_pilot'
    sources.extend((json.loads(p.read_text()),folder/'traces'/(p.stem+'.npz')) for p in (folder/'cases').glob('*.json')
                   if not json.loads(p.read_text()).get('force_at_s'))
    folder=HERE/'evidence/stage2_screen_r9'
    sources.extend((json.loads(p.read_text()),folder/'traces'/(p.stem+'.npz')) for p in (folder/'cases').glob('*.json')
                   if not json.loads(p.read_text()).get('force_at_s'))
    for folder in (HERE/'evidence/contact_calibration/raw',HERE/'evidence/contact_calibration_dr/raw'):
        sources.extend((json.loads(p.with_suffix('.json').read_text()),p) for p in folder.glob('*.npz'))
    for row,path in sources:
        with np.load(path) as z:x=z['control']
        raw=x[:,1:36]; filtered=raw[0].copy(); previous=filtered.copy(); noisy=False
        values=[];impulses=[]
        for obs in raw:
            noisy |= abs(np.linalg.norm(obs[7:10])-1.)>.003
            filtered+=(.25 if noisy else 1.)*(obs-filtered)
            filtered[:4]=obs[:4]; filtered[22:]=obs[22:]
            wheel=filtered[20:22].mean()*.625
            last=previous[20:22].mean()*.625
            values.append([(filtered[0]-wheel)/max(filtered[0],.3),filtered[7],filtered[5],last-wheel])
            impulses.append([abs(filtered[7]-previous[7]),abs(filtered[5]-previous[5]),last-wheel,
                np.max(abs(filtered[16:20]-previous[16:20])),filtered[7],wheel,filtered[0],noisy])
            previous=filtered.copy()
        a=np.array(values)
        padded=np.pad(a,((2,0),(0,0)),mode='edge')
        features=(padded[2:]+padded[1:-1]+padded[:-2])/3.
        times=x[:,0]-.02
        face=row['first_face_contact_s']
        pre=(raw[:,0]>.3)&(x[:,48]>.10)
        if face is not None:pre &= times<face
        negatives.append(features[pre])
        impulse=np.array(impulses)
        impulse_negatives.append(impulse[pre])
        if face is not None:
            valid=(times>=face-.003)&(times<=face+.301)&(raw[:,0]>.3)
            if row.get('first_climb_s') is not None:valid &= times<=row['first_climb_s']+.002
            if valid.any():positives.append((row['id'],features[valid],times[valid]-face))
            if valid.any():impulse_positives.append((row['id'],impulse[valid],times[valid]-face))
    negative=np.concatenate(negatives)
    results=[]
    for deficit,pitch,rate,decel in product((.15,.25,.35,.45,.55),(-.08,-.05,-.02,0.,.02,.04),(.04,.08,.12,.18,.25),(.015,.03,.05,.08,.12,.20)):
        def hit(f):return (f[:,0]>deficit)&(f[:,1]>pitch)&(f[:,2]>rate)&(f[:,3]>decel)
        if hit(negative).any():continue
        found=[]
        for name,f,t in positives:
            h=np.flatnonzero(hit(f))
            if len(h):found.append(dict(id=name,delay_ms=float(1000*t[h[0]])))
        results.append(dict(deficit=deficit,pitch=pitch,rate=rate,decel=decel,detected=len(found),
            within_100ms=sum(r['delay_ms']<=100 for r in found),found=found))
    results.sort(key=lambda r:(r['detected'],r['within_100ms']),reverse=True)
    put(HERE/'evidence/STAGE2_OBSTRUCTION_FIT.json',dict(negative_frames=len(negative),positive_cases=len(positives),
        best=results[:8],zero_false_positive=True,training_fit_only=True))
    print(json.dumps(dict(negative_frames=len(negative),positive_cases=len(positives),best=results[:2]),indent=2))
    all_negative=np.concatenate(impulse_negatives)
    all_positive=impulse_positives
    for noisy in (False,True):
      negative=all_negative[(all_negative[:,7]>.5)==noisy]
      impulse_positives=[(name,f[(f[:,7]>.5)==noisy],t[(f[:,7]>.5)==noisy]) for name,f,t in all_positive]
      impulse_positives=[r for r in impulse_positives if len(r[1])]
      fit_impact(negative,impulse_positives,noisy)


def fit_impact(negative,impulse_positives,noisy):
    fits=[]
    for pitch,dp,rate,decel,leg in product((-.1,-.05,0.,.03),(.005,.01,.015,.02,.03,.05),
        (.04,.06,.08,.12,.20,.30),(.04,.06,.1,.15,.2),(.05,.1,.15,.25)):
        def hit(f):
            gate=((f[:,5]<.85*f[:,6])|(f[:,4]>.07)) if noisy else np.ones(len(f),dtype=bool)
            return gate&(f[:,4]>pitch)&(((f[:,0]>dp)&(f[:,1]>rate))|((f[:,2]>decel)&(f[:,1]>rate)&(f[:,3]>leg)))
        if hit(negative).any():continue
        found=[]
        for name,f,t in impulse_positives:
            h=np.flatnonzero(hit(f))
            if len(h):found.append(dict(id=name,delay_ms=float(1000*t[h[0]])))
        fits.append(dict(pitch=pitch,dp=dp,rate=rate,decel=decel,leg=leg,detected=len(found),
            within_40ms=sum(r['delay_ms']<=40 for r in found),within_100ms=sum(r['delay_ms']<=100 for r in found),found=found))
    fits.sort(key=lambda r:(r['detected'],r['within_100ms'],r['within_40ms']),reverse=True)
    label='NOISY' if noisy else 'CLEAN'
    put(HERE/f'evidence/STAGE2_{label}_IMPACT_FIT.json',dict(negative_frames=len(negative),positive_cases=len(impulse_positives),best=fits[:8],zero_false_positive=True))
    print(label,json.dumps([{k:v for k,v in r.items() if k!='found'} for r in fits[:3]]),flush=True)


if __name__=='__main__':main()

"""Fit signed differences of adjacent three-tick sensor means."""
from itertools import product
import json
import numpy as np
from fsm_paths import HERE
from fsm_io import put


def main():
    neg=[];pos=[];sources=[]
    for name in ('stair_r9_009m_contract','stage2_initial_pilot'):
        folder=HERE/'evidence'/name
        sources.extend((json.loads(p.read_text()),folder/'traces'/(p.stem+'.npz')) for p in (folder/'cases').glob('*.json')
            if not json.loads(p.read_text()).get('force_at_s'))
    for name in ('contact_calibration','contact_calibration_dr'):
        folder=HERE/'evidence'/name/'raw'
        sources.extend((json.loads(p.with_suffix('.json').read_text()),p) for p in folder.glob('*.npz'))
    for row,path in sources:
        with np.load(path) as z:x=z['control']
        raw=x[:,1:36];v=np.c_[raw[:,20:22].mean(1)*.625,raw[:,7],raw[:,5]]
        pad=np.pad(v,((5,0),(0,0)),mode='edge')
        current=(pad[5:]+pad[4:-1]+pad[3:-2])/3.
        prior=(pad[2:-3]+pad[1:-4]+pad[:-5])/3.
        f=np.c_[prior[:,0]-current[:,0],current[:,1]-prior[:,1],current[:,2],current[:,1],raw[:,0]]
        t=x[:,0]-.02;face=row['first_face_contact_s']
        valid=raw[:,0]>.3
        pre=valid&(x[:,48]>.10)
        if face is not None:pre &=t<face
        neg.append(f[pre])
        if face is not None:
            good=valid&(t>=face-.003)&(t<=face+.301)
            if row.get('first_climb_s') is not None:good &=t<=row['first_climb_s']+.002
            if good.any():pos.append((row['id'],f[good],t[good]-face))
    negative=np.concatenate(neg);fits=[]
    for drop,rise,rate,pitch in product((.05,.08,.12,.16,.20,.25,.3),(.005,.01,.015,.02,.03,.04,.05),
        (.04,.08,.12,.18,.25),(-.08,-.05,-.02,0.,.03)):
        def hit(f):return (f[:,0]>drop)&(f[:,1]>rise)&(f[:,2]>rate)&(f[:,3]>pitch)
        if hit(negative).any():continue
        found=[]
        for name,f,t in pos:
            h=np.flatnonzero(hit(f))
            if len(h):found.append(dict(id=name,delay_ms=float(t[h[0]]*1000)))
        fits.append(dict(drop=drop,rise=rise,rate=rate,pitch=pitch,detected=len(found),
            within_100ms=sum(r['delay_ms']<=100 for r in found),found=found))
    fits.sort(key=lambda r:(r['detected'],r['within_100ms']),reverse=True)
    put(HERE/'evidence/STAGE2_INTEGRATED_CONTACT_FIT.json',dict(negative_frames=len(negative),positive_cases=len(pos),best=fits[:6]))
    print(json.dumps([{k:v for k,v in r.items() if k!='found'} for r in fits[:3]]),flush=True)


if __name__=='__main__':main()

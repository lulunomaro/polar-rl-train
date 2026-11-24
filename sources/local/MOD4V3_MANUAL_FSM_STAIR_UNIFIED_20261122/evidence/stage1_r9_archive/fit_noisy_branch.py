"""Calibrate the noisy-sensor branch separately from exact unit-gravity inputs."""
from itertools import product
import json
import numpy as np
from fit_filtered_detector import features
from fsm_paths import HERE
from fsm_io import put


def main():
    best_all=None;results=[]
    for alpha in (.15,.25,.35,.5):
        neg=[];pos=[]
        for path in (HERE/'evidence/contact_calibration_dr/raw').glob('*.npz'):
            r=json.loads(path.with_suffix('.json').read_text());x=np.load(path)['control'];t=x[:,0]-.02
            f=features(x[:,1:36],alpha)[:,0]
            pre=np.ones(len(x),bool) if r['course']=='flat' else x[:,48]>.10
            face=r['first_face_contact_s']
            if face is not None:pre &=t<face
            neg.append(f[pre])
            if face is not None:
                w=(t>=face-.003)&(t<=face+.041)
                later=(t>=face-.003)&(t<=face+.401)
                if w.any():pos.append((r['id'],f[w],f[later]))
        neg=np.concatenate(neg);best=None
        for pmin,dp,rate,decel,leg in product((-.1,0.,.05),(.01,.015,.02,.025,.03,.05,.08,.12),
            (.04,.06,.08,.1,.12,.16,.2,.3,.5),(.1,.15,.2,.3,.5,.8),(.1,.15,.25,.4,.6,.9)):
            def hit(a):
                return (a[:,6]>pmin)&(((a[:,0]>dp)&(a[:,1]>rate))|
                    ((a[:,2]>decel)&(a[:,1]>rate)&(a[:,3]>leg)))
            if hit(neg).any():continue
            found=[name for name,w,later in pos if hit(w).any()]
            delayed=[name for name,w,later in pos if hit(later).any()]
            score=(len(found),len(delayed))
            if best is None or score>best['score']:
                best=dict(alpha=alpha,dp=dp,rate=rate,decel=decel,leg=leg,pitch_min=pmin,score=score,
                    found=found,found_within_400ms=delayed,negative_frames=len(neg),positive_windows=len(pos))
        results.append(best)
        if best is None:
            print(alpha,'no zero-FP candidate',flush=True)
            continue
        print(alpha,best['score'],best,flush=True)
        if best_all is None or best['score']>best_all['score']:best_all=best
    put(HERE/'evidence/contact_calibration/NOISY_BRANCH_FIT.json',dict(best=best_all,results=results,
        calibration_only=True,runtime_unchanged=True))


if __name__=='__main__':main()

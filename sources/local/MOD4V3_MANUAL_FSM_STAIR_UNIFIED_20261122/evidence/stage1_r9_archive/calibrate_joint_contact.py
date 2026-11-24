"""Joint MuJoCo/Isaac calibration using only E0 approach frames as negatives."""
from itertools import product
from pathlib import Path
import json
import numpy as np
from fsm_paths import HERE
from fsm_io import put
from manual_fsm_core import DetectorConfig

def main():
    negatives=[];positives=[]
    for path in sorted((HERE/'evidence/contact_calibration/raw').glob('*.npz')):
        row=json.loads(path.with_suffix('.json').read_text(encoding='utf-8'))
        x=np.load(path)['control'];time=x[:,0]-.02
        if row['course'] in ('flat','rough_L9'):
            negatives.append(x[:,42:48])
        else:
            pre=x[:,48]>.10
            if row['first_face_contact_s'] is not None:pre &= time<row['first_face_contact_s']
            negatives.append(x[pre,42:48])
            face=row['first_face_contact_s']
            if face is not None:
                hits=x[(time>=face-.003)&(time<=face+.041),42:48]
                if len(hits):positives.append(('mujoco/'+row['id'],hits))
    frames=np.load(HERE/'evidence/fsm_r3/probe/NATIVE_CALIBRATION.npz')['frames']
    native_neg=0;native_pos=0
    for j in range(frames.shape[1]):
        x=frames[:,j];phase=x[:,41].astype(int);pre=x[:,42].astype(bool)
        entering=(phase==2)&np.r_[True,phase[:-1]!=2]
        valid=pre&((phase==0)|(phase==1)|entering)&(x[:,0]>.15)&(x[:,44]>=25)
        negatives.append(x[valid,35:41]);native_neg+=int(valid.sum())
        boundaries=np.r_[0,np.flatnonzero(np.diff(x[:,44])<=0)+1,len(x)]
        for start,end in zip(boundaries[:-1],boundaries[1:]):
            faces=np.flatnonzero(x[start:end,43]>.5)+start
            if not len(faces):continue
            first=int(faces[0])
            if np.any(entering[start:first]&pre[start:first]):continue
            window=x[first:min(first+3,end),35:41]
            positives.append((f'isaac/{j}/{start}',window));native_pos+=1
    neg=np.concatenate(negatives)
    candidates=[]
    for dp,rate,decel,leg in product((.015,.02,.025,.035,.05,.08,.12),(.12,.18,.25,.35,.5,.7),
                                    (.15,.25,.35,.5,.7,1.),(.15,.25,.35,.5,.7)):
        def hit(x):
            return ((x[:,0]>dp)&(x[:,1]>rate))|((x[:,2]>decel)&(x[:,1]>rate)&(x[:,3]>leg))
        if hit(neg).any():continue
        found=[name for name,x in positives if hit(x).any()]
        candidates.append((len(found),dp,rate,decel,leg,found))
    if not candidates:
        put(HERE/'evidence/contact_calibration/JOINT_CALIBRATION_FAILED.json',dict(negative_frames=len(neg),
            native_negative_frames=native_neg,positive_cases=len(positives),
            reason='No zero-FP thresholds in the searched grid; conservative full-body native gap recording required'))
        raise RuntimeError('No joint zero-FP thresholds found')
    best=max(candidates,key=lambda v:(v[0],-v[1],-v[2],-v[3],-v[4]))
    config=DetectorConfig(pitch_impulse=best[1],pitch_rate_impulse=best[2],wheel_deceleration=best[3],leg_impulse=best[4])
    old=json.loads((HERE/'DETECTOR.json').read_text(encoding='utf-8'))
    put(HERE/'evidence/contact_calibration/DETECTOR_MUJOCO_ONLY.json',old)
    result=dict(config=config.to_dict(),negative_frames=len(neg),native_negative_frames=native_neg,
        false_positive_frames=0,positive_cases=len(positives),native_positive_cases=native_pos,
        detected_within_40ms=best[0],detected_cases=best[5],calibration_only=True,
        impulse_rule='pitch_change AND rate_change OR wheel_deceleration AND rate_change AND leg_impulse')
    put(HERE/'DETECTOR.json',result)
    put(HERE/'evidence/contact_calibration/JOINT_CALIBRATION.json',result)
    print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()

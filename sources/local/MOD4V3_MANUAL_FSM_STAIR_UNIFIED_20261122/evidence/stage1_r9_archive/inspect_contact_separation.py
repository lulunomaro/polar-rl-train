"""Offline test of signed-pitch gating; never writes runtime thresholds."""
from itertools import product
import json
from argparse import ArgumentParser
import numpy as np
from fsm_paths import HERE
from fsm_io import put


def main():
    p=ArgumentParser();p.add_argument('--with-dr',action='store_true');args=p.parse_args()
    neg=[];pos=[]
    paths=list((HERE/'evidence/contact_calibration/raw').glob('*.npz'))
    if args.with_dr:paths+=list((HERE/'evidence/contact_calibration_dr/raw').glob('*.npz'))
    blocked_fp=[]
    for path in sorted(paths):
        row=json.loads(path.with_suffix('.json').read_text())
        x=np.load(path)['control'];time=x[:,0]-.02
        data=np.c_[x[:,42:48],x[:,8],x[:,6]]
        pre=np.ones(len(x),bool) if row['course'] in ('flat','rough_L9') else x[:,48]>.10
        face=row['first_face_contact_s']
        if face is not None:pre &=time<face
        b=(x[:,8]>.11)&(np.abs(x[:,46])<.15)&(x[:,1]>.15)&pre
        if np.any(b&np.r_[False,b[:-1]]):blocked_fp.append(row['id'])
        neg.append(data[pre])
        if face is not None:
            hits=data[(time>=face-.003)&(time<=face+.041)]
            if len(hits):pos.append(('cpu/'+row['id'],hits))
    frames=np.load(HERE/'evidence/fsm_r3/probe/NATIVE_CALIBRATION.npz')['frames']
    for j in range(frames.shape[1]):
        x=frames[:,j];phase=x[:,41].astype(int);pre=x[:,42].astype(bool)
        data=np.c_[x[:,35:41],x[:,7],x[:,5]]
        entering=(phase==2)&np.r_[True,phase[:-1]!=2]
        valid=pre&((phase==0)|(phase==1)|entering)&(x[:,0]>.15)&(x[:,44]>=25)
        neg.append(data[valid])
        boundaries=np.r_[0,np.flatnonzero(np.diff(x[:,44])<=0)+1,len(x)]
        for a,b in zip(boundaries[:-1],boundaries[1:]):
            faces=np.flatnonzero(x[a:b,43]>.5)+a
            if not len(faces):continue
            first=int(faces[0])
            if np.any(entering[a:first]&pre[a:first]):continue
            pos.append((f'gpu/{j}/{a}',data[first:min(first+3,b)]))
    negative=np.concatenate(neg)
    candidates=[]
    for pmin,dp,rate,decel,leg in product((-.1,0.,.06,.1),(.02,.06,.10,.12,.15,.2,.3),
        (.2,.4,.6,1.,1.5),(.15,.4,.8,1.2,1.8),(.3,.6,1.2,1.8)):
        def hit(a):
            return (a[:,6]>pmin)&(((a[:,0]>dp)&(a[:,1]>rate))|
                ((a[:,2]>decel)&(a[:,1]>rate)&(a[:,3]>leg)))
        if hit(negative).any():continue
        found=[name for name,a in pos if hit(a).any()]
        candidates.append((len(found),sum(n.startswith('cpu/') for n in found),pmin,dp,rate,decel,leg,found))
    best=max(candidates,key=lambda c:(c[0],c[1],-c[2]))
    result=dict(negative_frames=len(negative),positive_windows=len(pos),best=dict(detected=best[0],cpu=best[1],
        pitch_min=best[2],dp=best[3],rate=best[4],decel=best[5],leg=best[6],found=best[7]),
        blocked_false_positive_cases=blocked_fp,runtime_unchanged=True)
    put(HERE/'evidence/contact_calibration'/('FULL_DR_SEPARATION.json' if args.with_dr else 'SIGNED_PITCH_SEPARATION.json'),result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()

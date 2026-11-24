"""Fit a deterministic noise-aware proprioceptive contact detector offline."""
from itertools import product
import json
import numpy as np
from fsm_paths import HERE
from fsm_io import put


def features(raw,alpha,resets=None):
    """Same causal EMA and unit-gravity noise test proposed for the FSM."""
    if raw.ndim==2:raw=raw[:,None,:]
    t,n,_=raw.shape
    state=raw[0].copy();previous=state.copy();noisy=np.zeros(n,bool)
    out=np.zeros((t,n,8),np.float32)
    for k in range(t):
        fresh=np.ones(n,bool) if k==0 else resets[k] if resets is not None else np.zeros(n,bool)
        state[fresh]=raw[k,fresh];previous[fresh]=raw[k,fresh];noisy[fresh]=False
        noisy|=np.abs(np.linalg.norm(raw[k,:,7:10],axis=1)-1.)>.003
        a=np.where(noisy,alpha,1.)[:,None]
        state+=a*(raw[k]-state)
        # Operator commands and flags are not sensor-filtered.
        state[:,:4]=raw[k,:,:4];state[:,22:]=raw[k,:,22:]
        out[k,:,0]=np.abs(state[:,7]-previous[:,7])
        out[k,:,1]=np.abs(state[:,5]-previous[:,5])
        out[k,:,2]=(previous[:,20:22]-state[:,20:22]).mean(1)*.625
        out[k,:,3]=np.abs(state[:,16:20]-previous[:,16:20]).max(1)
        out[k,:,4]=state[:,20:22].mean(1)*.625
        out[k,:,5]=np.abs(state[:,7])
        out[k,:,6]=state[:,7];out[k,:,7]=state[:,5]
        previous=state.copy()
    return out


def main():
    cpu=[]
    for directory in ('contact_calibration','contact_calibration_dr'):
        for path in (HERE/'evidence'/directory/'raw').glob('*.npz'):
            row=json.loads(path.with_suffix('.json').read_text())
            x=np.load(path)['control'];time=x[:,0]-.02
            pre=np.ones(len(x),bool) if row['course'] in ('flat','rough_L9') else x[:,48]>.10
            face=row['first_face_contact_s']
            if face is not None:pre &=time<face
            hit=np.zeros(len(x),bool) if face is None else (time>=face-.003)&(time<=face+.041)
            cpu.append((row['id'],x[:,1:36],pre,hit))
    native=np.load(HERE/'evidence/fsm_r3/probe/NATIVE_CALIBRATION.npz')['frames']
    resets=np.zeros(native.shape[:2],bool);resets[1:]=np.diff(native[:,:,44],axis=0)<=0
    best_all=None;results=[]
    for alpha in (.15,.25,.35,.5,.7,1.):
        negatives=[];positives=[];blocked_fp=[]
        for name,raw,pre,hit in cpu:
            f=features(raw,alpha)[:,0]
            negatives.append(f[pre])
            if hit.any():positives.append(('cpu/'+name,f[hit]))
            b=(f[:,6]>.11)&(np.abs(f[:,4])<.15)&(raw[:,0]>.15)&pre
            if np.any(b&np.r_[False,b[:-1]]):blocked_fp.append(name)
        nf=features(native[:,:,:35],alpha,resets)
        for j in range(native.shape[1]):
            x=native[:,j];phase=x[:,41].astype(int);pre=x[:,42].astype(bool)
            entering=(phase==2)&np.r_[True,phase[:-1]!=2]
            valid=pre&((phase==0)|(phase==1)|entering)&(x[:,0]>.15)&(x[:,44]>=25)
            negatives.append(nf[valid,j])
            boundaries=np.r_[0,np.flatnonzero(np.diff(x[:,44])<=0)+1,len(x)]
            for a,b in zip(boundaries[:-1],boundaries[1:]):
                faces=np.flatnonzero(x[a:b,43]>.5)+a
                if not len(faces):continue
                first=int(faces[0])
                if np.any(entering[a:first]&pre[a:first]):continue
                positives.append((f'gpu/{j}/{a}',nf[first:min(first+3,b),j]))
        neg=np.concatenate(negatives)
        best=None
        for pmin,dp,rate,decel,leg in product((-.1,0.,.05),(.01,.015,.02,.03,.05,.08,.1),
            (.08,.12,.16,.2,.3,.5),(.1,.2,.35,.5,.8),(.15,.25,.4,.6,.9)):
            def hit(a):
                return (a[:,6]>pmin)&(((a[:,0]>dp)&(a[:,1]>rate))|
                    ((a[:,2]>decel)&(a[:,1]>rate)&(a[:,3]>leg)))
            if hit(neg).any():continue
            found=[name for name,f in positives if hit(f).any()]
            score=(len(found),sum(n.startswith('cpu/') for n in found))
            if best is None or score>best['score']:
                best=dict(score=score,alpha=alpha,pitch_min=pmin,dp=dp,rate=rate,decel=decel,leg=leg,found=found,
                    negatives=len(neg),positive_windows=len(positives),blocked_false_positive_cases=blocked_fp)
        results.append(best)
        print(alpha,best['score'],best['dp'],best['rate'],'blocked',blocked_fp,flush=True)
        if best_all is None or best['score']>best_all['score']:best_all=best
    put(HERE/'evidence/contact_calibration/FILTERED_DR_SEPARATION.json',dict(best=best_all,results=results,
        runtime_unchanged=True,calibration_only=True))


if __name__=='__main__':main()

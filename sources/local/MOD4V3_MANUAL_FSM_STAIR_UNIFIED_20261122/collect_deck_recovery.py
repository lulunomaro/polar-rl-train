"""Training-only physical-top recovery demonstrations; no teacher in deployment."""
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import torch
from torch import nn
from fsm_paths import HERE
from fsm_io import put
from manual_fsm_runtime import ManualPolicy
from manual_fsm_core import Phase
import fsm_evaluation as ev

class RecoveryHead(nn.Module):
    def __init__(self,owner,prior,kind='lqr'):
        super().__init__();self.owner=owner;self.prior=prior
        self.kind=kind
        self.recover_ticks=0;self.context=None;self.samples=[];self.actions=[]
    def forward(self,x):
        raw=self.prior(x)
        p=self.owner
        if int(p.fsm.age[0])==0:self.recover_ticks=0
        if self.context is not None:
            sim,judge=self.context
            # Only the training teacher reads physical top support.
            forces=np.asarray(judge.trace[-8:])[:,21:25]
            on_top=bool(np.any((forces[:,0]>5.)&(forces[:,1]>5.)))
            if len(judge.levels)>1:
                on_top|=bool(np.any((forces[:,2]>5.)&(forces[:,3]>5.)))
            if on_top and p.fsm.age[0]>8:self.recover_ticks=max(self.recover_ticks,1)
            if self.recover_ticks:
                blend=min(1.,self.recover_ticks/16.)
                if self.kind=='e0':
                    target=x[:,:35].clone();target[:,3]=.35*5.
                    raw=torch.lerp(raw,p.e0(target),blend)
                    self.recover_ticks+=1
                    self.samples.append(x.numpy().copy());self.actions.append(raw.numpy().copy())
                    return raw.clamp(-6.,6.)
                goal=sim.recovery_goal
                leg=torch.as_tensor(goal,dtype=raw.dtype)[None]
                raw[:,:4]=torch.lerp(raw[:,:4],leg,blend)
                obs=x[0,:35]
                # obs[7] = -R[2,0]; it has the same pitch sign as StrictJudge.
                pitch=torch.asin(obs[7].clamp(-.9,.9));rate=2.*obs[5]
                wheel=(obs[0]+3.*pitch+.35*rate)/.625
                pair=torch.stack((wheel-.20*obs[2],wheel+.20*obs[2]))[None]
                raw[:,4:]=torch.lerp(raw[:,4:],pair,blend)
                self.recover_ticks+=1
        raw=raw.clamp(-6.,6.)
        self.samples.append(x.numpy().copy());self.actions.append(raw.numpy().copy())
        return raw

def worker(args):
    case,checkpoint=args;captured=[]
    class Policy(ManualPolicy):
        def __init__(self,*a,**kw):
            super().__init__(*a,**kw);self.stair=RecoveryHead(self,self.stair,case.get('teacher','lqr'));captured.append(self)
    ev.ManualPolicy=Policy
    def teacher_context(sim,judge,tick):
        if not hasattr(sim,'recovery_goal'):
            length=.35-.0625
            q=sim.ik.fit(np.hypot(length,sim.ik.lateral_offset),0.)['qpos']
            sim.recovery_goal=(q[sim.qa[:4]]-sim.baseline[:4])/.5
        captured[0].stair.context=(sim,judge)
    row,trace=ev.run_case(case,checkpoint=checkpoint,frames=teacher_context)
    net=captured[0].stair
    folder=HERE/'evidence'/case.get('output_tag','deck_recovery_teacher');folder.mkdir(parents=True,exist_ok=True)
    put(folder/(case['id']+'.json'),row)
    np.savez_compressed(folder/(case['id']+'.npz'),inputs=np.concatenate(net.samples) if net.samples else np.zeros((0,455)),
        actions=np.concatenate(net.actions) if net.actions else np.zeros((0,6)),**trace)
    net.context=None;net.owner=None
    return row

def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint',default='evidence/fsm_r2/train/model_009m.pt')
    p.add_argument('--workers',type=int,default=2);p.add_argument('--quick',action='store_true')
    p.add_argument('--tag',default='deck_recovery_teacher');p.add_argument('--teacher',choices=('lqr','e0'),default='lqr');args=p.parse_args()
    cases=[]
    for course in ('curb_11','step_20') if args.quick else ('curb_11','step_20','oblique_20','rm27_west_400','rm27_east_400'):
        for speed in (.6,1.2,2.):
            cases.append(dict(id=f'recover_{len(cases):03d}',course=course,speed=speed,height=.39,
                yaw_deg=0.,offset=[.20,0.] if 'rm27' not in course else [-.35,0.],seconds=7.,
                settle_s=.8,wz=0.,task='',edge_sign=1,armed=True,output_tag=args.tag,teacher=args.teacher))
    rows=[]
    with ProcessPoolExecutor(args.workers) as pool:
        for row in pool.map(worker,[(c,args.checkpoint) for c in cases]):
            rows.append(row);print(row['id'],row['course'],row['speed'],row['passed'],row['longest_bilateral_support_substeps'],row['end_phase'],flush=True)
    put(HERE/'evidence'/args.tag/'RESULT.json',dict(rows=rows,passed=sum(r['passed'] for r in rows),total=len(rows)))

if __name__=='__main__':main()

"""Closed-loop CPU teacher collection behind the exact deployed manual FSM."""
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor
import json
import numpy as np
import torch
from torch import nn
from fsm_paths import HERE,R61_DIR
from fsm_io import put
from manual_fsm_runtime import ManualPolicy,legacy
import fsm_evaluation as ev

class TeacherHead(nn.Module):
    def __init__(self,owner):
        super().__init__()
        self.owner=owner
        donor,_,_=legacy.load_manifest(R61_DIR/'CANDIDATE_R61_RAISED_READY.json')
        self.donor=donor
        self.x=[];self.a=[]
    def forward(self,x):
        frames=list(self.owner.stationary_history)
        while len(frames)<40:frames.insert(0,frames[0])
        hist=torch.stack(frames[-40:],1).flatten(1)
        out=self.donor.height_stair_outputs(x[:,:35],hist)['a_stair'].clamp(-6.,6.)
        self.x.append(x.numpy().copy());self.a.append(out.numpy().copy())
        return out

class TeacherPolicy(ManualPolicy):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        self.stair=TeacherHead(self)

def worker(case):
    captured=[]
    class Captured(TeacherPolicy):
        def __init__(self,*a,**kw):
            super().__init__(*a,**kw);captured.append(self)
    ev.ManualPolicy=Captured
    row,trace=ev.run_case(case)
    folder=HERE/'evidence/closed_loop_teacher'
    folder.mkdir(parents=True,exist_ok=True)
    put(folder/(case['id']+'.json'),row)
    net=captured[0].stair
    np.savez_compressed(folder/(case['id']+'.npz'),inputs=np.concatenate(net.x) if net.x else np.zeros((0,455)),
        actions=np.concatenate(net.a) if net.a else np.zeros((0,6)),**trace)
    net.owner=None
    return row

def main():
    p=ArgumentParser(description=__doc__);p.add_argument('--workers',type=int,default=2);args=p.parse_args()
    cases=[]
    for course in ('curb_11','step_20','rm27_west_400','rm27_east_400'):
        for speed in (.6,1.2,2.):
            cases.append(dict(id=f'teacher_{len(cases):03d}',course=course,speed=speed,height=.39,
                yaw_deg=0.,offset=[.20,0.] if course in ('curb_11','step_20') else [-.35,0.],seconds=7.,
                settle_s=.8,wz=0.,task='',edge_sign=1,armed=True))
    rows=[]
    with ProcessPoolExecutor(args.workers) as pool:
        for row in pool.map(worker,cases):
            rows.append(row);print(row['id'],row['course'],row['speed'],row['passed'],row['longest_bilateral_support_substeps'],row['end_phase'],flush=True)
    put(HERE/'evidence/closed_loop_teacher/RESULT.json',dict(rows=rows,passed=sum(r['passed'] for r in rows),total=len(rows)))

if __name__=='__main__':main()

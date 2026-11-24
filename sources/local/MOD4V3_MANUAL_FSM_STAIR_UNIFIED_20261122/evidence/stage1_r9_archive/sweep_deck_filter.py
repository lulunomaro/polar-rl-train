"""Isolate E0 leg-target smoothing after the FSM has finished climbing."""
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from argparse import ArgumentParser
import numpy as np
import fsm_evaluation as ev
from fsm_paths import HERE
from fsm_io import put
from manual_fsm_core import Phase


def worker(case):
    original=ev.ManualPolicy
    class Policy(original):
        def act(self,obs):
            a,r=super().act(obs)
            if not hasattr(self,'filtered'):self.filtered=a[:4].copy()
            eligible=(r['e1']==0. and r['e2']==0.) if case.get('all_e0') else self.fsm.phase[0]==Phase.DECK_SETTLE
            alpha=case['filter_alpha'] if eligible else 1.
            self.filtered+=alpha*(a[:4]-self.filtered)
            a[:4]=self.filtered
            return a,r
    ev.ManualPolicy=Policy
    try:
        r,t=ev.run_case(case,checkpoint=HERE/'evidence/fsm_r5/train/model_018m.pt')
    finally:ev.ManualPolicy=original
    put(HERE/'evidence'/case['output_tag']/(case['id']+'.json'),r)
    return r


def main():
    p=ArgumentParser();p.add_argument('--all-e0',action='store_true');args=p.parse_args()
    tag='all_e0_filter_experiment' if args.all_e0 else 'deck_filter_experiment'
    cases=[dict(id=f'deck_{len_idx}',course=course,speed=speed,height=.39,yaw_deg=0.,
        offset=[.2,0.],seconds=7.,settle_s=.8,wz=0.,task='',edge_sign=1,armed=True,filter_alpha=alpha,
        all_e0=args.all_e0,output_tag=tag)
        for len_idx,(course,speed,alpha) in enumerate(product(('curb_11','step_20'),(.8,1.2,2.),(.04,.08,1.)))]
    rows=[]
    with ProcessPoolExecutor(4) as pool:
        for r in pool.map(worker,cases):
            rows.append(r);print(r['course'],r['speed'],r['filter_alpha'],r['passed'],
                r['longest_bilateral_support_substeps'],r['failure'],flush=True)
    put(HERE/'evidence'/tag/'RESULT.json',dict(rows=rows,passed=sum(r['passed'] for r in rows),total=len(rows)))


if __name__=='__main__':main()

"""Raised-box controls: isolate frozen E0 from stair execution and handoff."""
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor
from itertools import product
import numpy as np
import torch
from fsm_paths import HERE
from fsm_io import put
import fsm_evaluation as evaluation


def worker(case):
    # Reset is on the deck, but the scorer's level is relative to the arena
    # floor. Keep these independent references explicit.
    original = evaluation.ContactJudge
    class RaisedJudge(original):
        def __init__(self, sim, case, yaw, direction, ground):
            super().__init__(sim, case, yaw, direction, 0.)
    evaluation.ContactJudge = RaisedJudge
    policy_class = evaluation.ManualPolicy
    alpha=case.get('filter_alpha',1.)
    class FilteredPolicy(policy_class):
        def act(self,obs):
            action,route=super().act(obs)
            if not hasattr(self,'filtered_legs'):self.filtered_legs=action[:4].copy()
            self.filtered_legs+=alpha*(action[:4]-self.filtered_legs)
            action[:4]=self.filtered_legs
            return action,route
    evaluation.ManualPolicy=FilteredPolicy
    try:
        row, trace = evaluation.run_case(case)
        loads=trace['reference_trace'][:,21:23]
        tail=trace['physics'][:,0]>=1.5
        best=streak=0
        for good in (loads[tail]>5.).all(1):
            streak=streak+1 if good else 0
            best=max(best,streak)
        row['moving_tail_best_substeps']=int(best)
        row['moving_tail_contact_fraction']=float((loads[tail]>5.).all(1).mean())
    finally:
        evaluation.ContactJudge = original
        evaluation.ManualPolicy=policy_class
    return row


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--filter-sweep',action='store_true')
    args = p.parse_args()
    cases = [dict(id=f'e0_{h}_{v}', course='step_20', speed=v, height=h, yaw_deg=0.,
        offset=[2., 0.], seconds=4., settle_s=.8, wz=0., task='', edge_sign=1, armed=False)
        for h, v in product((.24, .28, .32, .34, .35, .36, .38, .42), (0., 1.2, 2.8))]
    if args.filter_sweep:
        cases=[dict(id=f'filter_{h}_{v}_{alpha}',course='step_20',speed=v,height=h,yaw_deg=0.,
            offset=[2.,0.],seconds=4.,settle_s=.8,wz=0.,task='',edge_sign=1,armed=False,filter_alpha=alpha)
            for h,v,alpha in product((.35,.39),(1.2,2.8),(.04,.02,.01,0.))]
    rows = []
    with ProcessPoolExecutor(args.workers) as pool:
        for row in pool.map(worker, cases):
            rows.append(row)
            print(row['height'], row['speed'], row['longest_bilateral_support_substeps'],
                  row['moving_tail_best_substeps'],row.get('filter_alpha'),row['failure'],flush=True)
    put(HERE/'evidence'/('E0_FILTER_SUPPORT_SWEEP_SLOW.json' if args.filter_sweep else 'E0_RAISED_SUPPORT_SWEEP.json'), dict(rows=rows, physics_hz=400,
        explanation='Unarmed frozen E0, reset entirely on 200 mm deck; no stair actions.'))


if __name__ == '__main__':
    main()

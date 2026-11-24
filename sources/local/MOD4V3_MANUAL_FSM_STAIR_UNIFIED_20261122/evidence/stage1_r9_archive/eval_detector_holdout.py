"""Independent nominal/full-DR early-arm audit for the noise-aware FSM."""
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from argparse import ArgumentParser
from eval_manual_fsm_all import worker
from fsm_paths import HERE
from fsm_io import put


def main():
    p=ArgumentParser();p.add_argument('--tag',default='noise_filter_holdout_r2');p.add_argument('--seed',type=int,default=919)
    args=p.parse_args()
    folder=HERE/'evidence'/args.tag
    jobs=[]
    for dr,course,speed in product((0.,1.),('flat','rough_L9','step_20','rm27_west_400','rm27_east_400'),(.8,1.2,1.6,2.)):
        if course in ('flat','rough_L9'):offset=[-1.5,0.] if course=='rough_L9' else [0.,0.]
        else:offset=[-1.8,0.] if course=='step_20' else [-2.1,0.]
        c=dict(id=f'holdout_{len(jobs):03d}',course=course,speed=speed,height=.39,yaw_deg=0.,
            offset=offset,seconds=6. if course in ('flat','rough_L9') else 10.,settle_s=.8,wz=0.,task='',
            edge_sign=1,armed=True,dr=dr,seed=args.seed)
        jobs.append((c,HERE/'evidence/fsm_r5/train/model_024m.pt',folder))
    rows=[]
    with ProcessPoolExecutor(2) as pool:
        for r in pool.map(worker,jobs):
            rows.append(r)
            print(r['id'],r['dr'],r['course'],r['speed'],'pre',r['precontact_active_samples'],
                'height',r['precontact_min_relative_height_m'],'delay',r['trigger_delay_ms'],flush=True)
    put(folder/'RESULT.json',dict(rows=rows,total=len(rows),
        precontact_active_samples=sum(r['precontact_active_samples'] for r in rows),
        zero_activation_cases=sum(r['precontact_active_samples']==0 for r in rows),
        minimum_precontact_height_m=min(r['precontact_min_relative_height_m'] for r in rows
            if r['precontact_min_relative_height_m'] is not None),
        note=f'Seed {args.seed} is excluded from detector fitting; this is not stair graduation.'))


if __name__=='__main__':main()

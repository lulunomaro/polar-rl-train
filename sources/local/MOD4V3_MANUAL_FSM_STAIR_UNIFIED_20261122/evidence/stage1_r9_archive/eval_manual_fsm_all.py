"""Run the shared manual-FSM player through independent CPU MuJoCo benchmarks."""
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import product
import json
from pathlib import Path
import numpy as np
from fsm_paths import HERE
from fsm_io import put
from fsm_evaluation import run_case
from fsm_maps import reference

def cases(suite):
    out=[]
    def add(course,speed,height=.39,yaw=0.,offset=None,seconds=7.,**kw):
        row=dict(id=f'{suite}_{len(out):04d}_{course}',course=course,speed=speed,height=height,
                 yaw_deg=yaw,offset=offset or [0.,0.],seconds=seconds,settle_s=.8,wz=0.,task='',
                 edge_sign=-1 if course.endswith('negative') else 1,armed=False,dr=0.)
        row.update(kw)
        out.append(row)
    if suite=='flat60':
        out=reference.cases()[:60]
        for r in out:
            r.update(armed=False,dr=0.,id='fsm_'+r['id'])
        return out
    if suite in ('flat','premature','pilot'):
        heights=(.24,.28,.36,.42) if suite=='flat' else (.39,)
        speeds=(-.6,1.,0.,0.) if suite=='flat' else (.8,1.6,2.4,2.8,3.)
        for course,h,(v,w) in product(('flat','rough_L9'),heights,
                zip(speeds,(0.,0.,-1.8,1.8)) if suite=='flat' else [(v,0.) for v in speeds]):
            add(course,v,h,offset=[-1.5,0.] if course=='rough_L9' else [0.,0.],seconds=6. if suite=='premature' else 3.5,wz=w)
    if suite=='premature':
        for course,speed in product(('step_20','rm27_west_400','rm27_east_400'),(.8,1.2,1.6,2.)):
            # The conservative front bound starts at least 2.5 m from the face.
            offset=[-1.8,0.] if course=='step_20' else [-2.1,0.]
            add(course,speed,offset=offset,seconds=10.,armed=True)
    if suite in ('stair','pilot'):
        speeds=(.6,1.,1.5,2.) if suite=='stair' else (.8,1.2,2.)
        offsets=(-.06,-.03,0.,.03,.06) if suite=='stair' else (0.,)
        for course,speed,dx in product(('curb_11','step_20'),speeds,offsets):
            add(course,speed,offset=[.20+dx,0.],armed=True,seconds=6.)
        for course,yaw,speed in product(('step_20','oblique_20','oblique_20_negative'),
                                        (-25.,25.),(1.,2.) if suite=='stair' else (1.2,)):
            add(course,speed,yaw=yaw,offset=[.20,0.],armed=True,seconds=6.)
        for course,speed in product(tuple(reference.DOUBLE),(.8,1.2,2.) if suite=='stair' else (1.2,)):
            add(course,speed,offset=[-.35,0.],armed=True,seconds=7.)
        for course,speed in product(('curb_11','step_20'),(.6,1.,1.5,2.) if suite=='stair' else (1.2,)):
            add(course,speed,offset=[.68,0.],armed=True,seconds=7.,restart=True,settle_s=0.)
            add(course,speed,offset=[.68,0.],armed=True,force_at_s=.2,seconds=7.,restart=True,settle_s=0.)
        if suite=='stair':
            base=list(out)
            for seed in (1729,2718,3141):
                for row in base:
                    out.append(dict(row,id=f"{row['id']}_dr{seed}",dr=1.,seed=seed))
    return out

def worker(args):
    import gc
    case,checkpoint,output=args
    row,trace=run_case(case,checkpoint=checkpoint)
    output=Path(output)
    put(output/'cases'/(case['id']+'.json'),row)
    folder=output/'traces'
    folder.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(folder/(case['id']+'.npz'),**trace)
    gc.collect()
    return row

def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument('--suite',choices=('pilot','flat60','flat','premature','stair','all'),default='pilot')
    p.add_argument('--checkpoint',type=Path)
    p.add_argument('--out',type=Path)
    p.add_argument('--workers',type=int,default=2)
    p.add_argument('--courses',nargs='+')
    p.add_argument('--limit',type=int)
    args=p.parse_args()
    suites=('flat60','flat','premature','stair') if args.suite=='all' else (args.suite,)
    for suite in suites:
        output=args.out or HERE/'evidence'/f'eval_{suite}'
        jobs=cases(suite)
        if args.courses:jobs=[r for r in jobs if r['course'] in args.courses]
        if args.limit:jobs=jobs[:args.limit]
        rows=[]
        with ProcessPoolExecutor(args.workers) as pool:
            futures={pool.submit(worker,(case,args.checkpoint,output)):case for case in jobs}
            for future in as_completed(futures):
                row=future.result()
                rows.append(row)
                print(row['id'],'strict',row['passed'],'support',row['longest_bilateral_support_substeps'],
                      'pre',row['precontact_active_samples'],'delay',row['trigger_delay_ms'],'fall',row['failure'],flush=True)
        rows.sort(key=lambda r:r['id'])
        put(output/'RESULT.json',dict(suite=suite,passed=sum(r['passed'] for r in rows),total=len(rows),
            physical=sum(r['physical_crossed'] and not r['failure'] for r in rows),
            nominal=sum(r['passed'] for r in rows if not r.get('dr',0.)),
            full_dr=sum(r['passed'] for r in rows if r.get('dr',0.)==1.),
            precontact_active_samples=sum(r['precontact_active_samples'] for r in rows),
            physics_hz=400,rows=rows))
        print(suite,sum(r['passed'] for r in rows),'/',len(rows),flush=True)

if __name__=='__main__':
    main()

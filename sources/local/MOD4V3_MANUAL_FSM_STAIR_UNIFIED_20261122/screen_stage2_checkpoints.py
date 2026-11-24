"""Compare fixed closed-loop stair cases before selecting a PPO checkpoint."""
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from eval_manual_fsm_all import cases,worker
from fsm_paths import HERE
from fsm_io import put,sha256


def screen_cases():
    base=[r for r in cases('stair') if not r['dr']]
    chosen=[]
    for r in base:
        c=r['course']; v=r['speed']; offset=r['offset'][0]
        keep=c in ('rm27_west','rm27_east')
        keep |= c in ('rm27_west_400','rm27_east_400') and v==1.2
        keep |= c=='step_20' and abs(r['yaw_deg'])==25 and v==1.
        keep |= c=='step_20' and bool(r.get('restart')) and v==.6
        keep |= c=='step_20' and not r.get('restart') and r['yaw_deg']==0 and abs(offset-.2)<1.e-6 and v in (.6,2.)
        keep |= c in ('oblique_20','oblique_20_negative') and r['yaw_deg']==25 and v==1.
        if keep:chosen.append(r)
    dr=[]
    for r in chosen:
        if (r['course'] in ('rm27_west','rm27_east') and r['speed']==1.2) or (r['course']=='step_20' and r['yaw_deg']==0):
            dr.append(dict(r,id=r['id']+'_dr3141',dr=1.,seed=3141))
    return chosen+dr


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--workers',type=int,default=2)
    a=p.parse_args()
    jobs=screen_cases();rows=[]
    with ProcessPoolExecutor(a.workers) as pool:
        for row in pool.map(worker,[(r,a.checkpoint,a.out) for r in jobs]):
            rows.append(row)
            print(row['id'],row['passed'],row['physical_crossed'],row['failure'],
                row['longest_bilateral_support_windows_20ms'],row['precontact_active_samples'],flush=True)
    unforced=[r for r in rows if not r.get('force_at_s')]
    rm=[r for r in rows if r['course'] in ('rm27_west','rm27_east') and not r['dr']]
    score=[-sum(r['precontact_active_samples']>0 for r in unforced),sum(r['passed'] for r in rm),
        sum(r['passed'] for r in rows),sum(r['physical_crossed'] and not r['failure'] for r in rows),
        -sum(bool(r['failure']) for r in rows)]
    result=dict(checkpoint=str(a.checkpoint.resolve().relative_to(HERE)),sha256=sha256(a.checkpoint),
        calibration_sha256=sha256(HERE/'E0_CALIBRATION.json'),detector_sha256=sha256(HERE/'DETECTOR.json'),
        source_code_sha256={n:sha256(HERE/n) for n in ('manual_fsm_model.py','manual_fsm_core.py','manual_fsm_runtime.py','fsm_evaluation.py')},
        cases=len(rows),passed=sum(r['passed'] for r in rows),score=score,rows=rows,
        selection_rule='lexicographic: unforced early activation violations, full-map nominal RM strict passes, total strict passes, physical no-fall crossings, falls')
    put(a.out/'RESULT.json',result)
    print('SCREEN',score,flush=True)


if __name__=='__main__':main()

"""Frozen-E0 negative/impact traces with full sensor and physical randomization."""
from concurrent.futures import ProcessPoolExecutor
from itertools import product
import numpy as np
from fsm_paths import HERE
from fsm_io import put
from fsm_evaluation import run_case


def worker(case):
    row,trace=run_case(case,calibration=True)
    folder=HERE/'evidence/contact_calibration_dr/raw'
    folder.mkdir(parents=True,exist_ok=True)
    put(folder/(case['id']+'.json'),row)
    np.savez_compressed(folder/(case['id']+'.npz'),**trace)
    return row


def main():
    cases=[]
    for course,speed,seed in product(('flat','step_20'),(.8,1.6,2.8),(111,222,333)):
        cases.append(dict(id=f'drcal_{len(cases):03d}',course=course,speed=speed,height=.39,
            yaw_deg=0.,offset=[0.,0.] if course=='flat' else [-1.8,0.],seconds=6.,
            settle_s=.8,wz=0.,task='',edge_sign=1,armed=True,dr=1.,seed=seed))
    rows=[]
    with ProcessPoolExecutor(1) as pool:
        for r in pool.map(worker,cases):
            rows.append(r);print(r['id'],r['course'],r['speed'],r['failure'],r['first_face_contact_s'],flush=True)
    put(HERE/'evidence/contact_calibration_dr/RESULT.json',dict(rows=rows,
        purpose='Calibration only; frozen E0, zero PPO/optimizer steps'))


if __name__=='__main__':main()

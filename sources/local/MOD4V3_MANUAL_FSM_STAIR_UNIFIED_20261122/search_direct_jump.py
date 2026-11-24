"""Offline key-timing calibration using the fixed moving jump expert."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from itertools import product
from eval_fsm_jump import worker
from fsm_paths import HERE
from fsm_io import put


def main():
    tag='direct_jump_'+datetime.now().strftime('%Y%m%d_%H%M%S')
    cases=[]
    for h,gap in product((.24,.28,.32),(.7,.9,1.1,1.3)):
        cases.append(dict(id=f'key_{len(cases):03d}',course='platform_380',speed=2.8,
            height=h,yaw_deg=0.,offset=[0.,0.],seconds=7.,settle_s=.8,
            front_gap=gap,wz=0.,task='',armed=False,hold_ticks=31,output_tag=tag))
    rows=[]
    with ProcessPoolExecutor(4) as pool:
        for r in pool.map(worker,cases):
            rows.append(r)
            print(r['height'],r['front_gap'],r['passed'],round(r['peak_bilateral_tire_clearance_m'],3),
                round(r['peak_riser_face_force_n'],2),r['main_flight_first_landing_on_top'],flush=True)
    put(HERE/'evidence'/tag/'RESULT.json',dict(rows=rows,passed=sum(r['passed'] for r in rows),total=len(rows)))


if __name__=='__main__':main()

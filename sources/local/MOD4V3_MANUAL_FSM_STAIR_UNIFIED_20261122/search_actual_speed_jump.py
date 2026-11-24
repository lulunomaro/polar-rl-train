"""Calibrate key timing only after measured approach speed reaches the target."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from itertools import product
from eval_fsm_jump import worker
from fsm_paths import HERE
from fsm_io import put


def main():
    tag='actual_speed_jump_'+datetime.now().strftime('%Y%m%d_%H%M%S')
    jobs=[]
    for speed,heights,gaps in ((2.8,(.28,.32,.36),(.55,.7,.85,1.)),(1.6,(.24,.28),(.35,.5,.65))):
        for h,gap in product(heights,gaps):
            jobs.append(dict(id=f'actual_{len(jobs):03d}',course='platform_380',speed=speed,height=h,
                yaw_deg=0.,offset=[-5.,0.],seconds=10.,settle_s=.8,front_gap=gap,wz=0.,task='',
                armed=False,hold_ticks=31,output_tag=tag,checkpoint='evidence/fsm_r9/train/model_009m.pt'))
    rows=[]
    with ProcessPoolExecutor(2) as pool:
        for r in pool.map(worker,jobs):
            rows.append(r);print(r['speed'],r['height'],r['front_gap'],r['passed'],
                'key_v',round(r['actual_speed_at_key_m_s'] or 0.,3),'peak',round(r['peak_bilateral_tire_clearance_m'],3),
                'face',round(r['peak_riser_face_force_n'],1),flush=True)
    put(HERE/'evidence'/tag/'RESULT.json',dict(rows=rows,passed=sum(r['passed'] for r in rows),total=len(rows)))


if __name__=='__main__':main()

"""Offline timing search for the 1.6 m/s unified-player 380 mm jump."""
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from datetime import datetime
from argparse import ArgumentParser
from fsm_paths import HERE
from fsm_io import put
from eval_fsm_jump import worker

def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument('--heights',type=float,nargs='+',default=(.24,.28))
    p.add_argument('--holds',type=int,nargs='+',default=(31,))
    p.add_argument('--gaps',type=float,nargs='+',default=(.25,.35,.45,.55,.65,.75))
    args=p.parse_args()
    tag='mid_jump_'+datetime.now().strftime('%Y%m%d_%H%M%S')
    jobs=[]
    for height,hold,gap in product(args.heights,args.holds,args.gaps):
        jobs.append(dict(id=f'mid_{len(jobs):03d}',output_tag=tag,course='platform_380',speed=1.6,height=height,
            yaw_deg=0.,offset=[0.,0.],seconds=7.,settle_s=.8,front_gap=gap,wz=0.,task='',armed=False,hold_ticks=hold))
    rows=[]
    with ProcessPoolExecutor(2) as pool:
        for row in pool.map(worker,jobs):
            rows.append(row)
            print(row['id'],row['height'],row['hold_ticks'],row['front_gap'],row['passed'],row['both_wheels_top_samples'],row['failure'],flush=True)
    put(HERE/'evidence'/tag/'RESULT.json',dict(total=len(rows),passed=sum(r['passed'] for r in rows),rows=rows))

if __name__=='__main__':main()

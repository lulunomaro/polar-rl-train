import argparse,json,time,numpy as np
from control_core import Plant,ROOT
from jump_trial import run
from concurrent.futures import ProcessPoolExecutor,as_completed

def trial(item):
    idx,cfg=item
    try:
        r,_=run(cfg,False)
        score=5*r['max_wheel_bottom']+2*r['air_time']+r['last']['upright_cos']+.2*min(r['last']['xyz'][0]+.6,1)
        if r.get('stop_reason')=='health':score-=2
        return idx,score,r
    except Exception as e:return idx,-100,{'config':cfg,'error':str(e)}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--n',type=int,default=64);ap.add_argument('--workers',type=int,default=8);ap.add_argument('--out',default='sweep_v1');args=ap.parse_args()
    rng=np.random.default_rng(20261101);cfgs=[]
    for i in range(args.n):
        cfg={'step':False,'duration':2.5,'push_at':.6,'speed':0.,'start_delta':float(rng.uniform(-.5,-.1)),'hip_shift':float(rng.uniform(-.7,-.15)),'push_for':float(rng.uniform(.08,.28)),'push_delta':float(rng.uniform(.15,.45)),'tuck_delta':float(rng.uniform(-1.,-.4)),'tuck_hip':float(rng.uniform(.1,.49)),'push_kp':float(rng.uniform(150,500)),'push_kd':float(rng.uniform(1,6)),'pitch_gain':float(rng.uniform(-12,20)),'air_pitch':float(rng.uniform(-10,18)),'wheel_push':float(rng.uniform(-2,2))}
        cfgs.append((i,cfg))
    folder=ROOT/'results'/args.out;folder.mkdir(exist_ok=True);rows=[];start=time.time()
    with ProcessPoolExecutor(args.workers) as pool,open(folder/'all_trials.jsonl','w') as f:
        for future in as_completed([pool.submit(trial,x) for x in cfgs]):
            idx,score,r=future.result();row={'id':idx,'score':score,'result':r};rows.append(row);f.write(json.dumps(row)+'\n');f.flush()
            if len(rows)%8==0:
                best=max(rows,key=lambda r:r['score']);print(json.dumps({'done':len(rows),'seconds':time.time()-start,'best':best}),flush=True)
    rows.sort(key=lambda r:r['score'],reverse=True);(folder/'ranked.json').write_text(json.dumps(rows,indent=2));print(json.dumps({'complete':True,'best':rows[0],'seconds':time.time()-start}),flush=True)

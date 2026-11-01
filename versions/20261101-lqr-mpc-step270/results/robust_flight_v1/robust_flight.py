import json,time,numpy as np,shutil
from concurrent.futures import ProcessPoolExecutor,as_completed
from hybrid_trial import run
from control_core import ROOT

def one(v):
    i,c=v
    try:r,_=run(c,False);return {'id':i,'result':r}
    except Exception as e:return {'id':i,'result':{'config':c,'success':False,'error':str(e)}}
if __name__=='__main__':
    base=json.load(open(ROOT/'results/smooth_landing_v1/best_config.json'));base.update(duration=5.,full_dr=True,launch_x=-.5,measured_launch_pose=True)
    cfgs=[];rng=np.random.default_rng(20261104)
    settings=[{'extend_after':float(e),'tuck_hip':float(h),'push_for':float(d),'hip_shift':float(s)} for e,h,d,s in zip(rng.uniform(.15,.4,40),rng.uniform(-.1,.3,40),rng.uniform(.075,.14,40),rng.uniform(-.8,-.45,40))]
    for params in settings:
        for seed in range(1000,1006):c=dict(base,**params,seed=seed);cfgs.append((len(cfgs),c))
    folder=ROOT/'results/robust_flight_v1';folder.mkdir(exist_ok=False);rows=[];start=time.time()
    for name in ['hybrid_trial.py','control_core.py','full_lqr.py','dr_components.py','robust_flight.py']:shutil.copy2(ROOT/name,folder/name)
    with ProcessPoolExecutor(24) as pool,open(folder/'all_trials.jsonl','w') as f:
        for fut in as_completed([pool.submit(one,v) for v in cfgs]):
            row=fut.result();rows.append(row);f.write(json.dumps(row)+'\n');f.flush()
    groups={}
    for row in rows:
        r=row['result'];c=r['config'];key=str(tuple(c[k] for k in ['extend_after','tuck_hip','push_for','hip_shift']));g=groups.setdefault(key,{'n':0,'success':0,'cross':0,'stable_sum':0.,'config':dict(c,full_dr=False)})
        g['n']+=1;g['success']+=r.get('success',False);g['cross']+=bool(r.get('cross') and r['cross']['flight_id']==1);g['stable_sum']+=r.get('stable_time',0.)
    ranked=sorted(groups.values(),key=lambda g:(g['success'],g['stable_sum'],g['cross']),reverse=True);(folder/'summary.json').write_text(json.dumps({'ranked':ranked,'rows':rows},indent=2));(folder/'best_config.json').write_text(json.dumps(ranked[0]['config'],indent=2));print(json.dumps({'complete':True,'best_groups':ranked[:5],'seconds':time.time()-start}),flush=True)

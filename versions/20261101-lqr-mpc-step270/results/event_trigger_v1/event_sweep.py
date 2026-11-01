import json,time,numpy as np,shutil
from concurrent.futures import ProcessPoolExecutor,as_completed
from hybrid_trial import run
from control_core import ROOT

def one(v):
    i,c=v
    try:r,_=run(c,False);return {'id':i,'result':r}
    except Exception as e:return {'id':i,'result':{'config':c,'success':False,'error':str(e)}}
if __name__=='__main__':
    base=json.load(open(ROOT/'results/strict_landing_v1/best_config.json'));base['duration']=4.;cfgs=[];index=[]
    for launch in [-.50,-.455,-.41,-.365]:
        for measured in [False,True]:
            for seed in [1000,1001,1002,1003,1004,1005,1006,1007]:
                c=dict(base,launch_x=launch,full_dr=True,seed=seed,measured_launch_pose=measured);cfgs.append((len(cfgs),c));index.append((launch,measured))
    folder=ROOT/'results/event_trigger_v1';folder.mkdir(exist_ok=False);rows=[]
    for name in ['hybrid_trial.py','full_lqr.py','control_core.py','dr_components.py','event_sweep.py']:shutil.copy2(ROOT/name,folder/name)
    with ProcessPoolExecutor(16) as pool,open(folder/'all_trials.jsonl','w') as f:
        for fut in as_completed([pool.submit(one,v) for v in cfgs]):
            row=fut.result();rows.append(row);f.write(json.dumps(row)+'\n');f.flush()
    groups={}
    for row in rows:
        r=row['result'];cfg=r['config'];key=str((cfg['launch_x'],cfg['measured_launch_pose']));g=groups.setdefault(key,{'n':0,'success':0,'cross_first':0,'stable_sum':0.})
        g['n']+=1;g['success']+=r.get('success',False);g['cross_first']+=bool(r.get('cross') and r['cross']['flight_id']==1);g['stable_sum']+=r.get('stable_time',0)
    (folder/'summary.json').write_text(json.dumps({'groups':groups,'rows':rows},indent=2));print(json.dumps({'groups':groups}),flush=True)

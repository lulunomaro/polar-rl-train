import json,time,numpy as np,shutil
from concurrent.futures import ProcessPoolExecutor,as_completed
from hybrid_trial import run
from control_core import ROOT

def one(v):
    i,c=v
    try:r,_=run(c,False);return {'id':i,'result':r}
    except Exception as e:return {'id':i,'result':{'config':c,'success':False,'error':str(e)}}
if __name__=='__main__':
    base=json.load(open(ROOT/'results/strict_landing_v1/best_config.json'));base.update(duration=5.,full_dr=True,smooth_landing=True,landing_delta=-.4)
    cfgs=[]
    for event in [False,True]:
        for blend in [.1,.3,.5]:
            for run_speed in [.5,1.,1.5]:
                for run_s in [.3,.6]:
                    for seed in range(1000,1008):
                        cfg=dict(base,landing_blend_s=blend,landing_run_speed=run_speed,landing_run_s=run_s,seed=seed)
                        if event:cfg.update(launch_x=-.5,measured_launch_pose=True)
                        cfgs.append((len(cfgs),cfg))
    folder=ROOT/'results/robust_smooth_v1';folder.mkdir(exist_ok=False);rows=[];start=time.time()
    for name in ['hybrid_trial.py','full_lqr.py','control_core.py','dr_components.py','robust_smooth.py']:shutil.copy2(ROOT/name,folder/name)
    with ProcessPoolExecutor(24) as pool,open(folder/'all_trials.jsonl','w') as f:
        for fut in as_completed([pool.submit(one,v) for v in cfgs]):
            row=fut.result();rows.append(row);f.write(json.dumps(row)+'\n');f.flush()
    groups={}
    for row in rows:
        r=row['result'];c=r['config'];key=str((bool(c.get('launch_x')),c['landing_blend_s'],c['landing_run_speed'],c['landing_run_s']));g=groups.setdefault(key,{'n':0,'success':0,'cross':0,'stable_sum':0.,'config':dict(c,full_dr=False)})
        g['n']+=1;g['success']+=r.get('success',False);g['cross']+=bool(r.get('cross') and r['cross']['flight_id']==1);g['stable_sum']+=r.get('stable_time',0.)
    ranked=sorted(groups.values(),key=lambda g:(g['success'],g['stable_sum']),reverse=True);(folder/'summary.json').write_text(json.dumps({'ranked':ranked,'rows':rows},indent=2));(folder/'best_config.json').write_text(json.dumps(ranked[0]['config'],indent=2));print(json.dumps({'complete':True,'best_groups':ranked[:8],'seconds':time.time()-start}),flush=True)

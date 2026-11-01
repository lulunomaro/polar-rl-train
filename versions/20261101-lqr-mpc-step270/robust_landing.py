"""Search landing feedback across a fixed full-DR ensemble; preserve every run."""
import json,time,numpy as np,shutil
from concurrent.futures import ProcessPoolExecutor,as_completed
from hybrid_trial import run
from control_core import ROOT

def one(item):
    i,cfg=item
    try:r,_=run(cfg,False);return {'id':i,'result':r}
    except Exception as e:return {'id':i,'result':{'config':cfg,'success':False,'error':str(e)}}
if __name__=='__main__':
    base=json.load(open(ROOT/'results/strict_landing_v1/best_config.json'));base.update(duration=4.,launch_x=-.5,measured_launch_pose=True,full_dr=True)
    cfgs=[]
    for landing in [-.2,-.4,-.55,-.7]:
        for capture in [.1,.4,.8]:
            for minx in [.4,.7]:
                for seed in range(1000,1008):
                    cfg=dict(base,landing_delta=landing,capture_time=capture,landing_min_x=minx,seed=seed);cfgs.append((len(cfgs),cfg))
    folder=ROOT/'results/robust_landing_v1';folder.mkdir(exist_ok=False);rows=[];start=time.time()
    for name in ['control_core.py','full_lqr.py','hybrid_trial.py','dr_components.py','robust_landing.py']:shutil.copy2(ROOT/name,folder/name)
    with ProcessPoolExecutor(20) as pool,open(folder/'all_trials.jsonl','w') as f:
        for future in as_completed([pool.submit(one,v) for v in cfgs]):
            row=future.result();rows.append(row);f.write(json.dumps(row)+'\n');f.flush()
    groups={}
    for row in rows:
        r=row['result'];c=r['config'];key=str((c['landing_delta'],c['capture_time'],c['landing_min_x']));g=groups.setdefault(key,{'n':0,'success':0,'stable_sum':0.,'config':dict(c,full_dr=False)})
        g['n']+=1;g['success']+=r.get('success',False);g['stable_sum']+=r.get('stable_time',0.)
    ranked=sorted(groups.values(),key=lambda g:(g['success'],g['stable_sum']),reverse=True);(folder/'summary.json').write_text(json.dumps({'ranked':ranked,'rows':rows},indent=2));(folder/'best_config.json').write_text(json.dumps(ranked[0]['config'],indent=2));print(json.dumps({'complete':True,'groups':ranked,'seconds':time.time()-start}),flush=True)

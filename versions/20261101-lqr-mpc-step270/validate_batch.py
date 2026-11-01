import json,time,shutil,numpy as np
from concurrent.futures import ProcessPoolExecutor,as_completed
from hybrid_trial import run
from control_core import ROOT

def one(item):
    i,cfg=item
    try:r,_=run(cfg,False);return {'id':i,'result':r}
    except Exception as e:return {'id':i,'result':{'config':cfg,'error':str(e),'success':False}}
if __name__=='__main__':
    base=json.load(open(ROOT/'results/strict_landing_v1/best_config.json'));base['duration']=5.;folder=ROOT/'results/validation_fullDR_v2';folder.mkdir(exist_ok=False)
    for name in ['hybrid_trial.py','full_lqr.py','control_core.py','linear_mpc.py','dr_components.py']:shutil.copy2(ROOT/name,folder/name)
    cfgs=[(0,dict(base,full_dr=False,mpc=False)),(1,dict(base,full_dr=False,mpc=True))]
    cfgs += [(i+2,dict(base,full_dr=True,seed=1000+i,mpc=False)) for i in range(32)]
    rows=[];start=time.time()
    with ProcessPoolExecutor(16) as pool,open(folder/'all_trials.jsonl','w') as f:
        for fut in as_completed([pool.submit(one,v) for v in cfgs]):
            r=fut.result();rows.append(r);f.write(json.dumps(r)+'\n');f.flush()
            v=r['result'];print(json.dumps({'id':r['id'],'success':v.get('success'),'cross':v.get('cross'),'stable':v.get('stable_time'),'stop':v.get('stop_reason'),'error':v.get('error')}),flush=True)
    nominal=[r for r in rows if r['id']<2];dr=[r for r in rows if r['id']>=2]
    out={'nominal':nominal,'fullDR_successes':sum(r['result'].get('success',False) for r in dr),'fullDR_trials':len(dr),'wall_s':time.time()-start,'rows':rows}
    (folder/'summary.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ('rows','nominal')}),flush=True)

import json,time,numpy as np,shutil
from concurrent.futures import ProcessPoolExecutor,as_completed
from hybrid_trial import run
from control_core import ROOT

def one(v):
    i,c=v
    try:r,_=run(c,False);return {'id':i,'result':r}
    except Exception as e:return {'id':i,'result':{'config':c,'success':False,'error':str(e)}}
if __name__=='__main__':
    base=json.load(open(ROOT/'results/smooth_landing_v1/best_config.json'));base.update(duration=5.,mpc=True)
    cfgs=[]
    for launch in [-.5,-.455,-.41,-.365]:
        for speed in [1.1,1.4,1.7]:
            for extend in [.2,.3,.4]:
                c=dict(base,launch_x=launch,speed=speed,extend_after=extend);cfgs.append((len(cfgs),c))
    folder=ROOT/'results/mpc_jump_v1';folder.mkdir(exist_ok=False);rows=[]
    for name in ['hybrid_trial.py','full_lqr.py','control_core.py','linear_mpc.py','mpc_sweep.py']:shutil.copy2(ROOT/name,folder/name)
    with ProcessPoolExecutor(12) as pool,open(folder/'all_trials.jsonl','w') as f:
        for future in as_completed([pool.submit(one,v) for v in cfgs]):
            row=future.result();rows.append(row);f.write(json.dumps(row)+'\n');f.flush()
    rows.sort(key=lambda r:(r['result'].get('success',False),r['result'].get('stable_time',0)),reverse=True);(folder/'ranked.json').write_text(json.dumps(rows,indent=2));(folder/'best_config.json').write_text(json.dumps(rows[0]['result']['config'],indent=2));print(json.dumps({'complete':True,'successes':sum(r['result'].get('success',False) for r in rows),'trials':len(rows),'best':rows[0]}),flush=True)

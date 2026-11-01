import json,shutil,numpy as np
from concurrent.futures import ProcessPoolExecutor,as_completed
from hybrid_trial import run
from control_core import ROOT

def one(v):
    i,c=v
    try:r,_=run(c,False);return {'id':i,'result':r}
    except Exception as e:return {'id':i,'result':{'config':c,'success':False,'error':str(e)}}
if __name__=='__main__':
    base=json.load(open(ROOT/'results/smooth_landing_v1/best_config.json'));base.update(duration=5.,mpc=True);cfgs=[]
    for mode in ['approach','landing','both']:
        for speed in [1.2,1.4,1.6]:
            for launch in [-.52,-.48,-.44,-.4]:
                for run_speed in [.4,1.,1.6]:
                    c=dict(base,speed=speed,launch_x=launch,mpc_approach=mode!='landing',mpc_landing=mode!='approach',landing_run_speed=run_speed);cfgs.append((len(cfgs),c))
    folder=ROOT/'results/mpc_phases_v2';folder.mkdir(exist_ok=False);rows=[]
    for name in ['hybrid_trial.py','linear_mpc.py','mpc_phases.py']:shutil.copy2(ROOT/name,folder/name)
    with ProcessPoolExecutor(20) as pool,open(folder/'all_trials.jsonl','w') as f:
        for future in as_completed([pool.submit(one,v) for v in cfgs]):
            row=future.result();rows.append(row);f.write(json.dumps(row)+'\n');f.flush()
    rows.sort(key=lambda r:(r['result'].get('success',False),r['result'].get('stable_time',0)),reverse=True);(folder/'ranked.json').write_text(json.dumps(rows,indent=2));(folder/'best_config.json').write_text(json.dumps(rows[0]['result']['config'],indent=2));print(json.dumps({'complete':True,'successes':sum(r['result'].get('success',False) for r in rows),'n':len(rows),'best':rows[0]}),flush=True)

"""Calibrate fixed feedback prediction; DR sampled unchanged, no delay oracle."""
import json,time,shutil
from concurrent.futures import ProcessPoolExecutor,as_completed
from hybrid_trial import run
from control_core import ROOT

def one(v):
    key,cfg=v
    try:r,_=run(cfg,False);return {'id':key,'result':r}
    except Exception as e:return {'id':key,'result':{'config':cfg,'success':False,'error':repr(e)}}
if __name__=='__main__':
    base=json.load(open(ROOT/'results/robust_flight_v1/best_config.json'));base['duration']=5.;folder=ROOT/'results/feedback_prediction_v1';folder.mkdir(exist_ok=False)
    for name in ['hybrid_trial.py','full_lqr.py','control_core.py','dr_components.py','linear_mpc.py','prediction_validation.py']:shutil.copy2(ROOT/name,folder/name)
    configs=[]
    for mode in [False,True]:
        for prediction in [0.,.005,.01]:
            configs.append((f'nominal_{mode}_{prediction}',dict(base,full_dr=False,mpc=mode,feedback_predict_s=prediction)))
            for seed in range(1000,1016):configs.append((f'{mode}_{prediction}_{seed}',dict(base,full_dr=True,mpc=mode,feedback_predict_s=prediction,seed=seed)))
    rows=[];start=time.time()
    with ProcessPoolExecutor(24) as pool,open(folder/'all_trials.jsonl','w') as f:
        for fut in as_completed([pool.submit(one,v) for v in configs]):
            row=fut.result();rows.append(row);f.write(json.dumps(row)+'\n');f.flush()
    groups=[]
    for mode in [False,True]:
        for prediction in [0.,.005,.01]:
            rr=[r['result'] for r in rows if r['result']['config']['full_dr'] and r['result']['config']['mpc']==mode and r['result']['config']['feedback_predict_s']==prediction]
            groups.append({'mpc':mode,'prediction_s':prediction,'n':len(rr),'ever_success':sum(r.get('success',False) for r in rr),'end_success':sum(r.get('success',False) and r.get('stop_reason')=='complete' and r.get('stable_at_end',0)>=.5 for r in rr),'health':sum(r.get('stop_reason')=='health' for r in rr),'cross_first':sum(bool(r.get('cross') and r['cross']['flight_id']==1) for r in rr)})
    result={'groups':groups,'nominal':[r for r in rows if r['id'].startswith('nominal')],'rows':rows,'wall_s':time.time()-start};(folder/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({'complete':True,'groups':groups,'nominal':[(r['id'],r['result'].get('success'),r['result'].get('stable_at_end')) for r in result['nominal']],'seconds':result['wall_s']}),flush=True)

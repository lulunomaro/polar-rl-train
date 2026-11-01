"""Broad forward-impulse parameter sweep; preserves every complete physical result."""
import json,time,numpy as np,shutil
from concurrent.futures import ProcessPoolExecutor,as_completed
from hybrid_trial import run
from control_core import ROOT

def one(item):
    i,cfg=item
    try:
        r,_=run(cfg,False);ap=r['apex'];x=float(np.min(np.array(ap['wheels'])[:,0]));score=10*min(r['max_wheel_bottom'],.4)+6*min(x,.6)+2*ap['upright']+15*bool(r['cross'])+30*r['landed_top']+100*r['success']+8*r['stable_time']-4*(r['stop_reason']=='health')
        return {'id':i,'score':score,'result':r}
    except Exception as e:return {'id':i,'score':-100,'result':{'config':cfg,'error':str(e)}}
if __name__=='__main__':
    base={'step':True,'duration':3.,'start_x':-.7,'speed':1.2,'push_at':.6,'push_delta':.38,'tuck_delta':-1.,'tuck_hip':.1,'push_kp':350,'push_kd':3,'push_pitch':25,'push_pitch_d':4,'wheel_push':3,'air_pitch':35,'air_pitch_d':6,'extend_after':.3,'air_kp':100,'air_kd':3}
    cfgs=[]
    for delta in [-.2,-.35,-.5]:
        for hip_shift in [-.6,-.3,0.,.3,.6]:
            for duration in [.07,.1,.14,.18]:
                for wheel in [-3,0,3,5.5]:
                    c=dict(base,start_delta=delta,hip_shift=hip_shift,push_for=duration,wheel_push=wheel);cfgs.append((len(cfgs),c))
    folder=ROOT/'results/forward_impulse_v1';folder.mkdir(exist_ok=False);rows=[];start=time.time()
    for name in ['hybrid_trial.py','control_core.py','full_lqr.py','forward_sweep.py']:shutil.copy2(ROOT/name,folder/name)
    with ProcessPoolExecutor(20) as pool,open(folder/'all_trials.jsonl','w') as f:
        for fut in as_completed([pool.submit(one,v) for v in cfgs]):
            row=fut.result();rows.append(row);f.write(json.dumps(row)+'\n');f.flush()
            if len(rows)%60==0:
                best=max(rows,key=lambda v:v['score']);r=best['result'];print(json.dumps({'done':len(rows),'score':best['score'],'height':r.get('max_wheel_bottom'),'apex':r.get('apex'),'cross':r.get('cross'),'top':r.get('landed_top'),'success':r.get('success'),'config':r['config'],'seconds':time.time()-start}),flush=True)
    rows.sort(key=lambda v:v['score'],reverse=True);(folder/'ranked.json').write_text(json.dumps(rows,indent=2));(folder/'best_config.json').write_text(json.dumps(rows[0]['result']['config'],indent=2));print(json.dumps({'complete':True,'best':rows[0]}),flush=True)

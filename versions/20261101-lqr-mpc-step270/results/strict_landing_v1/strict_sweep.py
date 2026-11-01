import json,time,numpy as np,shutil
from concurrent.futures import ProcessPoolExecutor,as_completed
from hybrid_trial import run
from control_core import ROOT

def one(v):
    i,c=v
    try:
        r,_=run(c,False);score=100*r['success']+30*(r['cross'] is not None and r['cross']['flight_id']==1)+20*r['stable_time']+min(r['top_contact_controls'],200)*.03+.2*r['last']['xyz'][0]-.01*r['nonwheel_contact_controls']
        return {'id':i,'score':score,'result':r}
    except Exception as e:return {'id':i,'score':-100,'result':{'config':c,'error':str(e)}}
if __name__=='__main__':
    base=json.load(open(ROOT/'results/landing_sweep_v1/best_config.json'));base['duration']=4.;cfgs=[]
    for dx in [-.05,0,.05,.1,.15]:
        for speed in [1.2,1.4,1.6,1.8]:
            for extend in [.12,.18,.24,.3]:
                cfg=dict(base,start_x=base['start_x']+dx,speed=speed,extend_after=extend);cfgs.append((len(cfgs),cfg))
    folder=ROOT/'results/strict_landing_v1';folder.mkdir(exist_ok=False);rows=[];start=time.time()
    for name in ['hybrid_trial.py','full_lqr.py','control_core.py','strict_sweep.py']:shutil.copy2(ROOT/name,folder/name)
    with ProcessPoolExecutor(20) as pool,open(folder/'all_trials.jsonl','w') as f:
        for fut in as_completed([pool.submit(one,c) for c in cfgs]):
            row=fut.result();rows.append(row);f.write(json.dumps(row)+'\n');f.flush()
            if len(rows)%40==0:
                b=max(rows,key=lambda x:x['score']);r=b['result'];print(json.dumps({'done':len(rows),'best_score':b['score'],'success':r.get('success'),'cross':r.get('cross'),'stable':r.get('stable_time'),'config':r['config'],'seconds':time.time()-start}),flush=True)
    rows.sort(key=lambda r:r['score'],reverse=True);(folder/'ranked.json').write_text(json.dumps(rows,indent=2));(folder/'best_config.json').write_text(json.dumps(rows[0]['result']['config'],indent=2));print(json.dumps({'complete':True,'best':rows[0]}),flush=True)

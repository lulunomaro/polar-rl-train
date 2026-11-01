import json,time,numpy as np,shutil
from concurrent.futures import ProcessPoolExecutor,as_completed
from hybrid_trial import run
from control_core import ROOT

def one(item):
    i,cfg=item
    try:
        r,_=run(cfg,False);score=15*bool(r['cross'])+25*r['landed_top']+min(r['top_contact_controls'],100)*.08+100*r['success']+20*r['stable_time']-.05*r['nonwheel_contact_controls']
        if r['last']['xyz'][0]>.1 and r['last']['wheel_xyz'][0][2]>.3:score+=10
        return {'id':i,'score':score,'result':r}
    except Exception as e:return {'id':i,'score':-100,'result':{'config':cfg,'error':str(e)}}
if __name__=='__main__':
    base=json.load(open(ROOT/'results/hybrid_position_v1/best_config.json'));base['duration']=4.;cfgs=[]
    for landing in [-.1,-.25,-.4,-.55,-.75]:
        for extend in [.08,.14,.2,.26,.32]:
            for capture in [.15,.4,.8]:
                for speed in [0.,.5]:
                    c=dict(base,landing_delta=landing,extend_after=extend,capture_time=capture,landing_speed=speed,landing_min_x=.45);cfgs.append((len(cfgs),c))
    folder=ROOT/'results/landing_sweep_v1';folder.mkdir(exist_ok=False);rows=[];start=time.time()
    for name in ['hybrid_trial.py','control_core.py','full_lqr.py','landing_sweep.py']:shutil.copy2(ROOT/name,folder/name)
    with ProcessPoolExecutor(20) as pool,open(folder/'all_trials.jsonl','w') as f:
        for future in as_completed([pool.submit(one,v) for v in cfgs]):
            row=future.result();rows.append(row);f.write(json.dumps(row)+'\n');f.flush()
            if len(rows)%60==0:
                b=max(rows,key=lambda r:r['score']);r=b['result'];print(json.dumps({'done':len(rows),'score':b['score'],'top_controls':r.get('top_contact_controls'),'stable':r.get('stable_time'),'success':r.get('success'),'last':r.get('last'),'config':r['config'],'seconds':time.time()-start}),flush=True)
    rows.sort(key=lambda r:r['score'],reverse=True);(folder/'ranked.json').write_text(json.dumps(rows,indent=2));(folder/'best_config.json').write_text(json.dumps(rows[0]['result']['config'],indent=2));print(json.dumps({'complete':True,'best':rows[0]}),flush=True)

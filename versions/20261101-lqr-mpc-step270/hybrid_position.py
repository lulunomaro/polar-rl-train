import json,time,numpy as np
from concurrent.futures import ProcessPoolExecutor,as_completed
from hybrid_trial import run
from control_core import ROOT
base=json.load(open(ROOT/'results/hybrid_step_v1/best_config.json'));base['duration']=3.
cfgs=[]
for start in [-.8,-.65,-.5,-.4,-.3]:
    for speed in [.5,.8,1.1,1.4,1.8]:
        for at in [.35,.5,.65,.8,1.]:
            cfg=dict(base,start_x=start,speed=speed,push_at=at);cfgs.append((len(cfgs),cfg))
def one(v):
    i,c=v
    try:
        r,_=run(c,False);x=float(np.min(np.array(r['apex']['wheels'])[:,0]));score=12*min(r['max_wheel_bottom'],.4)+4*min(x,.5)+3*r['apex']['upright']+15*bool(r['cross'])+20*r['landed_top']+100*r['success']+8*r['stable_time']-4*(r['stop_reason']=='health')
        return {'id':i,'score':score,'result':r}
    except Exception as e:return {'id':i,'score':-100,'result':{'config':c,'error':str(e)}}
if __name__=='__main__':
    folder=ROOT/'results/hybrid_position_v1';folder.mkdir(exist_ok=False);rows=[];start=time.time()
    with ProcessPoolExecutor(16) as pool,open(folder/'all_trials.jsonl','w') as f:
        for fut in as_completed([pool.submit(one,v) for v in cfgs]):
            r=fut.result();rows.append(r);f.write(json.dumps(r)+'\n');f.flush()
    rows.sort(key=lambda r:r['score'],reverse=True);(folder/'ranked.json').write_text(json.dumps(rows,indent=2));(folder/'best_config.json').write_text(json.dumps(rows[0]['result']['config'],indent=2));print(json.dumps({'complete':True,'trials':len(rows),'best':rows[0],'seconds':time.time()-start}),flush=True)

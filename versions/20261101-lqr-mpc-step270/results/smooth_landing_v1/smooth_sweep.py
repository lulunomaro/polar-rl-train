import json,time,numpy as np,shutil
from concurrent.futures import ProcessPoolExecutor,as_completed
from hybrid_trial import run
from control_core import ROOT

def one(v):
    i,c=v
    try:
        r,_=run(c,False);score=100*r['success']+10*r['stable_time']+10*bool(r['cross'])+5*r['landed_top']-10*r.get('edge_return_after_cross',False)-10*r.get('returned_ground_after_cross',False)
        return {'id':i,'score':score,'result':r}
    except Exception as e:return {'id':i,'score':-100,'result':{'config':c,'success':False,'error':str(e)}}
if __name__=='__main__':
    base=json.load(open(ROOT/'results/strict_landing_v1/best_config.json'));base['duration']=5.;cfgs=[]
    for landing in [-.2,-.4,-.55,-.7]:
        for blend in [.1,.25,.5]:
            for velocity in [.4,.8,1.2]:
                for runtime in [.2,.4,.6]:
                    c=dict(base,smooth_landing=True,landing_delta=landing,landing_blend_s=blend,landing_run_speed=velocity,landing_run_s=runtime);cfgs.append((len(cfgs),c))
    folder=ROOT/'results/smooth_landing_v1';folder.mkdir(exist_ok=False);rows=[];start=time.time()
    for name in ['hybrid_trial.py','full_lqr.py','control_core.py','smooth_sweep.py']:shutil.copy2(ROOT/name,folder/name)
    with ProcessPoolExecutor(20) as pool,open(folder/'all_trials.jsonl','w') as f:
        for future in as_completed([pool.submit(one,v) for v in cfgs]):
            r=future.result();rows.append(r);f.write(json.dumps(r)+'\n');f.flush()
            if len(rows)%36==0:
                b=max(rows,key=lambda v:v['score']);print(json.dumps({'done':len(rows),'best':b,'seconds':time.time()-start}),flush=True)
    rows.sort(key=lambda r:r['score'],reverse=True);(folder/'ranked.json').write_text(json.dumps(rows,indent=2));(folder/'best_config.json').write_text(json.dumps(rows[0]['result']['config'],indent=2));print(json.dumps({'complete':True,'best':rows[0]}),flush=True)

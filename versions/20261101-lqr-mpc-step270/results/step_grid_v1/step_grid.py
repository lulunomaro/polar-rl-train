import argparse,json,shutil,time,numpy as np
from concurrent.futures import ProcessPoolExecutor,as_completed
from jump_trial import run
from control_core import ROOT

def one(item):
    idx,cfg=item
    try:
        r,rows=run(cfg,False)
        apex=np.array(r.get('apex_wheels',[[-3,0,0],[-3,0,0]]));x=float(apex[:,0].min());h=r['max_wheel_bottom'];last=r['last']
        score=8*h+min(x,.5)*2+10*r['landed_top']+30*r['success']+3*r['stable_time']
        if r.get('stop_reason')=='health':score-=1
        return {'id':idx,'score':score,'result':r}
    except Exception as e:return {'id':idx,'score':-100,'result':{'config':cfg,'error':str(e)}}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',default='cem_flat_v2');ap.add_argument('--out',default='step_grid_v1');ap.add_argument('--workers',type=int,default=16);args=ap.parse_args()
    base=json.load(open(ROOT/'results'/args.source/'best_config.json'));base['step']=True;base['duration']=3.
    rng=np.random.default_rng(20261102);cfgs=[]
    for x in np.linspace(-.7,-.25,10):
        for speed in [.4,.8,1.2,1.6]:
            for push in [.3,.45,.6]:
                cfg=dict(base,start_x=float(x),speed=speed,push_at=push);cfgs.append((len(cfgs),cfg))
    folder=ROOT/'results'/args.out;folder.mkdir(exist_ok=False)
    for fn in ['control_core.py','jump_trial.py','step_grid.py']:shutil.copy2(ROOT/fn,folder/fn)
    rows=[];start=time.time()
    with ProcessPoolExecutor(args.workers) as pool,open(folder/'all_trials.jsonl','w') as f:
        for future in as_completed([pool.submit(one,v) for v in cfgs]):
            row=future.result();rows.append(row);f.write(json.dumps(row)+'\n');f.flush()
            if len(rows)%24==0:
                best=max(rows,key=lambda r:r['score']);print(json.dumps({'done':len(rows),'best':best,'seconds':time.time()-start}),flush=True)
    rows.sort(key=lambda r:r['score'],reverse=True);(folder/'ranked.json').write_text(json.dumps(rows,indent=2));(folder/'best_config.json').write_text(json.dumps(rows[0]['result']['config'],indent=2));print(json.dumps({'complete':True,'best':rows[0]}),flush=True)

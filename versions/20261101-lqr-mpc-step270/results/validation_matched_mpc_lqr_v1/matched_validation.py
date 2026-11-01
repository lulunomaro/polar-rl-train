"""Compare the same frozen robust policy with LQR/MPC on held-out full-DR seeds."""
import argparse,json,shutil,time
from concurrent.futures import ProcessPoolExecutor,as_completed
from hybrid_trial import run
from control_core import ROOT

def one(item):
    key,cfg=item
    try:r,_=run(cfg,False);return {'id':key,'result':r}
    except Exception as exc:return {'id':key,'result':{'config':cfg,'success':False,'error':repr(exc)}}
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--n',type=int,default=64);a.add_argument('--seed',type=int,default=4000);a.add_argument('--out',default='validation_matched_mpc_lqr_v1');args=a.parse_args()
    base=json.load(open(ROOT/'results/robust_flight_v1/best_config.json'));base['duration']=5.
    folder=ROOT/'results'/args.out;folder.mkdir(exist_ok=False)
    for name in ['hybrid_trial.py','control_core.py','full_lqr.py','linear_mpc.py','dr_components.py','matched_validation.py']:shutil.copy2(ROOT/name,folder/name)
    configs=[]
    for mpc in [False,True]:
        configs.append((f'nominal_{mpc}',dict(base,full_dr=False,mpc=mpc)))
        configs += [(f'{mpc}_{i}',dict(base,full_dr=True,mpc=mpc,seed=args.seed+i)) for i in range(args.n)]
    rows=[];start=time.time()
    with ProcessPoolExecutor(24) as pool,open(folder/'all_trials.jsonl','w') as f:
        for fut in as_completed([pool.submit(one,v) for v in configs]):
            row=fut.result();rows.append(row);f.write(json.dumps(row)+'\n');f.flush()
            if len(rows)%32==0:print(json.dumps({'done':len(rows),'total':len(configs),'seconds':time.time()-start}),flush=True)
    groups={}
    for mode in [False,True]:
        group=[r['result'] for r in rows if r['result']['config'].get('full_dr') and r['result']['config'].get('mpc',False)==mode]
        groups[str(mode)]={'n':len(group),'success':sum(r.get('success',False) for r in group),'cross_first':sum(bool(r.get('cross') and r['cross']['flight_id']==1) for r in group),'health':sum(r.get('stop_reason')=='health' for r in group),'completed_success':sum(r.get('success',False) and r.get('stop_reason')=='complete' and r.get('stable_at_end',0)>=.5 for r in group)}
    summary={'groups':groups,'seed_start':args.seed,'seed_count':args.n,'nominal':[r for r in rows if r['id'].startswith('nominal')],'rows':rows,'wall_s':time.time()-start}
    (folder/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps({'complete':True,'groups':groups,'wall_s':summary['wall_s']}),flush=True)

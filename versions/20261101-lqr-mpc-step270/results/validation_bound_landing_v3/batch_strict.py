"""DR seed evaluation of strict candidate, plus source snapshots."""
import argparse,json,time,shutil,numpy as np
from concurrent.futures import ProcessPoolExecutor,as_completed
from hybrid_trial import run
from control_core import ROOT

def one(v):
    i,c=v
    try:r,_=run(c,False);return {'id':i,'result':r}
    except Exception as e:return {'id':i,'result':{'config':c,'success':False,'error':str(e)}}
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--source',default='strict_landing_v1');a.add_argument('--out',default='validation_strict_v3');a.add_argument('--n',type=int,default=32);a.add_argument('--seed',type=int,default=1000);args=a.parse_args()
    base=json.load(open(ROOT/'results'/args.source/'best_config.json'));base['duration']=5.;folder=ROOT/'results'/args.out;folder.mkdir(exist_ok=False)
    cfgs=[(-1,dict(base,full_dr=False)),(-2,dict(base,full_dr=False,mpc=True))]+[(i,dict(base,full_dr=True,seed=args.seed+i)) for i in range(args.n)]
    for name in ['control_core.py','full_lqr.py','hybrid_trial.py','dr_components.py','linear_mpc.py','batch_strict.py']:shutil.copy2(ROOT/name,folder/name)
    rows=[]
    with ProcessPoolExecutor(16) as pool,open(folder/'all_trials.jsonl','w') as f:
        for fut in as_completed([pool.submit(one,v) for v in cfgs]):
            r=fut.result();rows.append(r);f.write(json.dumps(r)+'\n');f.flush();v=r['result'];print(json.dumps({'id':r['id'],'success':v.get('success'),'cross':v.get('cross'),'stable':v.get('stable_time'),'nonwheel':v.get('nonwheel_contact_controls'),'stop':v.get('stop_reason'),'error':v.get('error')}),flush=True)
    dr=[r for r in rows if r['id']>=0];summary={'fullDR_success':sum(r['result'].get('success',False) for r in dr),'fullDR_n':len(dr),'nominal':[r for r in rows if r['id']<0],'rows':rows};(folder/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps({k:v for k,v in summary.items() if k!='rows'}),flush=True)

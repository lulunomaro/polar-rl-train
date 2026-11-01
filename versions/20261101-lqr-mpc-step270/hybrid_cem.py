"""CUDA cross-entropy search for hybrid traditional controller parameters."""
import argparse,json,time,shutil,numpy as np,torch
from concurrent.futures import ProcessPoolExecutor
from hybrid_trial import run
from control_core import ROOT
NAMES=['start_delta','hip_shift','push_for','push_delta','tuck_delta','tuck_hip','push_kp','push_kd','push_pitch','push_pitch_d','wheel_push','speed','air_pitch','air_pitch_d','air_wheel','push_at','extend_after','air_kp','air_kd']
LOW=[-.55,-.8,.055,.12,-1.03,-.25,120,.5,0,1,-4,.2,5,1,-2,.25,.12,30,1]
HIGH=[-.15,-.1,.22,.41,-.5,.49,500,6,50,8,5.7,1.8,65,12,2,1.,.45,160,6]

def one(item):
    idx,params,base=item;cfg=dict(base);cfg.update(zip(NAMES,map(float,params)))
    try:
        r,_=run(cfg,False);apex=r['apex'];height=r['max_wheel_bottom'];x=float(np.min(np.array(apex['wheels'])[:,0]));upr=apex['upright']
        if cfg['step']:
            score=12*min(height,.4)+4*min(x,.5)+3*upr+15*bool(r['cross'])+20*r['landed_top']+100*r['success']+8*r['stable_time']
        else:score=12*min(height,.5)+3*upr-abs(apex['state'][5])*.1
        if r['stop_reason']=='health':score-=4
        return {'id':idx,'score':float(score),'result':r,'parameters':list(map(float,params))}
    except Exception as e:return {'id':idx,'score':-100,'result':{'config':cfg,'error':str(e)},'parameters':list(map(float,params))}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--n',type=int,default=128);ap.add_argument('--generations',type=int,default=6);ap.add_argument('--workers',type=int,default=16);ap.add_argument('--out',default='hybrid_cem_v1');ap.add_argument('--step',action='store_true');ap.add_argument('--start-x',type=float,default=-.4);ap.add_argument('--seed-config');ap.add_argument('--full-dr',action='store_true');args=ap.parse_args()
    torch.set_num_threads(1);torch.manual_seed(20261103);lo=torch.tensor(LOW,device='cuda');hi=torch.tensor(HIGH,device='cuda');mu=(lo+hi)/2;sd=(hi-lo)/3
    if args.seed_config:
        cfg=json.load(open(args.seed_config));mu=torch.tensor([cfg.get(k,float(mu[i])) for i,k in enumerate(NAMES)],device='cuda');sd=(hi-lo)/6
    base={'step':args.step,'duration':3.,'start_x':args.start_x,'full_dr':args.full_dr,'seed':20261101}
    folder=ROOT/'results'/args.out;folder.mkdir(exist_ok=False)
    for name in ['control_core.py','full_lqr.py','hybrid_trial.py','hybrid_cem.py','dr_components.py']:shutil.copy2(ROOT/name,folder/name)
    rows=[];start=time.time()
    with ProcessPoolExecutor(args.workers) as pool,open(folder/'all_trials.jsonl','w') as f:
        for gen in range(args.generations):
            pop=torch.clamp(mu+sd*torch.randn(args.n,len(NAMES),device='cuda'),lo,hi);pop[0]=mu
            results=list(pool.map(one,[(gen*args.n+i,v,base) for i,v in enumerate(pop.cpu().numpy())]));scores=torch.tensor([r['score'] for r in results],device='cuda');ids=torch.topk(scores,max(8,args.n//8)).indices;elite=pop[ids]
            mu=.2*mu+.8*elite.mean(0);sd=torch.maximum(.2*sd+.8*elite.std(0),.025*(hi-lo))
            for r in results:f.write(json.dumps(r)+'\n')
            f.flush();rows+=results;best=max(rows,key=lambda r:r['score']);(folder/'best.json').write_text(json.dumps(best,indent=2));(folder/'best_config.json').write_text(json.dumps(best['result']['config'],indent=2))
            r=best['result'];print(json.dumps({'gen':gen,'trials':len(rows),'seconds':time.time()-start,'score':best['score'],'height':r.get('max_wheel_bottom'),'landed_top':r.get('landed_top'),'cross':r.get('cross'),'success':r.get('success'),'apex':r.get('apex'),'config':r['config']}),flush=True)
    print(json.dumps({'complete':True,'trials':len(rows),'best':best}),flush=True)

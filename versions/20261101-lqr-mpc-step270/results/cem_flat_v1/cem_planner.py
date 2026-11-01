"""CUDA CEM parameter planner evaluated against the complete MuJoCo contact plant."""
import argparse,json,time,hashlib,shutil
from concurrent.futures import ProcessPoolExecutor
import numpy as np,torch
from control_core import ROOT
from jump_trial import run
NAMES=['start_delta','hip_shift','push_for','push_delta','tuck_delta','tuck_hip','push_kp','push_kd','pitch_gain','air_pitch','wheel_push','speed','air_wheel','push_at']
LOW=[-.6,-.8,.045,.2,-1.06,-.1,150,.5,-15,-20,-4,0,-2,.3]
HIGH=[-.05,-.15,.23,.43,-.6,.49,600,7,25,25,4,1.6,2,.8]

def evaluate(item):
    idx,params,base=item;cfg=dict(base);cfg.update(zip(NAMES,map(float,params)))
    try:
        r,_=run(cfg,False)
        height=r['max_wheel_bottom'];pitch=r.get('apex_state',[0,0])[1];upright=r.get('apex_upright',0)
        if cfg.get('step',False):
            wheels=np.array(r.get('apex_wheels',[[-2,0,0],[-2,0,0]]));x=float(wheels[:,0].min());
            score=height*8+2*min(x,.4)+2*r.get('stable_time',0)+5*float(r['landed_top'])+20*float(r['success'])
        else:score=height*12+min(r['air_time'],.5)-.2*abs(pitch)+.5*upright
        if r.get('stop_reason')=='health':score-=1
        return {'id':idx,'score':score,'parameters':list(params),'result':r}
    except Exception as e:return {'id':idx,'score':-100,'parameters':list(params),'result':{'error':str(e),'config':cfg}}
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--n',type=int,default=128);a.add_argument('--generations',type=int,default=6);a.add_argument('--workers',type=int,default=16);a.add_argument('--out',default='cem_flat_v1');a.add_argument('--step',action='store_true');a.add_argument('--start-x',type=float,default=-.65);a.add_argument('--seed-config');args=a.parse_args()
    torch.set_num_threads(1);device='cuda';torch.manual_seed(20261101)
    lo=torch.tensor(LOW,device=device);hi=torch.tensor(HIGH,device=device);mu=(lo+hi)/2;sd=(hi-lo)/3
    if args.seed_config:
        cfg=json.load(open(args.seed_config));mu=torch.tensor([cfg.get(k,float(mu[i])) for i,k in enumerate(NAMES)],device=device);sd=(hi-lo)/6
    base={'step':args.step,'duration':2.,'start_x':args.start_x}
    folder=ROOT/'results'/args.out;folder.mkdir(exist_ok=False)
    for fn in ['control_core.py','jump_trial.py','cem_planner.py']:shutil.copy2(ROOT/fn,folder/fn)
    (folder/'spec.json').write_text(json.dumps({'names':NAMES,'low':LOW,'high':HIGH,'args':vars(args),'gpu':torch.cuda.get_device_name(0),'method':'CEM parameter optimization with full MuJoCo contact rollouts','no_RL':True},indent=2))
    rows=[];best=None;start=time.time()
    with ProcessPoolExecutor(args.workers) as pool,open(folder/'all_trials.jsonl','w') as f:
        for gen in range(args.generations):
            pop=torch.clamp(mu+sd*torch.randn(args.n,len(NAMES),device=device),lo,hi);pop[0]=mu
            cpu=pop.cpu().numpy();results=list(pool.map(evaluate,[(gen*args.n+i,p,base) for i,p in enumerate(cpu)]))
            scores=torch.tensor([r['score'] for r in results],device=device);elite=torch.topk(scores,max(8,args.n//8)).indices
            elitepop=pop[elite];mu=.3*mu+.7*elitepop.mean(0);sd=torch.maximum(.3*sd+.7*elitepop.std(0),.025*(hi-lo))
            for r in results:f.write(json.dumps(r)+'\n')
            f.flush();rows.extend(results);best=max(rows,key=lambda r:r['score'])
            (folder/'best.json').write_text(json.dumps(best,indent=2));(folder/'best_config.json').write_text(json.dumps(best['result']['config'],indent=2))
            print(json.dumps({'generation':gen,'trials':len(rows),'seconds':time.time()-start,'best_score':best['score'],'height':best['result'].get('max_wheel_bottom'),'apex_wheels':best['result'].get('apex_wheels'),'success':best['result'].get('success'),'best_cfg':best['result'].get('config')}),flush=True)
    print(json.dumps({'complete':True,'trials':len(rows),'seconds':time.time()-start,'best':best}),flush=True)

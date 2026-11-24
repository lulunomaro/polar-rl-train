"""Bounded 400 Hz closed-loop policy-weight calibration with no runtime teacher."""
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from pathlib import Path
import json
import numpy as np
import torch
from fsm_paths import HERE
from fsm_io import put,sha256
from manual_fsm_model import ResidualStair
from fsm_evaluation import run_case

def worker(task):
    checkpoint,case=task
    row,trace=run_case(case,checkpoint=checkpoint)
    score=(100.*row['passed']+min(row['longest_bilateral_support_substeps'][-1],400)/4.
        +15.*row['physical_crossed']+30.*(row['failure'] is None)-.2*row['peak_abs_pitch_deg']
        -10.*row['max_rollback_m']-100.*bool(row['precontact_active_samples']))
    return float(score),row

def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint',type=Path,default=HERE/'evidence/fsm_r2/train/model_final.pt')
    p.add_argument('--generations',type=int,default=10)
    p.add_argument('--population',type=int,default=12)
    p.add_argument('--workers',type=int,default=2)
    args=p.parse_args();torch.set_num_threads(1)
    tag='cem_bridge_'+datetime.now().strftime('%Y%m%d_%H%M%S')
    folder=HERE/'evidence'/tag;folder.mkdir()
    parent=torch.load(args.checkpoint,map_location='cpu',weights_only=False)
    model=ResidualStair();model.base.load_state_dict(parent['stair'])
    model.eval()
    cases=[]
    for i,(course,speed,x) in enumerate((('step_20',1.1,.185),('step_20',1.8,.215))):
        cases.append(dict(id=f'cem_training_{i}',course=course,speed=speed,height=.39,yaw_deg=0.,offset=[x,0.],
            seconds=6.,settle_s=.8,wz=0.,task='',edge_sign=1,armed=True))
    rng=np.random.default_rng(11222026)
    mean=np.zeros(12)
    sigma=np.array([.08,.15,.15,.20,.45,.10,.15,.10,.15,.6,.4,.25])
    best_score=-1.e9;best=None;log=[]
    with ProcessPoolExecutor(args.workers) as pool:
        for generation in range(args.generations):
            population=rng.normal(mean,sigma,(args.population,12))
            population[0]=mean
            if best is not None:population[1]=best
            population=np.clip(population,-3.,3.)
            paths=[]
            for i,theta in enumerate(population):
                model.set_coordinates(theta)
                path=folder/f'policy_{generation:03d}_{i:03d}.pt'
                torch.save(dict(format='mod4v3_manual_fsm_stair_v1',architecture='cnn12_obs_linear_residual',
                    stair=model.state_dict(),parent_sha256=sha256(args.checkpoint),coordinates=theta.tolist(),
                    ppo_updates=parent.get('ppo_updates',0),optimizer_steps=parent.get('optimizer_steps',0),
                    cpu_evolution_generation=generation),path)
                paths.append(path)
            tasks=[(path,case) for path in paths for case in cases]
            outcomes=list(pool.map(worker,tasks))
            scores=np.array([np.mean([x[0] for x in outcomes[i*len(cases):(i+1)*len(cases)]])
                             -.1*np.linalg.norm(population[i]) for i in range(args.population)])
            elite=np.argsort(scores)[-max(3,args.population//4):]
            winner=int(np.argmax(scores))
            if scores[winner]>best_score:
                best_score=float(scores[winner]);best=population[winner].copy()
                best_path=paths[winner]
                put(folder/'BEST.json',dict(checkpoint=str(best_path.relative_to(HERE)),sha256=sha256(best_path),
                    score=best_score,coordinates=best.tolist(),generation=generation,
                    cases=[row for _,row in outcomes[winner*len(cases):(winner+1)*len(cases)]]))
            mean=.35*mean+.65*population[elite].mean(0)
            sigma=np.maximum(.04,.35*sigma+.65*population[elite].std(0))
            entry=dict(generation=generation,best_score=best_score,population_scores=scores.tolist(),
                strict_successes=[sum(row['passed'] for _,row in outcomes[i*len(cases):(i+1)*len(cases)]) for i in range(args.population)],
                coordinates=best.tolist(),mean=mean.tolist(),sigma=sigma.tolist())
            log.append(entry);put(folder/'SEARCH.json',dict(parent_sha256=sha256(args.checkpoint),
                training_cases=cases,iterations=log,strict_holdout_evaluation_pending=True))
            print(tag,generation,'best',round(best_score,3),'strict',entry['strict_successes'],flush=True)
    print('BEST',best_path,sha256(best_path),flush=True)

if __name__=='__main__':main()

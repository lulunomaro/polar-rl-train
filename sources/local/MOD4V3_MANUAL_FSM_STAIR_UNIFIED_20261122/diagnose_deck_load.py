"""Compare independent signed wheel loads with scoring at every physical step."""
from argparse import ArgumentParser
import json
import numpy as np
import mujoco as mj
from fsm_paths import HERE
from fsm_io import put
from fsm_evaluation import run_case

def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint',default='evidence/fsm_r2/train/model_final.pt')
    p.add_argument('--deck-height',type=float,default=.35)
    p.add_argument('--out',default='DECK_LOAD_SUBSTEPS')
    args=p.parse_args()
    records=[];buffer=np.zeros(6)
    def capture(sim,judge):
        main=np.zeros(2);total=np.zeros(2);guide=0.;structure=0.;contacts=[]
        for i in range(sim.d.ncon):
            c=sim.d.contact[i];a,b=map(int,c.geom)
            if a in judge.terrain:robot=b;sign=1.
            elif b in judge.terrain:robot=a;sign=-1.
            else:continue
            mj.mj_contactForce(sim.m,sim.d,i,buffer)
            force=float(sign*buffer[0]*c.frame[2])
            if robot in judge.tires:
                side=judge.robot_side[robot];main[side]+=force
                total[side]+=(sign*c.frame.reshape(3,3).T@buffer[:3])[2]
                contacts.append(dict(geom_a=sim.m.geom(a).name,geom_b=sim.m.geom(b).name,
                    normal=(sign*c.frame[:3]).tolist(),normal_force=float(buffer[0]),
                    signed_vertical=force,pos=c.pos.tolist(),distance=float(c.dist)))
            elif sim.m.geom(robot).name.startswith('guide_wheel_'):guide+=force
            elif robot in judge._robot_gids:structure+=force
        records.append(dict(t=float(sim.d.time),x=float(sim.d.qpos[0]),z=float(sim.d.qpos[2]),
            tire_bottom_z=(sim.d.geom_xpos[sim.tire_gids,2]-.0625).tolist(),main_n=main.tolist(),guide_n=guide,
            total_n=total.tolist(),scored_n=list(judge.trace[-1][21:23]),
            contacts=contacts if len(records)<32 or not (main>5.).all() else [],
            structure_n=structure,phase=int(sim.unified.fsm.phase[0])))
    c=dict(id='deck_load_diagnosis',course='step_20',speed=1.2,height=.39,yaw_deg=0.,offset=[.2,0.],
           seconds=6.,settle_s=.8,wz=0.,task='',edge_sign=1,armed=True)
    config=json.loads((HERE/'DETECTOR.json').read_text())['config']
    config['deck_height']=args.deck_height
    row,_=run_case(c,checkpoint=args.checkpoint,detector=config,physics_frames=capture)
    late=[r for r in records if r['x']>1.5 and r['phase']==4]
    stats=dict(case=row,samples=records,
        mean_main_load_n=np.mean([r['main_n'] for r in late],axis=0).tolist() if late else None,
        mean_guide_load_n=float(np.mean([r['guide_n'] for r in late])) if late else None,
        mean_structure_load_n=float(np.mean([r['structure_n'] for r in late])) if late else None)
    if late:
        normal=np.array([r['main_n'] for r in late]);scored=np.array([r['scored_n'] for r in late])
        stats.update(late_samples=len(late),late_load_missing_samples=int((normal<=5.).any(1).sum()),
            scored_normal_max_error=float(np.abs(normal-scored).max()),
            normal_quantiles=np.quantile(normal,[0,.1,.5,.9,1],axis=0).tolist())
    put(HERE/'evidence'/(args.out+'.json'),stats)
    print('result',row['passed'],'support',row['longest_bilateral_support_substeps'])
    print(json.dumps({k:v for k,v in stats.items() if k not in ('case','samples')},indent=2))
    print('first 24 loads',[(r['main_n'],r['scored_n']) for r in late[:24]])

if __name__=='__main__':main()

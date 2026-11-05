"""Independent first80 episodes on the actual Newton plant, with saved poses."""
from pathlib import Path
import argparse,hashlib,json,random,time,traceback
import numpy as np
import torch
from .config import runner_config
from .newton_env import NewtonEnv
from .newton_train import put


def triangle_boxes():
    vertices=[];faces=[]
    for lo,hi in [((-3.6,-3.6,-.1),(3.6,3.6,0.)),((.8,-3.5,0.),(3.5,3.5,.2))]:
        start=len(vertices)
        vertices += [[x,y,z]for x in (lo[0],hi[0])for y in (lo[1],hi[1])for z in (lo[2],hi[2])]
        for quad in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]:
            for tri in [(quad[0],quad[1],quad[2]),(quad[0],quad[2],quad[3])]:faces.append([start+i for i in tri])
    return np.asarray(vertices),np.asarray(faces)


def main(actor_loader=None):
    p=argparse.ArgumentParser()
    for key in ('package','components','reset-bank','checkpoint','checkpoint-SHA','job-root'):p.add_argument('--'+key,required=True)
    a=p.parse_args();out=Path(a.job_root);out.mkdir(exist_ok=False);env=None;error=None
    try:
        random.seed(9137);np.random.seed(9137);torch.manual_seed(9137);torch.cuda.manual_seed_all(9137)
        from rsl_rl.runners import OnPolicyRunner
        env=NewtonEnv(a.package,a.components,a.reset_bank,80,'cuda:0',9137)
        if actor_loader is None:
            runner=OnPolicyRunner(env,runner_config(),None,'cuda:0')
            with Path(a.checkpoint).open('rb')as f:assert hashlib.file_digest(f,'sha256').hexdigest()==a.checkpoint_SHA
            saved=torch.load(a.checkpoint,map_location='cpu',weights_only=False)
            assert saved['reward_family']=='FUDAN_JUMP' and saved['actor_dim']==35 and saved['critic_dim']==78
            runner.alg.actor.load_state_dict(saved['actor_state_dict'],strict=True)
            actor=runner.alg.actor;actor.eval().requires_grad_(False);del saved
        else:
            actor=actor_loader(env,a.checkpoint,a.checkpoint_SHA)
        active=torch.ones(80,dtype=torch.bool,device=env.device)
        rows=[None]*80;curves=[];ticks=[];poses=[];record=[0,1,40,41]
        put(out/'NATIVE_STARTUP.json',dict(epoch=time.time(),native=True,actual_Newton_MuJoCo_Warp=True,
            model=env.plant.receipt,seed=9137,optimizer_operations=0,source_SHA=a.checkpoint_SHA,
            saved_pose_quaternion_order='wxyz',physics_hz=400,feedback_hz=100,policy_hz=50))
        def observe(e):
            d,r,s=e.data,e.reward,e.acceptance
            row=dict(tick=np.int32(e.physics_ticks),active=active.cpu().numpy().copy())
            fields=dict(top_force=e.top_force,ground_force=e.ground_force,
                wheel_pos=d.body_pos_w[:,e.wheel_bodies],root_pos=d.root_pos_w,
                root_quat=d.root_quat_w,root_velocity=d.root_lin_vel_w,
                wholeclear=s.wholeclear,leading=s.leading,strict=s.success,flight_id=s.flight_id,
                upward_flight=s.up,landed_top=s.landed_top,
                wheel_contact_force=e.net_force[:,e.wheel_bodies].norm(dim=-1),
                nonwheel_contact_force=e.net_force[:,r._nonwheel_contact_link_idx].norm(dim=-1).amax(-1))
            row.update({k:v.detach().cpu().numpy().copy()for k,v in fields.items()});ticks.append(row)
            if e.physics_ticks%8==0:
                poses.append(dict(tick=np.int32(e.physics_ticks),active=active[record].cpu().numpy().copy(),
                    body_pos=d.body_pos_w[record].cpu().numpy().copy(),body_quat=d.body_quat_w[record].cpu().numpy().copy()))
        env.physics_observer=observe
        with torch.inference_mode():
            obs=env.get_observations()
            for control in range(400):
                action=actor(obs);obs,reward,done,info=env.step(action)
                s=env.terminal_snapshot;ended=(done|((control+1)==400))&active
                for i in ended.nonzero().flatten().tolist():
                    rows[i]={k:v[i].cpu().tolist()for k,v in s.items()}
                    rows[i].update(env=i,controls=control+1,jump200_success=rows[i]['success'],
                        jump200_wholeclear=rows[i]['wholeclear'],jump200_landed_top=rows[i]['landed_top'])
                curves.append(dict(control=control+1,active=active.cpu().tolist(),reward=reward.cpu().tolist(),
                    action=action.cpu().tolist(),
                    **{k:v.cpu().tolist()for k,v in s.items()},
                    weighted_reward_active_mean={k:float(v[active].mean())for k,v in env.reward._last_reward_terms.items()}))
                active &= ~ended
                if not bool(active.any()):break
        def npz(name,values,extra=None):
            path=out/name;data={k:np.stack([r[k]for r in values])for k in values[0]}
            np.savez_compressed(path,**data,**(extra or {}))
            with path.open('rb')as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
            return dict(path=str(path),bytes=path.stat().st_size,SHA=sha)
        vertices,faces=triangle_boxes()
        extra={}
        for i in record:extra['terrain_vertices_'+str(i)]=vertices;extra['terrain_faces_'+str(i)]=faces
        tickfile=npz('actual400hz.npz',ticks);posefile=npz('selected_actual_poses.npz',poses,extra)
        put(out/'ALL80.json',dict(seed=9137,first_episodes=rows))
        put(out/'CONTROL_CURVES.json',dict(curves=curves))
        valid=np.stack([r['active']for r in ticks]);top=np.stack([r['top_force']for r in ticks])
        put(out/'RESULT.json',dict(epoch=time.time(),passed_execution=all(r is not None for r in rows),
            independent_first_episodes=80,seed=9137,actual_physics_hz=400,controls_max=400,
            actual_Newton_MuJoCo_Warp=True,optimizer_operations=0,source_SHA=a.checkpoint_SHA,
            numerical_resets=int(env.numerical_reset_counts.sum()),
            solver_overflow_world_masks=env.solver_overflow_summary(),
            jump200_success=sum(r['success']for r in rows),jump200_wholeclear=sum(r['wholeclear']for r in rows),
            jump200_landed_top=sum(r['landed_top']for r in rows),
            ground_validated_flight=sum(r['flight_id']>0 for r in rows),
            simultaneous_top_force_over1N=int(((top>1).all(-1)&valid).sum()),
            all80_manifold=tickfile,actual_poses=posefile,recorded_envs=record,body_names=env.body_names,
            environment_origins=[[0.,0.,0.]]*80,saved_pose_quaternion_order='wxyz',
            course=dict(kind='MOD4_SINGLE_STEP_JUMP200',near_edge_m=.8,top_height_m=.2,top_end_m=3.5),
            native_pose_visual_review_pending=True))
    except BaseException:
        error=traceback.format_exc();put(out/'ERROR.json',dict(epoch=time.time(),error=error));raise
    finally:
        if env is not None:env.close()
        put(out/'APP_CLOSE_INTENT.json',dict(epoch=time.time(),error=error,env_closed=env is not None))


if __name__=='__main__':main()

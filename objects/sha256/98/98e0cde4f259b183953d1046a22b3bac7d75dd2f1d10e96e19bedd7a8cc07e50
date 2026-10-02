"""Local deterministic USD playback: no PPO, no remote writes, no balance assist."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
parser = argparse.ArgumentParser()
parser.add_argument('--checkpoint', default=str(ROOT/'model_8725.pt'))
parser.add_argument('--seconds', type=float, default=0.)
parser.add_argument('--profile', choices=['interactive','forward_reverse'], default='interactive')
parser.add_argument('--output', default=str(ROOT/'isaac_telemetry.json'))
parser.add_argument('--num_envs', type=int, default=1)
parser.add_argument('--smoke_report', default=str(ROOT/'isaac_local_smoke.json'))
parser.add_argument('--seed', type=int, default=20260927)
for k,v in json.loads((ROOT/'run_manifest.remote.json').read_text())['env'].items():
    if k.startswith('RM_'): os.environ[k]=str(v)
os.environ['RM_MOD4_USD']=str(ROOT/'src_snapshot/robot.usd')
os.environ.pop('RM_RESCUE_DEADLINE',None)
os.environ['ISAACSIM_ACCEPT_EULA']='Y'
os.environ['OMNI_KIT_ACCEPT_EULA']='YES'
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(parser)
args=parser.parse_args()
app=AppLauncher(args).app

import torch
from torch import nn
# One robot uses tiny matrices: large CPU thread pools add substantial latency.
torch.set_num_threads(1)
torch.set_num_interop_threads(1)
import mod4_task as task
from mod4_env import Mod4Env


def atomic(path,data):
    path=Path(path); temp=path.with_suffix('.partial')
    temp.write_text(json.dumps(data,indent=2),encoding='utf8')
    # Windows readers briefly lock the destination. A missed UI frame must not stop physics.
    for _ in range(20):
        try:os.replace(temp,path);return True
        except PermissionError:time.sleep(.002)
    return False


class PlaybackEnv(Mod4Env):
    """Keep the failure pose visible. Only explicit operator resets reset state."""
    permit_reset=True
    _physics_handles_decimation=False  # local 2.x executes the explicit substep loop
    def _reset_idx(self,env_ids):
        if self.permit_reset:super()._reset_idx(env_ids)


@torch.inference_mode()
def main():
    ck=Path(args.checkpoint)
    receipt=json.loads((ROOT/'DOWNLOAD_RECEIPT.json').read_text())
    assert hashlib.sha256(ck.read_bytes()).hexdigest()==receipt['source_checkpoint_sha256']
    torch.manual_seed(args.seed)
    raw=torch.load(ck,map_location='cpu',weights_only=False)
    mlp=nn.Sequential(nn.Linear(35,256),nn.ELU(),nn.Linear(256,128),nn.ELU(),
                      nn.Linear(128,64),nn.ELU(),nn.Linear(64,6))
    mlp.load_state_dict({k.removeprefix('mlp.'):v for k,v in raw['actor_state_dict'].items()if k.startswith('mlp.')},strict=True)
    cfg=task.Mod4EnvCfg();cfg.seed=args.seed;cfg.scene.num_envs=args.num_envs
    cfg.sim.device=args.device
    cfg.observations.policy.enable_corruption=False
    if not args.headless:
        cfg.sim.render_interval=cfg.decimation*3  # rendering only; physics/policy cadence unchanged
    cfg.episode_length_s=3600. if args.seconds<=0 else max(args.seconds+1.,20.)
    cfg.viewer.eye=(1.8,1.8,1.0);cfg.viewer.lookat=(0.,0.,.25)
    env=PlaybackEnv(cfg=cfg);robot=env.scene['robot'];dev=env.device;mlp=mlp.to(dev).eval()
    env.reset();env.permit_reset=False
    term=env.command_manager.get_term('twist')
    command_path=ROOT/'operator_command.json'
    current=0.; target=0.; reset_id=0;paused=False;fault=None
    begin=time.perf_counter();next_tick=begin;last_output=0.;step=0
    trace=[];last=torch.zeros((env.num_envs,6),device=dev)
    previous_delta=last.clone();maxclosure=0.;maxmimic=0.
    print('LOCAL_PLAY_READY '+json.dumps({'checkpoint':ck.name,'iteration':raw['iter'],
        'device':str(dev),'usd_sha256':hashlib.sha256((ROOT/'src_snapshot/robot.usd').read_bytes()).hexdigest(),
        'leg_kp':task.LEG_KP,'leg_kd':task.LEG_KD,'height':.25,'no_exploration':True}),flush=True)
    while app.is_running() and (args.seconds<=0 or step*env.step_dt<args.seconds):
        if args.profile=='interactive':
            try:
                command=json.loads(command_path.read_text())
                if command.get('quit'):break
                target=float(max(-1.5,min(1.5,command.get('vx',0.))))
                paused=bool(command.get('paused',False))
                if int(command.get('reset_id',0))!=reset_id:
                    reset_id=int(command['reset_id']);env.permit_reset=True;env.reset();env.permit_reset=False
                    current=0.;fault=None;last.zero_();previous_delta.zero_();maxclosure=maxmimic=0.
            except (OSError,ValueError):pass
        else:
            t=step*env.step_dt
            target=0. if t<2 or t>=13 else .6 if t<6 else 0. if t<8 else -.6 if t<12 else 0.
        if paused or fault:
            if not args.headless:app.update()
            time.sleep(.01)
            next_tick=time.perf_counter()
            if args.profile!='interactive':break
        else:
            current+=max(-.6*env.step_dt,min(.6*env.step_dt,target-current))
            term.time_left[:]=1e9;term.is_standing_env[:]=False
            if hasattr(term,'is_heading_env'):term.is_heading_env[:]=False
            term.command[:]=0.;term.command[:,0]=current;task.height_cmd(env)[:]=.25
            obs=env.observation_manager.compute(update_history=False)['policy']
            assert obs.shape==(env.num_envs,35)
            action=mlp(obs).clamp(-6,6)
            _,reward,terminated,truncated,extras=env.step(action)
            step+=1
            delta=action-last;d2=delta-previous_delta;last=action.clone();previous_delta=delta.clone()
            closure=float(torch.stack(list(task.closure_errors(env).values())).max())
            mimic=float(torch.stack(list(task.mimic_errors(env).values())).max())
            maxclosure=max(maxclosure,closure);maxmimic=max(maxmimic,mimic)
            tilt=torch.rad2deg(torch.acos((-robot.data.projected_gravity_b[:,2]).clamp(-1,1)))
            if not torch.isfinite(robot.data.joint_pos).all()or not torch.isfinite(action).all():fault='nonfinite'
            elif bool(terminated.any()):fault='termination: '+str(env.termination_manager.active_terms)
            elif closure>.002: fault='closed-loop residual exceeds2mm'
            elif mimic>.01: fault='mimic residual exceeds.01rad'
            data={'engine':'Isaac Lab local PhysX 5.1; compatibility port, not remote version',
                  'checkpoint':ck.name,'iteration':int(raw['iter']),'sim_time_s':step*env.step_dt,
                  'command_vx':current,'target_vx':target,'actual_vx':float(robot.data.root_lin_vel_b[0,0]),
                  'height_m':float(task.root_height_above_ground(env)[0]),'target_height_m':.25,
                  'tilt_deg':float(tilt[0]),'delta':float(delta[0].square().mean().sqrt()),
                  'd2':float(d2[0].square().mean().sqrt()),'closure_mm':closure*1000.,'mimic_rad':mimic,
                  'max_closure_mm':maxclosure*1000.,'max_mimic_rad':maxmimic,
                  'fault':fault,'paused':paused,'root_xyz':robot.data.root_pos_w[0].cpu().tolist(),
                  'finite':fault!='nonfinite','updated_epoch':time.time(),
                  'physics_device':str(dev), 'realtime_ratio':step*env.step_dt/max(.001,time.perf_counter()-begin)}
            force=env.scene.sensors['wheel_contact'].data.net_forces_w[0]
            data['left_wheel_load_n']=float(force[0,2]);data['right_wheel_load_n']=float(force[1,2])
            if hasattr(env,'_integrated_contact'):
                data['contact_integration_enabled']=True
            if args.profile!='interactive':trace.append(data)
            if step%3==0 or fault:
                positions=robot.data.body_pos_w[0].cpu().tolist()
                quaternions=robot.data.body_quat_w[0].cpu().tolist()
                data['body_world_poses']={name:pos+quat for name,pos,quat in zip(robot.body_names,positions,quaternions)}
                atomic(args.output,data)
            if step%100==0:print('PLAY_METRIC '+json.dumps(data),flush=True)
            if not args.headless:
                position=robot.data.root_pos_w[0].cpu().tolist()
                if step%3==0:
                    env.sim.set_camera_view(eye=[position[0]+1.8,position[1]+1.8,1.2],target=position)
            if not args.headless or args.profile=='interactive':
                next_tick+=env.step_dt;time.sleep(max(0.,next_tick-time.perf_counter()))
                if time.perf_counter()-next_tick>1.:next_tick=time.perf_counter()
    if args.profile!='interactive':
        result={'checkpoint':ck.name,'steps':step,'seconds':step*env.step_dt,'fault':fault,
                'max_closure_mm':maxclosure*1000.,'max_mimic_rad':maxmimic,'trace':trace,
                'scope':'local engine/version replay; no official or remote graduation claim'}
        atomic(args.smoke_report,result)
        print('LOCAL_PLAY_FINISHED '+json.dumps({k:v for k,v in result.items()if k!='trace'}),flush=True)
    env.close()


try:main()
except BaseException:
    import traceback
    error=traceback.format_exc()
    print(error,flush=True)
    atomic(ROOT/'isaac_play_failure.json',{'error':error,'epoch':time.time()})
finally:app.close()

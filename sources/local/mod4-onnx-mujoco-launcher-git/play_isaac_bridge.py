"""Local deterministic USD playback: no PPO, no remote writes, no balance assist."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys
import time

ROOT = Path(__file__).resolve().parent
from playback_ipc import CommandReader, atomic_json as atomic, read_json, slew
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--bundle', type=Path, required=True)
parser.add_argument('--checkpoint', type=Path, required=True)
parser.add_argument('--command-file', type=Path, required=True)
parser.add_argument('--session-id', required=True)
parser.add_argument('--seconds', type=float, default=0.)
parser.add_argument('--profile', choices=['interactive','forward_reverse','spin_check'], default='interactive')
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--num_envs', type=int, default=1)
parser.add_argument('--smoke_report', type=Path)
parser.add_argument('--seed', type=int, default=20260927)
bootstrap, _ = parser.parse_known_args()
bundle = bootstrap.bundle.resolve()
sys.path.insert(0, str(bundle/'isaac/mod4'))
manifest = read_json(bundle/'run_manifest.remote.json')
if not isinstance(manifest.get('env'), dict):raise ValueError('Missing training env manifest')
for k,v in manifest['env'].items():
    if k.startswith('RM_'):os.environ[k]=str(v)
usd = bundle/'src_snapshot/robot.usd'
os.environ['RM_MOD4_USD']=str(usd)
os.environ['RM_MILD_DR_PROFILE']='nominal'  # a single-car demonstration, not a DR test
os.environ['RM_SIM2REAL_SENSOR_PROFILE']='off'
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


class PlaybackEnv(Mod4Env):
    """Keep the failure pose visible. Only explicit operator resets reset state."""
    permit_reset=True
    # This bridge targets the delivery's verified Isaac Lab 2.x compatibility port.
    _physics_handles_decimation=False
    def _reset_idx(self,env_ids):
        if self.permit_reset:super()._reset_idx(env_ids)


@torch.inference_mode()
def main():
    ck=Path(args.checkpoint)
    receipt=read_json(bundle/'DOWNLOAD_RECEIPT.json')
    relative=ck.resolve().relative_to(bundle).as_posix()
    expected=receipt.get('files',{}).get(relative)
    if not expected or hashlib.sha256(ck.read_bytes()).hexdigest()!=expected:
        raise ValueError('Checkpoint is absent from the bundle receipt or its SHA256 differs')
    capabilities=read_json(bundle/'PLAYBACK_CAPABILITIES.json')
    yaw_limit=float(capabilities.get('yaw_max_rad_s',0.))
    if yaw_limit:
        cap_path=bundle/'PLAYBACK_CAPABILITIES.json'
        if hashlib.sha256(cap_path.read_bytes()).hexdigest()!=receipt['files'].get(cap_path.name):
            raise ValueError('Yaw capability does not match the download receipt')
        if capabilities.get('verified_checkpoint_sha256')!=expected:
            raise ValueError('Yaw capability belongs to another checkpoint')
        if not 0 < yaw_limit <= float(manifest['env'].get('RM_SPIN_MAX_RAD_S',0)):
            raise ValueError('Playback yaw exceeds this checkpoint command contract')
    torch.manual_seed(args.seed)
    raw=torch.load(ck,map_location='cpu',weights_only=True)
    if not all(torch.isfinite(v).all() for v in raw['actor_state_dict'].values()):
        raise ValueError('Non-finite checkpoint actor weights')
    mlp=nn.Sequential(nn.Linear(35,256),nn.ELU(),nn.Linear(256,128),nn.ELU(),
                      nn.Linear(128,64),nn.ELU(),nn.Linear(64,6))
    mlp.load_state_dict({k.removeprefix('mlp.'):v for k,v in raw['actor_state_dict'].items()if k.startswith('mlp.')},strict=True)
    cfg=task.Mod4EnvCfg();cfg.seed=args.seed;cfg.scene.num_envs=args.num_envs
    if not hasattr(cfg.sim,'physx'):
        raise RuntimeError('Use the verified Isaac Lab 2.x local compatibility bundle for this bridge')
    cfg.sim.device=args.device
    cfg.observations.policy.enable_corruption=False
    if not args.headless:
        cfg.sim.render_interval=cfg.decimation*3  # rendering only; physics/policy cadence unchanged
    cfg.episode_length_s=3600. if args.seconds<=0 else max(args.seconds+1.,20.)
    cfg.viewer.eye=(1.8,1.8,1.0);cfg.viewer.lookat=(0.,0.,.25)
    env=PlaybackEnv(cfg=cfg);robot=env.scene['robot'];dev=env.device;mlp=mlp.to(dev).eval()
    env.reset();env.permit_reset=False
    term=env.command_manager.get_term('twist')
    reader=CommandReader(args.command_file,args.session_id,yaw_limit=yaw_limit)
    data={}
    current=0.; target=0.; current_yaw=0.; target_yaw=0.; reset_id=0;paused=False;fault=None
    begin=time.perf_counter();next_tick=begin;step=0
    trace=[];last=torch.zeros((env.num_envs,6),device=dev)
    previous_delta=last.clone();maxclosure=0.;maxmimic=0.
    print('LOCAL_PLAY_READY '+json.dumps({'checkpoint':ck.name,'iteration':raw['iter'],
        'device':str(dev),'usd_sha256':hashlib.sha256(usd.read_bytes()).hexdigest(),
        'leg_kp':task.LEG_KP,'leg_kd':task.LEG_KD,'height':.25,'yaw_limit':yaw_limit,
        'physical_profile':'nominal','no_exploration':True}),flush=True)
    while app.is_running() and (args.seconds<=0 or step*env.step_dt<args.seconds):
        if args.profile=='interactive':
            command=reader.read()
            if command['quit']:break
            target=command['vx']
            target_yaw=command['wz']
            # The current skills are straight driving and pure spin; world-directed
            # translation during spin has not yet been trained.
            if abs(target_yaw)>1e-6:target=0.
            paused=command['paused']
            if command['reset_id']!=reset_id:
                reset_id=command['reset_id'];env.permit_reset=True;env.reset();env.permit_reset=False
                current=current_yaw=0.;fault=None;last.zero_();previous_delta.zero_();maxclosure=maxmimic=0.
                # Publish the new reset state only after the next physical step.
                data={}
        elif args.profile=='forward_reverse':
            t=step*env.step_dt
            target=0. if t<2 or t>=13 else .6 if t<6 else 0. if t<8 else -.6 if t<12 else 0.
        else:
            t=step*env.step_dt
            target=0.
            target_yaw=0. if t<.4 else min(2.,yaw_limit) if t<2.2 else 0. if t<2.6 else -min(2.,yaw_limit)
        if paused or fault:
            if data:
                data.update(updated_epoch=time.time(),paused=paused,fault=fault)
                atomic(args.output,data)
            # Headless mode must not advance physics during an operator pause.
            time.sleep(.01)
            next_tick=time.perf_counter()
            if args.profile!='interactive':break
        else:
            current=slew(current,target,env.step_dt)
            next_yaw=target_yaw if abs(current)<1e-6 else 0.
            current_yaw=slew(current_yaw,next_yaw,env.step_dt,acceleration=4.)
            if abs(current_yaw)>1e-6:current=0.
            term.time_left[:]=1e9;term.is_standing_env[:]=False
            if hasattr(term,'is_heading_env'):term.is_heading_env[:]=False
            term.command[:]=0.;term.command[:,0]=current;term.command[:,2]=current_yaw;task.height_cmd(env)[:]=.25
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
            if not all(torch.isfinite(v).all() for v in (robot.data.joint_pos,robot.data.root_state_w,action)):
                raise FloatingPointError('Non-finite native state; last finite display frame is retained')
            elif bool(terminated.any()):fault='termination: '+str(env.termination_manager.active_terms)
            elif closure>.002: fault='closed-loop residual exceeds2mm'
            elif mimic>.01: fault='mimic residual exceeds.01rad'
            data={'session_id':args.session_id,'engine':'Isaac PhysX physics / MuJoCo display only',
                  'checkpoint':ck.name,'iteration':int(raw['iter']),'sim_time_s':step*env.step_dt,
                  'command_vx':current,'target_vx':target,'actual_vx':float(robot.data.root_lin_vel_b[0,0]),
                  'command_wz':current_yaw,'target_wz':target_yaw,'actual_wz':float(robot.data.root_ang_vel_b[0,2]),
                  'actual_rpm':float(robot.data.root_ang_vel_b[0,2])*60/(2*torch.pi),
                  'physical_profile':'nominal','playback_yaw_limit':yaw_limit,
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
            if step%100==0:print('PLAY_METRIC '+json.dumps({k:v for k,v in data.items()if k!='body_world_poses'}),flush=True)
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
        if args.smoke_report:atomic(args.smoke_report,result)
        print('LOCAL_PLAY_FINISHED '+json.dumps({k:v for k,v in result.items()if k!='trace'}),flush=True)
    env.close()


try:main()
except BaseException:
    import traceback
    error=traceback.format_exc()
    print(error,flush=True)
    atomic(args.output.parent/'isaac_play_failure.json',{'error':error,'epoch':time.time()})
    raise
finally:app.close()

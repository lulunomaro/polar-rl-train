"""Independent local flat MuJoCo trajectories; never PhysX admission or a live player edit."""
from pathlib import Path
import os,sys,json,time,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np,torch,mujoco
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';D=W/'MOD4_LOCAL_MUJOCO_DRIVE_20261008';P=W/'MOD4_SCUT_FUDAN_THIRTEENTH_HOUR_20261019'
sys.path.insert(0,str(W/'mod4-onnx-mujoco-launcher'));sys.path.insert(0,str(D))
from current_sim import CurrentSim
from sim_runtime import Mod4Sim,RuntimeConfig
from export_latest_moe import Mean35
sys.path.insert(0,str(P/'payload/h1/job0/runtime/isaac/mod4'))
from h1_public_request_phase_v1 import H1PublicRequestPhase,PROFILE
from h1_scut_fudan_jump_reward_v1 import terms,PROFILE as REWARD_PROFILE,FUDAN_TERMS
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

class Policy:
 input_width=35
 def __init__(self,checkpoint):self.net=Mean35(checkpoint['actor_state_dict']).eval()
 def __call__(self,x):
  with torch.no_grad():return self.net(torch.from_numpy(x.reshape(1,35))).numpy()[0].clip(-6,6)

class Sim(CurrentSim):
 def __init__(self,policy):
  self.reset_bank=json.loads((D/'src_snapshot/reset_bank.json').read_bytes())['poses'];self.spawn=(-2.,0.,0.)
  # Exact old player's robot/config/reset; existing onnx is used only by constructor, never stepped.
  receipt=json.loads((D/'BUILD_RECEIPT.json').read_bytes())
  Mod4Sim.__init__(self,D/'playground.xml',D/receipt['onnx'],RuntimeConfig(**json.loads((D/'runtime_config.json').read_bytes())))
  self.policy=policy

def min_z(m,d,ids):
 values=[]
 for g in ids:
  z=d.geom_xmat[g].reshape(3,3)[2];s=m.geom_size[g];t=m.geom_type[g]
  if t==mujoco.mjtGeom.mjGEOM_BOX:e=np.abs(z)@s
  elif t==mujoco.mjtGeom.mjGEOM_CAPSULE:e=abs(z[2])*s[1]+s[0]
  elif t==mujoco.mjtGeom.mjGEOM_CYLINDER:e=abs(z[2])*s[1]+s[0]*np.sqrt(max(0.,1-z[2]**2))
  elif t==mujoco.mjtGeom.mjGEOM_SPHERE:e=s[0]
  else:raise ValueError('Unsupported real local collision type '+str(t))
  values.append(d.geom_xpos[g,2]-e)
 return np.array(values)

def main():
 outpath=R/'THIRTEENTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json';assert not outpath.exists();torch.set_num_threads(2)
 finals=json.loads((P/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert finals['passed_all_three_whole_final_models_CPU']
 dispatch=json.loads((P/'reports/THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').read_bytes())
 sources={'after_reward_hour13':(Path(finals['experts']['h1']['final']['local_path']),finals['experts']['h1']['final']['SHA'])}
 dest=B/'local_thirteenth_reward_hour_new_source_trajectories';assert not dest.exists();dest.mkdir();results=[];begin=time.monotonic()
 for label,(path,sha) in sources.items():
  assert H(path)==sha;policy=Policy(torch.load(path,map_location='cpu',weights_only=False));sim=Sim(policy);m=sim.model;d=sim.data
  ids=np.flatnonzero((m.geom_bodyid>0)&(m.geom_contype==2));assert len(ids)==34
  wheels=np.array([mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_GEOM,x) for x in ('left_tire','right_tire')]);assert all(g in ids for g in wheels)
  nonwheel=[g for g in ids if g not in wheels];force=np.zeros(6)
  for requested in (False,True):
   for yaw0 in (0.,np.pi):
    sim.reset(-2.,0.,yaw0,0.);phase=H1PublicRequestPhase(1,'cpu');rows=[];reward_rows=[];actuator_rows=[];first_failure=None;ready_before=False;maxclosure=0.;maxmimic=0.;t0=time.monotonic();hist=[]
    for control in range(1500):
     if time.monotonic()-begin>480:raise TimeoutError('Bounded local evaluation wall time exhausted; original saved partial prefixes retained')
     phase.begin_control()
     # Normal diagnostic suppresses the request clock through a separate declared control schedule.
     if not requested:phase.request_for_action.zero_();phase.attempt.zero_()
     sim.command.mode=4 if requested and 100<=control<180 else 0;sim.command.auto_mode=False;sim.command.vx=sim.command.vy=sim.command.wz=0.
     if control==100:ready_before=bool(phase.ready.item())
     sim._append_observation(sim.observation_frame());action=policy(sim.observation());sim.last_action[:]=action
     impulse=np.zeros((2,3));non_impulse={g:np.zeros(3) for g in nonwheel}
     for sub in range(sim.decimation):
      tau=sim.action_to_torque(action);d.ctrl[:]=tau;d.xfrc_applied[:]=0.;mujoco.mj_step(m,d)
      for ci in range(d.ncon):
       c=d.contact[ci];g1,g2=int(c.geom1),int(c.geom2)
       # Only robot-versus-static-floor/field contact, excluding internal robot contact.
       if (m.geom_bodyid[g1]>0)==(m.geom_bodyid[g2]>0):continue
       g=g1 if m.geom_bodyid[g1]>0 else g2;mujoco.mj_contactForce(m,d,ci,force);f=c.frame.reshape(3,3).T@force[:3]*(1 if g==g2 else -1)
       if g in wheels:impulse[int(np.flatnonzero(wheels==g)[0])]+=f*m.opt.timestep
       elif g in non_impulse:non_impulse[g]+=f*m.opt.timestep
      if (sub+1)%5:continue
      # Physics .5ms is the original player. Evidence callbacks remain exactly2.5ms,
      # with two-bin5ms wheel integration and unchanged original16/12/200 thresholds.
      hist.append(impulse/.0025);hist=hist[-2:];wheel_n=np.linalg.norm(np.mean(hist,axis=0),axis=1);impulse[:]=0
      non=max(np.linalg.norm(f/.0025) for f in non_impulse.values());non_impulse={g:np.zeros(3) for g in nonwheel}
      clear=min_z(m,d,ids);wc=min_z(m,d,wheels);rot=d.xmat[sim.chassis_id].reshape(3,3);roll=np.arctan2(rot[2,1],rot[2,2]);pitch=np.arcsin(np.clip(-rot[2,0],-1,1));yaw=np.arctan2(rot[1,0],rot[0,0]);vel=np.zeros(6);mujoco.mj_objectVelocity(m,d,mujoco.mjtObj.mjOBJ_BODY,sim.chassis_id,vel,0)
      ev=phase.physical(wheel_N=torch.tensor(wheel_n[None],dtype=torch.float32),wheel_clear_m=torch.tensor(wc[None],dtype=torch.float32),all_min_clear_m=torch.tensor([clear.min()],dtype=torch.float32),nonwheel_max_N=torch.tensor([non],dtype=torch.float32),root_vz=torch.tensor([vel[5]],dtype=torch.float32),root_planar_speed=torch.tensor([np.linalg.norm(vel[3:5])],dtype=torch.float32),roll=torch.tensor([roll],dtype=torch.float32),pitch=torch.tensor([pitch],dtype=torch.float32),yaw=torch.tensor([yaw],dtype=torch.float32))
      closure=sim.closure_error();mimic=sim.mimic_error();maxclosure=max(maxclosure,closure);maxmimic=max(maxmimic,mimic);tilt=np.arccos(np.clip(rot[2,2],-1,1));finite=np.isfinite(d.qpos).all() and np.isfinite(d.qvel).all()
      fail='nonfinite' if not finite else 'closure' if closure>.002 else 'mimic' if mimic>.01 else 'bad_orientation_local_tilt_0.75' if tilt>.75 else None
      rows.append([d.time,control,sim.command.mode,*d.qpos[:7],*vel,*action,*tau,*wheel_n,*wc,clear.min(),non,roll,pitch,yaw,closure,mimic,*[int(ev[k].item()) for k in ('takeoff','landing','recovery')],int(phase.ready.item()),int(phase.attempt.item()),int(phase.air_ticks.item()),int(phase.recover_ticks.item())])
      # Diagnostic-only callback rates, not a PhysX RewardManager/PPO readback.
      # MuJoCo actuator order is hip,crank,wheel on each side; wheel torque is2,5.
      body_ids=[mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,n) for n in ('left_wheel','right_wheel')]
      delta=d.xpos[body_ids]-d.xpos[sim.chassis_id]
      body_omega=rot.T@vel[:3];gravity=rot.T@np.array([0.,0.,-1.])
      tensor=lambda x:torch.as_tensor(x,dtype=torch.float32)
      active=phase.attempt & phase.request_for_action;airborne=phase.air_ticks>0
      raw_rates=terms(active=active,airborne=airborne,supported=torch.tensor([(wheel_n>1.).any()]),vz=tensor([vel[5]]),leg_lengths=tensor(np.linalg.norm(delta,axis=1)[None]),wheel_bottom_relative_z=tensor((wc-d.xpos[sim.chassis_id,2])[None]),wheel_torque=tensor(np.asarray(d.actuator_force)[[2,5]][None]),projected_gravity=tensor(gravity[None]),angular_velocity_body=tensor(body_omega[None]))
      weighted={n:(raw_rates[n]*w).clamp(-2.5,2.5) if n in FUDAN_TERMS else raw_rates[n]*w for n,w in REWARD_PROFILE['weights'].items()}
      actuator_rows.append([d.time,control,*np.asarray(tau),*np.asarray(d.actuator_force)])
      reward_rows.append([d.time,control,int(active.item()),int(airborne.item()),int(phase.launched.item()),int(phase.landed.item()),int(phase.recovered.item()),int(phase.recover_ticks.item()),*body_omega,*gravity,*[float(weighted[n].item()) for n in REWARD_PROFILE['weights']]])
      if fail:first_failure=dict(time=float(d.time),control=control,kind=fail,mode=sim.command.mode,roll=float(roll),pitch=float(pitch));break
     sim.control_steps+=1;phase.finish_control_before_selected_reset()
     if first_failure:break
    raw=dest/(label+('_jump_' if requested else '_normal_')+str(round(yaw0,4))+'.npz');np.savez_compressed(raw,callback=np.asarray(rows,dtype=np.float64),reward_callback=np.asarray(reward_rows,dtype=np.float64),actuator_readback=np.asarray(actuator_rows,dtype=np.float64));results.append(dict(source=label,SHA=sha,public4_requested=requested,yaw=yaw0,ready_before_request=ready_before,counts={k:int(getattr(phase,k+'_count').item()) for k in ('takeoff','landing','recovery')},first_failure=first_failure,survived15s=first_failure is None,callbacks=len(rows),simulated_s=float(d.time),max_closure_m=maxclosure,max_mimic_rad=maxmimic,raw=dict(path=str(raw),bytes=raw.stat().st_size,SHA=H(raw)),wall_seconds=time.monotonic()-t0));print(json.dumps(results[-1]),flush=True)
 out=dict(epoch=time.time(),trial_id='scut-fudan-thirteenth-hour-new-source-local-flat-mujoco-prefix',backend='local CPU MuJoCo original October8 player robot on flat floor',not_PhysX_or_RM7V7_qualification=True,not_statistical_or_unique_causal_comparison=True,no_remote_or_player_change=True,policy='each H1 source actor for both normal and public4 rows; no E0/W35 router or auxiliary forces',strict_phase_source=dict(path=str(P/'payload/h1/job0/runtime/isaac/mod4/h1_public_request_phase_v1.py'),SHA=H(P/'payload/h1/job0/runtime/isaac/mod4/h1_public_request_phase_v1.py'),profile=PROFILE),different_backend_physics=dict(dt=float(m.opt.timestep),evidence_callback=.0025,closure_bound=.002,mimic_bound=.01,local_tilt_first_failure=.75),config=json.loads((D/'runtime_config.json').read_bytes()),source_files={str(p):H(p) for p in [D/'playground.xml',D/'sim_runtime.py',D/'current_sim.py',D/'src_snapshot/reset_bank.json']},raw_columns=['time','control','mode','root7','world_spatial_vel6','action6','actuator_tau6','wheel_norm2','wheel_clear2','all_min_clear','nonwheel_force','roll','pitch','yaw','closure','mimic','takeoff','landing','recovery','ready','attempt','air_ticks','recover_ticks'],reward_telemetry=dict(columns=['time','control','active','airborne','launched','landed','recovered','recover_ticks','body_angular_velocity3','projected_gravity3',*REWARD_PROFILE['weights']],profile=REWARD_PROFILE,callback_rates_only_not_PhysX_PPO_reward=True,weighted_Fudan_rate_clip=2.5,no_reward_used_for_control=True,wheel_torque_input="actual local MuJoCo d.actuator_force indices2,5",actuator_readback_columns=["time","control","sent_d_ctrl6","actual_d_actuator_force6"],not_PhysX_applied_torque_readback=True),episodes=results,not_skill_graduation=True)
 with outpath.open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(local_diagnostic_complete=True,episodes=len(results),counts=[r['counts'] for r in results])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('LOCAL_BEHAVIOR_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_player_or_budget_change=True),f,indent=2)
  raise

"""Measure original SCUT V14_2 pitch under the existing eight start-stop commands."""
from pathlib import Path
import sys,json,hashlib,time,types,datetime,gc,traceback
import numpy as np
import mujoco
R=Path(__file__).resolve().parents[3];A=Path(__file__).resolve().parent;E=A/'evidence'
SOURCE=R/'sources/local/SCUT_ORIGINAL_MUJOCO_ROUGH_20261115'
sys.path.insert(0,str(SOURCE));import scut_backend as backend
backend.RUNTIME=A/'runtime';backend.RUNTIME.mkdir(exist_ok=False)
def sha(path):
 with Path(path).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
expected='d19492be858ffd431a67e5aa40afb4a4c51dc9a1c914c5c92022ed46d5868db7'
assert sha(backend.CHECKPOINT)==expected
assert sha(SOURCE/'weights/SCUT_V14_2_rough_rotation_stair_1000.pt')==expected
assert sha(backend.PLANT)=='60518f64de99edbaa9197c8a9f6f6ac9097e831204df3ad60b4c565e6f77b6f6'
reference=R/'sources/local/MOD4V3_HISTORICAL_BEST_PITCH_AUDIT_20261116'
plan=dict(created_at=datetime.datetime.now().astimezone().isoformat(),kind='frozen_original_scut_pitch_evaluation',model=dict(path=str(backend.CHECKPOINT),sha256=expected,iteration=1000),plant=dict(path=str(backend.PLANT),sha256=sha(backend.PLANT),name='Original author V14_2 ROS2 MuJoCo plant'),backend=dict(path=str(SOURCE/'scut_backend.py'),sha256=sha(SOURCE/'scut_backend.py')),configuration=dict(path=str(backend.CHECKPOINT.parent/'params/env.yaml'),sha256=sha(backend.CHECKPOINT.parent/'params/env.yaml')),script_sha256=sha(__file__),matched_command_protocol='Official random_uniform level9 and plane0; heights0.28/0.40 x commands1.2/2.2; stand2s then1s hard run/2s hard stop,alternating directions;14s;initial x=-0.8,y=-0.1 for1.2 and+0.1 for2.2;first episode only',preserved_native_control=dict(physics_dt=.001,policy_dt=.02,leg_and_wheel_PD_Hz=1000,leg_kp=60,leg_kd=2,leg_torque_limit=40,wheel_kd=.2,wheel_target_scale=10,wheel_torque_limit=5,closure_guard_m=.002),comparison_limit='Different robot plant, actuator envelope, springs and PD/physics rate from MOD4v3; comparison is each published policy on its own paired plant, not a common-plant policy ablation',optimizer_updates=0,jump_requests=0,reference_results=[str(reference/'evidence/nov12_matched_pitch/RESULT.json'),str(reference/'evidence/NOV13_EXISTING_BASELINE_RESULT.json')],command=[sys.executable,'-X','utf8','-B','-u',str(Path(__file__).resolve())])
(A/'PLAN.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
columns=['command_age_s','body_gravity_pitch_rad','local_body_omega_y_rad_s','cmd_vx_m_s','backend_body_vx_m_s','world_root_x_m','world_root_z_m','closure_m','resets','moving','phase_s','observed_sim_time_s','root_world_vx_m_s','height_above_ground_m']
rows=[];arrays={};events=[];compiled=[];started=time.monotonic()
def snapshot(s,age,vx,moving,phase,resets):
 rotation=np.asarray(s.d.xmat[s.base]).reshape(3,3);gravity=rotation.T@np.array([0.,0.,-1.]);pitch=float(np.arctan2(gravity[0],np.linalg.norm(gravity[1:])))
 velocity=np.zeros(6);mujoco.mj_objectVelocity(s.m,s.d,mujoco.mjtObj.mjOBJ_BODY,s.base,velocity,1)
 return [age,pitch,float(velocity[1]),vx,float(s.env.vx),float(s.d.qpos[0]),float(s.d.qpos[2]),float(s.closure),float(resets),float(moving),phase,float(s.d.time),float(s.d.qvel[0]),float(s.z)]
try:
 for family,level in [('random_uniform_for_rm',9),('plane_for_rm',0)]:
  for height in [.28,.40]:
   for speed in [1.2,2.2]:
    s=backend.SCUTReplay(level=level,family=family,direction='up',show=False);s.paused=False
    assert abs(float(s.m.opt.timestep)-.001)<1e-12
    assert s.m.neq==6 and all(int(v)==int(mujoco.mjtEq.mjEQ_CONNECT)for v in s.m.eq_type)
    compiled.append(dict(family=family,height=height,speed=speed,physics_dt=float(s.m.opt.timestep),equality_connect_count=int(s.m.neq),action_names=s.names,actuator_ctrlrange=s.m.actuator_ctrlrange[s.ctrl].tolist(),low_pass_enabled=s.cfg.get('use_action_low_pass_filter'),spring_settings=s.cfg['spring_settings']))
    x0=-.8;y0=-.1 if speed<2 else .1;s.d.qpos[:3]=[x0,y0,s.ground(x0,y0)+.18483];s.d.qpos[3:7]=[1.,0.,0.,0.];s.d.qvel[:]=0.
    mujoco.mj_forward(s.m,s.d);s._update_state();base_reset=s.reset_count;s.reason='';s.max_closure=s.closure
    trace=[];pre_reset=[];original_reset=s.reset_standing;context={}
    def observe_reset(self):
     state=snapshot(self,context['age'],context['vx'],context['moving'],context['phase'],self.reset_count-base_reset+1)
     pre_reset.append(state);events.append(dict(family=family,height=height,speed=speed,reason=self.reason,pre_reset_state=state))
     return original_reset()
    s.reset_standing=types.MethodType(observe_reset,s)
    try:
     for k in range(700):
      age=k*.02;elapsed=max(0.,age-2.);leg=int(elapsed//3.);phase=elapsed%3.;moving=age>=2. and phase<1.
      vx=speed*(1. if leg%2==0 else -1.)if moving else 0.
      context.update(age=age,vx=vx,moving=moving,phase=phase)
      s.args.vx=speed;s.cmd_vx=vx;s.cmd_vy=0.;s.cmd_wz=0.;s.set_height(height)
      s.step({'w'}if vx>0 else {'s'}if vx<0 else set())
      if pre_reset:trace.append(pre_reset[-1]);break
      trace.append(snapshot(s,age,vx,moving,phase,s.reset_count-base_reset))
     arr=np.asarray(trace);window=arr[:,0]>=2.;startup=window&(arr[:,9]>.5)&(arr[:,10]<.8);braking=window&(arr[:,9]<.5)&(arr[:,10]>=1.)&(arr[:,10]<1.8)
     def peak(mask):return float(np.degrees(np.abs(arr[mask,1])).max())if mask.any()else None
     row=dict(family=family,level=level,height=height,speed=speed,resets=s.reset_count-base_reset,reason=s.reason,completed_s=float(arr[-1,0]),pitch_RMS_deg=float(np.degrees(np.sqrt(np.mean(arr[window,1]**2))))if window.any()else None,pitch_rate_RMS_rad_s=float(np.sqrt(np.mean(arr[window,2]**2)))if window.any()else None,startup_peak_deg=peak(startup),braking_peak_deg=peak(braking),moving_vx_MAE=float(np.mean(np.abs(arr[startup,4]-arr[startup,3])))if startup.any()else None,max_closure_m=float(s.max_closure),pitch_rate_peak_rad_s=float(np.abs(arr[window,2]).max())if window.any()else None)
     if len(arr)>151:
      wx=np.r_[np.nan,np.diff(arr[:,5])/.02];before=np.where((arr[:,0]>=2.8-1e-6)&(arr[:,0]<3.-1e-6))[0];stop=np.where((arr[:,0]>=3.-1e-6)&(arr[:,0]<3.8-1e-6))[0]
      if len(before)and len(stop):row.update(first_stop_entry_world_vx_fd=float(wx[before[-1]]),first_stop_pitch_peak_deg=peak(np.isin(np.arange(len(arr)),stop)),first_stop_0p8s_displacement_m=float(abs(arr[stop[-1],5]-arr[before[-1],5])))
     key=family+f'_h{height}_v{speed}';arrays[key]=arr;rows.append(row)
     (E/'PROGRESS.json').write_text(json.dumps(dict(completed=len(rows),last=row),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
     print('CASE_COMPLETE',json.dumps(row,ensure_ascii=False),flush=True)
    finally:s.close();del s;gc.collect()
 summary={}
 for fam in ['random_uniform_for_rm','plane_for_rm']:
  group=[r for r in rows if r['family']==fam];valid=[r for r in group if r['pitch_RMS_deg']is not None]
  summary[fam]=dict(cases=len(group),completed_without_reset=sum(r['resets']==0 and r['completed_s']>=13.9 for r in group),pitch_RMS_deg_mean=float(np.mean([r['pitch_RMS_deg']for r in valid]))if valid else None,startup_peak_deg_max=max((r['startup_peak_deg']for r in valid if r['startup_peak_deg']is not None),default=None),braking_peak_deg_max=max((r['braking_peak_deg']for r in valid if r['braking_peak_deg']is not None),default=None))
 np.savez_compressed(E/'trajectory.npz',**arrays)
 result=dict(model=str(backend.CHECKPOINT),sha256=expected,plant=str(backend.PLANT),plant_sha256=sha(backend.PLANT),rows=rows,summary=summary,wall_seconds=time.monotonic()-started,no_optimizer=True,jump_requests=0,protocol=plan['matched_command_protocol'],native_control=plan['preserved_native_control'],comparison_limit=plan['comparison_limit'],columns=columns)
 (E/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(E/'COMPILED_CONTROL.json').write_text(json.dumps(compiled,indent=2)+'\n');(E/'RESET_EVENTS.json').write_text(json.dumps(events,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 assert sha(backend.CHECKPOINT)==expected
 print('FINAL_RESULT',json.dumps(summary),flush=True)
except Exception:
 (E/'ERROR.txt').write_text(traceback.format_exc(),encoding='utf8');raise

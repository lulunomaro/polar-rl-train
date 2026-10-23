"""Human-authorized local run/jump playtest, using the pinned actual player."""
from pathlib import Path
import hashlib,json,sys,time,traceback
import numpy as np
import mujoco
B=Path(__file__).resolve().parent;R=B/'reports';sys.path.insert(0,str(B/'player'))
from rm7v7_moe_sim import RM7V7MoESim,ROUTES
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 put('REQUESTED_PLAYTEST_STARTED_ACTUAL.json',dict(epoch=time.time(),human_request='你自己试玩跑跑跳跳看看有啥问题？这是后面能解决这些问题的吧',scope='Frozen local47/52/47 MoE, actual copied MuJoCo player; no training/remote/GPU/budget. UI window absent and both original local player processes out at pretest snapshot; cause unknown.'))
 sim=RM7V7MoESim();cases=[];traces={}
 for name,route,kind in [('forward_flat','flat_run','forward'),('reverse_flat','flat_run','reverse'),('jump_flat','flat_run','jump'),('jump_route','flat_jump','jump'),('spin_left','flat_run','spin')]:
  sim.reset_route(route);start=sim.base_position.copy();rows=[];q=[];fault=None;peak=sim.base_position[2];takeoff_samples=0
  for i in range(400):
   if kind=='jump':mode=4 if 100<=i<180 else 0;vx=.8 if mode==4 else 0.;wz=0.
   elif kind=='spin':mode=6;vx=0.;wz=4.
   else:mode=0;vx=(.6 if kind=='forward' else -.6)*min((i+1)/75,1.);wz=0.
   sim.command.mode=mode;sim.command.vx=vx;sim.command.wz=wz;sim.command.auto_mode=False;sim.step_control();h=sim.health();assert h['finite'];peak=max(peak,float(sim.base_position[2]));contact_count=sim.data.ncon
   rows.append([float(sim.data.time),mode,vx,wz,*sim.base_position,h['upright_cos'],h['closure_error_m'],h['mimic_error_rad'],contact_count]);q.append(sim.data.qpos.copy())
   if h['upright_cos']<.60 or sim.base_position[2]<.12:
    fault=dict(control=i+1,time_s=float(sim.data.time),reason='Same local UI tilt/base-height pause condition',health=h);break
  rows=np.asarray(rows);q=np.asarray(q);traces[name+'_state']=rows;traces[name+'_qpos']=q
  cases.append(dict(case=name,route=route,route_source=ROUTES[route],controls=len(rows),duration_s=float(sim.data.time),delta_xyz=(sim.base_position-start).tolist(),base_peak_z_m=peak,start_z_m=float(start[2]),max_base_rise_m=peak-float(start[2]),minimum_upright_cos=float(rows[:,7].min()),fault=fault,last_health=sim.health(),clock_calls=sim.policy.calls,no_wheel_clearance_or_270mm_success_inferred_from_base_height=True))
 out=B/'PLAYTEST_SELECTED_LOCAL_TRACES.npz';np.savez_compressed(out,**traces);artifact=dict(path=str(out),bytes=out.stat().st_size,SHA=hashlib.sha256(out.read_bytes()).hexdigest())
 put('REQUESTED_LOCAL_RUN_JUMP_PLAYTEST_CPU_ACTUAL.json',dict(epoch=time.time(),passed_execution_finite=True,cases=cases,artifact=artifact,source_manifest=json.loads((B/'policy/manifest.json').read_bytes()),scope='Five finite 4-second-or-fault command sequences, same MuJoCo model and player adapter, not PhysX, native skill graduation, seed population, or training reward evaluation. No action scripts, external forces, or mid-air reset.',UI_computer_use='Computer-use list_windows returned no player; fresh CIM found original launcher and child both out, no error log. No UI input attempted against a nonexistent window.',not_unique_cause_or_fix_guarantee=True))
 print(json.dumps([dict(case=x['case'],controls=x['controls'],delta=x['delta_xyz'],rise=x['max_base_rise_m'],minimum_upright=x['minimum_upright_cos'],fault=bool(x['fault'])) for x in cases]))
except BaseException:put('REQUESTED_PLAYTEST_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise

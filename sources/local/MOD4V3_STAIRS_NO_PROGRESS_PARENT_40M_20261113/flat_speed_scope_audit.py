"""Frozen policy flat-only speed-coordinate audit. No optimizer or training edits."""
from pathlib import Path
import ast,hashlib,json,sys,math,time
import numpy as np
import torch
T=Path(__file__).resolve().parent; R=T.parents[2]; O=T/'evidence/flat_speed_scope_audit'
sys.path.insert(0,str(R/'sources/local/MOD4V3_STEP7_DELAY_DIAG_20261110'))
import replay_delay_diagnostic as replay
from eval_flatv2_final import args_for
fixed=R/'sources/local/MOD4V3_FLAT_SPEED_REPAIR_20261112/fixed_60_eval.py'
plan=json.loads((fixed.parent/'TRAIN_PLAN.json').read_text(encoding='utf8'))
recipe=plan['flat_speed_repair'];ld=recipe['leg_pd_decimation'];wd=recipe['wheel_pd_decimation'];assert(ld,wd)==(4,1)
tree=ast.parse(fixed.read_text(encoding='utf8'));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='physics');exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),str(fixed),'exec'),globals());replay.DelayReplay.physics=physics
models={'parent':T/'weights/parent_iter24692.pt','no_progress_020m':T/'weights/model_020m.pt'}
source_plan=json.loads((T/'PLAN.json').read_text(encoding='utf8'));assert hashlib.sha256(models['parent'].read_bytes()).hexdigest()==source_plan['parent_sha256']
torch.set_num_threads(1);rows=[];start=time.time()
columns=['t_s','cmd_vx','cmd_wz','body_vx','reward_vx','heading_vx','world_vx','world_vy','world_vz','roll_rad','pitch_rad','yaw_rad','height_m','cos_tilt','wheel_left_rad_s','wheel_right_rad_s','wheel_tau_left','wheel_tau_right']+[f'action{i}' for i in range(6)]
cases=[('nominal0',0,0,2.,.28),('nominal0',0,0,2.2,.28),('nominal0',0,0,-1.5,.28),('physical5',5,5,2.,.28),('physical10_15',10,15,2.,.28),('nominal0_height040',0,0,2.,.4)]
for label,model in models.items():
 sha=hashlib.sha256(model.read_bytes()).hexdigest()
 for mode,ams,oms,vx,height in cases:
  ns=args_for(str(model));pkg=Path(plan['package']);ns.xml=str(pkg/'mjcf/scene.xml');ns.runtime=str(pkg/'runtime_config.json');ns.semantics=str(pkg/'semantics.json')
  sim=replay.Simulation(ns);rr=replay.DelayReplay(sim,ams,oms,'sent','sensors');trace=[];old_step=sim.step
  def step(keys):
   telemetry=old_step(keys);e=sim.env;d=e.d;rot=np.asarray(d.xmat[e.base_id]).reshape(3,3);vw=np.asarray(d.qvel[:3]).copy();vb=rot.T@vw
   pitch=math.asin(float(np.clip(-rot[2,0],-1,1)));roll=math.atan2(rot[2,1],rot[2,2]);yaw=math.atan2(rot[1,0],rot[0,0]);_,qd=sim._current_active();wheel=qd.detach().cpu().numpy()[4:];tau=np.asarray(d.ctrl)[e.act_ids[4:]]
   trace.append([float(d.time),sim.cmd_vx,sim.cmd_wz,float(vb[0]),float(vb[0]*math.cos(pitch)),float(e.vx),*vw.tolist(),roll,pitch,yaw,sim.z,sim.cos_tilt,*wheel.tolist(),*tau.tolist(),*sim.a_prev[0].tolist()]);return telemetry
  sim.step=step
  try:original=replay.run_case(sim,rr,0,vx,600,200,height=height,wz=0.)
  finally:sim.close()
  x=np.asarray(trace,dtype=float);tail=x[-200:];ix={n:i for i,n in enumerate(columns)};name=f'{label}_{mode}_vx{vx:+.1f}'.replace('.','p').replace('+','pos').replace('-','neg');csv=O/(name+'.csv');np.savetxt(csv,x,delimiter=',',header=','.join(columns),comments='',fmt='%.10g')
  stats={}
  for key in ['body_vx','reward_vx','heading_vx','world_vx']:
   values=tail[:,ix[key]];err=values-tail[:,ix['cmd_vx']]
   stats[key]={'mean':float(values.mean()),'signed_error':float(err.mean()),'mean_absolute_error':float(np.abs(err).mean()),'rms_error':float(np.sqrt(np.mean(err**2))),'std':float(values.std())}
  row=dict(model=label,sha256=sha,mode=mode,action_ms=ams,sensor_ms=oms,target_vx=vx,target_height=height,seed=0,steps=len(x),resets=original['reset_count'],sample_window='last4of12seconds',statistics=stats,command_tail_min=float(tail[:,1].min()),command_tail_max=float(tail[:,1].max()),max_abs_reward_vs_heading=float(np.abs(tail[:,ix['reward_vx']]-tail[:,ix['heading_vx']]).max()),mean_abs_reward_vs_heading=float(np.abs(tail[:,ix['reward_vx']]-tail[:,ix['heading_vx']]).mean()),pitch_abs_max_deg=float(np.degrees(np.abs(tail[:,ix['pitch_rad']]).max())),height_mean=float(tail[:,ix['height_m']].mean()),wheel_rad_s_mean=tail[:,[ix['wheel_left_rad_s'],ix['wheel_right_rad_s']]].mean(0).tolist(),wheel_tau_mean=tail[:,[ix['wheel_tau_left'],ix['wheel_tau_right']]].mean(0).tolist(),trace=csv.name,original_protocol_row=original)
  rows.append(row);(O/'PROGRESS.json').write_text(json.dumps(dict(completed=len(rows),rows=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:row[k] for k in ['model','mode','target_vx','target_height','statistics','max_abs_reward_vs_heading','resets']},ensure_ascii=False),flush=True)
result=dict(scope='flat only, nominal plant; body/reward/heading/world measured simultaneously; frozen deterministic CPU; matched400Hz wheel100Hz leg; no optimizer; fullDR transfer not measured',columns=columns,source_fixed_evaluator_sha256=hashlib.sha256(fixed.read_bytes()).hexdigest(),plant_sha256=hashlib.sha256((Path(plan['package'])/'mjcf/scene.xml').read_bytes()).hexdigest(),rows=rows,wall_seconds=time.time()-start)
(O/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

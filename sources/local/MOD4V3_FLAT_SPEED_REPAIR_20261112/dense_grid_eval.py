"""Checkpoint consumer: fixed MuJoCo tasks with the recorded controller periods."""
from pathlib import Path
import argparse,sys,json,hashlib,time,math,xml.etree.ElementTree as ET
import numpy as np,torch
p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--out',required=True);a=p.parse_args()
T=Path(__file__).resolve().parent;R=T.parents[2];plan=json.loads((T/'TRAIN_PLAN.json').read_text());recipe=plan['flat_speed_repair'];sys.path.insert(0,str(R/'sources/local/MOD4V3_STEP7_DELAY_DIAG_20261110'))
import replay_delay_diagnostic as replay
from eval_flatv2_final import args_for,actual_yaw_rate
ld=recipe['leg_pd_decimation'];wd=recipe['wheel_pd_decimation']
def physics(self,action):
 e=self.sim.env;action=action.clamp(-e.action_clip,e.action_clip);self.action_history.append((float(e.d.time),action.detach().clone()));self.sent_trace.append(action.detach().numpy().reshape(-1).tolist());applied=action
 for j in range(e.decim):
  applied=self.lookup(self.action_history,float(e.d.time)-self.action_s)
  if j%ld==0 or j%wd==0:
   tau=e._torque(applied).detach().numpy().reshape(-1)
   if j%ld==0:e.d.ctrl[e.act_ids[:4]]=tau[:4]
   if j%wd==0:e.d.ctrl[e.act_ids[4:]]=tau[4:]
  replay.mujoco.mj_step(e.m,e.d);self.sensor_history.append((float(e.d.time),self.sensor()))
 e.a_prev=applied.detach().clone();self.last_applied=applied[:,self.sim.ppo_to_env].detach().cpu().clone();self.applied_trace.append(applied.detach().numpy().reshape(-1).tolist());return e.state()
replay.DelayReplay.physics=physics
out=Path(a.out);out.mkdir(exist_ok=False);rows=[];arrays={};start=time.time();torch.set_num_threads(1)
tasks=[(f'v{vx}_h{h}',vx,0.,h,.20 if vx<0 else .15,None) for h in (.20,.24,.28,.32,.36,.40,.42) for vx in (-2.2,-1.5,0.,1.,1.5,2.,2.2)]
for delay in (0,):
 ns=args_for(a.model);pkg=Path(plan['package']);ns.xml=str(pkg/'mjcf/scene.xml');ns.runtime=str(pkg/'runtime_config.json');ns.semantics=str(pkg/'semantics.json')
 sim=replay.Simulation(ns);rr=replay.DelayReplay(sim,delay,delay,'sent','sensors');old_step=sim.step;trace=[]
 pairs=[(sim.env.m.site(c.get('site1')).id,sim.env.m.site(c.get('site2')).id) for c in ET.parse(ns.xml).getroot().findall('equality/connect')]
 def step(keys):
  value=old_step(keys);d=sim.env.d;closure=max(np.linalg.norm(d.site_xpos[x]-d.site_xpos[y]) for x,y in pairs)
  trace.append([float(sim.env.vx),actual_yaw_rate(sim),float(sim.z),float(sim.cos_tilt),float(closure),*sim.a_prev[0].tolist()])
  if closure>.002:raise RuntimeError('Replay2mm per-env closure guard')
  return value
 sim.step=step
 try:
  for name,vx,wz,h,vtol,wtol in tasks:
   trace=[];row=replay.run_case(sim,rr,0,vx,600,200,height=h,wz=wz);data=np.asarray(trace);arrays[name+'_delay'+str(delay)]=data
   passed=row['reset_count']==0 and row['completed_steps']==600
   if vtol is not None:passed=passed and row['vx_abs_error']<=vtol
   if wtol is not None:passed=passed and row['wz_abs_error']<=abs(wz)*wtol
   if name.startswith('height'):passed=passed and row['height_abs_error']<=.02
   row.update(task=name,delay_ms=delay,velocity_tolerance=vtol,yaw_relative_tolerance=wtol,passed=bool(passed),diagnostic_only=name.startswith('combo'),max_closure_m=float(data[:,4].max()))
   rows.append(row);(out/'PROGRESS.json').write_text(json.dumps(dict(completed_cases=len(rows),last=row,elapsed=time.time()-start)))
 finally:sim.close()
model=Path(a.model);ckpt=torch.load(model,map_location='cpu',weights_only=False)
result=dict(model=str(model),sha256=hashlib.sha256(model.read_bytes()).hexdigest(),iteration=ckpt['iter'],method=ckpt.get('flat_speed_repair',{}),protocol='49case nominal0ms dense MuJoCo;7heights.20-.42x7velocities-2.2to2.2;seed0;12s/tail4s;recorded matchedcontroller;strict2mmclosure;not fullDR acceptance',physics_s=.0025,leg_PD_s=ld*.0025,wheel_PD_s=wd*.0025,policy_s=.02,rows=rows,wall_seconds=time.time()-start,no_optimizer=True)
np.savez_compressed(out/'TRAJECTORY.npz',**arrays);(out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(dict(sha256=result['sha256'],rows=[{k:x[k] for k in ('task','delay_ms','vx_mean','wz_mean','height_mean','reset_count','passed')} for x in rows]),ensure_ascii=False),flush=True)

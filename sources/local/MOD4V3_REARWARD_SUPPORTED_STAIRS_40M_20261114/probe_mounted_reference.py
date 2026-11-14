"""Nominal mounted-state feasibility only; actual motor envelope, no RL updates."""
from pathlib import Path
import sys,json,importlib.util,math,time
import numpy as np,torch,mujoco
from scipy.optimize import least_squares
T=Path(__file__).resolve().parent;R=T.parents[2];LOW=T.parent/'MOD4V3_LOW_SPEED_RETRACTION_20261113';D=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112';PLANT=D/'plant/MOD4v3_HW300N60_R3'
sys.path.insert(0,str(LOW));spec=importlib.util.spec_from_file_location('rearward_existing_replay',LOW/'replay_probe.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
out=T/'evidence/local_reference_r1';out.mkdir(exist_ok=False);show=old.setup(out,'parent');sim=show.Replay(level=3);e=sim.env;m,d=e.m,e.d
sys.path.insert(0,str(PLANT));import kinematics
bank=json.loads((T/'support/mod4v3_ppo_v1/rearward_mount_bank.json').read_text());row=bank['poses'][1]
for name,value in row['joint_positions'].items():d.qpos[m.joint(name).qposadr[0]]=value
d.qpos[:7]=[-2.9+row['root_inward_of_edge_m'],0,.3785,1,0,0,0];d.qvel[:]=0.;d.time=0.;mujoco.mj_forward(m,d)
knots=[(0.,[-.13,-.3155]),(1.,[-.13,-.3155]),(2.,[-.21,-.20]),(2.7,[-.20,-.09]),(4.1,[.045,-.10]),(5.,[.045,-.116]),(6.,[.045,-.116])]
bounds=kinematics.mechanical_delta_bounds();prior=np.array([-.323272,1.71105]);targets=[];errors=[]
for age in np.arange(0,6.,.02):
 j=next(i for i in range(len(knots)-1) if knots[i][0]<=age<knots[i+1][0]);a,b=knots[j],knots[j+1];u=(age-a[0])/(b[0]-a[0]);goal=np.array(a[1])*(1-u)+np.array(b[1])*u
 def fun(v):
  try:return kinematics.leg_configuration(v[0]+v[1],v[0])[1]['W']-goal
  except ValueError:return np.full(2,10.)
 sol=least_squares(fun,prior,bounds=([-3,bounds[0]+1e-4],[3,bounds[1]-1e-4]),diff_step=1e-5);prior=sol.x;errors.append(float(np.linalg.norm(sol.fun)))
 dd=mujoco.MjData(m);kinematics.set_configuration(m,dd,left=(sum(sol.x),sol.x[0]),right=(sum(sol.x),sol.x[0]));native=np.array(dd.qpos[e.qadr_all]);action=np.zeros(6,np.float32);action[:4]=(native[e.leg_ids]-e.default_q[e.leg_ids].cpu().numpy())/.5;targets.append(action)
trace=[];forcebuf=np.zeros(6);wheelids=[m.body(x).id for x in ['left_wheel_link','right_wheel_link']];guideids={i for i in range(m.nbody) if 'guide' in m.body(i).name};peak=0.;stop=None;held=np.zeros(4)
for k in range(2400):
 action=torch.tensor(targets[min(k//8,len(targets)-1)]).reshape(1,6);torque=e._torque(action).detach().cpu().numpy().reshape(-1)
 if k%4==0:held=torque[:4].copy()
 d.ctrl[e.act_ids]=np.r_[held,torque[4:]];mujoco.mj_step(m,d)
 closure=max(float(np.linalg.norm(d.site_xpos[a]-d.site_xpos[b])) for a,b in sim.pairs);peak=max(peak,closure)
 if not np.isfinite(d.qpos).all() or closure>.002:stop=dict(step=k,closure=closure,finite=bool(np.isfinite(d.qpos).all()));break
 if k%8==0:
  vertical=0.;wheel_support=[0.,0.]
  for ci in range(d.ncon):
   c=d.contact[ci];g1,g2=int(c.geom1),int(c.geom2);b1,b2=int(m.geom_bodyid[g1]),int(m.geom_bodyid[g2]);
   if (b1==0)==(b2==0):continue
   robot,sign=(b2,1.) if b1==0 else (b1,-1.);mujoco.mj_contactForce(m,d,ci,forcebuf);f=sign*np.asarray(c.frame).reshape(3,3).T@forcebuf[:3]
   if robot in guideids or robot==e.base_id:vertical+=max(0.,float(f[2]))
   if robot in wheelids and ((m.geom(g1).name or '').startswith('step_') or (m.geom(g2).name or '').startswith('step_')):wheel_support[wheelids.index(robot)]+=max(0.,float(f[2]))
  trace.append(dict(time=float(d.time),root=d.qpos[:3].tolist(),wheel=d.xpos[wheelids].tolist(),guide_body_upward_N=vertical,wheel_tread_upward_N=wheel_support,closure=closure))
result=dict(no_optimizer=True,controller='scripted IK/PD reference only; not learned policy',motor_and_physics='existing MOD4 envelope;2.5ms,legs100Hz,wheels400Hz',max_kinematic_target_error_m=max(errors),max_closure_m=peak,stop=stop,initial_support_mean_N=float(np.mean([x['guide_body_upward_N'] for x in trace if x['time']<1.])),first_step_both_supported=any(min(x['wheel_tread_upward_N'])>5 and min(w[2] for w in x['wheel'])>.24 for x in trace),trace=trace)
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');sim.close();print(json.dumps({k:v for k,v in result.items() if k!='trace'},indent=2))

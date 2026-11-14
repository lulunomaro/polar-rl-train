"""Bounded real-MOD4 IK/PD feasibility search. No policy updates or external holding."""
from pathlib import Path
import sys,json,importlib.util,itertools,time,math
import numpy as np,torch,mujoco
from scipy.optimize import least_squares
T=Path(__file__).resolve().parent;R=T.parents[2];LOW=T.parent/'MOD4V3_LOW_SPEED_RETRACTION_20261113';D=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112';PLANT=D/'plant/MOD4v3_HW300N60_R3'
spec=importlib.util.spec_from_file_location('prior_probe',LOW/'replay_probe.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
out=T/'evidence/reference_search_r4';out.mkdir(exist_ok=False);show=old.setup(out,'parent');sim=show.Replay(level=3);e=sim.env;m,d=e.m,e.d
sys.path.insert(0,str(PLANT));import kinematics as kin
bounds=kin.mechanical_delta_bounds();grid=[];av=[]
for rr in np.linspace(-1.8,1.5,44):
 for delta in np.linspace(bounds[0]+.001,bounds[1]-.001,36):
  try:grid.append(kin.leg_configuration(rr+delta,rr)[1]['W']);av.append([rr,delta])
  except ValueError:pass
grid=np.array(grid);av=np.array(av);cache={}
def solve(goal):
 key=tuple(goal)
 if key not in cache:
  seed=av[np.argmin(np.linalg.norm(grid-np.array(goal),axis=1))]
  def f(v):
   try:return kin.leg_configuration(v[0]+v[1],v[0])[1]['W']-goal
   except ValueError:return np.full(2,10.)
  v=least_squares(f,seed,bounds=([-3,bounds[0]+1e-4],[3,bounds[1]-1e-4]),diff_step=1e-5)
  dd=mujoco.MjData(m);kin.set_configuration(m,dd,left=(sum(v.x),v.x[0]),right=(sum(v.x),v.x[0]))
  native=dd.qpos[e.qadr_all];action=np.zeros(6,np.float32);action[:4]=(native[e.leg_ids]-e.default_q[e.leg_ids].cpu().numpy())/.5
  cache[key]=(action,dd.qpos.copy(),float(np.linalg.norm(v.fun)))
 return cache[key]
wheelids=[m.body(x).id for x in ['left_wheel_link','right_wheel_link']];supportids={i for i in range(m.nbody) if 'guide' in m.body(i).name}|{e.base_id};forcebuf=np.zeros(6)
def sample():
 support=0.;tread=np.zeros(2)
 for ci in range(d.ncon):
  c=d.contact[ci];g1,g2=int(c.geom1),int(c.geom2);b1,b2=int(m.geom_bodyid[g1]),int(m.geom_bodyid[g2])
  if (b1==0)==(b2==0):continue
  terrain,robot,sign=(g1,b2,1.) if b1==0 else(g2,b1,-1.);mujoco.mj_contactForce(m,d,ci,forcebuf);frame=np.asarray(c.frame).reshape(3,3);f=sign*frame.T@forcebuf[:3]
  if robot in supportids:support+=max(0.,float(f[2]))
  if robot in wheelids and (m.geom(terrain).name or '')=='step_1' and sign*frame[0,2]>.7:tread[wheelids.index(robot)]+=max(0.,float(f[2]))
 return dict(time=float(d.time),root=d.qpos[:3].tolist(),wheel=d.xpos[wheelids].tolist(),support_N=support,tread_N=tread.tolist(),upright=float(d.xmat[e.base_id].reshape(3,3)[2,2]),com=d.subtree_com[e.base_id].tolist())
# An inward chassis pose with both guide pairs on tread; wheel/riser separation remains >=wheel radius.
starts=[(-.24,-.23,.165),(-.27,-.20,.195),(-.30,-.16,.225),(-.28,-.18,.205)]
results=[];best=None;starttime=time.time()
for case,(start,rearx,wvel,pace) in enumerate(itertools.product(starts,[-.26],[.4,.8],[.25,.4])):
 sx,sz,inward=start;initial=solve([sx,sz]);d.qpos[:]=initial[1];d.qpos[:7]=[-2.9+inward,0,.3785,1,0,0,0];d.qvel[:]=0;d.ctrl[:]=0;d.time=0;mujoco.mj_forward(m,d)
 # Circular short-leg sweep crosses vertical at a reachable .118m, instead of an impossible .10m length.
 knots=[(0,[sx,sz]),(.25,[sx,sz]),(.8,[rearx,-.18]),(1.5,[rearx,-.10]),(2.,[-.105,-.09]),(2.5,[0.,-.118]),(3.,[.08,-.105]),(3.4,[.08,-.125]),(3.9,[-.04,-.24]),(4.6,[-.10,-.32])]
 times=np.array([a[0]*pace for a in knots]);actions=np.array([solve(p)[0] for _,p in knots]);actions[:,4:]=wvel/(.0625*10)
 trace=[];held=np.zeros(4);peak=0.;stop=None;land=0.;rearclear=False;support0=0.;maxlift=-1.
 steps=round((times[-1]+1.)/.0025)
 for k in range(steps):
  age=k*.0025;j=min(np.searchsorted(times,age,side='right')-1,len(times)-2);u=np.clip((age-times[j])/(times[j+1]-times[j]),0,1);u=u*u*(3-2*u);a=torch.tensor(actions[j]*(1-u)+actions[j+1]*u).reshape(1,6).clamp(-e.action_clip,e.action_clip)
  qnow=torch.tensor(d.qpos[e.qadr_all][e.leg_ids],dtype=torch.float32);desired=e.default_q[e.leg_ids]+.5*a[0,:4];a[0,:4]+=2.0*(desired-qnow)/.5;a=a.clamp(-e.action_clip,e.action_clip)
  torque=e._torque(a).detach().cpu().numpy().reshape(-1)
  if k%4==0:held=torque[:4].copy()
  d.ctrl[e.act_ids]=np.r_[held,torque[4:]];mujoco.mj_step(m,d)
  closure=max(float(np.linalg.norm(d.site_xpos[a]-d.site_xpos[b]))for a,b in sim.pairs);peak=max(peak,closure)
  if not np.isfinite(d.qpos).all() or closure>.002:stop=dict(step=k,closure=closure);break
  if k%8==0:
   row=sample();row['closure']=closure;row['qpos']=d.qpos.tolist();row['qvel']=d.qvel.tolist();row['action_env']=a[0].tolist();trace.append(row);maxlift=max(maxlift,min(w[2]-.2625 for w in row['wheel']))
   if min(row['tread_N'])>5:land+=.02
   if row['upright']<math.cos(math.radians(40)) or d.qpos[2]<.15:stop=dict(step=k,tilt=row['upright'],root=d.qpos[:3].tolist());break
 result=dict(case=case,start=list(start),rearx=rearx,wheel_speed=wvel,pace=pace,first_both_tread_seconds=round(land,3),max_both_clearance_m=maxlift,max_closure_m=peak,stop=stop,final=trace[-1],max_IK_residual_m=max(solve(p)[2] for _,p in knots),initial_support_N=float(np.mean([r['support_N']for r in trace if r['time']<.2])),trace=trace)
 results.append(result);(out/f'case_{case:03d}.json').write_text(json.dumps(result,indent=2)+'\n')
 score=(land,maxlift)
 if best is None or score>best[0]:best=(score,case)
 print('CASE',case,'landing',round(land,2),'clear',round(maxlift,4),'stop',stop,'best',best[1],flush=True)
 if land>=.2:print('PHYSICAL_REFERENCE_FOUND',case,flush=True);break
summary=dict(no_policy_updates=True,actual_plant_sha='77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f',external_holding_force=False,physics_ms=2.5,leg_Hz=100,wheel_Hz=400,nominal_only=True,cases=len(results),best_case=best[1],successful=results[best[1]]['first_both_tread_seconds']>=.2,elapsed=time.time()-starttime,results=[{k:v for k,v in r.items()if k!='trace'}for r in results])
(out/'RESULT.json').write_text(json.dumps(summary,indent=2)+'\n');sim.close();print('SEARCH_COMPLETE',json.dumps({k:v for k,v in summary.items()if k!='results'}),flush=True)

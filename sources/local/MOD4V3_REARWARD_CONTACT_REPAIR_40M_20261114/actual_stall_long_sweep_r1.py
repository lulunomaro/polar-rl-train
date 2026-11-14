"""Bounded real-MOD4 IK/PD feasibility search. No policy updates or external holding."""
from pathlib import Path
import sys,json,importlib.util,itertools,time,math
import numpy as np,torch,mujoco
from scipy.optimize import least_squares
T=Path(__file__).resolve().parent;R=T.parents[2];LOW=T.parent/'MOD4V3_LOW_SPEED_RETRACTION_20261113';D=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112';PLANT=D/'plant/MOD4v3_HW300N60_R3'
spec=importlib.util.spec_from_file_location('prior_probe',LOW/'replay_probe.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
out=T/'evidence/actual_stall_long_sweep_r1';out.mkdir(exist_ok=False);show=old.setup(out,'parent');sim=show.Replay(level=3);e=sim.env;m,d=e.m,e.d
sys.path.insert(0,str(PLANT));import kinematics as kin
sys.path.insert(0,str(T/'manual_replay'));from replay_supported_guards import supported_contact
from replay_guards import pose_state
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
starts=[]
for label in ['parent','previous40m']:
 metadata=json.loads((T/'evidence/actual_stall_capture_r1'/(label+'.json')).read_text());states=np.load(T/'evidence/actual_stall_capture_r1'/(label+'_states.npz'))
 for i,row in enumerate(metadata['actual_stuck_snapshots']):starts.append((label,i,row,{key:states[f'{key}_{i}'].copy()for key in ['qpos','qvel','ctrl','a_prev']}))
results=[];best=None;successful_frames=[];starttime=time.time()
for case,(start,rearx,wvel,pace) in enumerate(itertools.product(starts,[-.26],[-.4,0.,.4],[.25,.4])):
 label,snapshot,row,raw=start;d.qpos[:]=raw['qpos'];d.qvel[:]=raw['qvel'];d.ctrl[:]=raw['ctrl'];d.time=0;mujoco.mj_forward(m,d);relative=(d.xmat[e.base_id].reshape(3,3).T@(d.xpos[wheelids].mean(0)-d.qpos[:3]));sx,sz=float(relative[0]),float(relative[2]);inward=float(d.qpos[0]+2.9)
 # Circular short-leg sweep crosses vertical at a reachable .118m, instead of an impossible .10m length.
 knots=[(0,[sx,sz]),(.25,[sx,sz]),(.8,[-.20,-math.sqrt(.343**2-.20**2)]),(1.25,[-.27,-math.sqrt(.343**2-.27**2)]),(1.8,[-.26,-.10]),(2.3,[-.105,-.09]),(2.8,[0.,-.118]),(3.3,[.08,-.105]),(3.7,[.08,-.125]),(4.2,[-.04,-.24]),(4.9,[-.10,-.32])]
 times=np.array([a[0]*pace for a in knots]);actions=np.array([solve(p)[0] for _,p in knots]);actions[:,4:]=wvel/(.0625*10)
 tilt_dwell=0;contact_dwell=0;sim._repair_stair_stage=0;caught=False;parent_action=None;current_action=None;demo=[];sim.a_prev=torch.tensor(raw['a_prev'],dtype=torch.float32);firstland=None;trace=[];held=np.zeros(4);peak=0.;stop=None;land=0.;rearclear=False;support0=0.;maxlift=-1.
 steps=round((times[-1]+1.)/.0025)
 for k in range(steps):
  age=k*.0025;j=min(np.searchsorted(times,age,side='right')-1,len(times)-2);u=np.clip((age-times[j])/(times[j+1]-times[j]),0,1);u=u*u*(3-2*u);a=torch.tensor(actions[j]*(1-u)+actions[j+1]*u).reshape(1,6).clamp(-e.action_clip,e.action_clip)
  qnow=torch.tensor(d.qpos[e.qadr_all][e.leg_ids],dtype=torch.float32);desired=e.default_q[e.leg_ids]+.5*a[0,:4];a[0,:4]+=2.0*(desired-qnow)/.5;a=a.clamp(-e.action_clip,e.action_clip)
  if k%8==0 or current_action is None:
   q,qd=sim._current_active();rot=torch.tensor(d.xmat[e.base_id].reshape(3,3),dtype=torch.float32);jp=q-sim.default_active;jp[4:]=0;mode=torch.zeros(7);mode[0]=1
   obs=torch.cat((torch.tensor([.4,0.,0.,.42*5]),torch.tensor(d.qvel[3:6],dtype=torch.float32)*.5,rot.T@torch.tensor([0.,0.,-1.]),jp,qd[:4]*.1,qd[4:]*.1,sim.a_prev[0],mode)).unsqueeze(0)
   if caught:
    with torch.no_grad():a=sim.actor(obs.float()).clamp(-6,6)[:,sim.ppo_to_env]
   a=a.float();current_action=a.clone();demo.append(dict(time=age,policy=obs[0].tolist(),actions=a[0,sim.ppo_to_env].tolist(),scripted=not caught));sim.a_prev=a[:,sim.ppo_to_env].clone()
  a=current_action
  torque=e._torque(a).detach().cpu().numpy().reshape(-1)
  if k%4==0:held=torque[:4].copy()
  d.ctrl[e.act_ids]=np.r_[held,torque[4:]];mujoco.mj_step(m,d)
  closure=max(float(np.linalg.norm(d.site_xpos[a]-d.site_xpos[b]))for a,b in sim.pairs);peak=max(peak,closure)
  if not np.isfinite(d.qpos).all() or closure>.002:stop=dict(step=k,closure=closure);break
  if k%8==7:
   row=sample();row['closure']=closure;row['qpos']=d.qpos.tolist();row['qvel']=d.qvel.tolist();row['action_env']=a[0].tolist();trace.append(row);maxlift=max(maxlift,min(w[2]-.2625 for w in row['wheel']))
   if min(row['tread_N'])>5 and min(w[2] for w in row['wheel'])>.25 and min(w[0] for w in row['wheel'])>-2.92:land+=.02;caught=True;firstland=age if firstland is None else firstland
   state=pose_state(sim);contact=supported_contact(sim);tilted=abs(state['pitch_deg'])>40. or abs(state['roll_deg'])>40.
   tilt_dwell=tilt_dwell+1 if tilted else 0;contact_dwell=contact_dwell+1 if contact['contact_bad']else 0
   row['pitch_deg']=state['pitch_deg'];row['roll_deg']=state['roll_deg'];row['orientation_dwell']=tilt_dwell;row['contact_dwell']=contact_dwell
   if tilt_dwell>=10 or contact_dwell>=10 or d.qpos[2]<sim.ground(0.,0.)-1. or abs(d.qpos[0])>4.1 or abs(d.qpos[1])>4.1:stop=dict(step=k,orientation_dwell=tilt_dwell,contact_dwell=contact_dwell,root=d.qpos[:3].tolist());break
 result=dict(case=case,start=dict(model=label,snapshot=snapshot,root=d.qpos[:3].tolist(),initial_body_wheel_xz=[sx,sz]),rearx=rearx,wheel_speed=wvel,pace=pace,first_both_tread_seconds=round(land,3),max_both_clearance_m=maxlift,max_closure_m=peak,stop=stop,final=trace[-1],max_IK_residual_m=max(solve(p)[2] for _,p in knots),initial_support_N=float(np.mean([r['support_N']for r in trace if r['time']<.2])),trace=trace)
 results.append(result);(out/f'case_{case:03d}.json').write_text(json.dumps(result,indent=2)+'\n')
 score=(land,maxlift)
 if best is None or score>best[0]:best=(score,case)
 print('CASE',case,'landing',round(land,2),'clear',round(maxlift,4),'stop',stop,'best',best[1],flush=True)
 if land>=.2 and stop is None and d.qpos[2]>.52 and trace[-1]['upright']>.9:
  successful_frames.append([x for x in demo if x['time']<min(1.5,firstland+.4)]);print('PHYSICAL_REFERENCE_FOUND',case,flush=True)
summary=dict(no_policy_updates=True,actual_plant_sha='77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f',external_holding_force=False,physics_ms=2.5,leg_Hz=100,wheel_Hz=400,nominal_only=True,cases=len(results),best_case=best[1],successful=results[best[1]]['first_both_tread_seconds']>=.2,elapsed=time.time()-starttime,results=[{k:v for k,v in r.items()if k!='trace'}for r in results])
summary['strategy']='Keep .343m near-extended virtual leg while sweeping rearward first, then retract/lift; wheel negative/zero/positive0.4m/s tested; no extra PPO';summary['protection_protocol']='Existing native analogue:roll/pitch>40deg and non-exempt contact separately10x20ms;2mm closure immediate,terrain-origin-minus1m and4.1m tile guard unchanged';summary['prior_prototype_difference']='r1 stopped at first total-tilt>40deg; original result kept, not native-equivalent timing';summary['actual_stalled_initial_state']=True;summary['successful_recoveries']=len(successful_frames);summary['no_dataset_or_weight_write']=True;summary['scope']='Captured actual stalled states, not horizontal IK reset bank; same50Hz motor targets,2.5ms,100Hz legs,400Hz wheels,original2mm/40deg protections; scripted reference then frozen comprehensive parent, not learned-policy performance'
(out/'RESULT.json').write_text(json.dumps(summary,indent=2)+'\n');sim.close();print('SEARCH_COMPLETE',json.dumps({k:v for k,v in summary.items()if k!='results'}),flush=True)

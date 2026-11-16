"""Frozen nominal MuJoCo analogue of native single-step course; exact real top contacts."""
from pathlib import Path
import argparse,sys,json,hashlib,time,importlib.util,types,math,gc
import numpy as np,torch,mujoco,trimesh
p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--out',required=True);p.add_argument('--quick',action='store_true');a=p.parse_args();torch.set_num_threads(1)
T=Path(__file__).resolve().parent;R=T.parents[2];E=Path(a.out).resolve();E.mkdir(parents=True,exist_ok=False)
D=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112'
spec=importlib.util.spec_from_file_location('single_course_show',D/'viewer/showcase.py');show=importlib.util.module_from_spec(spec);spec.loader.exec_module(show)
show.CKPT=Path(a.model).resolve();show.EXPECTED=hashlib.sha256(show.CKPT.read_bytes()).hexdigest()
show.Simulation.step.__globals__['CMD_SLEW']=.02
sys.path.insert(0,str(T/'manual_replay'));from replay_guards import policy_step_without_flat_reset
advance=policy_step_without_flat_reset(show.Simulation)
heights=[.05,.07,.09,.11,.13,.15,.17,.19,.20];starts=[(-2.25,0.,0.),(-2.15,-.10,-.03),(-2.40,.10,.03),(-2.5,.06,-.04),(-2.3,-.06,.04)]
if a.quick:heights=[.05];starts=starts[:1]
rows=[];arrays={};wall=time.time()
for h in heights:
 B=E/('h%03dmm'%round(h*1000));(B/'tiles').mkdir(parents=True)
 base=trimesh.creation.box((9.,9.,.1));base.apply_translation((0,0,-.05));top=trimesh.creation.box((3.,3.,h));top.apply_translation((0,0,h/2));mesh=trimesh.util.concatenate([base,top]);np.savez_compressed(B/'tiles/r00_c00.npz',vertices=mesh.vertices,faces=mesh.faces);show.B=B
 for seed,(sx,sy,syaw)in enumerate(starts):
  s=show.Replay();e=s.env;m=e.m;d=e.d;s.args.vx=.4;s.cmd_vx=0.;s.cmd_wz=0.;s.cmd_vy=0.
  d.qpos[:3]=[sx,sy,e.bank_z+.01];d.qpos[3:7]=[math.cos(syaw/2),0.,0.,math.sin(syaw/2)];d.qvel[:]=0.;mujoco.mj_forward(m,d);e.state();s.reset_count=1
  wb=[m.body(n).id for n in ['left_wheel_link','right_wheel_link']];guides={int(m.geom_bodyid[i])for i in range(m.ngeom)if m.geom(i).name.startswith('guide_wheel_')}
  maxclosure=0.;reason='timeout';hold=0.;success=False;physical_top=False;entry=None;speedmax=0.;trace=[];landed=[False,False];tiltsteps=contactsteps=0
  def physics(env,act):
   nonlocal_placeholder=None
   global maxclosure
   act=act.clamp(-env.action_clip,env.action_clip)
   for j in range(env.decim):
    tau=env._torque(act).detach().numpy().reshape(-1)
    if j%4==0:d.ctrl[env.act_ids[:4]]=tau[:4]
    d.ctrl[env.act_ids[4:]]=tau[4:];mujoco.mj_step(m,d)
    if not np.isfinite(d.qpos).all()or not np.isfinite(d.qvel).all():raise show.SafetyStop('nonfinite')
    cl=max(float(np.linalg.norm(d.site_xpos[u]-d.site_xpos[v]))for u,v in s.pairs);maxclosure=max(maxclosure,cl)
    if cl>1.0:raise show.SafetyStop('catastrophic closure>1m')
   env.a_prev=act.detach().to(env.device);return env.state()
  e.step=types.MethodType(physics,e)
  try:
   for k in range(800):
    age=k*.02;s.set_height(min(.28+.4*h,.28+.06*age))
    try:advance(s,{'w'}if age>=1.5 else set())
    except show.SafetyStop as exc:reason=str(exc);break
    forces=np.zeros((m.nbody,3));supported=[False,False]
    for ci in range(d.ncon):
     c=d.contact[ci];g1,g2=int(c.geom1),int(c.geom2);b1,b2=int(m.geom_bodyid[g1]),int(m.geom_bodyid[g2]);cf=np.zeros(6);mujoco.mj_contactForce(m,d,ci,cf);world=np.asarray(c.frame).reshape(3,3).T@cf[:3];forces[b1]-=world;forces[b2]+=world
     terrain,body,sgn=(g1,b2,1.)if b1==0 else(g2,b1,-1.)if b2==0 else(-1,-1,0.)
     if terrain>=0 and m.geom(terrain).name=='step_1'and body in wb:
      normal=sgn*np.asarray(c.frame).reshape(3,3)[0]
      if cf[0]>5. and normal[2]>.7 and abs(float(c.pos[2])-h)<.012:supported[wb.index(body)]=True
    wheel=d.xpos[wb];x=-wheel[:,0];y=wheel[:,1];z=wheel[:,2];vx=float(np.linalg.norm(d.qvel[:2]));near=float(np.min(np.abs(x-1.5)))<.45
    if age>=1.5:
     if entry is None and min(x)<1.7:entry=vx
     if near or entry is not None:speedmax=max(speedmax,vx)
    tol=max(.012,min(.025,.3*h));upper=np.array(supported)&(x<1.475)&(x>-1.4)&(np.abs(y)<1.4)&(np.abs(z-(h+.0625))<tol)
    for wi in range(2):landed[wi]|=bool(upper[wi])
    rot=d.xmat[e.base_id].reshape(3,3);pitch=math.asin(float(np.clip(-rot[2,0],-1,1)));roll=math.atan2(float(rot[2,1]),float(rot[2,2]));ang=np.zeros(6);mujoco.mj_objectVelocity(m,d,mujoco.mjtObj.mjOBJ_BODY,e.base_id,ang,1)
    badcontact=bool(np.linalg.norm(forces[e.base_id])>1. or(any(np.linalg.norm(forces[g])>1. for g in guides)and not near))
    contactsteps=contactsteps+1 if badcontact else 0;tiltsteps=tiltsteps+1 if max(abs(pitch),abs(roll))>math.radians(40)else 0
    if contactsteps>=10:reason='chassis_or_nonexempt_guide_contact_0.2s';break
    if tiltsteps>=10:reason='roll_or_pitch>40deg_0.2s';break
    if max(abs(float(d.qpos[0])),abs(float(d.qpos[1])))>4.1:reason='boundary';break
    top=bool(upper.all()and -float(d.qpos[0])<1.38 and -float(d.qpos[0])> -1.3);physical_top|=top
    stable=top and max(abs(pitch),abs(roll))<math.radians(25)and np.linalg.norm(ang[:2])<1.5 and abs(float(d.qvel[2]))<.25 and not badcontact and entry is not None and .1<=entry<=.6 and speedmax<=.6
    hold=hold+.02 if stable else 0.;success=hold>=.4-1e-7
    trace.append([age,*d.qpos[:3],vx,entry if entry is not None else -1.,speedmax,pitch,roll,float(upper[0]),float(upper[1]),hold,maxclosure])
    if success:reason='qualified_success';break
   row=dict(height_m=h,seed=seed,start=[sx,sy,syaw],command_vx=.4,entry_speed_m_s=entry,maximum_approach_ascent_speed_m_s=speedmax,success=success,ever_both_wheels_and_body_on_top=physical_top,each_wheel_landed=landed,hold_s=hold,reason=reason,completed_s=k*.02,maximum_closure_m=maxclosure);rows.append(row);arrays['h%03d_seed%d'%(round(h*1000),seed)]=np.asarray(trace)
   (E/'PROGRESS.json').write_text(json.dumps(dict(completed=len(rows),last=row),indent=2)+'\n')
  finally:s.close();del s,e,m,d;gc.collect()
summary={str(h):dict(passed=sum(r['success']for r in rows if r['height_m']==h),requested=sum(r['height_m']==h for r in rows),actual_top=sum(r['ever_both_wheels_and_body_on_top']for r in rows if r['height_m']==h))for h in heights}
np.savez_compressed(E/'trajectory.npz',**arrays)
result=dict(model=str(show.CKPT),sha256=show.EXPECTED,rows=rows,by_height=summary,wall_seconds=time.time()-wall,no_optimizer=True,protocol='Frozen9single-step heights x5starts;0.4m/s command;actual entry0.1-0.6m/s and peak<=0.6;both wheel actual upper contact>5N,body crosses,25deg/1.5rad/s and0.4s hold;native100Hzleg/400Hzwheel/50Hzpolicy;2mm diagnostic only;>1mcatastrophic and0.2s ordinary guards;nominal MuJoCo analogue,not native fullDR graduation')
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)

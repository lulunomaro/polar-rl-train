"""Frozen 200mm continuous stair evaluation; five varied starts, actual wheel landings."""
from pathlib import Path
import argparse,sys,json,hashlib,time,importlib.util,types,shutil,math,xml.etree.ElementTree as ET
import torch,numpy as np,mujoco
p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--out',required=True);p.add_argument('--highest-command-only',action='store_true');a=p.parse_args();torch.set_num_threads(1)
T=Path(__file__).resolve().parent;R=T.parents[2];D=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112';E=Path(a.out).resolve();E.mkdir(parents=True,exist_ok=False);B=E/'scene_assets';(B/'tiles').mkdir(parents=True)
source=np.load(D/'viewer/tiles/r03_c00.npz');vertices=source['vertices'].copy();vertices[:,2]*=.2/float(np.unique(vertices[:,2])[1]);np.savez_compressed(B/'tiles/r00_c00.npz',vertices=vertices,faces=source['faces'])
spec=importlib.util.spec_from_file_location('fixed200_show',D/'viewer/showcase.py');show=importlib.util.module_from_spec(spec);spec.loader.exec_module(show);show.B=B;show.CKPT=Path(a.model).resolve();show.EXPECTED=hashlib.sha256(show.CKPT.read_bytes()).hexdigest()
sys.path.insert(0,str(T/'manual_replay'))
from replay_supported_guards import replay_step
show.Replay.step=replay_step(show.Simulation,show.SafetyStop,duration_steps=10,event_dir=E/'reset_events')
starts=[(-3.9,0.,0.),(-3.75,-.12,-.03),(-3.6,.12,.03),(-3.99,.06,-.04),(-3.8,-.06,.04)];rows=[];arrays={};wall=time.time()
cases=[('whole_low040','up',.42,.4),('whole_low060','up',.42,.6),('supported_low040','up',.42,.4),('supported_late040','up',.42,.4)]
for case,direction,height,speed in cases:
 for seed,(sx,sy,syaw) in enumerate(starts[:3] if case=='supported_late040' else starts[:2]):
  if case.startswith('whole_oblique_'):
   syaw=math.radians(float(case.rsplit('_',1)[1]));sy=(seed-2)*.04+(sx+1.1)*math.tan(syaw)
  s=show.Replay(direction=direction);s.args.vx=speed;e=s.env;m=e.m;d=e.d;wb=[m.body(n).id for n in ['left_wheel_link','right_wheel_link']];x0=sx if case.startswith('whole') else (-2.35+(seed-2)*.04 if case.startswith('mid') else .25+(seed-2)*.04)
  d.qpos[:3]=[x0,sy,s.ground(x0,sy)+e.bank_z];d.qpos[3:7]=[math.cos(syaw/2),0.,0.,math.sin(syaw/2)];d.qvel[:]=0.;mujoco.mj_forward(m,d);s.reset_count=1;s.reason='';s.z=float(e.z)-s.ground(x0,sy)
  if case.startswith('supported'):
   bank=json.loads((T/'support/mod4v3_ppo_v1/rearward_mount_bank.json').read_text())['poses'][seed+3 if case=='supported_late040' else seed]
   for name,value in bank['joint_positions'].items():d.qpos[m.joint(name).qposadr[0]]=value
   d.qpos[:7]=[-2.9+bank['root_inward_of_edge_m'],0.,.3785,1.,0.,0.,0.];d.qvel[:]=0.;mujoco.mj_forward(m,d);e.state();syaw=0.
  x0,sy=map(float,d.qpos[:2]);landing={};wall_contact_yaw={};wall_contact_speed={};trace=[];hold=0.;success=False;maxclosure=0.
  def physics(env,act):
   global maxclosure
   act=act.clamp(-env.action_clip,env.action_clip)
   for j in range(env.decim):
    tau=env._torque(act).detach().numpy().reshape(-1)
    if j%4==0:d.ctrl[env.act_ids[:4]]=tau[:4]
    d.ctrl[env.act_ids[4:]]=tau[4:];mujoco.mj_step(m,d)
    if not np.isfinite(d.qpos).all() or not np.isfinite(d.qvel).all():raise show.SafetyStop('nonfinite')
    cl=max(float(np.linalg.norm(d.site_xpos[u]-d.site_xpos[v])) for u,v in s.pairs);s.closure=cl;maxclosure=max(maxclosure,cl)
    if cl>.002:raise show.SafetyStop('closure>2mm')
    if d.time>=3. or case.startswith('supported'):
     for level in [1,2]:
      supported=set()
      for ci in range(d.ncon):
       c=d.contact[ci];g1,g2=int(c.geom1),int(c.geom2);terrain=m.geom(g1).name if m.geom(g1).name.startswith('step_') else m.geom(g2).name
       if terrain!='step_'+str(level):continue
       robot=g2 if m.geom(g1).name==terrain else g1;bid=int(m.geom_bodyid[robot])
       if bid not in wb and not m.body(bid).name.startswith(('left_guide','right_guide')):continue
       cf=np.zeros(6);mujoco.mj_contactForce(m,d,ci,cf);normal=np.asarray(c.frame).reshape(3,3)[0]*(1 if m.geom(g1).name==terrain else -1)
       if cf[0]>5 and abs(normal[0])>.7 and level not in wall_contact_yaw:
        axis=np.zeros(3);mujoco.mju_rotVecQuat(axis,np.array([1.,0.,0.]),d.qpos[3:7]);wall_contact_yaw[level]=float(math.degrees(math.atan2(axis[1],axis[0])));wall_contact_speed[level]=float(np.dot(d.qvel[:3],axis))
       if bid in wb and cf[0]>5 and normal[2]>.7:supported.add(bid)
      if len(supported)==2 and level not in landing:landing[level]=float(d.time-.0025)
   env.a_prev=act.detach().to(env.device);return env.state()
  e.step=types.MethodType(physics,e)
  try:
   for k in range(1500):
    s.set_height(height if case.startswith('supported') else .28+(height-.28)*min(k/100.,1.));s.step({'w'} if k>=150 or case.startswith('supported') else set());x,y=map(float,d.qpos[:2]);w=d.xpos[wb];on_top=bool((np.abs(w[:,0])<1.4).all() and (np.abs(w[:,1])<1.4).all() and (w[:,2]>.3925).all());goal=(2 in landing and on_top and float(d.qpos[2])-.4>=.32 and float(s.cos_tilt)>.8) if direction=='up' else bool(x>3.6 and s.ground(x,y)<.02)
    hold=hold+.02 if goal and s.reset_count==1 else 0.;success=bool(hold>=.3)
    trace.append([k*.02,x,y,float(d.qpos[2]),float(e.vx),float(s.z),float(s.cos_tilt),float(w[:,2].mean()),s.closure,*s.a_prev[0].tolist()])
    if success or s.reset_count>1:break
   row=dict(case=case,seed=seed,height=height,speed=speed,start=[x0,sy,syaw],success=success,resets=s.reset_count-1,reason=s.reason,first_landing_s=landing.get(1),second_landing_s=landing.get(2),first_to_second_s=(landing[2]-landing[1]) if direction=='up' and 1 in landing and 2 in landing else None,completed_s=k*.02,max_closure_m=maxclosure,whole_course=case.startswith('whole'),diagnostic_only=case.startswith('mid'))
   before_motion=[t[5] for t in trace if 2.<=t[0]<3.];row['first_riser_contact_forward_speed_m_s']=wall_contact_speed.get(1);row['second_riser_contact_forward_speed_m_s']=wall_contact_speed.get(2);row['actual_forward_speed_peak_m_s']=max(abs(t[4]) for t in trace) if trace else None;row['first_riser_contact_yaw_deg']=wall_contact_yaw.get(1);row['second_riser_contact_yaw_deg']=wall_contact_yaw.get(2);row['actual_oblique_success']=bool(success and wall_contact_yaw.get(1) is not None and abs(wall_contact_yaw[1])>=10.);row['pre_motion_height_mean_m']=float(np.mean(before_motion)) if before_motion else None
   rows.append(row);arrays[case+'_seed'+str(seed)]=np.asarray(trace);(E/'PROGRESS.json').write_text(json.dumps(dict(completed=len(rows),last=row)))
  finally:s.close()
summary={}
for case,_,_,_ in cases:
 part=[r for r in rows if r['case']==case];tt=[r['first_to_second_s'] for r in part if r['success'] and r['first_to_second_s'] is not None];summary[case]=dict(passed=sum(r['success'] for r in part),actual_oblique_passed=sum(r['actual_oblique_success'] for r in part),requested=len(part),mean_first_to_second_s=float(np.mean(tt)) if tt else None)
np.savez_compressed(E/'trajectory.npz',**arrays);result=dict(model=str(show.CKPT),sha256=show.EXPECTED,rows=rows,summary=summary,whole_passed=sum(r['success'] for r in rows if r['whole_course']),whole_requested=sum(r['whole_course'] for r in rows),assisted_first_passed=sum(r['first_landing_s'] is not None for r in rows if r['case']=='supported_low040'),late_assisted_first_passed=sum(r['first_landing_s'] is not None for r in rows if r['case']=='supported_late040'),late_assisted_requested=sum(r['case']=='supported_late040' for r in rows),highest_command_only=a.highest_command_only,protocol='Video-supported low-speed task;0.4/0.6m/s commands, two starts each;two early assisted0.4 starts and three late mounted0.4 starts reported separately;upper-tread chassis/guide normal support allowed;standing>=0.32m above top required;30s first physical episode;Level3 horizontal geometry;200mm x2;whole/mid/descent separate;actual pair wheel tread contact>5N and0.3s on top;wheel-ground height;native terrain-fall;40deg/10endpoints;separate1Ncontact/tilt dwell;edge-guide exemption;2mmguard;nominal MuJoCo contact analogue only;protocolV4-specialist;actual touch velocity and peak forward speed reported;original fast straight5/oblique20 evaluated separately',wall_seconds=time.time()-wall,no_optimizer=True)
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(sha256=show.EXPECTED,summary=summary,whole_passed=result['whole_passed'],whole_requested=result['whole_requested'])),flush=True)

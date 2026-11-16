"""Zero-optimizer transfer probe: source leg motion -> MOD4 closed-chain poses -> native PD actions."""
from pathlib import Path
import sys,json,time,math,types,hashlib,xml.etree.ElementTree as ET,gc
import numpy as np,torch,mujoco as mj
from mod4_retarget import Mod4Retarget,PPO_ORDER,PLANT,PIN,T,R
D=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112'
sys.path.insert(0,str(D/'runtime/core'))
from args_for import args_for
from play_ppo_flatv1_control import Simulation
SOURCE=Path(r'D:\claude2\fangzhen\playgrounds\Serial_Leg_Simulation')
SOURCE_DATA=json.loads((T/'source_demonstrations_20cm_dynamics/RESULT.json').read_text())
COL={n:i for i,n in enumerate(SOURCE_DATA['columns'])}
A=np.load(T/'source_demonstrations_20cm_dynamics/trajectories.npz')
OUT=T/'mod4_transfer_20cm_r5';OUT.mkdir(exist_ok=False)
CKPT=R/'deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt'
assert hashlib.sha256(CKPT.read_bytes()).hexdigest()=='c874a1afa9adc33c3fa806d098fc135a76d3e9ecdf411d0ca4ab879696b18617'
torch.set_num_threads(1)
sm=mj.MjModel.from_xml_path(str(SOURCE/'mjcf/bigeye_flat.xml'));sd=mj.MjData(sm);mj.mj_forward(sm,sd)
source_base=sm.body('base').id
source_hips=np.stack([sd.xanchor[sm.joint(s+'_rear_hip_joint').id]-sd.xpos[source_base]for s in ['left','right']])

def source_task(rows):
 values=[]
 for row in rows:
  rotation=np.zeros(9);mj.mju_quat2Mat(rotation,row[4:8]);rotation=rotation.reshape(3,3)
  wheel=row[[COL[f'wheel_xyz_{i}']for i in range(6)]].reshape(2,3)
  vector=(wheel-row[1:4])@rotation-source_hips
  values.append(np.r_[np.linalg.norm(vector,axis=1),np.arctan2(vector[:,0],-vector[:,2])])
 return np.asarray(values)

def observation(sim,vx,height):
 q,qd=sim._current_active();rot=torch.tensor(sim.env.d.xmat[sim.env.base_id].reshape(3,3),dtype=torch.float32)
 gravity=rot.T@torch.tensor([0.,0.,-1.]);jp=q-sim.default_active;jp[4:]=0.
 mode=torch.zeros(7);mode[0]=1.
 return torch.cat([torch.tensor([vx,0.,0.]),torch.tensor([height*5.]),torch.tensor(sim.env.d.qvel[3:6],dtype=torch.float32)*.5,gravity,jp,qd[:4]*.1,qd[4:]*.1,sim.a_prev[0],mode]).reshape(1,35)

def scene(height,name):
 original=PLANT/'mjcf/scene.xml';assert hashlib.sha256(original.read_bytes()).hexdigest()==PIN
 tree=ET.parse(original);root=tree.getroot();root.find('compiler').set('meshdir',str(original.parent/'assets'))
 if height:ET.SubElement(root.find('worldbody'),'geom',name='skill_teacher_platform',type='box',pos=f'2.1 0 {height/2}',size=f'.9 1.1 {height/2}',contype='1',conaffinity='2',friction='.9 .005 .0001')
 path=OUT/(name+'.xml');tree.write(path,encoding='utf-8',xml_declaration=True);return path

results=[];trajectories={};paired={}
for name,key,height,cmd,base_height,amplitude in [('step20_vmc_capture_force_balance_xminus','step20_auto_low',.20,.4,.40,1.),('step20_vmc_capture_force_balance_nominal','step20_auto_low',.20,.4,.40,1.),('step20_vmc_capture_force_balance_xplus','step20_auto_low',.20,.4,.40,1.)]:
 source=A[key];source_info=next(x for x in SOURCE_DATA['rows']if x['case']==key)
 phase_ids=source_info['phases'];active=[v for k,v in phase_ids.items()if k!='idle|idle']
 t0=(float(source[source[:,COL['wheel_xyz_0']]>=1.125,0].min()) if 'auto' in key else float(source[np.isin(source[:,-1],active),0].min())-.10)
 ref=source[source[:,0]>=t0].copy();source_generalized=A[key+'_task_force'][source[:,0]>=t0].copy();source_generalized[:,:,1]*=-1.;ref_time=ref[:,0]-ref[0,0];task=source_task(ref)
 args=args_for(str(CKPT));args.xml=str(scene(height,name));sim=Simulation(args);e=sim.env;m=e.m;d=e.d
 root_offset=-.06 if 'xminus' in name else .06 if 'xplus' in name else 0.
 d.qpos[0]+=root_offset;mj.mj_forward(m,d)
 e.dt=.0025;e.decim=8;m.opt.timestep=.0025
 maxclosure=0.;closed=False
 pairs=[(m.site(x.get('site1')).id,m.site(x.get('site2')).id)for x in ET.parse(args.xml).getroot().findall('equality/connect')]
 def physics(env,action):
  global maxclosure
  action=action.clamp(-env.action_clip,env.action_clip)
  for j in range(8):
   tau=env._torque(action).detach().numpy().reshape(-1)
   if j%4==0:d.ctrl[env.act_ids[:4]]=tau[:4]
   d.ctrl[env.act_ids[4:]]=tau[4:];mj.mj_step(m,d)
   if not np.isfinite(d.qpos).all()or not np.isfinite(d.qvel).all():raise RuntimeError('nonfinite')
   cl=max(np.linalg.norm(d.site_xpos[u]-d.site_xpos[v])for u,v in pairs);maxclosure=max(maxclosure,float(cl))
   if cl>1.:raise RuntimeError('catastrophic closure>1m')
  env.a_prev=action.detach();return env.state()
 e.step=types.MethodType(physics,e)
 tire=[m.geom(n).id for n in ['left_tire','right_tire']];wb=[int(m.geom_bodyid[x])for x in tire]
 platform=mj.mj_name2id(m,mj.mjtObj.mjOBJ_GEOM,'skill_teacher_platform')
 hip=[m.joint(s+'_rear1_joint').id for s in ['left','right']]
 ik=None;qrefs=None;force_actions=None;wheel_bias=None;start_at=None;eq_action=None;first_top=None;air=False;max_z=float(d.qpos[2]);hold=0.;reason='timeout';numeric_error=None
 rows=[];obs_rows=[];act_rows=[];skill_rows=[];state_rows=[];velocity_rows=[];fit_errors=[];torque_peaks=np.zeros(6);pose_bad=0
 try:
  for k in range(600):
   age=k*.02;speed=cmd if age>=2. else 0.
   wheel=d.geom_xpos[tire].copy()
   edge_contact=False
   if height:
    for ci in range(d.ncon):
     hit=d.contact[ci]
     if platform in (int(hit.geom1),int(hit.geom2)):
      f=np.zeros(6);mj.mj_contactForce(m,d,ci,f)
      if f[0]>5.:edge_contact=True
   if start_at is None and ((not height and age>=2.)or(height and 'auto' in key and edge_contact)or(height and 'jump' in key and age>=2. and float(d.qpos[0])>=.95)):
    start_at=age;ik=Mod4Retarget();ik.d.qpos[ik.qadr]=d.qpos[ik.qadr];ik.q=d.qpos[ik.qadr].copy()
    rotation=d.xmat[e.base_id].reshape(3,3)
    vector=(d.xpos[wb]-np.stack([d.xanchor[j]for j in hip]))@rotation
    baseL=np.linalg.norm(vector,axis=1);baseTheta=np.arctan2(vector[:,0],-vector[:,2])
    qrefs=[];force_actions=[];wheel_bias=[];baseline_vmc=None
    baseline_force=np.median(ref[:max(1,min(4,len(ref))),[COL['left_force_z'],COL['right_force_z']]],axis=0)
    mass_ratio=float(m.body_mass.sum()/sm.body_mass.sum())
    for ri,target in enumerate(task):
     L=np.clip(baseL+amplitude*(target[:2]-task[0,:2]),.13,.38)
     theta=baseTheta+amplitude*(target[2:]-task[0,2:])
     fitted=ik.fit(L,theta);q0=fitted['active_q'];qrefs.append(q0);fit_errors.append(fitted['target_error_m'])
     phase_name=next(k for k,v in phase_ids.items()if v==int(ref[ri,-1]))
     pulse=('thrust' in phase_name) if 'jump' in key else (ref_time[ri]<.80)
     tau_ff=np.zeros(4)
     if 'vmc' in name:
      qL=ik.fit(L+.0005,theta)['active_q'];qTheta=ik.fit(L,theta+.0005)['active_q'];ik.fit(L,theta)
      mapped=np.zeros(4)
      for side in range(2):
       ids=slice(2*side,2*side+2);dq=np.column_stack(((qL[ids]-q0[ids])/.0005,(qTheta[ids]-q0[ids])/.0005))
       J=np.linalg.pinv(dq)
       mapped[ids]=J.T@(source_generalized[ri,side]*mass_ratio)
      if baseline_vmc is None:baseline_vmc=mapped.copy()
      tau_ff=mapped-baseline_vmc
     force_actions.append(tau_ff/30.)
     wheel_bias.append((float(ref[ri,COL['root_qvel_0']])-cmd)/(.0625*10.) if height else 0.)
    qrefs=np.asarray(qrefs);force_actions=np.asarray(force_actions);wheel_bias=np.asarray(wheel_bias)
   control_height=.24 if 'capture' in name and start_at is not None and age-start_at>ref_time[-1] else base_height
   x=observation(sim,speed,control_height)
   with torch.no_grad():action=sim.actor(x).clamp(-6.,6.)
   active_now=False
   if start_at is not None:
    elapsed=age-start_at
    if eq_action is None:eq_action=action[0,:4].numpy().copy()
    if elapsed<=ref_time[-1]:
     qref=np.array([np.interp(elapsed,ref_time,qrefs[:,j])for j in range(4)])
     extra=np.array([np.interp(elapsed,ref_time,force_actions[:,j])for j in range(4)])
     action[0,:4]=torch.tensor(eq_action+(qref-qrefs[0])/.5+extra,dtype=torch.float32)
     if height and 'auto' in key and 'balance' not in name:
      source_tau=np.array([np.interp(elapsed,ref_time,ref[:,COL[f'source_torque_{j}']])for j in [4,5]])
      traction_tau=source_tau*(float(m.body_mass.sum()/sm.body_mass.sum()))*(.0625/.06)
      wheel_velocity=d.qvel[e.dadr_all[e.wheel_ids]]
      if 'fused' in name:
       native_tau=.6*(action[0,4:].numpy()*10.-wheel_velocity)
       traction_tau=traction_tau+.5*native_tau
      action[0,4:]=torch.tensor((wheel_velocity+traction_tau/.6)/10.,dtype=torch.float32)
     active_now=True
   action=action.clamp(-6.,6.)
   student_x=x[0].numpy().copy();student_x[3]=base_height*5.
   if height:
    student_x[-7:]=[0.,1.,0.,0.,0.,0.,0.]
   elif start_at is not None:
    student_x[-7:]=[0.,0.,0.,0.,1.,.10*5.,age-start_at]
   obs_rows.append(student_x);act_rows.append(action[0].numpy().copy());skill_rows.append(active_now)
   e.step(action[:,sim.ppo_to_env]);sim.a_prev=action.detach().clone()
   torque_peaks=np.maximum(torque_peaks,np.abs(d.ctrl[e.act_ids]))
   rotation=d.xmat[e.base_id].reshape(3,3);pitch=math.asin(float(np.clip(-rotation[2,0],-1,1)));roll=math.atan2(float(rotation[2,1]),float(rotation[2,2]))
   ground=np.zeros(2,dtype=bool);upper=np.zeros(2,dtype=bool)
   for ci in range(d.ncon):
    contact=d.contact[ci];g1,g2=int(contact.geom1),int(contact.geom2);b1,b2=int(m.geom_bodyid[g1]),int(m.geom_bodyid[g2])
    for side,body in enumerate(wb):
     other=g1 if b2==body and b1==0 else g2 if b1==body and b2==0 else -1
     if other<0:continue
     cf=np.zeros(6);mj.mj_contactForce(m,d,ci,cf);normal=(1. if b2==body else -1.)*np.asarray(contact.frame).reshape(3,3)[0]
     if cf[0]>5. and normal[2]>.7:
      ground[side]=True
      if other==platform and abs(float(contact.pos[2])-height)<.012:upper[side]=True
   wheel=d.geom_xpos[tire];air|=bool(not ground.any()and np.all(wheel[:,2]>.0825));max_z=max(max_z,float(d.qpos[2]))
   physical=bool(upper.all()and 1.32<d.qpos[0]<2.85)
   if physical and first_top is None:first_top=age
   ready=physical if height else air and ground.all()and start_at is not None and age-start_at>ref_time[-1]
   stable=ready and max(abs(pitch),abs(roll))<math.radians(25)and np.linalg.norm(d.qvel[3:5])<1.5 and abs(float(d.qvel[2]))<.25
   hold=hold+.02 if stable else 0.
   pose_bad=pose_bad+1 if max(abs(pitch),abs(roll))>math.radians(40)else 0
   rows.append([age,*d.qpos[:3],pitch,roll,*wheel.reshape(-1),*ground.astype(float),*upper.astype(float),active_now,hold,maxclosure])
   state_rows.append(d.qpos.copy());velocity_rows.append(d.qvel.copy())
   if hold>=.4-1e-8:reason='qualified_stable_landing';break
   if pose_bad>=10:reason='orientation>40deg_0.2s';break
   if np.abs(d.qpos[:2]).max()>4.1:reason='boundary';break
 except Exception as ex:reason='probe_error';numeric_error=str(ex)
 finally:
  result=dict(case=name,source_case=key,root_start_offset_m=root_offset,success=reason=='qualified_stable_landing',reason=reason,error=numeric_error,source_reference_started_at=start_at,physical_top=first_top is not None,first_top_s=first_top,both_wheels_airborne=air,root_peak_z=max_z,hold_s=hold,max_closure_m=maxclosure,max_IK_target_error_m=max(fit_errors,default=0.),torque_abs_peak=torque_peaks.tolist(),frames=len(rows),PPO_updates=0,actor_changed=False,actor_input=35,action_output=6,source_FSM_phase_is_teacher_only=True,existing_mode_slots_used=True,jump_clock_is_elapsed_from_user_request=True,jump_intent_not_yet_distilled=True,temporary_teacher_capture_stance_m=.24,public_stance_command_m=base_height)
  results.append(result);trajectories[name]=np.asarray(rows);trajectories[name+'_qpos']=np.asarray(state_rows);trajectories[name+'_qvel']=np.asarray(velocity_rows);paired[name+'_obs']=np.asarray(obs_rows);paired[name+'_actions']=np.asarray(act_rows);paired[name+'_skill_mask']=np.asarray(skill_rows)
  (OUT/'PROGRESS.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(result),flush=True)
  sim.close();del sim,e,m,d;gc.collect()
np.savez_compressed(OUT/'trajectories.npz',**trajectories)
np.savez_compressed(OUT/'paired_student_obs_actions.npz',**paired)
(OUT/'RESULT.json').write_text(json.dumps(dict(rows=results,admitted=[x['case']for x in results if x['success']],method='Full source generalized radial force/swing moment obtained from source Jacobian and source motor+gas efforts, then mapped through MOD4 Jacobian; task-space motion retarget and actual MOD4 execution; no copied source torques;35/78/6 unchanged; no PPO updates; existing7mode slots encode stair intent or jump intent/target/elapsed request clock; source FSM phase is not an added actor input; learned policy still requires independent validation',source_reference=str(T/'source_demonstrations_20cm_dynamics/RESULT.json')),indent=2)+'\n')

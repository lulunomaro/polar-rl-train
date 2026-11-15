"""Frozen-policy causal replay; action holds and command ramps are diagnostic interventions only."""
from pathlib import Path
import argparse,json,hashlib,sys,importlib.util,types,time,gc,traceback
import numpy as np
import torch,mujoco
T=Path(__file__).resolve().parent;R=T.parents[2];OLD=T.parent/'MOD4V3_PITCH_RATE_SQUARE_40M_20261115';D=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112'
p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');p.add_argument('--model');p.add_argument('--label',default='actuation_grid');a=p.parse_args();torch.set_num_threads(1)
E=T/'evidence'/a.label;E.mkdir(exist_ok=False);B=E/'scene_assets';(B/'tiles').mkdir(parents=True)
spec=importlib.util.spec_from_file_location('causal_showcase',D/'viewer/showcase.py');show=importlib.util.module_from_spec(spec);spec.loader.exec_module(show)
for level,family in [(9,'random_uniform_for_rm'),(0,'plane_for_rm')]:
 col=show.COLS[family];name=f'r{level:02d}_c{col:02d}.npz';(B/'tiles'/name).write_bytes((D/'viewer/tiles'/name).read_bytes())
show.B=B;show.CKPT=Path(a.model).resolve() if a.model else OLD/'weights/parent_comprehensive.pt'
if not show.CKPT.exists():
 candidates=list((OLD/'weights').glob('*parent*'));print('PARENT_FILES',candidates);raise FileNotFoundError(show.CKPT)
show.EXPECTED=hashlib.sha256(show.CKPT.read_bytes()).hexdigest()
sys.path.insert(0,str(OLD/'manual_replay'));from replay_supported_guards import replay_step
show.Replay.step=replay_step(show.Simulation,show.SafetyStop,duration_steps=10,event_dir=E/'reset_events')
rows=[];arrays={};switches=[];wall=time.time()
variants=[f'leg_{leg_scale}:wheel_{wheel_delta}' for leg_scale in [.5,1.,1.5] for wheel_delta in [-.5,0.,.5,1.]]
cases=[(family,level,h,v) for family,level in [('random_uniform_for_rm',9),('plane_for_rm',0)] for h in ([.28,.4] if a.full else [.4]) for v in ([1.2,2.2] if a.full else [2.2])]
for family,level,height,speed in cases:
 for variant in variants:
  leg_scale=float(variant.split(':')[0].split('_')[1]);wheel_delta=float(variant.split(':')[1].split('_')[1])
  s=show.Replay(level=level,family=family,direction='up');e=s.env;m=e.m;d=e.d
  x0=-.8;y0=-.1 if speed<2. else .1;d.qpos[:3]=[x0,y0,s.ground(x0,y0)+e.bank_z];d.qpos[3:7]=[1,0,0,0];d.qvel[:]=0.;mujoco.mj_forward(m,d);e.state();s.reset_count=1;s.reason=''
  record={};before_stop=None;pre_action=None;step_index=0;trace=[];subtrace=[];maxclosure=0.;effective=speed
  def actor_hook(module,inputs,output):
   global pre_action,before_stop
   obs=inputs[0];record['obs']=obs.detach().cpu().numpy()[0].copy();record['raw_action']=output.detach().cpu().numpy()[0].copy()
   if step_index==150:
    with torch.no_grad():
     oldobs=obs.clone();oldobs[:,0]=speed;oldaction=module.forward(oldobs)
    before_stop=dict(obs=record['obs'].tolist(),raw_new_command_action=output.detach().cpu().numpy()[0].tolist(),same_state_old_command_action=oldaction.detach().cpu().numpy()[0].tolist(),previous_executed_action=pre_action.detach().cpu().numpy()[0].tolist())
   result=output
   if 150<=step_index<155 and variant in ['hold_legs_100ms','hold_wheels_100ms']:
    result=output.clone()
    if variant=='hold_legs_100ms':result[:,:4]=held[:,:4]
    else:result[:,4:]=held[:,4:]
   if 150<=step_index<155:
    result=result.clone();result[:,:4]=held[:,:4]+leg_scale*(result[:,:4]-held[:,:4]);result[:,4:]+=wheel_delta
   record['executed_action']=result.detach().cpu().numpy()[0].copy();pre_action=result.detach().clone();return result
  hook=s.actor.register_forward_hook(actor_hook)
  def physics(env,act):
   global maxclosure
   act=act.clamp(-env.action_clip,env.action_clip);taus=[]
   for j in range(env.decim):
    tau=env._torque(act).detach().numpy().reshape(-1)
    if j%4==0:d.ctrl[env.act_ids[:4]]=tau[:4]
    d.ctrl[env.act_ids[4:]]=tau[4:];taus.append(d.ctrl[env.act_ids].copy());mujoco.mj_step(m,d)
    if not np.isfinite(d.qpos).all() or not np.isfinite(d.qvel).all():raise show.SafetyStop('nonfinite')
    cl=max(float(np.linalg.norm(d.site_xpos[u]-d.site_xpos[v]))for u,v in s.pairs);maxclosure=max(maxclosure,cl);s.closure=cl
    if cl>.002:raise show.SafetyStop('closure>2mm')
    vel=np.zeros(6);mujoco.mj_objectVelocity(m,d,mujoco.mjtObj.mjOBJ_BODY,e.base_id,vel,1)
    if 145<=step_index<165:subtrace.append([step_index*.02+(j+1)*.0025,float(vel[1]),*d.ctrl[env.act_ids].tolist(),float(d.qacc[4]),float(d.qfrc_actuator[4]),float(d.qfrc_constraint[4])])
   record['tau_mean']=np.mean(taus,axis=0);record['tau_first']=taus[0];env.a_prev=act.detach().to(env.device);return env.state()
  e.step=types.MethodType(physics,e)
  try:
   for k in range(250):
    step_index=k;age=k*.02;requested=speed if 2.<=age<3. else 0.
    if k==150:held=pre_action.clone()
    command=requested
    if age>=3. and variant.startswith('brake_ramp_'):
     limit=4. if variant=='brake_ramp_4mps2' else 8.;effective=max(0.,effective-limit*.02);command=effective
    s.args.vx=abs(command) if command else speed;s.cmd_vx=command;s.cmd_vy=0.;s.cmd_wz=0.;s.set_height(height)
    s.step({'w'}if command>0 else set())
    rotation=np.asarray(d.xmat[e.base_id]).reshape(3,3);gravity=rotation.T@np.array([0.,0.,-1.]);pitch=float(np.arctan2(gravity[0],np.linalg.norm(gravity[1:])))
    vel=np.zeros(6);mujoco.mj_objectVelocity(m,d,mujoco.mjtObj.mjOBJ_BODY,e.base_id,vel,1)
    trace.append([age,pitch,float(vel[1]),requested,command,float(e.vx),float(d.qpos[0]),float(d.qpos[2]),s.closure,float(s.reset_count-1),*record['raw_action'],*record['executed_action'],*record['tau_mean'],*record['tau_first']])
    if s.reset_count>1:break
   z=np.asarray(trace);brake=(z[:,0]>=3.)&(z[:,0]<3.8);start=(z[:,0]>=2.)&(z[:,0]<2.8);allstop=(z[:,0]>=3.)
   switch=z[np.argmin(abs(z[:,0]-3.))];prior=z[np.argmin(abs(z[:,0]-2.98))]
   row=dict(family=family,level=level,height=height,speed=speed,variant=variant,reset=s.reset_count-1,reason=s.reason,braking_pitch_peak_deg=float(np.degrees(abs(z[brake,1])).max()),braking_rate_peak_rad_s=float(abs(z[brake,2]).max()),startup_pitch_peak_deg=float(np.degrees(abs(z[start,1])).max()),vx_at_stop=float(prior[5]),vx_after_020s=float(z[np.argmin(abs(z[:,0]-3.2)),5]),vx_after_050s=float(z[np.argmin(abs(z[:,0]-3.5)),5]),max_closure_m=maxclosure,first_stop_action_delta=(switch[16:22]-prior[16:22]).tolist(),first_stop_tau=switch[28:34].tolist())
   name=family+f'_h{height}_v{speed}_{variant}';arrays[name]=z;arrays[name+'_substep']=np.asarray(subtrace);switches.append(dict(case=name,**(before_stop or {})));rows.append(row)
   (E/'PROGRESS.json').write_text(json.dumps(dict(completed=len(rows),total=len(cases)*len(variants),last=row),indent=2)+'\n',encoding='utf8');print(json.dumps(row),flush=True)
  finally:hook.remove();s.close();del s,e,m,d;gc.collect()
np.savez_compressed(E/'trajectories.npz',**arrays)
result=dict(model=str(show.CKPT),sha256=show.EXPECTED,rows=rows,switches=switches,wall_seconds=time.time()-wall,no_optimizer_updates=True,columns=['time','pitch','omega_y','requested_vx','effective_vx','actual_vx','root_x','root_z','closure','resets']+['raw_action_'+str(i) for i in range(6)]+['executed_action_'+str(i) for i in range(6)]+['tau_mean_'+str(i) for i in range(6)]+['tau_first_'+str(i) for i in range(6)],protocol='Frozen referenced MOD4v3; exact first-stop counterfactual states through2.98s;2.5ms physics,50Hz policy,100Hz legs,400Hz wheels,2mm guard. Finite actuator intervention grid; no optimizer or policy training; outputs exist only in this diagnostic process, not deployment or ongoingPPO. First stop only, same nominal maps; no fullDR claim.')
(E/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('COMPLETE',len(rows),flush=True)

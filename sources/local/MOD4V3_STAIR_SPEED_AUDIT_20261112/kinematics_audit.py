"""Frozen actor speed-response and control-channel audit; no training/source mutation."""
from pathlib import Path
import sys,json,time,hashlib,math,xml.etree.ElementTree as ET
import numpy as np,torch
T=Path(__file__).resolve().parent;R=T.parents[2];S=R/'sources/local/MOD4V3_SCUT_STAIR_LIFT_20M_20261112';sys.path.insert(0,str(R/'sources/local/MOD4V3_STEP7_DELAY_DIAG_20261110'))
import replay_delay_diagnostic as replay
from eval_flatv2_final import args_for
torch.set_num_threads(1);E=T/'evidence';E.mkdir(exist_ok=True)
MODELS={'parent':R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/model/training_checkpoint.pt','first':S/'weights/model_first_complete.pt','005m':S/'weights/model_005m.pt','010m':S/'weights/model_010m.pt'}
actors={};identities={}
for name,p in MODELS.items():
 d=torch.load(p,map_location='cpu',weights_only=False);layers=[]
 for i,(x,y) in enumerate(zip((35,256,128,64),(256,128,64,6))):
  layers.append(torch.nn.Linear(x,y))
  if i<3:layers.append(torch.nn.ELU())
 a=torch.nn.Sequential(*layers);a.load_state_dict({k.removeprefix('mlp.'):v for k,v in d['actor_state_dict'].items() if k.startswith('mlp.')});a.eval();actors[name]=a
 identities[name]=dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),iteration=d['iter'],std_param=d['actor_state_dict']['distribution.std_param'].tolist())
arrays={};results=[]
class Capture:
 def __init__(self,fn):self.fn=fn;self.inputs=[];self.outputs=[]
 def __call__(self,x):
  y=self.fn(x);self.inputs.append(x.detach().cpu().numpy()[0].copy());self.outputs.append(y.detach().cpu().numpy()[0].copy());return y

def run(model,fn,delay,commands,height=.28):
 sim=replay.Simulation(args_for(str(MODELS['parent'])));r=replay.DelayReplay(sim,delay,delay,'sent','sensors');capture=Capture(fn);r.actor=capture
 assert sim.env.dt==.0025 and sim.env.decim==8
 pairs=[(sim.env.m.site(c.get('site1')).id,sim.env.m.site(c.get('site2')).id) for c in ET.parse(sim.args.xml).getroot().findall('equality/connect')]
 original=sim.step;trace=[]
 def step(keys):
  value=original(keys);d=sim.env.d;rot=np.asarray(d.xmat[sim.env.base_id]).reshape(3,3);vw=np.asarray(d.qvel[:3]);vb=rot.T@vw;pitch=math.asin(float(np.clip(-rot[2,0],-1,1)));roll=math.atan2(rot[2,1],rot[2,2]);q,qd=sim._current_active();w=qd[4:].numpy();act=sim.a_prev[0].numpy();heading=np.r_[rot[:2,0]/np.linalg.norm(rot[:2,0]),0.]
  wheel_sign=np.array([np.dot(np.cross(d.xaxis[sim.env.joint_ids[n]],np.array([0.,0.,1.])),heading) for n in sim.active_names[4:]])
  clos=max(np.linalg.norm(d.site_xpos[a]-d.site_xpos[b]) for a,b in pairs)
  trace.append([float(sim.env.vx),float(vb[0]),float(vb[0]*math.cos(pitch)),pitch,roll,float(vw[2]),float(sim.z),float(sim.cos_tilt),float(sim.cmd_vx),*w.tolist(),*act.tolist(),float(np.mean(.0625*wheel_sign*w)),float(clos)])
  if clos>.002:raise RuntimeError('Flat replay closure guard exceeded2mm')
  return value
 sim.step=step
 try:
  for cmd in commands:
   capture.inputs=[];capture.outputs=[];trace=[]
   row=replay.run_case(sim,r,0,cmd,600,200,height=height)
   a=np.asarray(trace);tail=a[-200:];key=model+'_d'+str(delay)+'_v'+str(cmd)+'_h'+str(height)
   arrays[key+'_kinematics']=a;arrays[key+'_observation']=np.asarray(capture.inputs);arrays[key+'_actions']=np.asarray(capture.outputs)
   row.update(model=model,delay_ms=delay,height=height,physics_dt_s=sim.env.dt,PD_s=sim.env.dt*4,window_3p6to6_vx=float(a[180:300,0].mean()),tail_horizontal_vx=float(tail[:,0].mean()),tail_body_vx=float(tail[:,1].mean()),tail_reward_projected_vx=float(tail[:,2].mean()),tail_pitch_deg=float(np.rad2deg(tail[:,3]).mean()),tail_abs_pitch_deg=float(np.abs(np.rad2deg(tail[:,3])).mean()),tail_roll_deg=float(np.rad2deg(tail[:,4]).mean()),tail_vz=float(tail[:,5].mean()),tail_height=float(tail[:,6].mean()),tail_vx_std=float(tail[:,0].std()),tail_action_mean=tail[:,11:17].mean(0).tolist(),tail_wheel_speed_rad_s=tail[:,9:11].mean(0).tolist(),tail_wheel_rolling_estimate_m_s=float(tail[:,17].mean()),tail_projection_difference_m_s=float((tail[:,0]-tail[:,2]).mean()),max_closure_m=float(a[:,18].max()))
   results.append(row);(E/'SPEED_RESPONSE.json').write_text(json.dumps(dict(protocol='Fixed deterministic actors, same native2.5/10/20ms MuJoCo plant; seed0;12s/case, final4s; zero or5ms physical sensor/action delay; no optimizer',identities=identities,rows=results,kinematics_columns=['horizontal_heading_vx','body_vx','reward_projected_vx','pitch','roll','world_vz','height','cos_tilt','actual_command','wheel_L','wheel_R','a0','a1','a2','a3','a4','a5','rolling_velocity_estimate','closure']),indent=2),encoding='utf8')
   print(json.dumps({k:row[k] for k in ('model','delay_ms','cmd_vx','height','tail_horizontal_vx','tail_reward_projected_vx','tail_pitch_deg','tail_action_mean','reset_count')}),flush=True)
 finally:sim.close()

if __name__=='__main__':
 commands=(-2.2,-1.5,-1.,0.,1.,1.5,2.,2.2)
 for name,actor in actors.items():
  for delay in (0,5):run(name,actor,delay,commands)
 for name in ('parent','010m'):run(name,actors[name],5,(2.2,),height=.38)
 run('parent_legs_child_wheels',lambda x:torch.cat((actors['parent'](x)[:,:4],actors['010m'](x)[:,4:]),-1),5,(2.2,))
 run('child_legs_parent_wheels',lambda x:torch.cat((actors['010m'](x)[:,:4],actors['parent'](x)[:,4:]),-1),5,(2.2,))
 np.savez_compressed(E/'SPEED_RESPONSE_TRAJECTORIES.npz',**arrays)
 (E/'LOCAL_COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),cases=len(results),no_optimizer=True,source_mutations=False)),encoding='utf8')
 print('COMPLETE '+str(len(results)),flush=True)
 

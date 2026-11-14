"""Shared MuJoCo playback guards: wheel-ground height and native40deg/10-endpoint orientation dwell."""
from pathlib import Path
import ast,inspect,textwrap,json,time,os,math
import numpy as np

def policy_step_without_flat_reset(simulation):
 source=textwrap.dedent(inspect.getsource(simulation.step));tree=ast.parse(source);fn=tree.body[0];removed=0;body=[]
 for node in fn.body:
  if isinstance(node,ast.If) and any(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr=='reset_standing' for x in ast.walk(node)) and 'term_height' in ast.unparse(node.test):
   removed+=1;continue
  body.append(node)
 assert removed==1,'Expected exactly the legacy flat-only termination block'
 fn.body=body;fn.name='_advance_replay_policy';ast.fix_missing_locations(tree);scope=dict(simulation.step.__globals__);exec(compile(tree,'<replay-policy-without-flat-reset>','exec'),scope);return scope[fn.name]

def pose_state(sim):
 e=sim.env;d=e.d;m=e.m;w=d.xpos[[m.body(n).id for n in ('left_wheel_link','right_wheel_link')]];g=[sim.ground(float(v[0]),float(v[1])) for v in w];r=d.xmat[e.base_id].reshape(3,3);pitch=math.degrees(math.asin(float(np.clip(-r[2,0],-1,1))));roll=math.degrees(math.atan2(float(r[2,1]),float(r[2,2])))
 return dict(simulation_time_s=float(d.time),root_xyz=d.qpos[:3].tolist(),ground_under_root=sim.ground(float(d.qpos[0]),float(d.qpos[1])),ground_under_wheels=g,height_above_wheel_ground=float(e.z)-min(g),cos_tilt=float(e.cos_tilt),pitch_deg=pitch,roll_deg=roll,closure_m=float(sim.closure),wheel_xyz=w.tolist(),vx=float(e.vx))

def replay_step(simulation,safety_stop,*,duration_steps=10,event_dir=None):
 advance=policy_step_without_flat_reset(simulation);dest=Path(event_dir) if event_dir is not None else None
 if dest is not None:dest.mkdir(parents=True,exist_ok=True)
 def reset_with_reason(sim,reason,state=None):
  state=pose_state(sim) if state is None else state;sim.reason=reason;event=dict(epoch=time.time(),reason=reason,orientation_counter=getattr(sim,'_replay_tilt_steps',0),duration_steps=duration_steps,**state);sim.last_guard_reset=event
  print('MANUAL_GUARD_RESET '+json.dumps(event,ensure_ascii=False),flush=True)
  if dest is not None:(dest/(str(time.time_ns())+'_'+str(os.getpid())+'.json')).write_text(json.dumps(event,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  sim.reset_standing();sim._replay_tilt_steps=0;return sim.telemetry()
 def step(sim,pressed):
  if sim.paused:return sim.telemetry()
  now=float(sim.env.d.time)
  if now<=getattr(sim,'_replay_last_time',-1.):sim._replay_tilt_steps=0
  sim.just_reset=False
  try:advance(sim,pressed)
  except safety_stop as exc:return reset_with_reason(sim,str(exc))
  state=pose_state(sim);sim._replay_last_time=state['simulation_time_s'];sim.z=state['height_above_wheel_ground'];sim.cos_tilt=state['cos_tilt']
  bad=abs(state['pitch_deg'])>40. or abs(state['roll_deg'])>40.;sim._replay_tilt_steps=getattr(sim,'_replay_tilt_steps',0)+1 if bad else 0
  if sim.z<.18:return reset_with_reason(sim,'height_above_wheel_ground<0.18m',state)
  if sim._replay_tilt_steps>=duration_steps:return reset_with_reason(sim,'roll_or_pitch>40deg_for_10_consecutive_policy_steps',state)
  if abs(state['root_xyz'][0])>4.1 or abs(state['root_xyz'][1])>4.1:return reset_with_reason(sim,'tile_boundary',state)
  return sim.telemetry()
 return step

"""Bounded counterfactual: bypass only the viewer's extra instantaneous tilt rule; physical guards unchanged."""
from pathlib import Path
import types,json,time,math,traceback
import numpy as np,torch
T=Path(__file__).resolve().parent;OUT=T/'evidence/manual_tilt_counterfactual_20261113';OUT.mkdir(exist_ok=False)
path=T/'manual_replay/replay.py';source=path.read_text(encoding='utf8');source=source[:source.index("try:\n (T/'evidence/MANUAL_REPLAY_READY.json')")];scope={'__file__':str(path),'__name__':'diagnostic_only'};exec(compile(source,str(path),'exec'),scope);show=scope['show'];Replay=scope['MatchedReplay'];rows=[]
def state(s):
 e=s.env;d=e.d;w=d.xpos[[e.m.body(n).id for n in ('left_wheel_link','right_wheel_link')]];g=[s.ground(float(v[0]),float(v[1])) for v in w];R=d.xmat[e.base_id].reshape(3,3)
 return dict(t=float(d.time),xyz=d.qpos[:3].tolist(),height=float(e.z)-min(g),cos_tilt=float(e.cos_tilt),tilt_deg=float(np.degrees(np.arccos(np.clip(float(e.cos_tilt),-1,1)))),pitch_deg=float(np.degrees(np.arcsin(np.clip(-R[2,0],-1,1)))),roll_deg=float(np.degrees(np.arctan2(R[2,1],R[2,2]))),closure_m=s.closure,wheel_xyz=w.tolist(),ground_wheels=g,vx=float(e.vx),reason=s.reason)
for height,warm in ((.4,150),(.42,150),(.4,0),(.42,0)):
 s=Replay(show=False);s.set_height(height);s.args.vx=2.2;s.paused=False;trace=[];events=[];original_reset=s.reset_standing
 def reset(self):events.append(state(self));return original_reset()
 s.reset_standing=types.MethodType(reset,s)
 def no_extra_tilt(self,pressed):
  self.just_reset=False
  try:show.Simulation.step(self,pressed)
  except show.SafetyStop as exc:self.reason=str(exc);self.reset_standing()
  q=state(self);self.z=q['height'];self.cos_tilt=q['cos_tilt']
  if self.z<.18:self.reason='unchanged wheel-reference height<0.18';self.reset_standing()
  elif abs(q['xyz'][0])>4.1 or abs(q['xyz'][1])>4.1:self.reason='unchanged tile boundary';self.reset_standing()
  return self.telemetry()
 s.step=types.MethodType(no_extra_tilt,s);first=None;recovered=False;upright=0;max_tilt=0.
 try:
  for k in range(1500):
   s.step({'w'} if k>=warm else set());q=state(s);trace.append([q['t'],*q['xyz'],q['height'],q['cos_tilt'],q['pitch_deg'],q['roll_deg'],q['closure_m'],q['vx']]);max_tilt=max(max_tilt,q['tilt_deg'])
   if first is None and q['cos_tilt']<.766:first=q.copy()
   if first is not None:
    upright=upright+1 if q['cos_tilt']>.9 and not events else 0
    recovered|=upright>=25
    if events or q['t']-first['t']>=3.:break
  label=f'h{round(height*1000)}_warm{warm}';result=dict(case=label,height_command=height,warmup_steps=warm,first_original_viewer_tilt_trigger=first,orientation_recovered_0_5s=recovered,max_tilt_deg=max_tilt,subsequent_original_guard_events=events,last=state(s),physical_guards_unchanged=True,change='Only unconditional viewer cos_tilt<0.766 reset bypassed in this headless diagnostic; no live viewer or frozen evaluation changed',no_optimizer=True)
  rows.append(result);np.savez_compressed(OUT/(label+'.npz'),trace=np.asarray(trace));(OUT/(label+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result),flush=True)
 finally:s.close()
(OUT/'RESULT.json').write_text(json.dumps({'rows':rows,'whole_stair_success_not_scored':True,'scope':'Orientation recovery diagnostic, not graduation or re-scored historic results'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')

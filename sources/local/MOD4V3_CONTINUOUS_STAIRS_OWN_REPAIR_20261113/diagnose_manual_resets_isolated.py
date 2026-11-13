"""Headless reproduction of the two live viewers; capture every state before their reset."""
from pathlib import Path
import sys,types,importlib.util,json,time,traceback,hashlib,math,argparse
import torch,numpy as np,mujoco
T=Path(__file__).resolve().parent;R=T.parents[2];ap=argparse.ArgumentParser();ap.add_argument('--viewer',choices=['old','new'],required=True);a=ap.parse_args();OUT=T/('evidence/manual_reset_diag_20261113_1053_'+a.viewer);OUT.mkdir(exist_ok=False);torch.set_num_threads(1)
OLD=R.parent/'tmp/rough_v1_local_showcase_20261112'
for label,path in [('old',OLD/'MANUAL_STATUS.json'),('new',T/'manual_replay/runtime/MANUAL_STATUS.json')]:
 (OUT/(label+'_live_status.json')).write_bytes(path.read_bytes())
# Isolate the two runtimes: their helper modules have the same names and incompatible template readers.
old=None;new=None;scope={}
if a.viewer=='old':
 spec=importlib.util.spec_from_file_location('old_showcase_diag',OLD/'showcase.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
else:
 path=T/'manual_replay/replay.py';source=path.read_text(encoding='utf8');source=source[:source.index("try:\n (T/'evidence/MANUAL_REPLAY_READY.json')")];scope={'__file__':str(path),'__name__':'diagnostic_only'};exec(compile(source,str(path),'exec'),scope);new=scope['MatchedReplay']
rows=[];arrays={}
def snapshot(s):
 e=s.env;m=e.m;d=e.d;wheel=d.xpos[[m.body(n).id for n in ('left_wheel_link','right_wheel_link')]];rootx,rooty=float(d.qpos[0]),float(d.qpos[1]);rootz=float(e.z);ground_root=s.ground(rootx,rooty);ground_wheels=[s.ground(float(w[0]),float(w[1])) for w in wheel]
 contacts=[]
 for i in range(d.ncon):
  c=d.contact[i];n1=m.geom(int(c.geom1)).name;n2=m.geom(int(c.geom2)).name
  if 'wheel' in n1 or 'wheel' in n2:
   force=np.zeros(6);mujoco.mj_contactForce(m,d,i,force);contacts.append({'geoms':[n1,n2],'point':c.pos.tolist(),'normal':np.asarray(c.frame).reshape(3,3)[0].tolist(),'normal_force':float(force[0])})
 return {'t':float(d.time),'root_xyz':[rootx,rooty,rootz],'ground_at_root':ground_root,'ground_at_wheels':ground_wheels,'height_root_reference':rootz-ground_root,'height_wheel_reference':rootz-min(ground_wheels),'cos_tilt':float(e.cos_tilt),'closure_m':float(s.closure),'wheel_xyz':wheel.tolist(),'vx':float(e.vx),'command_vx':float(s.cmd_vx),'height_command':float(s.height),'reason_field':s.reason,'contacts':contacts}
cases=[('old_L4_h28_v22',old.Replay,4,.28,2.2,150),('old_L4_h40_v22',old.Replay,4,.4,2.2,150),('old_L3_h40_v22',old.Replay,3,.4,2.2,150),('old_L4_h42_immediate',old.Replay,4,.42,2.2,0)] if a.viewer=='old' else [('new_L3_h40_v22',new,3,.4,2.2,150),('new_L3_h42_v22',new,3,.42,2.2,150),('new_L3_h40_immediate',new,3,.4,2.2,0),('new_L3_h42_immediate',new,3,.42,2.2,0)]
for label,constructor,level,h,speed,warm in cases:
 s=constructor(level=level,show=False);s.set_height(h);s.args.vx=speed;s.paused=False;original_reset=s.reset_standing;events=[];trace=[]
 def observed_reset(self):
  event=snapshot(self);event['caller']=[{'file':Path(f.filename).name,'line':f.lineno,'function':f.name} for f in traceback.extract_stack(limit=5)[:-1]];event['tail']=trace[-15:];events.append(event);return original_reset()
 s.reset_standing=types.MethodType(observed_reset,s)
 try:
  for k in range(1500):
   s.step({'w'} if k>=warm else set());v=snapshot(s);trace.append([v['t'],*v['root_xyz'],v['height_root_reference'],v['height_wheel_reference'],v['cos_tilt'],v['closure_m'],v['vx'],v['command_vx']])
   if events:break
  result={'case':label,'level':level,'height':h,'speed':speed,'checkpoint_sha256':hashlib.sha256((old.CKPT if label.startswith('old') else scope['MODEL']).read_bytes()).hexdigest(),'terrain_heights':np.unique(s.vertices[:,2]).tolist(),'steps':k+1,'reset_occurred':bool(events),'first_reset':events[0] if events else None,'last_state':snapshot(s)};rows.append(result);arrays[label]=np.asarray(trace)
  np.savez_compressed(OUT/(label+'.npz'),trace=np.asarray(trace))
  (OUT/(label+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'case':label,'reset':bool(events),'trigger':{k:events[0][k] for k in ['t','root_xyz','ground_at_root','ground_at_wheels','height_root_reference','height_wheel_reference','cos_tilt','closure_m','reason_field','caller']} if events else None}),flush=True)
 finally:s.close()
np.savez_compressed(OUT/'trajectories.npz',**arrays);(OUT/'RESULT.json').write_text(json.dumps({'cases':rows,'no_optimizer':True,'live_windows_unchanged':True,'source':'Exact current old/new viewer with unchanged thresholds and motor/controller timing'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')



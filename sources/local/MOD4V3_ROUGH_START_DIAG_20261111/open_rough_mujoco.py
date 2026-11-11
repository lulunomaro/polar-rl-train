"""Use the existing MOD4 MuJoCo controller on sampled R1 terrain. No training."""
from pathlib import Path
import argparse,hashlib,json,sys,time,xml.etree.ElementTree as ET
import numpy as np
ROOT=Path(r'D:/claude2/fangzhen');PLAY=ROOT/'runs3060/mod4v3_play_20261107';sys.path.insert(0,str(PLAY))
import torch,mujoco,mujoco.viewer,tkinter as tk
from tkinter import ttk
from eval_flatv2_final import args_for
from play_ppo_flatv1_control import Simulation,ControlApp
BASE=Path(__file__).resolve().parent
MODELS={
 'R1 cubic 005m':(ROOT/'frozen_models/rough_r1_abscubic_005m_candidate_20261111/model_005m.pt','4d0976cf1e7995e50d4084926701209982f26c2606a3c3e8c896f2df0de1efd8'),
 'Flat1.5 020m':(ROOT/'frozen_models/flat_square15_020m_candidate_20261111/model_020m.pt','a5102af62938f6bf472855edba34c5f10efce061eecaeb3aebee34815fe7cf87'),
 'R1 square 010m':(ROOT/'frozen_models/rough_r1_square15_010m_candidate_20261111/model_010m.pt','959dc6a5a0ce1b221f8f7c489437b81da3149a712a96d2b8c319a1b3c496e022')}

def scene(family):
 args=args_for(str(MODELS['R1 cubic 005m'][0]));source=Path(args.xml);tree=ET.parse(source);root=tree.getroot()
 root.find('compiler').set('meshdir',str(source.parent/'assets'))
 world=root.find('worldbody');ground=world.find("geom[@name='ground']");world.remove(ground)
 data=np.load(BASE/'evidence/terrain_heightfields.npz');grid=data['grid'];h=(data[family] if family!='flat' else np.zeros_like(data['mid'])).astype(float)
 minimum=float(h.min());span=float(h.max()-minimum)
 # Shift only the world terrain's vertical origin; robot mechanism is identical.
 if family=='flat':h=np.zeros_like(data['mid']);minimum=0.;span=.001
 hf=ET.SubElement(root.find('asset'),'hfield',name='r1_terrain',nrow=str(len(grid)),ncol=str(len(grid)),size=f'4.5 4.5 {max(span,.001)} .2')
 attrs=dict(ground.attrib);attrs.update(name='ground',type='hfield',hfield='r1_terrain',pos=f'0 0 {minimum}',rgba='.36 .43 .48 1');attrs.pop('size',None)
 ET.SubElement(world,'geom',attrs)
 path=BASE/'viewer_generated_scene.xml';tree.write(path,encoding='utf8',xml_declaration=True)
 return path,grid,h,minimum,max(span,.001)

class RoughSimulation(Simulation):
 def __init__(self,label='R1 cubic 005m',family='mid',spawn='approach',show_viewer=True):
  self.label=label;self.family=family;self.spawn=spawn;self.ground_z=0.;self.reset_count=0;self.sequence_start=time.monotonic();self.telemetry_path=BASE/'evidence/VIEWER_LATEST.json'
  path,grid,h,mn,span=scene(family);self.grid=grid;self.terrain=h;self.terrain_min=mn;self.terrain_span=span
  model,digest=MODELS[label];assert hashlib.sha256(model.read_bytes()).hexdigest()==digest
  args=args_for(str(model));args.xml=str(path);args.headless=True;args.vx=1.;args.height=.28
  super().__init__(args)
  self.env.m.hfield_data[:]=((h-mn)/span).ravel()
  self.env.m.opt.timestep=.0025;self.env.dt=.0025;self.env.decim=8
  self.sitepairs=[]
  for el in ET.parse(path).getroot().findall('equality/connect'):
   self.sitepairs.append((int(self.env.m.site(el.get('site1')).id),int(self.env.m.site(el.get('site2')).id)))
  self.reset_standing();self.viewer=None
  if show_viewer:
   self.viewer=mujoco.viewer.launch_passive(self.env.m,self.env.d)
   self.viewer.cam.type=1;self.viewer.cam.trackbodyid=self.env.base_id;self.viewer.cam.distance=3.;self.viewer.cam.azimuth=145;self.viewer.cam.elevation=-20
  self.paused=True
  self.update_values()
 def ground(self,x,y):
  gx=(float(x)+4.5)/.05;gy=(float(y)+4.5)/.05;ix=int(np.clip(np.floor(gx),0,179));iy=int(np.clip(np.floor(gy),0,179));fx=np.clip(gx-ix,0,1);fy=np.clip(gy-iy,0,1)
  h=self.terrain
  return float((1-fy)*((1-fx)*h[iy,ix]+fx*h[iy,ix+1])+fy*((1-fx)*h[iy+1,ix]+fx*h[iy+1,ix+1]))
 def reset_standing(self):
  super().reset_standing()
  x=-.8 if self.spawn=='slope' else -4.15
  if self.family=='flat':x=-3.
  self.env.d.qpos[0]=x;self.env.d.qpos[1]=0.;self.ground_z=self.ground(x,0.);self.env.d.qpos[2]=self.ground_z+self.env.bank_z
  self.env.d.qvel[:]=0.;mujoco.mj_forward(self.env.m,self.env.d);self.env.d.time=0.;self.sequence_start=time.monotonic();self.reset_count+=1;self.update_values()
 def update_values(self):
  x,y=self.env.d.qpos[:2];self.ground_z=self.ground(x,y);self.z=float(self.env.z)-self.ground_z;self.cos_tilt=float(self.env.cos_tilt)
 def step(self,pressed):
  if self.paused:return self.telemetry()
  # Existing player terminates on absolute z; terrain needs the same relative-height rule.
  old_h=self.args.term_height;self.args.term_height=-100.
  value=super().step(pressed);self.args.term_height=old_h;self.update_values()
  closure=max(float(np.linalg.norm(self.env.d.site_xpos[a]-self.env.d.site_xpos[b])) for a,b in self.sitepairs)
  if self.z<.18 or self.cos_tilt<.766 or closure>.002 or not np.isfinite(self.env.d.qpos).all():
   print(json.dumps(dict(event='reset',t=float(self.env.d.time),z=self.z,closure=closure,model=self.label,terrain=self.family)),flush=True);self.reset_standing()
  if self.steps%10==0:
   record=dict(epoch=time.time(),model=self.label,terrain=self.family,spawn=self.spawn,nominal_mujoco=True,physics_dt=self.env.dt,pd_dt=.01,policy_dt=.02,t=float(self.env.d.time),x=float(self.env.d.qpos[0]),vx=float(self.env.vx),command=float(self.cmd_vx),height=self.z,closure_m=closure,resets=self.reset_count-1)
   self.telemetry_path.write_text(json.dumps(record,indent=2))
  return self.telemetry()

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--headless',action='store_true');a=parser.parse_args()
 if a.headless:
  rows=[]
  for spawn in ['approach','slope']:
   sim=RoughSimulation(spawn=spawn,show_viewer=False);sim.paused=False;records=[]
   for _ in range(500):
    sim.step({'w'});records.append([float(sim.env.d.time),float(sim.env.d.qpos[0]),float(sim.env.vx),float(sim.z)])
   rows.append(dict(spawn=spawn,model=sim.label,finite=bool(np.isfinite(sim.env.d.qpos).all()),resets=sim.reset_count-1,tail_mean_velocity=float(np.mean(np.asarray(records)[-50:,2])),trajectory=records));sim.close()
  (BASE/'evidence/MUJOCO_SMOKE.json').write_text(json.dumps(dict(nominal_mujoco=True,not_PhysX_fullDR=True,rows=rows),indent=2));print(json.dumps([{k:v for k,v in x.items() if k!='trajectory'} for x in rows]));return
 root=tk.Tk();sim=RoughSimulation();app=ControlApp(root,sim);root.title('MOD4 Rough replay | R1 cubic005 | MuJoCo nominal')
 extra=tk.Toplevel(root);extra.title('Rough replay selection');extra.geometry('460x300+550+70')
 tk.Label(extra,text='MOD4 R1 rough / MuJoCo nominal',font=('Arial',13,'bold')).pack(pady=8)
 tk.Label(extra,text='Same robot and motor envelope; PhysX fullDR is evaluated separately.').pack()
 model_var=tk.StringVar(value=sim.label);terrain_var=tk.StringVar(value='mid');spawn_var=tk.StringVar(value='approach')
 for text,var,choices in [('Model',model_var,list(MODELS)),('R1 level3 terrain',terrain_var,['mid','inv_mid','flat']),('Reset',spawn_var,['approach','slope'])]:
  frame=tk.Frame(extra);frame.pack(fill='x',padx=10,pady=4);tk.Label(frame,text=text,width=17,anchor='w').pack(side='left');ttk.Combobox(frame,textvariable=var,values=choices,state='readonly',width=26).pack(side='left')
 def switch():
  old=app.sim;old.close();new=RoughSimulation(model_var.get(),terrain_var.get(),spawn_var.get());app.sim=new;app.keys.clear();root.title('MOD4 Rough replay | '+new.label+' | MuJoCo nominal');app._event('changed / paused')
 def auto_forward():
  app.keys.add('w');app.sim.paused=False;app._event('forward 1m/s')
 tk.Button(extra,text='Load selection (paused)',command=switch).pack(pady=4)
 tk.Button(extra,text='Run forward 1m/s',command=auto_forward).pack(pady=4)
 tk.Label(extra,text='approach = flat run-up; slope = original slope standing start\nP pause / R reset / Space stop. Close control window to finish.').pack(pady=4)
 extra.protocol('WM_DELETE_WINDOW',extra.withdraw)
 root.after(500,auto_forward);root.mainloop()
if __name__=='__main__':main()

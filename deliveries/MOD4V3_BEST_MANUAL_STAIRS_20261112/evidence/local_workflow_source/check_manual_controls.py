from pathlib import Path
import json,sys,tkinter as tk
import torch
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B))
from showcase import Replay,FAMILIES
from manual_control import ManualRoughControl
root=tk.Tk();root.withdraw();sim=Replay(family=FAMILIES[8],direction='down');sim.paused=True;app=ManualRoughControl(root,sim);app._is_control_foreground=lambda:True
checks={};seen=[]
hook=sim.actor.register_forward_pre_hook(lambda module,args:seen.append(float(args[0][0,3])))
try:
 checks['starts_paused']=sim.paused and sim.cmd_vx==0 and sim.cmd_wz==0
 app._handle_key_down('p');app._handle_key_up('p')
 app._handle_key_down('w')
 for _ in range(60):sim.step(app.keys)
 checks['forward_key_reaches_policy']=sim.cmd_vx>.9
 app._handle_key_up('w')
 for _ in range(60):sim.step(app.keys)
 checks['release_stops_command']=abs(sim.cmd_vx)<.01
 app._handle_key_down('a')
 for _ in range(40):sim.step(app.keys)
 checks['yaw_control']=sim.cmd_wz>1.
 app._handle_key_up('a');app._stop()
 checks['stop_button_clears_movement']=not (app.keys&{'w','s','a','d'}) and sim.cmd_vx==0 and sim.cmd_wz==0
 heights=[]
 for key,height in [('1',.2),('2',.28),('3',.4)]:
  app._handle_key_down(key);app._handle_key_up(key);sim.step(set());heights.append(dict(key=key,target=sim.height,actor_slot=seen[-1]));assert abs(sim.height-height)<1e-6;assert abs(seen[-1]-5*height)<1e-5
 checks['height_presets_reach_actor']=True
 app.set_height(.28);app._handle_key_down('e')
 for _ in range(10):sim.step(app.keys)
 app._handle_key_up('e');checks['height_E_raises']=sim.height>.28
 app._handle_key_down('q')
 for _ in range(20):sim.step(app.keys)
 app._handle_key_up('q');checks['height_Q_lowers']=sim.height<.28
 app.set_height(.35);app._update_ui();checks['height_slider_sync']=abs(app.height_scale.get()-.35)<1e-6
 app.reset_scene();checks['reset_pauses']=sim.paused and not app.keys
 assert all(checks.values()),checks
 result=dict(checks=checks,height_obs=heights,closure_mm=sim.closure*1000,scope='Existing control callbacks and actual fixed-policy observation input; no training')
 (B/'MANUAL_CONTROL_CHECK.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result),flush=True)
finally:
 hook.remove();app.close()

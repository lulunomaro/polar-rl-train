from pathlib import Path
import sys,json,time
import numpy as np,mujoco,imageio.v2 as imageio
from PIL import Image,ImageDraw,ImageFont
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B))
from showcase import Replay,CN,FAMILIES,EXPECTED
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
rows=[]
for direction,cn in [('up','上台阶'),('down','下台阶')]:
 sim=Replay(direction=direction);cam=mujoco.MjvCamera();cam.distance=3.4;cam.azimuth=30.;cam.elevation=-21.
 opt=mujoco.MjvOption();opt.geomgroup[5]=0
 log=[]
 with mujoco.Renderer(sim.env.m,height=720,width=1280) as r,imageio.get_writer(B/(direction+'_stairs.mp4'),fps=25,codec='libx264',quality=8,macro_block_size=None) as video:
  for k in range(600):
   sim.step({'w'} if sim.env.d.time>.7 else set())
   log.append([k*.02,float(sim.env.d.qpos[0]),float(sim.env.vx),sim.closure,sim.reset_count-1])
   if k%2:continue
   x,y=sim.env.d.qpos[:2];cam.lookat[:]=[x+.6,y,sim.ground(x,y)+.25]
   r.update_scene(sim.env.d,camera=cam,scene_option=opt);im=Image.fromarray(r.render());draw=ImageDraw.Draw(im);draw.rectangle((0,0,1280,92),fill=(23,28,36))
   draw.text((20,7),f'Rough-v1 120m｜{cn}｜低档宽阶：单级16.5cm，踏面1.5m',font=font,fill='white')
   draw.text((20,43),f'MuJoCo 名义条件｜指令 {sim.cmd_vx:.2f} / 实速 {sim.env.vx:.2f} m/s｜保护重置 {sim.reset_count-1}｜t={k*.02:.1f}s',font=small,fill=(200,215,229))
   video.append_data(np.asarray(im))
   if k in (120,300):im.save(B/(direction+f'_stairs_{k}.png'))
 sim.close();rows.append(dict(direction=direction,checkpoint_sha256=EXPECTED,trajectory=log,final_reason=sim.reason));print('CLIP_READY',direction,flush=True)
(B/'LOCAL_REPLAY_CAPTURE.json').write_text(json.dumps(dict(scope='Local nominal visual playback; fixed existing actor; no training; not full-DR acceptance',cases=rows),indent=2),encoding='utf8')

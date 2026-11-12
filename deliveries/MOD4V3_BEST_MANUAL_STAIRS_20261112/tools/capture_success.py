from pathlib import Path
import sys,json,time
import numpy as np,mujoco,imageio.v2 as imageio
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'viewer'))
from showcase import Replay,EXPECTED
import play_mod4v3
from supermimic_wheelbipe import spec as vendor_spec
assert Path(play_mod4v3.__file__).is_relative_to(P)
assert Path(vendor_spec.__file__).is_relative_to(P)
s=Replay();s.args.vx=2.2;rows=[];reached=False;stop_at=None
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
cam=mujoco.MjvCamera();cam.distance=3.4;cam.azimuth=30.;cam.elevation=-21.
opt=mujoco.MjvOption();opt.geomgroup[5]=0
with mujoco.Renderer(s.env.m,height=720,width=1280) as r,imageio.get_writer(P/'media/upstairs_success_16p5cm.mp4',fps=25,codec='libx264',quality=8,macro_block_size=None) as video:
 for k in range(1000):
  s.set_height(.28+(.365-.28)*min(k/100,1.))
  s.step({'w'} if k>=150 and not reached else set())
  x,y=s.env.d.qpos[:2];ground=s.ground(float(x),float(y))
  if not reached and x>-.9 and ground>.30 and s.z>.18 and s.cos_tilt>.766 and s.reset_count==1:
   reached=True;stop_at=k;s.cmd_vx=0.;print('ENTERED_PLATFORM',k,float(x),ground,flush=True)
  rows.append(dict(t=k*.02,x=float(x),y=float(y),ground=ground,height=s.height,height_measured=s.z,vx=float(s.env.vx),command=s.cmd_vx,closure=s.closure,resets=s.reset_count-1,platform_reached=reached))
  if k%2==0:
   cam.lookat[:]=[x+.6,y,ground+.25];r.update_scene(s.env.d,camera=cam,scene_option=opt);im=Image.fromarray(r.render());d=ImageDraw.Draw(im);d.rectangle((0,0,1280,92),fill=(23,28,36))
   d.text((20,7),'11月12日选定模型｜上台阶：16.5cm × 2 → 33cm平台',font=font,fill='white')
   d.text((20,43),f'高度指令 {s.height:.3f}m｜前进指令 {s.cmd_vx:.2f} / 实速 {s.env.vx:.2f}m/s｜场景重置 {s.reset_count-1}｜'+('已登上平台' if reached else '本机MuJoCo名义回放'),font=small,fill=(205,220,230));video.append_data(np.asarray(im))
   if reached and k==stop_at+(stop_at%2):im.save(P/'media/upstairs_success_platform.png')
  if stop_at is not None and k>=stop_at+100:break
  if s.reset_count>1:break
success=reached and s.reset_count==1
result=dict(portable_package=True,success=success,checkpoint_sha256=EXPECTED,height_command=.365,height_ramp_s=2.,forward_command_mps=2.2,forward_start_s=3.,steps=2,single_step_height_m=.165,platform_height_m=.33,portable_module_bindings=dict(controller=str(Path(play_mod4v3.__file__).relative_to(P)),vendor=str(Path(vendor_spec.__file__).relative_to(P))),original_scene_sha256='77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f',trajectory=rows)
(P/'evidence/PORTABLE_REPLAY_CHECK.json').write_text(json.dumps(result,indent=2),encoding='utf8');s.close()
assert success,result['trajectory'][-1]
print(json.dumps(dict(success=success,steps=len(rows),last=rows[-1],module_bindings=result['portable_module_bindings'])),flush=True)

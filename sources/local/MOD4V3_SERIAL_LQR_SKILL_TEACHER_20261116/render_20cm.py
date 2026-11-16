"""Render saved physical rollout states; never resimulate or alter a live viewer."""
from pathlib import Path
import numpy as np,mujoco as mj,imageio.v2 as imageio
from PIL import Image,ImageDraw,ImageFont
T=Path(__file__).resolve().parent
case='step20_vmc_capture_force_balance_nominal'
source=T/'mod4_transfer_20cm_r5'
a=np.load(source/'trajectories.npz');rows=a[case];qpos=a[case+'_qpos'];qvel=a[case+'_qvel']
m=mj.MjModel.from_xml_path(str(source/(case+'.xml')));d=mj.MjData(m)
m.vis.quality.shadowsize=1024;m.vis.headlight.ambient[:]=.55;m.vis.headlight.diffuse[:]=.75
renderer=mj.Renderer(m,height=400,width=704)
cam=mj.MjvCamera();cam.type=mj.mjtCamera.mjCAMERA_FREE;cam.lookat[:]=[1.25,-.12,.30];cam.distance=2.15;cam.azimuth=110;cam.elevation=-18
out=T/'replay_20cm';out.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
shots=[];shot_times=[3.98,4.52,4.94,float(rows[-1,0])];shot_ids=[int(np.argmin(abs(rows[:,0]-t)))for t in shot_times]
with imageio.get_writer(str(out/'mod4v3_teacher_200mm.mp4'),fps=25,codec='libx264',quality=8,macro_block_size=None)as video:
 for k in range(len(rows)):
  if k%2 and k not in shot_ids:continue
  d.qpos[:]=qpos[k];d.qvel[:]=qvel[k];mj.mj_forward(m,d);renderer.update_scene(d,camera=cam)
  im=Image.fromarray(renderer.render().copy());draw=ImageDraw.Draw(im);draw.rectangle([0,0,704,49],fill=(15,20,27));draw.text((12,5),f'MOD4v3 | 200 mm step | teacher execution | t={rows[k,0]:.2f}s',font=font,fill='white');draw.text((12,27),f'pitch={np.degrees(rows[k,4]):+.1f} deg | stable hold={rows[k,17]:.2f}s',font=font,fill=(90,220,210))
  if k%2==0:video.append_data(np.asarray(im))
  if k in shot_ids:
   im.save(out/f'frame_{k:04d}.png');shots.append((k,im.copy()))
renderer.close()
canvas=Image.new('RGB',(1408,800),(15,20,27))
for n,(_,im)in enumerate(sorted(shots,key=lambda x:x[0])):canvas.paste(im,((n%2)*704,(n//2)*400))
canvas.save(out/'mod4v3_teacher_200mm_contact_sheet.png')
print('VIDEO',out/'mod4v3_teacher_200mm.mp4');print('CONTACT_SHEET',out/'mod4v3_teacher_200mm_contact_sheet.png')

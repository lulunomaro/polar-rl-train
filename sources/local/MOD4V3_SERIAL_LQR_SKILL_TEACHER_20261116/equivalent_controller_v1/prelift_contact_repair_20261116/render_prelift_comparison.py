"""Render and plot stored source/native trajectories without running control."""
from pathlib import Path
import json,numpy as np,mujoco as mj
from PIL import Image,ImageDraw,ImageFont
import imageio.v2 as imageio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'motion_quality_audit_20261116'))
from analyze_motion import source,native,metrics
P=Path(__file__).resolve().parent
sets=[source('source_reference_v047'),native(),native(P/'step200_blocked_reference_gate_center_v1', 'MOD4 pre-lift repair')]
labels=['Source reference | actual entry 0.530 m/s','MOD4 baseline | actual entry 0.518 m/s','MOD4 pre-lift repair | entry 0.518 m/s']
colors=['#23a886','#2f80ed','#e25d48'];anchors=[]
for d in sets:
 r=json.loads((d['path']/'RESULT.json').read_text());anchors.append(r['entry'].get('t',r['entry'].get('time')))
font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',17);small=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',14)
render=[]
for d in sets:
 m=d['model'];m.vis.global_.offwidth=480;m.vis.global_.offheight=440;m.vis.headlight.ambient[:]=.65;m.vis.headlight.diffuse[:]=.8
 renderer=mj.Renderer(m,height=440,width=480);data=mj.MjData(m);cam=mj.MjvCamera();cam.distance=1.9;cam.azimuth=95.;cam.elevation=-13.;render.append((renderer,data,cam))
video=P/'SOURCE_BASELINE_PRELIFT_REPAIR_1X.mp4'
with imageio.get_writer(video,fps=25,codec='libx264',quality=8,macro_block_size=2)as writer:
 for frame,dt in enumerate(np.arange(-.32,2.321,.04)):
  panels=[]
  for k,(d,anchor,(renderer,data,cam))in enumerate(zip(sets,anchors,render)):
   i=int(np.argmin(abs(d['t']-(anchor+dt))));data.qpos[:]=d['qpos'][i];data.qvel[:]=d['qvel'][i];mj.mj_forward(d['model'],data);cam.lookat[:]=[.6*data.qpos[0]+.5,0.,.33];renderer.update_scene(data,camera=cam);im=Image.fromarray(renderer.render());dr=ImageDraw.Draw(im);dr.rectangle((0,0,480,85),fill=(15,22,30));dr.text((10,7),labels[k],fill=colors[k],font=font);dr.text((10,30),f'dt_contact={dt:+.2f}s | {d["phases"][i]}',fill='white',font=small);dr.text((10,51),f'pitch {np.rad2deg(d["pitch"][i]):+.1f} deg | vx {d["vx"][i]:+.2f} m/s',fill='white',font=small);dr.text((10,68),f'leg {d["length"][i].mean()*1000:.0f} mm | 1x playback',fill='white',font=small);panels.append(im)
  combined=Image.new('RGB',(1440,440))
  for k,im in enumerate(panels):combined.paste(im,(480*k,0))
  writer.append_data(np.asarray(combined))
  if frame in [12,18,24,36,50]:combined.save(P/f'comparison_frame_{frame:03d}.png')
for r,_,_ in render:r.close()
print('VIDEO',video,video.stat().st_size,flush=True)
fig,ax=plt.subplots(4,1,figsize=(11.5,10),sharex=True)
for k,(d,anchor)in enumerate(zip(sets,anchors)):
 mask=(d['t']>=anchor-.32)&(d['t']<=anchor+2.32);tm=d['t'][mask]-anchor
 ax[0].plot(tm,np.rad2deg(d['pitch'][mask]),color=colors[k],label=labels[k]);ax[1].plot(tm,d['vx'][mask],color=colors[k]);ax[2].plot(tm,d['length'][mask].mean(axis=1)*1000,color=colors[k]);ax[3].plot(tm,(d['x'][mask]-np.interp(anchor,d['t'],d['x']))*1000,color=colors[k])
for a in ax:a.axvline(0,color='#444',ls=':',lw=1);a.grid(alpha=.22)
ax[0].set_ylabel('Body pitch (deg)');ax[0].legend(loc='upper right',fontsize=9);ax[1].set_ylabel('Forward vx (m/s)');ax[2].set_ylabel('Mean leg length (mm)');ax[3].set_ylabel('Base x travel (mm)');ax[3].set_xlabel('Seconds from first measured stair contact');ax[3].set_xlim(-.32,2.32)
fig.suptitle('200 mm stair | source, native baseline, pre-lift repair\nSame 1x time scale; source/native bodies, contact physics and control rates differ',fontsize=12);fig.tight_layout(rect=(0,0,1,.95));fig.savefig(P/'PRELIFT_COMPARISON.png',dpi=150);plt.close(fig)
print('PLOT',P/'PRELIFT_COMPARISON.png',flush=True)

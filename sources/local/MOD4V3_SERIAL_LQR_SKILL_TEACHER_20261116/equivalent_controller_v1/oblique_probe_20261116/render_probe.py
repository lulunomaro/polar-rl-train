from pathlib import Path
import sys,json,numpy as np,mujoco as mj,imageio.v2 as imageio
from PIL import Image,ImageDraw,ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'motion_quality_audit_20261116'));from analyze_motion import native
font=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',20);small=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',15)
sets=[];renders=[]
for deg in [-20,-10,10,20]:
 d=native(P/f'oblique_{deg:+04d}deg_v1',str(deg));d['eval']=json.loads((d['path']/'OBLIQUE_EVAL.json').read_text());d['result']=json.loads((d['path']/'RESULT.json').read_text());d['entry']=d['result']['entry']['time'];d['raw']=np.load(d['path']/'trace.npz');sets.append(d)
 m=d['model'];m.vis.global_.offwidth=560;m.vis.global_.offheight=420;m.vis.headlight.ambient[:]=.65;m.vis.headlight.diffuse[:]=.8
 renderer=mj.Renderer(m,height=420,width=560);data=mj.MjData(m);cam=mj.MjvCamera();idx=np.argmin(abs(d['t']-d['entry']));cam.lookat[:]=[1.3,d['qpos'][idx,1],.32];cam.distance=2.35;cam.azimuth=130.;cam.elevation=-23.;renders.append((renderer,data,cam))
video=P/'OBLIQUE_FOUR_ANGLES_1X.mp4'
with imageio.get_writer(video,fps=25,codec='libx264',quality=8,macro_block_size=2)as writer:
 for frame,dt in enumerate(np.arange(-.24,5.521,.04)):
  combined=Image.new('RGB',(1120,840))
  for k,(d,(renderer,data,cam))in enumerate(zip(sets,renders)):
   deg=d['eval']['case']['yaw_deg'];i=int(np.argmin(abs(d['t']-(d['entry']+dt))));data.qpos[:]=d['qpos'][i];data.qvel[:]=d['qvel'][i];mj.mj_forward(d['model'],data);renderer.update_scene(data,camera=cam);im=Image.fromarray(renderer.render());dr=ImageDraw.Draw(im);dr.rectangle((0,0,560,112),fill=(15,22,30));color='#45c99c'if d['eval']['pass_oblique']else'#ee8855';outcome='稳定登台'if d['eval']['pass_oblique']else('短暂登台后掉台'if deg==10 else'未触发抬腿');dr.text((10,4),f'200mm | 指令斜角 {deg:+d}° | {outcome}',fill=color,font=font);dr.text((10,34),f'1× 触阶后 {dt:+.2f}s | {d["phases"][i]}',fill='white',font=small);dr.text((10,58),f'实际航向 {np.rad2deg(d["yaw"][i]):+.1f}° | 俯仰 {np.rad2deg(d["pitch"][i]):+.1f}°',fill='white',font=small);axis=np.array([np.cos(np.deg2rad(deg)),np.sin(np.deg2rad(deg))]);v=float(d['qvel'][i,:2]@axis);dr.text((10,82),f'前向速度 {v:+.3f}m/s | 横滚 {np.rad2deg(d["raw"]["trace"][i,4]):+.1f}°',fill='white',font=small);combined.paste(im,((k%2)*560,(k//2)*420))
  writer.append_data(np.asarray(combined))
  if frame in [24,40,75]:combined.save(P/f'four_angles_frame_{frame:03d}.png')
for renderer,_,_ in renders:renderer.close()
plt.rcParams['font.family']='Microsoft YaHei';plt.rcParams['axes.unicode_minus']=False
fig,axes=plt.subplots(4,4,figsize=(18,11),sharex=True)
for row,d in enumerate(sets):
 deg=d['eval']['case']['yaw_deg'];t=d['t']-d['entry'];mask=(t>=-.24)&(t<=3.5);f=d['raw']['trace'];axis=np.array([np.cos(np.deg2rad(deg)),np.sin(np.deg2rad(deg))]);forward=d['qvel'][:,:2]@axis
 axes[row,0].plot(t[mask],np.rad2deg(f[mask,5]),label='俯仰');axes[row,0].plot(t[mask],np.rad2deg(f[mask,4]),label='横滚');axes[row,1].plot(t[mask],forward[mask]);axes[row,2].plot(t[mask],np.rad2deg(f[mask,6]));axes[row,2].axhline(deg,color='#b65a31',ls='--');axes[row,3].step(t[mask],np.sum(f[mask,16:18]>.5,axis=1),where='post')
 axes[row,0].set_ylabel(f'指令 {deg:+d}°')
 for ax in axes[row]:ax.grid(alpha=.25);ax.axvline(0,color='#888',ls=':',lw=.8);ax.set_xlim(-.24,3.5)
 axes[row,3].set_ylim(-.1,2.2);axes[row,3].set_yticks([0,1,2])
axes[0,0].legend(fontsize=8)
for j,title in enumerate(['机身倾角 (°)','真实前向速度 (m/s)','实际偏航 / 指定航向 (°)','台顶承载轮数']):axes[0,j].set_title(title);axes[-1,j].set_xlabel('首次触阶后时间 (s)')
fig.suptitle('冻结当前200mm教师：真实斜向进场测试，每角度单次；仅−10°通过',fontsize=14);fig.tight_layout(rect=(0,0,1,.95));fig.savefig(P/'OBLIQUE_COMPARISON.png',dpi=145);plt.close(fig)
print(video,video.stat().st_size,flush=True)

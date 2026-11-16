from pathlib import Path
import sys,json,numpy as np,mujoco as mj
from PIL import Image,ImageDraw,ImageFont
import imageio.v2 as imageio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'motion_quality_audit_20261116'))
from analyze_motion import native
font=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',21)
small=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',16)
plt.rcParams['font.family']='Microsoft YaHei';plt.rcParams['axes.unicode_minus']=False
pairs=[]
for mm in [-60,-30,0,30,60]:
 pair=[]
 for label in ['baseline_v2','final_clean_v2']:
  d=native(P/f'{label}_{mm:+04d}mm',label);r=json.loads((d['path']/'RESULT.json').read_text());d['entry']=r['entry']['time'];d['raw']=np.load(d['path']/'trace.npz');pair.append(d)
 pairs.append((mm,pair))
video=P/'FIVE_STARTS_V2_VS_CAPTURE_REPAIR_1X.mp4'
if '--plots-only' not in sys.argv:
 with imageio.get_writer(video,fps=25,codec='libx264',quality=8,macro_block_size=2)as writer:
  for mm,pair in pairs:
   renders=[]
   for d in pair:
    m=d['model'];m.vis.global_.offwidth=560;m.vis.global_.offheight=480;m.vis.headlight.ambient[:]=.65;m.vis.headlight.diffuse[:]=.8
    renderer=mj.Renderer(m,height=480,width=560);data=mj.MjData(m);cam=mj.MjvCamera();cam.lookat[:]=[1.3,0.,.32];cam.distance=2.05;cam.azimuth=95.;cam.elevation=-13.;renders.append((renderer,data,cam))
   for frame,dt in enumerate(np.arange(-.24,5.521,.04)):
    combined=Image.new('RGB',(1120,480))
    for col,(d,(renderer,data,cam))in enumerate(zip(pair,renders)):
     i=int(np.argmin(abs(d['t']-(d['entry']+dt))));data.qpos[:]=d['qpos'][i];data.qvel[:]=d['qvel'][i];mj.mj_forward(d['model'],data);renderer.update_scene(data,camera=cam);im=Image.fromarray(renderer.render());dr=ImageDraw.Draw(im);dr.rectangle((0,0,560,113),fill=(15,22,30));color='#e87950'if col==0 else '#45c99c';label='原版 v2'if col==0 else '接管修复候选';dr.text((12,5),f'{label} | 起点 {mm:+d} mm | 1×',fill=color,font=font);dr.text((12,34),f'触阶后 {dt:+.2f}s | {d["phases"][i]}',fill='white',font=small);dr.text((12,59),f'俯仰 {np.rad2deg(d["pitch"][i]):+.2f}°  速度 {d["vx"][i]:+.3f} m/s',fill='white',font=small);margin=(min(d['raw']['trace'][i,[8,11]])-1.2)*1000;dr.text((12,84),f'机身 x {d["x"][i]:.3f}m | 两轮较小越边量 {margin:+.0f}mm',fill='white',font=small);combined.paste(im,(560*col,0))
    writer.append_data(np.asarray(combined))
    if mm==0 and frame in [20,28,65,120]:combined.save(P/f'center_frame_{frame:03d}.png')
    if frame==28:combined.save(P/f'offset_{mm:+04d}_landing.png')
   for renderer,_,_ in renders:renderer.close()
   print('rendered',mm,flush=True)
colors=['#d66d3e','#168b69']
fig,axes=plt.subplots(5,4,figsize=(19,13),sharex=True)
for row,(mm,pair)in enumerate(pairs):
 for col,d in enumerate(pair):
  t=d['t']-d['entry'];mask=(t>=-.24)&(t<=2.2);x0=np.interp(d['entry'],d['t'],d['x']);vals=[np.rad2deg(d['pitch']),d['vx'],(d['x']-x0)*1000,(np.min(d['raw']['trace'][:,[8,11]],axis=1)-1.2)*1000]
  for j,y in enumerate(vals):axes[row,j].plot(t[mask],y[mask],color=colors[col],label='原版 v2'if col==0 else '接管修复')
 for j in range(4):axes[row,j].grid(alpha=.22);axes[row,j].axhline(0,color='#777',lw=.7);axes[row,j].axvline(0,color='#888',ls=':',lw=.8);axes[row,j].set_xlim(-.24,2.2)
 axes[row,0].set_ylabel(f'起点 {mm:+d}mm')
for j,title in enumerate(['俯仰 (°)','真实前向速度 (m/s)','机身相对触阶位置 (mm)','两轮较小越边量 (mm)']):axes[0,j].set_title(title);axes[-1,j].set_xlabel('触阶后时间 (s)')
axes[0,0].legend(fontsize=8);fig.suptitle('200mm 五起点｜相同 v2 前段，接管与停车参考修复\n前段至首个 capture 的状态/动作逐帧完全相同；短暂回缩仍保留，未宣称无倒退',fontsize=14);fig.tight_layout(rect=(0,0,1,.945));fig.savefig(P/'FIVE_STARTS_COMPARISON.png',dpi=145);plt.close(fig)
mm,pair=pairs[2];fig,axes=plt.subplots(4,1,figsize=(12,10),sharex=True)
for j,d in enumerate(pair):
 ds_path=(P/'diagnostic_v2_+000mm' if j==0 else d['path'])/'STEP_DIAGNOSTICS.json';ds=json.loads(ds_path.read_text());t=d['t']-d['entry'];dx=[];vv=[]
 for b in ds:
  l=b.get('lqr');dx.append(np.nan if not l else l['target'][0]-l['state'][0]);vv.append(np.nan if not l else l['target'][5])
 axes[0].plot(t,np.rad2deg(d['pitch']),color=colors[j],label='原版 v2'if j==0 else '接管修复');axes[1].plot(t,d['vx'],color=colors[j]);axes[2].plot(t,np.mean(d['raw']['requested'][:,4:],axis=1),color=colors[j]);axes[3].plot(t,np.array(dx)*1000,color=colors[j])
for a in axes:a.grid(alpha=.25);a.axhline(0,color='#777',lw=.8);a.set_xlim(-.1,5.5)
for a,label in zip(axes,['俯仰 (°)','真实前向速度 (m/s)','左右请求轮矩均值 (Nm)','位置目标 - 实测里程计 (mm)']):a.set_ylabel(label)
axes[0].legend();axes[-1].set_xlabel('触阶后时间 (s)');fig.suptitle('Center：早期等门控丢速未改；接管反拉减轻，停车后回到松油点的指令已移除');fig.tight_layout(rect=(0,0,1,.95));fig.savefig(P/'CENTER_REFERENCE_DIAGNOSTIC.png',dpi=150);plt.close(fig)
print('VIDEO',video,video.stat().st_size,flush=True)

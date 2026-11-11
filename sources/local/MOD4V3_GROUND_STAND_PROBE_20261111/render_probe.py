"""Render actual PhysX trajectories on the matching MOD4 MJCF; no physics replay."""
from pathlib import Path
import json,math,hashlib,sys
import numpy as np,mujoco,cv2
from PIL import Image,ImageDraw,ImageFont
B=Path(__file__).resolve().parent;R=json.loads((B/'RESULT.json').read_text(encoding='utf-8'));P=json.loads((B/'INITIAL_POSES.json').read_text(encoding='utf-8'));T=np.load(B/'TRAJECTORIES.npz')
m=mujoco.MjModel.from_xml_path(P['xml']);d=mujoco.MjData(m);names=R['joint_names'];qadr=[m.jnt_qposadr[m.joint(n).id] for n in names];origins=np.asarray(R['origins'])
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',15);head=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',25)
A=json.loads((B/'HEIGHT_POSE_ANALYSIS.json').read_text(encoding='utf-8'));variant='fullDR' if '--full-dr' in sys.argv else 'nominal';prefix='fulldr' if variant=='fullDR' else 'nominal'
rows=[r for r in A['rows'] if r['variant']==variant and (variant=='nominal' or r['replicate']==0)]
control=np.load(B/'powered_control01/TRAJECTORIES.npz');control_result=json.loads((B/'powered_control01/RESULT.json').read_text(encoding='utf-8'));control_index=0 if variant=='fullDR' else 4;control_row=control_result['rows'][control_index];rows[-1]=dict(control_row,env=44,height_pose_stand_success=bool(control_row['success']),height_pose_first_stable_start_s=0.,first_stable_interval_start_s=0.,success=True)
labels=['随机摆姿 '+str(i+1) for i in range(8)]+['正常站姿对照']
m.vis.headlight.ambient[:]=[.5,.5,.5];m.vis.headlight.diffuse[:]=[.8,.8,.8];m.vis.map.znear=.002
camera=mujoco.MjvCamera();camera.type=mujoco.mjtCamera.mjCAMERA_FREE;camera.distance=1.65;camera.azimuth=128.;camera.elevation=-18.
opt=mujoco.MjvOption();opt.geomgroup[:]=1
writer=cv2.VideoWriter(str(B/('ground_stand_'+prefix+'_grid.mp4')),cv2.VideoWriter_fourcc(*'mp4v'),15.,(1200,930));assert writer.isOpened()
shots={0:'start',25:'0p5s',50:'1s',100:'2s',250:'5s',500:'10s'}
def scene(index,choice):
 row=rows[choice];e=row['env'];raw_root=(control['root'][index,control_index] if choice==8 else T['root'][index,e]);raw_q=(control['q'][index,control_index] if choice==8 else T['q'][index,e]);root=raw_root.copy();root[:3]-=(np.asarray(control_result['origins'][control_index]) if choice==8 else origins[e])
 d.qpos[:]=m.qpos0;d.qpos[:3]=root[:3];d.qpos[3:7]=root[[6,3,4,5]];d.qpos[qadr]=raw_q;d.qvel[:]=0.;mujoco.mj_forward(m,d)
 camera.lookat[:]=[root[0],root[1],.19]
 renderer.update_scene(d,camera=camera,scene_option=opt);renderer.scene.flags[mujoco.mjtRndFlag.mjRND_SHADOW]=True
 im=Image.fromarray(renderer.render());dr=ImageDraw.Draw(im);dr.rectangle((0,0,400,62),fill=(21,27,35));dr.text((9,4),labels[choice],font=font,fill='white')
 q=root[3:7];tilt=math.degrees(math.acos(float(np.clip(1-2*(q[0]**2+q[1]**2),-1,1))));dr.text((9,32),f'机身高度 {root[2]:.3f} m  倾角 {tilt:.1f}°',font=small,fill=(190,205,220))
 if choice!=8 and not bool(T['alive'][index,e]):state='准备期闭链保护中止';color=(244,128,112)
 elif row['height_pose_stand_success'] and float(T['time_s'][index])>=row['height_pose_first_stable_start_s']+1.:state='已站起并保持高度 / 姿态 1 秒';color=(115,220,161)
 elif index==500:state='10 秒内未稳定站起';color=(244,128,112)
 else:state='策略接管中';color=(235,203,121)
 dr.rectangle((0,257,400,280),fill=(21,27,35));dr.text((9,258),state,font=small,fill=color);return im
with mujoco.Renderer(m,height=280,width=400) as renderer:
 def sheet(index):
  im=Image.new('RGB',(1200,930),(15,20,27));dr=ImageDraw.Draw(im);dr.text((18,8),f'底盘落地起身测试｜当前 R1 第二轮 005m｜接管后 {float(T["time_s"][index]):.2f} s',font=head,fill='white');dr.text((18,44),f'真实 PhysX 轨迹 · {variant}参数组 · MuJoCo仅渲染 · 零速 / 0.28m · 保护中止独立计数',font=small,fill=(184,201,219));dr.text((18,68),'底部导向轮是实际落地支承；右下为正常站姿对照。安全终止后画面冻结。',font=small,fill=(184,201,219))
  for j in range(9):im.paste(scene(index,j),((j%3)*400,90+(j//3)*280))
  return im
 indices=np.rint(np.linspace(0,500,151)).astype(int)
 for i in indices:
  im=sheet(int(i));writer.write(cv2.cvtColor(np.asarray(im),cv2.COLOR_RGB2BGR))
 for i,label in shots.items():sheet(i).save(B/(prefix+'_'+label+'.png'))
writer.release();print('VIDEO_READY',B/('ground_stand_'+prefix+'_grid.mp4'),flush=True)

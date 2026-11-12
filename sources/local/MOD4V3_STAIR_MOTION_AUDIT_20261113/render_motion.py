"""Render recorded states offscreen. Color changes are display-only, never used in physics."""
from pathlib import Path
import json,math
import numpy as np,mujoco
from PIL import Image,ImageDraw,ImageFont
T=Path(__file__).resolve().parent;E=T/'evidence';F=T/'figures';F.mkdir(exist_ok=True)
P=E/'raised365_fast';a=np.load(P/'trajectory.npz');m=mujoco.MjModel.from_xml_path(str(P/'scene.xml'));d=mujoco.MjData(m)
m.vis.headlight.ambient[:]=[.8,.8,.8];m.vis.headlight.diffuse[:]=[.7,.7,.7]
# Show the actual colliders: blue chassis, grey linkage, gold drive wheels, green front guide contacts.
for i in range(m.ngeom):
 body=m.body(int(m.geom_bodyid[i])).name
 if int(m.geom_group[i])==3:
  rgba=[.59,.63,.68,1.]
  if body=='base_link':rgba=[.24,.57,.79,.94]
  if body in ['left_wheel_link','right_wheel_link']:rgba=[.95,.68,.16,1.]
  if body in ['left_front_guide_link','right_front_guide_link']:rgba=[.12,.85,.36,1.]
  m.geom_rgba[i]=rgba
 if m.geom(i).name.startswith('step_'):m.geom_rgba[i]=[.61,.45,.31,1.]
 if m.geom(i).name=='ground':m.geom_rgba[i]=[.70,.72,.74,1.]
opt=mujoco.MjvOption();opt.geomgroup[:]=0;opt.geomgroup[3]=1;opt.geomgroup[5]=1
cam=mujoco.MjvCamera();cam.type=mujoco.mjtCamera.mjCAMERA_FREE;cam.distance=1.38;cam.azimuth=90.;cam.elevation=-8.
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17);big=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',28)
raw_contacts={round(json.loads(line)['t'],6):json.loads(line)['contacts'] for line in (P/'contacts.jsonl').open(encoding='utf8')}

def image_at(renderer,ts):
 i=int(np.argmin(abs(a['time']-ts)));d.qpos[:]=a['qpos'][i];d.qvel[:]=a['qvel'][i];d.ctrl[:]=0;d.ctrl[[m.actuator(name+'_motor').id for name in ['left_front1_joint','right_front1_joint','left_rear1_joint','right_rear1_joint','left_wheel_joint','right_wheel_joint']]]=a['ctrl_env'][i];mujoco.mj_forward(m,d)
 cam.lookat[:]=[d.qpos[0]-.05,d.qpos[1],.32+(0.165 if d.qpos[0]>-1.8 else 0.)]
 renderer.update_scene(d,camera=cam,scene_option=opt);renderer.scene.flags[mujoco.mjtRndFlag.mjRND_SHADOW]=False
 for c in raw_contacts.get(round(float(a['time'][i]),6),[]):
  if c['normal_force']<5:continue
  g=renderer.scene.geoms[renderer.scene.ngeom];mujoco.mjv_initGeom(g,mujoco.mjtGeom.mjGEOM_SPHERE,np.array([.012]*3),np.array(c['position']),np.eye(3).ravel(),np.array([1.,.12,.10,1.],dtype=np.float32));renderer.scene.ngeom+=1
 im=Image.fromarray(renderer.render());im=im.copy() # detach before the next render
 canvas=Image.new('RGB',(800,570),(20,26,34));canvas.paste(im,(0,72));draw=ImageDraw.Draw(canvas)
 draw.text((15,6),f"t={a['time'][i]:.2f}s  机身vx={a['root_vel_world'][i,0]:.2f}m/s  前俯={-a['root_noseup_deg'][i]:.1f}°",font=font,fill='white')
 draw.text((15,36),f"等效腿长={a['leg_length'][i].mean()*100:.1f}cm  驱动轮速={a['qvel'][i,[10,21]].mean():.1f}rad/s",font=small,fill=(200,210,220))
 draw.text((15,535),'蓝：机身  金：驱动轮  绿：前导向小轮  红点：有力接触',font=small,fill=(220,225,232))
 return canvas

schedule=[(4.,'① 触阶前：约1.81m/s'),(4.14,'② 前导向小轮搭上沿'),(4.30,'③ 前俯、收腿、抬轮'),(4.48,'④ 轮落台面、恢复姿态'),(5.48,'⑤ 再加速后触第二阶'),(5.62,'⑥ 第二阶重复支撑抬轮'),(5.78,'⑦ 轮越上沿、机身前俯'),(5.98,'⑧ 落轮后再恢复姿态')]
with mujoco.Renderer(m,height=450,width=800) as renderer:
 sheet=Image.new('RGB',(1600,4*610+115),(20,26,34));sd=ImageDraw.Draw(sheet);sd.text((20,12),'连续上阶的真实接触动作｜冻结模型iter24692｜名义MuJoCo',font=big,fill='white');sd.text((20,55),'碰撞几何视图，颜色仅用于分析；每级16.5cm，一级踏面深1.5m。',font=font,fill=(200,210,220))
 for k,(ts,caption) in enumerate(schedule):
  im=image_at(renderer,ts);panel=Image.new('RGB',(800,610),(20,26,34));panel.paste(im,(0,40));pd=ImageDraw.Draw(panel);pd.text((15,7),caption,font=font,fill=(255,209,115));sheet.paste(panel,((k%2)*800,115+(k//2)*610))
 sheet.save(F/'STAIR_KEYFRAMES.png')
 preview=image_at(renderer,4.30);preview.save(F/'FRAME_4_30.png')
 frames=[image_at(renderer,float(ts)).quantize(colors=128) for ts in np.arange(3.8,6.4,.04)]
 frames[0].save(F/'STAIR_MOTION_HALF_SPEED.gif',save_all=True,append_images=frames[1:],duration=80,loop=0,optimize=False)
(F/'RENDER_METHOD.json').write_text(json.dumps(dict(source='Recorded original simulation states; mj_forward only on a separate rendering model/data; original frozen physics not changed',view='Actual collision geometry with display-only body colors and >5N contact point markers; visual CAD meshes hidden for leg/contact visibility',gif_playback_speed=.5,case='raised365_fast',frames=len(frames),width=800,height=570,keyframe_times=[x[0] for x in schedule]),indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(figures=[p.name for p in F.iterdir()],gif_frames=len(frames))),flush=True)

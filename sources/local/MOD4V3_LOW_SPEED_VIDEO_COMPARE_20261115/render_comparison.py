from pathlib import Path
import json,math,numpy as np,mujoco,imageio.v2 as iio
from PIL import Image,ImageDraw,ImageFont
A=Path(__file__).resolve().parent;E=A/'evidence/replay40m'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20);title=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',32)
z=np.load(E/'whole_low040_seed0_details.npz');x=z['motion'];f=z['force_peak'];hits=np.where((f[:,4:8].sum(1)>5)&(x[:,0]>=3))[0];touch=float(x[hits[0],0]);times=[max(3.,touch-.25),touch+.3,touch+1.2,29.98]
m=mujoco.MjModel.from_xml_path(str(E/'whole_low040_seed0_scene.xml'));d=mujoco.MjData(m);cam=mujoco.MjvCamera();cam.lookat[:]=[-2.94,-.18,.25];cam.distance=1.5;cam.azimuth=295.;cam.elevation=-20.;opt=mujoco.MjvOption();opt.geomgroup[5]=1;opt.geomgroup[4]=0
for gid in range(m.ngeom):
 if m.geom_bodyid[gid]==0 and m.geom_group[gid]==1:m.geom_group[gid]=4
m.geom_rgba[m.geom('ground').id]=[.74,.77,.78,1.];m.geom_rgba[m.geom('step_1').id]=[.74,.52,.30,1.];m.geom_rgba[m.geom('step_2').id]=[.60,.40,.23,1.];m.vis.headlight.ambient[:]=[.7,.7,.7];m.vis.headlight.diffuse[:]=[.6,.6,.6]
frames=[]
with mujoco.Renderer(m,height=450,width=720)as renderer:
 for t in times:
  idx=int(np.argmin(abs(x[:,0]-t)));d.qpos[:]=z['qpos'][idx];d.qvel[:]=z['qvel'][idx];mujoco.mj_forward(m,d);renderer.update_scene(d,camera=cam,scene_option=opt);renderer.scene.flags[mujoco.mjtRndFlag.mjRND_SHADOW]=True;im=renderer.render();im[np.all(im<3,axis=2)]=[225,230,235];im=Image.fromarray(im);im.save(A/('sim_t'+str(round(x[idx,0],2))+'.png'));frames.append((im,idx))
canvas=Image.new('RGB',(1920,1060),(20,26,34));draw=ImageDraw.Draw(canvas);draw.text((20,12),'视频与当前40分钟检查点｜朝台阶为前，画面向左',font=title,fill='white');draw.text((20,60),'上排：原视频的成功动作。下排：当前0.4m/s指令的全程回放。时间分别属于各自片段，未强行对齐速度。',font=small,fill=(195,210,225));draw.text((20,105),'原视频：底盘进入台面 → 后上方搬轮 → 轮子收回台面 → 伸腿站稳',font=font,fill=(115,220,160))
reader=iio.get_reader('C:/Users/lulunomaro/Desktop/43574887781-1-192.mp4',format='ffmpeg');ref=[(70,'搭阶，轮子在后下方'),(85,'轮轴向后上方抬'),(105,'轮子已进入台面'),(285,'再伸腿站立')]
for col,(frame,label)in enumerate(ref):
 im=Image.fromarray(reader.get_data(frame)).crop((310,125,960,570)).resize((480,328),Image.Resampling.LANCZOS);canvas.paste(im,(col*480,147));draw.text((col*480+12,483),f'{frame/30:.2f}s：'+label,font=small,fill='white')
reader.close();draw.text((20,535),'当前策略：触阶 → 主轮仍压下层地面 → 前后挤动 → 30秒仍未第一阶落轮',font=font,fill=(255,190,95))
labels=['接近触阶','触阶后仍长腿顶住','有后移，抬升很小','仍留在下层地面']
for col,(im,idx)in enumerate(frames):
 canvas.paste(im.resize((480,300),Image.Resampling.LANCZOS),(col*480,577));draw.text((col*480+12,888),f'{x[idx,0]:.2f}s：'+labels[col],font=small,fill='white');draw.text((col*480+12,925),f'轮轴高度 {x[idx,6]*100:.1f}/{x[idx,9]*100:.1f} cm',font=small,fill=(255,211,140));draw.text((col*480+12,960),f'相对机身x {x[idx,10]*100:.1f}/{x[idx,13]*100:.1f} cm',font=small,fill=(195,210,225))
draw.text((20,1012),'第一阶高20cm，轮半径6.25cm；主轮落到台面时轮轴需约26.25cm。图中仿真位置来自保存的完整qpos。',font=small,fill=(195,210,225));canvas.save(A/'VIDEO_VS_SIM_40M.jpg',quality=95)
# The auxiliary pose is already rearward. Show whether it continues the mount or drops to ground.
z2=np.load(E/'supported_late040_seed0_details.npz');x2=z2['motion'];m2=mujoco.MjModel.from_xml_path(str(E/'supported_late040_seed0_scene.xml'));d2=mujoco.MjData(m2)
for gid in range(m2.ngeom):
 if m2.geom_bodyid[gid]==0 and m2.geom_group[gid]==1:m2.geom_group[gid]=4
m2.geom_rgba[m2.geom('ground').id]=[.74,.77,.78,1.];m2.geom_rgba[m2.geom('step_1').id]=[.74,.52,.30,1.];m2.geom_rgba[m2.geom('step_2').id]=[.60,.40,.23,1.];m2.vis.headlight.ambient[:]=[.7,.7,.7];m2.vis.headlight.diffuse[:]=[.6,.6,.6]
cam.lookat[:]=[-2.9,0,.27];aux=Image.new('RGB',(1440,590),(20,26,34));ad=ImageDraw.Draw(aux);ad.text((20,10),'后摆辅助初态：已有后摆，也没有接上向上搬轮',font=title,fill='white')
with mujoco.Renderer(m2,height=450,width=720)as renderer:
 for col,t in enumerate([0.,.5,2.]):
  idx=int(np.argmin(abs(x2[:,0]-t)));d2.qpos[:]=z2['qpos'][idx];mujoco.mj_forward(m2,d2);renderer.update_scene(d2,camera=cam,scene_option=opt);renderer.scene.flags[mujoco.mjtRndFlag.mjRND_SHADOW]=True;im=renderer.render();im[np.all(im<3,axis=2)]=[225,230,235];aux.paste(Image.fromarray(im).resize((480,330),Image.Resampling.LANCZOS),(col*480,65));ad.text((col*480+12,410),f't={x2[idx,0]:.2f}s',font=font,fill='white');ad.text((col*480+12,454),f'轮轴高度 {x2[idx,6]*100:.1f}/{x2[idx,9]*100:.1f} cm',font=small,fill=(255,211,140));ad.text((col*480+12,494),f'相对机身x {x2[idx,10]*100:.1f}/{x2[idx,13]*100:.1f} cm',font=small,fill=(195,210,225))
ad.text((20,548),'辅助初态单列：不算从地面完整上两阶。画面显示实际台阶碰撞体，动力学沿用原回放。',font=small,fill=(195,210,225));aux.save(A/'LATE_ASSISTED_RETURN_TO_GROUND_40M.jpg',quality=95)
(A/'evidence/RENDER_INDEX.json').write_text(json.dumps(dict(model=str(E),whole_times=times,reference_frames=[x[0]for x in ref],first_contact_s=touch,render_geometry='Existing compiled MOD4 scene; saved qpos; lighting/terrainRGBA only'),indent=2)+chr(10))
print('COMPARISON_IMAGES_SAVED',flush=True)

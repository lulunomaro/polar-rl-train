"""Render all actual IsaacLab R1 terrain mesh types and levels locally; no training."""
from pathlib import Path
import sys,json,hashlib,xml.etree.ElementTree as ET
import numpy as np,mujoco
from PIL import Image,ImageDraw,ImageFont
B=Path(__file__).resolve().parent;ROOT=Path(r'D:/claude2/fangzhen');sys.path.insert(0,str(ROOT/'runs3060/mod4v3_play_20261107'))
from eval_flatv2_final import args_for
from play_ppo_flatv1_control import Simulation
DATA=np.load(B/'evidence/TERRAIN_MESHES_ALL_LEVELS.npz');manifest=json.loads((B/'evidence/TERRAIN_MESHES_MANIFEST.json').read_text())
families=[('tiny_step_rot','交错栅格 / 小凸条','R0已接入'),('slope_for_rm_low','正向缓坡','R0已接入'),('inv_slope_for_rm_low','反向缓坡','R0已接入'),('stair_slope_for_rm_low','浅正阶','R0已接入'),('stair_slope_for_rm_mid','中级正阶','R1新增'),('inv_stair_slope_for_rm_low','浅反阶','R0已接入'),('inv_stair_slope_for_rm_mid','中级反阶','R1新增'),('random_uniform_for_rm','随机起伏','R0已接入'),('plane_for_rm_rot','平地保留组','固定level0')]
args=args_for(str(ROOT/'frozen_models/rough_r1_square15_010m_candidate_20261111/model_010m.pt'));source=Path(args.xml);tree=ET.parse(source);root=tree.getroot();root.find('compiler').set('meshdir',str(source.parent/'assets'))
world=root.find('worldbody');world.remove(world.find("geom[@name='ground']"));asset=root.find('asset');(B/'meshes').mkdir(exist_ok=True)
for level in range(4):
 for j,(family,_,_) in enumerate(families):
  key=f'level{level}__{family}';pos=f'{j*12.} {level*12.} 0';name='terrain_'+key
  if family=='plane_for_rm_rot':ET.SubElement(world,'geom',name=name,type='box',size='4.5 4.5 .01',pos=f'{j*12.} {level*12.} -.01',rgba='.52 .61 .67 1',contype='0',conaffinity='0',group='5');continue
  v=DATA[key+'__vertices'];f=DATA[key+'__faces'];obj=B/'meshes'/(key+'.obj')
  with obj.open('w',encoding='ascii') as file:
   for x,y,z in v:file.write(f'v {x:.8f} {y:.8f} {z:.8f}\n')
   for a,b,c in f+1:file.write(f'f {a} {b} {c}\n')
  ET.SubElement(asset,'mesh',name=name,file=str(obj));ET.SubElement(world,'geom',name=name,type='mesh',mesh=name,pos=pos,rgba='.52 .61 .67 1',contype='0',conaffinity='0',group='5')
visual=root.find('visual')
if visual is None:visual=ET.SubElement(root,'visual')
global_=visual.find('global')
if global_ is None:global_=ET.SubElement(visual,'global')
global_.set('offwidth','1300');global_.set('offheight','1000')
scene=B/'terrain_gallery_scene.xml';tree.write(scene,encoding='utf-8',xml_declaration=True);args.xml=str(scene);sim=Simulation(args);m,d=sim.env.m,sim.env.d
m.vis.headlight.ambient[:]=[.65,.65,.65];m.vis.headlight.diffuse[:]=[.8,.8,.8];m.vis.headlight.specular[:]=[.1,.1,.1];m.vis.map.znear=.001
allids=[m.geom('terrain_'+f'level{l}__{family}').id for l in range(4) for family,_,_ in families];opt=mujoco.MjvOption();opt.geomgroup[:]=1;opt.geomgroup[5]=0
font=ImageFont.truetype(r'C:/Windows/Fonts/msyh.ttc',27);small=ImageFont.truetype(r'C:/Windows/Fonts/msyh.ttc',19);heading=ImageFont.truetype(r'C:/Windows/Fonts/msyh.ttc',38)
(B/'single').mkdir(exist_ok=True);images=[]
def ground(v,f,x,y):
 tri=v[f];a=tri[:,0,:2];u=tri[:,1,:2]-a;w=tri[:,2,:2]-a;p=np.array([x,y])-a;det=u[:,0]*w[:,1]-u[:,1]*w[:,0];valid=np.abs(det)>1e-12
 b=np.zeros(len(det));c=b.copy();b[valid]=(p[valid,0]*w[valid,1]-p[valid,1]*w[valid,0])/det[valid];c[valid]=(u[valid,0]*p[valid,1]-u[valid,1]*p[valid,0])/det[valid];ok=valid&(b>=-1e-5)&(c>=-1e-5)&(b+c<=1.00001)
 z=tri[:,0,2]+b*(tri[:,1,2]-tri[:,0,2])+c*(tri[:,2,2]-tri[:,0,2]);return float(z[ok].max()) if ok.any() else 0.
with mujoco.Renderer(m,height=800,width=1200) as renderer:
 for level in range(4):
  sheet=Image.new('RGB',(2400,1770),(20,25,32));sd=ImageDraw.Draw(sheet);sd.text((30,16),f'Isaac Lab 实际训练地形｜Level {level}｜8类Rough＋平地保留组',font=heading,fill='white');sd.text((30,68),'同一类型沿level0→3升难度，类型之间并行训练；平地组固定level0。真实网格，无高度夸张；机器人作比例参考。',font=font,fill=(185,202,217))
  sd.text((30,108),'R0/R1标签表示地形类型最早引入的阶段，不表示那个阶段已经完成此level。',font=small,fill=(233,190,116))
  for j,(family,cn,phase) in enumerate(families):
   key=f'level{level}__{family}';v=DATA[key+'__vertices'];f=DATA[key+'__faces'];tilex=j*12.;tiley=level*12.
   m.geom_group[allids]=5;m.geom_group[m.geom('terrain_'+key).id]=1
   x=-1.8;y=-.6;z=ground(v,f,x,y);d.qpos[:3]=[tilex+x,tiley+y,z+sim.env.bank_z];d.qvel[:]=0.;mujoco.mj_forward(m,d)
   cam=mujoco.MjvCamera();cam.type=mujoco.mjtCamera.mjCAMERA_FREE;cam.lookat[:]=[tilex,tiley,float((v[:,2].min()+v[:,2].max())*.5)];cam.distance=12.;cam.azimuth=125.;cam.elevation=-32.
   renderer.update_scene(d,camera=cam,scene_option=opt);renderer.scene.flags[mujoco.mjtRndFlag.mjRND_SHADOW]=False;im=Image.fromarray(renderer.render());draw=ImageDraw.Draw(im);draw.rectangle((0,0,1200,94),fill=(20,25,32));draw.text((20,10),f'{cn}｜'+('平地固定level0' if family=='plane_for_rm_rot' else f'Level {level}')+f'｜{phase}',font=font,fill='white');draw.text((20,54),'Isaac Lab 原始碰撞网格 · MuJoCo本地渲染 · 9 × 9 m · 比例1:1',font=small,fill=(185,202,217))
   name=key+'.png';im.save(B/'single'/name);images.append(dict(file='single/'+name,family=family,level=level,phase=phase,sha256=hashlib.sha256((B/'single'/name).read_bytes()).hexdigest()))
   thumb=im.resize((800,533),Image.Resampling.LANCZOS);sheet.paste(thumb,((j%3)*800,145+(j//3)*540))
   if level==3 and family in ('tiny_step_rot','random_uniform_for_rm'):
    cam.lookat[:]=[tilex,tiley,ground(v,f,0.,0.)+.05];cam.distance=4.8;cam.elevation=-23.;renderer.update_scene(d,camera=cam,scene_option=opt);renderer.scene.flags[mujoco.mjtRndFlag.mjRND_SHADOW]=False;close=Image.fromarray(renderer.render());dr=ImageDraw.Draw(close);dr.rectangle((0,0,1200,70),fill=(20,25,32));dr.text((20,16),f'{cn}｜Level3近景｜无高度夸张',font=font,fill='white');close.save(B/'single'/(key+'__close.png'))
  sheet.save(B/f'rough_all_level{level}.png');print('RENDERED_LEVEL',level,flush=True)
sim.close();(B/'evidence/RENDER_COMPLETE.json').write_text(json.dumps(dict(images=images,contact_sheets=[f'rough_all_level{l}.png' for l in range(4)],source='Exact vertices/faces from frozen evaluation terrain generator; visual rendering does not run training or change robot plant',source_archive_sha256=hashlib.sha256((B/'evidence/TERRAIN_MESHES_ALL_LEVELS.npz').read_bytes()).hexdigest()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('ALL_TERRAIN_IMAGES_READY',flush=True)

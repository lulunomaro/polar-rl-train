"""Local visual playback, latest fixed Rough-v1 actor; no training or export."""
from pathlib import Path
import sys,os,json,hashlib,struct,time,math,traceback,argparse,types,xml.etree.ElementTree as ET
import numpy as np
import mujoco,mujoco.viewer,torch
B=Path(__file__).resolve().parent;ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT/'training'
sys.path.insert(0,str(ROOT/'runtime/core'))
from args_for import args_for
from play_ppo_flatv1_control import Simulation
MAN=json.loads((B/'MAP_MANIFEST.json').read_text()); FAMILIES=MAN['families']
CN=['低速宽台阶','栅格小凸条','正向坡面','反向坡面','高速宽台阶','密集浅台阶','浅反阶','高反阶','平地','随机起伏','阶梯落差']
COLS={f:next(t['col'] for t in MAN['tiles'] if t['family']==f) for f in FAMILIES}
COLORS=['.72 .51 .29 1','.36 .59 .64 1','.39 .63 .42 1','.30 .56 .48 1','.78 .47 .28 1','.48 .53 .73 1','.44 .57 .67 1','.60 .46 .68 1','.48 .52 .56 1','.64 .61 .39 1','.70 .41 .48 1']
CKPT=ROOT/'model/training_checkpoint.pt'; EXPECTED='7cc1fc6deeee3d3aba8ae8d2da31dce200079fb229a145f1cbb1cd3bfabea103'

def meshfile(tile):
 p=B/'mesh'/f'{tile}.msh'
 if not p.exists():
  p.parent.mkdir(exist_ok=True);a=np.load(B/'tiles'/(tile+'.npz'));v=a['vertices'];f=a['faces']
  # A tiny hidden underside tetrahedron gives planar visual meshes nonzero volume.
  if np.ptp(v[:,2])<1e-7:
   n=len(v);v=np.vstack((v,[[0,0,-.02],[.01,0,-.02],[0,.01,-.02],[0,0,-.03]])).astype(np.float32)
   f=np.vstack((f,[[n,n+1,n+2],[n,n+3,n+1],[n,n+2,n+3],[n+1,n+3,n+2]])).astype(np.int32)
  with p.open('wb') as h:
   h.write(struct.pack('<4i',len(v),0,0,len(f)));h.write(v.astype('<f4').tobytes());h.write(f.astype('<i4').tobytes())
 return p

def tiledata(level,family):
 name=f'r{level:02d}_c{COLS[family]:02d}';a=np.load(B/'tiles'/(name+'.npz'))
 return name,a['vertices'],a['faces']

def heightfield(tile):
 cache=B/(tile+'_hf_v2.npz')
 if cache.exists():return np.load(cache)['h']
 path=meshfile(tile);m=mujoco.MjModel.from_xml_string(f'<mujoco><asset><mesh name="t" file="{path.as_posix()}"/></asset><worldbody><geom type="mesh" mesh="t"/></worldbody></mujoco>');d=mujoco.MjData(m);mujoco.mj_forward(m,d)
 grid=np.linspace(-4.5,4.5,181);h=np.zeros((181,181));vec=np.array([0.,0.,-1.]);p=np.array([0.,0.,10.]);gid=np.zeros(1,dtype=np.int32)
 for iy,y in enumerate(grid):
  for ix,x in enumerate(grid):
   p[:2]=np.clip([x+1.7e-5,y+2.9e-5],-4.5+1e-4,4.5-1e-4);dist=mujoco.mj_ray(m,d,p,vec,None,True,-1,gid)
   if dist<0:raise RuntimeError(f'Ground-ray miss: {tile} {x} {y}')
   h[iy,ix]=10-dist
 np.savez_compressed(cache,h=h)
 return h

def make_scene(level,family):
 args=args_for(str(CKPT));source=Path(args.xml)
 assert hashlib.sha256(source.read_bytes()).hexdigest()=='77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f','Robot source identity changed'
 tree=ET.parse(source);root=tree.getroot();root.find('compiler').set('meshdir',str(source.parent/'assets'))
 world=root.find('worldbody');ground=world.find("geom[@name='ground']");world.remove(ground)
 tile,v,f=tiledata(level,family);idx=FAMILIES.index(family)
 ET.SubElement(root.find('asset'),'mesh',name='tile_visual',file=str(meshfile(tile)))
 ET.SubElement(world,'geom',type='mesh',mesh='tile_visual',contype='0',conaffinity='0',rgba=COLORS[idx],group='1')
 h=None
 if family in (FAMILIES[0],FAMILIES[4]):
  ET.SubElement(world,'geom',name='ground',type='box',pos='0 0 -.10',size='4.5 4.5 .1',contype='1',conaffinity='2',group='5')
  for k,z in enumerate(np.unique(v[:,2])):
   if z<=1e-6:continue
   top=v[v[:,2]>=z-1e-6];lo=top[:,:2].min(0);hi=top[:,:2].max(0)
   center=(lo+hi)*.5;half=(hi-lo)*.5
   ET.SubElement(world,'geom',name=f'step_{k}',type='box',pos=f'{center[0]} {center[1]} {z/2}',size=f'{half[0]} {half[1]} {z/2}',contype='1',conaffinity='2',group='5')
 else:
  h=heightfield(tile);mn=float(h.min());span=max(float(h.max()-mn),.001)
  ET.SubElement(root.find('asset'),'hfield',name='tile_collision',nrow='181',ncol='181',size=f'4.5 4.5 {span} .2')
  ET.SubElement(world,'geom',name='ground',type='hfield',hfield='tile_collision',pos=f'0 0 {mn}',contype='1',conaffinity='2',group='5')
 root.find('visual/global').set('offwidth','1600');root.find('visual/global').set('offheight','1000')
 path=B/f'scene_{tile}_{os.getpid()}.xml';tree.write(path,encoding='utf8',xml_declaration=True)
 return path,v,h

class SafetyStop(Exception):pass

class Replay(Simulation):
 def __init__(self,level=0,family=FAMILIES[0],direction='up',show=False):
  self.level=level;self.family=family;self.direction=direction;self.reset_count=0;self.reason='';self.closure=0.;self.just_reset=False
  assert hashlib.sha256(CKPT.read_bytes()).hexdigest()==EXPECTED,'Checkpoint identity changed'
  scene,v,h=make_scene(level,family);self.vertices=v;self.h=h
  args=args_for(str(CKPT));args.xml=str(scene);args.term_height=-100.;args.vx=1.;args.height=.28
  super().__init__(args)
  if h is not None:
   mn=float(h.min());span=max(float(h.max()-mn),.001);self.env.m.hfield_data[:]=((h-mn)/span).ravel()
  self.env.dt=.0025;self.env.decim=8;self.env.m.opt.timestep=.0025
  self.env.m.vis.headlight.ambient[:]=[.65,.65,.65];self.env.m.vis.headlight.diffuse[:]=[.8,.8,.8];self.env.m.vis.headlight.specular[:]=[.08,.08,.08]
  self.pairs=[(self.env.m.site(el.get('site1')).id,self.env.m.site(el.get('site2')).id) for el in ET.parse(scene).getroot().findall('equality/connect')]
  owner=self
  def physics(env,a):
   a=a.clamp(-env.action_clip,env.action_clip)
   for j in range(env.decim):
    if j%4==0:env.d.ctrl[env.act_ids]=env._torque(a).detach().cpu().numpy().reshape(-1)
    mujoco.mj_step(env.m,env.d)
    if not np.isfinite(env.d.qpos).all() or not np.isfinite(env.d.qvel).all():raise SafetyStop('nonfinite')
    owner.closure=max(float(np.linalg.norm(env.d.site_xpos[u]-env.d.site_xpos[w])) for u,w in owner.pairs)
    if owner.closure>.002:raise SafetyStop('closure > 2mm')
   env.a_prev=a.detach().to(env.device)
   return env.state()
  self.env.step=types.MethodType(physics,self.env)
  self.reset_standing();self.paused=False
  if show:
   self.viewer=mujoco.viewer.launch_passive(self.env.m,self.env.d)
   self.viewer.opt.geomgroup[5]=0
   self.viewer.cam.type=mujoco.mjtCamera.mjCAMERA_FREE;self.viewer.cam.lookat[:]=[-.5,0,.45]
   self.viewer.cam.distance=4.6;self.viewer.cam.azimuth=30.;self.viewer.cam.elevation=-22.
 def ground(self,x,y):
  if self.h is None:
   v=self.vertices;z=0.
   for height in np.unique(v[:,2]):
    if height<=0:continue
    top=v[v[:,2]>=height-1e-6];lo=top[:,:2].min(0);hi=top[:,:2].max(0)
    if lo[0]<=x<=hi[0] and lo[1]<=y<=hi[1]:z=float(height)
   return z
  ix=np.clip((x+4.5)*20,0,180);iy=np.clip((y+4.5)*20,0,180)
  x0=min(int(ix),179);y0=min(int(iy),179);a=ix-x0;b=iy-y0;h=self.h
  return float((1-b)*((1-a)*h[y0,x0]+a*h[y0,x0+1])+b*((1-a)*h[y0+1,x0]+a*h[y0+1,x0+1]))
 def reset_standing(self):
  super().reset_standing()
  x=.25 if self.direction=='down' else -3.9
  self.env.d.qpos[:3]=[x,0,self.ground(x,0)+self.env.bank_z]
  self.env.d.qvel[:]=0.;mujoco.mj_forward(self.env.m,self.env.d)
  self.env.d.time=0.;self.reset_count+=1;self.just_reset=True
  self.z=float(self.env.z)-self.ground(x,0)
 def step(self,pressed):
  if self.paused:return self.telemetry()
  self.just_reset=False
  try:super().step(pressed)
  except SafetyStop as exc:self.reason=str(exc);self.reset_standing()
  x,y=self.env.d.qpos[:2];self.z=float(self.env.z)-self.ground(x,y);self.cos_tilt=float(self.env.cos_tilt)
  if self.z<.18 or self.cos_tilt<.766:
   self.reason='height / tilt reset';self.reset_standing()
  elif abs(x)>4.1 or abs(y)>4.1:
   self.reason='tile boundary';self.reset_standing()
  return self.telemetry()

def map_model():
 p=B/'full_map_scene.xml'
 if not p.exists():
  root=ET.Element('mujoco',model='SCUT Rough-v1 FULL MAP 10x75 - local recipe reconstruction')
  ET.SubElement(root,'compiler',angle='radian');visual=ET.SubElement(root,'visual');ET.SubElement(visual,'global',offwidth='2400',offheight='1600');ET.SubElement(visual,'headlight',ambient='.65 .65 .65',diffuse='.7 .7 .7',specular='.05 .05 .05');ET.SubElement(visual,'map',znear='.001',zfar='20')
  ET.SubElement(root,'statistic',center='0 0 0',extent='400');asset=ET.SubElement(root,'asset');world=ET.SubElement(root,'worldbody')
  for t in MAN['tiles']:
   k=t['name'];ET.SubElement(asset,'mesh',name=k,file=str(meshfile(k)))
   ET.SubElement(world,'geom',name=k,type='mesh',mesh=k,pos=f'{(t["row"]+.5)*9-45} {(t["col"]+.5)*9-337.5} 0',contype='0',conaffinity='0',rgba=COLORS[FAMILIES.index(t['family'])])
  ET.ElementTree(root).write(p,encoding='utf8',xml_declaration=True)
 return mujoco.MjModel.from_xml_path(str(p))

def map_view():
 m=map_model();d=mujoco.MjData(m);mujoco.mj_forward(m,d)
 with mujoco.viewer.launch_passive(m,d) as viewer:
  viewer.cam.lookat[:]=[0,0,.2];viewer.cam.distance=1050.;viewer.cam.azimuth=180.;viewer.cam.elevation=-75.
  print('FULL_MAP_VIEWER_READY',flush=True)
  while viewer.is_running():viewer.sync();time.sleep(.04)

def render_map():
 from PIL import Image,ImageDraw,ImageFont
 m=map_model();d=mujoco.MjData(m);mujoco.mj_forward(m,d)
 font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',28);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21)
 cam=mujoco.MjvCamera();cam.lookat[:]=[0,0,.2];cam.distance=410.;cam.azimuth=180.;cam.elevation=-80.
 opt=mujoco.MjvOption();opt.geomgroup[5]=0
 def cropped(r):
  r.update_scene(d,camera=cam,scene_option=opt);r.scene.flags[mujoco.mjtRndFlag.mjRND_SHADOW]=False
  im=Image.fromarray(r.render());arr=np.asarray(im);mask=np.any(arr>12,axis=2);yy,xx=np.where(mask)
  return im.crop((max(0,xx.min()-15),max(0,yy.min()-15),min(im.width,xx.max()+16),min(im.height,yy.max()+16)))
 with mujoco.Renderer(m,height=950,width=2200) as r:
  im=cropped(r);im=im.resize((2140,round(im.height*2140/im.width)))
  canvas=Image.new('RGB',(2200,im.height+240),(23,28,36));canvas.paste(im,(30,105));draw=ImageDraw.Draw(canvas)
  draw.text((35,15),'本轮 SCUT Rough-v1 全地图｜10行 × 75列｜750块地形｜11类',font=font,fill='white')
  draw.text((35,62),'按本轮训练配方在本机重建；每块9×9m。短边10档难度，长边75个地形列，净地形90×675m。',font=small,fill=(195,208,222))
  draw.text((35,im.height+120),'左至右：低速宽阶 → 栅格 → 正坡 → 反坡 → 高速宽阶 → 浅正阶 → 浅反阶 → 高反阶 → 平地 → 随机起伏 → 阶梯落差',font=small,fill='white')
  draw.text((35,im.height+165),'地形高度按实际比例显示。11类地形同时分布在地图中，难度沿短边递增。',font=small,fill=(195,208,222))
  canvas.save(B/'full_map_overview.png')
  panels=[];labels=['低速宽阶5列 / 栅格10列 / 正坡5列 / 反坡5列','高速宽阶5列 / 浅正阶5列 / 浅反阶5列 / 高反阶10列','平地15列 / 随机起伏5列 / 阶梯落差5列']
  for part in range(3):
   m.geom_group[:]=5
   for t in MAN['tiles']:
    if part*25<=t['col']<(part+1)*25:m.geom_group[m.geom(t['name']).id]=0
   cam.lookat[:]=[0,(part*25+12.5)*9-337.5,.2];cam.distance=155.;cam.elevation=-75.
   im=cropped(r);im=im.resize((1800,round(im.height*1800/im.width)))
   panel=Image.new('RGB',(1840,im.height+100),(23,28,36));pd=ImageDraw.Draw(panel)
   pd.text((25,10),f'第{part*25+1}～{(part+1)*25}列｜'+labels[part],font=small,fill='white');panel.paste(im,(20,65));panels.append(panel)
  sheet=Image.new('RGB',(1840,100+sum(p.height for p in panels)),(23,28,36));sd=ImageDraw.Draw(sheet);sd.text((25,15),'完整地图分三段放大｜全部750块地形｜原始高度比例',font=font,fill='white')
  y=85
  for panel in panels:sheet.paste(panel,(0,y));y+=panel.height
  sheet.save(B/'full_map_three_panels.png')
 print('FULL_MAP_IMAGES_READY',flush=True)

def gui():
 from manual_control import run
 run()

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=['play','map','render-map','smoke'],default='play');a=p.parse_args()
 try:
  if a.mode=='map':map_view()
  elif a.mode=='render-map':render_map()
  elif a.mode=='smoke':
   rows=[]
   for direction in ['up','down']:
    s=Replay(direction=direction)
    for _ in range(100):s.step({'w'})
    rows.append(dict(direction=direction,x=float(s.env.d.qpos[0]),vx=float(s.env.vx),closure=s.closure,resets=s.reset_count-1));s.close()
   print(json.dumps(rows),flush=True)
  else:gui()
 except Exception:
  (B/('error_'+a.mode+'.log')).write_text(traceback.format_exc(),encoding='utf8');raise


from pathlib import Path
p=Path(r'D:/claude2/fangzhen/tmp/rough_v1_local_showcase_20261112/showcase.py')
s=p.read_text(encoding='utf-8-sig').replace("viewer.cam.distance=460.;viewer.cam.azimuth=0.;viewer.cam.elevation=-75.","viewer.cam.distance=1050.;viewer.cam.azimuth=180.;viewer.cam.elevation=-75.")
a=s.index('def render_map():');b=s.index('\ndef gui():',a)
s=s[:a]+'''def render_map():
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
  draw.text((35,62),'保存配方＋seed66本机重建；每块9×9m。短边10档难度，长边75个地形列，净地形90×675m。',font=small,fill=(195,208,222))
  draw.text((35,im.height+120),'左至右：低速宽阶 → 栅格 → 正坡 → 反坡 → 高速宽阶 → 浅正阶 → 浅反阶 → 高反阶 → 平地 → 随机起伏 → 阶梯落差',font=small,fill='white')
  draw.text((35,im.height+165),'原始高度比例1:1；这是本机配方重建图，与目标机随机网格不作逐字节相同声明。边界外沿另有10m。',font=small,fill=(195,208,222))
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
''' + s[b:]
p.write_text(s,encoding='utf8')

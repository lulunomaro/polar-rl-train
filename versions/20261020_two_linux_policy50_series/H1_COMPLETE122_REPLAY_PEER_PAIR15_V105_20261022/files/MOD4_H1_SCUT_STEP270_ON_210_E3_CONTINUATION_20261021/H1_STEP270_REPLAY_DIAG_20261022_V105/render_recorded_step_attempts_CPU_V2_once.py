from pathlib import Path
import hashlib,json,math,time,traceback
import numpy as np
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent;R=D/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def hull(points):
 points=sorted(set(map(tuple,points)))
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 low=[];high=[]
 for p in points:
  while len(low)>1 and cross(low[-2],low[-1],p)<=0:low.pop()
  low.append(p)
 for p in reversed(points):
  while len(high)>1 and cross(high[-2],high[-1],p)<=0:high.pop()
  high.append(p)
 return low[:-1]+high[:-1]
def local_points(s):
 if s['type']=='Mesh':p=np.array(s['points'])
 elif s['type']=='Cube':p=np.array([[x,y,z] for x in (-.5,.5) for y in (-.5,.5) for z in (-.5,.5)])*s['size']
 else:
  axis=s['axis'];other=[i for i in range(3) if i!=axis];rows=[]
  if s['type']=='Capsule':
   for end in (-1,1):
    for latitude in np.linspace(-np.pi/2,np.pi/2,7):
     for angle in np.linspace(0,2*np.pi,18,endpoint=False):
      q=np.zeros(3);q[axis]=end*s['height']/2+s['radius']*np.sin(latitude);q[other]=s['radius']*np.cos(latitude)*np.array([np.cos(angle),np.sin(angle)]);rows.append(q)
  else:
   for end in (-1,1):
    for angle in np.linspace(0,2*np.pi,24,endpoint=False):
     q=np.zeros(3);q[axis]=end*s['height']/2;q[other]=s['radius']*np.array([np.cos(angle),np.sin(angle)]);rows.append(q)
  p=np.array(rows)
 return p@np.array(s['linear_body_from_shape']).T+np.array(s['origin_body_m'])
def main():
 z=np.load(D/'SELECTED_RECORDED_MOTION.npz',allow_pickle=False);k=np.load(D/'RECORDED_KINEMATIC_RECONSTRUCTION.npz',allow_pickle=False);meta=json.loads((R/'RECORDED_USD_KINEMATICS_CPU_ACTUAL.json').read_bytes());names=meta['body_names'];shapes=meta['shapes'];byid={x['env_id']:x for x in meta['case_summaries']}
 cases=[(1912,'跳得够高，但还离台阶很远'),(17789,'前进更远，但片段内轮底仍不够高'),(16932,'前进和抬轮的时机尚未对齐')]
 font=lambda n:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n);f=font(19);small=font(15);title=font(25)
 cam=np.array([3.,-5.,3.]);forward=-cam/np.linalg.norm(cam);right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,forward)
 def proj(p):
  p=np.asarray(p);return np.stack((280+380*(p@right),470-380*(p@up)),-1)
 def polygon(dr,p,color,edge='#364152'):
  pts=hull(proj(p));
  if len(pts)>2:dr.polygon(pts,fill=color,outline=edge)
 cloud=[local_points(s) for s in shapes];frames=[];selected=[]
 for ci,(env_id,label) in enumerate(cases):
  row=byid[env_id];e=row['column'];selected.append(row)
  for frame in range(48):
   im=Image.new('RGB',(1100,640),'#f4f6fa');dr=ImageDraw.Draw(im)
   dr.text((24,16),'跳上270mm台阶：真实训练记录回放',font=title,fill='#182b46')
   dr.text((24,55),'100Hz记录位姿 + 原USD碰撞几何重建 | 非重新物理仿真 | 原片段0.48秒，4倍慢放',font=small,fill='#54647b')
   dr.rounded_rectangle((18,87,700,565),radius=14,fill='white',outline='#dce3ec');dr.text((36,103),f'案例{ci+1} · 环境 {env_id}：{label}',font=f,fill='#203e65')
   floor=np.array([[-.45,-.7,0],[1.2,-.7,0],[1.2,.7,0],[-.45,.7,0]]);polygon(dr,floor,'#e1e8ed','#b5c2cc')
   x0,x1,y0,y1,h=.35,1.15,-.6,.6,.27
   for p in ([(x0,y0,0),(x0,y1,0),(x0,y1,h),(x0,y0,h)],[(x0,y0,0),(x1,y0,0),(x1,y0,h),(x0,y0,h)],[(x0,y0,h),(x1,y0,h),(x1,y1,h),(x0,y1,h)]):polygon(dr,np.array(p),'#f4c76e','#ba8732')
   groups=[]
   for s,p in zip(shapes,cloud):
    mat=k['body_pose'][frame,e,names.index(s['body'])];world=p@mat[:3,:3].T+mat[:3,3];color='#355d92' if s['body']=='chassis' else '#253344' if 'wheel' in s['body'] or 'roller' in s['body'] else '#ce7847' if any(a in s['body'] for a in ('input','coupler','rocker')) else '#72a5a1';groups.append((float(world.mean(0)@forward),world,color))
   for _,p,color in sorted(groups,key=lambda x:x[0],reverse=True):polygon(dr,p,color)
   dr.text((42,530),'金色 = 真实台阶尺寸；蓝/橙/绿 = 原模型碰撞几何',font=small,fill='#54647b')
   dr.rounded_rectangle((716,87,1082,565),radius=14,fill='white',outline='#dce3ec');dr.text((735,104),'双轮同时满足：够高 + 到达边缘',font=f,fill='#203e65')
   X=lambda x:750+(x+.35)/1.05*300;Y=lambda zz:400-zz/.5*220
   dr.rectangle((X(.35),Y(.27),X(.7),Y(0)),fill='#f8e2ad');dr.line((X(.35),Y(0),X(.35),Y(.5)),fill='#c9922a',width=2);dr.line((X(-.35),Y(.27),X(.7),Y(.27)),fill='#cf6947',width=2)
   lows=k['wheel_min'][:,e];highs=k['wheel_max'][:,e];trackx=highs[:,:,0].min(-1);trackz=lows[:,:,2].min(-1);pts=[(X(float(x)),Y(float(zz))) for x,zz in zip(trackx,trackz)];dr.line(pts,fill='#8da8c7',width=3)
   cx,cy=pts[frame];dr.ellipse((cx-6,cy-6,cx+6,cy+6),fill='#1e5ba5');dr.text((750,418),'横轴：两轮中较落后的前缘 x',font=small,fill='#54647b');dr.text((750,442),'竖轴：两轮中较低的轮底高度',font=small,fill='#54647b')
   gap=.35-trackx[frame];dr.text((738,478),f'距台阶边缘：{gap*1000:.0f} mm',font=f,fill='#a15325');dr.text((738,510),f'当前轮底高度：{trackz[frame]*1000:.0f} mm',font=f,fill='#203e65')
   dr.text((24,585),f'记录控制步 {int(z["control_rows"][frame])} | 请求前进{(.8 if bool(z["public_request"][frame,e]) else 0.):.1f} m/s | 实际世界vx {z["root13"][frame,e,7]:+.2f} m/s | 无已记录越缘成功',font=small,fill='#243b58');dr.text((24,612),'仅重放保留的连续0.48秒，不能补回已按授权清除的更早原始帧。',font=small,fill='#6b7789')
   frames.append(im)
   if frame==row['apex_row']:im.save(D/f'case_V2_{env_id}_apex.png')
 frames[0].save(D/'STEP270_RECORDED_REPLAY_V2.gif',save_all=True,append_images=frames[1:],duration=40,loop=0,optimize=False)
 frames[48].save(D/'STEP270_REPLAY_POSTER_V2.png')
 # Contact sheet is useful even when inline animation is unavailable.
 sheet=Image.new('RGB',(1100,640*3),'white')
 for j,(env_id,_) in enumerate(cases):sheet.paste(Image.open(D/f'case_V2_{env_id}_apex.png'),(0,j*640))
 sheet.save(D/'STEP270_REPLAY_CASES_V2.png')
 artifacts=[]
 for p in (D/'STEP270_RECORDED_REPLAY_V2.gif',D/'STEP270_REPLAY_POSTER_V2.png',D/'STEP270_REPLAY_CASES_V2.png'):
  artifacts.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
 put('RECORDED_REPLAY_RENDER_V2_CPU_ACTUAL.json',dict(epoch=time.time(),frames=len(frames),source_dt=.01,display_frame_duration_ms=40,slowdown=4,recorded_seconds_each_case=.48,cases=selected,artifacts=artifacts,renderer='Pillow CPU orthographic collider visualization; no simulation integration',original_mesh_and_capsule_colliders=True,not_new_FINAL_policy_evaluation=True,no_GPU_optimizer_or_training_change=True))
 print(json.dumps(dict(rendered=True,frames=len(frames),artifacts=artifacts)))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('RENDER_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_rerun_same_once=True));raise

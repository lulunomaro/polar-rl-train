"""Actual recorded body poses + original collider geometry; no policy or physics."""
from pathlib import Path
import argparse,hashlib,json,math,time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from PIL import Image

def rotation(q):
 x,y,z,w=np.asarray(q,float);n=x*x+y*y+z*z+w*w;assert n>0;q=np.asarray(q)/math.sqrt(n);x,y,z,w=q
 return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def hull(points):
 p=sorted(set(map(tuple,points)))
 if len(p)<=2:return np.asarray(p)
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 low=[];high=[]
 for a in p:
  while len(low)>=2 and cross(low[-2],low[-1],a)<=0:low.pop()
  low.append(a)
 for a in reversed(p):
  while len(high)>=2 and cross(high[-2],high[-1],a)<=0:high.pop()
  high.append(a)
 return np.asarray(low[:-1]+high[:-1])
def local_points(s):
 kind=s['type']
 if kind=='Mesh':p=np.asarray(s['points'],float)
 elif kind=='Cube':p=np.asarray([[a,b,c] for a in (-.5,.5) for b in (-.5,.5) for c in (-.5,.5)])*s['size']
 elif kind in ('Cylinder','Capsule'):
  theta=np.linspace(0,2*np.pi,32,endpoint=False);rings=[]
  for z in (-s['height']/2,s['height']/2):rings.append(np.stack((s['radius']*np.cos(theta),s['radius']*np.sin(theta),np.full_like(theta,z)),-1))
  p=np.concatenate(rings)
  if kind=='Capsule':
   for sign in (-1,1):
    for phi in np.linspace(0,np.pi/2,7):
     rr=s['radius']*np.cos(phi);zz=sign*(s['height']/2+s['radius']*np.sin(phi));p=np.concatenate((p,np.stack((rr*np.cos(theta),rr*np.sin(theta),np.full_like(theta,zz)),-1)))
  axis=s['axis'];p=p[:,[2,0,1] if axis==0 else [0,2,1] if axis==1 else [0,1,2]]
 elif kind=='Sphere':
  p=np.asarray([[s['radius']*np.cos(a)*np.cos(b),s['radius']*np.sin(a)*np.cos(b),s['radius']*np.sin(b)] for a in np.linspace(0,2*np.pi,32) for b in np.linspace(-np.pi/2,np.pi/2,17)])
 else:raise ValueError('Unknown original collider '+kind)
 return p@np.asarray(s['linear_body_from_shape']).T+np.asarray(s['origin_body_m'])
def project(p):return np.stack((p[...,0]+.24*p[...,1],p[...,2]+.08*p[...,1]),-1)
def artifact(p):return dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--stage',required=True);args=parser.parse_args();S=Path(args.stage).resolve();R=S/'reports'
 receipt=json.loads((R/'FROZEN_NATIVE86_SINGLE_COMPLETE_ATTEMPT_RETURNED_ACTUAL.json').read_bytes())
 assert receipt['actual_finite_returned'] and receipt['all_own_children_actual_out'] and receipt['actual_result'] and not receipt['original_error']
 status=receipt['actual_result']['result'];assert status['Pi_parameters_and_normalizers_literal_unchanged']
 root=S/'actual_72';geo=json.loads((root/'ACTUAL_RENDER_GEOMETRY.json').read_bytes())
 frames_path=root/'attempt/ACTUAL_SINGLE_ATTEMPT_FRAMES.jsonl';controls_path=root/'attempt/ACTUAL_SINGLE_ATTEMPT_CONTROLS.jsonl'
 records=[json.loads(line) for line in frames_path.read_text('utf8').splitlines() if line.strip()]
 controls=[json.loads(line) for line in controls_path.read_text('utf8').splitlines() if line.strip()]
 assert records and len(records)==status['physics_frames'] and len(controls)==status['controls']
 assert all(r['physics_row']==i+1 for i,r in enumerate(records))
 select=list(range(3,len(records),4))
 if not select:select=[len(records)-1]
 if select[-1]!=len(records)-1:select.append(len(records)-1)
 origin=np.asarray(status['environment_origin_m']);names=geo['body_names'];shapes=[(s,local_points(s)) for s in geo['shapes']]
 chosen=[records[i] for i in select];poses=np.asarray([r['state']['body_position31_world'] for r in chosen])-origin
 xmin=min(-.4,float(poses[...,0].min())-.15);xmax=max(1.4,float(poses[...,0].max())+.15)
 zmin=min(-.06,float(poses[...,2].min())-.08);zmax=max(.9,float(poses[...,2].max())+.15)
 fig,ax=plt.subplots(figsize=(10,6),dpi=110);images=[]
 for number,row in enumerate(chosen):
  ax.clear();state=row['state'];pos=np.asarray(state['body_position31_world'])-origin;quat=state['body_quaternion31_sdk_xyzw']
  ground=project(np.array([[xmin,-.6,0],[xmax,-.6,0],[xmax,.6,0],[xmin,.6,0]]));ax.add_patch(Polygon(ground,color='#e6e9ed'))
  for face,col in [([[.35,-.6,0],[.35,.6,0],[.35,.6,.27],[.35,-.6,.27]],'#8b98a8'),([[.35,-.6,.27],[1.15,-.6,.27],[1.15,.6,.27],[.35,.6,.27]],'#c2cbd5')]:ax.add_patch(Polygon(project(np.array(face)),facecolor=col,edgecolor='#657386',linewidth=1.1))
  world=[]
  for s,p in shapes:
   i=s['body_index'];v=p@rotation(quat[i]).T+pos[i];world.append((float(v[:,1].mean()),s,v))
  for _,s,v in sorted(world,reverse=True,key=lambda x:x[0]):
   points=hull(project(v));body=s['body'];col='#293a4b' if 'wheel' in body else '#b7c6d4' if body=='chassis' else '#d98b4e' if any(x in body for x in ('crank','rocker')) else '#738ba1'
   if len(points)>=3:ax.add_patch(Polygon(points,facecolor=col,edgecolor='#34495e',linewidth=.65,alpha=.98))
  control=controls[min(row['control']-1,len(controls)-1)];c=control['actual_pre_reset']
  ax.set_xlim(xmin,xmax+.15);ax.set_ylim(zmin,zmax);ax.set_aspect('equal');ax.grid(alpha=.14)
  ax.set_xlabel('Forward projection (m)');ax.set_ylabel('Height projection (m)')
  ax.set_title('MOD4 | frozen SuperMimic native policy | full single attempt\n'+f"t={row['sim_time_s']:.3f}s   public age={state['public_age']}   270 mm step",fontsize=12)
  ax.text(.015,.975,f"takeoff {c['takeoff_count']}   landing {c['landing_count']}   recovery {c['recovery_count']}\nstable callbacks {c['stable_callback_ticks']} / 200   request {state['public_request']}",transform=ax.transAxes,va='top',fontsize=10,bbox=dict(facecolor='white',alpha=.85,edgecolor='#cbd2da'))
  for text in list(fig.texts):text.remove()
  fig.text(.5,.025,'Actual SDK poses and original collider geometry | deterministic native mean | same single test',ha='center',fontsize=8)
  fig.tight_layout(rect=(0,.035,1,1));fig.canvas.draw();image=Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[...,:3].copy());images.append(image)
  if number==0:image.save(S/'NATIVE86_SINGLE_ATTEMPT_START.png')
 images[-1].save(S/'NATIVE86_SINGLE_ATTEMPT_END.png');plt.close(fig)
 gif=S/'NATIVE86_FULL_SINGLE_ATTEMPT_4X_SLOW.gif';assert not gif.exists()
 images[0].save(gif,save_all=True,append_images=images[1:],duration=40,optimize=False)
 artifacts=[artifact(gif),artifact(S/'NATIVE86_SINGLE_ATTEMPT_START.png'),artifact(S/'NATIVE86_SINGLE_ATTEMPT_END.png')]
 mp4_error=None
 try:
  import imageio_ffmpeg,subprocess
  ff=imageio_ffmpeg.get_ffmpeg_exe();mp4=S/'NATIVE86_FULL_SINGLE_ATTEMPT_1X.mp4';assert not mp4.exists()
  frame_dir=S/'render_frame_pngs';frame_dir.mkdir()
  for i,im in enumerate(images):im.save(frame_dir/('frame_'+str(i).zfill(5)+'.png'))
  subprocess.run([ff,'-framerate','100','-i',str(frame_dir/'frame_%05d.png'),'-c:v','libx264','-movflags','+faststart','-pix_fmt','yuv420p',str(mp4)],check=True,capture_output=True);artifacts.append(artifact(mp4))
 except Exception as error:mp4_error=type(error).__name__+': '+str(error)
 report=dict(epoch=time.time(),passed=True,source=receipt['source'],status=status,physical_frames=len(records),controls=len(controls),rendered_frames=len(images),physics_record_rate_hz=400,video_fps=100,GIF_fps=25,GIF_playback_is_4x_slow=True,
  geometry='original collision shapes posed by actually recorded31 SDK body transforms; not a policy-generated cartoon or foreign demonstration',
  complete_single_attempt_or_explicit_cap=status['termination'],not_an_exact_training_trajectory_replay=True,no_actor_physics_or_model_read=True,artifacts=artifacts,optional_mp4_conversion_error=mp4_error)
 with (R/'FULL_NATIVE86_SINGLE_ATTEMPT_VIDEO_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(passed=True,termination=status['termination'],events=status['final_original_event_counts'],artifacts=artifacts)))
if __name__=='__main__':main()

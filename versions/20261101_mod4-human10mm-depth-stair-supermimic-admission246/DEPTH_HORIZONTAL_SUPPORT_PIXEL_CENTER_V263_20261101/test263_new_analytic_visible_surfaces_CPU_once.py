from pathlib import Path
import hashlib,json,time
import numpy as np
from depth_stair263 import target_from_depth
N=Path(__file__).resolve().parent;R=N/'reports'
with(R/'ROOT263_NEW_ANALYTIC_FIXTURE_CONSUMED.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),old_fixtures_raw_models_SDK_GPU=0),f)
h,w=48,84;theta=np.deg2rad(10.);K=np.array([[w/(2*np.tan(np.deg2rad(87/2))),0,w/2],[0,h/(2*np.tan(np.deg2rad(58/2))),h/2],[0,0,1]],dtype=np.float32)
T=np.eye(4,dtype=np.float32);T[:3,:3]=[[0,-np.sin(theta),np.cos(theta)],[-1,0,0],[0,-np.cos(theta),-np.sin(theta)]];T[:3,3]=[.15,0,.4]
v,u=np.indices((h,w),dtype=np.float32);ray=np.stack(((u+.5-K[0,2])/K[0,0],(v+.5-K[1,2])/K[1,1],np.ones((h,w))),-1)@T[:3,:3].T;o=T[:3,3]
def image(kind):
    with np.errstate(divide='ignore',invalid='ignore'):
        ground=-o[2]/ray[...,2];ground=np.where(ground>0,ground,np.inf)
        if kind=='flat':return ground.astype(np.float32)
        front=(1.25-o[0])/ray[...,0];p=o+front[...,None]*ray
        front=np.where((front>0)&(np.abs(p[...,1])<=.75)&(p[...,2]>=0)&(p[...,2]<=.27),front,np.inf)
        top=(.27-o[2])/ray[...,2];p=o+top[...,None]*ray
        top=np.where((top>0)&(p[...,0]>=1.25)&(p[...,0]<=2.75)&(np.abs(p[...,1])<=.75),top,np.inf)
        return np.minimum(ground,np.minimum(front,top if kind=='stair'else np.inf)).astype(np.float32)
rows=[]
for kind in('flat','vertical_riser_only','stair'):
    got=target_from_depth(image(kind),K,T,sensor_time=1.,control_time=1.,pixel_center_offset=.5)
    assert got['found']==(kind=='stair'),(kind,got)
    if got['found']:assert abs(got['step_height_m']-.27)<1e-5 and got['edge_distance_m']>=1.25
    rows.append(dict(kind=kind,result={k:(v.tolist()if isinstance(v,np.ndarray)else v)for k,v in got.items()}))
stale=target_from_depth(image('stair'),K,T,sensor_time=1.,control_time=1.3,pixel_center_offset=.5);assert not stale['found']and stale['reason']=='STALE_DEPTH'
report=R/'ROOT263_NEW_ANALYTIC_SURFACE_LOCALIZATION_CPU_RETURNED.json'
with report.open('x',encoding='utf8')as f:json.dump(dict(passed=True,epoch=time.time(),groups=4,rows=rows,actual_new261_raw_reads=0,models_SDK_GPU_remote=0,not_actual_navigation_or_learning=True),f,indent=2,allow_nan=False)
files=[N/'depth_stair263.py',N/'prepare263_depth_surface_and_pixel_center_once.py',Path(__file__).resolve()]+sorted(R.glob('*.json'))
idx=N/'INDEX263_DEPTH_SURFACE_SOURCE_FROZEN.json'
with idx.open('x',encoding='utf8')as f:json.dump(dict(kind='SOURCE_ONLY_PIXEL_CENTER_AND_HORIZONTAL_SUPPORT',epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in files]),f,indent=2)
print(json.dumps(dict(passed=True,index_SHA=hashlib.sha256(idx.read_bytes()).hexdigest(),stair=rows[-1]['result'])))

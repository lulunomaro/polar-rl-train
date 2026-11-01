"""Depth-derived stair targets in a gravity-level heading frame; no ground-truth map."""
from dataclasses import dataclass
import numpy as np

FEATURES=('edge_distance_m','step_height_m','lateral_center_m','target_yaw_rad','visible_width_m','visible_depth_m','confidence','depth_age_seconds','valid')

@dataclass(frozen=True)
class DetectorCfg:
    min_height_m:float=.08
    max_height_m:float=.40
    min_visible_depth_m:float=.20
    min_visible_width_m:float=.45
    range_min_m:float=.12
    range_max_m:float=4.
    height_bin_m:float=.01
    max_depth_age_seconds:float=.20

def deproject(depth,K,T_level_optical,*,depth_kind='distance_to_image_plane'):
    """SDK Z-depth metres; optical x-right/y-down/z-forward -> heading x-forward/y-left/z-up."""
    assert depth_kind=='distance_to_image_plane','Range-depth needs a separate explicitly selected projection.'
    z=np.asarray(depth,dtype=np.float32);K=np.asarray(K,dtype=np.float32);T=np.asarray(T_level_optical,dtype=np.float32)
    assert z.ndim==2 and K.shape==(3,3)and T.shape==(4,4)and K[0,0]>0 and K[1,1]>0
    assert np.isfinite(K).all()and np.isfinite(T).all()
    v,u=np.indices(z.shape,dtype=np.float32)
    optical=np.stack(((u-K[0,2])*z/K[0,0],(v-K[1,2])*z/K[1,1],z),axis=-1)
    return optical@T[:3,:3].T+T[:3,3]

def target_from_depth(depth,K,T_level_optical,*,sensor_time,control_time,cfg=DetectorCfg()):
    age=float(control_time-sensor_time);assert age>=0,'Do not use future-depth truth.'
    empty=dict(found=False,depth_age_seconds=age,features=np.array([0.,0.,0.,0.,0.,0.,0.,age,0.],dtype=np.float32),reason='NO_SUPPORTED_VISIBLE_PLATFORM')
    if age>cfg.max_depth_age_seconds:return dict(empty,reason='STALE_DEPTH')
    z=np.asarray(depth,dtype=np.float32)
    with np.errstate(invalid='ignore',over='ignore'):cloud=deproject(z,K,T_level_optical)
    mask=np.isfinite(z)&(z>=cfg.range_min_m)&(z<=cfg.range_max_m)&np.isfinite(cloud).all(-1)&(cloud[...,0]>.15)
    p=cloud[mask]
    if len(p)<30:return dict(empty,reason='INSUFFICIENT_DEPTH')
    # With gravity already removed by the IMU transform, estimate the lower visible horizontal floor.
    # This needs visible floor; occluded/unseen landing area is never filled with map truth.
    floor=float(np.quantile(p[:,2],.08));h=p[:,2]-floor;bins=np.rint(h/cfg.height_bin_m).astype(np.int32);candidates=[]
    for level in np.unique(bins[(h>=cfg.min_height_m)&(h<=cfg.max_height_m)]):
        q=p[bins==level]
        if len(q)<20:continue
        x0,x1=np.quantile(q[:,0],[.03,.97]);y0,y1=np.quantile(q[:,1],[.03,.97]);width=float(y1-y0);length=float(x1-x0)
        if width<cfg.min_visible_width_m or length<cfg.min_visible_depth_m:continue
        height=float(np.median(q[:,2])-floor);lateral=float((y0+y1)*.5);distance=float(x0)
        confidence=float(min(1.,len(q)/100.)*max(0.,1.-float(np.std(q[:,2]))/.02))
        f=np.array([distance,height,lateral,np.arctan2(lateral,distance),width,length,confidence,age,1.],dtype=np.float32)
        candidates.append(dict(found=True,features=f,edge_distance_m=distance,step_height_m=height,lateral_center_m=lateral,target_yaw_rad=float(f[3]),visible_width_m=width,visible_depth_m=length,confidence=confidence,depth_age_seconds=age,visible_floor_z_m=floor,reason='VISIBLE_HORIZONTAL_PLATFORM_CANDIDATE',landing_footprint_certified=False))
    return min(candidates,key=lambda c:c['edge_distance_m'])if candidates else empty

def normalized_features(target):
    """Fixed SI scaling, separate from original35 policy and38 critic channels."""
    f=np.asarray(target['features'],dtype=np.float32);assert f.shape==(9,)and np.isfinite(f).all()
    return f/np.array([4.,.4,2.,np.pi,2.,4.,1.,.2,1.],dtype=np.float32)

def zero_expand_input_matrix(weight,new_features=9):
    """Source-only array transform. Actual model and optimizer-ID admission is separate."""
    a=np.asarray(weight);assert a.ndim==2 and a.shape[1]in(35,38)and new_features==9
    b=np.zeros((a.shape[0],a.shape[1]+new_features),dtype=a.dtype);b[:,:a.shape[1]]=a
    return b

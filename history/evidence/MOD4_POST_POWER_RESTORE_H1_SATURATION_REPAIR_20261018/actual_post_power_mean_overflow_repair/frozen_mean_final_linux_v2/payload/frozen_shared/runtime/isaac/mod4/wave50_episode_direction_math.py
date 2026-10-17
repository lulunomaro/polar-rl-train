"""CPU component only: fixed legal entry-side direction, preserve command draws."""
import hashlib,json,numpy as np
PROFILE='WAVE50_legal_entry_episode_direction_component_v1'

def bind(xy,assignments,halfspan,extent_xy):
 xy=np.asarray(xy,dtype='<f4');extent=np.asarray(extent_xy,dtype=float)
 assert xy.ndim==2 and xy.shape[1]==2 and np.isfinite(xy).all() and extent.shape==(2,) and (extent>0).all() and halfspan>0
 owners=np.zeros(len(xy),np.int32);mask=np.zeros(len(xy),bool);sign=np.zeros(len(xy),dtype='<f4')
 for a in assignments:
  b=np.asarray(a['bounds'],dtype=float);inside=((xy>=b[0,:2])&(xy<b[1,:2])).all(1);owners+=inside
  if a['family']!='random_uniform_for_rm':continue
  center=(b[0,:2]+b[1,:2])*.5;off=xy[inside]-center
  assert (abs(off[:,0])-extent[0]-halfspan>=.4).all(), 'entry complete footprint not before/after waves'
  assert (xy[inside]-extent>=b[0,:2]+.004-1e-7).all() and (xy[inside]+extent<=b[1,:2]-.004+1e-7).all(), 'complete footprint cell containment'
  mask[inside]=True;sign[inside]=-np.sign(off[:,0])
 assert (owners==1).all(), 'actual cell assignment ownership must be unique'
 if len(xy)==20000:assert int(mask.sum())==2820, 'production20k exact actual Wave cohort'
 return mask,sign

def apply(original,mask,sign):
 x=np.asarray(original,dtype='<f4');mask=np.asarray(mask,dtype=bool);sign=np.asarray(sign,dtype='<f4')
 assert x.shape==(len(mask),3) and sign.shape==mask.shape and np.isfinite(x).all()
 assert (abs(sign[mask])==1).all() and (sign[~mask]==0).all()
 assert (abs(x[mask,0])<=.300001).all() and (x[mask,1:]==0).all()
 out=x.copy();out[mask,0]=np.abs(x[mask,0])*sign[mask]
 assert np.array_equal(out[~mask],x[~mask]) and np.array_equal(abs(out[mask,0]),abs(x[mask,0]))
 assert np.array_equal(out[:,1:],x[:,1:]) and np.array_equal(out[mask,0]==0,x[mask,0]==0)
 return out

class OriginBoundCPUCache:
 def __init__(self):self.key=None;self.value=None
 def current(self,xy,assignments,halfspan,extent_xy):
  key=hashlib.sha256(np.asarray(xy,dtype='<f4').tobytes()+json.dumps(assignments,sort_keys=True,separators=(',',':')).encode()+repr((float(halfspan),tuple(extent_xy))).encode()).hexdigest()
  if key!=self.key:self.value=bind(xy,assignments,halfspan,extent_xy);self.key=key
  return self.value

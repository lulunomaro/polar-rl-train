"""Independent reset-position component. CPU mathematics only, no live environment."""
import hashlib,json
import numpy as np
PROFILE='WAVE50_actual_cell_flat_entry_v1'

def entry_map(origins, assignments, points, span_m):
 old=np.asarray(origins,dtype=np.float64)[:,:2].copy();xy=old.copy()
 points=np.asarray(points,dtype=np.float64);extent=np.max(abs(points[:,:2]),axis=0)
 if old.ndim!=2 or old.shape[1]!=2 or not np.isfinite(old).all():raise ValueError('Invalid actual origins')
 if points.ndim!=2 or points.shape[1]!=3 or not np.isfinite(points).all():raise ValueError('Incomplete collision bank')
 if not 2.<span_m<3. or extent[0]>=.30 or extent[1]>=.30:raise ValueError('Pinned profile or complete footprint differs')
 half=span_m*.5;seen=set();groups=[];wave=np.zeros(len(old),dtype=bool)
 for a in assignments:
  key=(a['row'],a['column'])
  if key in seen:raise ValueError('Duplicate actual assignment')
  seen.add(key)
  if a['family']!='random_uniform_for_rm':continue
  b=np.asarray(a['bounds'],dtype=np.float64);center=(b[0,:2]+b[1,:2])*.5
  if b.shape!=(2,3) or not np.isfinite(b).all() or a['actual_mesh_flat']:raise ValueError('Wrong Wave cell')
  if not np.allclose(b[1,:2]-b[0,:2],9.,atol=1e-5,rtol=0):raise ValueError('Unexpected actual cell size')
  ids=np.flatnonzero(((old>=b[0,:2])&(old<b[1,:2])).all(1))
  if not len(ids):continue
  if wave[ids].any():raise ValueError('Overlapping assignments')
  wave[ids]=True;xy[ids,1]=np.clip(xy[ids,1],b[0,1]+extent[1]+.004,b[1,1]-extent[1]-.004)
  for side in (-1.,1.):
   select=ids[(old[ids,0]<center[0]) if side<0 else (old[ids,0]>=center[0])]
   values=np.unique(abs(old[select,0]-center[0]));values.sort()
   if len(values)>2:raise ValueError('Actual grid cannot fit admitted separated entry lanes')
   for rank,value in enumerate(values):
    chosen=select[np.isclose(abs(old[select,0]-center[0]),value,atol=1e-7,rtol=0)]
    xy[chosen,0]=center[0]+side*(half+.8+.85*rank)
  if (abs(xy[ids,0]-center[0])-half-extent[0]<.4-1e-6).any():raise ValueError('Complete footprint lacks flat front support')
  if ((xy[ids]-extent<b[0,:2])|(xy[ids]+extent>b[1,:2])).any():raise ValueError('Complete footprint outside actual cell')
  for i,idx in enumerate(ids):
   delta=abs(xy[ids[i+1:]]-xy[idx])
   if ((delta[:,0]<2*extent[0]+.004)&(delta[:,1]<2*extent[1]+.004)).any():raise ValueError('Reset footprints overlap')
  groups.append(dict(row=int(a['row']),column=int(a['column']),environments=len(ids),left_right=[int((xy[ids,0]<center[0]).sum()),int((xy[ids,0]>center[0]).sum())]))
 if not wave.any():raise ValueError('No actual Wave origins in supplied assignments')
 if len(np.unique(xy,axis=0))!=len(xy):raise ValueError('Duplicate reset XY')
 assert np.array_equal(xy[~wave],old[~wave])
 report=dict(profile=PROFILE,map_sha256=hashlib.sha256(np.asarray(xy,dtype='<f4').tobytes()).hexdigest(),
  changed_environments=int(np.any(xy!=old,axis=1).sum()),Wave_environments=int(wave.sum()),other_environments_unchanged=int((~wave).sum()),
  actual_Wave_groups=groups,collision_sample_extent_xy=extent.tolist(),minimum_full_flat_front_support_m=float(.8-extent[0]),
  minimum_same_side_lane_gap_m=.85,ten_wave_span_m=float(span_m),commands_and_RNG_consumption_unchanged=True,
  no_new_random_stream=True,reset_position_only_axis=True,no_actor_gate_truth_input=True,
  original2m_route_truncation_unchanged=True,not_whole_ten_wave_training_episode_certificate=True,
  CPU_map_not_physical_contact_nonpenetration_or_causal_certificate=True)
 return xy,report

class OriginBoundEntryCache:
 """Invalidate on actual origin/assignment/bank/profile bytes, including SDK moves."""
 def __init__(self):self.key=None;self.value=None;self.builds=0
 def get(self,origins,assignments,points,span_m):
  key=hashlib.sha256(np.asarray(origins,dtype='<f4').tobytes()+json.dumps(assignments,sort_keys=True,separators=(',',':')).encode()+np.asarray(points,dtype='<f4').tobytes()+repr(float(span_m)).encode()).hexdigest()
  if key!=self.key:
   self.value=entry_map(origins,assignments,points,span_m);self.key=key;self.builds+=1
  return self.value[0].copy(),dict(self.value[1],actual_input_identity_sha256=key,cache_builds=self.builds)

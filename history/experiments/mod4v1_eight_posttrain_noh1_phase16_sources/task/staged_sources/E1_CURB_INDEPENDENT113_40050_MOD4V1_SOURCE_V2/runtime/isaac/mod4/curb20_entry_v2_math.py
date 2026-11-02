"""Deterministic reset-position axis; no command, actor or gate changes."""
import hashlib,json
import numpy as np
PROFILE='CURB20_actual_cell_entry_reset_v2'

def entry_map(origins,assignments,points):
 xy=np.asarray(origins,dtype=np.float64)[:,:2].copy();old=xy.copy()
 points=np.asarray(points,dtype=np.float64)
 extent=np.max(np.abs(points[:,:2]),axis=0)
 if extent[0]>=.30 or extent[1]>=.30:raise ValueError('Pinned full collision footprint differs')
 seen=set();groups=[]
 for a in assignments:
  key=(a['row'],a['column'])
  if key in seen:raise ValueError('Duplicate actual assignment')
  seen.add(key)
  if a['family']!='random_uniform_for_rm':continue
  b=np.asarray(a['bounds']);center=(b[0,:2]+b[1,:2])/2
  mask=((old>=b[0,:2])&(old<b[1,:2])).all(1);ids=np.flatnonzero(mask)
  if not len(ids):continue
  if not np.allclose(b[1,:2]-b[0,:2],9.,atol=1e-5):raise ValueError('Unexpected actual cell size')
  # Both sides are flat supports. Rank original geometric grid x coordinates,
  # retaining distinct lanes and Y. This does not infer a policy's command.
  xy[ids,1]=np.clip(xy[ids,1],b[0,1]+extent[1]+.004,b[1,1]-extent[1]-.004)
  u=old[ids,0]-center[0]
  for side in (-1.,1.):
   select=ids[(u<0) if side<0 else (u>=0)]
   values=np.unique(np.abs(old[select,0]-center[0]));values.sort()
   if len(values)>2:raise ValueError('Grid cannot fit admitted separated entry lanes')
   for rank,value in enumerate(values):
    selected=select[np.isclose(abs(old[select,0]-center[0]),value,atol=1e-7,rtol=0)]
    xy[selected,0]=center[0]+side*(.8+.85*rank)
  if (abs(xy[ids,0]-center[0])-extent[0]-.075<.4-1e-6).any():raise ValueError('Complete footprint lacks front support')
  if ((xy[ids]-extent<b[0,:2])|(xy[ids]+extent>b[1,:2])).any():raise ValueError('Complete footprint outside actual cell')
  # Axis aligned full sampled footprint bounding rectangles are conservative.
  for i,idx in enumerate(ids):
   d=abs(xy[ids[i+1:]]-xy[idx])
   if ((d[:,0]<2*extent[0]+.004)&(d[:,1]<2*extent[1]+.004)).any():raise ValueError('Reset footprints overlap')
  groups.append(dict(row=int(a['row']),column=int(a['column']),environments=len(ids),lower_or_upper_world_x_counts=[int((xy[ids,0]<center[0]).sum()),int((xy[ids,0]>center[0]).sum())]))
 if len(np.unique(xy,axis=0))!=len(xy):raise ValueError('Reset XY duplicated')
 changed=np.any(xy!=old,axis=1)
 sha=hashlib.sha256(np.asarray(xy,dtype='<f4').tobytes()).hexdigest()
 return xy,dict(profile=PROFILE,map_sha256=sha,changed_environments=int(changed.sum()),actual_CURB_groups=groups,collision_sample_extent_xy=extent.tolist(),minimum_front_support_m=float(.8-.075-extent[0]),minimum_same_side_lane_gap_m=.85,no_new_random_stream=True,commands_unchanged=True,reset_only_axis=True,non_CURB_origins_unchanged=True,no_assignment_actor_gate_input=True)

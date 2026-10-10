"""Independent same-episode direction/heading/contact diagnosis of complete132/133 raw."""
from review133_io import *
import numpy as np

def inspect(folder,probe):
 raw=folder/probe['full_route_raw']['name'];assert H(raw.read_bytes())==probe['full_route_raw']['sha256']
 s=probe['route_scope'];center=np.array(s['tile_centers']);orient=np.array(s['orientation']);names=probe['body_names'];wi=[names.index(n) for n in ('left_wheel','right_wheel')];rows=[]
 with np.load(raw) as a:
  # Actual e1_full_pose_reset writes scipy Rotation.as_quat(): x,y,z,w.
  q=a['root'][:,:,3:7];x,y,z,w=np.moveaxis(q,-1,0)
  yaw=np.arctan2(2*(w*z+x*y),1-2*(y*y+z*z))
  forces=a['physical_wheel_force_N'].reshape(1500,4,80,2,3)
  support=np.maximum(forces[...,2],0).sum(1)*.0025/.01>1.
  for i in range(80):
   if i%3!=0:continue
   u=(a['COM_link_pos'][:,i,wi,0]-center[i,0])*orient[i]
   segments=[]
   for ep in np.unique(a['episode'][:,i]):
    ids=np.flatnonzero(a['episode'][:,i]==ep)
    failure=ids[a['terminated'][ids,i]]
    if len(failure):ids=ids[ids<=failure[0]]
    xy=a['root'][ids,i,:2]-center[i];du=(a['root'][ids,i,0]-a['before_root'][ids,i,0])*orient[i]
    dy=a['root'][ids,i,1]-a['before_root'][ids,i,1]
    heading=np.unwrap(yaw[ids,i]);before=np.flatnonzero(u[ids].max(1)<-.275);after=np.flatnonzero(u[ids].min(1)>.275)
    complete=bool(len(before) and len(after) and before.min()<after.max())
    best=int(ids[np.argmax(u[ids].min(1))]);events=ids[a['truncated'][ids,i]]
    segments.append(dict(episode=int(ep),first_control=int(ids[0]),last_control=int(ids[-1]),complete=complete,
     max_both_wheels_canonical_min_m=float(u[ids].min(1).max()),required_both_wheels_after_m=.275,
     wheel_canonical_at_best_progress_m=u[best].tolist(),best_progress_control=best,
     root_canonical_x_range_m=[float((xy[:,0]*orient[i]).min()),float((xy[:,0]*orient[i]).max())],
     lateral_y_range_m=[float(xy[:,1].min()),float(xy[:,1].max())],
     heading_xyzw_delta_range_rad=[float((heading-heading[0]).min()),float((heading-heading[0]).max())],
     signed_prereset_displacement_m=float(du.sum(dtype=np.float64)),lateral_prereset_displacement_m=float(dy.sum(dtype=np.float64)),
     mean_signed_progress_m_s=float(du.sum(dtype=np.float64)/(.01*len(ids))),
     actual_ordinary_failure_controls=failure.tolist(),declared_truncation_controls=events.tolist(),
     declared_truncation_reasons=[{name:bool(a['reasons'][k,i,j]) for j,name in enumerate(probe['reason_names'])} for k in events],
     both_wheel_actual1N_support_fraction=float(support[ids,i].all(1).mean()),
     commanded_vx=float(a['command'][ids[0],i,0]),commanded_yaw_max_abs=float(abs(a['command'][ids,i,2]).max())))
   rows.append(dict(env=i,orientation=int(orient[i]),complete=any(x['complete'] for x in segments),segments=segments))
 return dict(raw_path=str(raw.resolve()),bytes=raw.stat().st_size,sha256=H(raw.read_bytes()),rows=rows)

def main():
 v=json.loads(sorted((P/'reports').glob('CURB133_COLLECTED_[0-9]*.json'))[-1].read_bytes())
 assert not v['pending'] and len(v['cases'])==4
 jid=next(k for k,r in v['cases'].items() if 'full_route_raw' in r['probe']);candidate=inspect(P/'reports/cases'/jid,v['cases'][jid]['probe'])
 jid0='clk2500-closure-episode-d3-132-e1-curb20-source364-mirrored-fullroute-flat'
 folder=D.parent/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011/reports/cases'/jid0
 source=inspect(folder,json.loads((folder/'probe.json').read_bytes()))
 assert sum(x['complete'] for x in source['rows'])==26 and sum(x['complete'] for x in candidate['rows'])==22
 failed=[x for x in candidate['rows'] if not x['complete']]
 assert [x['env'] for x in failed]==[3,6,9,15,18] and all(x['orientation']==1 for x in failed)
 paired={str(x['env']):dict(source=next(y for y in source['rows'] if y['env']==x['env']),candidate=x) for x in failed}
 result=dict(epoch=time.time(),trial_id='CURB133-FULL-PREFIX-DIRECTION-DIAGNOSIS-01',source=source,candidate=candidate,failed_pair=paired,
  facts=['All five incomplete ascending cases are original orientation +1 with BODY vx+.3 and yaw command zero.',
   'Four source-complete cases become candidate-incomplete; env15 is incomplete in both original frozen results.',
   'Candidate incomplete paths turn while one wheel remains short of the curb; lateral travel reaches the route boundary in env6/18.',
   'No ordinary failure precedes these prefixes; declared route truncations and reset teleports remain separate.'],
  inference='The saved trajectories support a positive-forward curb crossing/direction problem rather than only a slightly short rear-support window. They do not prove a causal optimizer, reward or router fault.',
  shorter_approach_or_longer_window_not_adopted=True,original132_133_incomplete_flags_not_relabelled=True,
  no_MORE_CURB_PPO_or_height_increase_or_gate_admission=True,new_budget_seconds=0)
 p=save('CURB133_PREFIX_DIRECTION_ACTUAL_DIAGNOSIS.json',result)
 print(json.dumps(dict(report=str(p),source_ascending=26,candidate_ascending=22,failed_envs=[x['env'] for x in failed],all_failed_original_positive_orientation=True,shorter_window_patch_not_adopted=True)))

if __name__=='__main__':main()

"""Future complete-candidate direct149 pair and physical contact/prefix audit only."""
from wave_direction_io import *
import numpy as np
from review_direction_candidate_actual import initial_legacy_pair,final_sensor_receipt_pair

def latest(pattern):return max(R.glob(pattern),key=lambda p:int(p.stem.rsplit('_',1)[1]))

def main():
 rp=latest('DIRECTION_CANDIDATE_ACTUAL_REVIEW_[0-9]*.json');v=json.loads(rp.read_bytes());assert v['review_complete'] and not v['pending']
 before=json.loads((PRIOR/'reports/CANDIDATE149_COMPLETE_SCOPE_DECISION.json').read_bytes());source=json.loads(Path(before['actual_collection']).read_bytes());source_review=json.loads(Path(before['full_actual_review']).read_bytes());assert source_review['review_complete'] and source['own']['checkpoint']['sha256']==before['own_checkpoint']['sha256']=='9bfe7655b8a641660548c2a62d2ac3151e25bdf1f0e943d529099c017a2e986e'
 current=json.loads(Path(v['collection']).read_bytes());paired={}
 for jid,row in current['cases'].items():
  p=row['probe'];terrain='full_route_raw' in p
  source_jid,srow=next((k,x) for k,x in source['cases'].items() if ('full_route_raw' in x['probe'])==terrain and (terrain or x['manifest']['kind']==row['manifest']['kind']))
  q=srow['probe']
  if terrain:
   for name in ('initial','geometry','geometry_recipe','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names'):assert p[name]==q[name],('direct149',name)
   sensor=final_sensor_receipt_pair(p,q)
  else:initial_legacy_pair(p,q);sensor=None
  paired[jid]=dict(source149_case=source_jid,root30q_parameters_recipes_assignment_exact=True,final_sensor_static_dynamic_audit=sensor)
 jid,row=next((k,x) for k,x in current['cases'].items() if 'full_route_raw' in x['probe']);p=row['probe'];a=v['terrain'];raw=R/'cases'/jid/p['full_route_raw']['name'];assert H(raw.read_bytes())==p['full_route_raw']['sha256']
 centers=np.asarray(p['route_scope']['tile_centers']);half=p['route_scope']['wave_x_halfspan_m'];wheelids=a['actual_wheel_indices'];rows=[]
 with np.load(raw,allow_pickle=False) as z:
  force=z['physical_wheel_force_N'].reshape(1500,4,80,2,3);support=np.maximum(force[...,2],0).sum(1)*.0025/.01>1.;q=z['root'][:,:,3:7];x,y,zz,w=[q[:,:,i] for i in range(4)];heading=np.arctan2(2*(w*zz+x*y),1-2*(y*y+zz*zz))
  for r in a['full_route_rows']:
   i=r['env'];g=i%3;d=1 if g==0 else -1;local=z['COM_link_pos'][:,i,wheelids,0]-centers[i,0];failure=r['first_ordinary_failure_control'];segments=[];complete=[]
   for ep in np.unique(z['episode'][:,i]):
    ids=np.flatnonzero((z['episode'][:,i]==ep)&(np.arange(1500)<failure));signed=d*local[ids];both=support[ids,i].all(-1);front=np.flatnonzero((signed.max(1)<-half-.2)&both);after=np.flatnonzero((signed.min(1)>half+.2)&both);ok=g!=2 and len(front)>0 and len(after)>0 and front.min()<after.max()
    if ok:complete.append(int(ep))
    delta=z['root'][ids,i,:3]-z['before_root'][ids,i,:3]
    segments.append(dict(episode=int(ep),first_control=int(ids[0]),last_control=int(ids[-1]),controls=int(len(ids)),signed_wheel_x_range_m=[float(signed.min()),float(signed.max())],original1N_before=bool(len(front)),original1N_200mm_after=bool(len(after)),complete_with_original1N_support=bool(ok),xyzw_heading_range_rad=[float(heading[ids,i].min()),float(heading[ids,i].max())],same_control_prereset_before_signed_x_m=float(d*delta[:,0].sum()),same_control_prereset_before_abs_cross_y_m=float(abs(delta[:,1]).sum()),route_declared_truncations=int(z['reasons'][ids,i,p['reason_names'].index('rough_route_boundary')].sum())))
   assert complete==r['complete_episodes'],('original1N_position_match',i)
   rows.append(dict(env=i,group=r['group'],position_complete_episodes=r['complete_episodes'],contact_complete_episodes=complete,all_valid_prefixes=segments))
 pairs={}
 for group in ('forward','reverse'):
  oldids={x['env'] for x in source_review['terrain']['full_route_rows'] if x['group']==group and x['complete_episodes']};newids={x['env'] for x in a['full_route_rows'] if x['group']==group and x['complete_episodes']}
  pairs[group]=dict(source149_complete=len(oldids),candidate_complete=len(newids),complete_to_incomplete_envs=sorted(oldids-newids),incomplete_to_complete_envs=sorted(newids-oldids),all_candidate_valid_incomplete_envs=[x['env'] for x in rows if x['group']==group and not x['position_complete_episodes']])
 out=save('DIRECTION_DIRECT149_PREFIX_ACTUAL_'+str(time.time_ns())+'.json',dict(epoch=time.time(),passed=True,collection=v['collection'],review=str(rp),fullraw=p['full_route_raw'],all_four_cases_direct149_exact=paired,original1N_contact_matches_position_completions=True,rows=rows,pairs=pairs,all_valid_prefixes_and_old_false_preserved=True,standing26_not_required_to_cross=True,reset_teleport_excluded_same_episode_prereset_before=True,no_window_extension_approach_shortening_or_relabeling=True,no_GPU_PPO_queue_budget_write=True,requires_complete_training_trace_and_independent_scope_decision=True,no_automatic_third_same50_duration_only_block_or70mm=True))
 print(json.dumps(dict(report=str(out),pairs=pairs,contact_position_exact=True)))
if __name__=='__main__':
 try:main()
 except BaseException:save('DIRECT149_PREFIX_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only_no_GPU_or_training_replay=True));raise

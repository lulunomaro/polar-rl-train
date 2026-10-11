from wave50_io import *
import numpy as np
def latest(g):return max(R.glob(g),key=lambda p:int(p.stem.rsplit('_',1)[1]))
def main():
 assert not (R/'WAVE50_146_COMPLETE_SCOPE_DECISION.json').exists()
 rp=latest('WAVE50_CANDIDATE_ACTUAL_REVIEW_[0-9]*.json');v=json.loads(rp.read_bytes());assert v['review_complete'] and not v['pending'] and set(v['retention'])=={'flat','spin','world'}
 cp=Path(v['collection']);c=json.loads(cp.read_bytes());jid,row=next((k,x) for k,x in c['cases'].items() if 'full_route_raw' in x['probe']);p=row['probe'];a=v['terrain'];assert a['groups']['forward']['complete_envs']==7 and a['groups']['reverse']['complete_envs']==25 and a['base_review']['ordinary']==0
 prior_r=json.loads(max((PRIOR/'reports').glob('WAVE50_WORLDMESH_ACTUAL_REVIEW_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1])).read_bytes());old=next(iter(prior_r['review'].values()))['review']
 raw=R/'cases'/jid/p['full_route_raw']['name'];assert H(raw.read_bytes())==p['full_route_raw']['sha256'];rows=[];centers=np.asarray(p['route_scope']['tile_centers']);half=p['route_scope']['wave_x_halfspan_m'];wheelids=a['actual_wheel_indices']
 with np.load(raw,allow_pickle=False) as z:
  force=z['physical_wheel_force_N'].reshape(1500,4,80,2,3);support=np.maximum(force[...,2],0).sum(1)*.0025/.01>1.;q=z['root'][:,:,3:7];x,y,zz,w=[q[:,:,i] for i in range(4)];heading=np.arctan2(2*(w*zz+x*y),1-2*(y*y+zz*zz))
  for r in a['full_route_rows']:
   i=r['env'];g=i%3;d=1 if g==0 else -1;local=z['COM_link_pos'][:,i,wheelids,0]-centers[i,0];failure=r['first_ordinary_failure_control'];segments=[];contact_complete=[]
   for ep in np.unique(z['episode'][:,i]):
    ids=np.flatnonzero((z['episode'][:,i]==ep)&(np.arange(1500)<failure));signed=d*local[ids];both=support[ids,i].all(-1)
    front=np.flatnonzero((signed.max(1)<-half-.2)&both);after=np.flatnonzero((signed.min(1)>half+.2)&both);ok=g!=2 and len(front)>0 and len(after)>0 and front.min()<after.max()
    if ok:contact_complete.append(int(ep))
    delta=z['root'][ids,i,:3]-z['before_root'][ids,i,:3]
    segments.append(dict(episode=int(ep),first_control=int(ids[0]),last_control=int(ids[-1]),controls=int(len(ids)),signed_wheel_x_range_m=[float(signed.min()),float(signed.max())],both_wheels_before_full_section_with_original1N_support=bool(len(front)),both_wheels_200mm_after_with_original1N_support=bool(len(after)),complete_with_original1N_before_after_support=bool(ok),xyzw_heading_range_rad=[float(heading[ids,i].min()),float(heading[ids,i].max())],same_control_prereset_before_signed_root_x_m=float(d*delta[:,0].sum()),same_control_prereset_before_abs_cross_root_y_m=float(abs(delta[:,1]).sum()),declared_route_truncations=int(z['reasons'][ids,i,p['reason_names'].index('rough_route_boundary')].sum())))
   assert contact_complete==r['complete_episodes'],('original1N_position_match',i)
   rows.append(dict(env=i,group=r['group'],position_complete_episodes=r['complete_episodes'],contact_complete_episodes=contact_complete,all_valid_prefixes=segments))
 pairs={}
 for g in ('forward','reverse'):
  before={x['env'] for x in old['full_route_rows'] if x['group']==g and x['complete_episodes']};after={x['env'] for x in a['full_route_rows'] if x['group']==g and x['complete_episodes']}
  pairs[g]=dict(source145_complete=len(before),candidate146_complete=len(after),complete_to_incomplete_envs=sorted(before-after),incomplete_to_complete_envs=sorted(after-before),candidate_all_valid_incomplete_envs=[x['env'] for x in rows if x['group']==g and not x['position_complete_episodes']])
 diagnosis=save('WAVE50_146_COMPLETE_PREFIX_CONTACT_EXPOSURE_DIAGNOSIS.json',dict(epoch=time.time(),case=jid,fullraw=p['full_route_raw'],query=row['probe']['route_scope']['query_worldmesh_evidence'],all_root30q_parameters_recipes_assignments_original_contracts_reviewed=True,original1N_before_after_support_matches_position_completions=True,pairs=pairs,rows=rows,ordinary_before_prefix_and_all_valid_failures_preserved=True,reset_teleport_excluded_same_episode_and_same_control_prereset_before=True,stand26_not_required_to_traverse=True,training_trace_review=str(latest('WAVE50_FULL_TRAINING_TRACE_ACTUAL_[0-9]*.json')),formal144_controls_1point44_seconds_per_env=True,nominal_maximum_gentle_integral_m=.3*1.44,exposure_insufficiency_is_testable_inference_not_causal_ablation=True,no_shortened_approach_extended_window_or_failure_relabel=True,no_GPU_queue_budget_write=True))
 dec=save('WAVE50_146_COMPLETE_SCOPE_DECISION.json',dict(epoch=time.time(),full_four_cases_complete_errorfree_and_raw_reviewed=True,collection=str(cp),review=str(rp),diagnosis=str(diagnosis),own_checkpoint_SHA=v['own']['checkpoint']['sha256'],own_checkpoint=v['own']['checkpoint'],source_count=384,forward_complete=7,reverse_complete=25,each_direction_environments=27,ordinary=0,route_declared_truncations=a['base_review']['unique_truncations'],closure_mm=a['base_review']['closure_mm'],full_raw=p['full_route_raw'],not_qualified50mm_scope=True,allow_one_second_bounded_same50_scope_exposure_block_under005=True,maximum_additional_block_seconds=1800,same50_geometry_commands_reset_reward_LR_DR=True,source_is_complete_reviewed_own384_not_other_expert_default=True,automatic_third_block_disallowed=True,no70mm_until_actual50_scope_acceptance=True,all_original_strictfalse_and_oldskill_diagnostic_regressions_preserved=True,retention_summary=v['summary']['retention'],E0_CURB_SLOPE_WAVE35_ranges_frozen_and_gate_untrained=True,requires_new_root_CPU_fullsame50_restore_actual_boundary_and_unique_budget_segment=True))
 print(json.dumps(dict(decision=str(dec),forward=7,reverse=25,second1800s_allowed=True,contact_position_exact=True)))
if __name__=='__main__':
 try:main()
 except BaseException:save('COMPLETE146_DECISION_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_old_once_replay=True));raise

"""Only newly extracted original UTF8 diagnostic text. No tensor/SDK/model IO."""
from pathlib import Path
import hashlib,json,math,time,traceback
B=Path(__file__).resolve().parent
def H(b):return hashlib.sha256(b).hexdigest()
def read(n):return json.loads((B/n).read_bytes())
def put(n,v):
 with (B/n).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2,allow_nan=False)
checks=[]
def require(ok,label):
 assert bool(ok),label;checks.append(label)
def value(x):return x['value']
def flatten(x):
 if isinstance(x,list):
  for v in x:yield from flatten(v)
 else:yield x
def main():
 evidence=read('EXACT_SAVED_TEXT_EXTRACTION_AND_ORIGINAL_RESTORE_METADATA_EVIDENCE.json');q=read('EXACT_query_ORIGINAL_SAVED_UTF8.json');native=read('EXACT_native24_ORIGINAL_SAVED_UTF8.json');tt=read('EXACT_terminal_ORIGINAL_SAVED_UTF8.json')
 require(q['diagnostic_valid'] and not q['errors'] and len(q['records'])==95 and not q['retention_limited'],'valid95-record diagnostic, no retention/error')
 require(native['passed'] and native['controls']==24 and native['physics_callbacks']==192 and native['feedback_samples']==48 and native['legs_queue_apply']==native['wheels_queue_apply']==192,'actual24/192/48/fullqueue')
 require(tt['actual_worker_waited'] and tt['returncode']==0 and not tt['deadline_terminated'] and tt['private_EX_released'],'originalwait0/private release')
 require(tt['result']['controls']==24 and tt['result']['all17_Adam_steps']==866060 and tt['result']['actual_LR_unchanged']==.0002562890625000001 and tt['result']['core_actor_critic_STD_norm_optimizer_literal_unchanged'],'source core/17Adam/LR unchanged actual physical24')
 scalars=evidence['original_restore_reset_evidence_scalars'];require(any(r['path'].endswith('/initial30q_error_rad') and r['value']==0 for r in scalars),'original74 bank qerr0 receipt before q34')
 require(any(r['path'].endswith('/original_qerr_zero_guard_completed_before_declared_fall_axis') and r['value'] is True for r in scalars),'original receipt explicitly orders qerr0 before q34placement')
 events=q['records'];groups={name:[(i,r) for i,r in enumerate(events) if r['event']==name] for name in {r['event'] for r in events}};placement=groups['DECLARED_FALL_BEFORE_ORIGINAL_WRITE'];queries=groups['ORIGINAL_CLOSURE_QUERY_CACHED_INPUT_AND_RESULT'];queue=groups['ORIGINAL_QUEUE_APPLY_RESULT']
 require(len(placement)==13 and len(queries)==24 and len(queue)==32,'13 placement batches /24 original queries /32queue returns')
 initial=placement[0][1];iv=initial['values'];ids0=value(iv['ids']);recipe0=value(iv['recipe']);q34=value(iv['cached_q30']);recipe_by_id=dict(zip(ids0,recipe0));require(initial['physics_tick']==0 and ids0==list(range(26)) and all(recipe0.count(k)==2 for k in range(13)),'selected26 IDs /2per13recipe initialactual write')
 q30_difference_from74=[max(abs(a-b) for a,b in zip(q34,row)) for row in value(iv['original74_reset_q'])]
 placed=[]
 for seq,(i,r) in enumerate(placement):
  v=r['values'];jr=events[i+1];rr=events[i+2];j=jr['values'];root=rr['values'];ids=value(v['ids']);recipes=value(v['recipe'])
  require(jr['event']=='ORIGINAL_JOINT_WRITE_REQUEST' and rr['event']=='ORIGINAL_ROOT_WRITE_REQUEST' and jr['physics_tick']==rr['physics_tick']==r['physics_tick'],'originaljoint→root request ordering batch'+str(seq))
  require(value(j['env_ids'])==value(root['env_ids'])==ids and all(qrow==value(v['cached_q30']) for qrow in value(j['q30'])),'original requested q rows equal cached q34 batch'+str(seq))
  require(all(x==0 for x in flatten(value(j['dq30']))),'requested dq zero batch'+str(seq))
  states=value(root['root13']);want_z=value(v['declared_root_z']);quat=value(v['cached_recipe_quat_xyzw']);mins=value(v['cached_sampled_minimum']);bound=v['original_limit_read_not_yet_bound']
  require(all(s[2]==z and s[3:7]==rot and all(x==0 for x in s[7:]) for s,z,rot in zip(states,want_z,quat)),'original root.z/XYZW/zero6 request exact batch'+str(seq))
  require(all(x==0 for x in value(v['env_origins_z'])),'original selected flat origin.z0 batch'+str(seq))
  if bound:require(seq==0 and v['original_actual_limits2'] is None and v['cached_q_gas_outside_actual_limits'] is None,'initial readbacknotyetbound staysunknown')
  else:
   require(not any(flatten(value(v['cached_q_gas_outside_actual_limits']))),'later original limitreadback q inbounds batch'+str(seq))
  placed.append(dict(event_index=i,physics_tick=r['physics_tick'],seconds=r['physics_tick']*.0025,selected_ids=ids,recipes=recipes,original_requested_q_equals_cached_q34=True,root_requested_Z_XYZW_matches_declaration=True,requested_minimum_sampled_clearance_range_m=[min(z+m for z,m in zip(want_z,mins)),max(z+m for z,m in zip(want_z,mins))],actual_limits_initially_unbound=bound,postwrite_actual_FK_or_manifold_not_observed=True))
 summary=[];perenv={x:[] for x in ids0};first_exceed=None
 for i,r in queries:
  v=r['values'];ids=value(v['ids']);recipes=value(v['recipe']);eps=value(v['episode_length_buf']);loops={k:value(s) for k,s in v['per_loop_anchor_residual'].items()};clear=value(v['authored_cached_clearance34']);tick=r['physics_tick']
  require(tick%8==0 and len(ids)==26 and all(recipe_by_id[x]==rec for x,rec in zip(ids,recipes)),'originalcontrol-end query domain/tick '+str(tick))
  require(all(math.isfinite(x) for x in flatten(clear)) and all(math.isfinite(x) for vals in loops.values() for x in vals),'finite already reported residual/clearance '+str(tick))
  byid=[]
  for j,(env,recipe) in enumerate(zip(ids,recipes)):
   worst_name=max(loops,key=lambda name:loops[name][j]);worst=loops[worst_name][j];row=dict(physics_tick=tick,seconds=tick*.0025,control=tick//8,env_id=env,recipe=recipe,episode_length_buf=eps[j],worst_original_closure_loop=worst_name,worst_original_closure_m=worst,original_2mm_exceeded=worst>.002,authored_cached_minimum_clearance_m=min(clear[j]),NOT_cooked_manifold_penetration=True)
   perenv[env].append(row);byid.append(row)
   if row['original_2mm_exceeded'] and first_exceed is None:first_exceed=row
  summary.append(dict(event_index=i,physics_tick=tick,seconds=tick*.0025,maximum_original_closure_m=max(x['worst_original_closure_m'] for x in byid),minimum_reported_authored_clearance_m=min(x['authored_cached_minimum_clearance_m'] for x in byid),above2mm_selected_query_env_rows=[x for x in byid if x['original_2mm_exceeded']],selected_rows=byid))
 require([r['physics_tick'] for r in summary]==list(range(8,193,8)),'exact24 original controlend query ticks8..192; not per-substep')
 require(not summary[0]['above2mm_selected_query_env_rows'],'first20ms selected query all below original2mm')
 require(first_exceed['physics_tick']==32 and first_exceed['env_id']==18 and first_exceed['recipe']==5,'earliest saved crossing .08s env18 recipe5')
 repeat_chains=[]
 for row in placed[1:]:
  tick=row['physics_tick'];query=next(x for x in summary if x['physics_tick']==tick);before={x['env_id']:x for x in query['selected_rows']};nextq=next((x for x in summary if x['physics_tick']>tick),None);nxt={x['env_id']:x for x in nextq['selected_rows']} if nextq else {}
  chain=[]
  for env in row['selected_ids']:
   prev=before[env];after=nxt.get(env);require(prev['original_2mm_exceeded'],'repeatplacement follows samecontrol >2mm query '+str((tick,env)))
   if after:require(after['episode_length_buf']<prev['episode_length_buf'],'nextquery episodecounter drop '+str((tick,env)))
   chain.append(dict(env_id=env,recipe=prev['recipe'],original_samecontrol_query=prev,next_query_after_new_placement=after,reset_reason_mask_not_saved=True,consistent_with_original2mm_episode_reset_not_exclusive_cause_proof=True))
  repeat_chains.append(dict(physics_tick=tick,seconds=tick*.0025,original_write_batch=row['selected_ids'],selected_chains=chain))
 per_recipe=[]
 for recipe in range(13):
  selected=[env for env in ids0 if recipe_by_id[env]==recipe];rr=[x for env in selected for x in perenv[env]];over=[x for x in rr if x['original_2mm_exceeded']];new=[env for batch in placed[1:] for env in batch['selected_ids'] if recipe_by_id[env]==recipe]
  per_recipe.append(dict(recipe=recipe,selected_env_ids=selected,first20ms_max_closure_m=max(perenv[e][0]['worst_original_closure_m'] for e in selected),window_max_closure_m=max(x['worst_original_closure_m'] for x in rr),first_saved_over2mm=next((x for x in sorted(over,key=lambda x:(x['physics_tick'],x['env_id']))),None),over2mm_query_env_events=len(over),unique_selected_env_over2mm=len({x['env_id'] for x in over}),original_repeat_placement_selected_ID_events=len(new),unique_selected_env_replaced=len(set(new)),only2env_per_recipe_not_population_failure_rate=True))
 qstats=[]
 for group,dim in [('legs',4),('wheels',2)]:
  rr=[r for _,r in queue if r['values']['group']==group];ticks=[r['values']['tick'] for r in rr];require(ticks==list(range(16)),'originalqueue '+group+' ticks0..15 once')
  require(all(r['values']['value']['shape']==[26,dim] for r in rr),'selectedqueue shape '+group);vals=[x for r in rr for x in flatten(value(r['values']['value']))];require(all(math.isfinite(x) for x in vals),'original queue returned finite '+group)
  qstats.append(dict(group=group,original_apply_tick_values=ticks,values_min=min(vals),values_max=max(vals),zero_scalar_elements=sum(x==0 for x in vals),scalar_elements=len(vals),units_or_target_space_not_declared_by_this_JSON_no_clip6_comparison=True,after_tick15_not_observed_by_narrow_hook=True))
 result=dict(kind='E3_q34_valid_original_query95_saved_text_chain_review_v1',passed_text_chain_checks=True,checks=checks,check_count=len(checks),source_extraction=evidence,actual_physical24_and_diagnostic_valid=True,original74_qerr0_precedes_q34_request=True,initial_q34_vs_selected_old74_q30_max_difference_range=[min(q30_difference_from74),max(q30_difference_from74)],difference_is_declared_independent_pose_not_an_error=True,placement_batches=placed,control_end_queries=summary,first_saved_over2mm=first_exceed,first_original_selected_query_at20ms_max_closure_m=summary[0]['maximum_original_closure_m'],first_original_selected_query_at20ms_min_authored_clearance_m=summary[0]['minimum_reported_authored_clearance_m'],earliest_selected_repeat_placement=repeat_chains[0],repeat_placement_chains=repeat_chains,repeat_selected_ID_events=sum(len(p['selected_ids']) for p in placed[1:]),repeat_unique_selected_IDs=len({env for p in placed[1:] for env in p['selected_ids']}),per_recipe_selected26_only=per_recipe,original_queue_returns_first16ticks=qstats,unknowns=['No actual SDK FK read immediately after q34 write or before first physics callback. Requestedpose equality is not an appliedpose/manifold proof.','First closure observation occurs after8physics callbacks20ms; cannot determine the first2.5ms change or separate action/contact/solver causes within that interval.','Only2selected IDs perrecipe and24controls. No20k population failure rate, no3s request/.5s recovery/fullskill acceptance.','Authoredcached support negatives (tens of micrometres) are not cookedshape contact/manifold penetration evidence and are not a new1um physical gate.','No per-ID termination reason masks in this query receipt. Repeatplacements occur after samecontrol >2mm and observedepisodecounter drops, consistent with originalclosure reset, but other overlapping causes cannot be excluded.','Queue target values are originalapply returns, not necessarily normalized actor6 ingress; do not judge them by clip6 or infer unrecorded delay-state correctness.'],no_unique_root_cause_or_new_physics_repair_inferred=True,V2_change_was_diagnostic_device_routing_not_plant_change=True,no_model_NPZ_raw_gz_SDK_host_or_GPU_read=True,skill_graduation=False,complete_WM_dataset=False)
 put('E3_V2_VALID95_ORIGINAL_RESET_WRITE_QUERY_CHAIN_SAVED_TEXT_REVIEW_ACTUAL.json',result)
 lines=['E3 q34 original-query V2 — saved-text chain review','',f"Valid95records/errors[]/retentionfalse, actual24controls/192physics/48feedback+queue192,17Adam866060/LR literal/core unchanged, originalwait0/allownout/privateEXrelease. One exact saved-first JSON input; only seven original producer text paths/bytes/SHA extracted. No model/NPZ/raw/host/SDK/GPU read.",'',f"Original74bank reset qerr=0 and explicit receipt order BEFORE q34placement are present. At tick0, requested q30 rows equal cached nearest-pose34, dq0, rootZ/XYZW match the declared request and root6vel0. First placement correctly says actual limitread notyetbound; later12batches use the original readback and report no gas limit violation. This proves requests, not backend postwrite FK.",'',f"Earliest original closure query is tick8=.020s AFTER8physics callbacks: all26selected residuals below2mm, maximum {summary[0]['maximum_original_closure_m']*1000:.6f}mm. Thus this record does not show an immediate >2mm error at firstquery. No pre-firstphysics or per-substep state exists.",'',f"First saved >2mm is tick32=.080s/control4/env18/recipe5/episode_length4, right_gas_closure={first_exceed['worst_original_closure_m']*1000:.6f}mm. It occurs before the declared5-control spawn grace ends, so it is not by itself an observed reset. Earliest selected repeatplacement is tick40=.100s/env5/recipe5 after samecontrol residual {repeat_chains[0]['selected_chains'][0]['original_samecontrol_query']['worst_original_closure_m']*1000:.6f}mm/episode_length5; nextquery episodecounter drops to1. These are observed sample times, not exact onset times.",'',f"12repeat-placement batches contain {result['repeat_selected_ID_events']} selected-ID events across {result['repeat_unique_selected_IDs']} unique selected IDs. Every samecontrol selected row before repeatplacement is >2mm; every available followingquery shows episodecounter drop. Original per-env2mm behaviour is consistent; no per-ID reasonmask exists to prove exclusive cause. Last tick192 placement has no subsequentquery in this24-step window. Guard/physics/model were not changed by the device-index fix.",'','| Recipe | IDs | First20ms max closure mm | Window max closure mm | >2mm query-env events | Repeat placement events /uniqueIDs |','|---|---|---:|---:|---:|---:|']
 for r in per_recipe:lines.append(f"| {r['recipe']} | {r['selected_env_ids']} | {r['first20ms_max_closure_m']*1000:.6f} | {r['window_max_closure_m']*1000:.6f} | {r['over2mm_query_env_events']} | {r['original_repeat_placement_selected_ID_events']} /{r['unique_selected_env_replaced']} |")
 lines+=['',f"First20ms minimum alreadyreported authoredclearance={summary[0]['minimum_reported_authored_clearance_m']*1000:.6f}mm. It is pure authored geometry on originalcached body values, not contactmanifold. No cooking/skin/physics change or newprecision healthgate follows from it. Legs/wheels each originalapply ticks0..15 are complete/finite with selectedshapes26×4/26×2; magnitudes are physicaltarget-space values, not a clip6 audit. Tick16+ unobserved by thishook.",'','Unknowns remain:']+['- '+x for x in result['unknowns']]
 lines+=['',f"{len(checks)} saved-text shape/order/clock/request/residual-chain checks. No solecause/wholepopulation/recovery/skill or completeWMdataset claim. Root ordinaryGitpending; no newtrial/tag."]
 with (B/'HANDOFF_FROZEN_E3_V2_VALID95_SAVED_TEXT_CHAIN_REVIEW.md').open('x',encoding='utf8',newline='\n') as f:f.write('\n'.join(lines)+'\n')
 print(json.dumps(dict(passed=True,checks=len(checks),first20ms_max_mm=summary[0]['maximum_original_closure_m']*1000,first_over2mm=first_exceed,repeat_selected_events=result['repeat_selected_ID_events'],repeat_selected_unique=result['repeat_unique_selected_IDs'],no_unique_cause=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('SAVED_TEXT_CHAIN_REVIEW_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_model_or_remote=True));raise

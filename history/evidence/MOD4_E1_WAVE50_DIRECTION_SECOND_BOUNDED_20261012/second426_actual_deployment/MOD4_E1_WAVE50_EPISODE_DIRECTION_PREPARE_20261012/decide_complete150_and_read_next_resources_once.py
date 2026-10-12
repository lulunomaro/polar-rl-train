"""Retain complete150 acceptance failure and inspect the next bounded scope's resources."""
from wave_direction_io import *
def latest(pattern):return max(R.glob(pattern),key=lambda p:int(p.stem.rsplit('_',1)[1]))
def main():
 cp=latest('DIRECTION_CANDIDATE_COLLECTED_[0-9]*.json');c=json.loads(cp.read_bytes());rp=latest('DIRECTION_CANDIDATE_ACTUAL_REVIEW_[0-9]*.json');r=json.loads(rp.read_bytes());pp=latest('DIRECTION_DIRECT149_PREFIX_ACTUAL_[0-9]*.json');p=json.loads(pp.read_bytes());final=json.loads((R/'DIRECTION_FORMAL_FINAL_ACTUAL_REVIEW.json').read_bytes());assert not c['pending'] and len(c['cases'])==4 and r['review_complete'] and p['passed']
 assert p['pairs']['forward']['candidate_complete']==12 and p['pairs']['reverse']['candidate_complete']==25 and p['original1N_contact_matches_position_completions']
 decision=dict(epoch=time.time(),all_four_actual_complete_errorfree_fullraw_reviewed=True,actual_collection=str(cp),full_actual_review=str(rp),direct149_pair_review=str(pp),own_formal_final_ref=str(R/'DIRECTION_FORMAL_FINAL_ACTUAL_REVIEW.json'),full_training_trace_ref=final['full_training_trace_ref'],own_checkpoint=final['own_checkpoint'],checkpoint_bytes=final['checkpoint_bytes'],source_count=424,actual_finite_tensor_count=104,candidate_forward_complete=12,candidate_reverse_complete=25,source149_forward_complete=1,source149_reverse_complete=25,accepted35_frozen145_forward_complete=11,accepted35_frozen145_reverse_complete=23,fullraw=p['fullraw'],terrain_original_health=r['terrain']['base_review'],direct149_pairs=p['pairs'],original1N_contact_matches_position=True,all_valid_failed_prefixes_originalfalse_raw_cost_preserved=True,stand26_no_cross_required=True,not_qualified50=True,no70mm_or_fullRM_MoE_permanent_antiforgetting_graduation=True,no_causal_improvement_claim_different_initial_source_and_no_ablation=True,legacy_diagnostics=r['summary']['retention'],one_direction300s_block_completed=True,allow_one_second_same50_entry_direction_bounded_exposure_under005=True,maximum_additional_block_seconds=1800,automatic_third_block_disallowed=True,continuation_source_SHA=final['own_checkpoint']['sha256'],continuation_source_is_only_same_scope_not_other_expert_default=True,original35_b026_and129_lineage_preserved=True,E0_CURB20_WAVE35_SLOPE_onlyobserved_frozen_gate_untrained=True,second_root_CPU_CUDA_PPO_not_yet_deployed=True)
 save('CANDIDATE150_COMPLETE_SCOPE_DECISION.json',decision)
 save('REFERENCE_LOOKUP_MISSING_BUILD_SCRIPT.json',dict(epoch=time.time(),path=str(PRIOR/'build_entry_second_payload_once.py'),error='Get-Content: path not found',read_only_reference_lookup=True,no_GPU_or_physics_error=True,original_tool_output_and_reference_sources_retained=True))
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import sys,json,time,torch,shutil,subprocess
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_direction_once as own
j=lambda p:json.loads(p.read_bytes());b=j(own.s.q.ctl.CANONICAL);st=j(D/'reports/E1_STATE.json');assert st['phase']=='E1_WAVE50_direction_saved_review_ready' and b['active_segment'] is None and not j(own.s.q.ctl.STATE_PATH).get('active_training')
prior=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_SECOND_BOUNDED_20261012');size=sum(p.stat().st_size for p in prior.rglob('*') if p.is_file());required=2*size+2*1024**3
mem=int(next(x for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')).split()[1])*1024
disk=shutil.disk_usage(D);devices=subprocess.check_output(['df','-B1','--output=source,fstype,size,used,avail,target'],text=True)
print(json.dumps(dict(epoch=time.time(),prior_actual_completed1800s_wholeoutput_path=str(prior),prior_actual_completed_wholeoutput_bytes=size,required_bytes=required,actual_current_root_disk_free_bytes=disk.free,RAM_available_bytes=mem,original_resource_guard_passed=disk.free>required and mem>8*1024**3,actual_filesystem_inventory=devices,no_root_create_GPU_or_budget_write=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  save('NEXT_DIRECTION_BOUNDED_RESOURCE_ACTUAL.json',v);print(json.dumps(dict(complete150_scope_decided=True,forward=12,reverse=25,not_qualified50=True,next1800_resources=v)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('COMPLETE150_DECISION_RESOURCE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_write=True));raise

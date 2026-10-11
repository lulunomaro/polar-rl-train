"""Complete148 actual decision and prepare a new same-entry second scope, no GPU."""
from entry_io import *

def main():
 own=json.loads((R/'ENTRY_OWN_FORMAL_CPU_ACTUAL_1791752650313248100.json').read_bytes())
 rp=R/'ENTRY_CANDIDATE_ACTUAL_REVIEW_1791754421370293900.json'; review=json.loads(rp.read_bytes())
 pp=R/'ENTRY_DIRECT147_PREFIX_ACTUAL_1791754506003881900.json'; pair=json.loads(pp.read_bytes())
 tp=R/'ENTRY_FULL_TRAINING_TRACE_ACTUAL_1791752694983782500.json'; trace=json.loads(tp.read_bytes())
 assert own['closeout_ready'] and review['review_complete'] and pair['passed'] and trace['passed']
 assert own['own_checkpoint']['sha256']=='ea9fd8558079ec690b0a483e3620c27201ed1afc36cfac56ec2a5c74f42c1f5a'
 assert pair['pairs']['forward']['candidate_complete']==16 and pair['pairs']['reverse']['candidate_complete']==24
 decision=dict(epoch=time.time(),full_four_cases_complete_errorfree_and_raw_reviewed=True,actual_collection=review['collection'],full_actual_review=str(rp),direct147_pair_review=str(pp),full_training_trace=str(tp),feedback_final_reset_schema_review=str(R/'ENTRY148_FINAL_FEEDBACK_RESET_SCHEMA_ACTUAL_REVIEW.json'),
  own_checkpoint=own['own_checkpoint'],own_checkpoint_SHA=own['own_checkpoint']['sha256'],own_checkpoint_bytes=17616882,source_count=410,actual_finite_tensors=102,fullraw=pair['fullraw'],candidate_forward_complete=16,candidate_reverse_complete=24,standing26_not_required_to_cross=True,original1N_contact_and_position_completions_agree=True,ordinary=0,route_declared_truncations=4,closure_m=.000851099088,
  direct147_pairs=pair['pairs'],oldskill_diagnostics=review['summary']['retention'],not_qualified50=True,all_original_false_raw_cost_validprefixes_retained=True,no_causal_learning_or_permanent_antiforgetting_claim=True,
  allow_one_second_bounded_same50_entry_scope_exposure_block_under005=True,maximum_additional_block_seconds=1800,automatic_third_block_disallowed=True,no_70mm_before_actual50_acceptance=True,
  rationale='Actual initial entry formal contains144controls/1.44s perenv; nominal .432m travel is below .517m minimum fullfootprint frontflat approach. Test an additional bounded exposure window after full148 review, without changing entry/command/RNG/reward/DR/route. This is a testable exposure hypothesis, not causal proof.',
  original2m_training_route_not_full3_006m_test=True,root_proxy_not_contact_fullroute_certificate=True,E0_CURB20_SLOPE_WAVE35_frozen_gate_untrained=True,no_GPU_or_budget_write=True)
 save('ENTRY148_COMPLETE_SCOPE_DECISION.json',decision)
 save('ENTRY148_LOCAL_PATH_READER_ERRORS_PRESERVED.json',dict(epoch=time.time(),errors=[dict(path=p,error='Get-Content path not found; read-only path lookup, corrected by rg, no experiment replay') for p in ('payload_initialization_reviewed/train_wave50_entry_resume_ppo_v2.py','MOD4_E1_WAVE50_SECOND_BOUNDED_20261012/stage_second50_and_CPU_once.py','MOD4_E1_WAVE50_SECOND_BOUNDED_20261012/prepare_second_scope_once.py','MOD4_E1_WAVE50_ENTRY_PREPARE_20261012/stage_initialization_reviewed_once.py')],not_physical_failures=True))
 N=W/'MOD4_E1_WAVE50_ENTRY_SECOND_BOUNDED_20261012';assert not N.exists();N.mkdir();(N/'reports').mkdir();(N/'payload/isaac/mod4').mkdir(parents=True)
 source=D/'payload_initialization_reviewed/isaac/mod4/train_wave50_entry_resume_ppo_v2.py';text=source.read_text(encoding='utf8')
 changes=[("manifest['explicit_G3_to_WAVE50_geometry_transition']=True","manifest['explicit_G3_to_WAVE50_geometry_transition']=False"),("manifest['source_scope_geometry_and_command_assignment_migration_disclosed']=True","manifest['source_scope_geometry_and_command_assignment_migration_disclosed']=False"),("    manifest['active_expert']='E1_WAVE50'","    manifest['same_WAVE50_entry_geometry_command_fullrestore_continuation']=True\n    manifest['active_expert']='E1_WAVE50'")]
 for a,b in changes:assert text.count(a)==1;text=text.replace(a,b)
 compile(text,'sameentry_worker','exec');(N/'payload/isaac/mod4/train_wave50_entry_same_scope_resume_ppo.py').write_text(text,encoding='utf8',newline='\n')
 controller=(PREV/'payload/supervise_wave50_second_bounded_once.py').read_text()
 controller=controller.replace('import supervise_wave50_independent_scope_once as prior','import supervise_wave50_entry_scope_once_v2 as prior').replace('from wave_budget005_source_guard import verify_original_records as original005','from wave50_entry_source_guard import verify_original_records as original005')
 controller=controller.replace('MOD4_S3_E1_WAVE50_INDEPENDENT_REVIEWED_20261012','MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012').replace('219faeadcceaa3e015b6a50ccdbf7614cd0f7e0b1cafe2cea04fad0d59b0c550',decision['own_checkpoint_SHA'])
 controller=controller.replace('train_wave50_same_scope_resume_ppo.py','train_wave50_entry_same_scope_resume_ppo.py').replace('COMPLETE146_SCOPE_DECISION','COMPLETE148_SCOPE_DECISION').replace('allow_one_second_bounded_same50_scope_exposure_block_under005','allow_one_second_bounded_same50_entry_scope_exposure_block_under005')
 controller=controller.replace('len(old)==384 and len(f)==386','len(old)==410 and len(f)==412').replace('same50_geometry_command_reset_reward_LR_DR','same50_entry_geometry_command_reset_reward_LR_DR').replace('SECOND_TARGET_CPU_PASSED','ENTRY_SECOND_TARGET_CPU_PASSED')
 controller=controller.replace('E1_WAVE50_independent_saved_review_ready','E1_WAVE50_entry_saved_review_ready').replace('e1_WAVE50_independent_observation_PASSED','e1_WAVE50_entry_observation_PASSED').replace('start_ticks=89621745','start_ticks=90749332')
 controller=controller.replace("entry='train_wave50_fresh_preflight_ppo.py' if count==128 else 'train_wave50_full_resume_ppo.py'","entry='train_wave50_entry_fresh_preflight_ppo_v2.py' if count==128 else 'train_wave50_entry_resume_ppo_v2.py'")
 controller=controller.replace("entry='train_wave50_fresh_preflight_ppo.py' if count==128 else 'train_wave50_entry_same_scope_resume_ppo.py'","entry='train_wave50_entry_fresh_preflight_ppo_v2.py' if count==128 else 'train_wave50_entry_same_scope_resume_ppo.py'")
 controller=controller.replace("('train_wave50_fresh_preflight_ppo.py','train_wave50_full_resume_ppo.py')","('train_wave50_entry_fresh_preflight_ppo_v2.py','train_wave50_entry_resume_ppo_v2.py')").replace("('train_wave50_fresh_preflight_ppo.py','train_wave50_full_resume_ppo.py','train_wave50_entry_same_scope_resume_ppo.py')","('train_wave50_entry_fresh_preflight_ppo_v2.py','train_wave50_entry_resume_ppo_v2.py','train_wave50_entry_same_scope_resume_ppo.py')")
 anchor="exec(compile(text,str(Path(__file__))+'::same50_train','exec'),prior.__dict__)"
 extra="""old="assert entryproof['passed'] and entryproof['explicit_new_entry_scope'] and not entryproof['same_entry_identity_restored_exact'] and entryproof['actual_entry_terrain_command_CUDA_disk_roundtrip_exact']"
new="assert entryproof['passed'] and not entryproof['explicit_new_entry_scope'] and entryproof['same_entry_identity_restored_exact'] and entryproof['actual_entry_terrain_command_CUDA_disk_roundtrip_exact']"
assert text.count(old)==1;text=text.replace(old,new)
"""
 assert controller.count(anchor)==1;controller=controller.replace(anchor,extra+anchor)
 controller=controller.replace("old=\"'-e1-wave50-independent'\"","old=\"'-e1-wave50-entry-repair'\"").replace("'-e1-wave50-second-bounded'","'-e1-wave50-entry-second-bounded'")
 controller=controller.replace('bounded_E1_WAVE50_second_bounded_learning','bounded_E1_WAVE50_entry_second_bounded_learning').replace('E1_WAVE50_second_bounded_saved_review_ready','E1_WAVE50_entry_second_bounded_saved_review_ready').replace('e1_WAVE50_second_bounded_observation','e1_WAVE50_entry_second_bounded_observation').replace('old384_actual_exit','old410_actual_exit').replace('reviewed146 same50','reviewed148 same50entry').replace('second_same50_block=True','second_same50_entry_block=True')
 compile(controller,'sameentry_controller','exec');(N/'payload/supervise_wave50_entry_second_bounded_once.py').write_text(controller,encoding='utf8',newline='\n')
 text=(PREV/'second50_io.py').read_text();text=text.replace("OLD=old.ROOT","OLD='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012'").replace("MOD4_S3_E1_WAVE50_SECOND_BOUNDED_20261012'","MOD4_S3_E1_WAVE50_ENTRY_SECOND_BOUNDED_20261012'").replace('219faeadcceaa3e015b6a50ccdbf7614cd0f7e0b1cafe2cea04fad0d59b0c550',decision['own_checkpoint_SHA'])
 text=text.replace("SOURCE=json.loads((PRIOR/'reports/WAVE50_146_COMPLETE_SCOPE_DECISION.json').read_bytes())['own_checkpoint']['path']","ENTRY_LOCAL=W/'MOD4_E1_WAVE50_ENTRY_PREPARE_20261012'\nSOURCE=json.loads((ENTRY_LOCAL/'reports/ENTRY148_COMPLETE_SCOPE_DECISION.json').read_bytes())['own_checkpoint']['path']")
 (N/'entry_second_io.py').write_text(text,encoding='utf8',newline='\n')
 dispatch=(PREV/'dispatch_second_once.py').read_text().replace('from second50_io import *','from entry_second_io import *').replace('SECOND_TARGET_CPU_PASSED','ENTRY_SECOND_TARGET_CPU_PASSED').replace('==386','==412').replace('source_count=386','source_count=412').replace('supervise_wave50_second_bounded_once','supervise_wave50_entry_second_bounded_once')
 (N/'dispatch_entry_second_once.py').write_text(dispatch,encoding='utf8',newline='\n')
 print(json.dumps(dict(full148_decided=True,local_new_scope=str(N),payload_count=2,new_GPU_not_deployed_yet=True)))
if __name__=='__main__':
 try:main()
 except BaseException:save('ENTRY148_SECOND_PREPARATION_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_old_once_replay=True));raise

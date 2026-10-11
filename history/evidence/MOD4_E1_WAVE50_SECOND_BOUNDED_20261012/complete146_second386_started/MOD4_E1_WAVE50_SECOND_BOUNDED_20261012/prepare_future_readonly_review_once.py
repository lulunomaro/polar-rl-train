from second50_io import *

def put(name,text):
 p=D/name;assert not p.exists();compile(text,str(p),'exec');p.write_text(text,encoding='utf8')

text=(PRIOR/'read_own_formal_cpu_actual.py').read_text(encoding='utf8')
changes={
'from wave50_io import *':'from second50_io import *',
'import supervise_wave50_independent_scope_once as own':'import supervise_wave50_second_bounded_once as wrapper\nown=wrapper.prior',
'e1_WAVE50_independent_observation':'e1_WAVE50_second_bounded_observation',
'own.SOURCE_SHA':'wrapper.INIT_SHA','len(freeze)==384':'len(freeze)==386',
"assert not t['terrain_state_restored_exact'] and t['explicit_G3_to_WAVE50_geometry_transition']":"assert t['terrain_state_restored_exact'] and not t['explicit_G3_to_WAVE50_geometry_transition']",
"and c['explicitly_new_command_scope']":"and not c['explicitly_new_command_scope']",
'E1_WAVE50_independent_saved_review_ready':'E1_WAVE50_second_bounded_saved_review_ready',
"'WAVE50_OWN_FORMAL_CPU_ACTUAL_'":"'SECOND50_OWN_FORMAL_CPU_ACTUAL_'",
}
for a,b in changes.items():assert a in text,a;text=text.replace(a,b)
put('read_second50_own_formal_cpu_actual.py',text)
text=(PRIOR/'collect_candidate_actual.py').read_text(encoding='utf8').replace('from wave50_io import *','from second50_io import *').replace('str(PRIOR)','str(old.PRIOR)').replace('e1_WAVE50_independent_observation_PASSED','e1_WAVE50_second_bounded_observation_PASSED').replace('WAVE50_CANDIDATE_COLLECTED_','SECOND50_CANDIDATE_COLLECTED_')
put('collect_second50_candidate_actual.py',text)
text=(PRIOR/'review_candidate_reset_schema_actual.py').read_text(encoding='utf8').replace('own384','own386').replace('from wave50_io import *','from second50_io import *').replace("PRIOR/'","old.PRIOR/'").replace("(PRIOR/","(old.PRIOR/").replace('WAVE50_CANDIDATE_COLLECTED_','SECOND50_CANDIDATE_COLLECTED_').replace('WAVE50_OWN_FORMAL_CPU_ACTUAL_','SECOND50_OWN_FORMAL_CPU_ACTUAL_').replace("['actual_source_count']==384","['actual_source_count']==386").replace('WAVE50_CANDIDATE_ACTUAL_REVIEW_','SECOND50_CANDIDATE_ACTUAL_REVIEW_')
put('review_second50_candidate_actual.py',text)
text=(PRIOR/'review_complete_dynamic_family_trace_actual.py').read_text(encoding='utf8').replace('from wave50_io import *','from second50_io import *').replace('WAVE50_OWN_FORMAL_CPU_ACTUAL_','SECOND50_OWN_FORMAL_CPU_ACTUAL_').replace("['actual_source_count']==384","['actual_source_count']==386").replace('WAVE50_FULL_TRAINING_TRACE_ACTUAL_','SECOND50_FULL_TRAINING_TRACE_ACTUAL_')
put('review_second50_complete_dynamic_family_trace_actual.py',text)
save('FUTURE_READONLY_REVIEW_PREPARED.json',dict(epoch=time.time(),prepared_only_not_future_pass=True,source386_actual_CPU102_binding=True,actual_publication_number_not_blind_claim=True,same50_strict_restore_not_initial_transition=True,original145_query_ground1e6_contactCOMhardware_and115129_skill_auditors_unchanged=True,original_actual_reset_schema_used=True,no_GPU_queue_budget_mutation=True,requires_complete_fourcase_and_direct146_pair_and_fulltrace_before_next_axis=True))
save('LOCAL_READER_FILENAME_LOOKUP_ERRORS_RETAINED.json',dict(epoch=time.time(),missing_paths=['sync_formal_final_and_partial_candidate_once.py','review_complete_dynamic_family_training_trace_actual.py','review_full_training_trace_actual.py'],actual_files_located_with_rg=True,inspection_only_no_experiment_or_GPU_failure=True,no_old_file_changed_or_once_replayed=True))
print('Prepared future final/collection/fullraw/trace readers; no future pass claimed')

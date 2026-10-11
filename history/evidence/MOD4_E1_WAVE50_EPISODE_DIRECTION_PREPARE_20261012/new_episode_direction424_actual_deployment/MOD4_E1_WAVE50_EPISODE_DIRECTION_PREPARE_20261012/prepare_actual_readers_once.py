"""Prepare new read-only readers with actual scope semantics; no future pass claimed."""
from wave_direction_io import *
import ast
def put(name,s):
 p=D/name;assert not p.exists();ast.parse(s);p.write_text(s,encoding='utf8',newline='\n')
def base(name):return (PRIOR/name).read_text().replace('from entry_second_io import *','from wave_direction_io import *')
def initial(s):
 s=s.replace('import supervise_wave50_entry_second_bounded_once as wrapper\nown=wrapper.prior','import supervise_wave50_direction_once as own')
 s=s.replace('wrapper.INIT_SHA','own.SOURCE_SHA').replace('==412','==424').replace('actual_source_count=412','actual_source_count=424')
 s=s.replace('e1_WAVE50_entry_second_bounded_observation','e1_WAVE50_direction_observation').replace('E1_WAVE50_entry_second_bounded_saved_review_ready','E1_WAVE50_direction_saved_review_ready')
 s=s.replace("t['terrain_state_restored_exact'] and not t['explicit_G3_to_WAVE50_geometry_transition']", "not t['terrain_state_restored_exact'] and t['explicit_G3_to_WAVE50_geometry_transition']")
 s=s.replace("ep['same_entry_identity_restored_exact'] and not ep['explicit_new_entry_scope']", "not ep['same_entry_identity_restored_exact'] and ep['explicit_new_entry_scope']")
 s=s.replace("c['predecessor_command_state_restored_exact'] and not c['explicitly_new_command_scope']", "c['predecessor_command_state_restored_exact'] and c['explicitly_new_command_scope']")
 s=s.replace("'E1_WAVE50_ENTRY_STARTUP_VERIFIED.json')", "'E1_WAVE50_ENTRY_STARTUP_VERIFIED.json','E1_WAVE50_DIRECTION_RESUME_STARTUP_VERIFIED.json')")
 anchor="assert c['predecessor_command_state_restored_exact'] and c['explicitly_new_command_scope'] and c['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact'] and c['saved_source_episode_plus_one_verified']"
 assert anchor in s
 s=s.replace(anchor,anchor+"\ndirection=j("+('root' if "root/'E1_TERRAIN" in s else 'run')+"/'E1_WAVE50_DIRECTION_RESUME_STARTUP_VERIFIED.json');assert direction['passed'] and direction['explicit_new_episode_direction_scope'] and not direction['predecessor_direction_state_restored_exact'] and direction['actual_CUDA_direction_disk_roundtrip_exact'] and direction['saved_source_episode_plus_one_verified']")
 s=s.replace('ENTRY_SECOND_OWN_FORMAL_CPU_ACTUAL','DIRECTION_OWN_FORMAL_CPU_ACTUAL').replace('ENTRY_SECOND_OWN_STARTUP_CPU_ACTUAL','DIRECTION_OWN_STARTUP_CPU_ACTUAL')
 return s
put('read_direction_own_formal_cpu_actual.py',initial(base('read_entry_second_own_formal_CPU_call_reviewed_actual.py')))
put('verify_direction_saved_PPO_cpu_actual.py',initial(base('verify_entry_second_saved_CPU_call_reviewed_actual.py')))
s=base('collect_entry_second_candidate_actual.py').replace('str(old.PRIOR)','str(previous.old.PRIOR)').replace('e1_WAVE50_entry_second_bounded_observation','e1_WAVE50_direction_observation').replace('ENTRY_SECOND_CANDIDATE_COLLECTED','DIRECTION_CANDIDATE_COLLECTED')
put('collect_direction_candidate_actual.py',s)
s=base('review_entry_second_candidate_actual.py').replace('old.PRIOR','previous.old.PRIOR').replace('ENTRY_SECOND_CANDIDATE','DIRECTION_CANDIDATE').replace('ENTRY_SECOND_OWN_FORMAL_CPU_ACTUAL','DIRECTION_OWN_FORMAL_CPU_ACTUAL').replace("cpu['actual_source_count']==412","cpu['actual_source_count']==424")
put('review_direction_candidate_actual.py',s)
s=base('review_entry_second_complete_dynamic_family_trace_actual.py').replace('ENTRY_SECOND_OWN_FORMAL_CPU_ACTUAL','DIRECTION_OWN_FORMAL_CPU_ACTUAL').replace("own['actual_source_count']==412","own['actual_source_count']==424").replace('ENTRY_SECOND_FULL_TRAINING_TRACE_ACTUAL','DIRECTION_FULL_TRAINING_TRACE_ACTUAL')
anchor="assert h(ckpath)==v['checkpoint']['sha256'];m="
add="assert h(ckpath)==v['checkpoint']['sha256'];ck=torch.load(ckpath,map_location='cpu',weights_only=False);direction=ck['E1_WAVE50_episode_direction_state'];sign=direction['entry_sign'].numpy();boundmask=direction['wave_mask'].numpy();assert int(boundmask.sum())==2820;m="
assert anchor in s;s=s.replace(anchor,add)
anchor="  hist+=np.array([(c<0).sum(),(c>0).sum(),(c==0).sum()]);"
add="  active_direction=current_wave&boundmask[None,:];assert np.min((x[:,:,7]*sign[None,:])[active_direction])>=-1e-7\\n  hist+=np.array([(c<0).sum(),(c>0).sum(),(c==0).sum()]);"
assert anchor in s;s=s.replace(anchor,add)
put('review_direction_complete_dynamic_family_trace_actual.py',s)
save('ACTUAL_READERS_PREPARED_ONLY.json',dict(epoch=time.time(),prepared_only_not_future_pass=True,files=['read_direction_own_formal_cpu_actual.py','verify_direction_saved_PPO_cpu_actual.py','collect_direction_candidate_actual.py','review_direction_candidate_actual.py','review_direction_complete_dynamic_family_trace_actual.py'],own_finite_tensors_bound_to_actual_checkpoint_not_prior_source102=True,nine_startup_receipts_include_new_direction=True,old_entry_and_terrain_initial_transition_disclosed=True,no_GPU_or_budget_write=True))
print(json.dumps(dict(prepared_readonly_readers=5,not_future_pass=True)))

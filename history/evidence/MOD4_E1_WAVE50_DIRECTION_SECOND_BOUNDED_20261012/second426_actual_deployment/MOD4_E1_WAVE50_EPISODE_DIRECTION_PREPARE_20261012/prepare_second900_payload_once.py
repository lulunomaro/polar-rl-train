"""One shorter second block within005 ceiling; preserve1800 resource refusal."""
from wave_direction_io import *
import ast
N=W/'MOD4_E1_WAVE50_DIRECTION_SECOND_BOUNDED_20261012';P=N/'payload';C=P/'isaac/mod4';C.mkdir(parents=True,exist_ok=True);(N/'reports').mkdir(exist_ok=True)
NEWROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_DIRECTION_SECOND_BOUNDED_20261012'
def put(p,s):assert not p.exists(),p;ast.parse(s);p.write_text(s,encoding='utf8',newline='\n')
decision=json.loads((R/'CANDIDATE150_COMPLETE_SCOPE_DECISION.json').read_bytes());assert decision['allow_one_second_same50_entry_direction_bounded_exposure_under005']
worker=(D/'payload/isaac/mod4/train_wave50_direction_resume_ppo.py').read_text()
for old,new in (("manifest['explicit_G3_to_WAVE50_geometry_transition']=True","manifest['explicit_G3_to_WAVE50_geometry_transition']=False"),("manifest['source_scope_geometry_and_command_assignment_migration_disclosed']=True","manifest['source_scope_geometry_and_command_assignment_migration_disclosed']=False"),("manifest['new_episode_direction_axis']=True","manifest['new_episode_direction_axis']=False")):
 assert worker.count(old)==1;worker=worker.replace(old,new)
worker=worker.replace("    manifest['active_expert']='E1_WAVE50'","    manifest['same50_entry_direction_fullstate_continuation']=True\n    manifest['active_expert']='E1_WAVE50'")
put(C/'train_wave50_direction_same_scope_resume_ppo.py',worker)
s=(PRIOR/'payload/supervise_wave50_entry_second_bounded_once.py').read_text()
s=s.replace('import supervise_wave50_entry_scope_once_v2 as prior','import supervise_wave50_direction_once as prior').replace('from wave50_entry_source_guard import','from wave50_direction_source_guard import')
s=s.replace("OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012')","OLD=Path("+repr(ROOT)+")").replace('ea9fd8558079ec690b0a483e3620c27201ed1afc36cfac56ec2a5c74f42c1f5a',decision['own_checkpoint']['sha256'])
s=s.replace('train_wave50_entry_same_scope_resume_ppo.py','train_wave50_direction_same_scope_resume_ppo.py').replace('train_wave50_entry_fresh_preflight_ppo_v2.py','train_wave50_direction_fresh_preflight_ppo.py').replace('train_wave50_entry_resume_ppo_v2.py','train_wave50_direction_resume_ppo.py')
s=s.replace('len(old)==410 and len(f)==412','len(old)==424 and len(f)==426').replace('finite_tensors']==102','finite_tensors']==104').replace('start_ticks=90749332','start_ticks=91780234')
s=s.replace('COMPLETE148_SCOPE_DECISION.json','COMPLETE150_SCOPE_DECISION.json').replace('full_four_cases_complete_errorfree_and_raw_reviewed','all_four_actual_complete_errorfree_fullraw_reviewed').replace('allow_one_second_bounded_same50_entry_scope_exposure_block_under005','allow_one_second_same50_entry_direction_bounded_exposure_under005').replace("decision['maximum_additional_block_seconds']==1800","decision['maximum_additional_block_seconds']==1800 and decision['chosen_additional_block_seconds']==900").replace("decision['own_checkpoint_SHA']==INIT_SHA","decision['own_checkpoint']['sha256']==INIT_SHA")
s=s.replace('same50_entry_geometry_command_reset_reward_LR_DR','same50_entry_direction_geometry_command_reset_reward_LR_DR').replace('ENTRY_SECOND_TARGET_CPU_PASSED.json','DIRECTION_SECOND_TARGET_CPU_PASSED.json').replace('remaining_training_seconds']>1920','remaining_training_seconds']>1020')
s=s.replace('E1_WAVE50_entry_saved_review_ready','E1_WAVE50_direction_saved_review_ready').replace('e1_WAVE50_entry_observation','e1_WAVE50_direction_observation').replace('bounded_E1_WAVE50_entry_second_bounded_learning','bounded_E1_WAVE50_direction_second_bounded_learning').replace('E1_WAVE50_entry_second_bounded_saved_review_ready','E1_WAVE50_direction_second_bounded_saved_review_ready').replace('e1_WAVE50_entry_second_bounded_observation','e1_WAVE50_direction_second_bounded_observation')
s=s.replace("'-e1-wave50-entry-repair'","'-e1-wave50-direction-repair'").replace("'-e1-wave50-entry-second-bounded'","'-e1-wave50-direction-second-bounded'")
anchor="exec(compile(text,str(Path(__file__))+'::same50_train','exec'),prior.__dict__)"
extra='''old="assert direction['passed'] and direction['explicit_new_episode_direction_scope'] and not direction['predecessor_direction_state_restored_exact'] and direction['actual_CUDA_direction_disk_roundtrip_exact'] and direction['saved_source_episode_plus_one_verified']"
new="assert direction['passed'] and not direction['explicit_new_episode_direction_scope'] and direction['predecessor_direction_state_restored_exact'] and direction['actual_CUDA_direction_disk_roundtrip_exact'] and direction['saved_source_episode_plus_one_verified']"
assert text.count(old)==1;text=text.replace(old,new)
'''
assert anchor in s;s=s.replace(anchor,extra+anchor)
s=s.replace("seconds=1800","seconds=900").replace("prior.train(init,20000,10000,1800,","prior.train(init,20000,10000,900,").replace('old410_actual_exit_and_two_locks_held','old424_actual_exit_and_two_locks_held').replace('004005 reviewed148 same50entry second1800s exposure','004005 full150 reviewed same50entrydirection second900s exposure with measured storage guard').replace('same50 fullstate1800s','same50entrydirection fullstate900s')
put(P/'supervise_wave50_direction_second_bounded_once.py',s)
io_s=(D/'wave_direction_io.py').read_text();start=io_s.index("PRIOR=W/");end=io_s.index('def save(',start)
io_s=io_s[:start]+"PRIOR=W/'MOD4_E1_WAVE50_EPISODE_DIRECTION_PREPARE_20261012';sys.path.insert(0,str(PRIOR))\nimport wave_direction_io as previous\nio=previous.io;H=previous.H\nOLD=previous.ROOT\nROOT="+repr(NEWROOT)+"\nSOURCE_SHA="+repr(decision['own_checkpoint']['sha256'])+"\nSOURCE="+repr(decision['own_checkpoint']['path'])+"\n"+io_s[end:]
put(N/'wave_direction_second_io.py',io_s)
decision['chosen_additional_block_seconds']=900;decision['1800_resource_refusal_preserved']=True;decision['900_resource_reference_not_physics_admission']=True
with (N/'reports/COMPLETE150_SCOPE_DECISION.json').open('x',encoding='utf8') as f:json.dump(decision,f,ensure_ascii=False,indent=2)
save('SECOND900_PAYLOAD_PREPARED_ONLY.json',dict(epoch=time.time(),new_local_scope=str(N),new_remote_root=NEWROOT,only_truthful_same_scope_manifest_worker_and_unique_second_controller=True,maximum_allowed_seconds=1800,chosen_seconds=900,original1800_resource_guard_rejection_ref=str(R/'NEXT_DIRECTION_BOUNDED_RESOURCE_ACTUAL.json'),actual900_resource_reference=str(R/'NEXT_DIRECTION_900S_RESOURCE_REFERENCE_ACTUAL.json'),no_target_CPU_GPU_yet=True))
print(json.dumps(dict(new_local_scope=str(N),second900_prepared=True,not_targetCPU_or_GPU=True)))

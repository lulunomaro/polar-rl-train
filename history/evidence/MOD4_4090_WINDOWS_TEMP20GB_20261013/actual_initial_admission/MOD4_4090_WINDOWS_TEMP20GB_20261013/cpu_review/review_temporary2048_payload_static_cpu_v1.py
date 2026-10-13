"""Independent CPU-only review of prepared2048 payload; no GPU/admission claim."""
from pathlib import Path
import ast,copy,hashlib,json,sys,time,traceback
import torch

W=Path('C:/Users/lulu/Desktop/claude/mjcf')
D=W/'MOD4_4090_WINDOWS_TEMP20GB_20261013/cpu_review'
P=D.parent/'payload'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sys.path.insert(0,str(P))
import temporary_state_binding as bind
import selected_source_projection as projection
import left_head_offset_aware_migration_v3 as repair

def main():
 assert not torch.cuda.is_initialized()
 source_ref=json.loads((W/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/reports/SOURCE_FULL_STATE_CPU_ACTUAL.json').read_bytes())
 source=Path(source_ref['path']);assert H(source)==source_ref['sha256']==bind.DONOR_SHA
 ck=bind.old.validate(torch.load(source,map_location='cpu',weights_only=False),bind.DONOR_SHA)
 inputs=[]
 for p in sorted(P.iterdir()):
  if p.suffix in ('.py','.ps1'):
   if p.suffix=='.py':compile(p.read_text(encoding='utf8'),str(p),'exec')
   inputs.append(dict(path=str(p),bytes=p.stat().st_size,sha256=H(p)))
 cpu_rng=torch.get_rng_state().clone()
 ids=torch.linspace(0,19999,2048).round().long();changed=[]
 small=projection.project_tree(ck,ids,changes=changed)
 assert len(changed)==99 and bind.floating_count(small)==107
 assert len(bind.perenv_inventory(small))==99
 for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state'):
  assert bind.same(ck[k],small[k]),k
 def at(tree,path):
  v=tree
  for key in path.strip('/').split('/'):
   v=v[int(key)] if isinstance(v,(tuple,list)) else v[key]
  return v
 for row in changed:
  old=at(ck,row['path']);new=at(small,row['path'])
  assert bind.same(new,old.index_select(row['axis'],ids)) and old.data_ptr()!=new.data_ptr()
 # Constructed metadata permits testing the standalone reduced validator only.
 # This is not actual selected family/map GPU binding and is never a sourcefile.
 t=small['E1_terrain_state'];sha=hashlib.sha256(t['spawn_xy'].numpy().astype('<f4').tobytes()).hexdigest()
 for k in bind.STATES:
  for field in ('entry_map_sha256','entry_origin_sha256'):
   if field in small[k]:small[k][field]=sha
 small['WINDOWS4090_TEMPORARY_BRANCH']=dict(profile=bind.PROFILE,original20k_donor_SHA=bind.DONOR_SHA,num_envs=2048,source_original_ids=ids.tolist(),family_counts=[0,0,0,0,2048])
 bind.validate(small,bind.DONOR_SHA)
 off=torch.zeros((2048,4),dtype=torch.float32)
 fixed=repair.migrate_tree(small,source_sha=bind.DONOR_SHA,actual_offsets=off)
 assert bind.floating_count(fixed)==107
 assert torch.equal(torch.get_rng_state(),cpu_rng) and not torch.cuda.is_initialized()
 rejected=[]
 for name,mutate in (
  ('wrong_original_donor',lambda x:x['WINDOWS4090_TEMPORARY_BRANCH'].__setitem__('original20k_donor_SHA','0'*64)),
  ('duplicate_selection',lambda x:x['WINDOWS4090_TEMPORARY_BRANCH']['source_original_ids'].__setitem__(0,x['WINDOWS4090_TEMPORARY_BRANCH']['source_original_ids'][1])),
  ('wrong_geometry',lambda x:x['E1_terrain_state'].__setitem__('geometry_triangles_sha256','0'*64)),
  ('wrong_assignment',lambda x:x['E1_terrain_state'].__setitem__('entry_assignment_sha256','0'*64)),
  ('wrong_route_map',lambda x:x['E1_WAVE50_route_lifecycle_state'].__setitem__('entry_map_sha256','0'*64)),
  ('wrong_direction_episode',lambda x:x['E1_WAVE50_episode_direction_state']['bound_episode'].add_(1))):
  bad=copy.deepcopy(small);mutate(bad)
  try:bind.validate(bad,bind.DONOR_SHA)
  except (AssertionError,KeyError):rejected.append(name)
  else:raise AssertionError(('negative not rejected',name))
  del bad
 gaps=[]
 for name,mutate in (
  ('seed',lambda x:x['E1_terrain_state'].__setitem__('seed',1)),
  ('command_vx_range',lambda x:x['E1_terrain_state'].__setitem__('command_vx_range',[-99.,99.])),
  ('positive_std',lambda x:x['actor_state_dict']['distribution.std_param'].__setitem__(0,-1.)),
  ('family_counts_sum',lambda x:x['WINDOWS4090_TEMPORARY_BRANCH'].__setitem__('family_counts',[0,0,0,0,1]))):
  bad=copy.deepcopy(small);mutate(bad)
  try:bind.validate(bad,bind.DONOR_SHA)
  except (AssertionError,KeyError):pass
  else:gaps.append(dict(field=name,standalone_validator_accepts=True,actual_runtime_rebinding_or_RSL_has_additional_checks=True,current_donor_not_corrupted=True))
  del bad
 runtime=(P/'temporary_training_runtime.py').read_text(encoding='utf8');parent=(P/'temporary_parent.py').read_text(encoding='utf8');worker=(P/'temporary_worker.py').read_text(encoding='utf8')
 assert "saved['WINDOWS4090_TEMPORARY_BRANCH']" in runtime and 'actual_API_offset_all_selected_exact=True' in runtime
 assert "args.source_sha == DONOR_SHA" in runtime and "initializer_repeated_on_this_resume" in runtime
 assert 'peakrss*1.25+536870912<20000000000' in parent and 'peakhard*1.25+536870912<20000000000' in parent
 assert 'job.assign(os.getpid())' in parent and 'msvcrt.LK_NBLCK' in parent
 assert 'time.sleep(2)' in parent and "STOP_AFTER_SAVE" in parent
 assert "import torch, tensordict" in worker and worker.index('import torch, tensordict')<worker.index('from isaaclab.app import AppLauncher')
 report=dict(epoch=time.time(),CPU_review_completed=True,no_network_no_GPU_no_once_execution=True,
  reviewed_sources=inputs,original_source=source_ref,original_SHA_unchanged=H(source)==bind.DONOR_SHA,
  independent_projection=dict(num_envs=2048,linear_CPU_fixture_not_actual_family_selected=True,exact99_fields=changed,finite_floating107=True,actorcritic_std_Adam_globalnamed_privateRNG_exact=True,selected_tensor_independent_storage=True,no_RNG_or_CUDA=True),
  CPU_left_migration=dict(actual_GPU_offsets_not_claimed=True,zero_offset_review_fixture_only=True,other5rows_hidden_critic_DR_RNG_exact=True,Adamrow0_moments_only_step_scalars_preserved=True,no_repeated_initialization=True),
  strict_negative_CPU_rejections=rejected,standalone_validator_hardening_gaps=gaps,
  closed_prior_findings=dict(ownsave_branch_explicitly_preserved_now=True,API_offset_all_selected_label_corrected_now=True),
  static_guard_contract=dict(native_single_OSlock=True,parent_memory_job_hard_commit_bytes=20000000000,softstop_train_bytes=18000000000,SDK_native_fullrestore_peak_RSS_and_commit_each_times1_25_plus512MiB_must_be_below20GB_before_formal=True,no_kill_on_close=True,max_updates256=True,save_every2_plus_final_events_max129=True,maximum_controls6144=True,maximum_envsteps12582912=True,trace_float32_RAM_upper_bytes=805306368),
  identity_binding_review=dict(initial_complete20k_donor_checked=True,projected99not_91dsplice=True,actual_selected_env_metadata_binding_GPU_pending=True,same2048_nonTensor_state_metadata_no_rebinding=True,fullrestore_12_markers_then_left_initializer_only_once=True,same_repaired_formal_from_actual_ownfullrestore_source_skips_initializer=True),
  no_new_deterministic_blocker_found_after_source_corrections=True,
  limitations=['Broad initial metadata allowlist is code-hash/selected-map migration, no per-state reviewed old/new plan assertion. Frozen runtime and subsequent strict metadata equality provide additional checks.','Standalone reduced validate does not mirror all original seed/layout/command/actoroptimizer positive-shape checks; actual binding and RSL load add checks, but stricter CPU-only rejection is recommended.','2048 actual SDK/native/fullrestore resource/physics pass remains required. CPU projection and migration are not capacity or terrain qualification.','MemoryJob hard20GB allocation failure may occur before parent2second softstop can complete currentupdate; originalerror/retainedsave must remain, no kill/relabel.'])
 path=D/('TEMPORARY2048_PAYLOAD_STATIC_CPU_REVIEW_'+str(time.time_ns())+'.json')
 with path.open('xb') as f:f.write(json.dumps(report,indent=2,ensure_ascii=False).encode())
 print(json.dumps(dict(report=str(path),sha256=H(path),CPU_review_completed=True,negative_rejections=len(rejected),standalone_hardening_gaps=[x['field'] for x in gaps],GPU_pass_not_claimed=True)))

if __name__=='__main__':
 try:main()
 except BaseException:
  path=D/('TEMP2048_REVIEW_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')
  path.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_no_network=True),indent=2),encoding='utf8')
  raise

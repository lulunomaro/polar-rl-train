"""New target whole-state CPU admission under original locks; never starts Kit or PPO."""
from pathlib import Path
import hashlib,json,os,sys,time,shutil,fcntl,traceback
SHA='f5166509d297814e3c3fe4f457ae064d9b02a8bd62702914759dc430f20d2139';KEY='E1_WAVE50_balanced_birth_bodyframe_state_v1';MARK='E1_WAVE50_BODYFRAME_OWN_GPU_SOURCE'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=sha(p))
def write(p,v):
 with Path(p).open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
def main(context):
 stage=Path(context['upload_stage']);root=Path(context['root']);base=Path(context['base']);prior=Path(context['prior']);created=False;locks=[]
 assert root.parent==base and stage.parent==base and not root.exists() and context['source_SHA']==SHA
 for name,h in context['files'].items():
  assert Path(name).name==name and sha(stage/name)==h
  if name.endswith('.py'):compile((stage/name).read_bytes(),str(stage/name),'exec')
 decision=json.loads((stage/'FOURCASE_SECOND_BODY_SCOPE_DECISION_ACTUAL.json').read_bytes())
 assert decision['passed'] is True and decision['all_own_four_cases_actual_complete'] is True and decision['second_body3600_reasonable'] is True
 assert decision['selected_source_SHA']==SHA and decision['scope_learning_block_index']==2 and decision['max_blocks_same_axis']==2
 assert decision['first_seconds']==300 and decision['second_seconds']==3600 and decision['total_axis_planned_seconds']==3900
 assert decision['qualified50'] is False and decision['qualified70'] is False and decision['new_axis_initializer_requested'] is False
 evidence={}
 for key,row in decision['evidence'].items():
  p=stage/('evidence_'+key+'.json');assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes'];evidence[key]=json.loads(p.read_bytes())
 assert evidence['own_final']['passed'] and evidence['own_final']['own_checkpoint']['sha256']==SHA and evidence['own_final']['actual_parent_guardian_child_out'] and evidence['own_final']['two_locks_free']
 assert evidence['three_pairs']['passed'] and evidence['three_pairs']['source_own_SHA']==SHA and evidence['three_pairs']['all_three_inherited_full1500_complete'] and not evidence['three_pairs']['pending']
 assert evidence['wave_direct']['passed'] and evidence['wave_direct']['new_source_SHA']==SHA and evidence['wave_direct']['actual_all_initial_root_q30_physical_parameters_recipes_assignments_captured_RNG_and_queue_values_exact'] is True
 assert evidence['wave_complete']['passed'] and evidence['wave_complete']['source_SHA']==SHA and evidence['wave_complete']['position_contact_agree_all_episodes'] is True and evidence['wave_complete']['all_valid_unfinished_and_preordinary_prefixes_preserved'] is True and evidence['wave_complete']['no_sameepisode_reset_teleport_credit'] is True
 assert evidence['wave_data']['passed'] and evidence['wave_data']['source_SHA']==SHA and evidence['wave_data']['full1500_original_data_contract_actual_passed'] and evidence['wave_data']['actual_parent_child_exited_and_shared_OSlockfree']
 sys.path.insert(0,str(stage));import bodyframe_original_CPU_guard as g
 try:
  for path in g.LOCKS:
   f=path.open('r+b');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
  budget=json.loads(g.B.read_bytes());g.budget_guard(budget);budget_before=sha(g.B)
  assert budget['remaining_training_seconds']-9400.860692501068>64800+3600
  import psutil,subprocess,torch
  assert psutil.virtual_memory().available>=55000000000 and shutil.disk_usage(base).free>=30000000000
  assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True).strip()
  complete=json.loads((prior/'PIPELINE_COMPLETE_REVIEW_READY.json').read_bytes());assert complete['passed'] and complete['formal']['passed'] and complete['formal']['updates']==6
  for kind in ('native','fullrestore'):
   assert complete[kind]['passed'] and complete[kind]['updates']==0 and complete[kind]['actual_GPU14_restore_passed']
  source=Path(complete['formal']['own_checkpoint']['path']);assert sha(source)==SHA and source.stat().st_size==19894311
  original=json.loads((prior/'PIPELINE_TARGET_CPU_ACTUAL.json').read_bytes());assert original['passed'] and original['original522_runtime_bytes_exact'] and len(original['base_runtime'])==522
  root.mkdir();created=True;runtime=root/'base_runtime';runtime.mkdir();rows=[]
  for item in original['base_runtime']:
   p=Path(item['path']);assert p.resolve().is_relative_to(prior.resolve()) and p.stat().st_size==item['bytes'] and sha(p)==item['sha256']
   target=runtime/item['relative'];assert target.resolve().is_relative_to(runtime.resolve());target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
   assert sha(target)==item['sha256'];rows.append(dict(path=str(target),relative=item['relative'],sha256=item['sha256'],bytes=target.stat().st_size))
  active=[]
  for name,h in context['files'].items():
   dst=root/name;shutil.copy2(stage/name,dst);assert sha(dst)==h;active.append(dict(name=name,sha256=h,bytes=dst.stat().st_size))
  rng=torch.get_rng_state().clone();assert not torch.cuda.is_initialized();ck=torch.load(source,map_location='cpu',weights_only=False)
  core={k:v for k,v in ck.items() if k not in (KEY,MARK)};info=g.logical_fullsave(core);fingerprint=g.tree_sha(ck)
  from birth_bodyframe_state_v1 import validate,clone
  from birth_bodyframe_full_checkpoint_v5 import bindings_from_checkpoint
  validate(ck[KEY],bindings_from_checkpoint(ck));assert ck[MARK]['actual_GPU_fullrestore'] is True and torch.equal(ck[KEY]['bound_episode'],ck['E1_terrain_state']['episode'])
  disk=root/'OWN_F516_WHOLE_CPU_ROUNDTRIP_NOT_SOURCE.pt';torch.save(ck,disk)
  with disk.open('r+b') as f:os.fsync(f.fileno())
  loaded=torch.load(disk,map_location='cpu',weights_only=False);assert g.same(ck,loaded)
  for key,tensor in g.walk(ck):
   other=dict(g.walk(loaded))[key]
   if tensor.numel():assert tensor.untyped_storage().data_ptr()!=other.untyped_storage().data_ptr()
  negatives=g.negative_logical_checks(core)
  body_negatives=[]
  for name in ('version','profile','bound_episode','flip_pi'):
   bad=clone(ck[KEY])
   if name=='version':bad[name]=2
   elif name=='profile':bad[name]='wrong'
   elif name=='bound_episode':bad[name][0]+=1
   else:bad[name][0]=not bool(bad[name][0])
   try:validate(bad,bindings_from_checkpoint(ck))
   except AssertionError:body_negatives.append(name)
   else:raise AssertionError('Bad owned body state accepted: '+name)
  assert g.tree_sha(ck)==fingerprint and sha(source)==SHA and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized() and sha(g.B)==budget_before
  result=dict(epoch=time.time(),passed=True,target_CPU_actual=True,source=rec(source),source_CPU_core=info,source_tree_SHA=fingerprint,whole_core_and_owned_BODY_independent_CPU_disk_roundtrip=True,disk_evidence_NOT_source=rec(disk),negative_core_cases=negatives,negative_owned_body_cases=body_negatives,original522_runtime_bytes_exact=True,base_runtime=rows,active_files=active,original_environment=original['original_environment'],canonical_bytes_unchanged=budget_before,GPU_dispatched=False,same_declared_BODY_profile_continuation=True,actual_fourcase_decision_bound=True,original_native_and_fullrestore_legal_proofs_reused_no_GPU_replay=True,previous_native_source=complete['native']['own_checkpoint'],previous_fullrestore_source=complete['fullrestore']['own_checkpoint'],new_axis_initializer_requested=False)
  write(root/'PIPELINE_TARGET_CPU_ACTUAL.json',result);print(json.dumps(dict(passed=True,root=str(root),source=rec(source),core=info,owned_BODY_CPU_verified=True,sourcefreeze_count=522+len(active),GPU_dispatched=False,target_receipt=rec(root/'PIPELINE_TARGET_CPU_ACTUAL.json'))))
 except BaseException:
  write((root if created else stage)/('SECOND_BODY_TARGET_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),new_root_created=created,no_GPU_or_budget_write=True));raise
 finally:
  for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
if __name__=='__main__':main(CONTEXT)

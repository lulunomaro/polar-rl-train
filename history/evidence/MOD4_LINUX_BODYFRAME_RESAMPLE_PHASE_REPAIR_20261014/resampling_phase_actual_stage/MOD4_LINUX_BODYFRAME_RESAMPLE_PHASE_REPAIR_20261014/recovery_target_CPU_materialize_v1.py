"""Admit retained whole state and a one-line sampler phase fix; no GPU is started."""
from pathlib import Path
import hashlib,json,os,sys,time,shutil,fcntl,traceback
SOURCE='1a370588db7706006a303e8d4ccd2efbb966201b826d3719ae42692a5339fd1a';KEY='E1_WAVE50_balanced_birth_bodyframe_state_v1';MARK='E1_WAVE50_BODYFRAME_OWN_GPU_SOURCE'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=sha(p))
def write(p,v):
 with Path(p).open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
def main(context):
 stage=Path(context['upload_stage']);root=Path(context['root']);base=Path(context['base']);failed=Path(context['failed']);original=Path(context['original']);locks=[];created=False
 assert stage.parent==root.parent==base and not root.exists() and context['source_SHA']==SOURCE
 for name,h in context['files'].items():
  assert Path(name).name==name and sha(stage/name)==h
  if name.endswith('.py'):compile((stage/name).read_bytes(),str(stage/name),'exec')
 decision=json.loads((stage/'RESAMPLING_PHASE_RECOVERY_SCOPE_DECISION_ACTUAL.json').read_bytes());assert decision['passed'] and decision['original_fourcase_actual_scope_bound'] and decision['remaining_second_allocation_recovery_reasonable']
 assert decision['selected_source_SHA']==SOURCE and decision['scope_learning_block_index']==2 and decision['max_blocks_same_axis']==2 and decision['recovery_max_seconds']==2470
 evidence={}
 for key,row in decision['evidence'].items():
  p=stage/('evidence_'+key+'.json');assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes'];evidence[key]=json.loads(p.read_bytes())
 retained=evidence['retained'];fix=evidence['phase_fix'];four=evidence['approved_fourcase'];assert retained['passed_retained_checkpoint_only'] and retained['original_scope_PARENT_FAIL_preserved'] and retained['source_checkpoint']['sha256']==SOURCE and retained['remaining_original_second_window_seconds']==2470
 assert fix['passed'] and fix['old_adapter_transient_ASSERT_reproduced'] and fix['new_adapter_defers_during_original_sampler_only'] and fix['stable_original_mapping_exact'] and fix['all_other_adapter_AST_exact']
 assert four['passed'] and four['all_own_four_cases_actual_complete'] and four['selected_source_SHA']=='f5166509d297814e3c3fe4f457ae064d9b02a8bd62702914759dc430f20d2139' and four['second_body3600_reasonable']
 sys.path.insert(0,str(stage));import bodyframe_original_CPU_guard as g
 try:
  for path in g.LOCKS:
   f=path.open('r+b');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
  d=json.loads(g.B.read_bytes());g.budget_guard(d);budget_before=sha(g.B);assert d['remaining_training_seconds']-9400.860692501068>64800+2470
  import psutil,subprocess,torch
  assert psutil.virtual_memory().available>=55000000000 and shutil.disk_usage(base).free>=30000000000 and not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True).strip()
  parent=json.loads((failed/'PARENT_IDENTITY.json').read_bytes());exit=json.loads((failed/'formal3600/attempt/EXIT_RECEIPT.json').read_bytes());assert (failed/'PIPELINE_ORIGINAL_ERROR.json').exists() and (failed/'GUARDIAN_EXIT.json').exists() and not (failed/'PIPELINE_COMPLETE_REVIEW_READY.json').exists()
  for row in (parent,exit['child']):
   try:assert psutil.Process(row['pid']).create_time()!=row['created']
   except psutil.NoSuchProcess:pass
  segment=[x for x in d['completed_segments'] if x['kind']==exit['canonical_unique_segment']];assert len(segment)==1
  actual_cost=segment[0]['ended_epoch']-segment[0]['started_epoch'];assert abs(actual_cost-retained['original_unique_parent_cost_seconds'])<1e-6 and int(3600-actual_cost)==2470
  latest=list((failed/'formal3600/attempt/learning_logs').glob('*/latest_complete.json'));assert len(latest)==1;source=Path(json.loads(latest[0].read_bytes())['checkpoint']);assert sha(source)==SOURCE and source.stat().st_size==19894311
  config=json.loads((failed/'PIPELINE_TARGET_CPU_ACTUAL.json').read_bytes());assert config['passed'] and config['original522_runtime_bytes_exact'] and len(config['base_runtime'])==522
  native=json.loads((original/'PIPELINE_COMPLETE_REVIEW_READY.json').read_bytes());assert native['passed'] and all(native[k]['passed'] and native[k]['updates']==0 and native[k]['actual_GPU14_restore_passed'] for k in ('native','fullrestore'))
  root.mkdir();created=True;runtime=root/'base_runtime';runtime.mkdir();rows=[]
  for item in config['base_runtime']:
   p=Path(item['path']);assert p.resolve().is_relative_to(failed.resolve()) and p.stat().st_size==item['bytes'] and sha(p)==item['sha256'];target=runtime/item['relative'];assert target.resolve().is_relative_to(runtime.resolve());target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);assert sha(target)==item['sha256'];rows.append(dict(path=str(target),relative=item['relative'],bytes=target.stat().st_size,sha256=item['sha256']))
  active=[]
  for name,h in context['files'].items():
   dst=root/name;shutil.copy2(stage/name,dst);assert sha(dst)==h;active.append(dict(name=name,bytes=dst.stat().st_size,sha256=h))
  rng=torch.get_rng_state().clone();assert not torch.cuda.is_initialized();ck=torch.load(source,map_location='cpu',weights_only=False);core={k:v for k,v in ck.items() if k not in (KEY,MARK)};info=g.logical_fullsave(core)
  from birth_bodyframe_state_v1 import validate
  from birth_bodyframe_full_checkpoint_v6_resample_guard import bindings_from_checkpoint
  validate(ck[KEY],bindings_from_checkpoint(ck));assert ck[MARK]['actual_GPU_fullrestore'] and torch.equal(ck[KEY]['bound_episode'],ck['E1_terrain_state']['episode']);tree=g.tree_sha(ck)
  disk=root/'RETAINED_WHOLE_CPU_ROUNDTRIP_NOT_SOURCE.pt';torch.save(ck,disk)
  with disk.open('r+b') as f:os.fsync(f.fileno())
  loaded=torch.load(disk,map_location='cpu',weights_only=False);assert g.same(ck,loaded)
  for key,tensor in g.walk(ck):
   other=dict(g.walk(loaded))[key]
   if tensor.numel():assert tensor.untyped_storage().data_ptr()!=other.untyped_storage().data_ptr()
  negative=g.negative_logical_checks(core);assert g.tree_sha(ck)==tree and sha(source)==SOURCE and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized() and sha(g.B)==budget_before
  result=dict(epoch=time.time(),passed=True,target_CPU_actual=True,source=rec(source),whole_core=info,owned_BODY_CPU_validated=True,whole_tree_SHA=tree,independent_whole_CPU_storage_disk_roundtrip=True,disk_evidence_NOT_source=rec(disk),negative_core_cases=negative,original522_runtime_bytes_exact=True,base_runtime=rows,active_files=active,original_environment=config['original_environment'],same_declared_BODY_profile_continuation=True,actual_fourcase_decision_bound=True,recovery_of_failed_second_block=True,remaining_second_allocation_seconds=2470,original_failed_parent_cost_seconds=actual_cost,original_failed_scope_NOT_PASS=True,canonical_bytes_unchanged=budget_before,original_native14_scope_reused_no_GPU_replay=True,GPU_dispatched=False,new_axis_initializer_requested=False)
  write(root/'PIPELINE_TARGET_CPU_ACTUAL.json',result);print(json.dumps(dict(passed=True,root=str(root),source=rec(source),core=info,owned_BODY_CPU_validated=True,sourcefreeze_count=522+len(active),GPU_dispatched=False,target_receipt=rec(root/'PIPELINE_TARGET_CPU_ACTUAL.json'))))
 except BaseException:
  write((root if created else stage)/('RECOVERY_TARGET_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),created=created,no_GPU_or_budgetwrite=True));raise
 finally:
  for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
if __name__=='__main__':main(CONTEXT)

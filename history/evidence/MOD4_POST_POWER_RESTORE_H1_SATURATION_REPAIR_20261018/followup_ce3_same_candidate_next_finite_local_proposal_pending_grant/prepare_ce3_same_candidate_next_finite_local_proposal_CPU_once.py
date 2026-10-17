"""Reviewable LOCAL proposal only. No deployer, transport, worker, GO or human approval is created."""
from pathlib import Path
import os,sys,json,time,ast,shutil,hashlib,types,importlib.util,copy,zipfile,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,numpy as np
from h1_owned_dual_FP64_mean_reference_same_bound_v1 import audit_saved_mean
B=Path(__file__).resolve().parent;R=B/'reports';OLD=B/'paid_mean_public4_v2/payload/h1';E=B/'proposal_ce3_same_candidate_finite_v1';Q=E/'payload/h1';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();SHA='ce3c69bbcf56bd6c884681f23f527b9fe9e1884a7b5444ff90d3f7a2e28b2d90'

def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();proof=json.loads((B/'paid_mean_public4_v2/reports/PUBLIC4_V2_H1_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json').read_bytes());frozen=json.loads((R/'H1_PUBLIC4FINAL_LINUX72_1500_ALL_PHYSICAL_PUBLIC04_SOURCE_FP64_REFERENCE_CPU_V3_ACTUAL.json').read_bytes());assert proof['passed_whole_final_model_local_CPU'] and proof['all17Adam_after']==646100 and proof['complete_final']['SHA']==SHA and proof['actual_original_owner_node_all_children_out'] and proof['original_canonicalNone_two_real_fcntlFree_and_target_GPU_private_shared_free'];assert frozen['passed_complete_data_and_source_CPU'] and frozen['source_SHA']==SHA and frozen['first_episode_before_failed_control_events']==dict(takeoff=39,landing=12,recovery=0)
 assert not E.exists();m=json.loads((OLD/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());E.mkdir();(E/'reports').mkdir();Q.mkdir(parents=True)
 omitted=[]
 for row in m['files']:
  src=OLD/row['relative'];assert src.stat().st_size==row['bytes'] and H(src)==row['SHA']
  if src.name=='migrate_saved_reward.py':
   omitted.append(dict(path=str(src),bytes=src.stat().st_size,SHA=H(src),reason='Unused standalone historical migration tool; original remains unchanged, not needed by native/production import graph'));continue
  dest=Q/row['relative'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
 for p in OLD.rglob('*.py'):
  if p.name=='migrate_saved_reward.py':continue
  for node in ast.walk(ast.parse(p.read_text('utf8'))):
   if isinstance(node,ast.Import):assert all(x.name.split('.')[0]!='migrate_saved_reward' for x in node.names)
   if isinstance(node,ast.ImportFrom):assert (node.module or '').split('.')[0]!='migrate_saved_reward'
 shutil.copy2(OLD/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',Q/'PREVIOUS_PUBLIC4_V2_MANIFEST_HISTORICAL.json')
 (Q/'job0/source/H1_final10_protected.pt').unlink();source=Q/'job0/source/H1_ce3_public4_closed24.pt';shutil.copy2(proof['complete_final']['local_path'],source);assert H(source)==SHA
 ck=torch.load(source,map_location='cpu',weights_only=False)
 def validate(c):
  assert c['owned_H1_phase']=='production' and c['owned_H1_completed_updates']==24 and c['failed_partial_prefix'] is False and {int(x['step']) for x in c['optimizer_state_dict']['state'].values()}=={646100};assert len(c['actor_state_dict'])==9 and len(c['critic_state_dict'])==8 and len(c['optimizer_state_dict']['state'])==17;assert c['actor_state_dict']['mlp.0.weight'].shape==(256,35) and c['critic_state_dict']['mlp.0.weight'].shape==(256,38);assert (c['actor_state_dict']['distribution.std_param']>0).all() and c['owned_H1_learning_task']['optimization_candidate']['name']=='public4_only_mean_overflow_regularizer_v2' and c['owned_H1_learning_task']['optimization_candidate']['coefficient']==.001
  counts=[0,0]
  def visit(x):
   if torch.is_tensor(x):
    counts[0]+=1
    if x.is_floating_point():counts[1]+=1;assert torch.isfinite(x).all()
   elif isinstance(x,dict):
    for v in x.values():visit(v)
   elif isinstance(x,(list,tuple)):
    for v in x:visit(v)
  visit(c);assert counts==[199,105];return counts
 assert validate(ck)==[199,105];bad=[]
 for label,change in [('phase',lambda c:c.__setitem__('owned_H1_phase','native')),('updates',lambda c:c.__setitem__('owned_H1_completed_updates',1)),('Adam',lambda c:next(iter(c['optimizer_state_dict']['state'].values()))['step'].fill_(645620)),('input_shape',lambda c:c['actor_state_dict'].__setitem__('mlp.0.weight',torch.zeros(256,34))),('STD',lambda c:c['actor_state_dict']['distribution.std_param'].fill_(-1)),('nonfinite',lambda c:c['critic_state_dict']['mlp.0.weight'].fill_(float('nan'))),('failed_prefix',lambda c:c.__setitem__('failed_partial_prefix',True)),('candidate',lambda c:c['owned_H1_learning_task']['optimization_candidate'].__setitem__('name','global')),('coefficient',lambda c:c['owned_H1_learning_task']['optimization_candidate'].__setitem__('coefficient',.01))]:
  v=copy.deepcopy(ck);change(v)
  try:validate(v)
  except AssertionError:bad.append(label)
  else:raise AssertionError(label)
 changed=[]
 for name in ['h1_ground_prelaunch_v2_native_worker_v1.py','h1_prelaunch_v2_production_worker_v1.py','review_H1_prelaunch_v2_native_allrows_CPU_v1.py']:
  p=Q/name;s=p.read_text('utf8');s=s.replace('H1_final10_protected.pt','H1_ce3_public4_closed24.pt').replace('645620','646100');ast.parse(s);p.write_text(s,encoding='utf8');changed.append(name)
 p=Q/'review_H1_prelaunch_v2_native_allrows_CPU_v1.py';s=p.read_text('utf8');start=s.index("  y=torch.from_numpy(x.reshape(-1,35));sd=s['actor_state_dict']");end=s.index(' assert control_count==180',start);original=s[start:end];assert 'assert maxmean<=1e-4' in original
 replacement="  from h1_owned_dual_FP64_mean_reference_same_bound_v1 import audit_saved_mean\n  precision=audit_saved_mean(s['actor_state_dict'],x.reshape(-1,35),d['raw6'].reshape(-1,6));reference_metrics.append(precision);maxmean=max(maxmean,precision['torch64_maxabs'],precision['numpy64_maxabs']);assert maxmean<=1e-4;control_count+=len(x)\n"
 s=s[:start]+replacement+s[end:];s=s.replace('def main():\n','def main():\n reference_metrics=[]\n',1).replace('all_saved_actor_CPUmean_maxabs=maxmean,','all_saved_actor_CPUmean_maxabs=maxmean,actor_reference_protocol="Independent Torch/NumPy FP64 on original F32 weights/observations, original absolute1e-4 unchanged",original_FP32_maxabs_diagnostic=max(r["original_fp32_maxabs"] for r in reference_metrics),original_FP32_pass_diagnostic=all(r["original_fp32_maxabs"]<=1e-4 for r in reference_metrics),dual_FP64_cross_maxabs=max(r["reference_cross_maxabs"] for r in reference_metrics),');ast.parse(s);p.write_text(s,encoding='utf8');shutil.copy2(B/'h1_owned_dual_FP64_mean_reference_same_bound_v1.py',Q/'h1_owned_dual_FP64_mean_reference_same_bound_v1.py')
 collection=json.loads((R/'LINUX_GPU1_PUBLIC4FINAL_FULL1500_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json').read_bytes());raw=next(x for x in collection['files'] if x['relative'].endswith('/retention_full_control_substep_actual.npz'))
 with np.load(raw['local_path'],allow_pickle=False) as z:obs=z['policy_obs'].reshape(-1,35).copy();actual=z['raw_actor_action'].reshape(-1,6).copy()
 precision=audit_saved_mean(ck['actor_state_dict'],obs,actual);negative_precision=[]
 for label,o,a in [('shape',obs[:2,:34],actual[:2]),('obs_dtype',obs[:2].astype(np.float64),actual[:2]),('nan',np.full_like(obs[:2],np.nan),actual[:2]),('over_original_bound',obs[:2],actual[:2]+.01)]:
  try:audit_saved_mean(ck['actor_state_dict'],o,a)
  except AssertionError:negative_precision.append(label)
  else:raise AssertionError(label)
 taskp=Q/'job0/TASK.json';task=json.loads(taskp.read_bytes());task.update(id='H1_CE3_SAME_PUBLIC4_V2_NEXT_FINITE_PENDING_HUMAN_20261018',source_SHA=SHA,source_Adamstep=646100,source_owned_completed_updates=24,exact_closed_source_owned_updates=24,source_filename=source.name,proposal_only_requires_explicit_new_human_finite_grant=True,CPU_is_not_learning_permission=True,newsource_native180_required=True,same_source_backend_native_reused_not_replayed=False,max_parent_seconds=1800,exit_headroom_seconds=300,max_completed_updates=24,no_automatic_following_window=True,complete_state_continuation_not_rollback=True);task.pop('explicit_protected_b326_baseline_rollback_after_unmasked_readiness_regression',None);taskp.write_text(json.dumps(task,indent=2),encoding='utf8')
 changed.append('job0/TASK.json');files=[]
 for p in sorted(Q.rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts:
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   files.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
 current=dict(m,source_SHA=SHA,source_Adamstep=646100,files=files,source_filename=source.name,proposal_only_no_human_grant=True,exact_changed_wrapper_files=changed,native_CPU_reference_precision_change_only_same_absolute1e4=True,unused_historical_helpers_not_selected=['h1_prelaunch_v2_native_CPU_production_node_v1.py','h1_same_source_native_reuse_v1.py'],omitted_unused_standalone_migration_tools=omitted);current.pop('explicit_source_Adam_expectation_changes',None);mf=Q/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';mf.write_text(json.dumps(current,indent=2),encoding='utf8')
 unchanged=[]
 for row in m['files']:
  rel=row['relative']
  if rel in changed or rel=='job0/source/H1_final10_protected.pt' or Path(rel).name=='migrate_saved_reward.py':continue
  assert H(Q/rel)==row['SHA'],rel;unchanged.append(rel)
 oldspec=json.loads((B/'paid_mean_public4_v2/reports/PUBLIC4_REPAIR_V2_H1_FINITE_NEW_SOURCE_NATIVE_PAYLOAD_CPU_ACTUAL.json').read_bytes())['specs'];spec=copy.deepcopy(oldspec['h1']);spec.update(source_SHA=SHA,source_Adamstep=646100,source_filename=source.name,manifest_SHA=H(mf),previous_runtime_root='/home/lc01/Zonglin Li/zonglin2/tasks/H1mp_1810p2')
 fcntl=types.ModuleType('fcntl');fcntl.flock=lambda *a:(_ for _ in ()).throw(AssertionError('No actual OS lock attempted in CPU'));previous=sys.modules.get('fcntl');sys.modules['fcntl']=fcntl
 try:
  sp=importlib.util.spec_from_file_location('ce3_proposal_common_CPU_only',Q/'three_slot_common_v1.py');common=importlib.util.module_from_spec(sp);sp.loader.exec_module(common);common.validate_payload(spec)
 finally:
  if previous is None:sys.modules.pop('fcntl',None)
  else:sys.modules['fcntl']=previous
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 bundle=E/'H1_CE3_SAME_CANDIDATE_NEXT_FINITE_PROPOSAL_V1.zip'
 with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for row in files:z.write(Q/row['relative'],'h1/'+row['relative'])
  z.write(mf,'h1/'+mf.name)
 out=dict(epoch=time.time(),passed_LOCAL_CPU_only=True,proposal_id='h1-ce3-same-public4-v2-single-finite-pending-human-20261018',source=dict(path=str(source),bytes=source.stat().st_size,SHA=SHA,owned_updates=24,Adam=646100),complete_source_counts=[199,105],source_negative_cases=bad,precision_negative_cases=negative_precision,reference_test_on_existing_complete_raw_only=precision,actual_raw_reference=raw,manifest=dict(path=str(mf),bytes=mf.stat().st_size,SHA=H(mf)),package=dict(path=str(bundle),bytes=bundle.stat().st_size,SHA=H(bundle)),proposed_spec=spec,proposed_target_root='/home/lc01/Zonglin Li/zonglin2/tasks/H1cq_1810p3',proposed_owner_root='/mnt/mod4_linux_durable_20261013/H1cq_1810p3/owner',prior_owner_and_children_actual_closed_evidence=str(B/'paid_mean_public4_v2/reports/PUBLIC4_V2_H1_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json'),all_unchanged_manifest_file_count=len(unchanged),unchanged_policy_optimization_coeff001_LR_STD_and_environment_physics_reward_DR_CAD_hardware=True,all_four_original_controllers_byteexact=True,exact_wrapper_metadata_and_audit_precision_changes=changed,original_FP32_false_retained_same_H1_absolute1e4_no_E3_geometry_exception=True,source_filename_historical_labels_replaced_for_selected_scripts_only=True,omitted_unused_standalone_tools=omitted,proposed_native180_720_3p6Mpolicy14p4Mphysical_then_independent_CPU_required=True,proposed_paid_cap1800_headroom300_max24_free8GiB_25GiBstart=True,planned_expert_seconds_ceiling1800_no_new_budget=True,E2_E3_hold0worker_GO_charge=True,human_approval_received=False,no_deployer_or_host_connection_or_Task_GPU_GO_or_budget_mutation=True,fresh_actual_resource_source_SDK_and_original_lock_handoff_still_required_after_approval=True,CPU_RNG_unchanged0CUDA0optimizer=True,initial_lookup_misses_old_preparer_name_and_unused_native_admission_alias_preserved_as_local_only=True)
 with (R/'H1_CE3_NEXT_SAME_CANDIDATE_FINITE_REVIEWABLE_LOCAL_CPU_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(proposal_CPU=True,source_SHA=SHA,Adam=646100,source_negative_cases=len(bad),precision_negative_cases=len(negative_precision),files=len(files),no_host_or_training=True,approval_received=False)))

if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('CE3_NEXT_FINITE_LOCAL_PROPOSAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_budget_mutation=True),f,indent=2)
  raise

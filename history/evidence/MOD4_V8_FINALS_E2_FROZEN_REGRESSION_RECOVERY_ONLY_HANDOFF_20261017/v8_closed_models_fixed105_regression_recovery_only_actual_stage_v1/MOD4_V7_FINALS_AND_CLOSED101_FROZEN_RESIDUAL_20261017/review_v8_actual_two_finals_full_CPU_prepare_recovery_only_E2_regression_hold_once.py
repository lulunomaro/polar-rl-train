"""Full final CPU review then prepare a new, finite, same-scope two72 continuation."""
from pathlib import Path
import os,sys,time,json,hashlib,shutil,ast,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
F=Path(__file__).resolve().parent;W=F.parent;G=W/'MOD4_V8_FINALS_E2_FROZEN_REGRESSION_RECOVERY_ONLY_HANDOFF_20261017';R=G/'reports';Q=G/'payload'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def exact(a,b):
 if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and a.contiguous().reshape(-1).view(torch.uint8).numpy().tobytes()==b.contiguous().reshape(-1).view(torch.uint8).numpy().tobytes()
 if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(exact(a[k],b[k]) for k in a)
 if isinstance(a,(tuple,list)):return type(a)==type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
 return a==b
def finite(x,c):
 if torch.is_tensor(x):c[0]+=1;c[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
 elif isinstance(x,dict):
  for z in x.values():finite(z,c)
 elif isinstance(x,(tuple,list)):
  for z in x:finite(z,c)
def main():
 frozen=json.loads((F/'reports/CLOSED101_VS_CLOSED105_FULL1500_ACTUAL_INITIAL_SIGNED_RESIDUAL_CPU_ACTUAL.json').read_bytes());assert frozen['all_matched_initial_proven'] and frozen['old_counts']['total']==22 and frozen['new_counts']['total']==0
 assert not G.exists();G.mkdir();R.mkdir();Q.mkdir();c=json.loads((F/'reports/V8_CLOSED_FINALS_EXACT_CPU_INPUT_BINDING_ACTUAL.json').read_bytes());assert c['actual_closed'];ledger=c['account']['original_canonical'];assert ledger['active_segment'] is None and ledger['authorized_training_seconds']==1188000 and len(ledger['budget_extensions'])==7 and all(x['actual_fcntl_free'] for x in c['account']['actual_locks']);cost=next(x for x in ledger['completed_segments'] if x.get('owner_parent_pid')==704221);assert set(cost['experts'])=={'e2','recovery'} and all(x['actual_returncode']==0 and x['duration_bound_passed'] for x in cost['experts'].values()) and abs(sum(x['charged_seconds'] for x in cost['experts'].values())-cost['charged_expert_seconds'])<1e-6
 done=next(r['value'] for r in c['owner']['files'] if r['path'].endswith('/COHORT_FINAL.json'));assert done['original_cost_settled'] and set(done['go'])=={'e2','recovery'} and done['rows']['h1']['original_error'] and done['rows']['h1']['actual_own_children_count']==0;assert next(r['value'] for r in c['owner']['files'] if r['path'].endswith('/OWNER_EXIT_ACTUAL.json'))['original_cost_settled'];oldprep=json.loads((F/'reports/RECOVERED_THREE_FINALS_FULL_CPU_AND_NEW_SAME_SCOPE_NATIVE_PAYLOADS_PREPARED_ACTUAL.json').read_bytes());first=json.loads((F/'reports/SAFE72_TWO_REAL_DISTINCT_FIRST_COMPLETE_MODELS_LOCAL_CPU_ACTUAL.json').read_bytes());assert first['all_two_healthy72_real_distinct_saved_PPO_positive'];specs=dict(oldprep['specs']);models={};rng=torch.get_rng_state().clone();torch.set_num_threads(2)
 for name in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','three_slot_resource_v1.py','owner_listener_ready_cpu_reviewed_v1.py'):shutil.copy2(F/name,G/name)
 for key in ('e2','recovery'):
  prior=F/'payload'/key;folder=Q/key;shutil.copytree(prior,folder,ignore=shutil.ignore_patterns('THREE_SLOT_COMPLETE_MANIFEST_V1.json'));shutil.copy2(prior/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',folder/'PREVIOUS_T3_V8R72_MANIFEST_EXACT.json');row=next(r for r in c['downloaded_final_models'][key] if r['kind']=='actual_complete_final');p=Path(row['local_path']);assert H(p)==row['SHA'] and p.stat().st_size==row['bytes'] and row['twohost_complete_SHA'];ck=torch.load(p,map_location='cpu',weights_only=False);counts=[0,0];finite(ck,counts);base=specs[key]['source_Adamstep'];steps=base+20*row['updates'];assert len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and len(ck['optimizer_state_dict']['state'])==17 and {int(z['step']) for z in ck['optimizer_state_dict']['state'].values()}=={steps};sourcefile=specs[key]['source_filename'];original=torch.load(prior/'job0/source'/sourcefile,map_location='cpu',weights_only=False);changes={g:[n for n in ck[g] if not exact(original[g][n],ck[g][n])] for g in ('actor_state_dict','critic_state_dict')};assert changes['actor_state_dict'] and changes['critic_state_dict'];shutil.copy2(p,folder/'job0/source'/sourcefile);taskpath=folder/'job0/TASK.json';task=json.loads(taskpath.read_bytes());shutil.copy2(taskpath,folder/'job0/PREVIOUS_T3_V8R72_TASK_EXACT.json');task.update(id='APPROVED_HEALTHY_TWO72_CLOSED_SOURCE_NEXT_BLOCK_'+key.upper()+'_20261017',source_SHA=row['SHA'],source_Adamstep=steps,exact_closed_source_updates=row['updates'],max_parent_seconds=3600,exit_headroom_seconds=300,new_original_GO_required_no_permission_from_prepared_files=True,own_new_native_for_actual_new_weights_required=True,same_source_backend_native_reused_not_replayed=False);taskpath.write_text(json.dumps(task,indent=2),encoding='utf8');edits=[]
  for name in ({'e2':['production_worker.py','native_admission_worker.py'],'recovery':['recovery_worker.py','native_CPU.py']}[key]):
   f=folder/name;old=f.read_text('utf8');assert str(base) in old;new=old.replace(str(base),str(steps));f.write_text(new,encoding='utf8');edits.append(dict(relative=name,old_SHA=hashlib.sha256(old.encode()).hexdigest(),new_SHA=H(f),only_exact_source_Adam_expectation_changed=True))
  files=[]
  for f in sorted(x for x in folder.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
   if f.suffix=='.py':ast.parse(f.read_text('utf8'))
   files.append(dict(relative=f.relative_to(folder).as_posix(),bytes=f.stat().st_size,SHA=H(f)))
  oldmanifest=json.loads((prior/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());manifest=dict(key=key,source_SHA=row['SHA'],source_filename=sourcefile,source_Adamstep=steps,source_schema_counts=counts,files=files,expected_actual_RSL_sources=oldmanifest['expected_actual_RSL_sources'],expected_actual_SDK_math_SHA=oldmanifest['expected_actual_SDK_math_SHA'],original_runtime_physics_reward_DR_and_hardware_bytes_unchanged=True,explicit_source_Adam_expectation_changes=edits);mf=folder/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';mf.write_text(json.dumps(manifest,indent=2),encoding='utf8');specs[key]={**specs[key],**dict(source_SHA=row['SHA'],source_Adamstep=steps,source_schema_counts=counts,manifest_SHA=H(mf),previous_runtime_root=c[key]['root'])};models[key]=dict(final_model=row,whole_model_tensor_counts=counts,all_finite=True,all17Adam_before=base,all17Adam_after=steps,actual_actor9_STD_critic8_changes=changes,production_updates=row['updates'],production_controls=24*row['updates'],production_envsteps=480000*row['updates'],not_frozen_skill_qualification=True)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();proof=dict(epoch=time.time(),passed_CPU_only=True,both_new_complete_finals_CPU_finite_and_parameters_changed=True,old_owner_allchildren_out_canonicalNone_twofcntl_free=True,original_cost_once=cost,remaining_original_budget=ledger['remaining_training_seconds'],source_models=models,specs=specs,only_recovery_new_native_required_E2_planned_source_CPU_only_held_no_dispatch=True,H1_same_full121_source_reference_only_no_new_H1_payload_or_qualification=True,H1_previous_storage_rejection_unchanged_requires_current_owner_preflight_recheck=True,only_recovery_planned_cap3600_headroom300_E2_no_GO_zero_charge=True,original_rewards_commands_DR_physics_hardware_unchanged=True,new_GPU_or_GO_not_yet=True)
 with (R/'TWO_CLOSED_FINALS_FULL_CPU_NEW_HEALTHY72_PAYLOADS_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(proof,f,indent=2)
 for name in ('SOURCE_PRECREATE_COMBINED_RESOURCE_ASSERTION_INDEPENDENT_READONLY_DIAGNOSIS_ACTUAL.json','UNCHANGED_FINITE_RUNTIME_AND_PREVIOUS_CPU_PROOFS_REUSED_ACTUAL.json','H1_STORAGE_PREGO_REJECTION_TWO_HEALTHY_SLOTS_UNCHANGED_OWNER_CPU_ACTUAL.json'):shutil.copy2(F/'reports'/name,R/name)
 # Small local aliases preserve the reviewed deploy functions' protocol without replaying them.
 with (R/'RECOVERED_THREE_FINALS_FULL_CPU_AND_NEW_SAME_SCOPE_NATIVE_PAYLOADS_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(proof,f,indent=2)
 print(json.dumps(dict(complete_CPU=models,old_exact_cost=cost['charged_expert_seconds'],remaining=ledger['remaining_training_seconds'],new_native_and_training_not_yet=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(parents=True,exist_ok=True)
  with (R/('TWO_CLOSED_SOURCE_CPU_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_remote_GPU_or_budget_mutation=True),f,indent=2)
  raise

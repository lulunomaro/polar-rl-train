"""Freeze actual completed sources; new bounded work on the same three subjects."""
from pathlib import Path
import os,sys,time,json,hashlib,shutil,ast,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
V=Path(__file__).resolve().parent;W=V.parent;U=W/'MOD4_THREE_EXPERTS_RECOVERED_FULL_FINAL_CONTINUATION_20261017';R=V/'reports';Q=V/'payload'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def exact(a,b):
 if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and a.contiguous().reshape(-1).view(torch.uint8).numpy().tobytes()==b.contiguous().reshape(-1).view(torch.uint8).numpy().tobytes()
 if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(exact(a[k],b[k]) for k in a)
 if isinstance(a,(list,tuple)):return type(a)==type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
 return a==b
def finite(x,c):
 if torch.is_tensor(x):c[0]+=1;c[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
 elif isinstance(x,dict):
  for z in x.values():finite(z,c)
 elif isinstance(x,(list,tuple)):
  for z in x:finite(z,c)
def write(p,s):
 assert not p.exists();p.write_text(s,encoding='utf8')
def main():
 R.mkdir(exist_ok=True);assert not Q.exists();c=json.loads((U/'reports/WINDOW_V2_THREE_FINALS_EXISTING_FULLSAVE_COST_EXIT_ORIGINAL_HANDOFF_COLLECTION_ACTUAL.json').read_bytes());first=json.loads((U/'reports/THREE_SLOT_REAL_DISTINCT_FIRST_COMPLETE_MODELS_LOCAL_CPU_ACTUAL.json').read_bytes());assert first['all_three_real_distinct_saved_PPO_positive'];account=c['account'];ledger=account['original_canonical'];assert ledger['active_segment'] is None and all(x['actual_fcntl_free'] for x in account['actual_locks']);cost=next(x for x in ledger['completed_segments'] if x.get('owner_parent_pid')==622585);assert all(x['actual_returncode']==0 and x['duration_bound_passed'] for x in cost['experts'].values()) and abs(sum(x['charged_seconds'] for x in cost['experts'].values())-cost['charged_expert_seconds'])<1e-6
 assert all(not c[k]['actual_own_processes'] for k in ('owner','h1','e2','recovery'));assert next(x['value'] for x in c['owner']['files'] if x['path'].endswith('/COHORT_FINAL.json'))['original_cost_settled'];assert next(x['value'] for x in c['owner']['files'] if x['path'].endswith('/OWNER_EXIT_ACTUAL.json'))['original_cost_settled'];rng=torch.get_rng_state().clone();torch.set_num_threads(2);models={};specs={};Q.mkdir()
 # Runtime is exact to the tested and actually executed v2. No repeated fixtures.
 for name in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','three_slot_resource_v1.py'):shutil.copy2(U/name,V/name)
 for key in ('h1','e2','recovery'):
  prior=U/'payload'/key;b=Q/key;shutil.copytree(prior,b,ignore=shutil.ignore_patterns('THREE_SLOT_COMPLETE_MANIFEST_V1.json'));shutil.copy2(prior/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',b/'PREVIOUS_WINDOW_V2_COMPLETE_MANIFEST_EXACT.json')
  row=next(x for x in c['downloaded_final_models'][key] if x['kind']=='actual_complete_final');p=Path(row['local_path']);assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'] and row['twohost_complete_SHA'];s=torch.load(p,map_location='cpu',weights_only=False);counts=[0,0];finite(s,counts);base=first['experts'][key]['first']['all17Adam_before'];steps=base+row['updates']*20;assert {int(x['step']) for x in s['optimizer_state_dict']['state'].values()}=={steps} and len(s['actor_state_dict'])==9 and len(s['critic_state_dict'])==8;oldsource=next((prior/'job0/source').glob({'h1':'H1_final10_protected.pt','e2':'E2_final58.pt','recovery':'E0_full_source.pt'}[key]));oldck=torch.load(oldsource,map_location='cpu',weights_only=False);changes={g:[n for n in s[g] if not exact(s[g][n],oldck[g][n])] for g in ('actor_state_dict','critic_state_dict')};assert changes['actor_state_dict'] and changes['critic_state_dict'];sourcefile=oldsource.name;shutil.copy2(p,b/'job0/source'/sourcefile)
  task=json.loads((b/'job0/TASK.json').read_bytes());shutil.copy2(b/'job0/TASK.json',b/'job0/PREVIOUS_WINDOW_V2_TASK_EXACT.json');task.update(id='APPROVED_HEALTHY_SAME_SCOPE_FOLLOWUP_V3_'+key.upper()+'_20261017',source_SHA=row['SHA'],source_Adamstep=steps,exact_closed_source_updates=row['updates'],max_parent_seconds=3600,exit_headroom_seconds=300,new_original_GO_required_no_permission_from_prepared_files=True,own_new_native_for_actual_new_weights_required=True,same_source_backend_native_reused_not_replayed=False)
  if key=='h1':task.update(source_H1_V2_final25_17Adam640260=False,source_H1_V2_final51_17Adam641280=False,source_H1_actual_latest_completed_updates=row['updates'],source_H1_actual_latest_Adamstep=steps,first_new_human_continue_bound1800_including_production_load_learn_save_exit=False,new_human_reconnected_followup_cap3600_including_production_loadlearnsaveexit=True)
  (b/'job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8');edits=[]
  targets={'h1':['h1_prelaunch_v2_production_worker_v1.py','review_H1_prelaunch_v2_native_allrows_CPU_v1.py'],'e2':['production_worker.py','native_admission_worker.py'],'recovery':['recovery_worker.py','native_CPU.py']}[key]
  for name in targets:
   f=b/name;old=f.read_text('utf8');assert str(base) in old;fixed=old.replace(str(base),str(steps))
   if key=='h1' and 'production_worker' in name:assert "go['max_parent_seconds']==1800" in fixed;fixed=fixed.replace("go['max_parent_seconds']==1800","go['max_parent_seconds']==3600")
   f.write_text(fixed,encoding='utf8');edits.append(dict(relative=name,old_SHA=hashlib.sha256(old.encode()).hexdigest(),new_SHA=H(f),source_Adam_expected_only_except_explicit_new_finite_H1_grant_cap=True))
  for name in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','three_slot_resource_v1.py'):shutil.copy2(V/name,b/name)
  if key=='h1':shutil.copy2(U/'payload/e2/native_CPU_status_bridge_v1.py',b/'native_CPU_status_bridge_v1.py')
  files=[]
  for f in sorted(x for x in b.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
   if f.suffix=='.py':ast.parse(f.read_text('utf8'))
   files.append(dict(relative=f.relative_to(b).as_posix(),bytes=f.stat().st_size,SHA=H(f)))
  oldmanifest=json.loads((prior/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());m=dict(key=key,source_SHA=row['SHA'],source_filename=sourcefile,source_Adamstep=steps,source_schema_counts=counts,files=files,expected_actual_RSL_sources=oldmanifest['expected_actual_RSL_sources'],expected_actual_SDK_math_SHA=oldmanifest['expected_actual_SDK_math_SHA'],original_runtime_physics_reward_DR_and_hardware_bytes_unchanged=True,explicit_source_Adam_expectation_changes=edits,new_H1_native180_for_new51weights_not_old25_reuse=True);mf=b/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';mf.write_text(json.dumps(m,indent=2),encoding='utf8')
  oldspec=json.loads((U/'reports/THREE_SLOT_ACTUAL_CLOSED_SOURCES_FULL_CPU_FROZEN_PAYLOADS_PREPARED.json').read_bytes())['specs'][key];specs[key]={**oldspec,**dict(source_SHA=row['SHA'],source_Adamstep=steps,source_schema_counts=counts,manifest_SHA=H(mf),max_parent_seconds=3600,previous_runtime_root=c[key]['root'],native_script='h1_ground_prelaunch_v2_native_worker_v1.py' if key=='h1' else oldspec['native_script'],native_CPU_script='review_H1_prelaunch_v2_native_allrows_CPU_v1.py' if key=='h1' else 'native_CPU.py')};models[key]=dict(final_model=row,whole_model_tensor_counts=counts,all_finite=True,all17Adam_before=base,all17Adam_after=steps,actual_changes=changes,production_updates=row['updates'],production_envsteps=480000*row['updates'],not_frozen_skill_qualification=True)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();proof=dict(epoch=time.time(),passed_CPU_only=True,all_three_complete_finals_finite=True,old_owner_allchildren_out_canonicalNone_twofcntl_free=True,original_cost_once=cost,remaining_original_budget=ledger['remaining_training_seconds'],new_distinct_cap_sum10800_not_budget_extension=True,source_models=models,specs=specs,all_three_own_new_native_required=True,original_rewards_commands_DR_physics_hardware_unchanged=True,new_GPU_or_GO_not_yet=True,old_network_pending0_retained_separate=True);out=R/'RECOVERED_THREE_FINALS_FULL_CPU_AND_NEW_SAME_SCOPE_NATIVE_PAYLOADS_PREPARED_ACTUAL.json';assert not out.exists();out.write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(dict(models={k:dict(SHA=v['final_model']['SHA'],updates=v['production_updates'],Adam=v['all17Adam_after'],counts=v['whole_model_tensor_counts']) for k,v in models.items()},old_actual_unique_cost=cost['charged_expert_seconds'],remaining=ledger['remaining_training_seconds'],new_training_not_yet=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(exist_ok=True)
  with (R/('NEW_THREE_SLOT_SOURCE_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_remote_GPU_or_budget_write=True),f,indent=2)
  raise

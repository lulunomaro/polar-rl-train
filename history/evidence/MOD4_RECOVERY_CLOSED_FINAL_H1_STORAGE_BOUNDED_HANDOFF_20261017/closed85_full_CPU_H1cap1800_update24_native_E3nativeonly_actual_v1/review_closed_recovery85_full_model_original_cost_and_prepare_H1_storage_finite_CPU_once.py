"""Full CPU freeze and a new storage-bounded H1 grant; recovery next is native-only review."""
from pathlib import Path
import os,sys,time,json,hashlib,shutil,ast,traceback,importlib.util,types
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';Q=B/'payload';K=W/'MOD4_V8_FINALS_E2_FROZEN_REGRESSION_RECOVERY_ONLY_HANDOFF_20261017';F=W/'MOD4_THREE_EXPERTS_HEALTHY_FOLLOWUP_V3_20261017'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sys.path.insert(0,str(W/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'))
from review_H1_complete_native_models_source_and_admission_local_CPU_once import eq,tensors
def save(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def write(p,s):
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();c=json.loads((R/'RECOVERY_EXISTING_FINAL_COMPLETE_COST_EXIT_ORIGINAL_HANDOFF_1603_BOUND_COLLECTION_ACTUAL.json').read_bytes());assert c['actual_closed'];ledger=c['account']['original_canonical'];seg=next(x for x in ledger['completed_segments'] if x.get('owner_parent_pid')==718138);assert set(seg['experts'])=={'recovery'} and abs(seg['charged_expert_seconds']-seg['experts']['recovery']['charged_seconds'])<1e-6 and seg['experts']['recovery']['duration_bound_passed'] and seg['experts']['recovery']['actual_returncode']==0
 row=next(x for x in c['downloaded_final_models']['recovery'] if x['kind']=='actual_complete_final');p=Path(row['local_path']);assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'] and row['twohost_complete_SHA'];s=torch.load(p,map_location='cpu',weights_only=False);counts=[0,0];tensors(s,counts);assert counts==[173,96] and row['updates']==85 and {int(x['step']) for x in s['optimizer_state_dict']['state'].values()}=={657660}
 src=K/'payload/recovery/job0/source/E0_full_source.pt';base=torch.load(src,map_location='cpu',weights_only=False);assert {int(x['step']) for x in base['optimizer_state_dict']['state'].values()}=={655960};changed={g:[n for n in s[g] if not eq(s[g][n],base[g][n])] for g in ('actor_state_dict','critic_state_dict')};assert len(changed['actor_state_dict'])==9 and len(changed['critic_state_dict'])==8
 finalproof=dict(epoch=time.time(),passed_full_model_CPU=True,complete_final=row,whole_tensor_counts=counts,all_model_runtime_finite=True,all17Adam_before=655960,all17Adam_after=657660,all_actor9_STD_critic8_actual_changes=changed,production_updates=85,production_controls=2040,production_envsteps=40800000,actual_old_owner_and_all_children_out=True,original_canonicalNone_two_real_fcntlFree=True,original_cost_once=seg,actual_cost_seconds=seg['charged_expert_seconds'],remaining_snapshot=ledger['remaining_training_seconds'],not_selfrescue_skill_qualification=True,no_first_native_or_old_complete_artifact_recollection=True)
 save(R/'RECOVERY_CLOSED85_COMPLETE_MODEL_CPU_COST_EXIT_ORIGINAL_HANDOFF_ACTUAL.json',finalproof)
 assert not Q.exists();Q.mkdir();prep=json.loads((K/'reports/RECOVERED_THREE_FINALS_FULL_CPU_AND_NEW_SAME_SCOPE_NATIVE_PAYLOADS_PREPARED_ACTUAL.json').read_bytes());specs=dict(prep['specs']);edits=[]
 for n in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','three_slot_resource_v1.py','owner_listener_ready_cpu_reviewed_v1.py'):
  raw=(K/n).read_text('utf8')
  if n=='three_slot_common_v1.py':
   assert raw.count("CAPS={'h1':3600,'e2':3600,'recovery':3600}")==1;raw=raw.replace("CAPS={'h1':3600,'e2':3600,'recovery':3600}","CAPS={'h1':1800,'e2':3600,'recovery':3600}")
  write(B/n,raw);ast.parse(raw)
 guard='''"""Only own H1 complete-update storage/time engineering bound; no learning input changes."""
import math
H1_MAX_COMPLETE_UPDATES=24
H1_EXIT_STORAGE_RESERVE_BYTES=8*1024**3
def should_save_stop(phase,completed,free_bytes):
 if phase not in ('production','precheck128','precheck20k') or not isinstance(completed,int) or completed<0 or not isinstance(free_bytes,(int,float)) or not math.isfinite(free_bytes) or free_bytes<0:raise ValueError('Unknown/invalid own finite storage state')
 return phase=='production' and (completed>=H1_MAX_COMPLETE_UPDATES or free_bytes<H1_EXIT_STORAGE_RESERVE_BYTES)
'''
 write(B/'own_H1_storage_finite_guard_v1.py',guard)
 tests={};ns={};exec(compile(guard,'own_H1_storage_guard','exec'),ns);fun=ns['should_save_stop']
 assert not fun('production',23,9*1024**3) and fun('production',24,9*1024**3) and fun('production',1,7*1024**3) and not fun('precheck20k',24,9*1024**3)
 rejected=0
 for args in [('unknown',1,1),('production',-1,1),('production',1,float('nan')),('production',1,-1),('production',1,float('inf')),('production',1,'unknown')]:
  try:fun(*args)
  except ValueError:rejected+=1
 assert rejected==6
 # Actual prior output measurement is only an engineering estimate, never a storage guarantee.
 free=c['source_current_storage']['D']['free'];estimate=24*int(.6*1024**3)+8*1024**3+1*1024**3+8*1024**3;assert estimate<free
 for key,prior in [('h1',F/'payload_v3/h1'),('recovery',K/'payload/recovery')]:
  dest=Q/key;assert prior.is_dir();shutil.copytree(prior,dest,ignore=shutil.ignore_patterns('THREE_SLOT_COMPLETE_MANIFEST_V1.json','__pycache__'))
  oldmanifest=json.loads((prior/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());shutil.copy2(prior/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',dest/'PREVIOUS_MANIFEST_EXACT_HISTORICAL.json');spec=dict(specs[key]);task=json.loads((dest/'job0/TASK.json').read_bytes());cap=1800 if key=='h1' else 3600
  if key=='h1':
   ck=dest/'job0/source'/spec['source_filename'];assert H(ck)==spec['source_SHA']=='3f7feb09c0034d0d902526c2f03a36e84db37d3d93b68b380a2ed844eb063a75';hs=torch.load(ck,map_location='cpu',weights_only=False);hc=[0,0];tensors(hs,hc);assert hc==[199,105] and {int(x['step']) for x in hs['optimizer_state_dict']['state'].values()}=={643700};count=hc
   worker=dest/'h1_prelaunch_v2_production_worker_v1.py';old=worker.read_text('utf8');new=old.replace("go['max_parent_seconds']==3600","go['max_parent_seconds']==1800");assert new!=old
   needle="   original_log(*aa,**kk);completed+=1;stop=";assert new.count(needle)==1;new=new.replace(needle,"   original_log(*aa,**kk);completed+=1;from own_H1_storage_finite_guard_v1 import should_save_stop\n   import shutil\n   own_storage_stop=should_save_stop(phase,completed,shutil.disk_usage(B).free)\n   if own_storage_stop:put(out/'OWN_STORAGE_OR_UPDATE_BOUND_SAVED_STOP_ACTUAL.json',dict(epoch=time.time(),completed=completed,free_bytes=shutil.disk_usage(B).free,max_completed_updates=24,reserve8GiB=True,no_reward_or_learning_input_change=True))\n   stop=own_storage_stop or ")
   worker.write_text(new,encoding='utf8');shutil.copy2(B/'own_H1_storage_finite_guard_v1.py',dest/'own_H1_storage_finite_guard_v1.py');edits.append(dict(key=key,file=worker.name,old_SHA=hashlib.sha256(old.encode()).hexdigest(),new_SHA=H(worker),only_new_grant_cap_and_complete_update_saved_stop_guard=True))
   task.update(max_parent_seconds=1800,exit_headroom_seconds=300,max_completed_updates=24,own_saved_stop_if_free_below8GiB=True,new_human_reconnected_followup_cap3600_including_production_loadlearnsaveexit=False,new_storage_bounded_H1_1800cap24updates=True)
  else:
   ck=dest/'job0/source'/spec['source_filename'];shutil.copy2(p,ck);count=counts;spec.update(source_SHA=row['SHA'],source_Adamstep=657660,source_schema_counts=counts,previous_runtime_root=c['recovery']['root'])
   for name in ('recovery_worker.py','native_CPU.py'):
    f=dest/name;old=f.read_text('utf8');assert '655960' in old;new=old.replace('655960','657660');f.write_text(new,encoding='utf8');edits.append(dict(key=key,file=name,old_SHA=hashlib.sha256(old.encode()).hexdigest(),new_SHA=H(f),only_exact_source_Adam_expectation_change=True))
   task.update(source_SHA=row['SHA'],source_Adamstep=657660,exact_closed_source_updates=85,native_only_frozen_source_review_no_new_production_GO=True)
  task.update(id='H1_STORAGE_BOUNDED_AND_RECOVERY_SOURCE85_NATIVE_ONLY_'+key.upper()+'_20261017',new_original_GO_required_no_permission_from_prepared_files=True,own_new_native_for_actual_new_weights_required=True,same_source_backend_native_reused_not_replayed=False)
  (dest/'job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8')
  for n in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','three_slot_resource_v1.py'):shutil.copy2(B/n,dest/n)
  files=[]
  for f in sorted(x for x in dest.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
   if f.suffix=='.py':ast.parse(f.read_text('utf8'))
   files.append(dict(relative=f.relative_to(dest).as_posix(),bytes=f.stat().st_size,SHA=H(f)))
  # All original runtime, lib and physical assets remain exact to the prior approved source.
  original_physics=[r for r in oldmanifest['files'] if r['relative'].startswith(('job0/runtime/','job0/assets/','lib/','job0/original_run_manifest.json'))]
  assert all(H(dest/r['relative'])==r['SHA'] for r in original_physics)
  mf=dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';manifest=dict(oldmanifest,key=key,source_SHA=spec['source_SHA'],source_filename=spec['source_filename'],source_Adamstep=spec['source_Adamstep'],source_schema_counts=count,files=files,explicit_new_contract_only_no_reward_command_DR_hardware_change=True)
  save(mf,manifest);spec.update(manifest_SHA=H(mf),max_parent_seconds=cap,exit_headroom_seconds=300);specs[key]=spec
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 proof=dict(epoch=time.time(),passed_CPU_only=True,recovery_closed_final=finalproof,specs=specs,H1_new_own_native180_required=True,recovery_new_source85_native336_only_zero_PPO_zero_charge=True,E2_behavior_hold_zero_worker_zero_GO=True,H1_new_cap1800_max24completeupdates_exitheadroom300=True,planned_paid_learning_cap_sum1800_only_not_new_budget=True,storage_estimate_bytes=estimate,actual_free_snapshot=free,storage_estimate_is_engineering_not_runtime_guarantee=True,original25GiB_start_guard_unchanged=True,added_H1_complete_update_saved_stop_reserve8GiB=True,storage_guard_positive_boundary_and6negative_CPU_passed=True,changes=edits,original_runtime_reward_command_physics_DR_hardware_AST_bytes_exact=True,CPU_RNG_unchanged0CUDA0optimizer=True,new_GPU_or_GO_not_yet=True)
 save(R/'CLOSED_RECOVERY85_FULL_CPU_H1_BOUNDED_RECOVERY_NATIVE_ONLY_PAYLOADS_PREPARED_ACTUAL.json',proof)
 print(json.dumps(dict(recovery_final_CPU=True,final_SHA=row['SHA'],updates=85,Adam=657660,actual_cost_seconds=seg['charged_expert_seconds'],H1_source_Adam=643700,H1_cap1800_updates24=True,recovery_next_native_only=True,storage_estimated=estimate,free=free,new_GPU_or_GO_not_yet=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('M_SOURCE_MODEL_PAYLOAD_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_remote_GPU_or_budget_change=True),f,indent=2)
  raise

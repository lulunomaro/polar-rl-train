"""Only actual complete prior finals can freeze the next independent source models."""
from pathlib import Path
import os,sys,time,json,hashlib,shutil,ast,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
U=Path(__file__).resolve().parent;W=U.parent;N=W/'MOD4_TWO72_E2_E3_HEALTHY_SAVED_CONTINUATIONS_20261017';R=U/'reports';Q=U/'payload'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def finite(x,c):
 if torch.is_tensor(x):c[0]+=1;c[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
 elif isinstance(x,dict):
  for z in x.values():finite(z,c)
 elif isinstance(x,(tuple,list)):
  for z in x:finite(z,c)
def main():
 v=json.loads((R/'EXISTING_N72_TWO_FINALS_ORIGINAL_CANONICAL_ACTUAL_HANDOFF_COLLECTION.json').read_bytes());assert v['both_current_N72_scopes_actual_closed_and_source_handoff'];cost=next(c for c in v['canonical']['selected_completed'] if c['owner_parent_pid']==594718);assert len(cost['experts'])==2 and all(z['duration_bound_passed'] for z in cost['experts'].values());assert abs(sum(z['charged_seconds'] for z in cost['experts'].values())-cost['charged_expert_seconds'])<1e-6;assert json.loads((R/'THREE_SLOT_RUNTIME_PROTOCOL_CPU_READINESS_COST_NEGATIVES_ACTUAL.json').read_bytes())['passed_CPU_protocol_only'];assert json.loads((R/'THREE_SLOT_FINAL_AUTH_NEGATIVES_AND_RUNTIME_CPU_V2_ACTUAL.json').read_bytes())['passed_CPU_only'];assert json.loads((R/'THREE_SLOT_LOCAL_HTTP_THREE_SIMULATED_NODES_HANDOFF_ISOLATION_CPU_V2_ACTUAL.json').read_bytes())['passed_local_HTTP_simulated_nodes'];assert not Q.exists();Q.mkdir();specs={};modelreports={};rng=torch.get_rng_state().clone()
 hproof=json.loads((N/'reports/H1_SOURCE210_NATIVE180_ALL_ROWS_TWO_COMPLETE_MODELS_LOCAL_CPU_VERIFIED_ACTUAL.json').read_bytes());assert hproof['passed'] and hproof['H1_PPO_updates0_new_canonical_charge0'];hcollect=json.loads((N/'reports/H1_SOURCE210_NATIVE_ONLY_EXISTING_CHAIN_BOUND_COLLECTION_ACTUAL.json').read_bytes());hCPU=next(r for r in hcollect['H1']['files'] if r['path'].endswith('/H1_PRELAUNCH_V2_NATIVE180_ALL_ROWS_CPU_ADMITTED.json'));hmanifest=N/'h1_closed25_source210_nativeonly_payload/H1_SOURCE210_NATIVE_ONLY_COMPLETE_MANIFEST.json'
 for key in ('h1','e2','recovery'):
  prior=N/('h1_closed25_source210_nativeonly_payload' if key=='h1' else 'v2_payload/'+key);b=Q/key;shutil.copytree(prior,b)
  if key=='h1':source=prior/'job0/source/H1_final10_protected.pt';sourcefile='H1_final10_protected.pt';row=dict(path=str(source),bytes=source.stat().st_size,SHA=H(source),updates=25);before=640260;expected_counts=[199,105];previous='/mnt/mod4_linux_durable_20261013/H125_1710n1';native_controls=180;cap=1800;gpu='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e';py='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
  else:
   row=v['downloaded_final_models'][key];source=Path(row['local_path']);assert row['twohost_complete_SHA'] and source.stat().st_size==row['bytes'] and H(source)==row['SHA'];sourcefile='E2_final58.pt' if key=='e2' else 'E0_full_source.pt';ck=torch.load(source,map_location='cpu',weights_only=False);before=next(iter({int(z['step']) for z in ck['optimizer_state_dict']['state'].values()}));expected_before=649400 if key=='e2' else 642040;assert {int(z['step']) for z in ck['optimizer_state_dict']['state'].values()}=={expected_before+20*row['updates']};expected_counts=[175,98] if key=='e2' else [173,96];previous='/home/lc01/Zonglin Li/zonglin2/tasks/N72_1710v2/'+key;native_controls=144 if key=='e2' else 336;cap=3600;gpu='GPU-16828f91-2b45-b646-8dc0-9481138e2842' if key=='e2' else 'GPU-c27eecbd-6838-7290-1cd2-37e34522213d';py='/home/lc01/Zonglin Li/zonglin2/run-python.sh';shutil.copy2(source,b/'job0/source'/sourcefile)
  ck=torch.load(source,map_location='cpu',weights_only=False);counts=[0,0];finite(ck,counts);assert counts==expected_counts and len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and len(ck['optimizer_state_dict']['state'])==17
  oldname='job0/TASK.json';shutil.copy2(b/oldname,b/'job0/HISTORICAL_INPUT_TASK_EXACT.json');task=json.loads((b/oldname).read_bytes());historical={k:task.pop(k) for k in ('template_approved_GPU','approved_for_PPO','native_only_no_PPO_or_canonical_write') if k in task};task.update(id='THREE_SLOT_'+key.upper()+'_EXACT_CLOSED_SOURCE_20261017',source_SHA=H(source),source_Adamstep=before,max_parent_seconds=cap,exit_headroom_seconds=300,exact_closed_source_updates=row['updates'],legacy_source_filename_history_not_model_identity=True,new_original_GO_required_no_permission_from_prepared_files=True,historical_input_preparation_flags_not_current_runtime_status=historical)
  if key=='h1':task.update(native_only_no_PPO_or_canonical_write=False,first_new_human_continue_bound1800_including_production_load_learn_save_exit=True,same_source_backend_native_reused_not_replayed=True)
  (b/oldname).write_text(json.dumps(task,indent=2),encoding='utf8');changes=[]
  edits=[('h1_prelaunch_v2_production_worker_v1.py','639760',str(before))] if key=='h1' else ([('production_worker.py','649400',str(before)),('native_admission_worker.py','649400',str(before))] if key=='e2' else [('recovery_worker.py','642040',str(before)),('native_CPU.py','642040',str(before))])
  for name,old,new in edits:
   p=b/name
   if key=='h1':shutil.copy2(W/'MOD4_H1_GROUNDED_PRELAUNCH_PROGRESS_V2_20261016/payload'/name,p)
   text=p.read_text('utf8');assert old in text;fixed=text.replace(old,new);p.write_text(fixed,encoding='utf8');changes.append(dict(relative=name,original_SHA=hashlib.sha256(text.encode()).hexdigest(),new_SHA=H(p),only_original_source_Adam_expectation_changed=True))
  for name in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','three_slot_resource_v1.py'):shutil.copy2(U/name,b/name)
  if key!='h1':shutil.copy2(N/'v2_payload'/key/'native_CPU_status_bridge_v1.py',b/'native_CPU_status_bridge_v1.py')
  mf=b/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';rows=[]
  for p in sorted(p for p in b.rglob('*') if p.is_file() and '__pycache__' not in p.parts):
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   rows.append(dict(relative=p.relative_to(b).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
  installed=json.loads((W/'MOD4_H1_GROUNDED_PRELAUNCH_PROGRESS_V2_20261016/payload/H1_GROUND_PRELAUNCH_V2_COMPLETE_MANIFEST.json').read_bytes())
  m=dict(key=key,source_SHA=H(source),source_filename=sourcefile,source_Adamstep=before,source_schema_counts=counts,files=rows,original_runtime_physics_reward_DR_and_hardware_bytes_unchanged=True,explicit_source_Adam_expectation_changes=changes,expected_actual_RSL_sources=[{k:r[k] for k in ('relative','bytes','SHA')} for r in installed['actual_RSL_sources']],expected_actual_SDK_math_SHA=installed['SDK_math_actual_SHA'])
  if key=='h1':m['H1_same_source_backend_native_reuse']=dict(previous_manifest_SHA=H(hmanifest),actual_native_CPU_report_SHA=hCPU['SHA'],same_source_SHA=H(source),source_native_counts180_720=True)
  mf.write_text(json.dumps(m,indent=2),encoding='utf8');specs[key]=dict(key=key,source_SHA=H(source),source_filename=sourcefile,source_Adamstep=before,source_schema_counts=counts,manifest_SHA=H(mf),native_controls=native_controls,max_parent_seconds=cap,exit_headroom_seconds=300,previous_runtime_root=previous,GPU_UUID=gpu,python=py,native_script=None if key=='h1' else ('native_admission_worker.py' if key=='e2' else 'recovery_worker.py'),production_script='h1_prelaunch_v2_production_worker_v1.py' if key=='h1' else ('production_worker.py' if key=='e2' else 'recovery_worker.py'))
  changed=None
  if key!='h1':
   ancestor=torch.load(prior/'job0/source'/sourcefile,map_location='cpu',weights_only=False);changed={group:[name for name in ck[group] if ck[group][name].contiguous().reshape(-1).view(torch.uint8).numpy().tobytes()!=ancestor[group][name].contiguous().reshape(-1).view(torch.uint8).numpy().tobytes()] for group in ('actor_state_dict','critic_state_dict')};assert changed['actor_state_dict'] and changed['critic_state_dict']
  modelreports[key]=dict(source_row=row,source_SHA=H(source),whole_model_counts=counts,all_finite=True,source_Adamstep=before,actual_actor_critic_changes_from_original_N72_source=changed,original_actor9STD_critic8_optimizer17_retained_not_initialized=True,production_envsteps_previous=480000*row['updates'],not_frozen_skill_qualification=True)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();out=dict(epoch=time.time(),passed_CPU_only=True,previous_N72_original_cost_once=cost,old_owner_and_children_actual_out_original_two_fcntl_free=True,source_models=modelreports,specs=specs,all_three_sources_not_native_or_PPO_pass_from_preparation=True,H1_same_source_backend_completed_native_reuse_required=True,new_E2_E3_source_own_native_required=True,only_Adam_expected_value_task_metadata_and_finite_pipeline_changed=True,actual_new_run_or_GO_not_dispatched=True);p=R/'THREE_SLOT_ACTUAL_CLOSED_SOURCES_FULL_CPU_FROZEN_PAYLOADS_PREPARED.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(dict(sources={k:dict(SHA=x['source_SHA'],Adam=x['source_Adamstep'],counts=x['whole_model_counts']) for k,x in modelreports.items()},old_actual_cost=cost['charged_expert_seconds'],new_PPO_or_GPU=False)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('THREE_SLOT_ACTUAL_SOURCE_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_budget_write=True),f,indent=2)
  raise

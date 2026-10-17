"""Freeze actual closed24, retain all physics, route the approved H1 slot to free72 GPU0."""
from pathlib import Path
import os,sys,json,time,hashlib,shutil,ast,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';R.mkdir(exist_ok=True);M=W/'MOD4_RECOVERY_CLOSED_FINAL_H1_STORAGE_BOUNDED_HANDOFF_20261017';Q=B/'payload'
sys.path.insert(0,str(W/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'))
from review_H1_complete_native_models_source_and_admission_local_CPU_once import eq,tensors
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def write(p,s):
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();v=json.loads((M/'reports/M_CLOSED24_H1_FINAL_RECOVERY85_NATIVE_COMPLETE_ORIGINAL_HANDOFF_1657_BOUND_ACTUAL.json').read_bytes());ledger=v['account']['original_canonical'];assert ledger['active_segment'] is None and all(x['actual_fcntl_free'] for x in v['account']['actual_locks']) and not any(v[k]['actual_own_processes'] for k in ('owner','h1','recovery'))
 seg=next(x for x in ledger['completed_segments'] if x.get('owner_parent_pid')==734415);assert set(seg['experts'])=={'h1'} and seg['experts']['h1']['actual_returncode']==0 and seg['experts']['h1']['duration_bound_passed']
 prior=json.loads((M/'reports/H1_BOUNDED_ONE_PAID_SLOT_RECOVERY_NATIVE_ONLY_OWNER_HTTP_CPU_ACTUAL.json').read_bytes());specs=prior['specs'];models={};cks={}
 for key,row in v['downloaded_models'].items():
  p=Path(row['local_path']);assert row['twohost_complete_SHA'] and p.stat().st_size==row['bytes'] and H(p)==row['SHA'];ck=torch.load(p,map_location='cpu',weights_only=False);counts=[0,0];tensors(ck,counts);cks[key]=ck;models[key]=dict(row,counts=counts)
 h=cks['h1_final'];hs=torch.load(M/'payload/h1/job0/source/H1_final10_protected.pt',map_location='cpu',weights_only=False);assert models['h1_final']['counts']==[199,105] and h['owned_H1_completed_updates']==24 and h['failed_partial_prefix'] is False and {int(z['step']) for z in h['optimizer_state_dict']['state'].values()}=={644180}
 changes={g:[k for k in hs[g] if not eq(hs[g][k],h[g][k])] for g in ('actor_state_dict','critic_state_dict')};assert len(changes['actor_state_dict'])==9 and len(changes['critic_state_dict'])==8
 rs=torch.load(M/'payload/recovery/job0/source/E0_full_source.pt',map_location='cpu',weights_only=False);rn=cks['recovery_native'];assert models['recovery_native']['counts']==[173,96] and {int(z['step']) for z in rn['optimizer_state_dict']['state'].values()}=={657660}
 for g in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(rs[g],rn[g])
 nr=next(x['value'] for x in v['recovery']['files'] if x['path'].endswith('/NATIVE_ONLY_FINAL_ACTUAL.json'));assert nr['passed_native_GPU_and_full_CPU'] and nr['no_production_GO_or_PPO_or_canonical_charge']
 closed=dict(epoch=time.time(),H1_full_final_CPU_passed=True,H1_final=models['h1_final'],all_model_runtime_finite=True,all17Adam643700_to644180=True,all17_actorcritic_changes=changes,H1_updates24_controls576_envsteps11520000=True,actual_original_cost_once=seg,actual_cost_seconds=seg['charged_expert_seconds'],actual_all_own_parents_children_out=True,original_canonicalNone_two_fcntlFree=True,recovery_native_complete_CPU_literalexact=models['recovery_native'],recovery_source85_Adam657660_unchanged_no_PPO=True,not_jump_or_recovery_skill_qualification=True,D_free_snapshot=v['source_resources']['durable_free'],single210_25GiB_admission_still_required=True)
 put('M_H1_CLOSED24_FULL_MODEL_CPU_RECOVERY_NATIVE_COMPLETE_ORIGINAL_HANDOFF_ACTUAL.json',closed)
 assert not Q.exists();Q.mkdir();dest=Q/'h1';shutil.copytree(M/'payload/h1',dest,ignore=shutil.ignore_patterns('THREE_SLOT_COMPLETE_MANIFEST_V1.json','__pycache__'))
 oldmf=json.loads((M/'payload/h1/THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());shutil.copy2(M/'payload/h1/THREE_SLOT_COMPLETE_MANIFEST_V1.json',dest/'PREVIOUS_SOURCE121_MANIFEST_HISTORICAL.json');src=dest/'job0/source/H1_final10_protected.pt';shutil.copy2(models['h1_final']['local_path'],src)
 edits=[]
 for name in ('h1_prelaunch_v2_production_worker_v1.py','review_H1_prelaunch_v2_native_allrows_CPU_v1.py'):
  p=dest/name;old=p.read_text('utf8');assert '643700' in old;new=old.replace('643700','644180');p.write_text(new,encoding='utf8');edits.append(dict(path=name,old_SHA=hashlib.sha256(old.encode()).hexdigest(),new_SHA=H(p),only_exact_source_Adam_expectation_and_report_label_change=True))
 gpu='GPU-16828f91-2b45-b646-8dc0-9481138e2842';common=(M/'three_slot_common_v1.py').read_text('utf8');assert common.count("'h1':'GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'")==1;common=common.replace("'h1':'GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'","'h1':'"+gpu+"'")
 write(B/'three_slot_common_v1.py',common)
 for n in ('three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','owner_listener_ready_cpu_reviewed_v1.py'):shutil.copy2(M/n,B/n)
 # The target owns GPU0's existing private lock and verifies the last same-GPU E2 parent exited.
 resource=(M/'three_slot_resource_v1.py').read_text('utf8');assert "source=key=='h1'" in resource;resource=resource.replace("source=key=='h1'","source=spec.get('execution_backend')=='source210'");write(B/'three_slot_resource_v1.py',resource)
 for n in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','three_slot_resource_v1.py'):shutil.copy2(B/n,dest/n)
 task=json.loads((dest/'job0/TASK.json').read_bytes());task.update(id='H1_CLOSED24_TARGET72_NEW_BACKEND_SAME_SCOPE_20261017',source_SHA=models['h1_final']['SHA'],source_Adamstep=644180,source_owned_completed_updates=24,source_parent_production_root=v['h1']['root'],execution_backend='target72',new_target_native180_and_full_CPU_required=True,max_parent_seconds=1800,exit_headroom_seconds=300,max_completed_updates=24,own_saved_stop_if_free_below8GiB=True,no_reward_command_LR_STD_physical_guard_change=True);(dest/'job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8')
 files=[]
 for p in sorted(x for x in dest.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.py':ast.parse(p.read_text('utf8'))
  files.append(dict(relative=p.relative_to(dest).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
 immutable=[x for x in oldmf['files'] if x['relative'].startswith(('job0/runtime/','job0/assets/','lib/','job0/original_run_manifest.json'))];assert all(H(dest/x['relative'])==x['SHA'] for x in immutable)
 mf=dict(oldmf,source_SHA=models['h1_final']['SHA'],source_Adamstep=644180,files=files,execution_backend='target72',source_owned_completed_updates24=True,same_scope_physics_reward_command_DR_hardware_exact=True);(dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(mf,indent=2),encoding='utf8')
 specs['h1'].update(source_SHA=models['h1_final']['SHA'],source_Adamstep=644180,manifest_SHA=H(dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),GPU_UUID=gpu,python=specs['recovery']['python'],execution_backend='target72',previous_runtime_root='/home/lc01/Zonglin Li/zonglin2/tasks/T3_1710v8r72/e2')
 # CPU exercise the actual payload validator and six wrong-slot/source/UUID/cap contracts.
 mod={};exec(compile(common,str(B/'three_slot_common_v1.py'),'exec'),dict(__file__=str(dest/'three_slot_common_v1.py')),mod)
 import importlib.util
 sp=importlib.util.spec_from_file_location('H1_target72_common_CPU_actual',dest/'three_slot_common_v1.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b);b.validate_payload(specs['h1']);rejected=0
 for change in ({'GPU_UUID':'GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'},{'GPU_UUID':specs['recovery']['GPU_UUID']},{'max_parent_seconds':3600},{'exit_headroom_seconds':0},{'manifest_SHA':'0'*64},{'key':'unknown'}):
  try:b.validate_payload(dict(specs['h1'],**change))
  except (AssertionError,KeyError):rejected+=1
 assert rejected==6 and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 put('H1_CLOSED24_TARGET72_SAME_SCOPE_PAYLOAD_FULL_CPU_PREPARED_ACTUAL.json',dict(epoch=time.time(),passed_CPU_only=True,closed_final_proof=closed,specs=specs,changes=edits,target72_h1_GPU0_new_backend_native180_required_not_reused=True,H1_original_1800cap24updates300headroom8GiB_exit_reserve_25GiB_start_guard_unchanged=True,all_runtime_lib_physics_reward_command_DR_bytes_exact=True,actual_common_manifest_validator_positive_and6negative_passed=True,E2_and_recovery_paid_hold_no_worker_GO=True,one_original_writer_original_budget_unchanged=True,new_native_GPU_PPO_not_yet=True))
 print(json.dumps(dict(H1_final_CPU=True,H1_final_step=644180,H1_cost_once=seg['charged_expert_seconds'],D_free=v['source_resources']['durable_free'],target72_payload_CPU=True,H1_next_GPU=gpu,new_native_required=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('H1_TARGET72_PAYLOAD_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_remote_or_GPU_launch=True));raise

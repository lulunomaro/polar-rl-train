"""Require own new native closure and exact local models before new finite GO payload."""
from pathlib import Path
import sys,os,time,json,shutil,hashlib,copy,types,importlib.util,ast,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;R=B/'reports';P=B/'paid_mean_v1';Q=P/'payload/h1';X=B.parent/'MOD4_H1_FROZEN_FE1709_REVIEW_20261018';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):
 with (P/'reports'/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 assert not Q.exists();P.mkdir();(P/'reports').mkdir();torch.set_num_threads(2);rng=torch.get_rng_state().clone()
 proof=json.loads((R/'NEW_B326_MEAN_NATIVE180_TWO_COMPLETE_MODELS_SOURCE_EXACT_LOCAL_CPU_ACTUAL.json').read_bytes());assert proof['passed_complete_native180_allrow_remote_and_full_model_local_CPU']
 collection=json.loads((R/'B326_MEAN_NATIVE_COMPLETE_TERMINAL_METADATA_MERGED_V2_COLLECTION_ACTUAL.json').read_bytes());rows=collection['rows'];oldQ=B/'payload_h1_native';oldm=json.loads((oldQ/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
 shutil.copytree(oldQ,Q,ignore=shutil.ignore_patterns('__pycache__','THREE_SLOT_COMPLETE_MANIFEST_V1.json'));shutil.copy2(oldQ/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',Q/'OWN_B326_MEAN_NATIVE_MANIFEST_HISTORICAL.json')
 for n in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','three_slot_resource_v1.py','owner_listener_ready_cpu_reviewed_v1.py'):
  src=X/'paid_d723_v4'/n;shutil.copy2(src,P/n)
  if n!='owner_listener_ready_cpu_reviewed_v1.py':shutil.copy2(src,Q/n)
 validator=(X/'paid_d723_v4/h1_same_source_native_reuse_v1.py').read_text('utf8').replace('645140','645620');(P/'h1_same_source_native_reuse_v1.py').write_text(validator,encoding='utf8');(Q/'h1_same_source_native_reuse_v1.py').write_text(validator,encoding='utf8')
 taskp=Q/'job0/TASK.json';task=json.loads(taskp.read_bytes());task.update(id='H1_B326_MEAN_OVERFLOW_REPAIR_FINITE_20261018',native_only_no_production_GO_or_canonical=False,native_only_no_PPO_or_canonical_write=False,newsource_native180_required=False,same_source_backend_native_reused_not_replayed=True,new_original_GO_required_no_permission_from_prepared_files=True,max_parent_seconds=1800,max_completed_updates=24,exit_headroom_seconds=300,human_requested_resume_and_fix_existing_H1_axis=True);taskp.write_text(json.dumps(task,indent=2),encoding='utf8')
 prod=Q/'h1_prelaunch_v2_production_worker_v1.py';code=prod.read_text('utf8');marker="  assert int(env._sim_step_counter)==0";assert code.count(marker)==1;code=code.replace(marker,"  assert runner.alg.__class__.__module__=='owned_h1_mean_overflow_ppo_v1';from h1_action_mean_overflow_loss_v1 import COEFFICIENT,ACTION_BOUND;assert COEFFICIENT==.001 and ACTION_BOUND==6.\n"+marker);code=code.replace('environment_reward_STD_LR_and_physics_unchanged=True','environment_reward_STD_load_keep_learning_contract_LR_and_physics_unchanged=True');prod.write_text(code,encoding='utf8')
 binding=dict(root='/home/lc01/Zonglin Li/zonglin2/tasks/H1mb_1810n1',manifest_SHA=H(oldQ/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_SHA=proof['source_SHA'],GPU_UUID=task['GPU_UUID'],native_CPU_SHA=rows['NATIVE_ONLY_FINAL_ACTUAL.json']['native_CPU']['SHA'])
 files=[]
 for p in sorted(x for x in Q.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.py':ast.parse(p.read_text('utf8'))
  files.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
 mf=dict(oldm,files=files,H1_same_source_backend_native_reuse=binding,native_only_no_PPO_or_canonical_permission=False,new_original_owner_GO_required=True);(Q/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(mf,indent=2),encoding='utf8')
 specs=json.loads((X/'paid_d723_v4/reports/PARALLEL_D723_H1_FINITE_SAME_SOURCE_NATIVE_REUSE_PAYLOAD_CPU_ACTUAL.json').read_bytes())['specs'];specs['h1'].update(source_SHA=proof['source_SHA'],source_Adamstep=645620,manifest_SHA=H(Q/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),previous_runtime_root='/home/lc01/Zonglin Li/zonglin2/tasks/H1r_1810v4',role='node',execution_backend='target72')
 fcntl=types.ModuleType('fcntl');fcntl.flock=lambda *a:(_ for _ in ()).throw(AssertionError('No real OS flock in CPU'));sys.modules['fcntl']=fcntl;sp=importlib.util.spec_from_file_location('common_payload_CPU_only',Q/'three_slot_common_v1.py');common=importlib.util.module_from_spec(sp);sp.loader.exec_module(common);common.validate_payload(specs['h1'])
 ns={};exec(compile(validator,str(P/'h1_same_source_native_reuse_v1.py'),'exec'),ns);args=[specs['h1'],binding,oldm,mf,rows['NATIVE_ONLY_FINAL_ACTUAL.json'],rows['NATIVE_ONLY_PARENT_EXIT_ACTUAL.json'],rows['job0/native_CPU_WAITED_EXIT_ACTUAL.json'],rows['job0/native_WAITED_EXIT_ACTUAL.json']];native=ns['validate'](*args)
 ready=dict(key='h1',phase='ready',native_GPU_waited_EXIT0=True,native_CPU=native,manifest_SHA=specs['h1']['manifest_SHA'],original_error=False);assert common.valid_ready(ready,specs['h1'])
 negatives=[]
 for label,index,change in [('wrong_backend',0,lambda a:a.__setitem__('execution_backend','source210')),('wrong_GPU',0,lambda a:a.__setitem__('GPU_UUID','unknown')),('wrong_source',0,lambda a:a.__setitem__('source_SHA','0'*64)),('wrong_Adam',0,lambda a:a.__setitem__('source_Adamstep',645140)),('wrong_optimization_runtime',3,lambda a:next(r for r in a['files'] if r['relative'].endswith('/owned_h1_mean_overflow_ppo_v1.py')).__setitem__('SHA','0'*64)),('GPU_final_failed',4,lambda a:a.__setitem__('passed_native_GPU_and_full_CPU',False)),('CPU_hash_wrong',1,lambda a:a.__setitem__('native_CPU_SHA','0'*64)),('parent_not_waited',5,lambda a:a.__setitem__('all_actual_own_GPU_children_waited',False)),('original_error',5,lambda a:a.__setitem__('original_error',True)),('CPU_nonzero_exit',6,lambda a:a.__setitem__('returncode',1)),('GPU_nonzero_exit',7,lambda a:a.__setitem__('returncode',1))]:
  bad=copy.deepcopy(args);change(bad[index])
  try:ns['validate'](*bad)
  except AssertionError:negatives.append(label)
  else:raise AssertionError(label)
 assert len(negatives)==11 and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 save('MEAN_REPAIR_H1_FINITE_PAYLOAD_CPU_ACTUAL.json',dict(epoch=time.time(),passed_CPU_only=True,specs=specs,source=proof,explicit_owned_PPO_loss_candidate=task['optimization_candidate'],reuse_binding=binding,reuse_pure_validator_positive_and11negative=negatives,all_original_environment_reward_physics_DR_commands_hardware_bytes_exact=True,original_actor9STDcritic8_optimizer17_initial_exact=True,no_STD_reset_or_LR_change_or_extra_optimizer=True,source_Adam645620=True,new_cap1800_headroom300_updates24_free8GiB_25GiB_start_guard=True,actual_prior_native_local_full_models_and_remote_allrow_CPU_passed=True,E2_E3_hold_no_worker_or_GO=True,human_restored_resume_fix_H1_same_subject=True,new_original_GO_required_not_already_learning=True))
 s=(X/'paid_d723_v4/deploy_parallel_d723_H1_new_finite_strict_native_reuse_once.py').read_text('utf8');s=s.replace('H1r_1810v4','H1mb_1810p1').replace("old=owned/'H1r_1710v3/owner'","old=owned/'H1r_1810v4/owner'").replace('PARALLEL_D723_H1_FINITE_SAME_SOURCE_NATIVE_REUSE_PAYLOAD_CPU_ACTUAL.json','MEAN_REPAIR_H1_FINITE_PAYLOAD_CPU_ACTUAL.json').replace('645140','645620').replace('PARALLEL_D723','MEAN_REPAIR')
 marker="owned=Path('/mnt/mod4_linux_durable_20261013');old=";assert s.count(marker)==1;s=s.replace(marker,"owned=Path('/mnt/mod4_linux_durable_20261013');assert os.path.ismount(owned), 'Original authorized D must actually be mounted before metadata owner';old=")
 (P/'deploy_mean_repair_H1_original_finite1800_once.py').write_text(s,encoding='utf8')
 print(json.dumps(dict(paid_payload_CPU=True,own_native180_reused_only_after_real_pass=True,source_Adam=645620,negative_cases=len(negatives),not_dispatched_yet=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  P.mkdir(exist_ok=True);(P/'reports').mkdir(exist_ok=True);save('MEAN_REPAIR_PAID_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_paid_or_GPU_replay=True));raise

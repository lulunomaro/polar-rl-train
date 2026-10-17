"""New human-requested finite H1 continuation; exact existing same-backend native, no replay."""
from pathlib import Path
import os,sys,json,time,hashlib,shutil,ast,copy,types,importlib.util,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;W=B.parent.parent;R=B/'reports';R.mkdir(exist_ok=True)
A=B.parent;O=W/'MOD4_H1_CLOSED24_TARGET72_SAME_SCOPE_FINITE_20261017';Q=B/'payload/h1'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
def write(path,text):
 with path.open('x',encoding='utf8',newline='\n') as f:f.write(text)
VALIDATOR='''"""Strict same-source/backend reuse; actual runtime checks surround this pure validator."""
from pathlib import Path
import json,hashlib,os,psutil,subprocess
def validate(spec,bind,oldm,newm,final,exitrow,cpuwait,gpuwait):
 assert spec['key']=='h1' and spec['execution_backend']=='target72' and spec['GPU_UUID']==bind['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
 assert spec['source_SHA']==bind['source_SHA']==oldm['source_SHA']==newm['source_SHA'] and spec['source_Adamstep']==oldm['source_Adamstep']==newm['source_Adamstep']==645140
 assert oldm['key']==newm['key']=='h1' and spec['native_controls']==180
 assert final['passed_native_GPU_and_full_CPU'] and final['actual_GPU_worker_EXIT0'] and final['source_SHA']==spec['source_SHA'] and final['no_production_GO_or_PPO_or_canonical_charge']
 assert exitrow['all_actual_own_GPU_children_waited'] and exitrow['private_GPU_fcntl_released_if_acquired'] and exitrow['passed_native_CPU'] and not exitrow['original_error']
 assert cpuwait['returncode']==gpuwait['returncode']==0 and cpuwait['actual_waited'] and gpuwait['actual_waited']
 native=final['native_CPU'];v=native['value'];assert native['actual_CPU_waited_EXIT0'] and native['SHA']==bind['native_CPU_SHA']==hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest()
 assert v['passed'] and v['source_SHA']==spec['source_SHA'] and v['controls']==180 and v['callbacks']==720 and v['all_policy_rows']==3600000 and v['all_physical_rows']==14400000
 assert v['all17Adam_step645140'] and v['sourceactor9critic8STD17Adam_literal_exact'] and v['complete_original20k_typed_source_restore_actual']
 def fixed(m):return {r['relative']:r['SHA'] for r in m['files'] if r['relative'].startswith(('job0/runtime/','job0/assets/','lib/')) or r['relative']=='job0/original_run_manifest.json'}
 assert fixed(oldm)==fixed(newm) and fixed(oldm)
 return native
def reuse_H1_native(spec,b,B):
 m=b.read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');bind=m['H1_same_source_backend_native_reuse'];old=Path(bind['root']);owned=Path('/home/lc01/Zonglin Li/zonglin2')
 assert old.resolve().is_relative_to(owned.resolve()) and B.resolve().is_relative_to(owned.resolve()) and old!=B
 oldpath=old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';assert b.H(oldpath)==bind['manifest_SHA'];oldm=b.read(oldpath)
 final=b.read(old/'NATIVE_ONLY_FINAL_ACTUAL.json');native=validate(spec,bind,oldm,m,final,b.read(old/'NATIVE_ONLY_PARENT_EXIT_ACTUAL.json'),b.read(old/'job0/native_CPU_WAITED_EXIT_ACTUAL.json'),b.read(old/'job0/native_WAITED_EXIT_ACTUAL.json'))
 identity=b.read(old/'NATIVE_ONLY_PARENT_IDENTITY.json')
 if psutil.pid_exists(identity['pid']):
  p=psutil.Process(identity['pid']);assert abs(p.create_time()-identity['creation'])>.01 or p.status()==psutil.STATUS_ZOMBIE
 alive=[]
 for p in psutil.process_iter(['pid','cmdline','create_time']):
  try:
   if p.pid!=os.getpid() and any(s.startswith(str(old)+'/') for s in p.info['cmdline'] or []):alive.append(p.info)
  except psutil.Error:pass
 assert not alive,alive
 for row in oldm['files']:
  if row['relative'].startswith(('job0/runtime/','job0/assets/','lib/')) or row['relative']=='job0/original_run_manifest.json':assert b.H(old/row['relative'])==b.H(B/row['relative'])==row['SHA']
 assert b.H(B/'job0/source/H1_final10_protected.pt')==b.H(old/'job0/source/H1_final10_protected.pt')==spec['source_SHA']
 assert b.H(native['path'])==native['SHA'];pt=Path(native['value']['native_checkpoint']['path']);assert pt.resolve().is_relative_to(old.resolve()) and pt.stat().st_size==native['value']['native_checkpoint']['bytes'] and b.H(pt)==native['value']['native_checkpoint']['SHA']
 compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert not any(spec['GPU_UUID'] in s for s in compute.splitlines()),compute
 b.put(B/'STRICT_EXISTING_H1_NATIVE_REUSE_ACTUAL.json',dict(epoch=__import__('time').time(),source_SHA=spec['source_SHA'],source_Adam645140=True,exact_backend_GPU=spec['GPU_UUID'],native_CPU_SHA=native['SHA'],old_native_parent_children_actual_out=True,source_runtime_assets_and_installed_CPU_manifest_bound=True,no_GPU_native_replay_or_old_raw_download=True,not_jump_skill_qualification=True))
 return dict(native,strict_same_source_backend_reuse=True)
'''
def main():
 assert not Q.exists();torch.set_num_threads(2);rng=torch.get_rng_state().clone()
 closed=json.loads((W/'MOD4_H1_HUMAN_REQUESTED_SAME_SCOPE_RESTART_20261017/reports/HUMAN_REQUESTED_H1_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json').read_bytes());proof=json.loads((A/'reports/NEW_D723_NATIVE180_TWO_COMPLETE_MODELS_SOURCE_EXACT_LOCAL_CPU_ACTUAL.json').read_bytes())
 assert closed['passed_whole_final_model_local_CPU'] and closed['actual_duration_bound_passed'] and closed['actual_original_owner_node_all_children_out'] and proof['passed_complete_native180_allrow_remote_and_full_model_local_CPU']
 current=json.loads((A/'reports/NEW_D723_NATIVE_EXISTING_TERMINAL_COMPLETE_MODELS_BOUND_COLLECTION_ACTUAL.json').read_bytes());rows=current['rows'];oldQ=A/'payload_h1_native';oldm=json.loads((oldQ/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
 shutil.copytree(oldQ,Q,ignore=shutil.ignore_patterns('__pycache__','THREE_SLOT_COMPLETE_MANIFEST_V1.json'))
 shutil.copy2(oldQ/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',Q/'PREVIOUS_NATIVE_ONLY_COMPLETE_MANIFEST_HISTORICAL.json')
 src=Q/'job0/source/H1_final10_protected.pt';assert H(src)==proof['source_SHA']==closed['complete_final']['SHA']
 c=torch.load(src,map_location='cpu',weights_only=False);assert c['owned_H1_completed_updates']==24 and {int(x['step']) for x in c['optimizer_state_dict']['state'].values()}=={645140}
 for n in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','owner_listener_ready_cpu_reviewed_v1.py'):shutil.copy2(O/n,B/n)
 shutil.copy2(oldQ/'three_slot_resource_v1.py',B/'three_slot_resource_v1.py')
 write(B/'h1_same_source_native_reuse_v1.py',VALIDATOR)
 node=(oldQ/'three_slot_finite_node_v1.py').read_text('utf8');needle="p=b.spawn(spec,'native');children.append(p);phase='native'";assert node.count(needle)==0 and node.count("native=reuse_H1_native(spec,b,B);phase='ready'")==1
 node=node.replace(needle,"from h1_same_source_native_reuse_v1 import reuse_H1_native;native=reuse_H1_native(spec,b,B);phase='ready'")
 write(B/'three_slot_finite_node_v1.py',node)
 for n in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','three_slot_resource_v1.py','h1_same_source_native_reuse_v1.py'):shutil.copy2(B/n,Q/n)
 taskp=Q/'job0/TASK.json';task=json.loads(taskp.read_bytes());write(Q/'job0/PREVIOUS_NATIVE_ONLY_TASK_HISTORICAL.json',json.dumps(task,indent=2));task.update(id='H1_HUMAN_REQUESTED_CLOSED24_ADAM645140_CONTINUATION_20261017',GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',source_SHA=proof['source_SHA'],source_Adamstep=645140,source_owned_completed_updates=24,exact_closed_source_updates=24,source_H1_actual_latest_completed_updates=24,source_H1_actual_latest_Adamstep=645140,native_only_no_PPO_or_canonical_write=False,native_only_no_production_GO_or_canonical=False,same_source_backend_native_reused_not_replayed=True,new_original_GO_required_no_permission_from_prepared_files=True,human_explicit_start_training_this_turn=True,max_parent_seconds=1800,max_completed_updates=24,exit_headroom_seconds=300)
 taskp.write_text(json.dumps(task,indent=2),encoding='utf8')
 binding=dict(root='/home/lc01/Zonglin Li/zonglin2/tasks/H1n_1810v4',manifest_SHA=H(oldQ/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_SHA=proof['source_SHA'],GPU_UUID=task['GPU_UUID'],native_CPU_SHA=rows['NATIVE_ONLY_FINAL_ACTUAL.json']['native_CPU']['SHA'])
 files=[]
 for p in sorted(x for x in Q.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.py':ast.parse(p.read_text('utf8'))
  files.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
 mf=dict(oldm,files=files,H1_same_source_backend_native_reuse=binding,human_requested_new_finite_continuation_not_old_grant_extension=True)
 write(Q/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',json.dumps(mf,indent=2))
 specs=json.loads((O/'reports/H1_CLOSED24_TARGET72_SAME_SCOPE_PAYLOAD_FULL_CPU_PREPARED_ACTUAL.json').read_bytes())['specs']
 specs['h1'].update(previous_runtime_root='/home/lc01/Zonglin Li/zonglin2/tasks/H1r_1710v3',source_SHA=proof['source_SHA'],source_Adamstep=645140,manifest_SHA=H(Q/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),role='node',execution_backend='target72')
 mock=types.ModuleType('fcntl');mock.flock=lambda *a:(_ for _ in ()).throw(AssertionError('No OS flock in CPU fixtures'));sys.modules['fcntl']=mock
 sp=importlib.util.spec_from_file_location('new_H1_common_CPU_validator_only',Q/'three_slot_common_v1.py');common=importlib.util.module_from_spec(sp);sp.loader.exec_module(common);common.validate_payload(specs['h1'])
 # Execute the exact new pure reuse validator on actual prior source evidence.
 ns={};exec(compile(VALIDATOR,str(B/'h1_same_source_native_reuse_v1.py'),'exec'),ns)
 args=[specs['h1'],binding,oldm,mf,rows['NATIVE_ONLY_FINAL_ACTUAL.json'],rows['NATIVE_ONLY_PARENT_EXIT_ACTUAL.json'],rows['job0/native_CPU_WAITED_EXIT_ACTUAL.json'],rows['job0/native_WAITED_EXIT_ACTUAL.json']]
 native=ns['validate'](*args);ready=dict(key='h1',phase='ready',native_GPU_waited_EXIT0=True,native_CPU=native,manifest_SHA=specs['h1']['manifest_SHA'],original_error=False);assert common.valid_ready(ready,specs['h1'])
 negatives=[]
 for label,index,change in [('wrong_backend',0,lambda a:a.__setitem__('execution_backend','source210')),('wrong_GPU',0,lambda a:a.__setitem__('GPU_UUID','unknown')),('wrong_source',0,lambda a:a.__setitem__('source_SHA','0'*64)),('wrong_Adam',0,lambda a:a.__setitem__('source_Adamstep',644180)),('wrong_runtime',3,lambda a:next(r for r in a['files'] if r['relative'].startswith('job0/runtime/')).__setitem__('SHA','0'*64)),('GPU_final_failed',4,lambda a:a.__setitem__('passed_native_GPU_and_full_CPU',False)),('CPU_hash_wrong',1,lambda a:a.__setitem__('native_CPU_SHA','0'*64)),('parent_not_waited',5,lambda a:a.__setitem__('all_actual_own_GPU_children_waited',False)),('original_error',5,lambda a:a.__setitem__('original_error',True)),('CPU_nonzero_exit',6,lambda a:a.__setitem__('returncode',1)),('GPU_nonzero_exit',7,lambda a:a.__setitem__('returncode',1))]:
  bad=copy.deepcopy(args);change(bad[index])
  try:ns['validate'](*bad)
  except AssertionError:negatives.append(label)
  else:raise AssertionError('Bad reuse accepted: '+label)
 assert len(negatives)==11 and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 put('PARALLEL_D723_H1_FINITE_SAME_SOURCE_NATIVE_REUSE_PAYLOAD_CPU_ACTUAL.json',dict(epoch=time.time(),passed_CPU_only=True,specs=specs,source=closed['complete_final'],source_Adam645140=True,new_cap1800_headroom300_updates24_free8GiB_25GiB_start_guard=True,actual_prior_native_local_full_models_and_remote_allrow_CPU_passed=True,reuse_binding=binding,reuse_pure_validator_positive_and11negative=negatives,unchanged_original_owner_caps_charge_code_and_controller=True,new_node_only_strict_ready_native_reuse_no_GPU_replay=True,all_original_physics_reward_commands_DR_hardware_runtime_assets_bytes_exact=True,CPU_fixture_not_real_OS_GPU=True,human_this_turn_requested_training_new_original_finite_grant_required=True,E2_E3_hold_no_worker_or_GO=True,new_GPU_PPO_not_yet=True))
 print(json.dumps(dict(new_H1_CPU_payload=True,source_Adam=645140,reused_native_no_replay=True,negative_cases=11,new_paid_dispatch_not_yet=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('PARALLEL_D723_H1_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_SSH_GPU_or_PPO=True));raise

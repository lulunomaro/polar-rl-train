"""Tiny synthetic CPU and saved JSON/source only; every torch.load is forbidden."""
from pathlib import Path
import ast
from copy import deepcopy
import hashlib
import importlib.util
import io
import json
import os
import sys
import time
import traceback
from unittest import mock
os.environ['CUDA_VISIBLE_DEVICES']=''
D=Path(__file__).resolve().parent;T=D.parent.parent
sys.path.insert(0,str(D/'source'))
import normal86_source_guard_v1 as g
import torch
torch.set_num_threads(1)


def main():
 cases=[];synthetic_receipts=[]
 def case(name,fn,reject=False):
  try:
   fn()
   if reject:raise AssertionError('Negative fixture unexpectedly admitted')
   cases.append(dict(name=name,passed=True,expected_rejection=False))
  except Exception as error:
   if reject and str(error)!='Negative fixture unexpectedly admitted':
    cases.append(dict(name=name,passed=True,expected_rejection=True,exception_type=type(error).__name__,original_error=str(error)))
   else:cases.append(dict(name=name,passed=False,expected_rejection=reject,exception_type=type(error).__name__,original_error=str(error),traceback=traceback.format_exc()))
 def forbidden_load(*a,**k):raise AssertionError('Synthetic test forbids torch.load')
 torch.load=forbidden_load
 for key in ('h1','recovery'):
  B=D/'candidate_overlays'/key;pin=g.SOURCES[key]
  contract=g.read(B/'NORMAL86_SOURCE_CONTRACT_ACTUAL.json');old=g.read(B/'NORMAL86_ORIGINAL_COMPLETE_MANIFEST.json')
  binding,data=g.read_bound_metadata(B)
  case(key+'_typed_individual_origin_and_independent_current85_closure',lambda binding=binding,data=data:g.validate_origin(binding,data))
  bad=deepcopy(data);bad['latest_cpu']['models']['h1']={}
  case(key+'_reject_fabricated_latest_three_normal_models',lambda bad=bad,binding=binding:g.validate_origin(binding,bad),True)
  bad=deepcopy(data);bad['latest_collector']['authority72']['original_locks'][0]['actual_fcntl_free']=False
  case(key+'_reject_latest72_closure_incomplete',lambda bad=bad,binding=binding:g.validate_origin(binding,bad),True)
  bad=deepcopy(data);bad['source_cpu']['models'][key]['Adam']+=20
  case(key+'_reject_wrong_origin_Adam',lambda bad=bad,binding=binding:g.validate_origin(binding,bad),True)
  spec=dict(key=key,normal86_continuation=True,source_SHA=pin['SHA'],source_Adamstep=pin['Adam'],
    GPU_UUID=pin['GPU'],execution_backend=pin['backend'],policy_hz=pin['hz'],source_policy_hz=pin['hz'],
    manifest_SHA='f'*64,normal_source_contract_SHA='e'*64,closed_production_continuation=True)
  case(key+'_normal_identity_positive',lambda spec=spec:g.identity(spec))
  for name,value in (('source_SHA','94e7f272176b4a7c485b50c1ac61f95a3ecd4460ee6a73034f9e7a47a57045af'),('source_Adamstep',pin['Adam']+20),('native_continuation',True),('key','e2')):
   wrong=dict(spec);wrong[name]=value
   case(key+'_reject_identity_'+name,lambda wrong=wrong:g.identity(wrong),True)
  rows=g.index(deepcopy(old['files']));rows.update(g.index(deepcopy(contract['overlay_files'])))
  source='job0/source/'+contract['source_filename'];rows[source]=dict(relative=source,bytes=pin['bytes'],SHA=pin['SHA'])
  rows['NORMAL86_SOURCE_CONTRACT_ACTUAL.json']=dict(relative='NORMAL86_SOURCE_CONTRACT_ACTUAL.json',bytes=(B/'NORMAL86_SOURCE_CONTRACT_ACTUAL.json').stat().st_size,SHA=g.H(B/'NORMAL86_SOURCE_CONTRACT_ACTUAL.json'))
  m=dict(old,source_filename=contract['source_filename'],source_SHA=pin['SHA'],source_Adamstep=pin['Adam'],files=list(rows.values()))
  case(key+'_exact_inventory_new_PT_pin_keeps_old_PT_metadata_only',lambda m=m,old=old,contract=contract:g.validate_inventory(m,old,contract))
  wrong=deepcopy(m);wrong['files'].append(dict(relative='source/unapproved.py',bytes=0,SHA='0'*64))
  case(key+'_reject_extra_python',lambda wrong=wrong,old=old,contract=contract:g.validate_inventory(wrong,old,contract),True)
  wrong=deepcopy(m);next(row for row in wrong['files'] if row['relative']=='job0/assets/robot.usd')['SHA']='0'*64
  case(key+'_reject_physical_asset_change',lambda wrong=wrong,old=old,contract=contract:g.validate_inventory(wrong,old,contract),True)
  worker='h1_step270_production_worker_v1.py' if key=='h1' else 'recovery_worker.py'
  before=bytes.fromhex(contract['original_worker_utf8_hex']).decode('utf8');after=(B/worker).read_text('utf8')
  case(key+'_exact_worker_delta_normalized_AST',lambda before=before,after=after,key=key:g.exact_worker_delta(before,after,key))
  case(key+'_worker_extra_reward_or_input_change_rejected',lambda before=before,after=after,key=key:g.exact_worker_delta(before,after+'\nUNAPPROVED_CHANGE=True\n',key),True)
  base=T/('H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026' if key=='h1' else 'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026')/'payloads'/key
  role='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py'
  def prefix_check(base=base,B=B,contract=contract,role=role):
   before=(base/role).read_bytes();after=(B/role).read_bytes();assert after.startswith(before)
   before=(base/contract['original_CPU_script']).read_bytes();after=(B/contract['new_CPU_script']).read_bytes();assert after.startswith(before)
   a,b=ast.parse(before),ast.parse(after)
   assert [ast.dump(n) for n in b.body[:len(a.body)]]==[ast.dump(n) for n in a.body]
   assert not any(isinstance(n,ast.ImportFrom) and n.module in ('closed_production_continuation_CPU_v2','original_account_policy50_source_CPU') for n in ast.walk(a))
   # Original target obtains source_SHA/Adam dynamically from the NEW manifest.
   assert b"m['source_SHA']" in before and b"m['source_Adamstep']" in before
  case(key+'_original_target_full_byte_AST_prefix_dynamic_source_not_old_owner_guard',prefix_check)
  def dispatch_case(base=base,B=B,role=role):
   sys.path.insert(0,str(base))
   s=importlib.util.spec_from_file_location('normal86_dispatch_'+role.replace('.','_'),B/role);module=importlib.util.module_from_spec(s);s.loader.exec_module(module)
   import normal86_closed_source_CPU_v1 as loader
   with mock.patch.object(loader,'load',return_value='normal86'),mock.patch.object(module,'_normal86_preceding_load',return_value='old_other_role'):
    assert module.load(dict(normal86_continuation=True),B)=='normal86'
    assert module.load(dict(normal86_continuation=False),B)=='old_other_role'
  case(key+'_unchanged_node_import_dispatch_CPU',dispatch_case)
  go=dict(source_SHA=pin['SHA'],manifest_SHA='f'*64,max_parent_seconds=3900,exit_headroom_seconds=300,save_deadline=3600,nominal_end_epoch=3900)
  case(key+'_normal_signed_GO_positive_no_Task_hash_cycle',lambda spec=spec,go=go,key=key:g.validate_task_go(spec,go,key,'f'*64))
  wrong=dict(go,native_continuation_restore_required=True)
  case(key+'_normal_GO_reject_native_restore_role',lambda spec=spec,wrong=wrong,key=key:g.validate_task_go(spec,wrong,key,'f'*64),True)
  # Build synthetic state with actual installed RSL constructors. No model
  # file, policy forward, environment, optimizer step or SDK scene occurs.
  from tensordict import TensorDict
  from rsl_rl.models import MLPModel
  obs=TensorDict(dict(policy=torch.zeros(1,35),critic=torch.zeros(1,38)),batch_size=[1]);groups=dict(actor=['policy'],critic=['critic'])
  actor=MLPModel(obs,groups,'actor',6,hidden_dims=[256,128,64],activation='elu',distribution_cfg=dict(class_name='rsl_rl.modules.distribution:GaussianDistribution',init_std=.3,std_type='scalar'))
  critic=MLPModel(obs,groups,'critic',1,hidden_dims=[256,128,64],activation='elu')
  opt=torch.optim.Adam(list(actor.parameters())+list(critic.parameters()),lr=.0001)
  for p in opt.param_groups[0]['params']:opt.state[p]=dict(step=torch.tensor(float(pin['Adam'])),exp_avg=torch.zeros_like(p),exp_avg_sq=torch.zeros_like(p))
  state=dict(actor_state_dict=deepcopy(actor.state_dict()),critic_state_dict=deepcopy(critic.state_dict()),optimizer_state_dict=deepcopy(opt.state_dict()))
  if key=='h1':state.update(owned_H1_completed_updates=130,failed_partial_prefix=False)
  else:state.update(E3_production_updates=87,policy_clock=dict(policy_hz=50,physics_dt_s=.0025,decimation=8),E3_public_recovery_state={},E3_reset_contract={})
  original_cpu=dict(passed_CPU_only=True,source_SHA=pin['SHA'],all17Adam=pin['Adam'],actual_RSL_sources=[{},{}],actual_SDK_math=dict(SHA=old['expected_actual_SDK_math_SHA']),source_schema_counts=pin['counts'],
    new_reward_integration_CPU=dict(actual_installed_sampled_excess_SDK_compute_tested=True),boundary_repair_integration_CPU=dict(passed=True),
    sampling_acceleration_CPU=dict(passed=True,fresh_bank_physical_read_count=1,V8_reward_publication_AST=dict(passed=True),lifetime_goal_diagnostic_CPU=dict(passed=True),landing_event_journal_CPU=dict(passed=True)))
  memory=io.StringIO();original_open=Path.open;original_read=g.read
  def open_without_receipt_file(path,*a,**kw):
   if path.name=='NORMAL86_INSTALLED_SOURCE_SDK_CPU_ADMITTED_ACTUAL.json':
    class Capture:
     def __enter__(self):return memory
     def __exit__(self,*unused):return False
    return Capture()
   return original_open(path,*a,**kw)
  def fixture_read(path):
   if Path(path).name=='original_run_manifest.json':return dict(env=dict(RM_HIDDEN_DIMS='256,128,64',RM_INIT_STD='0.3'))
   return original_read(path)
  fresh_holder={}
  def complete_case(B=B,m=m,state=state,original_cpu=original_cpu):
   with mock.patch.object(g,'check_payload',return_value={}),mock.patch.object(g,'read',side_effect=fixture_read),mock.patch.object(g,'H',return_value='f'*64),mock.patch.object(g,'read_bound_metadata',return_value=(binding,data)),mock.patch.object(Path,'open',open_without_receipt_file):
    fresh_holder['value']=g.complete_installed_CPU(B,m,state,original_cpu)
   assert fresh_holder['value']['RSL_strict_load_literal_roundtrip_CPU']
   synthetic_receipts.append(dict(scope='SYNTHETIC_IN_MEMORY_ONLY_NOT_ACTUAL86_SDK',key=key,value=fresh_holder['value']))
  case(key+'_installed_RSL_true_API_synthetic_state_literal_load_no_forward',complete_case)
  if fresh_holder:
   value=g.ready_value(spec,fresh_holder['value'],'d'*64)
   common=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86_20261026/controllers_v2/three_slot_common_v1.py'
   tree=ast.parse(common.read_text('utf8'));fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='valid_ready')
   scope=dict(hashlib=hashlib,json=json);exec(compile(ast.Module(body=[fn],type_ignores=[]),str(common),'exec'),scope)
   envelope=dict(value=value,SHA=hashlib.sha256(json.dumps(value,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
   row=dict(key=key,phase='ready',manifest_SHA='f'*64,closed_source_CPU=envelope,original_error=False)
   case(key+'_root_actual_common_normal_valid_ready_positive',lambda row=row,spec=spec,scope=scope:g.require(scope['valid_ready'](row,spec),'Root rejected normal fixture'))
   bad=deepcopy(fresh_holder['value']);bad['actual_installed_CPU_passed']=False
   case(key+'_cannot_promote_source_only_to_actual_SDK_ready',lambda spec=spec,bad=bad:g.ready_value(spec,bad,'d'*64),True)
  for p in B.rglob('*.py'):case(key+'_AST_'+p.name,lambda p=p:ast.parse(p.read_text('utf8')))
 for rel in ('../escape.py','/abs.py','source\\escape.py','C:/outside.py'):
  case('contained_reject_'+rel,lambda rel=rel:g.contained(D,rel),True)
 assert not torch.cuda.is_initialized()
 report=dict(epoch=time.time(),passed=all(c['passed'] for c in cases),count=len(cases),passed_count=sum(c['passed'] for c in cases),cases=cases,
    synthetic_installed_receipts=synthetic_receipts,CPU_only=True,CUDA_initialized=False,
    actual86_installed_SDK_CPU=False,original_target_SDK_scripts_executed=False,
    source_AST_and_true_installed_RSL_API_only=True,no_real_PT_NPZ_read_hash_copy=True,
    no_remote_GPU_policy_ledger_lock_Task_GO_Git=True,archive='pending root ordinary supplement')
 path=D/'reports'/('NORMAL86_TYPED_SOURCE_SYNTHETIC_CPU_ATTEMPT_'+str(time.time_ns())+'.json')
 with path.open('x',encoding='utf8') as stream:json.dump(report,stream,indent=2,allow_nan=False)
 print(json.dumps(dict(passed=report['passed'],count=report['count'],passed_count=report['passed_count'],report=str(path))))
 if not report['passed']:raise SystemExit(1)


if __name__=='__main__':main()

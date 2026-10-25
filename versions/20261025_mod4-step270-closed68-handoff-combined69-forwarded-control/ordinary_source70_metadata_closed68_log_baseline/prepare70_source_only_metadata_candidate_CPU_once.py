"""Actual69 GO/PPO permits source-only70 reservation; all tests below use synthetic metadata."""
from pathlib import Path
import copy,hashlib,importlib.util,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
R.mkdir(exist_ok=True)
current=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V4_RESOURCE_V69_20261025'
actual=json.loads((current/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes())
assert actual['passed'] and actual['actual_finite_returned'] and actual['H1_new_step270_actual_GO_and_positive_PPO'] and actual['E3_same50Hz_actual_GO_and_positive_PPO']
assert not any((N/x).exists() for x in ('payloads','controllers','current_pair_closed_models'))
p=N/'same_optimized_source_contract_metadata_candidate_v1.py';sp=importlib.util.spec_from_file_location('metadata_candidate',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
model=dict(final=dict(updates=3,twohost_complete_SHA=True,SHA='a'*64,bytes=100,local_path='SYNTHETIC_ONLY_NOT_A_FILE'),updates=3,Adam=790480+60,
           all17_changed=dict(actor_state_dict=['distribution.std_param']+['synthetic_actor_'+str(i) for i in range(8)],critic_state_dict=['synthetic_critic_'+str(i) for i in range(8)]),
           actual_cost=dict(started_epoch=1000.,ended_epoch=1200.,charged_seconds=200.,actual_returncode=0,duration_bound_passed=True))
fixture=dict(passed=True,all_owner_nodes_children_actual_out=True,original_canonical_cost_settled=True,all_original_private_shared_locks_free=True,models=dict(h1=model))
assert m.validate_closed69_metadata(fixture,'h1',790480)['metadata_passed'];tests=['synthetic_valid_metadata_passed']
cases=[]
for key in ('all_owner_nodes_children_actual_out','original_canonical_cost_settled','all_original_private_shared_locks_free'):
 v=copy.deepcopy(fixture);v[key]=False;cases.append((key,v))
v=copy.deepcopy(fixture);v['models']['h1']['Adam']+=20;cases.append(('wrong_Adam',v))
v=copy.deepcopy(fixture);v['models']['h1']['final']['SHA']='UNKNOWN';cases.append(('missing_full_SHA',v))
v=copy.deepcopy(fixture);v['models']['h1']['all17_changed']['actor_state_dict'][0]='not_STD';cases.append(('STD_not_changed',v))
v=copy.deepcopy(fixture);v['models']['h1']['actual_cost']['duration_bound_passed']=False;cases.append(('original_duration_bound_false_rejected',v))
v=copy.deepcopy(fixture);v['not_a_pass_of_original_owner_duration_bound']=True;cases.append(('closed68_exception_not_reused',v))
for label,v in cases:
 try:m.validate_closed69_metadata(v,'h1',790480)
 except (AssertionError,KeyError):tests.append(label+'_rejected')
 else:raise AssertionError(label)
prior=dict(files=[dict(relative='job0/runtime/reports/SOURCE_FREEZE.json',bytes=123,SHA='b'*64),dict(relative='job0/runtime/isaac/mod4/e3_reset_bank_cache_v1.py',bytes=456,SHA='c'*64)])
assert m.validate_same_optimized_protected_inventory(prior,copy.deepcopy(prior))['metadata_inventory_passed'];tests.append('same_optimized_inventory_passed')
for label,other in [('missing_SOURCE_FREEZE',dict(files=prior['files'][1:])),('extra_runtime',dict(files=prior['files']+[dict(relative='job0/runtime/extra.py',bytes=1,SHA='d'*64)])),('changed_runtime',dict(files=[dict(prior['files'][0],SHA='e'*64),prior['files'][1]]))]:
 try:m.validate_same_optimized_protected_inventory(prior,other)
 except AssertionError:tests.append(label+'_rejected')
 else:raise AssertionError(label)
config=dict(epoch=time.time(),status='SOURCE_ONLY_METADATA_CANDIDATE_CPU_TESTED_NO_PAYLOAD_NO_GO',predecessor_namespace=str(current),predecessor_actual_run_id=actual['run_id'],
            predecessor_first_PPO_only_not_FINAL=True,qualified_next_source_SHA=None,qualified_next_source_Adam=None,
            needs_current69_complete_FINAL_wholeCPU_original_cost_allout=True,needs_fresh_installed_source_SDK_RSL_and_guarded_deployer=True,
            no_auto_launch_or_payload_creation=True,reward_recipe_baseline='V6A sagittalXZ tuck1.7/.22 plus airborne feasibility-.05, subject to actual69 saved-data review',
            runtime_baseline='Current69d exact H1 lossless trace and E3 fixed geometry cache; same optimized inventory, no replay of old68->69 migration admission',
            physical_success_standard='Actual both-wheel270mm crossing + top contact +200callbacks/.5s stable recovery',
            reserved_source_only_after_actual69_GO_and_PPO=True,training_precision='FP32',subagents_prohibited=True,
            total_authorized_seconds=2268000,extension_records=9,strict_remaining_guard=82512.86069250107,original_single_writer_only=True,
            no_changes_to_current69_runtime_budget_locks_or_processes=True)
with (N/'SOURCE_ONLY_CONTINUATION_CONFIG.json').open('x',encoding='utf8') as f:json.dump(config,f,ensure_ascii=False,indent=2)
report=dict(epoch=time.time(),passed=True,scope='Synthetic metadata and inventory contract tests only; not model loading or target admission',tests=tests,
            metadata_candidate_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),actual69_GO_PPO_reference=str(current/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json'),
            no_new_PPO_or_GPU_or_remote_query_or_checkpoint_read=True,no_payload_Task_model_GO_or_fee=True)
with (R/'SOURCE_ONLY70_METADATA_AND_INVENTORY_CANDIDATE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(passed=True,source_only=True,tests=len(tests),no_payload_or_GO=True)))

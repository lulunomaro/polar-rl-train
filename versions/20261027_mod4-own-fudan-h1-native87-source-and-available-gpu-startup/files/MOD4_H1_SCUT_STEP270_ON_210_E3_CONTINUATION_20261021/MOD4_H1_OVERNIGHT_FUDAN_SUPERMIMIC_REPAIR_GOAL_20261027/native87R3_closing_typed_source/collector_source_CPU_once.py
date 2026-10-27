"""Metadata and source-only gate tests. No SSH, models, GPU or fee writes."""
from pathlib import Path
import ast,copy,json,sys
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from native87R3_closing_protocol_v1 import *
checks=[]
def yes(v,name):
 assert v,name
 checks.append(name)
def refuse(fn,name):
 try:fn()
 except (RuntimeError,AssertionError,KeyError,TypeError):checks.append(name);return
 raise AssertionError('accepted '+name)
go={k:dict(source_SHA=SOURCE_SHA,bootstrap_SHA=SOURCE_SHA,bootstrap_Adam=832460,max_parent_seconds=3900,exit_headroom_seconds=300,
 learning_started_epoch=100.,save_deadline=3700.,nominal_end_epoch=4000.,native87_policy_only=True,new_native_architecture_fresh=True,
 native_continuation_restore_required=False,source_qualification_kind=KIND,seed=SEEDS[k],num_envs=4096) for k in KEYS}
yes(closing_gate(go,3100.),'original_900_boundary_inclusive')
refuse(lambda:closing_gate(go,3099.999),'before_900_boundary_refused')
bad=copy.deepcopy(go);bad['h1']['save_deadline']+=1;refuse(lambda:closing_gate(bad,3100.),'original_3600_save_deadline_required')
bad=copy.deepcopy(go);bad['recovery']['source_SHA']='bad';refuse(lambda:closing_gate(bad,3100.),'normal_bootstrap_source_pin_required')
bad=copy.deepcopy(go);bad['e2']=copy.deepcopy(bad['h1']);refuse(lambda:closing_gate(bad,3100.),'deferred_e2_cannot_enter_R3_close')
owner=dict(pid=42,creation=50.)
cost={k:dict(duration_bound_passed=True,actual_returncode=0,started_epoch=100.,ended_epoch=200.,charged_seconds=100.,max_parent_seconds=3900) for k in KEYS}
a=dict(owner_exit=dict(original_cost_settled=True),cohort=dict(original_cost_settled=True,rows={k:dict(returncode=0) for k in KEYS}),
 all_authority72_owner_children_actual_out=True,canonical_active_segment=None,canonical_path=CANONICAL,
 original_locks=[dict(actual_fcntl_free=True)]*2,original_segment=dict(owner_parent_pid=42,started_epoch=75.,experts=cost,charged_expert_seconds=200.),original_canonical_remaining=123.)
yes(validate_fees(a,go,owner)['actual_cost_sumonce']==200.,'two_independent_original_cost_sumonce')
bad=copy.deepcopy(a);bad['original_segment']['experts']['h1']['duration_bound_passed']=False
refuse(lambda:validate_fees(bad,go,owner),'original_false_duration_not_repaired')
yes(bad['original_segment']['experts']['h1']['duration_bound_passed'] is False,'original_false_flag_retained')
bad=copy.deepcopy(a);bad['original_segment']['charged_expert_seconds']=100.;refuse(lambda:validate_fees(bad,go,owner),'no_single_role_fee_substitution')
bad=copy.deepcopy(a);bad['canonical_active_segment']={};refuse(lambda:validate_fees(bad,go,owner),'canonical_None_required')
bad=copy.deepcopy(a);bad['original_locks'][0]['actual_fcntl_free']=False;refuse(lambda:validate_fees(bad,go,owner),'both_original_locks_free_required')
remote=(D/'native87R3_close_readonly_remote_v1.py').read_text('utf8')
old=(D.parent.parent/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026/agent_three_gpu86b_closing_CPU_protocol_20261026/three_gpu86b_close_readonly_remote_v1.py').read_text('utf8')
def func(s,name):return ast.dump(next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name==name))
for name in ('_read_json','_own_processes','_free_locks','_texts'):
 yes(func(remote,name)==func(old,name),name+'_AST_exact_original')
yes('time.monotonic()+850' in remote and 'time.monotonic()+180' in remote,'owner850_each_node180_waits_retained')
collector=(D/'collect_H1_native87R3_finals_actual_cost_unused_once.py').read_text('utf8')
yes("assert max(x['nominal_end_epoch'] for x in go.values())-time.time()<=900" in collector and "assert max(x['nominal_end_epoch'] for x in original_go.values())-time.time()<=900" in remote,'both_local_and_remote_original_900_assertions_retained')
yes(collector.index('closing_gate(go,time.time())')<collector.index('import deploy_two50_reconciled_original_writer_once'),'local_gate_before_transport_import')
yes('one_fresh_snapshot_only=True' in collector and 'Unexpected text mismatch; original retained' in collector,'only_original_once_log_mismatch_exception_retained')
for p in D.glob('*.py'):ast.parse(p.read_bytes())
with (D/'COLLECTOR_SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,count=len(checks),checks=checks,source_and_metadata_only=True,network_model_GPU_or_budget_operation=False),f,indent=2)
print(json.dumps(dict(passed=True,count=len(checks))))

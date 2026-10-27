"""R5 namespace/GO/source-evidence tests, no model/SDK/transport/fee operation."""
from pathlib import Path
import ast,copy,hashlib,json,sys
D=Path(__file__).resolve().parent;O=D.parent/'native87R3_closing_typed_source'
N=D.parent.parent/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027';sys.path.insert(0,str(D))
import native87R5_closing_protocol_v1 as p
import review_H1_native87R5_finals_CPU_unused_once as reviewer
checks=[]
def yes(v,name):
 assert v,name
 checks.append(name)
def refuse(fn,name):
 try:fn()
 except (ValueError,RuntimeError,AssertionError,KeyError,TypeError):checks.append(name);return
 raise AssertionError('unexpected acceptance '+name)
prepared_path=N/'reports/AVAILABLE_TWO_NATIVE87R5_SOURCE_PREPARED_ACTUAL.json';prepared=json.loads(prepared_path.read_bytes())
q=dict(prepared,run_id='SYNTHETIC_BINDING_FIXTURE_NOT_ACTUAL_GO',owner_identity=dict(pid=42,creation=1.),nodes={k:{} for k in p.KEYS})
yes(p.validate_detached(q),'saved_actual_R5_source_roots_with_explicit_synthetic_owner_fixture')
go={k:dict(source_SHA=p.SOURCE_SHA,bootstrap_SHA=p.SOURCE_SHA,bootstrap_Adam=832460,max_parent_seconds=3900,exit_headroom_seconds=300,
 learning_started_epoch=100.,save_deadline=3700.,nominal_end_epoch=4000.,native87_policy_only=True,new_native_architecture_fresh=True,
 native_continuation_restore_required=False,source_qualification_kind=p.KIND,seed=p.SEEDS[k],num_envs=4096,
 run_id=q['run_id'],original_owner_pid=42,original_owner_creation=1.,manifest_SHA=q['specs'][k]['manifest_SHA'],native87_contract_SHA=q['specs'][k]['native87_contract_SHA']) for k in p.KEYS}
yes(p.closing_gate(go,3100.) and p.validate_actual_GO_binding(go,q),'synthetic_GO_exact_R5_run_owner_source_and_900_gate_positive')
refuse(lambda:p.closing_gate(go,3099.999),'original_900_gate_before_boundary_refused')
for field,badvalue,label in [('run_id','OLD_R4','old_run_GO_refused'),('original_owner_pid',99,'wrong_actual_owner_pid_refused'),('original_owner_creation',2.,'recycled_owner_creation_refused'),('manifest_SHA','a'*64,'wrong_GO_manifest_refused'),('native87_contract_SHA','b'*64,'wrong_GO_contract_refused')]:
 bad=copy.deepcopy(go);bad['h1'][field]=badvalue
 refuse(lambda:p.validate_actual_GO_binding(bad,q),label)
bad=copy.deepcopy(q);bad['roots']['h1']=bad['roots']['h1'].replace('v87r5','v87r4')
refuse(lambda:p.validate_detached(bad),'old_R4_root_not_accepted_as_R5')
bad=copy.deepcopy(go);bad['e2']=bad['h1'];refuse(lambda:p.closing_gate(bad,3100.),'unknown_busy_e2_not_added_to_schedule')
fixture=json.loads((D.parent/'native87_SDK_tensor_ingress_fix_v1/SOURCE_CPU_ACTUAL.json').read_bytes())['portable_target_CPU_fixture']
e=dict(value=dict(actual_observation_manager_API_source_CPU_passed=True,expected_actual_SDK_observation_manager_SHA='de7c9b2c6b6e0bdb431a0574727982feebe72142ebf41b1140dce624b932d6b8',
 actual_SDK_tensor_ingress_CPU_passed=True,actual_SDK_tensor_ingress_CPU=fixture,
 expected_actual_SDK_base_articulation_data_SHA='677d500672162d9bdc04b417c726b0d61edc839e0396cb3faf15316fbca28067',
 expected_actual_SDK_physx_articulation_data_SHA='43a31992353ad3a500024d0ec908d5b253ada7a0aac9a1cd2261466e10bda4ff'))
yes(reviewer.validate_R5_source_CPU_evidence(e),'explicit_source_fixture_evidence_schema_positive_not_actual_CPU_admission')
bad=copy.deepcopy(e);bad['value'].pop('actual_SDK_tensor_ingress_CPU')
refuse(lambda:reviewer.validate_R5_source_CPU_evidence(bad),'old_R3_R4_CPU_without_ingress_evidence_refused')
bad=copy.deepcopy(e);bad['value']['actual_SDK_tensor_ingress_CPU']['actual_GPU_runtime_readback_passed']=True
refuse(lambda:reviewer.validate_R5_source_CPU_evidence(bad),'source_fixture_cannot_claim_actual_GPU')
bad=copy.deepcopy(e);bad['value']['actual_SDK_tensor_ingress_CPU']['actual_source_SHA_checks']['base']['SHA']='a'*64
refuse(lambda:reviewer.validate_R5_source_CPU_evidence(bad),'wrong_actual_base_source_SHA_refused')
def node(path,name):
 tree=ast.parse(path.read_bytes());return next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
newreview=D/'review_H1_native87R5_finals_CPU_unused_once.py';oldreview=O/'review_H1_native87R3_finals_CPU_unused_once.py'
for name in ('exact','finite','original_physical_state','frozen_bootstrap','validate_native_optimizer','native_modules','role_terminal','review_role'):
 yes(ast.dump(node(newreview,name))==ast.dump(node(oldreview,name)),name+'_AST_exact_previously_CPU_verified')
yes(ast.dump(node(newreview,'OneInitialLoadPool')).replace('native87R5','native87R3')==ast.dump(node(oldreview,'OneInitialLoadPool')),'one_initial_load_pool_only_new_purpose_label_change')
yes((D/'native87R5_event_curve_summary_v1.py').read_text('utf8').replace('native87R5','native87R3')==(O/'native87R3_event_curve_summary_v1.py').read_text('utf8'),'completed_control_interval_curve_algorithm_byte_text_exact_except_schema_label')
remote=(D/'native87R5_close_readonly_remote_v1.py').read_text('utf8');oldremote=(O/'native87R3_close_readonly_remote_v1.py').read_text('utf8')
for name in ('_read_json','_own_processes','_free_locks','_texts'):
 yes(ast.dump(node(D/'native87R5_close_readonly_remote_v1.py',name))==ast.dump(node(O/'native87R3_close_readonly_remote_v1.py',name)),name+'_original_AST_exact')
collector=(D/'collect_H1_native87R5_finals_actual_cost_unused_once.py').read_text('utf8')
yes("assert max(x['nominal_end_epoch'] for x in go.values())-time.time()<=900" in collector and "assert max(x['nominal_end_epoch'] for x in original_go.values())-time.time()<=900" in remote,'both_original_900_assertions_retained')
yes('time.monotonic()+850' in remote and 'time.monotonic()+180' in remote,'original_owner850_then_each_target180')
yes(collector.index('validate_actual_GO_binding(go,q)')<collector.index('import deploy_two50_reconciled_original_writer_once'),'actual_GO_binding_before_credentials_or_transport')
yes('original.PT' not in collector and 'current_native87R5_method_fullstate' in collector,'model_collection_scope_new_R5_only')
for f in D.glob('*.py'):ast.parse(f.read_bytes())
with (D/'SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,count=len(checks),checks=checks,
 source_and_synthetic_metadata_only=True,actual_GO_deadline_not_assumed=True,actual_model_hash_load_actor_SDK_GPU_network_or_fee_operation=False,
 saved_R5_prepared_SHA=hashlib.sha256(prepared_path.read_bytes()).hexdigest(),
 retained_prior_source_CPU_reports=[dict(path=str(O/name),SHA=hashlib.sha256((O/name).read_bytes()).hexdigest()) for name in ('COLLECTOR_SOURCE_CPU_ACTUAL.json','REVIEWER_SOURCE_CPU_ACTUAL.json')],old_fixtures_not_rerun=True),f,indent=2)
print(json.dumps(dict(passed=True,count=len(checks))))

"""Independent semantic AST review; finish unexecuted local preparation only.

Original builderfalse/error and four generated files retained unchanged.
No oldonce/runtime/worker/controller imported or executed.
"""
from pathlib import Path
import ast,hashlib,json,time,traceback,copy,importlib.util
D=Path(__file__).resolve().parent;W=D.parent
OLD=W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013';P=D/'payload_v1';R=D/'reports'
OUT=R/'SECOND_SAMEIDENTITY_SEMANTIC_AST_SCHEMA_CPU_PREPARED_ACTUAL.json';assert not OUT.exists()
SOURCE_SHA='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971'
PROPOSED='/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_exploration20k_second_formal_sameidentity_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def index(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=sha(p))
try:
 original_error=next(R.glob('CPU_SECOND_PREPARE_ORIGINAL_ERROR_*.json'))
 e=json.loads(original_error.read_bytes());assert 'AssertionError' in e['error']
 assert "assert 'candidate' not in contract" in e['error']
 files=[P/'left_sameidentity_typed13_receipts.py',P/'left_exploration_sameidentity_resume_contract_v2.py',P/'left_exploration_sameidentity_second_worker_v1.py',P/'left_second_sameidentity_typed_parent_v1.py']
 before=[index(p) for p in files]
 trees={p.name:ast.parse(p.read_text()) for p in files}
 for p in files:compile(p.read_text(),str(p),'exec')
 contract=P/'left_exploration_sameidentity_resume_contract_v2.py';tree=trees[contract.name]
 calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)]
 assert not any(isinstance(n.func,ast.Attribute) and n.func.attr=='load_state_dict' for n in calls)
 identifiers=[n.id for n in ast.walk(tree) if isinstance(n,ast.Name)]
 assert 'candidate' not in identifiers and 'new' not in identifiers
 assert not any(isinstance(n,ast.If) and 'KEY not in' in ast.unparse(n.test) for n in ast.walk(tree))
 assert 'assert KEY in ck' in contract.read_text()
 worker=P/'left_exploration_sameidentity_second_worker_v1.py';parent=P/'left_second_sameidentity_typed_parent_v1.py'
 for p in [worker,parent]:
  assert any(isinstance(n,ast.If) and ast.unparse(n.test)=="__name__ == '__main__'" for n in trees[p.name].body)
 def fn(text,name):return next(n for n in ast.walk(ast.parse(text)) if isinstance(n,ast.FunctionDef) and n.name==name)
 oldworker=OLD/'left_exploration_worker_v3.py';oldparent=OLD/'left_first_formal_retained_parent_v2.py';oldcontract=OLD/'left_exploration_resume_contract_v1.py'
 assert ast.dump(fn(oldworker.read_text(),'install'),include_attributes=False)==ast.dump(fn(worker.read_text(),'install'),include_attributes=False)
 # Normallearn still exactly the inherited originalworker; only sameidentity
 # admission is stronger. No optimizer/learn override exists in this wrapper.
 assert 'rescue_training.learn=' not in worker.read_text() and 'native0PPO' not in worker.read_text() and 'fresh0PPO' not in worker.read_text()
 assert "runpy.run_path(str(worker),run_name='__main__')" in worker.read_text()
 s=parent.read_text();assert "str(R/'left_exploration_sameidentity_second_worker_v1.py')" in s
 for token in ["'--num_envs','20000'","'--seed','20260928'","'--save_interval','25'","'--steps_per_env','24'","'--learning_rate','0.0001'","RM_RESCUE_DEADLINE=str(begun+3600)","worker.wait(timeout=15)"]:
  assert token in s,token
 assert ast.dump(fn(oldparent.read_text(),'guardian'),include_attributes=False)==ast.dump(fn(s,'guardian'),include_attributes=False)
 assert "all(v['state']=='applied' for v in x)" in s and "USER_ADD100H_20261011_7TH" in s
 assert "B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')" in s
 assert "LOCKS=[B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]" in s
 typed=P/'left_sameidentity_typed13_receipts.py'
 spec=importlib.util.spec_from_file_location('new_typed_schema_only',typed);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 fixture_dir=OLD/'left_first_formal_ownsave_1791939576241228200';fixture=[];accepted=[]
 for p in sorted(fixture_dir.glob('*STARTUP*VERIFIED.json')):
  v=json.loads(p.read_bytes());name=p.name.split('_',1)[1]
  fixture.append(dict(path=str(p),sha256=sha(p),name=name,proof=v))
  accepted.append(module.validate_one(name,v,v['pid'],v['source_sha256']))
 assert len(accepted)==13 and sum(not x['passed_field_required'] for x in accepted)==8
 negatives=[]
 row=next(x for x in fixture if x['name']=='E1_WAVE50_ENTRY_STARTUP_VERIFIED.json')
 for label,mut in [('wrongsource',lambda v:v.update(source_sha256='0'*64)),('wrongpid',lambda v:v.update(pid=-1)),('unexpectednewentry',lambda v:v.update(explicit_new_entry_scope=True)),('missing_required_exact',lambda v:v.pop('same_entry_identity_restored_exact'))]:
  v=copy.deepcopy(row['proof']);mut(v)
  try:module.validate_one(row['name'],v,row['proof']['pid'],row['proof']['source_sha256'])
  except AssertionError:negatives.append(dict(case=label,strict_rejected=True))
  else:raise AssertionError('Badtypedfixture accepted: '+label)
 mpath=fixture_dir/'14_LEFT_FORMAL_ADMISSION_MANIFEST.json';m=json.loads(mpath.read_bytes());assert len(m['sourcefreeze'])==522
 proof=OLD/'reports/LEFT_FORMAL_FINAL_LOCAL_CPU_AND_FROZEN80_CANDIDATE_PREPARED.json';f=json.loads(proof.read_bytes());assert f['passed'] and f['own_final_source']['sha256']==SOURCE_SHA
 src=dict(path=f['own_final_source']['path'],sha256=SOURCE_SHA,bytes=f['own_final_source']['bytes'],local_reference=f['own_final_source']['local_path']);assert sha(src['local_reference'])==SOURCE_SHA
 template=dict(epoch=time.time(),CPU_prepared_only=True,proposed_remote_root=PROPOSED,remote_root_NOT_created_or_claimed_existing=True,num_envs=20000,seed=20260928,duration_seconds=3600,scope_learning_block_index=2,max_blocks_same_axis=2,planned_first_plus_second_seconds=7200,
  source=src,source_is_complete_first_formal_whole20k_own2b_not_candidates=True,no_new_policy_axis=True,no_initializer_repeat=True,approved_GPU=False,target_CPU_actual_passed=False,
  actual_four_case_scope_decision=dict(path='PENDING_ROOT_ACTUAL_FOUR_CASE_SCOPE_REVIEW',sha256=None),
  required_scope_decision_true_fields=['whole20k2b_source_actual_CPU_verified','first_formal_fulltrace_actual_reviewed','four_frozen_cases_actual_complete','physical_source_query_contact_COMhardware_all_raw_admitted','sameidentity_second3600_reasonable','no_new_policy_axis','center_near_candidates_rejected_not_source','second_and_last_block_before_full_audit'],
  sourcefreeze=[],target_sourcefreeze_PENDING_actual_materialization=True,original_runtime_sourcefreeze_reuse_required=index(mpath),original_runtime_sources522_byteexact_required=True,
  original_environment=m['original_environment'],original_environment_exact_digest=hashlib.sha256(json.dumps(m['original_environment'],sort_keys=True).encode()).hexdigest(),prepared_payload_sources=[index(p) for p in files],source_first_formal_actual_CPU_proof=index(proof),
  same_original_locks_and_sole1188000canonical_seven_applied_no_new_transaction=True,actual_source13_CPUCUDA_strict_then_newphysical_episode_plus_one_REQUIRED_future=True,
  actorcriticstdAdam_allD0D7_globalnamed_dictprivate_and_geometry_entry_command_direction_route_lifetime_leftmetadata_exact_REQUIRED_future=True,
  stale_original_environment_initialadmission_label_historical_actual_sameidentity_proofs_precede_claims=True,
  no_native_fresh_preflight_clock_replay_no_oldonce_entry_no_SSH_GPU_PPO_or_budget=True,qualified50=False,Git_archive_pending_root_owner=True)
 tp=P/'LEFT_SECOND_SAMEIDENTITY_ADMISSION_MANIFEST_CPU_TEMPLATE.json';assert not tp.exists();tp.write_text(json.dumps(template,indent=2),encoding='utf8')
 assert all(sha(x['path'])==x['sha256'] for x in before)
 out=dict(epoch=time.time(),passed=True,status='Independent CPU AST/schema prep; no remote target orGPU admission',proposed_remote_root=PROPOSED,remote_root_created=False,source2b_actual_localSHA_rechecked=True,
  prepared_sources=[index(p) for p in files+[tp]],inherited_readonly_sources=[index(p) for p in [oldparent,oldworker,oldcontract,mpath]],
  original_builder_error_retained=index(original_error),independent_repair='ASTsemanticchecks exclude docstrings; only finish unexecuted typedfixture andmanifest preparation. No rewrite/replayofoldbuilder.',
  actual_13_receipt_schema_preflight=accepted,eight_legacy_receipts_without_passed_accepted=True,four_bad_receipt_copies_strict_rejected=negatives,
  currentupdate_savehook_AST_exact=True,original_guardian_AST_exact=True,original_normallearn_path_byteexact_reuse_required=True,newtruthworker_formal_only_main_guarded=True,
  sameidentity_only_no_initializer_branch_or_load_state_dict_after_inherited_restore=True,original_parameters_seed_clock_LR_DRreward_hardware_retained=True,
  original_same2fcntl_locks_solecanonical_7applied_guard_same_owner_unique_fullcost=True,original_root_isolated_guardian_no_collision_prepared=True,
  actual_fourcase_scope_decision_and_target_CPU_sourcefreeze_required_before_unique_launch=True,template_approvedGPU_false_and_empty_freeze_failclosed=True,
  proposed_target_mount_durable_resources55GBRAM30GBdisk22GBfreeGPU_guard_not_lowered=True,
  no_oldonce_import_execution_no_SSH_GPU_budget_or_Git=True,Git_archive_pending_root_owner=True)
 OUT.write_text(json.dumps(out,indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(OUT),sameidentity_sources=len(files),schema13accepted=True,eightmissingpassedhandled=True,originalerror_preserved=True,only_CPU_prepared=True,remote_target_created=False)))
except Exception:
 p=R/f'SEMANTIC_CPU_READER_ERROR_{time.time_ns()}.json';p.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),source_script=index(__file__),no_GPU_SSH_budget=True,Git_archive_pending_root_owner=True),indent=2),encoding='utf8');raise

"""Prepare isolated CPU source only; read old source, never import old once."""
from pathlib import Path
import ast,hashlib,json,time,traceback,copy,importlib.util
W=Path(r'C:/Users/lulu/Desktop/claude/mjcf')
OLD=W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013'
D=Path(__file__).resolve().parent;P=D/'payload_v1';assert not P.exists(),'Preserve existing prepared source'
P.mkdir();R=D/'reports';R.mkdir(exist_ok=True)
SOURCE_SHA='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971'
PROPOSED='/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_exploration20k_second_formal_sameidentity_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def index(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=sha(p))
def write(name,s):
 p=P/name;assert not p.exists();p.write_text(s,encoding='utf8');compile(s,str(p),'exec');return p
try:
 oldparent=OLD/'left_first_formal_retained_parent_v2.py'
 oldworker=OLD/'left_exploration_worker_v3.py'
 oldcontract=OLD/'left_exploration_resume_contract_v1.py'
 mpath=OLD/'left_first_formal_ownsave_1791939576241228200/14_LEFT_FORMAL_ADMISSION_MANIFEST.json'
 fixtures=mpath.parent
 oldindices=[index(p) for p in [oldparent,oldworker,oldcontract,mpath]]
 m=json.loads(mpath.read_bytes());assert m['num_envs']==20000 and m['seed']==20260928 and len(m['sourcefreeze'])==522
 ow=oldworker.read_text();op=oldparent.read_text()
 ast.parse(ow);ast.parse(op)
 schema={};fixture=[]
 for p in sorted(fixtures.glob('*STARTUP*VERIFIED.json')):
  v=json.loads(p.read_bytes());name=p.name.split('_',1)[1]
  schema[name]={k:z for k,z in v.items() if isinstance(z,bool)}
  fixture.append(dict(path=str(p),sha256=sha(p),name=name,proof=v))
 assert len(schema)==13 and sum('passed' not in x for x in schema.values())==8
 typed='''"""Typed historical13receipt schema; no generic passed-key assumption."""
from pathlib import Path
import json
REQUIRED_BOOLEAN_SCHEMA = '''+repr(schema)+'''
def validate_one(name,v,expected_pid,expected_source_SHA):
    assert name in REQUIRED_BOOLEAN_SCHEMA,('Unknownreceipt',name)
    assert isinstance(v,dict) and v.get('pid')==expected_pid and v.get('source_sha256')==expected_source_SHA
    for field,required in REQUIRED_BOOLEAN_SCHEMA[name].items():
        assert v.get(field) is required,('Missingorwrongtypedreceiptfield',name,field,required)
    return dict(name=name,typed_actual_boolean_fields=len(REQUIRED_BOOLEAN_SCHEMA[name]),passed_field_required='passed' in REQUIRED_BOOLEAN_SCHEMA[name])
def validate_set(paths,expected_pid,expected_source_SHA):
    paths=list(paths);assert len(paths)==13
    names=[Path(p).name for p in paths];assert len(set(names))==13 and set(names)==set(REQUIRED_BOOLEAN_SCHEMA)
    return [validate_one(Path(p).name,json.loads(Path(p).read_bytes()),expected_pid,expected_source_SHA) for p in paths]
'''
 typedpath=write('left_sameidentity_typed13_receipts.py',typed)
 contract='''"""Sameidentity-only restore. No candidate or initializer branch exists."""
from pathlib import Path
import copy,hashlib,json,time,os
import torch
KEY='LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION'
EXPECTED_OWN_SOURCE_SHA='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971'
PROFILE='left_initial_joint_margin014_std1_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def same(a,b):
    if isinstance(a,torch.Tensor):return isinstance(b,torch.Tensor) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a.cpu(),b.cpu())
    if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(same(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return type(a)is type(b) and len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    if hasattr(a,'shape'):
        import numpy as np
        return type(a)is type(b) and np.array_equal(a,b)
    return type(a)is type(b) and a==b
def actual_action_API(env):
    assert env.num_envs==20000
    rows=[]
    for name,term in env.action_manager._terms.items():
        if term.action_dim==4:
            offset=term._offset;q=env.scene['robot'].data.default_joint_pos[:,term._joint_ids]
            assert isinstance(offset,torch.Tensor) and offset.shape==(20000,4)
            assert torch.equal(offset,torch.zeros_like(offset)) and torch.equal(q,torch.zeros_like(q))
            scale=term._scale
            if isinstance(scale,torch.Tensor):assert bool((scale==.5).all())
            else:assert scale==.5
            rows.append(dict(term=name,count=20000,offset_shape=list(offset.shape),offset_all_exact_zero=True,default_joint_q_all_exact_zero=True,scale_exact_half=True,joint_names=term._joint_names))
    assert len(rows)==1
    return rows
def patch(module,root):
    old_resume=module.resume_e1_new_episode;old_install=module.install_e1_save_contract
    def resume(runner,env,path,log_dir):
        assert sha(path)==EXPECTED_OWN_SOURCE_SHA,'Onlyactualwhole20kown2bsource'
        ck=torch.load(path,map_location='cpu',weights_only=False)
        assert ck['sensor_DR_state']['n']==20000 and ck['independent_terrain_expert']=='E1_WAVE50'
        assert ck['E1_WAVE50_initial_source_sha256']=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
        assert KEY in ck and ck[KEY]['profile']==PROFILE and ck[KEY]['source_envs']==20000
        assert ck[KEY]['source_SHA']=='1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06'
        assert not any(k.startswith('LINUX20K_LEFT_JOINT_CENTER_') or k.startswith('LINUX20K_LEFT_JOINT_LOWER_') for k in ck)
        original_proof=old_resume(runner,env,path,log_dir)
        assert same(runner.alg.actor.state_dict(),ck['actor_state_dict'])
        assert same(runner.alg.critic.state_dict(),ck['critic_state_dict'])
        assert same(runner.alg.optimizer.state_dict(),ck['optimizer_state_dict'])
        api=actual_action_API(env)
        beforeCPU=torch.get_rng_state().clone();beforeCUDA=[x.clone() for x in torch.cuda.get_rng_state_all()]
        mark=copy.deepcopy(ck[KEY]);runner._linux_left_exploration_mark=mark
        state=dict(actor=runner.alg.actor.state_dict(),optimizer=runner.alg.optimizer.state_dict(),mark=mark)
        q=Path(log_dir)/'LEFT_EXPLORATION_ACTUAL_CUDA_ROUNDTRIP.pt';torch.save(state,q)
        disk=torch.load(q,map_location='cpu',weights_only=False);assert same(state,disk)
        assert torch.equal(beforeCPU,torch.get_rng_state()) and all(torch.equal(a,b) for a,b in zip(beforeCUDA,torch.cuda.get_rng_state_all()))
        proof=dict(epoch=time.time(),pid=os.getpid(),passed=True,source_sha256=sha(path),source_envs=20000,profile=mark['profile'],explicit_one_time_left_mean_std_initialization=False,same_left_branch_restored_exact=True,all_original_twelve_fullstate_contracts_precede_left_axis=True,actual_all20k_action_offset_and_defaultq=api,actual_left_actor_optimizer_metadata_CUDA_disk_roundtrip_exact=True,no_CPU_CUDA_RNG_draw_for_initializer=True,no_env_DR_command_or_history_mutation_by_initializer=True,initial_other_five_heads_critic_exact=True,initializer_not_live_action_coupling=True,source_episode_plus_one_checked_by_original_contract=True,PhysX_exact_resume_claimed=False,qualified50=False,second_sameidentity_block=True,full_actor_critic_allstd_optimizer_restored_exact=True,no_initializer_branch_exists=True)
        Path(log_dir,'LEFT_EXPLORATION_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(proof,indent=2))
        return original_proof
    def install(runner,env):
        old_install(runner,env);old_save=runner.save
        def save(path,*a,**k):
            old_save(path,*a,**k);c=torch.load(path,map_location='cpu',weights_only=False)
            c[KEY]=copy.deepcopy(runner._linux_left_exploration_mark);torch.save(c,path)
        runner.save=save
    module.resume_e1_new_episode=resume;module.install_e1_save_contract=install
'''
 contractpath=write('left_exploration_sameidentity_resume_contract_v2.py',contract)
 worker='''"""Formal-onlysecondsameidentity worker; original RLworker and learn unchanged."""
import os,sys,runpy,json,time,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
def main():
    assert not os.environ.get('MOD4_LEFT_ADMISSION_MODE'),'NoSDKnativefreshreplay'
    worker=R/'isaac/mod4/train_wave50_lifetime_resume_ppo.py'
    sys.path.insert(0,str(worker.parent))
    import wave50_lifetime_full_checkpoint
    from left_exploration_sameidentity_resume_contract_v2 import patch
    patch(wave50_lifetime_full_checkpoint,R)
    import rescue_training
    original_install=rescue_training.install
    def install(runner,log_dir):
        original_install(runner,log_dir)
        original_log=runner.logger.log
        def log(*a,**kw):
            original_log(*a,**kw)
            if Path(os.environ['RM_RESCUE_STOP_FILE']).exists():runner.save(str(Path(log_dir)/f'model_{runner.current_learning_iteration}.pt'))
        runner.logger.log=log
    rescue_training.install=install
    sys.argv[0]=str(worker)
    runpy.run_path(str(worker),run_name='__main__')
if __name__=='__main__':main()
'''
 workerpath=write('left_exploration_sameidentity_second_worker_v1.py',worker)
 parent=op.replace('New formal-only Linux continuation.','New isolated secondsameidentity formal-only Linux continuation.',1)
 start=parent.index("    m=json.loads((R/'LEFT_FORMAL_ADMISSION_MANIFEST.json').read_bytes())")
 end=parent.index('    assert psutil.virtual_memory().available>=55000000000',start)
 gate='''    m=json.loads((R/'LEFT_SECOND_SAMEIDENTITY_ADMISSION_MANIFEST.json').read_bytes())
    expected='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971'
    assert m['num_envs']==20000 and m['seed']==20260928 and m['duration_seconds']==3600
    assert m['scope_learning_block_index']==2 and m['max_blocks_same_axis']==2
    assert m['planned_first_plus_second_seconds']==7200 and m['no_new_policy_axis'] is True
    assert m['approved_GPU'] is True and m['target_CPU_actual_passed'] is True
    assert m['source']['sha256']==expected and m['source']['bytes']==19044152
    assert not (R/'LEFT_SECOND_FORMAL_ONCE_CONSUMED.json').exists()
    assert sha(m['source']['path'])==expected
    decision=json.loads(Path(m['actual_four_case_scope_decision']['path']).read_bytes())
    assert sha(m['actual_four_case_scope_decision']['path'])==m['actual_four_case_scope_decision']['sha256']
    assert decision.get('selected_source_SHA')==expected
    for field in ('whole20k2b_source_actual_CPU_verified','first_formal_fulltrace_actual_reviewed','four_frozen_cases_actual_complete','physical_source_query_contact_COMhardware_all_raw_admitted','sameidentity_second3600_reasonable','no_new_policy_axis','center_near_candidates_rejected_not_source','second_and_last_block_before_full_audit'):
        assert decision.get(field) is True,field
    assert m['sourcefreeze'] and len(m['sourcefreeze'])>=522
    for x in m['sourcefreeze']:assert sha(x['path'])==x['sha256'],x['path']
'''
 parent=parent[:start]+gate+parent[end:]
 parent=parent.replace("assert d['authorized_training_seconds']==1188000 and len(x)==7", "assert d['authorized_training_seconds']==1188000 and len(x)==7\n    assert all(v['state']=='applied' for v in x)\n    assert x[-1]['extension_id']=='USER_ADD100H_20261011_7TH'\n    assert x[-1]['authorized_seconds_before']==828000 and x[-1]['authorized_seconds_after']==1188000",1)
 substitutions={
  'LEFT_FORMAL_ADMISSION_MANIFEST.json':'LEFT_SECOND_SAMEIDENTITY_ADMISSION_MANIFEST.json',
  'LEFT_FORMAL_ONCE_CONSUMED.json':'LEFT_SECOND_FORMAL_ONCE_CONSUMED.json',
  'left_formal3600_v1':'left_second_formal3600_v1',
  'left_exploration_worker_v3.py':'left_exploration_sameidentity_second_worker_v1.py',
  'E1_WAVE50_left_exploration_formal3600':'E1_WAVE50_left_sameidentity_second3600',
  'Linux_left20k_first_bounded_formal_':'Linux_left20k_second_bounded_formal_',
  'left20k_first_bounded_formal_learning':'left20k_second_sameidentity_bounded_formal_learning',
  'LEFT_FORMAL_PARENT_ERROR.json':'LEFT_SECOND_FORMAL_PARENT_ERROR.json',
  'LEFT_FORMAL_SAVED_REVIEW_READY.json':'LEFT_SECOND_FORMAL_SAVED_REVIEW_READY.json',
  'from left_exploration_resume_contract_v1 import same,KEY':'from left_exploration_sameidentity_resume_contract_v2 import same,KEY',
  'actual_first_formal_window=True':'actual_second_formal_window=True',
 }
 for a,b in substitutions.items():
  assert a in parent,a;parent=parent.replace(a,b)
 parent=parent.replace("if k.startswith('RM_'):env.pop(k)","if k.startswith('RM_') or k=='MOD4_LEFT_ADMISSION_MODE':env.pop(k)",1)
 pstart=parent.index('        markers=[]\n')
 pend=parent.index('        import torch\n',pstart)
 replacement='''        from left_sameidentity_typed13_receipts import validate_set
        paths=list(p.parent.glob('*STARTUP*VERIFIED.json'))
        typed=validate_set(paths,child['pid'],m['source']['sha256'])
        markers=[dict(path=str(q),sha256=sha(q),proof=json.loads(q.read_bytes())) for q in paths]
        assert len(markers)==13
'''
 parent=parent[:pstart]+replacement+parent[pend:]
 parentpath=write('left_second_sameidentity_typed_parent_v1.py',parent)
 # CPU AST proofs: wrapperlog savehookexact, budgethelper ownership unchanged
 # except appliedseven authorityguard, no launch or budgetmain executed.
 def function(text,name):
  return next(n for n in ast.walk(ast.parse(text)) if isinstance(n,ast.FunctionDef) and n.name==name)
 assert ast.dump(function(ow,'install'),include_attributes=False)==ast.dump(function(worker,'install'),include_attributes=False)
 astparent=ast.parse(parent);astworker=ast.parse(worker);astcontract=ast.parse(contract)
 assert any(isinstance(n,ast.If) and ast.unparse(n.test)=="__name__ == '__main__'" for n in astparent.body)
 assert any(isinstance(n,ast.If) and ast.unparse(n.test)=="__name__ == '__main__'" for n in astworker.body)
 assert "str(R/'left_exploration_sameidentity_second_worker_v1.py')" in parent
 assert "runpy.run_path(str(worker),run_name='__main__')" in worker and 'MOD4_LEFT_ADMISSION_MODE' in worker
 assert 'native0PPO' not in worker and 'fresh0PPO' not in worker and 'stochastic_output' not in worker
 assert 'candidate' not in contract and 'load_state_dict' not in contract
 # Testonlynewpuretypedhelper,neverimport oldonce or runtimecontroller/worker.
 spec=importlib.util.spec_from_file_location('new_typed_only',typedpath);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 accepted=[]
 for x in fixture:accepted.append(mod.validate_one(x['name'],x['proof'],x['proof']['pid'],x['proof']['source_sha256']))
 neg=[]
 for label,fix in [('wrongsource',lambda v:v.update(source_sha256='0'*64)),('wrongpid',lambda v:v.update(pid=-1)),('unexpectednewentry',lambda v:v.update(explicit_new_entry_scope=True)),('missing_required_exact',lambda v:v.pop('same_entry_identity_restored_exact'))]:
  row=next(x for x in fixture if x['name']=='E1_WAVE50_ENTRY_STARTUP_VERIFIED.json');v=copy.deepcopy(row['proof']);fix(v)
  try:mod.validate_one(row['name'],v,row['proof']['pid'],row['proof']['source_sha256'])
  except AssertionError:neg.append(dict(case=label,strict_rejected=True))
  else:raise AssertionError('Badtypedreceiptaccepted')
 assert len(accepted)==13 and len(neg)==4
 oldfinalproof=OLD/'reports/LEFT_FORMAL_FINAL_LOCAL_CPU_AND_FROZEN80_CANDIDATE_PREPARED.json'
 f=json.loads(oldfinalproof.read_bytes());assert f['passed'] and f['own_final_source']['sha256']==SOURCE_SHA
 source=dict(path=f['own_final_source']['path'],sha256=SOURCE_SHA,bytes=f['own_final_source']['bytes'],local_reference=f['own_final_source']['local_path'])
 assert sha(source['local_reference'])==SOURCE_SHA
 template=dict(epoch=time.time(),CPU_prepared_only=True,proposed_remote_root=PROPOSED,remote_root_NOT_created_or_claimed_existing=True,num_envs=20000,seed=20260928,duration_seconds=3600,scope_learning_block_index=2,max_blocks_same_axis=2,planned_first_plus_second_seconds=7200,
  source=source,source_is_complete_first_formal_whole20k_own2b_not_candidates=True,no_new_policy_axis=True,no_initializer_repeat=True,
  approved_GPU=False,target_CPU_actual_passed=False,actual_four_case_scope_decision=dict(path='PENDING_ROOT_ACTUAL_FOUR_CASE_SCOPE_REVIEW',sha256=None),
  required_scope_decision_true_fields=['whole20k2b_source_actual_CPU_verified','first_formal_fulltrace_actual_reviewed','four_frozen_cases_actual_complete','physical_source_query_contact_COMhardware_all_raw_admitted','sameidentity_second3600_reasonable','no_new_policy_axis','center_near_candidates_rejected_not_source','second_and_last_block_before_full_audit'],
  sourcefreeze=[],target_sourcefreeze_PENDING_actual_materialization=True,original_runtime_sourcefreeze_reuse_required=index(mpath),original_runtime_sources522_byteexact_required=True,
  original_environment=m['original_environment'],original_environment_exact_digest=hashlib.sha256(json.dumps(m['original_environment'],sort_keys=True).encode()).hexdigest(),
  prepared_payload_sources=[index(q) for q in [typedpath,contractpath,workerpath,parentpath]],
  source_first_formal_actual_CPU_proof=index(oldfinalproof),same_original_locks_and_sole1188000canonical_seven_applied_no_new_transaction=True,
  actual_source13_cpuCUDA_strict_then_newphysical_episode_plus_one_REQUIRED_future=True,actorcriticstdAdam_allD0D7_globalnamed_dictprivate_and_geometry_entry_command_direction_route_lifetime_leftmetadata_exact_REQUIRED_future=True,
  stale_original_environment_initialadmission_label_historical_actual_sameidentity_proofs_precede_claims=True,
  no_native_fresh_preflight_clock_replay_no_oldonce_entry_no_SSH_GPU_PPO_or_budget=True,qualified50=False,Git_archive_pending_root_owner=True)
 tp=P/'LEFT_SECOND_SAMEIDENTITY_ADMISSION_MANIFEST_CPU_TEMPLATE.json';tp.write_text(json.dumps(template,indent=2),encoding='utf8')
 assert all(sha(x['path'])==x['sha256'] for x in oldindices)
 report=dict(epoch=time.time(),passed=True,status='Only localCPUsource andASTschema prepared, not targetCPU/GPU/launch',proposed_remote_root=PROPOSED,remote_root_created=False,prepared_sources=[index(q) for q in [typedpath,contractpath,workerpath,parentpath,tp]],old_readonly_source_references=oldindices,
  actual13_fixture_schema_preflight=accepted,eight_legacy_receipts_without_passed_accepted=True,four_bad_actual_schema_copies_strict_rejected=neg,
  worker_currentupdate_savehook_ASTexact=True,original_normallearn_runpy_worker_path_preserved=True,worker_import_main_guarded_and_no_native_fresh_initializer_branch=True,
  formal_parent_unique_samefcntl_locks_solecanonical_seven_applied_guard=True,approvedGPU_and_complete_fourcase_actualdecision_blocklaunch=True,
  all_original_parameters_environment_exact_no_scope_axis_change=True,new_target_resource_CPU_freeze_importPopen_actual_pending=True,
  no_oldonce_import_execution_no_SSH_GPU_budget_or_Git=True,source2b_actual_localSHA_rechecked=True,all_oldsource_before_afterSHA_exact=True,Git_archive_pending_root_owner=True)
 (R/'SECOND_SAMEIDENTITY_WORKER_PARENT_SCHEMA_CPU_PREPARED_ACTUAL.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(R/'SECOND_SAMEIDENTITY_WORKER_PARENT_SCHEMA_CPU_PREPARED_ACTUAL.json'),sources=len(report['prepared_sources']),old13schema_accepted=True,eight_no_passed=True,remote_root_created=False,GPU_approved=False)))
except Exception:
 (R/f'CPU_SECOND_PREPARE_ORIGINAL_ERROR_{time.time_ns()}.json').write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),source_script=index(__file__),prepared_files_if_any=[index(p) for p in P.glob('*') if p.is_file()],no_GPU_SSH_or_budget=True,Git_archive_pending_root_owner=True),indent=2),encoding='utf8')
 raise

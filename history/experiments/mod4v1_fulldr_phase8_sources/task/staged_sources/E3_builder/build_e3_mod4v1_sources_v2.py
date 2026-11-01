"""E3-only source derivation: no H1/jump mixed task, PT/SDK/SSH/learning or GO.

Refuses an existing output. Keeps E3's actual89D trainer/resume/bank/reward.
Reuses only generic source-cache, text-diff and boot-storage utilities.
"""
from pathlib import Path
import argparse, ast, difflib, hashlib, importlib.util, json, time, traceback

HERE = Path(__file__).resolve().parent
STAGED = HERE.parent
P = 'runtime/isaac/mod4/'
KIND = 'MOD4V1_E3_SELECTED43090_FULLD0D7_RECOVERY13_V1'
MODEL = dict(path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E3_PPO50_GAS400_2610v97/e3/adaptation/final_valid_update87.pt',
    SHA='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8',bytes=14715029,
    iteration=43090,Adam17=866060,LR=.0002562890625000001,prior_new_PPO_updates=87,
    metadata_only_not_opened_or_copied=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--asset-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve()
    if not out.is_relative_to(STAGED):raise ValueError('Output outside authorized staged_sources')
    if out.exists():raise FileExistsError('REFUSE_OVERWRITE_E3_OUTPUT: '+str(out))
    # These functions manipulate source strings/metadata only, never expert configs.
    utility_path=STAGED/'build_w35_mod4v1_sources.py'
    spec=importlib.util.spec_from_file_location('source_text_utilities_only',utility_path)
    utility=importlib.util.module_from_spec(spec);spec.loader.exec_module(utility)
    replace,J=utility.replace,utility.J
    def read(path,expected=None):
        text,ref=utility.raw_text(path,expected)
        return text.replace('\r\n','\n'),ref  # input raw bytes/SHA unchanged
    root=args.project_root.resolve();night=root/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
    prep=night/'E3_PPO50_gas400_source_preparation_20261028'
    old=prep/'runtime_candidate_v1'
    mod=old/'isaac/mod4';files={};refs=[];patch=[]
    freeze_text,fr=read(old/'reports/SOURCE_FREEZE.json');refs.append(fr);freeze=json.loads(freeze_text)['sha256']
    install_text,install_ref=read(night/'E3_97_GAS400_COMPLETE_RUNTIME_SOURCE_CPU_PREPARATION_V1/E3_COMPLETE_INSTALL_MANIFEST_V1.json','04e88211fa685523c3a9a0bd074ac69a5618baf55ffea67c1eab93f7bc436023');refs.append(install_ref);rows={r['relative']:r for r in json.loads(install_text)['files']}
    def source(name):
        row=rows[P+name];text,ref=read(Path(row['local_path']),row['SHA']);refs.append(ref);return text
    def emit(name,text,original=None):
        if name.endswith('.py'):ast.parse(text,filename=name)
        files[name]=text.encode('utf-8')
        if original is not None:patch.extend(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile='originalE3/'+name,tofile='newE3/'+name))
    worker0,wr=read(prep/'E3_PPO50_gas400_finite_worker_v1.py',rows['E3_PPO50_gas400_finite_worker_v1.py']['SHA']);refs.append(wr)
    trainer0=source('train_E3_fullstate_v1.py');flat0=source('scut_flat_rescue.py');health0=source('clock_training_health.py')
    manifest,mr=read(prep/'original_run_manifest.json','ad1d4681d85d18dde8a545dbf58fc2460173faf556b6102c96f5eef69c33e80f');refs.append(mr)
    cpu_path=night/'TWO97_NEW_E3_PPO_FORMAL_INITIAL_CPU_SOURCE_V1/reports/E3_97_NEW_FORMAL_INITIAL_WHOLE_CPU_ACTUAL_V1.json'
    cpu,cr=read(cpu_path,'b9f5af6b1677ed6835ede170a38822f618e695e3f11fda5e6492a9c7282883bf');refs.append(cr)
    old_contract,oc=read(Path(rows['runtime/assets/import_contract.json']['local_path']),utility.OLD_CONTRACT_SHA)
    new_contract,nc=read(args.asset_dir/'import_contract.json',utility.NEW_CONTRACT_SHA);refs.extend([oc,nc])
    deployment_contract,dep_ref=read(old/'train/deploy/contract_rm2025_later.json',rows['runtime/train/deploy/contract_rm2025_later.json']['SHA']);refs.append(dep_ref)
    diff=utility.contract_diff(json.loads(old_contract),json.loads(new_contract));files['MOD4V1_ASSET_DIFF.json']=J(diff)
    shared=STAGED/'W35_MOD4V1_SOURCE_V2_FINAL/runtime/isaac/mod4'
    # Shared files are ONLY generic loaders/guards; not W35/H1 environment/reward.
    cache,ca=read(shared/'source_cache208_v3.py');hook,hr=read(shared/'mod4v1_fresh_dr_guard.py');refs.extend([ca,hr])
    emit(P+'source_cache208_v3.py',cache);emit(P+'mod4v1_fresh_dr_guard.py',hook)

    # Keep each E3 helper's original ABI/import graph; change only selected-source
    # torch.load to exact-path cache, while own roundtrip/save loads remain normal.
    helpers=['sensor_resume_contract.py','feedback_delay_checkpoint.py','action_delay_checkpoint.py',
             'spring_pressure_checkpoint.py','gas_damping_checkpoint.py','chassis_pd_checkpoint.py','e3_fullstate_checkpoint_v1.py']
    for name in helpers:
        initial=source(name);text='from source_cache208_v3 import cached_load,cached_H\n'+initial.replace('torch.load(', 'cached_load(')
        if name=='sensor_resume_contract.py':
            text=replace(text,'hashlib.sha256(p.read_bytes()).hexdigest()','cached_H(p)')
        if name=='e3_fullstate_checkpoint_v1.py':
            text=replace(text,'hashlib.sha256(Path(path).read_bytes()).hexdigest()','cached_H(path)')
        emit(P+name,text,initial)

    flat=replace(flat0,'from gas400_reset_bank_exact_compatibility_v1 import require_exact_gas400_reset_bank',
                 'from mod4v1_e3_asset_compat import require_mod4v1_flat_reset_bank')
    flat=replace(flat,"require_exact_gas400_reset_bank(source,task.MOD4_ISAAC/'import_contract.json',raw,actual_contract_SHA=actual)",
                 "env._mod4v1_e3_bank_compatibility = require_mod4v1_flat_reset_bank(source,task.MOD4_ISAAC/'import_contract.json',raw,actual_contract_SHA=actual)")
    emit(P+'scut_flat_rescue.py',flat,flat0)
    compat='''"""E3-specific unchanged flat133/height-filter74 reset bank with new nominal."""
from pathlib import Path
import hashlib,json,os
from mod4v1_fresh_dr_guard import read_asset_identity
from gas400_reset_bank_exact_compatibility_v1 import BANK_SHA,BANK_BYTES,OLD_CONTRACT_SHA,pose_gas_ranges

def require(value,message):
 if not value:raise RuntimeError(message)

def require_mod4v1_flat_reset_bank(bank_path,new_contract_path,raw,*,actual_contract_SHA=None):
 bank_path=Path(bank_path).resolve();contract=Path(new_contract_path).resolve()
 require(bank_path==Path(__file__).resolve().parent/'reset_bank.json','Original adjacent E3 bank required')
 b=bank_path.read_bytes();require(len(b)==BANK_BYTES and hashlib.sha256(b).hexdigest()==BANK_SHA,'Original E3 bank bytes changed')
 require(json.loads(b)==raw and raw['contract_sha256']==OLD_CONTRACT_SHA,'Original E3 geometry producer identity')
 identity=read_asset_identity(contract.parent)
 require(contract==Path(identity.contract_path),'Actual new E3 contract path')
 require(actual_contract_SHA==identity.contract_sha256,'Caller must identify new contract, not old517')
 diff=json.loads((Path(os.environ['MOD4V1_E3_JOB_ROOT'])/'MOD4V1_ASSET_DIFF.json').read_bytes())
 require(diff['new_contract_SHA']==identity.contract_sha256 and diff['new_USD_SHA']==identity.usd_sha256,'Declared new model DIFF')
 require(set(diff['changed_body_names'])=={'chassis','left_shin','right_shin'} and diff['contract_geometry_unchanged'],'Only declared mass/COM/I changes reuse E3 geometric bank')
 ranges=pose_gas_ranges(raw,identity.contract)
 require(ranges['all_poses']==133 and ranges['original_height_filter_selected_poses']==74,'Original E3 height population, NOT W35 pose34')
 return dict(schema='mod4v1.E3.flat133.filtered74.bank_geometry.v1',new_USD_SHA=identity.usd_sha256,
  new_contract_SHA=identity.contract_sha256,original_bank_SHA=BANK_SHA,pose_ranges=ranges,
  original_filter_random_selector_q_root_writes_unchanged=True,authorized_changed_bodies=diff['changed_body_names'],
  no_old_four_scalar_pass_relabelled=True,actual_SDK_or_expert_adaptation_validated=False)
'''
    emit(P+'mod4v1_e3_asset_compat.py',compat)
    for unchanged_name in ('e3_recovery_runtime_v1.py','e3_public_recovery_phase_v1.py','e3_reset_bank_cache_v1.py'):
        original_E3=source(unchanged_name);emit(P+unchanged_name,original_E3)
    health=replace(health0,'closure_2mm_still_resets_only_this_environment=True,',
        'closure_episode_threshold_m=float(self.env.cfg.terminations.closure.params["threshold"]),\n             closure_10mm_still_resets_only_this_environment=float(self.env.cfg.terminations.closure.params["threshold"])==.01,')
    health=replace(health,'legacy_single_peak_2mm_pass=','historical_single_peak_2mm_diagnostic_only=')
    health=replace(health,'ordinary_task_thresholds_unchanged=True,','ordinary_task_thresholds_declared_by_new_cfg=True,')
    emit(P+'clock_training_health.py',health,health0)
    launcher,lr=read(root/'W35_FULL_RM70_EXPERT_NORMALIZATION_SOURCE_V208_20261031/source/launcher208.py');refs.append(lr)
    launcher=launcher.replace('MOD4_NEW208_JOB_ROOT','MOD4V1_E3_JOB_ROOT').replace('MOD4_W35_OWN_KIT_STORAGE_ROOT','MOD4V1_E3_KIT_STORAGE_ROOT').replace('NEW208','NEW_E3')
    emit(P+'launcher_mod4v1_e3.py',launcher)

    trainer=replace(trainer0,'from zonglin2_app_launcher import Zonglin2AppLauncher as AppLauncher', 'from launcher_mod4v1_e3 import IsolatedAppLauncher208 as AppLauncher')
    trainer=replace(trainer,'from e3_recovery_runtime_v1 import RecoveryEnv as Mod4Env',
        "from mod4v1_fresh_dr_guard import bind_before_task_import,verify_task_module,configure_new_task,FreshDRNominalGuard\nE3_IDENTITY=bind_before_task_import(os.environ['MOD4V1_E3_ASSET_DIR'])\nassert os.environ.get('OWN_E2_H1_KIND')=='E3_PUBLIC_RECOVERY'  # H1 branch is never enabled\nfrom e3_recovery_runtime_v1 import RecoveryEnv as Mod4Env")
    trainer=replace(trainer,'    cfg.seed = args.seed\n',
        '    cfg.seed = args.seed\n    verify_task_module(mod4_task,E3_IDENTITY)\n    previous_thresholds=dict(closure=cfg.terminations.closure.params["threshold"],mimic=cfg.terminations.mimic.params["threshold"])\n    cfg.terminations.closure.params["threshold"]=.01\n    cfg.terminations.mimic.params["threshold"]=.01\n    configure_new_task(cfg,E3_IDENTITY)\n    assert cfg.sim.physics is not None\n')
    trainer=replace(trainer,'    env = Mod4Env(cfg=cfg)\n','    env = Mod4Env(cfg=cfg)\n    env._mod4v1_historical_thresholds=previous_thresholds\n')
    trainer=replace(trainer,'        runner.load(warm)\n','        from source_cache208_v3 import runner_source_load_scope\n        with runner_source_load_scope():\n            runner.load(warm)\n')
    start=trainer.index('    if args.init_checkpoint:\n',trainer.index('def main()'))
    end=trainer.index('    from e3_command_checkpoint_v1 import install_e3_save_contract',start)
    restore=trainer[start:end]
    trainer=trainer[:start]+"    from mild_dr import tensor\n    nominal_guard=FreshDRNominalGuard(env,E3_IDENTITY,torch_module=torch,tensor_converter=tensor)\n    env._mod4v1_e3_nominal_guard=nominal_guard\n    with nominal_guard.around_original_fullstate_restore():\n"+''.join('    '+s if s.strip() else s for s in restore.splitlines(True))+"    Path(log_dir,'MOD4V1_E3_NOMINAL_RESTORE_ACTUAL.json').write_text(json.dumps(nominal_guard.receipt(),indent=2))\n"+trainer[end:]
    trainer=replace(trainer,'    def _sha256(path):\n','    def _sha256(path):\n        from source_cache208_v3 import cached_source_owns,cached_H\n        if cached_source_owns(path):return cached_H(path)\n')
    trainer=trainer.replace('manifest["source_map"]','manifest["historical_source_map"]')
    trainer=replace(trainer,'    manifest["src_sha256"] = snapshot',
        '    for name in ("train_mod4v1_e3.py","mod4v1_e3_protocol.py","mod4v1_e3_asset_compat.py","mod4v1_fresh_dr_guard.py","source_cache208_v3.py","launcher_mod4v1_e3.py"):\n        shutil.copy2(Path(__file__).parent/name,snapshot_dir/name);snapshot[name]=_sha256(Path(__file__).parent/name)\n    manifest["active_expert"]="E3_MOD4V1_RECOVERY13"\n    manifest["mod4v1_historical_thresholds"]=env._mod4v1_historical_thresholds\n    manifest["mod4v1_derivation_index"]=json.loads((Path(os.environ["MOD4V1_E3_JOB_ROOT"])/"MOD4V1_DERIVATION_INDEX.json").read_text())\n    manifest["D6_scope"]="original_gas_damping_not_all_joint_friction"\n    manifest["src_sha256"] = snapshot')
    emit(P+'train_mod4v1_e3.py',trainer,trainer0)

    proto,pr=read(shared/'mod4v1_w35_protocol.py');refs.append(pr)
    replacements={
     'MOD4V1_W35_LATEST32481_FULLD0D7_RM70_V2':KIND,
     '2d0bc7b87c30f2f1d7b9130de2afddd554aab1fd8fe398a7e597ec7354d5650b':MODEL['SHA'],
     'SOURCE_BYTES = 17619333':'SOURCE_BYTES = 14715029',
     'ITER, ADAM, PRIOR_UPDATES = 32481, 651260, 77':'ITER, ADAM, PRIOR_UPDATES = 43090, 866060, 87',
     'LR = .0002562890625000001':'LR = .0002562890625000001',
     'e55cad0a6d1e70b99ed8b527a8d50241c4b30c59f4cdf449842889d2ee84e5fb':cr['SHA'],
     '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_QUALIFIED343E_CONTINUE327D_20261101_0712/w35_72/production/model_final_complete.pt':MODEL['path'],
     'historical_RM70_geometry_and_shared_material_proofs_exactly_reused':'historical_E3_recovery13_phase_bank_reward_RNG_scope_exactly_reused',
     'historical_RM70_scope_reuse_receipt_SHA':'historical_E3_recovery13_scope_reuse_receipt_SHA',
     'MOD4V1_W35_REVIEWABLE_SOURCE_ONLY_V2':'MOD4V1_E3_REVIEWABLE_SOURCE_ONLY_V1',
    }
    for x,y in replacements.items():
        if x not in proto:raise ValueError('Missing protocol metadata anchor: '+x)
        proto=proto.replace(x,y)
    proto=proto.replace('W35','E3').replace('w35','e2')
    if 'RM70' in proto:raise ValueError('E3 protocol retained RM70 scope')
    emit(P+'mod4v1_e3_protocol.py',proto)

    worker=replace(worker0,"SOURCE_SHA='59fa03e6e4d3ecf81153707082840df0347f6504508dd1a413dda7b714db6b75'","SOURCE_SHA='"+MODEL['SHA']+"'")
    worker=replace(worker,"KIND='MOD4_E3_PPO50_GAS400_FULLSTATE_SOURCE_CPU_V1'","KIND='"+KIND+"'")
    worker=utility.replace_function(worker,'guard_task_go',"""def guard_task_go(task,go,args,job):
 sys.path.insert(0,str(job/'runtime/isaac/mod4'))
 from mod4v1_e3_protocol import validate_new_job
 return validate_new_job(task,go,args,job)""")
    worker=replace(worker,"p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True);args=p.parse_args();job=args.job_root.resolve()",
        "p=argparse.ArgumentParser();p.add_argument('--mode',choices=('train',),required=True);p.add_argument('--num-envs',dest='num_envs',type=int,required=True);p.add_argument('--run-id',required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args();job=args.out.resolve().parent")
    worker=replace(worker,'guard_task_go(task,go)','guard_task_go(task,go,args,job)')
    worker=replace(worker,"OUT=job/'adaptation';OUT.mkdir()","OUT=job/'production';OUT.mkdir(exist_ok=False)")
    worker=replace(worker," assert H(job/'source/E3_86B89_N20K_PPO50_GAS400_SOURCE_NOT_GPU_ADMITTED.pt')==SOURCE_SHA\n",'')
    worker=replace(worker,"put(OUT/'E3_ORIGINAL_ENV_AND_EXACT_FORK_OVERRIDES.json'",
        "assert original['terrain']=='flat' and original['skill_tasks']=='all' and env['RM_JUMP_SCRIPT_PROB']=='0' and env['RM_MOD4_TERRAIN']=='flat'\n put(OUT/'E3_ORIGINAL_ENV_AND_EXACT_FORK_OVERRIDES.json'")
    worker=replace(worker," source=job/'source/E3_86B89_N20K_PPO50_GAS400_SOURCE_NOT_GPU_ADMITTED.pt';entry=mod/'train_E3_fullstate_v1.py'",
        " from mod4v1_fresh_dr_guard import bind_before_task_import\n identity=bind_before_task_import(task['asset_dir']);os.environ['MOD4V1_E3_ASSET_DIR']=task['asset_dir']\n os.environ['MOD4V1_E3_JOB_ROOT']=str(job)\n storage=job/'kit_isolation';storage.mkdir(exist_ok=False);(storage/'data').mkdir();(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')\n os.environ['MOD4V1_E3_KIT_STORAGE_ROOT']=str(storage)\n source=Path(task['model_path']);entry=mod/'train_mod4v1_e3.py'\n import torch\n from source_cache208_v3 import PinnedSource208,selected_source,cached_load\n cache=PinnedSource208(torch,source,SOURCE_SHA,14715029)\n assert cache.state['iter']==43090")
    worker=worker.replace("'E3_PPO50_GAS400_v1'","'E3_SELECTED43090_MOD4V1_WORLD_SIGNED4_FULLDR'").replace('6.666666666666667e-05','.0002562890625000001')
    worker=replace(worker,'only_asset_finite_stop_and_clock_migration=True','original_E3_task_reward_retained_with_explicit_new_asset_and_thresholds=True')
    worker=replace(worker,'Original per-env2mm reset and termination rules remain.','NEW task explicitly uses10mm per-env closure and.01rad mimic; source thresholds are historical.')
    worker=replace(worker,'assert required.issubset({x.name for x in receipts})','assert required.issubset({x.name for x in receipts})\n  for receipt in receipts:\n   if receipt.name in required:assert read(receipt).get("source_sha256",read(receipt).get("source_SHA"))==SOURCE_SHA')
    worker=replace(worker,'full=torch.load(source,map_location=\'cpu\',weights_only=False)','full=cache.state')
    worker=worker.replace('==43004','==43090').replace('{864320}','{866060}').replace('864320+20*updates','866060+20*updates')
    worker=replace(worker,"  from gas400_reset_bank_exact_compatibility_v1 import check_runtime_source\n  bankproof=check_runtime_source(mod);assert bankproof['passed'] and bankproof['pose_ranges']['original_height_filter_selected_poses']==74", "  bankproof=real._mod4v1_e3_bank_compatibility;assert bankproof['new_contract_SHA']==identity.contract_sha256 and bankproof['pose_ranges']['original_height_filter_selected_poses']==74\n  assert real._mod4v1_e3_nominal_guard.restore_completed")
    worker=replace(worker,"value['PPO50_gas400_adaptation']=full['PPO50_gas400_adaptation'];value['PPO50_gas400_new_updates']=updates",
        "value['historical_source_400N50_provenance']={k:full[k] for k in ('PPO50_gas400_adaptation','PPO50_gas400_new_updates','PPO50_gas400_clock') if k in full}\n   value['typed_E3_mod4v1_task']=dict(kind=KIND,source_SHA=SOURCE_SHA,source_iteration=43090,source_Adam17=866060,source_LR=.0002562890625000001,asset_USD_SHA=identity.usd_sha256,asset_contract_SHA=identity.contract_sha256,task='original_E3_public_recovery13',closure_episode_m=.01,mimic_rad=.01,D6_scope='gas_damping_not_all_joint_friction')\n   value['actual_new_PPO_updates']=updates;value['iter']=43090+updates")
    worker=replace(worker,"value['PPO50_gas400_clock']", "value['mod4v1_E3_clock']")
    worker=replace(worker,"row=dict(epoch=time.time(),path=str(path),bytes=path.stat().st_size,SHA=H(path),new_updates=updates,Adam_step=next(iter(steps)),not_skill_qualified=True)",
        "row=dict(epoch=time.time(),path=str(path),bytes=path.stat().st_size,SHA=H(path),new_updates=updates,actual_new_PPO_updates=updates,saved_iteration=value['iter'],source_SHA=SOURCE_SHA,Adam_step=next(iter(steps)),Adam_min=min(steps),Adam_max=max(steps),not_skill_qualified=True)")
    worker=replace(worker,'obs=vec.get_observations();tick=real._integrated_contact.tick;',
        "obs=vec.get_observations();real._mod4v1_e3_nominal_guard.check_observations(obs);put(OUT/'MOD4V1_E3_NOMINAL_RESTORE_ACTUAL.json',real._mod4v1_e3_nominal_guard.receipt());tick=real._integrated_contact.tick;")
    worker=replace(worker,'try:runner.learn(num_learning_iterations=n,init_at_random_ep_len=True)',
        'runner.alg.learning_rate=runner.alg.optimizer.param_groups[0]["lr"]\n  runner.current_learning_iteration=43091  # next NEW update label; source43090 remains immutable\n  try:runner.learn(num_learning_iterations=n,init_at_random_ep_len=True)')
    worker=replace(worker,"try:ns['main']()","try:\n  with selected_source(cache):ns['main']()")
    worker=replace(worker,"put(OUT/'APP_CLOSING.json',dict(epoch=time.time()));",
        "put(OUT/'SOURCE_FINAL_READ_COUNTS.json',cache.receipt());put(OUT/'APP_CLOSING.json',dict(epoch=time.time()));")
    emit('worker_mod4v1_e3.py',worker,worker0)

    template,template_ref=read(STAGED/'E2_builder/build_e2_mod4v1_sources_v5.py');driver,driver_ref=read(HERE/'derive_e3_builder_v1.py');refs.extend([template_ref,driver_ref])
    prior,prior_ref=read(HERE/'build_e3_mod4v1_sources_v1.py');dependency_fix,dependency_fix_ref=read(HERE/'finalize_e3_contract_dependency_v2.py');refs.extend([prior_ref,dependency_fix_ref])
    launcher_row=rows['lib/zonglin2_app_launcher.py'];original_launcher,original_launcher_ref=read(Path(launcher_row['local_path']),launcher_row['SHA']);refs.append(original_launcher_ref)
    history=[]
    for file in sorted(HERE.glob('E3_CPU_GENERATION_ERROR_*.json')):
        error,error_ref=read(file);refs.append(error_ref);history.append(json.loads(error))
    files['E3_CPU_GENERATION_HISTORY.json']=J(dict(scope='CPU_SOURCE_ONLY',errors=history,historical_SOURCE_FREEZE_delivery_SHA='bbb71edefa122f37efe7a8fe0271ae987dc3741a33d5697464db73d8a382b00a',active_E3_complete_manifest_delivery_SHA=dep_ref['SHA'],frozen_history_not_rewritten=True))
    files['E3_FROZEN97_SCOPE_AND_GAPS.json']=J(dict(actual_producer_manifest=install_ref,environment='original_e3_recovery_runtime_v1.RecoveryEnv',recipe_count=13,recovery_bank_SHA='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83',recovery_bank_bytes=32022178,original_fixed_recovery_pose=34,original_phase_reward_private_command_RNG_retained=True,producer_effort_owner_field='UNDEFINED_OR_UNKNOWN_NOT_ADDED',historical_unimplemented_owner_plan_not_a_new_admission_gate=True,new_coverage_not_claimed=True,fullskill_and_complete_SuperMimic_gap_preserved=True,E3_PT_or_SDK_executed=False))
    files['SOURCE_DIFF.patch']=''.join(patch).encode('utf-8')
    files['REQUIRED_ROOT_INPUTS.json']=J(dict(utility.required_schema(proto),Task_identity_required_keys=['kind','num_envs','source_SHA','source_bytes','source_iteration','source_Adam_step','source_LR','source_prior_new_PPO_updates','model_path','saved_source_CPU_proof_SHA','asset_USD_SHA','asset_contract_SHA','closure_episode_m','mimic_rad','original_canonical_generation','canonical_path','source_read_purpose'],pinned_metadata_not_a_Task=dict(kind=KIND,source=MODEL,saved_source_CPU_proof_SHA=cr['SHA'],source_manifest_SHA=mr['SHA'],task='E3_PUBLIC_RECOVERY_NOT_H1jump_NOT_RM70',asset_USD_SHA=utility.NEW_USD_SHA,asset_contract_SHA=utility.NEW_CONTRACT_SHA,interface=[35,38,6],physics_dt=.0025,TGS=[32,4],policy_hz=50,feedback_hz=100,closure_episode_m=.01,mimic_rad=.01)))
    files['README.md']=b"""# E3 selected1cd -> MOD4v1 source-only overlay

Worker worker_mod4v1_e3.py --mode train --num-envs20000 --run-id ACTUAL --out NEW_JOB/production. Trainer runtime/isaac/mod4/train_mod4v1_e3.py is derived ONLY from original97 train_E3_fullstate_v1 and RecoveryEnv, not E0/H1/W35 environment.

Actual97 complete manifest04e88211... and selected CPUb9f5af6... pin source1cd/14715029/43090/866060/LR.0002562890625000001/prior87. Original E3_PUBLIC_RECOVERY shared variable OWN_E2_H1_KIND remains intentional. Source-cache original D0-D7 plus E3_public_recovery_state/phase/private command RNG, ONE original sensor reset, then original declared-fall placement/publish/age0 are preserved. No fake PhysX exact resume.

Unchanged original RecoveryPhase has13 recipes, original 7 state tensors and original reward masks/upright progress/stable credit/age progression. RecoveryEnv still uses original E3ResetBankCache: bank78af9fa4.../32022178, original joint permutation/q30/fixedpick34, all25200 original points and13 rotations/cache mutation guards. Base flat133/filter74 random reset is a SEPARATE original helper, not a replacement for recovery resets. No raw NPZ/PT is opened by generation.

New2c/bae first import, explicit closure.01m and mimic.01rad/cfg.sim.physics; unchanged solver2.5ms/TGS32,4,50/100Hz, learned STD17Adam/fixedSI/original hardware envelope/reward. New nominal guard wraps the complete original restore. Old517 four-scalar base-bank admission is replaced by exact3body DIFF plus original range witnesses. D6=original gas damping, not all joint friction/hardware coverage.

Original producer has no specifically defined standalone effort-owner field in this join. That remains UNDEFINED/UNKNOWN; no new owner coverage is invented and later unimplemented owner plans are NOT a new admission gate. Preserve actual97 motor/control code and all historic fullskill/SuperMimic gaps. Static success is NOT E3 adaptation or graduation.

ROOT must install complete actual97 manifest runtime/lib/train-deploy/SOURCE_FREEZE/original manifests/bank dependencies into a NEW job before overlay, and provide fresh actual sourceSDK/asset/resource/privateEX/shared-finite/current original owner/budget/Ready/TaskGO. This generator creates NO Task/GO/actual pass. Source PT is metadata only; the runtime cache later allows one physical selected byte/hash/decode with original logical callers and own roundtrips.

Old source labels remain historical. New saved iteration labels start43091, saved iter43090+newupdates/Adam866060+20*newupdates, without an extra optimizer step. Original misleading Native34 receipt filename has24 controls; do not interpret it as34 or extend the protocol. Original freeze/error/reader history remains intact. Parent owns actual execution/independent skill evaluation and Git archival.
"""
    generator=Path(__file__);refs.append(dict(path=str(utility_path),bytes=utility_path.stat().st_size,SHA=hashlib.sha256(utility_path.read_bytes()).hexdigest()))
    outputs=[dict(relative=k,bytes=len(v),SHA=hashlib.sha256(v).hexdigest()) for k,v in sorted(files.items())]
    idx=dict(kind='MOD4V1_E3_REVIEWABLE_SOURCE_ONLY_V1',source_model_metadata=MODEL,inputs=refs,outputs=outputs,
        generator=dict(path=str(generator),SHA=hashlib.sha256(generator.read_bytes()).hexdigest()),original_E3_runtime=str(old),
        selected_source_CPU_proof=cr,original_manifest=mr,source_PT_opens=0,target_SDK_or_learning_executed=False,Task_GO_or_actual_pass_generated=False)
    files['MOD4V1_DERIVATION_INDEX.json']=J(idx)
    files['INSTALL_E3_BASE_AND_OVERLAY_SOURCE_MAP.json']=J(dict(kind='E3_SOURCE_ONLY_NOT_INSTALL_RECEIPT',original_runtime_root=str(old),
        original_remote_job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E3_PPO50_GAS400_2610v97/e2',
        base_source_freeze_historical=fr,original_complete_install_manifest=install_ref,base_files=[r for k,r in rows.items() if (k.startswith('runtime/') or k.startswith('lib/')) and Path(k).suffix.lower() not in ('.pt','.pth')],
        extra_base_required_files=[dict(relative='original_run_manifest.json',**mr),dict(relative='runtime/reports/SOURCE_FREEZE.json',**fr),dict(relative='runtime/train/deploy/contract_rm2025_later.json',**dep_ref)],
        original_run_manifest=mr,overlays=[dict(relative=k,bytes=len(v),SHA=hashlib.sha256(v).hexdigest()) for k,v in sorted(files.items())],
        model_metadata_only=MODEL,ROOT_complete_new_asset_and_dependencies_required=True))
    out.mkdir(parents=True,exist_ok=False)
    for name,raw in files.items():
        dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('xb') as stream:stream.write(raw)
    print(json.dumps(dict(status='E3_SOURCE_ONLY_GENERATED_NOT_EXECUTED',path=str(out),files=len(files),python_files=sum(k.endswith('.py') for k in files),PT_opens=0,SDK_SSH_training_budget=False),indent=2))


if __name__=='__main__':
    try:main()
    except BaseException:
        error_path=HERE/('E3_CPU_GENERATION_ERROR_'+str(time.time_ns())+'.json')
        error_path.write_text(json.dumps(dict(kind='E3_CPU_SOURCE_GENERATION_FAILURE_NOT_SDK',error=traceback.format_exc(),PT_or_SDK_or_training=False),indent=2),encoding='utf-8')
        raise

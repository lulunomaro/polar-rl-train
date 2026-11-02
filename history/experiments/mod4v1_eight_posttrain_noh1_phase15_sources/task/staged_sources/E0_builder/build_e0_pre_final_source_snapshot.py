"""E0-only source derivation: no H1/jump mixed task, PT/SDK/SSH/learning or GO.

Refuses an existing output. Keeps E0's actual89D trainer/resume/bank/reward.
Reuses only generic source-cache, text-diff and boot-storage utilities.
"""
from pathlib import Path
import argparse, ast, difflib, hashlib, importlib.util, json

HERE = Path(__file__).resolve().parent
STAGED = HERE.parent
P = 'runtime/isaac/mod4/'
KIND = 'MOD4V1_E0_SELECTED31984_FULLD0D7_FLAT_V1'
MODEL = dict(path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89d/e0/adaptation/final_valid_update82.pt',
    SHA='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a',bytes=14031973,
    iteration=31984,Adam17=641200,LR=.00038443359375000017,prior_new_PPO_updates=82,
    metadata_only_not_opened_or_copied=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--asset-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve()
    if not out.is_relative_to(STAGED):raise ValueError('Output outside authorized staged_sources')
    if out.exists():raise FileExistsError('REFUSE_OVERWRITE_E0_OUTPUT: '+str(out))
    # These functions manipulate source strings/metadata only, never expert configs.
    utility_path=STAGED/'build_w35_mod4v1_sources.py'
    spec=importlib.util.spec_from_file_location('source_text_utilities_only',utility_path)
    utility=importlib.util.module_from_spec(spec);spec.loader.exec_module(utility)
    read,replace,J=utility.raw_text,utility.replace,utility.J
    root=args.project_root.resolve();night=root/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
    old=night/'night_frozen_experts_PPO50_gas400_adaptation_20261027/E0_runtime50_gas400_candidate_v1'
    mod=old/'isaac/mod4';files={};refs=[];patch=[]
    freeze_text,fr=read(old/'reports/SOURCE_FREEZE.json');refs.append(fr);freeze=json.loads(freeze_text)['sha256']
    def source(name):
        text,ref=read(mod/name,freeze['isaac/mod4/'+name]);refs.append(ref);return text
    def emit(name,text,original=None):
        if name.endswith('.py'):ast.parse(text,filename=name)
        files[name]=text.encode('utf-8')
        if original is not None:patch.extend(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile='originalE0/'+name,tofile='newE0/'+name))
    worker0,wr=read(night/'E0_PPO50_gas400_logger_presave_V5_source_candidate_20261027/E0_PPO50_gas400_finite_worker_v5_writer_before_presave.py');refs.append(wr)
    trainer0=source('train_chassis_pd_resume_ppo.py');flat0=source('scut_flat_rescue.py');health0=source('clock_training_health.py')
    manifest,mr=read(night/'night_frozen_experts_PPO50_gas400_adaptation_20261027/E0_original_run_manifest_frozen_v1.json','1dbde5972c65baf8842bc82024fe7ddfd6393d73a51137cc9880ed6310ff1af1');refs.append(mr)
    cpu_path=root/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89D_20261027/reports/E0_89D_FORMAL_FINAL_WHOLE_INITIAL_CPU_REVIEW_ACTUAL_V2.json'
    cpu,cr=read(cpu_path);refs.append(cr)
    old_contract,oc=read(old/'assets/import_contract.json',utility.OLD_CONTRACT_SHA)
    new_contract,nc=read(args.asset_dir/'import_contract.json',utility.NEW_CONTRACT_SHA);refs.extend([oc,nc])
    deployment_contract,dep_ref=read(old/'train/deploy/contract_rm2025_later.json',freeze.get('train/deploy/contract_rm2025_later.json'));refs.append(dep_ref)
    diff=utility.contract_diff(json.loads(old_contract),json.loads(new_contract));files['MOD4V1_ASSET_DIFF.json']=J(diff)
    shared=STAGED/'W35_MOD4V1_SOURCE_V2_FINAL/runtime/isaac/mod4'
    # Shared files are ONLY generic loaders/guards; not W35/H1 environment/reward.
    cache,ca=read(shared/'source_cache208_v3.py');hook,hr=read(shared/'mod4v1_fresh_dr_guard.py');refs.extend([ca,hr])
    emit(P+'source_cache208_v3.py',cache);emit(P+'mod4v1_fresh_dr_guard.py',hook)

    # Keep each E0 helper's original ABI/import graph; change only selected-source
    # torch.load to exact-path cache, while own roundtrip/save loads remain normal.
    helpers=['sensor_resume_contract.py','feedback_delay_checkpoint.py','action_delay_checkpoint.py',
             'spring_pressure_checkpoint.py','gas_damping_checkpoint.py','chassis_pd_checkpoint.py']
    for name in helpers:
        initial=source(name);text='from source_cache208_v3 import cached_load,cached_H\n'+initial.replace('torch.load(', 'cached_load(')
        if name=='sensor_resume_contract.py':
            text=replace(text,'hashlib.sha256(p.read_bytes()).hexdigest()','cached_H(p)')
        emit(P+name,text,initial)

    flat=replace(flat0,'from gas400_reset_bank_exact_compatibility_v1 import require_exact_gas400_reset_bank',
                 'from mod4v1_e0_asset_compat import require_mod4v1_flat_reset_bank')
    flat=replace(flat,"env._gas400_reset_bank_compatibility_receipt = require_exact_gas400_reset_bank(",
                 "env._mod4v1_e0_bank_compatibility = require_mod4v1_flat_reset_bank(")
    emit(P+'scut_flat_rescue.py',flat,flat0)
    compat='''"""E0-specific unchanged flat133/height-filter74 reset bank with new nominal."""
from pathlib import Path
import hashlib,json,os
from mod4v1_fresh_dr_guard import read_asset_identity
from gas400_reset_bank_exact_compatibility_v1 import BANK_SHA,BANK_BYTES,OLD_CONTRACT_SHA,pose_gas_ranges

def require(value,message):
 if not value:raise RuntimeError(message)

def require_mod4v1_flat_reset_bank(bank_path,new_contract_path,raw,*,actual_contract_SHA=None):
 bank_path=Path(bank_path).resolve();contract=Path(new_contract_path).resolve()
 require(bank_path==Path(__file__).resolve().parent/'reset_bank.json','Original adjacent E0 bank required')
 b=bank_path.read_bytes();require(len(b)==BANK_BYTES and hashlib.sha256(b).hexdigest()==BANK_SHA,'Original E0 bank bytes changed')
 require(json.loads(b)==raw and raw['contract_sha256']==OLD_CONTRACT_SHA,'Original E0 geometry producer identity')
 identity=read_asset_identity(contract.parent)
 require(contract==Path(identity.contract_path),'Actual new E0 contract path')
 require(actual_contract_SHA==identity.contract_sha256,'Caller must identify new contract, not old517')
 diff=json.loads((Path(os.environ['MOD4V1_E0_JOB_ROOT'])/'MOD4V1_ASSET_DIFF.json').read_bytes())
 require(diff['new_contract_SHA']==identity.contract_sha256 and diff['new_USD_SHA']==identity.usd_sha256,'Declared new model DIFF')
 require(set(diff['changed_body_names'])=={'chassis','left_shin','right_shin'} and diff['contract_geometry_unchanged'],'Only declared mass/COM/I changes reuse E0 geometric bank')
 ranges=pose_gas_ranges(raw,identity.contract)
 require(ranges['all_poses']==133 and ranges['original_height_filter_selected_poses']==74,'Original E0 height population, NOT W35 pose34')
 return dict(schema='mod4v1.E0.flat133.filtered74.bank_geometry.v1',new_USD_SHA=identity.usd_sha256,
  new_contract_SHA=identity.contract_sha256,original_bank_SHA=BANK_SHA,pose_ranges=ranges,
  original_filter_random_selector_q_root_writes_unchanged=True,authorized_changed_bodies=diff['changed_body_names'],
  no_old_four_scalar_pass_relabelled=True,actual_SDK_or_expert_adaptation_validated=False)
'''
    emit(P+'mod4v1_e0_asset_compat.py',compat)
    health=replace(health0,'closure_2mm_still_resets_only_this_environment=True,',
        'closure_episode_threshold_m=float(self.env.cfg.terminations.closure.params["threshold"]),\n             closure_10mm_still_resets_only_this_environment=float(self.env.cfg.terminations.closure.params["threshold"])==.01,')
    health=replace(health,'legacy_single_peak_2mm_pass=','historical_single_peak_2mm_diagnostic_only=')
    health=replace(health,'ordinary_task_thresholds_unchanged=True,','ordinary_task_thresholds_declared_by_new_cfg=True,')
    emit(P+'clock_training_health.py',health,health0)
    launcher,lr=read(root/'W35_FULL_RM70_EXPERT_NORMALIZATION_SOURCE_V208_20261031/source/launcher208.py');refs.append(lr)
    launcher=launcher.replace('MOD4_NEW208_JOB_ROOT','MOD4V1_E0_JOB_ROOT').replace('MOD4_W35_OWN_KIT_STORAGE_ROOT','MOD4V1_E0_KIT_STORAGE_ROOT').replace('NEW208','NEW_E0')
    emit(P+'launcher_mod4v1_e0.py',launcher)

    trainer=replace(trainer0,'from isaaclab.app import AppLauncher', 'from launcher_mod4v1_e0 import IsolatedAppLauncher208 as AppLauncher')
    trainer=replace(trainer,'from chassis_pd_training_env import ChassisPDMod4Env as Mod4Env',
        "from mod4v1_fresh_dr_guard import bind_before_task_import,verify_task_module,configure_new_task,FreshDRNominalGuard\nE0_IDENTITY=bind_before_task_import(os.environ['MOD4V1_E0_ASSET_DIR'])\nfrom chassis_pd_training_env import ChassisPDMod4Env as Mod4Env")
    trainer=replace(trainer,'    cfg.seed = args.seed\n',
        '    cfg.seed = args.seed\n    verify_task_module(mod4_task,E0_IDENTITY)\n    previous_thresholds=dict(closure=cfg.terminations.closure.params["threshold"],mimic=cfg.terminations.mimic.params["threshold"])\n    cfg.terminations.closure.params["threshold"]=.01\n    cfg.terminations.mimic.params["threshold"]=.01\n    configure_new_task(cfg,E0_IDENTITY)\n    assert cfg.sim.physics is not None\n')
    trainer=replace(trainer,'    env = Mod4Env(cfg=cfg)\n','    env = Mod4Env(cfg=cfg)\n    env._mod4v1_historical_thresholds=previous_thresholds\n')
    trainer=replace(trainer,'        runner.load(warm)\n','        from source_cache208_v3 import runner_source_load_scope\n        with runner_source_load_scope():\n            runner.load(warm)\n')
    start=trainer.index('    if args.init_checkpoint:\n',trainer.index('def main()'))
    end=trainer.index('    from chassis_pd_checkpoint import install_chassis_pd_save_contract',start)
    restore=trainer[start:end]
    trainer=trainer[:start]+"    from mild_dr import tensor\n    nominal_guard=FreshDRNominalGuard(env,E0_IDENTITY,torch_module=torch,tensor_converter=tensor)\n    env._mod4v1_e0_nominal_guard=nominal_guard\n    with nominal_guard.around_original_fullstate_restore():\n"+''.join('    '+s if s.strip() else s for s in restore.splitlines(True))+"    Path(log_dir,'MOD4V1_E0_NOMINAL_RESTORE_ACTUAL.json').write_text(json.dumps(nominal_guard.receipt(),indent=2))\n"+trainer[end:]
    trainer=replace(trainer,'    def _sha256(path):\n','    def _sha256(path):\n        from source_cache208_v3 import cached_source_owns,cached_H\n        if cached_source_owns(path):return cached_H(path)\n')
    trainer=trainer.replace('manifest["source_map"]','manifest["historical_source_map"]')
    trainer=replace(trainer,'    manifest["src_sha256"] = snapshot',
        '    for name in ("train_mod4v1_e0.py","mod4v1_e0_protocol.py","mod4v1_e0_asset_compat.py","mod4v1_fresh_dr_guard.py","source_cache208_v3.py","launcher_mod4v1_e0.py"):\n        shutil.copy2(Path(__file__).parent/name,snapshot_dir/name);snapshot[name]=_sha256(Path(__file__).parent/name)\n    manifest["active_expert"]="E0_MOD4V1_FLAT_STAND_RUN_PURE_WORLD"\n    manifest["mod4v1_historical_thresholds"]=env._mod4v1_historical_thresholds\n    manifest["mod4v1_derivation_index"]=json.loads((Path(os.environ["MOD4V1_E0_JOB_ROOT"])/"MOD4V1_DERIVATION_INDEX.json").read_text())\n    manifest["D6_scope"]="original_gas_damping_not_all_joint_friction"\n    manifest["src_sha256"] = snapshot')
    emit(P+'train_mod4v1_e0.py',trainer,trainer0)

    proto,pr=read(shared/'mod4v1_w35_protocol.py');refs.append(pr)
    replacements={
     'MOD4V1_W35_LATEST32481_FULLD0D7_RM70_V2':KIND,
     '2d0bc7b87c30f2f1d7b9130de2afddd554aab1fd8fe398a7e597ec7354d5650b':MODEL['SHA'],
     'SOURCE_BYTES = 17619333':'SOURCE_BYTES = 14031973',
     'ITER, ADAM, PRIOR_UPDATES = 32481, 651260, 77':'ITER, ADAM, PRIOR_UPDATES = 31984, 641200, 82',
     'LR = .0002562890625000001':'LR = .00038443359375000017',
     'e55cad0a6d1e70b99ed8b527a8d50241c4b30c59f4cdf449842889d2ee84e5fb':cr['SHA'],
     '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_QUALIFIED343E_CONTINUE227D_20261101_0712/w35_72/production/model_final_complete.pt':MODEL['path'],
     'historical_RM70_geometry_and_shared_material_proofs_exactly_reused':'historical_E0_flat_reset_command_and_DR_scope_exactly_reused',
     'historical_RM70_scope_reuse_receipt_SHA':'historical_E0_flat_scope_reuse_receipt_SHA',
     'MOD4V1_W35_REVIEWABLE_SOURCE_ONLY_V2':'MOD4V1_E0_REVIEWABLE_SOURCE_ONLY_V1',
    }
    for x,y in replacements.items():
        if x not in proto:raise ValueError('Missing protocol metadata anchor: '+x)
        proto=proto.replace(x,y)
    proto=proto.replace('W35','E0').replace('w35','e0')
    if 'RM70' in proto:raise ValueError('E0 protocol retained RM70 scope')
    emit(P+'mod4v1_e0_protocol.py',proto)

    worker=replace(worker0,"SOURCE_SHA='54f53453a3f793cea990f0608c0a2c3bd3e5d37aecf41bb8817691af5fea0371'","SOURCE_SHA='"+MODEL['SHA']+"'")
    worker=replace(worker,"KIND='MOD4_E0_PPO50_GAS400_FULLSTATE_SOURCE_CPU_V1'","KIND='"+KIND+"'")
    worker=utility.replace_function(worker,'guard_task_go',"""def guard_task_go(task,go,args,job):
 sys.path.insert(0,str(job/'runtime/isaac/mod4'))
 from mod4v1_e0_protocol import validate_new_job
 return validate_new_job(task,go,args,job)""")
    worker=replace(worker,"p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True);args=p.parse_args();job=args.job_root.resolve()",
        "p=argparse.ArgumentParser();p.add_argument('--mode',choices=('train',),required=True);p.add_argument('--num-envs',dest='num_envs',type=int,required=True);p.add_argument('--run-id',required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args();job=args.out.resolve().parent")
    worker=replace(worker,'guard_task_go(task,go)','guard_task_go(task,go,args,job)')
    worker=replace(worker,"OUT=job/'adaptation';OUT.mkdir()","OUT=job/'production';OUT.mkdir(exist_ok=False)")
    worker=replace(worker," assert H(job/'source/E0_N20K_PPO50_GAS400_SOURCE_NOT_GPU_ADMITTED.pt')==SOURCE_SHA\n",'')
    worker=replace(worker,"put(OUT/'E0_ORIGINAL_ENV_AND_EXACT_FORK_OVERRIDES.json'",
        "assert original['terrain']=='flat' and original['skill_tasks']=='all' and env['RM_JUMP_SCRIPT_PROB']=='0' and env['RM_MOD4_TERRAIN']=='flat'\n put(OUT/'E0_ORIGINAL_ENV_AND_EXACT_FORK_OVERRIDES.json'")
    worker=replace(worker," source=job/'source/E0_N20K_PPO50_GAS400_SOURCE_NOT_GPU_ADMITTED.pt';entry=mod/'train_chassis_pd_resume_ppo.py'",
        " from mod4v1_fresh_dr_guard import bind_before_task_import\n identity=bind_before_task_import(task['asset_dir']);os.environ['MOD4V1_E0_ASSET_DIR']=task['asset_dir']\n os.environ['MOD4V1_E0_JOB_ROOT']=str(job)\n storage=job/'kit_isolation';storage.mkdir(exist_ok=False);(storage/'data').mkdir();(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')\n os.environ['MOD4V1_E0_KIT_STORAGE_ROOT']=str(storage)\n source=Path(task['model_path']);entry=mod/'train_mod4v1_e0.py'\n import torch\n from source_cache208_v3 import PinnedSource208,selected_source,cached_load\n cache=PinnedSource208(torch,source,SOURCE_SHA,14031973)\n assert cache.state['iter']==31984")
    worker=worker.replace("'E0_PPO50_GAS400_v1'","'E0_SELECTED31984_MOD4V1_FLAT_FULLDR'")
    worker=replace(worker,'full=torch.load(source,map_location=\'cpu\',weights_only=False)','full=cache.state')
    worker=worker.replace('==31903','==31984').replace('{639560}','{641200}').replace('639560+20*updates','641200+20*updates')
    worker=replace(worker,"assert real._gas400_reset_bank_compatibility_receipt['passed']",
        "assert real._mod4v1_e0_bank_compatibility['new_contract_SHA']==identity.contract_sha256\n  assert real._mod4v1_e0_nominal_guard.restore_completed")
    worker=replace(worker,"value['PPO50_gas400_adaptation']=full['PPO50_gas400_adaptation'];value['PPO50_gas400_new_updates']=updates",
        "value['historical_source_400N50_provenance']={k:full[k] for k in ('PPO50_gas400_adaptation','PPO50_gas400_new_updates','PPO50_gas400_clock') if k in full}\n   value['typed_E0_mod4v1_task']=dict(kind=KIND,source_SHA=SOURCE_SHA,source_iteration=31984,source_Adam17=641200,source_LR=.00038443359375000017,asset_USD_SHA=identity.usd_sha256,asset_contract_SHA=identity.contract_sha256,task='original_E0_flat_stand_run_pure_world',closure_episode_m=.01,mimic_rad=.01,D6_scope='gas_damping_not_all_joint_friction')\n   value['actual_new_PPO_updates']=updates;value['iter']=31984+updates")
    worker=replace(worker,"value['PPO50_gas400_clock']", "value['mod4v1_E0_clock']")
    worker=replace(worker,"row=dict(epoch=time.time(),path=str(path),bytes=path.stat().st_size,SHA=H(path),new_updates=updates,Adam_step=next(iter(steps)),not_skill_qualified=True)",
        "row=dict(epoch=time.time(),path=str(path),bytes=path.stat().st_size,SHA=H(path),new_updates=updates,actual_new_PPO_updates=updates,saved_iteration=value['iter'],source_SHA=SOURCE_SHA,Adam_step=next(iter(steps)),Adam_min=min(steps),Adam_max=max(steps),not_skill_qualified=True)")
    worker=replace(worker,'obs=vec.get_observations();tick=real._integrated_contact.tick;',
        "obs=vec.get_observations();real._mod4v1_e0_nominal_guard.check_observations(obs);put(OUT/'MOD4V1_E0_NOMINAL_RESTORE_ACTUAL.json',real._mod4v1_e0_nominal_guard.receipt());tick=real._integrated_contact.tick;")
    worker=replace(worker,'try:runner.learn(num_learning_iterations=n,init_at_random_ep_len=True)',
        'runner.alg.learning_rate=runner.alg.optimizer.param_groups[0]["lr"]\n  runner.current_learning_iteration=31985  # next NEW update label; source31984 remains immutable\n  try:runner.learn(num_learning_iterations=n,init_at_random_ep_len=True)')
    worker=replace(worker,"try:ns['main']()","try:\n  with selected_source(cache):ns['main']()")
    worker=replace(worker,"put(OUT/'APP_CLOSING.json',dict(epoch=time.time()));",
        "put(OUT/'SOURCE_FINAL_READ_COUNTS.json',cache.receipt());put(OUT/'APP_CLOSING.json',dict(epoch=time.time()));")
    emit('worker_mod4v1_e0.py',worker,worker0)

    error_history,er=read(HERE/'E0_CPU_GENERATION_ERROR_01.json');failed_draft,dr=read(HERE/'build_e0_failed_indent_draft.py');refs.extend([er,dr]);files['CPU_GENERATION_HISTORY.json']=error_history.encode('utf-8')
    files['SOURCE_DIFF.patch']=''.join(patch).encode('utf-8')
    files['REQUIRED_ROOT_INPUTS.json']=J(dict(utility.required_schema(proto),pinned_metadata_not_a_Task=dict(kind=KIND,source=MODEL,saved_source_CPU_proof_SHA=cr['SHA'],source_manifest_SHA=mr['SHA'],task='E0_flat_stand_run_pure_world_NOT_H1jump_NOT_RM70',asset_USD_SHA=utility.NEW_USD_SHA,asset_contract_SHA=utility.NEW_CONTRACT_SHA,interface=[35,38,6],physics_dt=.0025,TGS=[32,4],policy_hz=50,feedback_hz=100,closure_episode_m=.01,mimic_rad=.01)))
    files['README.md']=b'''# E0 selected a92 -> MOD4v1 source-only overlay

Worker: worker_mod4v1_e0.py --mode train --num-envs 20000 --run-id ACTUAL --out NEW_JOB/production
Trainer: runtime/isaac/mod4/train_mod4v1_e0.py, derived from E0's own train_chassis_pd_resume_ppo.py, NOT qualified240/H1 mixed jump.

Original 89D flat/all commands retained: stand .1, pure .3, moving .2, world directional V=.5, signed spins; jump script probability0. Original flat reset133/height-filter74/random selector retained, never W35 pose34 or arena/terrain commands. All learning algorithms/rewards/hardware envelope/35,38,6/STD17Adam/SI/RNG queues remain original except declared new asset and .01m/.01rad cfg thresholds.

Root must create actual new Task/GO/Ready/owner/current canonical/resource/target SDK/asset admission from REQUIRED_ROOT_INPUTS. No actual passed receipt or authority writer is generated. All existing workers/assets/PT stay untouched. Source a92/14031973/iter31984/Adam641200/LR.00038443359375000017 is metadata only; exactly one runtime PinnedSource208 source byte-open/decode serves original logical helper restores and hashes.

Install ORIGINAL E0 runtime from INSTALL_E0_BASE_AND_OVERLAY_SOURCE_MAP first in a NEW job, including train/deploy/contract_rm2025_later.json, runtime reports/SOURCE_FREEZE.json, original reset_bank JSON and all original imported modules. Then overlay these NEW sources and the complete pinned MOD4v1 asset directory. Generic cache/identity/Kit isolation utilities are not an imported W35/H1 task. Empty F discovery placeholders are not runtime files.

New asset2c/contractbae bound before first task import; constructor-new nominals are guarded around the original ONE fullstate reset. Old E0 four-scalar bank admission is replaced by exact new identity/three-body JSON DIFF plus unchanged original bank gas-range133/filter74 witness. No old four-scalar pass is relabelled. D6=original gas damping, not all joint friction/hardware full coverage.

New saves use typed_E0_mod4v1_task and historical_source_400N50_provenance. Source iter31984/prior82 saved by old RSL labeling remains original; this NEW continuation labels first update31985 and each new saved iter=31984+actual_new_updates, with Adam=641200+20*actual_updates. No extra optimizer update is executed for that label normalization.

No PT, Torch/SDK, SSH, training or budget operation was performed by the generator. Actual target fullrestore/native24/readbacks and independent post-save replay/skill evaluation are still required. Source/CPU checks are not expert adaptation or graduation. ROOT archives all sources/failures and owns budget/locks/dispatch.
'''
    generator=Path(__file__);refs.append(dict(path=str(utility_path),bytes=utility_path.stat().st_size,SHA=hashlib.sha256(utility_path.read_bytes()).hexdigest()))
    outputs=[dict(relative=k,bytes=len(v),SHA=hashlib.sha256(v).hexdigest()) for k,v in sorted(files.items())]
    idx=dict(kind='MOD4V1_E0_REVIEWABLE_SOURCE_ONLY_V1',source_model_metadata=MODEL,inputs=refs,outputs=outputs,
        generator=dict(path=str(generator),SHA=hashlib.sha256(generator.read_bytes()).hexdigest()),original_E0_runtime=str(old),
        selected_source_CPU_proof=cr,original_manifest=mr,source_PT_opens=0,target_SDK_or_learning_executed=False,Task_GO_or_actual_pass_generated=False)
    files['MOD4V1_DERIVATION_INDEX.json']=J(idx)
    files['INSTALL_E0_BASE_AND_OVERLAY_SOURCE_MAP.json']=J(dict(kind='E0_SOURCE_ONLY_NOT_INSTALL_RECEIPT',original_runtime_root=str(old),
        original_remote_job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89d/e0',
        base_source_freeze=fr,base_files=[dict(relative='runtime/'+k,SHA=v,original_local_path=str(old/k)) for k,v in freeze.items()],
        extra_base_required_files=[dict(relative='original_run_manifest.json',**mr),dict(relative='runtime/reports/SOURCE_FREEZE.json',**fr),dict(relative='runtime/train/deploy/contract_rm2025_later.json',**dep_ref)],
        original_run_manifest=mr,overlays=[dict(relative=k,bytes=len(v),SHA=hashlib.sha256(v).hexdigest()) for k,v in sorted(files.items())],
        model_metadata_only=MODEL,ROOT_complete_new_asset_and_dependencies_required=True))
    out.mkdir(parents=True,exist_ok=False)
    for name,raw in files.items():
        dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('xb') as stream:stream.write(raw)
    print(json.dumps(dict(status='E0_SOURCE_ONLY_GENERATED_NOT_EXECUTED',path=str(out),files=len(files),python_files=sum(k.endswith('.py') for k in files),PT_opens=0,SDK_SSH_training_budget=False),indent=2))


if __name__=='__main__':main()

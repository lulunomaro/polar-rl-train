"""Independent W35 source-only branch; no model/NPZ read, GPU, SSH or writer."""
from pathlib import Path
import ast,hashlib,json,shutil,time

HERE=Path(__file__).resolve().parent;L=HERE.parent;W=L.parents[1]
HISTORY=L/'night_frozen_experts_PPO50_gas400_adaptation_20261027'
BASE_RUNTIME=HISTORY/'E0_runtime50_gas400_candidate_v1'
RESET=HISTORY/'W35_nearest250_reset_gas400_mutable_candidate_v2'
WORKER=L/'E0_PPO50_gas400_logger_presave_V5_source_candidate_20261027/E0_PPO50_gas400_finite_worker_v5_writer_before_presave.py'
ORIGINAL_MANIFEST=W/'MOD4_S4_LINUX_LEARNER_FULLSTATE_ADMISSION_20261015/actual_original_W35_run_manifest.json'
SOURCE_SHA='36825921fb3e4a368791be7802c8ff16977e899240ac21ed2c067b2287bb9393'
ORIGINAL_SHA='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
MANIFEST_SHA='0543b0c47c53e15da0d7d017693d2b69f7f6354ef088c3a1b8ed2b9cc56e2beb'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 runtime=HERE/'runtime_candidate_v1';assert not runtime.exists();shutil.copytree(BASE_RUNTIME,runtime)
 for name in ('e1_full_pose_reset.py','W35_gas400_exact_selected_reset_compatibility_v2.py'):
  shutil.copy2(RESET/name,runtime/'isaac/mod4'/name)
 freeze=runtime/'reports/SOURCE_FREEZE.json'
 mapping={p.relative_to(runtime).as_posix():H(p) for p in runtime.rglob('*') if p.is_file() and p!=freeze}
 freeze.write_text(json.dumps(dict(schema='mod4.W35.PPO50_gas400.runtime_source_freeze.v1',sha256=mapping,
  base_E0_50Hz_gas400_runtime_source_only=True,W35_reset_uses_exact_nearest250_NPZ_not_flat74=True),indent=2),encoding='utf8')
 s=WORKER.read_text('utf8');assert H(WORKER)=='ec8eba0365f0129b2799ef4e1ae7f3673beb585f87d4e25d2c36cf7bdb33b08c'
 s=s.replace('E0','W35')
 for a,b in [('b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8',ORIGINAL_SHA),
  ('54f53453a3f793cea990f0608c0a2c3bd3e5d37aecf41bb8817691af5fea0371',SOURCE_SHA),
  ('1dbde5972c65baf8842bc82024fe7ddfd6393d73a51137cc9880ed6310ff1af1',MANIFEST_SHA),
  ('train_chassis_pd_resume_ppo.py','train_e1_retention_named_owned_resume_ppo.py'),
  ("'--learning_rate','.00038443359375000017'","'--learning_rate','.00001'"),
  ('current_learning_iteration==31903','current_learning_iteration==32259'),
  ('639560','646800')]:
  assert a in s,a;s=s.replace(a,b)
 old="'GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json'}"
 new="'GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json'}"
 assert s.count(old)==1;s=s.replace(old,new)
 old="  assert real._gas400_reset_bank_compatibility_receipt['passed']"
 new="  assert len(real._w35_gas400_asset_compatibility['authorized_four_scalar_changes'])==4\n  assert real._w35_gas400_selected_bank_compatibility['selected_pose_index']==34\n  assert runner.alg.learning_rate==full['optimizer_state_dict']['param_groups'][0]['lr']==.00001\n  assert real.command_manager.get_term('twist')._dt==.02"
 assert s.count(old)==1;s=s.replace(old,new)
 old="original_actor9_critic8_STD_17Adam_LR_D1_D7_exact=True,receipts="
 new="original_actor9_critic8_STD_17Adam_LR_D1_D7_exact=True,actual_algorithm_learning_rate=float(runner.alg.learning_rate),W35_retained_command_and_G3_state_restored=True,receipts="
 assert s.count(old)==1;s=s.replace(old,new)
 target=HERE/'W35_PPO50_gas400_finite_worker_v1.py';assert not target.exists();target.write_bytes(s.encode());ast.parse(s)
 assert H(ORIGINAL_MANIFEST)==MANIFEST_SHA
 manifest=HERE/'W35_original_run_manifest_frozen_v1.json';assert not manifest.exists();shutil.copy2(ORIGINAL_MANIFEST,manifest)
 # Source/model/binary identities come from existing producer receipts only.
 source_report=HISTORY/'reports/ORIGINAL_N20K_PPO50_GAS400_SOURCE_CPU_ACTUAL_V1.json'
 source=json.loads(source_report.read_bytes())['sources']['W35']
 assert source['new_source']['SHA']==SOURCE_SHA
 bundle=W/'MOD4_S4_GATE_FIRST_FINAL_FROZEN35_20261015/payload/SOURCE_BUNDLE_V2_MANIFEST.json'
 old=json.loads(bundle.read_bytes())['file_rows'];deps=[]
 for relative,targetrel in [('runtime/assets/robot.usd','runtime/assets/source_700N/robot.usd'),('runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz','runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz')]:
  r=next(x for x in old if x['relative']==relative);deps.append(dict(local_path=str(bundle.parent/relative),installed_relative=targetrel,bytes=r['bytes'],SHA=r['sha256'],SHA_reused_not_rehashed=True))
 for p in runtime.rglob('*.py'):ast.parse(p.read_bytes())
 report=dict(attempt_id='W35_PPO50_GAS400_OWN_ORIGINAL_N20K_RUNTIME_WORKER_SOURCE_20261027_V1',epoch=time.time(),
  worker=dict(path=str(target),bytes=target.stat().st_size,SHA=H(target)),original_env_manifest=dict(path=str(manifest),SHA=MANIFEST_SHA),
  source_model_existing_metadata=source['new_source'],original_source_SHA=ORIGINAL_SHA,old_iteration=32259,old_Adam17_step=646800,
  constructor_and_optimizer_LR=.00001,first_work_statement_writer_None=True,original_D1_D7_STD_command_rng_and_terrain_state_required=True,
  distinct_source_SHA_required_not_obs_width_weight_mixing=True,original_actor35_critic38_unchanged=True,
  clock=dict(policy_hz=50,physics_dt_s=.0025,decimation=8,feedback_hz=100,contact_bin_s=.005,command_elapsed_uses_env_step_dt=True,resampling_seconds=[12,16],gamma=.9801,lam=.9025),
  runtime_files=[dict(relative=p.relative_to(runtime).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(runtime.rglob('*')) if p.is_file()],
  binary_dependencies=deps,binary_dependency_copy_fullSHA_receipt_required_before_actual_CPU_admission=True,
  original_retention_trace_save_path_and_all_prefix_behavior_unchanged=True,WM_transition_tap_not_present=True,
  planned_GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',actual_resource_admission_pending=True,actual_source_SDK_GPU_or_PPO=False,
  reader_errors=[dict(tool_chunk='7e40a1',error='Initial reader looked for E0 CPUadmissionV2 in controller root; actual frozen file is under night_frozen_experts. Corrected explicit path, no model or runtime operation.')],
  no_PT_normalizer_NPZ_binary_GPU_SDK_remote_or_ledger_read=True,Git_status='ordinary_supplement_existing89trial_pending_root')
 p=HERE/'W35_RUNTIME_AND_WORKER_SOURCE_CPU_PREPARED_V1.json';assert not p.exists();p.write_text(json.dumps(report,indent=2),encoding='utf8')
 print(json.dumps(dict(worker=report['worker'],source_model=source['new_source'],runtime_files=len(report['runtime_files']),source_only=True)))
if __name__=='__main__':main()

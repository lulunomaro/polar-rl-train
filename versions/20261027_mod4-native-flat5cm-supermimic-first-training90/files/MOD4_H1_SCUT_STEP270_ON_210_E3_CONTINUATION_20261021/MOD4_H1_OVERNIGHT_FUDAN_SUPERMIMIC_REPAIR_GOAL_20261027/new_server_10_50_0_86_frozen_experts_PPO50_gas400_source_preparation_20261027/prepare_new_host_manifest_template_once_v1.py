"""Local JSON/source only. No remote/probe/mkdir/model/GPU/SDK/ledger operation."""
from pathlib import Path
import ast,hashlib,importlib.util,json,time,traceback
HERE=Path(__file__).resolve().parent;OLD=HERE.parent/'W35_PPO50_gas400_source_preparation_20261027'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def emit(name,value):
 with (HERE/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def main():
 assert not (HERE/'INDEX.json').exists()
 old_index=OLD/'W35_FROZEN_MINIMUM_SOURCE_ADMISSION_INDEX_V1.json';old_manifest=OLD/'W35_COMPLETE_INSTALL_MANIFEST_V1.json'
 assert H(old_index)=='8242c696e93883382f3dc9378ccf5fbee9a7f8d63ada08c5966aa44b9f0c9b4c'
 assert H(old_manifest)=='80e0fc5508fe55f421ee938c0c55354bb1da43e8b77b668c55b1d99208084a55'
 frozen=json.loads(old_index.read_bytes());manifest=json.loads(old_manifest.read_bytes())
 source=HERE/'workspace_boundary_source_v1.py';sp=importlib.util.spec_from_file_location('new_host_boundary_source_only',source);b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
 prefix='staging/W35_frozen_minimum_v1';rows=[]
 for r in manifest['small_source_files']:
  relative=prefix+'/'+r['installed_relative'];b.relative_path(relative)
  rows.append(dict(source_path=r['local_path'],target_relative=relative,bytes=r['bytes'],SHA=r['SHA'],kind='frozen_small_source',source_SHA_reused_from_frozen_index=True))
 for r in [manifest['model'],*manifest['binary_dependencies']]:
  relative=prefix+'/'+r['installed_relative'];b.relative_path(relative)
  rows.append(dict(source_path=r.get('local_path',r.get('path')),target_relative=relative,bytes=r['bytes'],SHA=r['SHA'],kind='producer_indexed_binary_not_opened',source_SHA_reused_from_producer=True))
 assert len(rows)==465
 marker=dict(schema='mod4.robemo.frozen_experts.workspace.v1',host='10.50.0.86',username='robemo',authorized_root=b.ROOT,
  project='MOD4_frozen_experts_PPO50_gas400',first_payload_frozen_index_SHA=H(old_index),budget_writer_host='72',canonical_copied=False)
 emit('NEW_WORKSPACE_OWNER_MANIFEST_TEMPLATE_V1.json',dict(status='TEMPLATE_NOT_ON_REMOTE',relative_filename=b.MARKER,content=marker,
  publish_only_after_actual_created_now_receipt=True,exclusive_create_never_replace_existing=True))
 emit('W35_NEW_HOST_DEPLOYMENT_MANIFEST_TEMPLATE_V1.json',dict(schema='mod4.W35.new_host.deploy_template.v1',status='SOURCE_TEMPLATE_NOT_INSTALLED_OR_ADMITTED',
  host='10.50.0.86',username='robemo',authorized_root=b.ROOT,staging_relative=prefix,
  existing_root_requires_our_manifest=True,all_writes_resolved_inside_root=True,exclusive_new_paths_only=True,
  source_frozen_index=dict(path=str(old_index),SHA=H(old_index)),source_install_manifest=dict(path=str(old_manifest),SHA=H(old_manifest)),
  source_CPU_fixture=frozen['source_only_CPU_fixture'],model=dict(SHA=manifest['model']['SHA'],bytes=manifest['model']['bytes']),
  original_iteration=32259,original_Adam_states=17,original_Adam_step=646800,original_LR=.00001,
  clock=dict(policy_hz=50,physics_dt_s=.0025,decimation=8,feedback_hz=100,queue_us=20000,solver='TGS32/4',gamma=.9801,lam=.9025),
  W35_nearest250_pose34_and_original_bank_unchanged=True,source_worker_is_currently_4090_specific=True,
  actual_host=dict(OS=None,GPU_UUID=None,GPU_name=None,GPU_free_MiB=None,Python=None,SDK=None,durable_free_bytes=None),
  actual_source_SDK_CUDA_restore_native24_newPPO_and_schedule_pending=True,files=rows,
  no_source_PT_USD_NPZ_or_normalizer_reopened=True,no_CPU_proof_rerun=True,no_remote_GPU_or_GO=True,
  no_account_or_credentials_in_deployment=True))
 emit('FIRST_NEW_HOST_PROBE_REQUEST_SOURCE_ONLY_V1.json',dict(status='REQUEST_SOURCE_ONLY_NOT_EXECUTED',host='10.50.0.86',username='robemo',
  allowed_new_root=b.ROOT,credentials_owner='root_memory_stdin_only',hostkey_pin='PENDING_ACTUAL_NEW_HOST_EVIDENCE_NOT_OLD72_PIN',
  required_actual_fields=['OS_architecture','own_username_uid_gid','parent_and_root_requested_resolved_paths','root_exists_before_created_now_exists_after',
   'existing_workspace_marker_identity_if_any','parent_root_permissions','durable_free_bytes','RAM_available_bytes','known_Python_executable_and_version',
   'installed_distribution_metadata_torch_rsl_rl_isaaclab_isaacsim_without_import','GPU_UUID_name_total_free_utilization','compute_GPU_UUID_only_rows'],
  GPU_commands=[['nvidia-smi','--query-gpu=uuid,name,memory.total,memory.free,utilization.gpu','--format=csv,noheader,nounits'],
   ['nvidia-smi','--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits']],
  maximum_filesystem_mutation='one new mkdir /data/robemo/polar-rl-train only if absent and parent already authorized/resolved',
  forbid=['unknown_PID_argv_exe_queries','plain_nvidia_smi_process_table','GPU_or_torch_or_SDK_initialization','other_user_job_changes','any_overwrite_or_cleanup',
   'global_install_driver_apt_conda_profile_edit','secret_files_or_argv','second_SSH_finite_during_root_lease'],
  remote_probe_and_new_mkdir_owner='root_after_current_serial_finite_returns',actual_probe_pending=True))
 # Tiny NEW path-contract metadata checks only; no old W35 fixture or file I/O.
 assert b.relative_path(prefix+'/runtime/isaac/mod4/e1_full_pose_reset.py')
 rejected=[]
 for value in ('../x','/tmp/x','a/../../x','a\\b','','.'):
  try:b.relative_path(value)
  except ValueError:rejected.append(value)
  else:raise AssertionError('escape accepted')
 synthetic=dict(host='10.50.0.86',username='robemo',requested_root=b.ROOT,resolved_root=b.ROOT,exists_before=False,created_now=True,exists_after=True)
 assert b.classify_root_metadata(synthetic,marker)=='new_root_created_by_current_authorized_probe_metadata_only'
 bad=dict(synthetic,exists_before=True,existing_our_marker={'another_project':True})
 try:b.classify_root_metadata(bad,marker)
 except ValueError:pass
 else:raise AssertionError('foreign root overwrite admitted')
 env=b.filesystem_environment();assert env['CUDA_VISIBLE_DEVICES']==''
 for key,value in env.items():
  if key not in ('CUDA_VISIBLE_DEVICES','PYTHONDONTWRITEBYTECODE','PYTHONNOUSERSITE','PYTHONUNBUFFERED'):assert value.startswith(b.ROOT+'/')
 emit('NEW_SOURCE_PATH_CONTRACT_TINY_METADATA_CPU_ACTUAL_V1.json',dict(epoch=time.time(),passed=True,new_relative_path_escape_rejections=rejected,
  foreign_existing_workspace_rejected=True,synthetic_created_root_metadata_case_only=True,no_actual_root_probe_or_mkdir=True,
  no_old_W35_CPU_fixture_or_PT_normalizer_USD_NPZ_GPU_SDK_remote_or_ledger_read=True,
  current_environment_not_changed=True,all_returned_process_write_locations_inside_root=True,actual_target_ready=False))
 emit('WM_DOMAIN_AND_CAPACITY_COLLECTION_PLAN_V1.json',dict(status='PLAN_ONLY_NO_TRANSITION_TAP_OR_DATA',
  existing_E0_W35_checkpoint_is_not_WM_dataset=True,domains_must_not_mix=['old700_vs400_absolute_xi','MuJoCo_vs_IsaacLab','different_control_physics_clocks','foreign_or_imagined_vs_actual_MOD4'],
  required_fields=['backend_asset_gas_policy_source_SHAs','physics_dt_control_dt_decimation_feedback_clock','s127_or_explicit_reconstructable_state',
   'actual_clipped_ingress6','physical_applied_queue_action_and_torque','xi_actual_absolute_parameters','episode_reset_ID','done_term_truncation',
   'nextstate_BEFORE_autoreset','valid_complete_transition_mask'],
  capacity_lower_bound=dict(floats_per_transition=127+127+6+6+31,bytes_per_float=4,bytes_per_transition_before_metadata=1188,
   full_N20K_50Hz_transitions_per_s=1000000,minimum_full_bytes_per_hour=4276800000000,
   example128_env_minimum_bytes_per_hour=27371520000,not_measured_traffic=True,actual_budget_and_subset_pending_probe=True),
  tap_must_preserve_actions_outputs_RNG_errors_fullsave_retention=True,deterministic_stratification_no_training_RNG_draw=True,
  never_unbounded_raw_or_silent_deletion=True,collector_source_and_real_retention_cap_not_implemented=True))
 for p in HERE.glob('*.py'):ast.parse(p.read_bytes())
 files=[dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p)) for p in sorted(HERE.iterdir()) if p.is_file()]
 emit('INDEX.json',dict(epoch=time.time(),schema='mod4.newhost86.W35.source_preparation.frozen.v1',files=files,source_frozen=True,
  local_source_only=True,actual_new_host_probe_environment_GPU_deployment_restore_PPO_data_and_same72_schedule_pending=True,
  no_new_trial_or_tag=True,Git_status='ordinary_supplement_pending_root'))
 print(json.dumps(dict(index_SHA=H(HERE/'INDEX.json'),deployment_template_SHA=H(HERE/'W35_NEW_HOST_DEPLOYMENT_MANIFEST_TEMPLATE_V1.json'),indexed_files=len(rows),source_only=True,actual_target_ready=False)))
if __name__=='__main__':
 try:main()
 except BaseException:emit('NEW_HOST_SOURCE_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_remote_or_model_IO=True));raise

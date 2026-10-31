from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent;R=N/'reports'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
v=json.loads((R/'ACTUAL198_TARGET72_CPU_NATIVE64_ADMISSION_RETURNED.json').read_bytes());a=v['admission']
assert v['passed_execution'] and v['CPU_returncode']==v['GPU_returncode']==0 and v['all_own_children_waited'] and v['private_EX_released']
assert a['actual_native_controls']==8 and a['actual_physics_callbacks']==64 and a['actual_feedback_samples']==16 and not a['worker_errors'] and a['parent_error'] is None
f=json.loads((R/'ACTUAL198_ADMIT_ALL_SSH_CLOSED_SESSION_RESTORED.json').read_bytes());assert f['all_owned_SSH_closed'] and f['SESSION_restored'] and f['global_serial_control_client_lease']=='FREE'
identities={Path(row['path']).name:json.loads(row['UTF8']) for row in v['full_UTF8'] if row['path'].endswith('IDENTITY_BEFORE_WAIT.json')}
row=dict(epoch=time.time(),status='ACTUAL198_TARGET72_SOURCE_CPU_AND_NATIVE64_PASS_READY_FOR_ROOT197_UNIFIED_GO',
 admission=a,selected_GPU=a['selected_GPU'],private_lock=a['resource']['private_lock'],
 resource_is_admission_snapshot_only_not_reserved_or_continuous_alive=True,
 worker_script='run198_E0_JUMP72_400N50_worker.py',worker_GO_required_fields=['role_key=e0_72','run_id','source_model_SHA','literal_original_fudan_JUMP=True','max_parent_seconds3900','exit_headroom_seconds300','learning_started_epoch','save_deadline=GO+3600','nominal_end_epoch=GO+3900'],
 remote_job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_82_FUDAN_JUMP72_400N50_20261031v198/e0_72',
 source_model_GPU_loads_so_far=0,source_model_CPU_loads_so_far=0,actual_training_updates=0,
 actual_CUDA_E0_fullstate_restore_and_first_PPO_still_required=True,
 original_preexec_identity_snapshots=identities,identity_scope='Popen immediately observed /usr/bin/bash run-python.sh before exec. Do not relabel as later Python or continuous identity.',
 all_owned_CPU_GPU_children_waited_RC0=True,private_EX_released=True,all_control_SSH_closed=True,SESSION_restored=True,
 root_global_serial_lease_returned=True,no_child_owner_or_GO_or_canonical_write=True,
 actual_report_path=str(R/'ACTUAL198_TARGET72_CPU_NATIVE64_ADMISSION_RETURNED.json'),actual_report_SHA=H(R/'ACTUAL198_TARGET72_CPU_NATIVE64_ADMISSION_RETURNED.json'),
 next_only='Root reviews197 unified cohort and194 safe completion/newformalCPU, then grants new finite startup lease to this child; do not start standalone195 owner.')
with (R/'ACTUAL198_ADMISSION_READY_ROOT197_HANDOFF.json').open('x',encoding='utf8') as out:json.dump(row,out,indent=2,ensure_ascii=False)
print(json.dumps(dict(passed=True,selected_GPU=a['selected_GPU'],control_lease_returned=True,training_started=False)))

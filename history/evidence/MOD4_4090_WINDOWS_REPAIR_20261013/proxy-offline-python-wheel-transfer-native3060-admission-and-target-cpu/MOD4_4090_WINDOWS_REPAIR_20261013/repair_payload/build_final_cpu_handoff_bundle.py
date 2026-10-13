from pathlib import Path
import hashlib,json,time,zipfile,shutil
D=Path(__file__).parent
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
R=D/'reports/FIRSTOBS_LOGGER_DETACH_CPU_V2_FINAL_READINESS_ACTUAL.json';ready=json.loads(R.read_bytes());assert ready['passed_CPU_prepared']
for row in ready['executable_sources']:assert H(Path(row['path']))==row['sha256']
parse=json.loads((D/'reports/DEMAND_TASK_POWERSHELL_PARSE_CPU_ACTUAL.json').read_bytes());assert parse['passed'] and not parse['task_registration_or_start_executed']
files=['windows20k_fullstate_binding.py','left_head_offset_aware_migration_v3.py','windows4090_training_runtime.py','windows4090_probe_contract.py','windows4090_repair_worker.py','run_windows4090_stage_once.py','windows4090_demand_task_wrapper.ps1','register_windows4090_demand_task_once.ps1','EXECUTION_CONTRACT_CPU_PREPARED.md']
snap=D/'prepared_source_versions/final_CPU_readiness_before_any_GPU';assert not snap.exists();snap.mkdir()
rows=[]
for name in files:
 p=D/name;q=snap/name;shutil.copy2(p,q);assert H(p)==H(q);rows.append(dict(path=str(p),bytes=p.stat().st_size,sha256=H(p),exact_snapshot=str(q)))
package=D/'WINDOWS4090_REPAIR_EXECUTABLES_CPU_PREPARED_FINAL.zip';assert not package.exists()
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
 for name in files:z.write(D/name,'repair_payload/'+name)
 # Reports retain local input paths and SHAs; they are evidence, not a remotely
 # admitted manifest, lease, CPU candidate checkpoint or GPU stage receipt.
 for name in ['FIRSTOBS_LOGGER_DETACH_CPU_V2_FINAL_READINESS_ACTUAL.json','OFFSET_AWARE_V3_FULL20K_CPU_ACTUAL_REVIEW.json','OFFSET_AWARE_V3_EFFECTIVE_GRADIENT_FUNCTIONAL_CPU_V2_ACTUAL.json','DEMAND_TASK_POWERSHELL_PARSE_CPU_ACTUAL.json']:
  z.write(D/'reports'/name,'repair_payload/reports/'+name)
large=[]
for p in sorted(D.glob('*.pt')):large.append(dict(path=str(p),bytes=p.stat().st_size,sha256=H(p),CPU_fixture_not_actual_GPU_source=True))
receipt=dict(epoch=time.time(),passed_CPU_prepare_only=True,package=dict(path=str(package),bytes=package.stat().st_size,sha256=H(package)),executable_files=rows,source_donor_sha256='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a',source_donor_num_envs=20000,source107_and99_perenv_tensor_contract=True,normal_firstobs_and_RSL_age_draw_order_CPU_exact=True,logger_unique_original_learn_init_and_safe_finalize=True,all12_original_restore_then_offset_aware_init_once_then_strict_same_repaired=True,new_actual20k_offsets_default_q_native_query_DR_geometry_actor_probe_admission_pending=True,Windows_default_capacity_not_Linux_numerical_equivalence=True,demand_detach_no_registration_or_launch=True,first_formal3600saveevery2updates_guardian15s_STOP_after_save=True,no_localGPU_remoteSSH_ScheduledTask_API_installedSDK_or_canonical_write=True,large_actual_CPU_fixtures=large,all_original_failed_observers_source_snapshots_and_reports_retained=True,ordinary_Git_supplement_pending_root_after_stage114c0545=True)
p=D/'reports/FINAL_CPU_PREPARED_EXECUTABLE_HANDOFF_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(receipt,indent=2),encoding='utf8');print(json.dumps(dict(report=str(p),package=receipt['package'],executables=len(rows),GPU_started=False)))

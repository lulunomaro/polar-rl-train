"""Freeze local text evidence and summarize completed isolated CPU checks."""
import hashlib,json,time
from pathlib import Path

B=Path(__file__).resolve().parent
T=B.parents[1]
M4=T/'MOD4_MIXED_PRECISION_MISSING_HALF_RSL_V4_AFTER67_20261025'
R=B/'reports'


def record(path):
    path=Path(path);data=path.read_bytes()
    return dict(path=str(path),bytes=len(data),SHA=hashlib.sha256(data).hexdigest())


def main():
    out=R/'SAMPLING_OPTIMIZATION_SOURCE_AND_RESULTS_V1_ACTUAL.json'
    assert not out.exists(),'Never overwrite completed audit'
    npz=json.loads((R/'NPZ_CPU_MICROBENCH_V1_ACTUAL.json').read_text(encoding='utf8'))
    e3=json.loads((R/'E3_FIXED_RECIPE_SYNTHETIC_CPU_V1_ACTUAL.json').read_text(encoding='utf8'))
    assert npz['status']=='CPU_checks_passed_not_deployed'
    assert e3['status']=='CPU_synthetic_equality_passed_not_production_device_validation'
    evidence=[M4/'reports/ACTUAL_M4_MISSING_HALF_VS_M3_FP32_THROUGHPUT_CPU_SUMMARY.json',
              M4/'mixed_precision_step_benchmark_runtime_v9_missing_half.py']
    h=M4/'benchmark_closed_text/h1'
    names=['h1_production_control_prefix_trace_v1.py','h1_prefix_pair_retention_v1.py',
           'h1_step270_production_worker_v1.py','h1_precision_step_benchmark_worker_v1.py',
           'h1_step270_sdk_runtime_candidate.py','h1_step270_fullstate_checkpoint_candidate_uninstalled.py',
           'job0/runtime/isaac/mod4/h1_fullstate_environment_v1.py','job0/runtime/isaac/mod4/mod4_env.py',
           'job0/runtime/isaac/mod4/mild_dr.py','job0/runtime/isaac/mod4/spring_pressure_training_env.py',
           'job0/runtime/isaac/mod4/gas_damping_sdk_adapter.py','job0/runtime/isaac/mod4/chassis_com_pose_roundtrip_sdk_adapter.py',
           'job0/runtime/isaac/mod4/explicit_pd_sdk_adapter.py','job0/runtime/isaac/mod4/sensor_a0_runtime.py',
           'job0/runtime/isaac/mod4/feedback_delay_checkpoint.py','job0/runtime/isaac/mod4/action_delay_checkpoint.py',
           'job0/runtime/isaac/mod4/spring_pressure_checkpoint.py','job0/runtime/isaac/mod4/gas_damping_checkpoint.py',
           'job0/runtime/isaac/mod4/chassis_pd_checkpoint.py','job0/TASK.json',
           'job0/production/bf16/TIMING_CURRENT.json','job0/production/bf16/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json']
    evidence.extend(h/name for name in names)
    recovery=M4/'benchmark_closed_text/recovery'
    evidence.extend([recovery/'job0/runtime/isaac/mod4/e3_recovery_runtime_v1.py',recovery/'job0/TASK.json',
                     next((recovery/'job0/production/logs').glob('*/run_manifest.json'))])
    bankmeta=T/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025/payloads/recovery/job0/runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.json'
    evidence.append(bankmeta)
    summary=json.loads(evidence[0].read_text())
    baselines={slot:{'cycle_s':value['modes']['fp32']['measurements']['cycle_wall_s']['median'],
                     'collection_s':value['modes']['fp32']['measurements']['collection_s']['median'],
                     'sampling_phases':value['modes']['fp32']['sampling_phases_CPU_exclusive_wall']}
               for slot,value in summary['slots'].items()}
    task_sources={slot:{k:value[k] for k in ('source_SHA','source_Adamstep','source_filename','num_envs','seed','policy_hz')}
                  for slot in ('h1','recovery')
                  for value in [json.loads((M4/'benchmark_closed_text'/slot/'job0/TASK.json').read_text())]}
    prefix=json.loads((h/'job0/production/bf16/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').read_text())
    live_manifest=json.loads(evidence[-2].read_text())
    h1T=baselines['h1']['cycle_s']
    persist=next(p['seconds']['median'] for p in baselines['h1']['sampling_phases'] if p['phase']=='trace_compression_full_SHA_and_retention')
    inference=[]
    for dataset in npz['benchmarks']:
        for variant in ('helper_fieldwise_stack_level3','helper_fieldwise_stack_level1'):
            ratio=dataset['medians'][variant]['CPU_serialization_speed_factor_vs_original']
            for fraction in (.25,.5,1.):
                saving=persist*fraction*(1-1/ratio)
                inference.append(dict(dataset=dataset['dataset'],variant=variant,
                                      assumed_fraction_of_persist_accelerated=fraction,borrowed_CPU_speed_factor=ratio,
                                      inferred_cycle_speed_factor=h1T/(h1T-saving),inferred_saved_s=saving,
                                      explicitly_not_measured_training_gain=True,excludes_extra_disk_hash_retention_cost_from_larger_archive=True))
    report=dict(record_id='MOD4_SAMPLING_OPTIMIZATION_AUDIT_20261025_V1',epoch=time.time(),
                status='Local preparation complete, helpers unused, actual training gain unmeasured',
                scope='Existing closed M3/M4 source and text timing plus small selected derivative and independent synthetic CPU checks',
                source_evidence=[record(p) for p in evidence],actual_source_checkpoints=task_sources,
                source_checkpoint_bytes_not_opened=True,FP32_baselines_from_existing_closed_M3=baselines,
                closed_M4_cost_snapshot=summary['actual_original_cost_sumonce'],
                cost_not_recharged_by_CPU_work=True,canonical_or_budget_not_opened_or_written=True,
                actual_M4_H1_BF16_prefix_sizes_and_original_SHA=prefix['index'],
                actual_bank_SHA_from_existing_manifest=live_manifest['source_map']['isaac/mod4/MOD4_RESET_COLLISION_BANK.npz'],
                actual_bank_binary_not_read=True,bank_metadata=dict(poses=133,points_per_pose=25200),
                npz_CPU_results=npz['benchmarks'],e3_CPU_results=e3,
                Amdahl_scenarios_inference_only=inference,
                ideal_eliminate_entire_trace_phase_upper_speed_factor=h1T/(h1T-persist),
                ideal_trace_upper_bound_not_attainable_by_compression_only=True,
                immutable_constraints=['FP32 production policy/state and 17Adam','no missing frames/fields/preupdate/producerSHA/fulltext/errors',
                                       'same first1_latest2 complete-pair retention plus incomplete/current-failure protection',
                                       'original 25GiB admission and 8GiB saved-stop disk guards',
                                       '20000 environments, 2.5ms TGS32/4, H1 100Hzx4 and E3 50Hzx8',
                                       'same reset timing, D0-D7 independent RNG and setter order, all hardware and finite checks',
                                       'no change to runtime0ec7 / pending68 reward-only source'],
                no_remote_GPU_policy_physics_GUI_kill_or_Git=True,
                archive_status='All agent files pending root unified unique annotated-trial archive and remote verification',
                no_local_only_file_called_Git_recorded=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    # Index all own files before this new index (no recursive self-hash claim).
    owned=[record(p) for p in sorted(B.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
    (R/'OWN_ARTIFACT_INDEX_PENDING_GIT_V1.json').write_text(json.dumps(dict(epoch=time.time(),files=owned,
        synthetic_archives_only_in_memory_not_written=True,original_small_derived_NPZ_retained_at_source=True,
        no_raw_PT_NPZ_USD_or_ZIP_copied=True,Git_status='pending root archive',index_itself_not_self_hashed=True),indent=2),encoding='utf8')
    print(json.dumps(dict(report=str(out),files=len(owned),pending_Git=True)))


if __name__=='__main__':main()

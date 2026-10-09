"""Review actual timings, exact interfaces and limits; never approves main adoption."""
from pathlib import Path
import json,time,statistics,hashlib,math
D=Path(__file__).resolve().parent;R=D/'reports';read=lambda p:json.loads(p.read_text(encoding='utf8'))
sdk=read(R/'ACTUAL_SDK_ACCEPTED.json');pub=read(R/'COLLECTION_PUBLISHED.json');cur=read(R/'CURRENT_ACTUAL.json')
paired={}
for job in pub['jobs']:
 p=read(R/job/'probe.json');result=read(R/job/'result.json');complete=read(R/job/'complete.json')
 assert result['phase']==complete['phase']=='complete' and result['exit_code']==0 and not result['errors'] and not result['error_files']
 row=next(x for x in cur['jobs'] if x['job_id']==job)
 assert row['probe.json_bridge_byte_exact'] and row['result.json_bridge_byte_exact']
 v=p['D7_reset_performance_review'];assert v['actual_num_envs']==80 and v['actual_steps']==1500 and v['stress_selected_reset_calls']==145
 assert not p['nonfinite'] and p['max_mimic_after_grace_rad']<.01
 assert p['physical_action_delay_audit']['callback_counts']=={'legs':6000,'wheels':6000}
 assert p['physical_action_delay_audit']['application_formula_max_error']==0
 assert p['mild_initial_parameters']['actual_parameters_pass'] and p['mild_final_parameters']['actual_parameters_pass']
 times=v['step_seconds'][50:];assert len(times)==1450 and all(math.isfinite(x) and x>0 for x in times)
 variant=v['variant'];paired[variant]=dict(job=job,probe=p,result=result,proof=v,
    total_collection_seconds=sum(times),environment_policy_steps=80*len(times),
    measured_steps_per_second=80*len(times)/sum(times),mean_control_ms=1000*statistics.mean(times),
    reset_median_ms=1000*statistics.median(v['reset_seconds']),reset_total_seconds=sum(v['reset_seconds']),
    reset_calls=len(v['reset_seconds']),timed_region=v['timed_region'])
a,b=paired['baseline'],paired['optimized'];va,vb=a['proof'],b['proof']
assert a['result']['checkpoint']==b['result']['checkpoint'] and a['result']['seed']==b['result']['seed'] and a['result']['profile']==b['result']['profile']
initial_equal=va['initial']==vb['initial'];assert initial_equal,'Initial test conditions did not match'
def maxdiff(x,y):
 if isinstance(x,list):return max((maxdiff(a,b) for a,b in zip(x,y)),default=0.)
 return abs(x-y)
matches={k:va['final'][k]==vb['final'][k] for k in va['final']}
for k in ('group_state','global_CPU_RNG','global_CUDA_RNG','explicit_PD','control_tick'):assert matches[k],k
comparison=dict(initial_full_root_q_parameters_private_global_streams_exact=True,
    action_trace_bytes_exact=va['action_trace_sha256']==vb['action_trace_sha256'],final_field_exact=matches,
    final_full_root_max_abs_diff=maxdiff(va['final']['root'],vb['final']['root']),
    final_joint_q_max_abs_diff=maxdiff(va['final']['q'],vb['final']['q']),final_joint_qd_max_abs_diff=maxdiff(va['final']['qd'],vb['final']['qd']),
    same_actual_reset_size_sequence=va['reset_sizes']==vb['reset_sizes'],
    task_hardware_full_parameter_audits_and_callback_scope_unchanged=True,
    actual_apply_callbacks_per_group_each_run=6000,
    observed_closure_max_mm={k:1000*x['probe']['max_closure_after_grace_m'] for k,x in paired.items()},
    observed_mimic_max_rad={k:x['probe']['max_mimic_after_grace_rad'] for k,x in paired.items()},
    existing_strict_flags_retained={k:x['probe']['strict_pass'] for k,x in paired.items()})
master=D.parent/'polar-rl-train/history/plans/MOD4_MOE_MASTER_PLAN.md'
sha=hashlib.sha256(master.read_bytes()).hexdigest();assert sha=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
src={n:hashlib.sha256((D/'baseline'/n).read_bytes()).hexdigest() for n in cur['main_source_SHA']}
assert cur['main_source_SHA']==src,'Active training source changed from original frozen source'
v=dict(epoch=time.time(),master_SHA_unchanged=sha,human_authorization='能先不打扰主训练优化一下在3060主机上试一下优化效果吗',
    optimization='Reuse current/after COM backend reads and calculate normalized-double quaternion preservation only for written rows; keep full all-row expected backend-buffer checks',
    SDK={k:x for k,x in sdk.items() if k!='full_collection_benchmark_pending'},SDK_source_review_SHA=hashlib.sha256((R/'ACTUAL_SDK_ACCEPTED.json').read_bytes()).hexdigest(),actual_collection_completed=True,comparison=comparison,
    collection={k:{name:row[name] for name in ('job','total_collection_seconds','environment_policy_steps','measured_steps_per_second','mean_control_ms','reset_median_ms','reset_total_seconds','reset_calls','timed_region')} for k,row in paired.items()},
    collection_speed_ratio=b['measured_steps_per_second']/a['measured_steps_per_second'],
    collection_single_process_pair_only=True,overall_20k_speed_gain_not_established=True,
    reset_median_speed_ratio=a['reset_median_ms']/b['reset_median_ms'],
    collection_gpu_memory_sampled_mib={k:x['result']['observed_GPU_memory_mib'] for k,x in paired.items()},
    sampler_seconds=2,sampled_peak_not_continuous=True,
    actual_scope='3060: 10-env actual COM ABBA SDK and 80-env 1500-control forced-subset-reset frozen collection; no PPO',
    not_tested='4090 20000-env PPO throughput, alternate reset distributions, all terrain or sim-to-real',
    production_adopted=False,main_training_source_bytes_unchanged=True,main_training_and_canonical_write_transactions=0,
    main_actual_child=cur['main_actual'],main_phase=cur['main_state']['phase'],
    artifacts_SHA={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in D.glob('*.zip')},
    failed_reader_jobs_retained=['clk2500-closure-episode-d3-92-d7-com-reset-performance-sdk','clk2500-closure-episode-d3-92-d7-com-reset-rotation-performance-sdk'])
(R/'PERFORMANCE_REVIEW.json').write_text(json.dumps(v,indent=2),encoding='utf8')
report=(f"# Isolated D7 COM reset performance on 3060\n\n"
 f"The user authorized testing optimization on 3060 without disturbing main training. Main 4090 source remains byte-identical; no PPO or canonical write occurred in these tests. Master SHA {sha} remains unchanged.\n\n"
 f"The candidate shares existing COM readbacks and applies the existing normalized-double quaternion proof to the selected rows only. Full all-row backend/buffer/expected pose checks still run at every reset; original parameter and hardware audits remain. CPU corrupt/stale/unselected-row fixtures passed on actual target Torch.\n\n"
 f"Actual 10-env PhysX ABBA SDK: {json.dumps(sdk['microbench'])}. Raw quaternion byte matching: {sdk['raw_quaternion_bytes_pairwise_exact']}; physical rotations use the already accepted dtype-derived contract. First byte-equality and CPU/CUDA reader errors remain retained_failed, not GPU/production failures.\n\n"
 f"Actual 80-env frozen collection, matched source/seed/DR and 145 forced four-row resets, 1500 controls each. The measured region includes forced reset, command, frozen inference, trace copy and env.step with synchronized endpoints; first 50 controls excluded. Post-step diagnostic scoring, cold load/save/exit and PPO are excluded. Baseline {a['mean_control_ms']:.6f} ms/control, optimized {b['mean_control_ms']:.6f}; throughput ratio {v['collection_speed_ratio']:.6f}. Full reset median {a['reset_median_ms']:.6f}→{b['reset_median_ms']:.6f} ms.\n\n"
 f"Interface/state comparison: {json.dumps(comparison)}. These reset-stress results are not skill graduation or a prediction of 20000-env 4090 training speed. The optimization is not installed in main training.\n")
(R/'PERFORMANCE_REPORT.md').write_text(report,encoding='utf8')
print(json.dumps(v))

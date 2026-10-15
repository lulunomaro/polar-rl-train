"""Append a read-only performance diagnosis to the existing trial, once."""
from pathlib import Path
import importlib.util,json,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports'
BASE='26fb5528794ecb1a1aee53301feb9e41674f565d'
def main():
 s=importlib.util.spec_from_file_location('prior_throughput_append_pure',D/'append_current_throughput_snapshot_ordinary_once.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 assert m.git('rev-parse','HEAD')==BASE and not m.git('status','--porcelain')
 report=R/'THREE_GPU_SCALING_EFFICIENCY_INTERPRETATION_AND_LIMITS_CPU_ACTUAL.json';assert not report.exists()
 x=json.loads((R/'THREE_GPU_SCALING_FACTOR_CURRENT_READONLY_ACTUAL.json').read_bytes());h=json.loads((R/'SAME_CONTROL_HEALTH_THREE_RANK_PHASE_TIMESTAMPS_ACTUAL.json').read_bytes())
 d=x['derived'];rows=[v for n in h['nodes'] for v in n['rows']];same_host=[v for v in rows if v['rank'] in (1,2)]
 v=dict(epoch=time.time(),question='Why three GPU 55k versus human single GPU 30k envsteps/s?',measured=d,
  global_envs=60000,per_rank_envs=20000,controls_per_update=24,global_envsteps_per_update=1440000,
  hypothetical_ideal_envsteps_s=90000,hypothetical_ideal_iteration_s=16.0,
  extra_iteration_s_vs_hypothetical_matched_single=d['total']-16,
  global_rate_is_same_envstep_unit_not_physics_substep=True,
  installed_logger_collect_plus_learning_timer=True,
  learning_timer_includes=['GAE_returns','backward_optimizer','adaptive_KL','allreduce','rank_wait'],
  learning_seconds_are_not_pure_network_seconds=True,
  native_PPO_gradient_allreduces_per_update=20,
  observed_both_host_links_Mbps=1000,NCCL_cross_host_transport='socket with IB disabled',
  bandwidth_or_network_latency_not_measured=True,
  same_control_health_timestamp_observation=dict(control_steps=rows[0]['control_steps'],all_controls_same=h['same_control_steps'],cross_host_epoch_spread_s=h['epoch_spread_if_same'],same_host_rank1_rank2_epoch_spread_s=max(z['epoch'] for z in same_host)-min(z['epoch'] for z in same_host),
   caveat='Health write timestamps are phase observations, not CUDA/NCCL profiling; inter-host clock synchronization/offset has not been verified. Do not label the cross-host spread as measured communication or wait time.'),
  GPU_utilization_snapshot_caveat='Single instantaneous samples; source/target sampled roughly 11 seconds apart. Cannot infer mean utilization or compare source versus target at one phase.',
  CPU_NUMA_threads_caveat='Two own simulator ranks share host72 and both have full CPU affinity; no isolated causal benchmark or CPU/NUMA attribution.',
  human_single_30000_caveat='Human-stated baseline; identical task/source/DR/co-load and timing boundary not independently rebenchmarked.',
  conclusion='Approx 1.79x throughput and 59.6% parallel efficiency against stated single baseline. Synchronous same-PPO training has compute, synchronization and slow-rank waiting costs. The dominant individual cause is not yet isolated; do not blame all 12.6 seconds on network or other jobs.',
  original_readonly_path_lookup_miss=dict(action='Get-Content from repository cwd used a workspace-relative path',error='Path not found',corrected_read='Used workspace cwd to read existing report; no runtime or file changed'),
  no_runtime_edits_signals_restarts_benchmarks_or_other_process_actions=True,
  same_original_seven_hour_parent_and_canonical=True)
 report.write_text(json.dumps(v,indent=2),encoding='utf8')
 src=(D/'append_current_throughput_snapshot_ordinary_once.py').read_text(encoding='utf8')
 src=src.replace("BASE='5e9c0ca47bf4a34ffbd5e2912e6b3385deecafe5'",'BASE='+repr(BASE))
 src=src.replace("/'shared_PPO_throughput_live_question_actual_ordinary_v1'","/'three_GPU_scaling_efficiency_phase_and_link_readonly_actual_ordinary_v1'")
 src=src.replace("/'real_shared_update1_three_full_models_CPU_and_active_7h_ordinary_v1/REPORT_CAPTURE_INDEX.json'","/'shared_PPO_throughput_live_question_actual_ordinary_v1/REPORT_CAPTURE_INDEX.json'")
 src=src.replace('Append current shared-PPO throughput snapshot, installed logger units and wall-rate distinction','Append three-GPU scaling diagnosis, phase timings, link constraints and attribution limits')
 src=src.replace("if __name__=='__main__':","if __name__=='__unused__':")
 scope={'__file__':str(D/'append_current_throughput_snapshot_ordinary_once.py'),'__name__':'scaling_append_once_implementation'}
 exec(compile(src,str(Path(__file__)),'exec'),scope);scope['main']()
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('SCALING_READONLY_ORDINARY_APPEND_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(error=traceback.format_exc(),resume_existing_objects_no_duplicate_commit_record_tag_or_runtime=True),f,indent=2)
  raise

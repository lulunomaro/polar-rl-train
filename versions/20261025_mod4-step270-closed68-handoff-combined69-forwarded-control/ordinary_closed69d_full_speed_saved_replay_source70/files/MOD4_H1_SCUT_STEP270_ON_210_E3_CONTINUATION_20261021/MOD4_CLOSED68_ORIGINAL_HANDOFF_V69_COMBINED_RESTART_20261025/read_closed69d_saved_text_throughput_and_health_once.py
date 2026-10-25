"""After original69d closure/wholeCPU, compare saved RSL timing with already-saved68 baseline."""
from pathlib import Path
import json,time,traceback
from closed_window_throughput_text_cpu_reader_v1 import read_worker_log
D=Path(__file__).resolve().parent;T=D.parent;R=D/'reports';N=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V4_RESOURCE_V69_20261025'
try:
    proof=json.loads((N/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())
    assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled']
    before=json.loads((R/'CLOSED68_SAVED_LOG_FP32_THROUGHPUT_BASELINE_CPU_ACTUAL.json').read_bytes())
    out=dict(epoch=time.time(),scope='Actual closed69d vs closed68 original saved RSL text; same480000environment transitions/update; exclude first2 warmup updates in each',
             previous_baseline_report=str(R/'CLOSED68_SAVED_LOG_FP32_THROUGHPUT_BASELINE_CPU_ACTUAL.json'),models={},
             no_new_checkpoint_raw_GPU_or_remote_read=True,not_a_fixed_input_causal_benchmark=True,
             interpretation='Observed production throughput. Different stochastic trajectories/reset populations and policy source states can affect the result. CPU wall includes implicit GPU waits; not CUPTI kernel utilization. No step skill qualification from speed.')
    for key in ('h1','recovery'):
        root=N/'current_pair_closed_text'/key/'job0/production'
        now=read_worker_log(root.parent/'production_WORKER.log',proof['models'][key]['updates'])
        healths=list((root/'logs').glob('*/CLOCK_TRAINING_HEALTH.json'));assert len(healths)==1
        health=json.loads(healths[0].read_bytes())
        assert health['actual_physics_callbacks']==health['expected_physics_callbacks']
        assert not health['nonfinite_observed'] and health['unknown_task_reset_events']==health['integrity_task_reset_events']==0
        assert health['termination_reason_coverage_exact'] and health['stop_reason'] is None
        base=before['models'][key]
        ratio={name:now[name]['median']/base[name]['median'] for name in ('collection_envsteps_per_second','cycle_envsteps_per_second')}
        out['models'][key]=dict(current69=now,baseline68_summary={name:base[name] for name in ('collection_seconds','PPO_seconds','cycle_seconds','collection_envsteps_per_second','cycle_envsteps_per_second')},
                                observed_throughput_ratio=ratio,observed_throughput_percent_change={k:(v-1)*100 for k,v in ratio.items()},
                                health_path=str(healths[0]),health_actual=health,
                                final_current_episode_snapshot_only=proof['models'][key].get('H1_current_episode_snapshot'))
    with (R/'ACTUAL_CLOSED69D_VS68_PRODUCTION_THROUGHPUT_AND_HEALTH_TEXT_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:dict(updates=v['current69']['measured_updates'],collection_s=v['current69']['collection_seconds']['median'],cycle_envsteps_s=v['current69']['cycle_envsteps_per_second']['median'],observed_percent_change=v['observed_throughput_percent_change']) for k,v in out['models'].items()}))
except BaseException:
    with (R/'CLOSED69D_THROUGHPUT_HEALTH_READER_ORIGINAL_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),original_values_not_overwritten=True,no_training_action=True),f,indent=2)
    raise

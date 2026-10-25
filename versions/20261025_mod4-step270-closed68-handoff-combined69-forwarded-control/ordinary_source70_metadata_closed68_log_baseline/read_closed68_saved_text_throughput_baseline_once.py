"""Actual closed68 log baseline, for later same-scope69 comparison without a new benchmark."""
from pathlib import Path
import hashlib,json,time,traceback
from closed_window_throughput_text_cpu_reader_v1 import read_worker_log
D=Path(__file__).resolve().parent;T=D.parent;R=D/'reports';P=T/'H1_STEP270_REWARD_SAGITTAL_TUCK_V6A_RESOURCE_V68_20261025'
try:
    proof=json.loads((P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['original_canonical_cost_settled']
    result=dict(epoch=time.time(),scope='Closed68 original saved text, first2 updates excluded; no new inference/rollout or checkpoint/raw read',models={},
                source_window_original_owner_receipt_duration_bound_false_preserved=True,
                no_causal_acceleration_gain_claim=True,no_remote_GPU_checkpoint_or_raw_read=True)
    for key in ('h1','recovery'):
        path=P/'current_pair_closed_text'/key/'job0/production_WORKER.log'
        result['models'][key]=read_worker_log(path,proof['models'][key]['updates'])
    with (R/'CLOSED68_SAVED_LOG_FP32_THROUGHPUT_BASELINE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:{'measured_updates':v['measured_updates'],'collection_seconds_median':v['collection_seconds']['median'],'cycle_envsteps_s_median':v['cycle_envsteps_per_second']['median']} for k,v in result['models'].items()}))
except BaseException:
    with (R/'CLOSED68_SAVED_LOG_BASELINE_READER_ORIGINAL_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_new_model_or_training_action=True),f,indent=2)
    raise

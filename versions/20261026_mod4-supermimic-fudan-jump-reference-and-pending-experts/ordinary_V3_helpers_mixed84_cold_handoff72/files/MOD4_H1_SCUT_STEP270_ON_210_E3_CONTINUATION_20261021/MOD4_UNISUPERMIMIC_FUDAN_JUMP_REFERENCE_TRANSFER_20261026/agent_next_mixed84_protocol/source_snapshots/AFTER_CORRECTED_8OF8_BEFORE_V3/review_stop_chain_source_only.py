"""New source-only stop-chain review; no old once or save chain is executed."""
from pathlib import Path
import ast
import hashlib
import json
import time

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'agent_native_finalization_cpu/source_snapshots'
paths=[OLD/'h1_unisupermimic_step270_worker_v1.py',
       OLD/'train_H1_ground_prelaunch_fullstate_v2.py',
       OLD/'h1_step270_fullstate_checkpoint_candidate_uninstalled.py',
       OLD/'chassis_pd_checkpoint.py',OLD/'gas_damping_checkpoint.py',
       OLD/'spring_pressure_checkpoint.py',OLD/'action_delay_checkpoint.py',
       OLD/'feedback_delay_checkpoint.py',HERE/'source_snapshots/sensor_a0_runtime.py',
       OLD/'rescue_training.py',OLD/'bridge_v5_h1_supermimic_bridge_v1.py']
rows=[]
for path in paths:
    raw=path.read_bytes();ast.parse(raw)
    rows.append(dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
worker=paths[0].read_text('utf8')
assert 'rescue_training.learn=learn' in worker
assert worker.index('rescue_training.learn=learn') < worker.index("try:ns['main']()")
train=paths[1].read_text('utf8')
assert 'from rescue_training import learn as bounded_learn' in train
assert 'install_h1_save_contract as install_chassis_pd_save_contract' in train
for path in paths[2:9]:
    text=path.read_text('utf8')
    assert 'rescue_training' not in text and 'SavedStop' not in text
bridge=paths[-1].read_text('utf8')
assert "time.time() >= self.go['save_deadline']" in bridge
assert "(self.out / 'STOP_AFTER_SAVE.json').exists()" in bridge
assert 'raise OwnCompleteSavedStop()' in bridge
report=dict(epoch=time.time(),attempt_id='mixed84-captured-native-stop-chain-source-only',
            passed_source_review=True,actual82Q_cause='UNPROVEN',
            files=rows,
            supplied_native_entry_route='Worker replaces rescue_training.learn before train.main imports bounded_learn',
            physical_save_chain=['step270','chassis_PD','gas_damping','spring_pressure','action_delay',
                                 'feedback_delay','sensor_a0','original_RSL_save'],
            rescue_install_in_this_supplied_route=False,
            ordinary_native_deadline_inevitably_fails=False,
            source_only_expected_normal_stop='before_action raises OwnCompleteSavedStop; lifecycle attempts unchanged full physical chain then native verification/publication/manifest',
            additional_inner_rescue_wrapper='If installed by a different route, SavedStop may interrupt upper physical/task/native augmentation; explicit errors and retained stage, no bypass or complete-file assumption',
            narrow_outer_acknowledgment='No captured outer SavedStop-after-verified-native-publication wrapper exists. Therefore no new exception acknowledgment is justified. A future explicit outer wrapper would need a fresh same-invocation verified publication receipt; filename/existence/rc0/last old receipt are insufficient.',
            actual_trace_persist_save_manifest_IO_failure_not_attributed=True,
            prior_finalization_CPU_evidence='Reuse actual21/21 and preserved20/20 attempt reports; not rerun for this source review',
            no_model_checkpoint_content_or_runtime_or_GPU_or_remote_or_budget_or_Git_action=True,
            Git_status='PENDING_ROOT_PHASE_ARCHIVE')
path=HERE/'reports/CAPTURED_NATIVE_STOP_CHAIN_SOURCE_REVIEW_ACTUAL.json'
with path.open('x',encoding='utf8') as stream:json.dump(report,stream,indent=2)
print(json.dumps(dict(source_review_passed=True,rescue_install_in_supplied_route=False,
                      ordinary_deadline_not_inevitably_error=True,actual82Q_cause='UNPROVEN')))

"""Keep inherited task labels and execution contracts distinct; no live mutation."""
from pathlib import Path
import json,time
B=Path(__file__).resolve().parent;R=B/'reports'
task=json.loads((B/'payload_h1_native/job0/TASK.json').read_bytes());prep=json.loads((R/'CLOSED_H1_NEW_SOURCE_TARGET72_NATIVE_ONLY_PAYLOAD_AND_PARENT_CPU_PREPARED_ACTUAL.json').read_bytes());spec=prep['spec'];admission=json.loads((R/'LATEST_H1_NATIVE_ONLY_ACTUAL_OLD_FINAL_RESOURCE_FCNTL_NEW_ROOT_ADMISSION.json').read_bytes())
assert task['source_SHA']==spec['source_SHA'] and task['source_Adamstep']==spec['source_Adamstep']==644660 and spec['execution_backend']=='target72' and spec['GPU_UUID'].startswith('GPU-16828f91')
v=dict(epoch=time.time(),actual_stale_labels=dict(GPU_UUID=task['GPU_UUID'],exact_closed_source_updates=task['exact_closed_source_updates']),correct_reference=dict(actual_source_closed_updates=24,source_SHA=spec['source_SHA'],source_Adam644660=True,execution_backend=spec['execution_backend'],execution_GPU_UUID=spec['GPU_UUID']),old_labels_not_rewritten_in_live_files_or_PT=True,no_native_or_PPO_result_inferred_from_metadata_labels=True,actual_execution_resource_admission=admission,old_TASK_scope_and_false_preserved=True,next_prepared_TASK_should_distinguish_historical_source_labels_from_actual_execution=True)
with (R/'LATEST_H1_NATIVE_TASK_LEGACY_LABELS_AND_ACTUAL_EXECUTION_SOURCE_CPU_DIAGNOSIS.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
print(json.dumps(dict(actual_legacy_labels_retained=v['actual_stale_labels'],actual_source_updates24=True,no_runtime_mutation=True)))

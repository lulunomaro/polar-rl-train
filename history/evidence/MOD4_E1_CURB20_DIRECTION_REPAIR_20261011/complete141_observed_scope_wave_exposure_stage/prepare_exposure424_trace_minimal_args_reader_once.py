"""Preserve original SSH reader failure and reduce only read-only command arguments."""
from direction_io import *

p=D/'review_exposure424_full_training_trace_actual.py';raw=p.read_bytes();text=raw.decode('utf8')
anchor="repr(json.dumps(own))"
replacement="repr(json.dumps(dict(own_checkpoint={k:own['own_checkpoint'][k] for k in ('path','sha256')},source_SHA=own['source_SHA'],health={k:own['health'][k] for k in ('control_steps','actual_physics_callbacks','expected_physics_callbacks')})))"
assert text.count(anchor)==1
q=D/'review_exposure424_minimal_args_full_trace_actual.py';assert not q.exists();q.write_text(text.replace(anchor,replacement),encoding='utf8')
save('EXPOSURE424_TRACE_MINIMAL_ARGS_READER_PREPARED.json',dict(epoch=time.time(),old_source=str(p),old_SHA=H(raw),new_source=str(q),new_SHA=H(q.read_bytes()),original_10054_SSH_execution_request_error_retained=True,old_full_own_receipts_preserved_on_disk=True,only_remote_read_only_argument_payload_reduced=True,no_validator_or_geometry_or_physics_or_PPO_change=True,no_old_once_replayed=True))
print(json.dumps(dict(prepared=True,source=str(q))))

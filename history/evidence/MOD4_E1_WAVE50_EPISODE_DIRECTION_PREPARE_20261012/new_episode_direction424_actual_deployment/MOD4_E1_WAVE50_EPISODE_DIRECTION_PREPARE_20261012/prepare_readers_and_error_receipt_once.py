"""Retain preparation reader errors; future readers are prepared, never future passes."""
from pathlib import Path
import ast,json,time
D=Path(__file__).resolve().parent;W=D.parent
with (D/'reports/LOCAL_REFERENCE_READ_MISSING_PATH.json').open('x') as f:
 json.dump(dict(epoch=time.time(),path=str(W/'MOD4_E1_WAVE50_ENTRY_SECOND_BOUNDED_20261012/prepare_complete149_decision_direction_cpu_metadata_monitor_once.py'),error='Get-Content: path not found',read_only_reference_lookup=True,no_GPU_or_physics_failure=True),f,indent=2)
print(json.dumps(dict(saved_reference_reader_error=True)))

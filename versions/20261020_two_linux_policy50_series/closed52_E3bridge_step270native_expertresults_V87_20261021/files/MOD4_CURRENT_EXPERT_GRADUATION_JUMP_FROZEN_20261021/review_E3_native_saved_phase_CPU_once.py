from pathlib import Path
import json,time,traceback
from recovery_saved_rows_phase_cpu import audit
B=Path(__file__).resolve().parent;R=B/'reports'
try:
 value=dict(epoch=time.time(),**audit(B,'E3_native60_actual',60));(R/'E3_NATIVE60_ALL104_SAVED_PHASE_AND_SENSOR_CPU_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(value,indent=2));print(json.dumps(value))
except BaseException:
 (R/'E3_NATIVE60_SAVED_PHASE_CPU_ORIGINAL_ERROR.json').open('x',encoding='utf8').write(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True),indent=2));raise

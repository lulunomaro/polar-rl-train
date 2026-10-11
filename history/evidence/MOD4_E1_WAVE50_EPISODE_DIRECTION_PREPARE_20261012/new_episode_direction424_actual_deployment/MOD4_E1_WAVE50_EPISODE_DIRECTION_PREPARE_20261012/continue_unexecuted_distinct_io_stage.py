from pathlib import Path
import json,time
D=Path(__file__).resolve().parent
with (D/'reports/LOCAL_IO_NAME_COLLISION_REJECTION.json').open('x') as f:
 json.dump(dict(epoch=time.time(),source='stage_direction_target_cpu_once.py',error="AttributeError: inherited wave_io imported already-initializing local direction_io instead of CURB module",before_stage_boundary_root_upload_CPU_GPU=True,original_sources_retained=True),f,indent=2)
s=(D/'stage_direction_target_cpu_once.py').read_text().replace('from direction_io import *','from wave_direction_io import *')
exec(compile(s,'<distinct-io-unexecuted-stage>','exec'),dict(__file__=str(D/'stage_direction_target_cpu_once.py'),__name__='__main__'))

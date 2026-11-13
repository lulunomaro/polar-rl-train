from pathlib import Path
import sys,json,importlib.util
T=Path(__file__).resolve().parent
S=T.parent/'MOD4V3_STAIRS_MAX_HEIGHT_40M_20261113'
sys.path.insert(0,str(S))
_spec=importlib.util.spec_from_file_location('frozen_height_remote_access',S/'remote_run.py')
_module=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_module)
connect=_module.connect;execute=_module.execute
P=json.loads((T/'PLAN.json').read_text(encoding='utf8'));REMOTE=P['root'];R=T.parents[2]

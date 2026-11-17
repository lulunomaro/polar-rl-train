from pathlib import Path
import sys,importlib.util,json
T=Path(__file__).resolve().parent;R=T.parents[2];F=R/'sources/local/MOD4V3_SERIAL_TEACHER_FIXED200_40M_20261116'
spec=importlib.util.spec_from_file_location('prior_completed40m_remote_access',F/'remote_run.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
connect=module.connect;execute=module.execute;P=json.loads((T/'PLAN.json').read_text());REMOTE=P['root']

"""Original archive failed before capture/record; execute only the missing phase."""
from pathlib import Path
import importlib.util,json,subprocess
D=Path(__file__).resolve().parent;R=D/'reports';REPO=D.parent/'polar-rl-train'
assert json.loads((R/'S4_RETENTION_COMPLETE_S5_FIRST_CELL_MONITOR_TOML_UTF8_ACTUAL_VERIFIED.json').read_bytes())['passed']
errors=list(R.glob('S5_FIRST_MATCHED35_ARCHIVE_ORIGINAL_ERROR_*.json'));assert len(errors)==1
error=json.loads(errors[0].read_bytes())['error'];assert 'FileNotFoundError' in error and 'S4_RETENTION_COMPLETE_S5_FIRST_CELL_MONITOR_TOML_UTF8_ACTUAL_VERIFIED.json' in error
assert not (R/'S5_FIRST_MATCHED35_STAGE_GIT_STARTED_ACTUAL.json').exists()
assert not (REPO/'history/evidence'/D.name/'first_original35_three_way_actual').exists()
assert not (REPO/'history/experiments/20261015-s4-retention-complete-s5-single-w35-first-matched-cell.json').exists()
p=D/'archive_s5_first_matched35_and_s4_retention_complete_stage_once.py'
s=importlib.util.spec_from_file_location('unexecuted_S5_archive_phase_only',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
assert not m.cap.g('status','--porcelain') and not m.cap.g('tag','--list','*'+m.ID)
m.main()

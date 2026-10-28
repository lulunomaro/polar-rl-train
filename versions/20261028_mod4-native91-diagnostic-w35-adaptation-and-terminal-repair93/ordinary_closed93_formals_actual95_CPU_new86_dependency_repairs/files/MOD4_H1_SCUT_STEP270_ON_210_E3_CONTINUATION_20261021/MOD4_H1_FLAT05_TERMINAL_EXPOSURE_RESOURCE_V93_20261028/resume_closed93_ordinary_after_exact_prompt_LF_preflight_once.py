"""First actual capture after the original preflight stopped before any marker."""
from pathlib import Path
import runpy,json
N=Path(__file__).resolve().parent
assert not (N/'reports/ORDINARY_CLOSED93_ACTUAL95_CPU_NEW86_CAPTURE_STARTED_ACTUAL.json').exists()
assert not (N.parent.parent/'polar-rl-train/versions/20261028_mod4-native91-diagnostic-w35-adaptation-and-terminal-repair93/ordinary_closed93_formals_actual95_CPU_new86_dependency_repairs').exists()
original=N/'archive_closed93_formals_actual95_CPU_and_new86_repairs_ordinary_once.py'
definitions=runpy.run_path(str(original),run_name='unchanged_ordinary_definitions_only')
definitions['main']()

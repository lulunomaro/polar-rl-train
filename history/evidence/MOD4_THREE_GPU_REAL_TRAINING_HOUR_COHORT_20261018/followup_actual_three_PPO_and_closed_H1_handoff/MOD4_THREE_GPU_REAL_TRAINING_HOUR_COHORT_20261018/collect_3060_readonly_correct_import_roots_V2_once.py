"""Resolve the original transport module chain; V1 failed locally before any connection."""
from pathlib import Path
import sys,json,time,runpy
B=Path(__file__).resolve().parent;W=B.parent
for rel in ('MOD4_H1_TARGET72_CLOSED_FINAL_E3_FROZEN_REVIEW_20261017','MOD4_TWO72_CLOSED_SOURCES_HEALTHY_NEXT_BLOCK_20261017','MOD4_TWO72_E2_E3_HEALTHY_SAVED_CONTINUATIONS_20261017/curb275_final87_frozen3060_v1','MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'):sys.path.insert(0,str(W/rel))
with (B/'reports/CURRENT3060_V1_LOCAL_IMPORT_MISSING_BEFORE_CONNECTION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original_error="ModuleNotFoundError: No module named 'transport_249_exact_desktop_role_stdin_fresh2233_v7'",original_V1_source_retained=True,failed_before_any_remote_connection_or_started_report=True,V2_only_existing_transport_import_roots=True,no_GPU_Task_or_training_change=True),f,indent=2)
runpy.run_path(str(B/'collect_3060_current_eval_surface_readonly_once.py'),run_name='__main__')

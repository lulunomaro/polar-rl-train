"""Consume original unused closed68 collector after proven original writer closure; route-only binding."""
from pathlib import Path
import importlib.util,json,sys,time,traceback
D=Path(__file__).resolve().parent;T=D.parent;R=D/'reports'
try:
 proof=json.loads((R/'ORIGINAL68_AUTHENTICATED_TERMINALS_ORIGINAL_WRITER_CLOSED_ACTUAL.json').read_bytes())
 assert proof['original_owner_actual_out'] and proof['actual_finite_returned'] and proof['temporary_route_restored']
 n=T/'H1_STEP270_REWARD_SAGITTAL_TUCK_V6A_RESOURCE_V68_20261025'
 assert not(n/'reports/PAIR_CLOSING_COLLECTOR_STARTED_ACTUAL.json').exists()
 source=n/'collect_selected_pair_finals_unused_once.py';spec=importlib.util.spec_from_file_location('original_closed68_collector',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 m.d.t.connect=route.connect
 m.main()
except BaseException:
 with (R/'CLOSED68_ORIGINAL_UNUSED_COLLECTOR_FORWARD_ROUTE_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_account_write_or_replay=True),f,indent=2)
 raise

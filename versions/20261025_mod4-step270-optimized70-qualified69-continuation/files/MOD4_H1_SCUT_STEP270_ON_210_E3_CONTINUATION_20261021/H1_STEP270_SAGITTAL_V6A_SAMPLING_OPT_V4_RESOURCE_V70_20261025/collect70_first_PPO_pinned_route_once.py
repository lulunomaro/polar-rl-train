"""New70 first-GO/PPO exact own identities; original bounded reader and pinned route."""
from pathlib import Path
import json,runpy,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
try:
 assert (R/'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').is_file() and not (R/'PAIR_FIRST_METADATA_STARTED_ACTUAL.json').exists()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 d.t.connect=route.connect
 runpy.run_path(str(N/'collect_selected_pair_first_PPO_unused_once.py'),run_name='__main__')
except BaseException:
 with (R/'SAME_OPTIMIZED70_FIRST_PPO_FORWARD_ROUTE_ORIGINAL_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_retry_hotpatch_refund=True),f,indent=2)
 raise

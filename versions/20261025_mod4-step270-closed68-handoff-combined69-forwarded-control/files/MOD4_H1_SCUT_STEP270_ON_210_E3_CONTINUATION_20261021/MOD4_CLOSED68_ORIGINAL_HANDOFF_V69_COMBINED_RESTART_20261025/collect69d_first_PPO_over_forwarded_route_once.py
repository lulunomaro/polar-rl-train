"""Consume original unused69d first-PPO reader with exact forwarded original-host binding."""
from pathlib import Path
import json,runpy,sys,time,traceback
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;R=D/'reports';N=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V4_RESOURCE_V69_20261025'
try:
 assert (N/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').is_file() and not(N/'reports/PAIR_FIRST_METADATA_STARTED_ACTUAL.json').exists()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 d.t.connect=route.connect
 runpy.run_path(str(N/'collect_selected_pair_first_PPO_unused_once.py'),run_name='__main__')
except BaseException:
 with (R/'COMBINED69D_FIRST_PPO_FORWARD_ROUTE_ORIGINAL_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_retry_or_hotpatch_or_refund=True),f,indent=2)
 raise

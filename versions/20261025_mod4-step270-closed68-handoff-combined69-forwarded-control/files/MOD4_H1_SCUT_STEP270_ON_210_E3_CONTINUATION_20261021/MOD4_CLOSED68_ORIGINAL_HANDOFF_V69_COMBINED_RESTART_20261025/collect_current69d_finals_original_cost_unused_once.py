"""Unused until original actual nominal-end <=900 gate. Route binding only; original collector."""
from pathlib import Path
import importlib.util,json,sys,time,traceback
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;R=D/'reports';N=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V4_RESOURCE_V69_20261025'
try:
 proof=json.loads((N/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes());assert proof['passed'] and proof['actual_finite_returned']
 assert max(x['nominal_end_epoch'] for x in proof['source210']['current']['go'].values())-time.time()<=900
 assert not(N/'reports/PAIR_CLOSING_COLLECTOR_STARTED_ACTUAL.json').exists()
 source=N/'collect_selected_pair_finals_unused_once.py';sp=importlib.util.spec_from_file_location('original_current69d_final_collector',source);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 m.d.t.connect=route.connect;m.main()
except BaseException:
 with (R/('CURRENT69D_CLOSING_COLLECTOR_FORWARD_ROUTE_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_replay_refund_account_write=True),f,indent=2)
 raise

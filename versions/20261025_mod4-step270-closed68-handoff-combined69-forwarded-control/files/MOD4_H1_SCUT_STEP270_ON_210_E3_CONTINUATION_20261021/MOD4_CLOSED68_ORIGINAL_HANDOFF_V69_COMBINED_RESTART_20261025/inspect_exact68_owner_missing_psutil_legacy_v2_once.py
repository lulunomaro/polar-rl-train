"""Missing210 result only; installed psutil uses Process.connections, preserve original error."""
from pathlib import Path
import ast, hashlib, json, os, sys, time, traceback
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;R=D/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
put('EXACT68_OWNER_HANDOFF_MISSING210_V2_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv))
try:
 assert (R/'EXACT68_OWNER_HANDOFF_CAPABILITIES_ORIGINAL_ERROR_ACTUAL.json').is_file()
 assert (R/'EXACT68_E3_FRESH_TERMINAL_AND_OWN_OUT_ACTUAL.json').is_file()
 source=D/'inspect_exact68_original_owner_handoff_capabilities_once.py'
 tree=ast.parse(source.read_text('utf8'));code=next(x.value.value for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(k,ast.Name) and k.id=='H1' for k in x.targets))
 needle="p.net_connections(kind='tcp')";assert code.count(needle)==1;code=code.replace(needle,"p.connections(kind='tcp')",1)
 n=T/'H1_STEP270_REWARD_SAGITTAL_TUCK_V6A_RESOURCE_V68_20261025';q=json.loads((n/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());meta=json.loads((n/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes())
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 c=route.connect()
 try:value=d.code(c,route.PY,code,dict(q=q,identities={k:meta['source210'][k] for k in ('H1_node','H1_worker')}),timeout=30)
 finally:c.close()
 put('EXACT68_OWNER_HANDOFF_MISSING210_V2_RETURNED_ACTUAL.json',dict(epoch=time.time(),source210=value,E3_original_fresh_receipt_reused_no_second72_read=True,exact_single_ABI_change=needle+' -> connections',remote_code_SHA=hashlib.sha256(code.encode()).hexdigest(),actual_finite_returned=True))
 print(json.dumps({k:value[k] for k in ['owner_listeners','owner_endpoint_TCP_only','own_owner_mem_read_access','sudo_noninteractive_own_owner_mem_access','canonical_remaining_snapshot']},ensure_ascii=False))
except BaseException:
 put('EXACT68_OWNER_HANDOFF_MISSING210_V2_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_canonical_write=True));raise

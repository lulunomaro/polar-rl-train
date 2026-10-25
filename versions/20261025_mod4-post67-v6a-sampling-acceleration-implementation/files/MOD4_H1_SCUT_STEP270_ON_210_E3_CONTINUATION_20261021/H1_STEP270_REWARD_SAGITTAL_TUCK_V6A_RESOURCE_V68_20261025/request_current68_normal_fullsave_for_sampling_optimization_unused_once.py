"""One exact current68 normal full-save request, no signal/account changes."""
from pathlib import Path
import importlib.util,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
import deploy_two50_reconciled_original_writer_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r"""
from pathlib import Path
import json,os,psutil,time
q=v['q'];key=v['key'];root=Path(q['roots'][key]);expected=v['worker'];out=root/'job0/production'
assert root.is_absolute() and out.resolve().is_relative_to(root.resolve()) and out.is_dir()
go=json.loads((root/'job0/GO_PRODUCTION.json').read_bytes());assert go['run_id']==q['run_id'] and go['source_SHA']==q['sources'][key]['SHA']
result=dict(epoch=time.time(),key=key,root=str(root),run_id=q['run_id'],no_signal_hotpatch_or_account_write=True)
if (root/'NODE_TERMINAL_ACTUAL.json').is_file():
 row=json.loads((root/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row']
 assert row['terminal_all_own_children_waited'] and row['returncode']==0 and row['final']['passed']
 result.update(already_complete_terminal=True,normal_save_request_written=False)
else:
 p=psutil.Process(expected['pid']);assert p.create_time()==expected['creation'] and p.exe()==expected['exe'] and p.cmdline()==expected['argv']
 assert str(root/v['script']) in p.cmdline()
 if key=='h1':
  C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
  c=json.loads(C.read_bytes());a=c['active_segment'];assert a['owner_parent_pid']==q['owner_identity']['pid']
  assert c['authorized_training_seconds']==2268000 and len(c['budget_extensions'])==9
 stop=out/'STOP_AFTER_SAVE.json';assert not stop.exists()
 value=dict(epoch=time.time(),reason='Human authorized lossless sampling optimization implementation: complete current update, full model and runtime save, SDKclose and childwait before new root',run_id=q['run_id'],source_SHA=go['source_SHA'],no_signal=True,no_budget_change=True)
 with stop.open('x',encoding='utf8') as f:json.dump(value,f,indent=2);f.flush();os.fsync(f.fileno())
 result.update(normal_save_request_written=True,path=str(stop),exact_worker=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline()),request=value)
print(json.dumps(result))
"""
try:
 stage=T/'MOD4_SAMPLING_THROUGHPUT_OPTIMIZATION_PREPARATION_20261025'
 ready=json.loads((stage/'reports/OPTIMIZED_NEXT69_IMPLEMENTATION_SOURCE_CPU_READY_ACTUAL.json').read_bytes());assert ready['passed'] and ready['no_live68_source_change']
 metadata=json.loads((R/'PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes());assert metadata['passed']
 q=json.loads((R/'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());assert q['run_id']==metadata['run_id']=='H1_STEP270_RECOVERY_ORIGINAL_1792908227707693100'
 put('PAIR_OPTIMIZATION_NORMAL_FULLSAVE_REQUEST_STARTED_ACTUAL.json',dict(epoch=time.time(),run_id=q['run_id'],human_request='开始提速方案实施',no_signal=True))
 spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);secret=m.recover()
 results={};c=None
 for key in ('h1','recovery'):
  c=d.t.connect() if key=='h1' else d.connect72(secret)
  try:
   worker=metadata['source210']['H1_worker'] if key=='h1' else metadata['source72']['worker']
   results[key]=d.code(c,d.t.PY if key=='h1' else d.PY72,CODE,dict(q=q,key=key,worker=worker,script='h1_step270_production_worker_v1.py' if key=='h1' else 'recovery_worker.py'),timeout=45)
   put('PAIR_OPTIMIZATION_'+key.upper()+'_NORMAL_FULLSAVE_REQUEST_ACTUAL.json',results[key])
  finally:c.close();c=None
 secret=None
 put('PAIR_OPTIMIZATION_BOTH_NORMAL_FULLSAVE_REQUESTS_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,run_id=q['run_id'],results=results,original_writer_remains_only_account_writer=True))
 print(json.dumps(dict(passed=True,normal_fullsave_requests=results)))
except BaseException:
 put('PAIR_OPTIMIZATION_NORMAL_SAVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_kill_refund_or_account_change=True));raise

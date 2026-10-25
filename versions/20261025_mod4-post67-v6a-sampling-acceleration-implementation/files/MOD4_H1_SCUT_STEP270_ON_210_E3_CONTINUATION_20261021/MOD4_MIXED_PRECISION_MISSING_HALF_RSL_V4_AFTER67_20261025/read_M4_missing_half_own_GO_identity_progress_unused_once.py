from pathlib import Path
import importlib.util,json,sys,time,traceback
M=Path(__file__).resolve().parent;T=M.parent;W=T.parent;R=M/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CODE=r'''
from pathlib import Path
import json,os,psutil,subprocess,time
q=v['q'];key=v['key'];root=Path(q['roots'][key]);read=lambda p:json.loads(p.read_bytes()) if p.is_file() else None
go=read(root/('GO_PRODUCTION.json' if key=='h1' else 'job0/GO_PRODUCTION.json'));assert go and go['run_id']==q['run_id'] and go['source_SHA']==q['specs'][key]['source_SHA']
start=read(root/'job0/production_STARTED_ACTUAL.json');assert start
current=read(root/'NODE_CURRENT.json');terminal=read(root/'NODE_TERMINAL_ACTUAL.json');identity=(terminal['row'] if terminal else current['row']).get('worker');worker=None;own=[];same=False
if identity:
 try:
  p=psutil.Process(identity['pid']);same=p.create_time()==identity['creation'] and p.cmdline()==identity['argv'];worker=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline()) if same else None
  if same:
   assert str(root/q['specs'][key]['production_script']) in p.cmdline()
   lines=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True).splitlines();own=[x for x in lines if len(x.split(','))>=3 and x.split(',')[1].strip()==str(p.pid)];assert all(q['specs'][key]['GPU_UUID'] in x for x in own)
 except psutil.NoSuchProcess:worker=None
out=root/'job0/production';errors={str(p):p.read_text('utf8') for p in out.rglob('*ORIGINAL_ERROR*.json')}
result=dict(epoch=time.time(),key=key,actual_GO=go,expected_GPU_UUID=q['specs'][key]['GPU_UUID'],worker_start=start,worker_identity_current=worker,own_compute_snapshot=own,benchmark_progress=read(out/'BENCHMARK_PROGRESS_CURRENT.json'),benchmark_protocol=read(out/'PRECISION_BENCHMARK_SOURCE_AND_PROTOCOL_ACTUAL.json'),benchmark_complete=read(out/'PRECISION_BENCHMARK_COMPLETE_ACTUAL.json'),actual_node_current=read(root/'NODE_CURRENT.json'),actual_node_terminal=read(root/'NODE_TERMINAL_ACTUAL.json'),original_errors=errors,not_training_FINAL_model_or_qualified_source=True,not_permanent_alive_or_success=True)
if key=='h1':
 owner=Path(q['owner_root']);result.update(owner_current=read(owner/'OWNER_CURRENT.json'),owner_final=read(owner/'COHORT_FINAL.json'),owner_exit=read(owner/'OWNER_EXIT_ACTUAL.json'))
print(json.dumps(result))
'''
try:
 q=json.loads((R/'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());assert q['specs']['h1']['performance_benchmark_only'] and q['specs']['recovery']['performance_benchmark_only']
 put('BENCHMARK_GO_IDENTITY_READER_STARTED_ACTUAL.json',dict(epoch=time.time(),run_id=q['run_id'],only_own_GO_UUID_exe_argv_create_and_progress=True))
 s=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(s);s.loader.exec_module(memory);secret=memory.recover()
 c=d.t.connect()
 try:a=d.code(c,d.t.PY,CODE,dict(q=q,key='h1'),timeout=60)
 finally:c.close()
 c=d.connect72(secret);secret=None
 try:b=d.code(c,d.PY72,CODE,dict(q=q,key='recovery'),timeout=60)
 finally:c.close()
 put('BENCHMARK_ACTUAL_GO_WORKER_IDENTITY_AND_PROGRESS_SNAPSHOT_ACTUAL.json',dict(epoch=time.time(),actual_finite_returned=True,run_id=q['run_id'],slots=dict(h1=a,recovery=b),not_an_actual_benchmark_final_or_qualification=True))
 print(json.dumps({k:dict(mode=v['benchmark_progress']['mode'] if v['benchmark_progress'] else None,completed=v['benchmark_progress']['completed_in_mode'] if v['benchmark_progress'] else None,errors=len(v['original_errors']),worker_identity_observed=bool(v['worker_identity_current']),own_GPU_allocation_observed=bool(v['own_compute_snapshot'])) for k,v in [('h1',a),('recovery',b)]}))
except BaseException:
 put('BENCHMARK_GO_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_same_once=True));raise


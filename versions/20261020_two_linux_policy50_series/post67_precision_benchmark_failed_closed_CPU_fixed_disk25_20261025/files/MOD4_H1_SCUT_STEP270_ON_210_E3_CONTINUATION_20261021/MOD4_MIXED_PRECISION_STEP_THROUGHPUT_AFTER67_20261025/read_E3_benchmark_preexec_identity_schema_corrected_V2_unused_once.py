from pathlib import Path
import importlib.util,json,sys,time,traceback
M=Path(__file__).resolve().parent;T=M.parent;W=T.parent;R=M/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CODE=r'''
from pathlib import Path
import json,psutil,subprocess,time
q=v['q'];root=Path(q['roots']['recovery']);read=lambda p:json.loads(p.read_bytes()) if p.is_file() else None
current=read(root/'NODE_CURRENT.json');terminal=read(root/'NODE_TERMINAL_ACTUAL.json');row=terminal['row'] if terminal else current['row'];identity=row.get('worker');worker=None;own=[]
if identity:
 try:
  p=psutil.Process(identity['pid']);assert p.create_time()==identity['creation'] and p.cmdline()==identity['argv'] and str(root/q['specs']['recovery']['production_script']) in p.cmdline();worker=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline())
  own=[x for x in subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True).splitlines() if len(x.split(','))>=3 and x.split(',')[1].strip()==str(p.pid)];assert all(q['specs']['recovery']['GPU_UUID'] in x for x in own)
 except psutil.NoSuchProcess:worker=None
out=root/'job0/production'
print(json.dumps(dict(epoch=time.time(),original_spawn_identity=read(root/'job0/production_STARTED_ACTUAL.json'),actual_current_worker=worker,node_current=current,node_terminal=terminal,own_GPU_snapshot=own,protocol=read(out/'PRECISION_BENCHMARK_SOURCE_AND_PROTOCOL_ACTUAL.json'),progress=read(out/'BENCHMARK_PROGRESS_CURRENT.json'),suite=read(out/'PRECISION_BENCHMARK_COMPLETE_ACTUAL.json'),mode_timings={p.parent.name:read(p) for p in out.glob('*/TIMING_CURRENT.json')},mode_completes={p.parent.name:read(p) for p in out.glob('*/MODE_COMPLETE_ACTUAL.json')},errors={str(p):p.read_text('utf8') for p in out.rglob('*ORIGINAL_ERROR*.json')},spawn_argv_preexec_not_relabelled_current_identity=True,no_worker_dead_claim_from_argv_transition=True,not_permanent_alive_or_complete_success=True)))
'''
try:
 q=json.loads((R/'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());s=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(s);s.loader.exec_module(memory);secret=memory.recover();c=d.connect72(secret);secret=None
 try:a=d.code(c,d.PY72,CODE,dict(q=q),timeout=60)
 finally:c.close()
 put('E3_BENCHMARK_PREEXEC_IDENTITY_SCHEMA_CORRECTION_AND_PROGRESS_ACTUAL.json',a)
 print(json.dumps(dict(worker_current=bool(a['actual_current_worker']),mode=a['progress']['mode'] if a['progress'] else None,completed=a['progress']['completed_in_mode'] if a['progress'] else None,errors=a['errors'],last_rows={k:v['rows'][-1] for k,v in a['mode_timings'].items() if v['rows']})))
except BaseException:
 put('E3_BENCHMARK_V2_IDENTITY_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise


"""Human speed question: one bounded own-worker text snapshot; no FINAL/PT/GPU query or training change."""
from pathlib import Path
import importlib.util,json,os,sys,time,traceback
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;R=D/'reports';N=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V4_RESOURCE_V69_20261025'
CODE=r'''
from pathlib import Path
import hashlib,json,math,os,psutil,re,statistics,time
e=v['worker'];p=psutil.Process(e['pid']);assert p.create_time()==e['creation'] and p.cmdline()==e['argv'] and p.exe()==e['exe']
path=Path(v['path']);assert path.is_file() and not path.is_symlink();st=path.stat()
with path.open('rb') as f:raw=f.read(st.st_size)
after=path.stat();assert len(raw)==st.st_size and st.st_dev==after.st_dev and st.st_ino==after.st_ino and after.st_size>=st.st_size
ansi=re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]');it=re.compile(r'Learning iteration\s+(\d+)\s*/\s*(\d+)')
ct=re.compile(r'Collection time:\s*([0-9.eE+-]+)s');lt=re.compile(r'Learning time:\s*([0-9.eE+-]+)s');tt=re.compile(r'Iteration time:\s*([0-9.eE+-]+)s')
rows=[];current=None;excerpt=[]
for original in raw.decode('utf8').splitlines():
 line=ansi.sub('',original)
 if m:=it.search(line):
  if current is not None:rows.append(current)
  current=dict(global_iteration=int(m[1]),raw_metric_lines=[original])
 elif current is not None:
  for pattern,key in [(ct,'collection_seconds'),(lt,'PPO_seconds'),(tt,'iteration_seconds_printed')]:
   if m:=pattern.search(line):current[key]=float(m[1]);current['raw_metric_lines'].append(original)
if current is not None:rows.append(current)
complete=[];incomplete=[]
for row in rows:
 if not {'collection_seconds','PPO_seconds'}<=set(row):incomplete.append(row);continue
 c=row['collection_seconds'];l=row['PPO_seconds'];assert math.isfinite(c) and math.isfinite(l) and c>0 and l>0
 if 'iteration_seconds_printed' in row:assert abs(c+l-row['iteration_seconds_printed'])<=.025
 row.update(owned_logged_update=len(complete)+1,collection_envsteps_s=480000/c,cycle_envsteps_s=480000/(c+l));complete.append(row)
measured=complete[2:];assert len(measured)>=4
def pct(a,p):
 a=sorted(a);t=(len(a)-1)*p;i=int(t);j=min(i+1,len(a)-1);return a[i] if i==j else a[i]*(j-t)+a[j]*(t-i)
def summary(key):
 a=[r[key] for r in measured];return dict(n=len(a),median=statistics.median(a),q25=pct(a,.25),q75=pct(a,.75),minimum=min(a),maximum=max(a))
print(json.dumps(dict(epoch=time.time(),path=str(path),source_text_snapshot_bytes=len(raw),source_text_snapshot_SHA=hashlib.sha256(raw).hexdigest(),inode=st.st_ino,source_stat_mtime_ns=st.st_mtime_ns,
 exact_own_worker_identity=e,own_identity_verified_before_read=True,complete_logged_updates=len(complete),excluded_first_warmup_updates=2,measured_logged_updates=len(measured),incomplete_trailing_logged_blocks=incomplete,
 collection_seconds=summary('collection_seconds'),PPO_seconds=summary('PPO_seconds'),collection_envsteps_s=summary('collection_envsteps_s'),cycle_envsteps_s=summary('cycle_envsteps_s'),
 all_complete_logged_rows=complete,scope='Ongoing69d original RSL text snapshot only.480000environment transitions/update. Logged timing is CPU wall with implicit GPUwait, not FINAL qualification or fixed-input causal benchmark.',
 no_GPU_checkpoint_raw_query_or_training_budget_mutation=True)))
'''
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
put('HUMAN_CURRENT69D_TIMING_TEXT_SNAPSHOT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,human='提速后速度提升了多少?',scope='Explicit human request authorizes new saved-log read only; not the closing collector or another PPO/native/GPU job'))
try:
 meta=json.loads((N/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes());assert meta['passed'] and meta['actual_finite_returned']
 q=json.loads((N/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes())
 baseline=json.loads((R/'CLOSED68_SAVED_LOG_FP32_THROUGHPUT_BASELINE_CPU_ACTUAL.json').read_bytes())
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 c=route.connect()
 try:h1=d.code(c,route.PY,CODE,dict(worker=meta['source210']['H1_worker'],path=q['roots']['h1']+'/job0/production_WORKER.log'),timeout=35)
 finally:c.close()
 sp=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 secret=m.recover();c=d.connect72(secret);secret=None
 try:e3=d.code(c,d.PY72,CODE,dict(worker=meta['source72']['worker'],path=q['roots']['recovery']+'/job0/production_WORKER.log'),timeout=35)
 finally:c.close()
 result=dict(epoch=time.time(),actual_finite_returned=True,scope='Ongoing69d saved timing snapshot vs complete68 baseline. Different trajectories/reset populations; observed total throughput change, no pure causal hardware/kernel attribution.',models={})
 for key,value in [('h1',h1),('recovery',e3)]:
  base=baseline['models'][key];ratio=value['cycle_envsteps_s']['median']/base['cycle_envsteps_per_second']['median']
  result['models'][key]=dict(snapshot=value,baseline68=base,observed_cycle_throughput_ratio=ratio,observed_cycle_throughput_percent_change=(ratio-1)*100)
 put('HUMAN_CURRENT69D_VS68_TIMING_TEXT_SNAPSHOT_RETURNED_ACTUAL.json',result)
 print(json.dumps({k:dict(measured_updates=v['snapshot']['measured_logged_updates'],baseline_cycle_envsteps_s=v['baseline68']['cycle_envsteps_per_second']['median'],current_cycle_envsteps_s=v['snapshot']['cycle_envsteps_s']['median'],observed_percent_change=v['observed_cycle_throughput_percent_change'],current_collection_seconds=v['snapshot']['collection_seconds']['median']) for k,v in result['models'].items()}))
except BaseException:
 put('HUMAN_CURRENT69D_TIMING_TEXT_SNAPSHOT_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_retry_or_training_change=True));raise

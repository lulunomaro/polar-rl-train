from pathlib import Path
import importlib.util,json,sys,time,traceback
M=Path(__file__).resolve().parent;T=M.parent;W=T.parent;R=M/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CODE=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,shutil,subprocess,time,stat
q=v['q'];key=v['key'];root=Path(q['roots'][key]);owner=Path(q['owner_root'])
assert json.loads((root/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited']
roots=[root]+([owner] if key=='h1' else [])
assert not any(p.pid!=os.getpid() and any(any(a.startswith(str(r)+'/') for r in roots) for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
locks=[Path(q['specs'][key]['private_lock'])]
if key=='h1':
 C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());assert c['active_segment'] is None and c['authorized_training_seconds']==2268000 and len(c['budget_extensions'])==9 and c['remaining_training_seconds']==v['remaining']
 assert json.loads((owner/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled'];locks+=[C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]
else:locks.append(Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock'))
for p in locks:
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
base=root/'job0';rows=[];dirs=[]
for p in [base/'data',base/'config',base/'home']:
 if not p.exists():dirs.append(dict(path=str(p),exists=False));continue
 assert not p.is_symlink() and p.resolve().is_relative_to(root.resolve())
 for parent,children,names in os.walk(p,followlinks=False):
  pp=Path(parent);children[:]=[n for n in children if not (pp/n).is_symlink() and (pp/n)!=base/'home/.nv/ComputeCache']
  for name in names:
   f=pp/name;s=f.lstat()
   rows.append(dict(path=str(f),bytes=s.st_size,allocated_bytes=s.st_blocks*512,mtime_ns=s.st_mtime_ns,inode=s.st_ino,nlink=s.st_nlink,symlink=f.is_symlink(),regular=stat.S_ISREG(s.st_mode)))
 dirs.append(dict(path=str(p),exists=True))
print(json.dumps(dict(epoch=time.time(),root=str(root),directories=dirs,files=rows,logical_bytes=sum(r['bytes'] for r in rows),allocated_bytes=sum(r['allocated_bytes'] for r in rows),fresh_source_free=shutil.disk_usage(root).free,old_benchmark_actual_allout_locks_free=True,canonical_SHA=hashlib.sha256(C.read_bytes()).hexdigest(),canonical_remaining=c['remaining_training_seconds'],metadata_only_no_hash_copy_delete_or_GPU=True)))
'''
try:
 q=json.loads((R/'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());proof=json.loads((R/'BENCHMARK_TEXT_CANONICAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes());assert proof['owner_node_workers_all_actual_out'] and proof['original_canonical_cost_settled']
 put('OWN_FAILED_BENCHMARK_MISSING_DATA_HOME_METADATA_STARTED_ACTUAL.json',dict(epoch=time.time(),only_after_benchmark_actual_closed=True,reason='Metadata-only inventory of own failed benchmark cache to resolve original disk25 guard; no protected model/raw/log/source reads'))
 s=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(s);s.loader.exec_module(memory);secret=memory.recover()
 c=d.t.connect()
 try:a=d.code(c,d.t.PY,CODE,dict(q=q,key='h1',remaining=proof['original_remaining_closed_snapshot']),timeout=60)
 finally:c.close()
 put('OWN_FAILED_BENCHMARK_MISSING_DATA_HOME_METADATA_210_ACTUAL.json',a)
 print(json.dumps(dict(own_failed_benchmark_cache_bytes=a['logical_bytes'],allocated_bytes=a['allocated_bytes'],source_free=a['fresh_source_free'])))
except BaseException:
 put('OWN_BENCHMARK_CACHE_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_same_once=True));raise

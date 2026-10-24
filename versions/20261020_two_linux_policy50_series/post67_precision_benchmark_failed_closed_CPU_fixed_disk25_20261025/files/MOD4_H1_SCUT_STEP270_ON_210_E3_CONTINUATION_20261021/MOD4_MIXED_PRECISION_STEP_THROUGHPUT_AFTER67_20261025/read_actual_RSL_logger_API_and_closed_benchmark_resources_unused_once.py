from pathlib import Path
import importlib.util,json,sys,time,traceback
M=Path(__file__).resolve().parent;T=M.parent;W=T.parent;R=M/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CODE=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,shutil,subprocess,time
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
runner=Path(v['runner']);rsl=runner.parent.parent;paths=[runner]+[p for p in rsl.rglob('*logger*.py') if 'def log(' in p.read_text('utf8')]
sources=[]
for p in paths:
 raw=p.read_bytes();sources.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8')))
uuid=q['specs'][key]['GPU_UUID'];rows=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True).splitlines();own_gpu=[x for x in rows if uuid in x]
line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if uuid in x)
free=shutil.disk_usage(root).free;ram=psutil.virtual_memory().available
print(json.dumps(dict(epoch=time.time(),key=key,sources=sources,resource=dict(expected_GPU_UUID=uuid,expected_GPU_empty=not own_gpu,allocation_count_on_expected_GPU=len(own_gpu),GPU_free_MiB=int(line.split(',')[-1]),GPU_threshold_MiB=15669 if key=='h1' else 7000,GPU_passed=int(line.split(',')[-1])>(15669 if key=='h1' else 7000),RAM_available_bytes=ram,RAM8_passed=ram>8*1024**3,durable_free_bytes=free,disk25_passed=free>25*1024**3),old_benchmark_actual_allout_locks_free=True,no_unknown_peer_identity_or_GPU_work_or_budget_write=True,actual_canonical_remaining=c['remaining_training_seconds'] if key=='h1' else None)))
'''
try:
 q=json.loads((R/'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());proof=json.loads((R/'BENCHMARK_TEXT_CANONICAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes());assert proof['owner_node_workers_all_actual_out'] and proof['original_canonical_cost_settled']
 put('ACTUAL_RSL_LOGGER_SOURCE_AND_RESOURCE_READ_STARTED_ACTUAL.json',dict(epoch=time.time(),only_after_benchmark_actual_closed=True,reason='Fix keyword Logger.log ABI and H1-vs-E3 callback counters before new unused GPU benchmark'))
 hs=json.loads((R/'H1_FULL_INSTALLED_SOURCE_SDK_RSL_CPU_ACTUAL.json').read_bytes());es=json.loads((R/'RECOVERY_TWO50_FULL_TARGET_SOURCE_RSL_SDK_CPU_ACTUAL.json').read_bytes())
 hpath=next(x['path'] for x in hs['actual_RSL_sources'] if x['path'].endswith('/runners/on_policy_runner.py'))
 # The E3 source audit uses the same primary installed RSL source list.
 epath=next(x['path'] for x in es['actual_RSL_sources'] if x['path'].endswith('/runners/on_policy_runner.py'))
 s=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(s);s.loader.exec_module(memory);secret=memory.recover()
 c=d.t.connect()
 try:a=d.code(c,d.t.PY,CODE,dict(q=q,key='h1',runner=hpath,remaining=proof['original_remaining_closed_snapshot']),timeout=60)
 finally:c.close()
 put('ACTUAL_RSL_RUNNER_LOGGER_SOURCE_AND_RESOURCE_210_ACTUAL.json',a)
 c=d.connect72(secret);secret=None
 try:b=d.code(c,d.PY72,CODE,dict(q=q,key='recovery',runner=epath,remaining=proof['original_remaining_closed_snapshot']),timeout=60)
 finally:c.close()
 put('ACTUAL_RSL_RUNNER_LOGGER_SOURCE_AND_RESOURCE_72_ACTUAL.json',b)
 print(json.dumps(dict(h1=a['resource'],recovery=b['resource'],RSL_sources_210=[r['path'] for r in a['sources']],RSL_sources_72=[r['path'] for r in b['sources']])))
except BaseException:
 put('RSL_LOGGER_SOURCE_RESOURCE_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_same_once=True));raise


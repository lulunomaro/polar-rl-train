from pathlib import Path
import importlib.util,json,shlex,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;N=W/'MOD4_TWO_LINUX_POLICY50_COHORT_51_20261021';sys.path.insert(0,str(N));import deploy_two50_reconciled_original_writer_once as d
s=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(s);s.loader.exec_module(memory)
REMOTE=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,shutil,time
old=Path(v['old']);B=Path(v['root']);assert not B.exists();ex=json.loads((old/'PARENT_EXIT_ACTUAL.json').read_bytes());co=json.loads((old/'PARENT_COMPLETE_ACTUAL.json').read_bytes());assert ex['all_own_children_waited'] and ex['own_eval_lease_released'] and co['passed'] and co['final']['steps']==180 and v['CPU']['passed_independent_execution_CPU'] and v['CPU']['source_SHA']==co['final']['source_SHA']
for p in psutil.process_iter(['pid','cmdline','status']):
 try:assert p.pid==os.getpid() or p.info['status']==psutil.STATUS_ZOMBIE or not any(x.startswith(str(old)+'/') for x in p.info['cmdline'] or [])
 except psutil.NoSuchProcess:pass
lease=Path('/home/lc01/Zonglin Li/zonglin2/state/MOD4_H1_SHARED_FROZEN_EVAL_20261021.lock').open('a+b');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(lease,fcntl.LOCK_UN);lease.close();B.mkdir();shutil.copytree(old/'job0',B/'job0');shutil.copytree(old/'lib',B/'lib')
for name in ('worker.py','parent.py','clock_training_health.py'):shutil.copy2(old/name,B/name)
assert hashlib.sha256((B/'job0/source.pt').read_bytes()).hexdigest()==v['CPU']['source_SHA'];cfg=json.loads((old/'FROZEN_CONFIG.json').read_bytes());cfg.update(kind='H1_original80_full1500',steps=1500,wall_seconds=3600);(B/'FROZEN_CONFIG.json').write_text(json.dumps(cfg,indent=2));shutil.copy2(old/'SOURCE_MANIFEST.json',B/'NATIVE_SOURCE_MANIFEST_EXACT.json');(B/'NATIVE180_ALLROWS_CPU_ACTUAL.json').write_text(json.dumps(v['CPU'],indent=2));print(json.dumps(dict(epoch=time.time(),root=str(B),source_SHA=cfg['source_SHA'],native_actual_exit_allout_and_CPU_passed=True,new_full_source_ready_not_yet_launched=True)))
'''
try:
 cpu=json.loads((R/'H1_NATIVE180_V2_ALL_ROWS_INDEPENDENT_CPU_ACTUAL.json').read_bytes());assert cpu['passed_independent_execution_CPU'];old=json.loads((R/'H1_NATIVE180_V2_DETACHED_ACTUAL_STARTED.json').read_bytes())['parent']['root'];root='/home/lc01/Zonglin Li/zonglin2/tasks/GraduationH1_2110v85_full1500_v1';secret=memory.recover();c=d.connect72(secret);secret=None
 try:
  prepared=d.code(c,d.PY72,REMOTE,dict(old=old,root=root,CPU=cpu),timeout=90)
  i,o,e=c.exec_command(shlex.quote(d.PY72)+' -u -B '+shlex.quote(root+'/parent.py')+' --detach',timeout=30);raw=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,(err,raw);parent=json.loads(raw)
  value=d.code(c,d.PY72,"from pathlib import Path;import json,psutil,time;B=Path(v['root']);p=psutil.Process(v['parent']['pid']);assert p.create_time()==v['parent']['creation'];until=time.monotonic()+20\nwhile not (B/'CHILD_STARTED_ACTUAL.json').exists() and not (B/'PARENT_ORIGINAL_ERROR.json').exists() and time.monotonic()<until:time.sleep(.25)\ns=json.loads((B/'CHILD_STARTED_ACTUAL.json').read_bytes());w=psutil.Process(s['worker']['pid']);assert w.create_time()==s['worker']['creation'];print(json.dumps(dict(epoch=time.time(),parent=v['parent'],child_started=s,actual_worker_argv=w.cmdline(),source_SHA=s['source_SHA'],no_optimizer=True,not_future_FINAL=True)))",dict(root=root,parent=parent),timeout=30)
 finally:c.close()
 (R/'H1_FULL1500_DETACHED_ACTUAL_STARTED.json').open('x',encoding='utf8').write(json.dumps(dict(prepared=prepared,**value),indent=2));print(json.dumps(value))
except BaseException:
 (R/'H1_FULL1500_LAUNCH_ORIGINAL_ERROR.json').open('x',encoding='utf8').write(json.dumps(dict(error=traceback.format_exc(),no_replay=True),indent=2));raise

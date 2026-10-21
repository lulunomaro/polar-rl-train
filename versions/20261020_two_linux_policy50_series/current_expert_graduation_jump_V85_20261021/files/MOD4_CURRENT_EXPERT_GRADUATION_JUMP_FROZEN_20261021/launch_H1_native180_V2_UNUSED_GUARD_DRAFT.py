from pathlib import Path
import importlib.util,json,shlex,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;N=W/'MOD4_TWO_LINUX_POLICY50_COHORT_51_20261021';sys.path.insert(0,str(N));import deploy_two50_reconciled_original_writer_once as d
s=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(s);s.loader.exec_module(memory)
READ=r'''
from pathlib import Path
import fcntl,json,os,psutil,time
old=Path('/home/lc01/Zonglin Li/zonglin2/tasks/H1shared_eval50_baseline32_full13_2110v6');ex=json.loads((old/'PARENT_EXIT_ACTUAL.json').read_bytes());assert ex['all_own_children_waited'] and ex['own_eval_lease_released']
for p in psutil.process_iter(['pid','cmdline','status']):
 try:assert p.pid==os.getpid() or p.info['status']==psutil.STATUS_ZOMBIE or not any(x.startswith(str(old)+'/') for x in p.info['cmdline'] or [])
 except psutil.NoSuchProcess:pass
lease=Path('/home/lc01/Zonglin Li/zonglin2/state/MOD4_H1_SHARED_FROZEN_EVAL_20261021.lock').open('a+b');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(lease,fcntl.LOCK_UN);lease.close();B=Path(v['root']);q=json.loads((B/'TARGET_SOURCE_CPU_INSTALLED_ACTUAL.json').read_bytes());assert q['source_SHA']==v['source_SHA'] and not (B/'PARENT_IDENTITY.json').exists();print(json.dumps(dict(epoch=time.time(),old_baseline_all_own_out=True,own_eval_lease_free=True,new_root=str(B))))
'''
try:
 q=json.loads((R/'H1_NATIVE180_V2_TARGET_SOURCE_CPU_INSTALLED_ACTUAL.json').read_bytes());secret=memory.recover();c=d.connect72(secret);secret=None
 try:
  boundary=d.code(c,d.PY72,READ,dict(root=q['root'],source_SHA=q['source_SHA']),timeout=90)
  i,o,e=c.exec_command(shlex.quote(d.PY72)+' -u -B '+shlex.quote(q['root']+'/parent.py')+' --detach',timeout=30);raw=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,(err,raw);parent=json.loads(raw)
  value=d.code(c,d.PY72,"from pathlib import Path;import json,psutil,time;B=Path(v['root']);p=psutil.Process(v['parent']['pid']);assert p.create_time()==v['parent']['creation'];until=time.monotonic()+20\nwhile not (B/'CHILD_STARTED_ACTUAL.json').exists() and not (B/'PARENT_ORIGINAL_ERROR.json').exists() and time.monotonic()<until:time.sleep(.25)\ns=json.loads((B/'CHILD_STARTED_ACTUAL.json').read_bytes());w=psutil.Process(s['worker']['pid']);assert w.create_time()==s['worker']['creation'];print(json.dumps(dict(epoch=time.time(),parent=v['parent'],child_started=s,actual_worker_argv=w.cmdline(),source_SHA=s['source_SHA'],no_optimizer=True,not_future_FINAL=True)))",dict(root=q['root'],parent=parent),timeout=30)
 finally:c.close()
 (R/'H1_NATIVE180_V2_DETACHED_ACTUAL_STARTED.json').open('x',encoding='utf8').write(json.dumps(dict(boundary=boundary,**value),indent=2));print(json.dumps(value))
except BaseException:
 (R/'H1_NATIVE180_V2_LAUNCH_ORIGINAL_ERROR.json').open('x',encoding='utf8').write(json.dumps(dict(error=traceback.format_exc(),no_replay=True),indent=2));raise

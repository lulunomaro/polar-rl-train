"""Human-approved, PID/start/path-bound cleanup of only the failed frozen probe."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
root='/home/egde/rl_candidates/MOD4_S3_E1_FULL_CONTRACT_20261009'
assert not (R/'E1_HUMAN_APPROVED_FAILED_NATIVE_FORCE_EXIT_REVIEW.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,time,os,signal,subprocess
D=Path(ROOT);R=D/'reports';sys.path.insert(0,str(D));import supervise_e1_boundary_path_review as rw
w=rw.w;st=w.read(R/'E1_STATE.json');att=w.read(R/'E1_ATTENTION.json')
assert not (R/'E1_HUMAN_APPROVED_FAILED_NATIVE_FORCE_EXIT_REVIEW.json').exists()
assert st['child']['pid']==1638740 and st['child']['start_ticks']==68823237
a=w.identity(1638740);before=w.s.q.ctl.CANONICAL.read_bytes()
row=dict(epoch=time.time(),human_authorization='Human replied to request to force-exit only failed no-learning PID1638740: 允许。继续推进训练',authorized_only_PID=1638740,authorized_start_ticks=68823237,actual_before=a,no_process_group_or_trainer_or_other_AI_signal=True,old_error_weights_and_source_retained=True,new_budget_seconds=0)
if not a or a['state']=='Z' or a['start_ticks']!=68823237:
 row.update(signal_sent=False,reason='Bound failed helper already exited; no process was signalled',actual_exit_verified=True)
else:
 assert a['ppid']==1 and a['cwd']=='/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002'
 assert a['argv'][1]==str(D/'native_e1_terrain_probe.py') and '--max_iterations' not in a['argv']
 assert a['argv'][a['argv'].index('--num_envs')+1]=='20000'
 assert a['argv'][a['argv'].index('--steps')+1]=='120'
 assert a['argv'][a['argv'].index('--warmup')+1]=='24'
 assert a['argv'][a['argv'].index('--profile_steps')+1]=='0'
 assert not w.identity(st['owner']['pid']) and att['own_child_still_alive'] and 'TimeoutExpired' in att['error']
 graceful=w.read(R/'E1_FAILED_FROZEN_NATIVE_EXIT_REVIEW.json')
 assert graceful['signal']=='SIGTERM' and not graceful['actual_exit_verified']
 assert (R/'E1_NATIVE20K.json.error').exists() and not (R/'E1_NATIVE20K.json').exists()
 assert not (D/'discard_logs').exists() and not (D/'learning_logs').exists()
 log=(D/'e1_native20k.log').read_text(errors='replace');error=(R/'E1_NATIVE20K.json.error').read_text()
 assert 'PxgPinnedMemoryAllocate failed' in log and 'Scene state is corrupted' in log and 'wheel_friction_error' in error
 assert not w.trainers() and w.s.q.base.budget_state()['active_segment'] is None and not w.read(w.s.q.ctl.STATE_PATH).get('active_training')
 nd=Path('/home/egde/rl_candidates/MOD4_S3_E1_SCENE_QUERY_RESOURCE_REVIEW_20261009/reports')
 ns=w.read(nd/'E1_STATE.json');assert ns['phase']=='waiting_actual_failed_frozen_native_exit_before_new_E1_authority' and ns.get('child') is None
 owner=w.identity(ns['owner']['pid']);assert owner and owner['start_ticks']==ns['owner']['start_ticks'] and owner['argv'][1].endswith('/supervise_e1_scene_query_resource_review.py')
 w.verify();src=w.source();assert w.s.q.base.sha(src)=='b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8'
 row.update(signal='SIGKILL via pidfd',signal_sent=True,native_error_sha256=w.s.q.base.sha(R/'E1_NATIVE20K.json.error'),log_sha256=w.s.q.base.sha(D/'e1_native20k.log'),source_sha256=w.s.q.base.sha(src),PPO_never_started=True,active_and_Sactive_empty_before=True,already_launched_recovery_owner=owner)
 capability=subprocess.run(['/usr/bin/python3','-c','import os,signal; assert hasattr(os,"pidfd_open") and hasattr(signal,"pidfd_send_signal"); print("system_pidfd_supported")'],capture_output=True,text=True,check=True)
 assert capability.stdout.strip()=='system_pidfd_supported'
 w.write('E1_HUMAN_APPROVED_FAILED_NATIVE_FORCE_EXIT_REQUESTED.json',row)
 signal_code="""
import os,signal,json,sys
from pathlib import Path
a=json.loads(sys.argv[1]);p=Path('/proc')/str(a['pid'])
def bound():
 fields=(p/'stat').read_text().split(') ',1)[1].split()
 return int(fields[19])==a['start_ticks'] and (p/'cmdline').read_bytes().decode().rstrip('\\0').split('\\0')==a['argv'] and str((p/'cwd').resolve())==a['cwd']
assert bound()
fd=os.pidfd_open(a['pid'],0)
try:
 assert bound();signal.pidfd_send_signal(fd,signal.SIGKILL)
finally:os.close(fd)
print('only_bound_failed_native_signalled')
"""
 sent=subprocess.run(['/usr/bin/python3','-c',signal_code,json.dumps(a)],capture_output=True,text=True,check=True)
 assert sent.stdout.strip()=='only_bound_failed_native_signalled'
 until=time.time()+20
 while (actual:=w.identity(a['pid'])) and actual['state']!='Z' and actual['start_ticks']==a['start_ticks'] and time.time()<until:time.sleep(.25)
 row['actual_after']=w.identity(a['pid']);row['actual_exit_verified']=not row['actual_after'] or row['actual_after']['state']=='Z' or row['actual_after']['start_ticks']!=a['start_ticks']
 assert row['actual_exit_verified'],'Do not signal again; audit retained force-exit intent'
row['budget_bytes_exact_at_cleanup']=before==w.s.q.ctl.CANONICAL.read_bytes()
row['budget_after']=w.s.q.base.budget_state()
w.write('E1_HUMAN_APPROVED_FAILED_NATIVE_FORCE_EXIT_REVIEW.json',row)
print(json.dumps(row))
'''.replace('ROOT',repr(root))
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=90)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 with c.open_sftp() as sf:
  for n in ('E1_HUMAN_APPROVED_FAILED_NATIVE_FORCE_EXIT_REQUESTED.json','E1_HUMAN_APPROVED_FAILED_NATIVE_FORCE_EXIT_REVIEW.json'):
   try:sf.get(root+'/reports/'+n,str(R/n))
   except FileNotFoundError:pass
 v=json.loads(raw);print(json.dumps(dict(actual_exit_verified=v['actual_exit_verified'],signal_sent=v['signal_sent'],only_authorized_PID=v['authorized_only_PID'],budget_bytes_exact=v['budget_bytes_exact_at_cleanup'])))
finally:c.close()

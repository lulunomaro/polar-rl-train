"""Request graceful exit of this failed no-learning helper after parent timeout.

Never signal a trainer or any other GPU owner; no SIGKILL or group signalling.
"""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';root='/home/egde/rl_candidates/MOD4_S3_E1_FULL_CONTRACT_20261009'
assert not (R/'E1_FAILED_FROZEN_NATIVE_EXIT_REQUESTED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,time,os,signal
D=Path(ROOT);R=D/'reports';sys.path.insert(0,str(D));import supervise_e1_boundary_path_review as rw
w=rw.w;st=w.read(R/'E1_STATE.json');att=w.read(R/'E1_ATTENTION.json');a=w.identity(st['child']['pid'])
assert not (R/'E1_FAILED_FROZEN_NATIVE_EXIT_REQUESTED.json').exists()
assert att['own_child_still_alive'] and 'TimeoutExpired' in att['error'] and not w.identity(st['owner']['pid'])
assert a and a['start_ticks']==st['child']['start_ticks'] and a['ppid']==1
assert a['argv'][1]==str(D/'native_e1_terrain_probe.py') and '--steps' in a['argv'] and '--profile_steps' in a['argv'] and '--max_iterations' not in a['argv'] and not w.trainers()
assert (R/'E1_NATIVE20K.json.error').exists() and not (R/'E1_NATIVE20K.json').exists() and not (D/'discard_logs').exists() and not (D/'learning_logs').exists()
error=(R/'E1_NATIVE20K.json.error').read_text();log=(D/'e1_native20k.log').read_text(errors='replace')
assert 'wheel_friction_error' in error and 'PhysX ABORT error' in log and 'Scene state is corrupted' in log and 'PxgPinnedMemoryAllocate failed' in log
assert w.s.q.base.budget_state()['active_segment'] is None and not w.read(w.s.q.ctl.STATE_PATH).get('active_training')
before=w.s.q.ctl.CANONICAL.read_bytes();w.verify();src=w.source()
row=dict(epoch=time.time(),actual_frozen_child_before=a,actual_old_parent_exited=True,native_error_sha256=w.s.q.base.sha(R/'E1_NATIVE20K.json.error'),log_sha256=w.s.q.base.sha(D/'e1_native20k.log'),source_sha256=w.s.q.base.sha(src),PPO_never_started=True,active_and_Sactive_empty=True,reason='Own no-learning resource-corrupt native helper stuck in app.close after exception and parent timeout; graceful termination only after exact path/start/parent and saved error audit.',signal='SIGTERM',no_SIGKILL_no_group_no_other_AI_signal=True,old_error_and_weights_retained=True)
w.write('E1_FAILED_FROZEN_NATIVE_EXIT_REQUESTED.json',row)
os.kill(a['pid'],signal.SIGTERM)
until=time.time()+45
while (actual:=w.identity(a['pid'])) and actual['state']!='Z' and actual['start_ticks']==a['start_ticks'] and time.time()<until:time.sleep(.5)
row['actual_after']=w.identity(a['pid']);row['actual_exit_verified']=not row['actual_after'] or row['actual_after']['state']=='Z' or row['actual_after']['start_ticks']!=a['start_ticks'];row['budget_bytes_exact']=before==w.s.q.ctl.CANONICAL.read_bytes();assert row['budget_bytes_exact']
w.write('E1_FAILED_FROZEN_NATIVE_EXIT_REVIEW.json',row);print(json.dumps(row))
'''.replace('ROOT',repr(root))
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 with c.open_sftp() as sf:
  for n in ('E1_FAILED_FROZEN_NATIVE_EXIT_REQUESTED.json','E1_FAILED_FROZEN_NATIVE_EXIT_REVIEW.json'):sf.get(root+'/reports/'+n,str(R/n))
 v=json.loads(raw);print(json.dumps(dict(actual_exit_verified=v['actual_exit_verified'],no_PPO=True,budget_bytes_exact=v['budget_bytes_exact'],source_SHA=v['source_sha256'],no_SIGKILL=True)))
finally:c.close()

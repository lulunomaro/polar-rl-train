"""Correct declared launcher API before any architecture GPU/ledger segment began."""
from pathlib import Path
import sys,json,shlex,ast
D=Path(__file__).resolve().parent;R=D/'reports'
ROOT='/home/egde/rl_candidates/MOD4_S1A_HISTORY_LAUNCH_REVIEW_20261007'
OLD='/home/egde/rl_candidates/MOD4_S1A_MATCHED_HISTORY_TRAINING_20261007'
assert not (R/'S1A_LAUNCH_REVIEW_LAUNCHED.json').exists()
s=(D/'supervise_matched_history_once.py').read_text(encoding='utf8')
assert 'env=q.w.runtime_env()' in s;s=s.replace('env=q.w.runtime_env()','env=q.w.runtime()',1)
s=s.replace("D/'supervise_matched_history_once.py'","D/'supervise_matched_history_launch_review_once.py'")
anchor="    write('S1A_HISTORY_STARTED.json'"
extra="""    old=Path('/home/egde/rl_candidates/MOD4_S1A_MATCHED_HISTORY_TRAINING_20261007')
    att=q.w.read(old/'reports/S1A_HISTORY_ATTENTION.json')
    assert att['active_segment'] is None and 'runtime_env' in att['error'] and not att['child_still_alive']
    assert not q.helpers.identity(q.w.read(old/'reports/S1A_HISTORY_LAUNCHED.json')['owner']['pid'])
    assert not q.helpers.identity(q.w.read(old/'reports/S1A_HISTORY_GUARDIAN_STARTED.json')['pid'])
    assert not (old/'reports/S1A_HISTORY_STATE.json').exists()
    assert callable(q.w.runtime) and q.w.runtime()['RM_PHYSICS_DT_S']=='0.001'
    write('S1A_LAUNCH_API_REVIEW.json',dict(epoch=time.time(),previous_error=att,
      old_owner_guardian_exited=True,error_before_GPU_PPO_or_budget_segment=True,actual_runtime_API_used=True,
      original212_runtime_and_architecture_sources_unchanged=True))
"""+anchor
assert anchor in s;s=s.replace(anchor,extra,1);ast.parse(s)
(D/'supervise_matched_history_launch_review_once.py').write_text(s,encoding='utf8')
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 with c.open_sftp() as sf:
  try:sf.stat(ROOT);raise AssertionError('Named launch review already exists')
  except FileNotFoundError:pass
  sf.mkdir(ROOT);sf.mkdir(ROOT+'/reports');sf.mkdir(ROOT+'/new_changes')
  sf.put(str(D/'supervise_matched_history_launch_review_once.py'),ROOT+'/new_changes/supervise_matched_history_launch_review_once.py')
 code=r'''
from pathlib import Path
import sys,json,shutil,subprocess,time
D=Path('ROOT');OLD=Path('OLD');R=D/'reports'
N=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT1000_WORKER_REVIEW_20261007');sys.path.insert(0,str(N))
import continue_clock1000_worker_manifest_review_once as q;q.verify()
assert not q.base.trainers() and q.base.budget_state()['active_segment'] is None and not q.w.read(q.ctl.STATE_PATH).get('active_training')
f=q.w.read(OLD/'reports/SOURCE_FREEZE.json');assert len(f['sha256'])==212
for n,h in f['sha256'].items():
 assert q.base.sha(OLD/n)==h,n;p=D/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/n,p)
for n in ('S1A_HISTORY_ATTENTION.json','S1A_HISTORY_INSTALL_BOUNDARY.json','HISTORY_SDK_PASSED.json','ARCHITECTURE_LABEL_REVIEW.json','INDEPENDENT_RUNTIME_RNG_CPU.txt'):
 shutil.copy2(OLD/'reports'/n,R/n if n not in ('S1A_HISTORY_ATTENTION.json','S1A_HISTORY_INSTALL_BOUNDARY.json') else R/('PREVIOUS_'+n))
n='supervise_matched_history_launch_review_once.py';shutil.copy2(D/'new_changes'/n,D/n)
sources={**f['sha256'],n:q.base.sha(D/n)}
q.base.atomic_json(R/'SOURCE_FREEZE.json',dict(sha256=sources,original212_byte_exact=True,new_changes=[n],
 scope='Correct actual launch API before any architecture worker/accounting; actual CPU/SDK reused'))
before=q.ctl.CANONICAL.read_bytes()
with (D/'supervisor.log').open('x') as log:
 p=subprocess.Popen([q.base.PY,str(D/n)],cwd=q.P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
v=dict(epoch=time.time(),owner=q.helpers.identity(p.pid),root=str(D),source_count=len(sources),original212_byte_exact=True,
 CPU20_and_SDK_reused=True,old_entries_not_resumed=True,new_budget_seconds=0,target_updates=275)
q.base.atomic_json(R/'S1A_HISTORY_LAUNCHED.json',v);print(json.dumps(v))
'''.replace("Path('ROOT')","Path("+repr(ROOT)+")").replace("Path('OLD')","Path("+repr(OLD)+")")
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=40)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,err.decode()
 v=json.loads(raw);(R/'S1A_LAUNCH_REVIEW_LAUNCHED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()

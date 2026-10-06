"""Retire only the idle201 waiter; preserve actual198 trainer and guardian."""
import sys,shlex
from pathlib import Path
W=Path(__file__).resolve().parent.parent;D=Path(__file__).resolve().parent
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();remote='/home/egde/rl_candidates/'+D.name
try:
    code='''import sys,json,time,signal,os,subprocess
from pathlib import Path
D=Path('/home/egde/rl_candidates/MOD4_SCUT_PERSISTENT_MIX_20261006');OLD=Path('/home/egde/rl_candidates/MOD4_SCUT_CONTINUOUS_CADENCE_20261006')
sys.path.insert(0,str(D));import supervise_scut_persistent_mix as p;q=p.q;c=p.c;read=c.w.read;c.verify()
assert not (c.R/'CADENCE_LAUNCH_INTENT.json').exists()
contract=read(c.R/'CADENCE_CPU_SOURCE_CONTRACT.json');assert contract['pass_'] and contract['source_count']==202 and contract['runtime_freeze_sha256']==c.base.sha(c.w.F)
install=read(c.R/'CADENCE_INSTALL_BOUNDARY.json');active=c.base.budget_state()['active_segment']
assert q.live(install['old_trainer']) and q.live(install['old_parent']) and q.live(install['old_guardian'])
assert active['pid']==install['old_trainer']['pid'] and c.base.trainers()==[active['pid']]
saved=read(OLD/'reports/CADENCE_LAUNCHED.json')['dispatcher'];waiter=q.live(saved)
assert waiter and waiter['cwd']==str(c.P) and str(OLD/'supervise_scut_continuous_mix.py') in waiter['argv']
assert read(OLD/'reports/SCUT_CADENCE_STATE.json')['phase']=='waiting_existing_baseline_closeout'
assert not (OLD/'reports/CADENCE_HANDOVER_ACCEPTED.json').exists() and not (OLD/'reports/CADENCE_TRAINING_AUTHORITY_STARTED.json').exists()
children=[]
for f in Path('/proc').glob('[0-9]*/stat'):
 try:
  parts=f.read_text().rsplit(')',1)[1].split()
  if int(parts[1])==waiter['pid'] and parts[0]!='Z':children.append(int(f.parent.name))
 except (FileNotFoundError,ProcessLookupError,PermissionError):pass
assert not children
intent=dict(epoch=time.time(),retired_idle_waiter=waiter,retirement_reason='Healthy6h review must auto-continue rather than wait for desktop',
 old_actual_trainer=install['old_trainer'],old_actual_parent=install['old_parent'],no_GPU_children_under_waiter=True,
 no_trainer_signals=True,no_budget_operations=True,new_entry=str(q.ENTRY))
c.base.atomic_json(c.R/'CADENCE_LAUNCH_INTENT.json',intent)
# This process never acquired canonical training authority, spawned a GPU child
# or changed the ledger. Retire its wait loop, not any production process.
os.kill(waiter['pid'],signal.SIGKILL);limit=time.time()+10
while q.live(saved):assert time.time()<limit;time.sleep(.1)
state=read(OLD/'reports/SCUT_CADENCE_STATE.json');state.update(phase='idle_waiter_retired_for_persistent_cadence',updated_epoch=time.time(),no_training_started=True)
c.base.atomic_json(OLD/'reports/SCUT_CADENCE_STATE.json',state)
with (D/'cadence_supervisor.log').open('x') as log:
 proc=subprocess.Popen([c.base.PY,str(q.ENTRY)],cwd=c.P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
identity=c.helpers.identity(proc.pid);assert identity
c.base.atomic_json(c.R/'CADENCE_LAUNCHED.json',dict(epoch=time.time(),dispatcher=identity,source_count=202,
 sole_new_entry_executed_once=True,training_takeover_started=False,waits_existing_first_full_review=True,
 retired_idle201_waiter=waiter,no_GPU_or_budget_transactions=True,current_trainer=install['old_trainer']))
limit=time.time()+15
while not (c.R/'CADENCE_WAIT_STARTED.json').exists():
 assert proc.poll() is None and time.time()<limit,(D/'cadence_supervisor.log').read_text();time.sleep(.2)
assert q.live(install['old_parent']) and q.live(install['old_trainer']) and q.live(install['old_guardian'])
assert c.base.budget_state()['active_segment']['pid']==active['pid'] and c.base.trainers()==[active['pid']]
stat=(Path('/proc')/str(identity['pid'])/'stat').read_text().rsplit(')',1)[1].split();identity.update(ppid=int(stat[1]),session=int(stat[3]))
out=dict(epoch=time.time(),dispatcher=identity,phase=read(c.w.STATE)['phase'],source202_exact=True,
 actual_trainer=q.live(install['old_trainer']),actual_parent=q.live(install['old_parent']),actual_guardian=q.live(install['old_guardian']),
 old_idle_waiter_exited=True,new_training_authority_started=False,current_training_continues=True,
 budget_operations=0,authorized_training_seconds=c.base.budget_state()['authorized_training_seconds'],healthy_review_auto_continues=True)
c.base.atomic_json(c.R/'CADENCE_DEPLOYMENT_ACTUAL.json',out);print(json.dumps(out))
'''
    _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60)
    result=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,err;print(result)
    with c.open_sftp() as s:
        for n in ('CADENCE_LAUNCH_INTENT.json','CADENCE_LAUNCHED.json','CADENCE_WAIT_STARTED.json','SCUT_CADENCE_STATE.json','CADENCE_DEPLOYMENT_ACTUAL.json'):
            s.get(remote+'/reports/'+n,str(D/'reports'/n))
finally:c.close()

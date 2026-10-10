"""One new parent executes only SDK10 and native20k, never PPO or an old entry."""
from curb_io import *
from stage_curb_native_contract_once import NEW,PY
import shlex,traceback
def main():
    assert json.loads((R/'CURB_NATIVE_TARGET_CPU_VERIFIED.json').read_bytes())['passed']
    save('CURB_NATIVE_DISPATCH_STARTED.json',dict(epoch=time.time(),trial_id='E1-CURB20-INDEPENDENT-NATIVE-DEPLOY-01',once=True,no_PPO=True))
    n,w=connect_both()
    try:
        authority=boundary(n)
        guard=linux_json(n,r'''from pathlib import Path
import json,fcntl
D=Path(NEW_ROOT);B=Path(BUDGET)
assert not (D/'reports/CURB_NATIVE_SCOPE_STARTED.json').exists() and not (D/'curb_native_parent.log').exists()
assert json.loads(B.read_bytes())['active_segment'] is None
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
print(json.dumps(dict(new_entry_not_previously_run=True,two_OS_locks_free=True,no_PPO=True)))
'''.replace('NEW_ROOT',repr(NEW)).replace('BUDGET',repr(B)))
        cmd='nohup '+shlex.quote(PY)+' '+shlex.quote(NEW+'/supervise_curb_native_scope_once.py')+' > '+shlex.quote(NEW+'/curb_native_parent.log')+' 2>&1 < /dev/null & echo $!'
        _,o,e=n.exec_command(cmd,timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,err.decode(errors='replace');pid=int(raw.strip())
        actual=linux_json(n,r'''from pathlib import Path
import json,time
p=Path('/proc')/str(PID);assert p.exists();s=(p/'stat').read_text().split(') ',1)[1].split();argv=[x.decode() for x in (p/'cmdline').read_bytes().split(b'\0') if x]
assert any(x.endswith('supervise_curb_native_scope_once.py') for x in argv)
print(json.dumps(dict(epoch=time.time(),pid=PID,state=s[0],start_ticks=int(s[19]),argv=argv,no_PPO=True)))
'''.replace('PID',str(pid)))
        save('CURB_NATIVE_DISPATCH_ACTUAL_RECEIPT.json',dict(epoch=time.time(),root=NEW,parent=actual,guard=guard,old_actual_authority=authority,
            actual_new_SDK_native_parent_started=True,no_PPO_or_canonical_transaction=True,new_budget_seconds=0))
        print(json.dumps(dict(root=NEW,parent=actual,actual_started=True,no_PPO=True)))
    finally:cleanup(n,w)
if __name__=='__main__':
    try:main()
    except Exception:
        save('CURB_NATIVE_DISPATCH_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_dispatched_entry=True));raise

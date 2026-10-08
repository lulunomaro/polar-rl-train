"""Actual process/run receipts only; no GPU/PPO or canonical write."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
    code=r'''
from pathlib import Path
import sys,json,time
D=Path('/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008');R=D/'reports'
sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));import supervise_d5_path_review as w
w.verify();st=w.read(R/'D5_STATE.json') if (R/'D5_STATE.json').exists() else None
reports={p.name:w.read(p) for p in R.glob('*.json') if p.name in ('D5_INSTALL_BOUNDARY.json','D5_DISPATCH_STARTED.json','D5_GUARDIAN_STARTED.json','D5_ATTENTION.json','D5_NATIVE20K_PASSED.json','D5_COMPLETE_PPO_PREFLIGHT_PASSED.json','d5_discard_128_PASSED.json','d5_discard_20000_PASSED.json','D5_CURRENT_SAVE.json','D5_ACTIVE_HEALTH.json','D5_REVIEW_READY.json')}
owner=w.identity(w.read(R/'D5_LAUNCHED.json')['owner']['pid']);child=w.identity(st['child']['pid']) if st and st.get('child') else None
g=reports.get('D5_GUARDIAN_STARTED.json');guardian=w.identity(g['pid']) if g else None
b=w.s.q.base.budget_state();s=w.read(w.s.q.ctl.STATE_PATH)
tail=max(0,time.time()-b['active_segment']['accounted_through_epoch']) if b['active_segment'] else 0
log=Path(st['active_log']).read_text(errors='replace')[-5000:] if st and st.get('active_log') and Path(st['active_log']).exists() else ''
v=dict(epoch=time.time(),state=st,actual_owner=owner,actual_child=child,actual_guardian=guardian,reports=reports,
    active_training=s.get('active_training'),budget={k:b[k] for k in ('authorized_training_seconds','charged_training_seconds','remaining_training_seconds','active_segment')},
    actual_tail_adjusted_remaining_seconds=b['remaining_training_seconds']-tail,last_actual_log=log,no_GPU_PPO_or_budget_write=True)
print(json.dumps(v))
'''
    _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    v=json.loads(raw);(R/'D5_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
    print(json.dumps(dict(epoch=v['epoch'],state=v['state'],owner=v['actual_owner'],child=v['actual_child'],reports=list(v['reports']),attention=v['reports'].get('D5_ATTENTION.json'),last_actual_log=v['last_actual_log'][-1600:])))
finally:c.close()

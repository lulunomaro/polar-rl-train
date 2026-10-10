"""Authorized transport and immutable evidence helpers; no launch or budget API."""
from pathlib import Path
import hashlib, json, os, shlex, sys, time
D = Path(__file__).resolve().parent
W = D.parent
R = D / 'reports'
E = '/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007'
WIN = 'D:/MOD4_async_eval/closure_episode_clock2500_v15'
B = '/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'
OLD = '/home/egde/rl_candidates/MOD4_S3_E1_WAVE_G3_INDEPENDENT_20261010'
SHA = '3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
PROTOCOL = 'approved_E1_CURB_derived20mm_mirrored_fullroute_behavior_v1'
H = lambda b: hashlib.sha256(b).hexdigest()

def save(name, value):
    R.mkdir(parents=True, exist_ok=True)
    p = R / name
    assert not p.exists(), str(p)
    p.write_bytes(json.dumps(value, ensure_ascii=False, indent=2).encode())
    return p

def connect_both():
    sys.path.insert(0, str(W/'RM2026_TERRAIN_AUDIT_20261009'))
    from reuse_authorized_session_transport import recover
    for name in ('RM_SSH_PASSWORD','MOD4_EVAL_SSH_PASSWORD'):
        secret, _ = recover(name)
        assert secret
        os.environ[name] = secret
    sys.path.insert(0, str(W/'MOD4_AUTONOMY_SLEEP_20261003'))
    from remote_io import connect
    sys.path.insert(0, str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'))
    from eval_remote_io import connect_eval
    return connect(), connect_eval()

def cleanup(n,w):
    n.close(); w.close()
    for name in ('RM_SSH_PASSWORD','MOD4_EVAL_SSH_PASSWORD'):
        os.environ.pop(name,None)

def linux_json(n, code):
    compile(code, '<curb-read-or-reviewed-operation>', 'exec')
    _,o,e=n.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=45)
    raw=o.read(); err=e.read()
    assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    return json.loads(raw)

def boundary(n):
    return linux_json(n, r'''from pathlib import Path
import json,fcntl,hashlib,time
D=Path(OLD_ROOT);E=Path(CENTRAL);B=Path(BUDGET)
j=lambda p:json.loads(p.read_bytes())
s=j(D/'reports/E1_STATE.json');p=j(D/'reports/e1_wave_G3_isolated_observation_PASSED.json');g=j(D/'reports/E1_GUARDIAN_STARTED.json');l=j(B)
assert s['phase']=='E1_WAVE_G3_isolated_saved_review_ready' and s['child'] is None
ids=[]
for v in (s['owner'],g,dict(pid=p['own_PID_bound_receipt']['pid'],start_ticks=80211793)):
 q=Path('/proc')/str(v['pid']);a=None
 if q.exists():
  st=(q/'stat').read_text().split(') ',1)[1].split();a=dict(state=st[0],start_ticks=int(st[19]))
  assert a['state']=='Z' or a['start_ticks']!=v['start_ticks']
 ids.append(dict(locator=v,actual=a))
assert p['checkpoint']['sha256']=='2b4f5a575d3a4d97013b331e215c503ab86e528a63a92d719a3366a684b52284' and len(p['unique_completed_segment'])==1
assert l['active_segment'] is None and l['authorized_training_seconds']==828000
locks=[]
for q in (Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock'),Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 assert q.is_file(),str(q)
 with q.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(str(q))
approval=j(E/'reports/MOE_TERRAIN_SUBEXPERT_REVISION_004_APPROVAL.json')
current=j(E/'reports/MOE_PLAN_EXECUTION_CURRENT.json')
assert current['terrain_subexpert_revision004']['approved'] is True
print(json.dumps(dict(epoch=time.time(),phase=s['phase'],actual_parent_guardian_child=ids,own_final=p['checkpoint'],unique_segment=p['unique_completed_segment'],two_original_OS_locks_free=locks,canonical_SHA=hashlib.sha256(B.read_bytes()).hexdigest(),authorized_seconds=l['authorized_training_seconds'],remaining_seconds=l['authorized_training_seconds']-l['charged_training_seconds'],active_segment=l['active_segment'],approval=approval,current_revision004=current['terrain_subexpert_revision004'],read_only=True)))
'''.replace('OLD_ROOT',repr(OLD)).replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)))

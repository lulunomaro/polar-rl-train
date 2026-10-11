from pathlib import Path
import sys,json,time,hashlib,shlex
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'MOD4_E1_SLOPE5_INDEPENDENT_PREPARE_20261011'))
from slope_io import E,B,PY,connect_both,cleanup,linux_json,put
OLD='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_FORMAL_DISPATCH_REVIEWED_20261011'
LAST='/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_SNAPSHOT_REVIEWED_20261011'
NEW='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENTRY_REPAIR_20261011'
SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
H=lambda b:hashlib.sha256(b).hexdigest()
def save(name,v):
 p=R/name;assert not p.exists(),p;p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());return p
def boundary(n):
 return linux_json(n,r'''from pathlib import Path
import json,time,hashlib,fcntl
E=Path(CENTRAL);B=Path(BUDGET);D=Path(LASTROOT);j=lambda p:json.loads(p.read_bytes())
s=j(D/'reports/E1_STATE.json');p=j(D/'reports/e1_SLOPE5_independent_observation_PASSED.json');assert s['child'] is None and len(p['unique_completed_segment'])==1
assert p['checkpoint']['sha256']=='24b18846fcff1e0b8da7fd478314fca9cd2ed2b97461ca34f65ef5b7c7ff2411'
assert hashlib.sha256(Path(p['checkpoint']['path']).read_bytes()).hexdigest()==p['checkpoint']['sha256']
exits=[]
for loc in (s['owner'],j(D/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=p['own_PID_bound_receipt']['pid'],start_ticks=83699658)):
 q=Path('/proc')/str(loc['pid']);a=None
 if q.exists():
  f=(q/'stat').read_text().split(') ',1)[1].split();a=dict(state=f[0],start_ticks=int(f[19]));assert a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
 exits.append(dict(locator=loc,actual=a))
l=j(B);assert l['active_segment'] is None and l['authorized_training_seconds']==1188000 and len(l['budget_extensions'])==7
assert 36000+sum(x['additional_training_seconds'] for x in l['budget_extensions'])==1188000
locks=[]
for q in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with q.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(str(q))
c=j(E/'reports/MOE_PLAN_EXECUTION_CURRENT.json');r=c['terrain_subexpert_revision004'];assert r['approved'] and r['active_next_expert']=='E1_CURB' and c['budget_retrain_revision005']['approved']
print(json.dumps(dict(epoch=time.time(),last_own_fullsave=p['checkpoint'],actual_old_exits=exits,two_OS_locks_free=locks,canonical_SHA=hashlib.sha256(B.read_bytes()).hexdigest(),authorized_seconds=l['authorized_training_seconds'],remaining_seconds=l['authorized_training_seconds']-l['charged_training_seconds'],completed_segments=len(l['completed_segments']),active_segment=l['active_segment'],protected_SHA={x:hashlib.sha256((E/'reports'/x).read_bytes()).hexdigest() for x in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')},oldsource=json.loads((Path(OLDROOT)/'reports/SOURCE_FREEZE.json').read_bytes()),no_runtime_or_budget_mutation=True)))
'''.replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)).replace('LASTROOT',repr(LAST)).replace('OLDROOT',repr(OLD)))

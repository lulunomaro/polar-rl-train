from pathlib import Path
import sys,json,time,hashlib,shlex
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
PRE=W/'MOD4_E1_CURB20_133_COMPLETE_REVIEW_20261011'
P=W/'MOD4_E1_CURB20_FULL_STATE_PREPARE_20261011'
sys.path.insert(0,str(P))
from stage_formal_dispatch_reviewed_once import E,B,PY,connect_both,cleanup,linux_json,put
OLD='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_FORMAL_DISPATCH_REVIEWED_20261011'
NEW='/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_INDEPENDENT_20261011'
SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
H=lambda b:hashlib.sha256(b).hexdigest()
def save(name,v):
 p=R/name;assert not p.exists(),p;p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());return p

BOUNDARY=r'''from pathlib import Path
import json,hashlib,fcntl,time
old=Path(OLD_ROOT);E=Path(CENTRAL);B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes())
s=j(old/'reports/E1_STATE.json');assert s['phase']=='E1_CURB20_independent_saved_review_ready' and s['child'] is None
passed=j(old/'reports/e1_CURB20_independent_observation_PASSED.json');g=j(old/'reports/E1_GUARDIAN_STARTED.json')
assert passed['checkpoint']['sha256']=='df0c141d444a6a85b983e49eedad10e91e0b7b264f627bff972dbd7cb1f2c753' and len(passed['unique_completed_segment'])==1
ids=[]
for v in (s['owner'],g,dict(pid=passed['own_PID_bound_receipt']['pid'],start_ticks=81560752)):
 p=Path('/proc')/str(v['pid']);actual=None
 if p.exists():
  a=(p/'stat').read_text().split(') ',1)[1].split();actual=dict(state=a[0],start_ticks=int(a[19]));assert actual['state']=='Z' or actual['start_ticks']!=v['start_ticks']
 ids.append(dict(locator=v,actual=actual))
l=j(B);assert l['authorized_training_seconds']==828000 and l['active_segment'] is None
locks=[]
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(str(p))
c=j(E/'reports/MOE_PLAN_EXECUTION_CURRENT.json');rev=c['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_SLOPE'
assert not list((E/'eval_queue').glob('*-135-*')) and not list((E/'results').glob('*-135-*'))
print(json.dumps(dict(epoch=time.time(),actual_old_parent_guardian_child_exited=ids,old_own_fullsave_PASSED=passed['checkpoint'],unique_original_settled_segment=passed['unique_completed_segment'],two_actual_OS_locks_free=locks,canonical_SHA=hashlib.sha256(B.read_bytes()).hexdigest(),remaining_seconds=l['authorized_training_seconds']-l['charged_training_seconds'],active_segment=l['active_segment'],current_revision004=rev,source_freeze=j(old/'reports/SOURCE_FREEZE.json'),source_selected=j(old/'reports/SOURCE_SELECTED.json'),protected_SHA={n:hashlib.sha256((E/'reports'/n).read_bytes()).hexdigest() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')},no_runtime_or_budget_mutation=True)))
'''
def boundary(n):return linux_json(n,BOUNDARY.replace('OLD_ROOT',repr(OLD)).replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)))

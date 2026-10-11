from direction_io import *

def main():
    root=json.loads((R/'DIRECTION_STARTUP_ACTIVE_ROOT.json').read_bytes())['root']
    n,w=io.connect_both()
    try:
        code=r'''from pathlib import Path
import sys,json,time,hashlib,torch,fcntl
D=Path(ROOT);R=D/'reports';j=lambda p:json.loads(p.read_bytes())
sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
p=R/'e1_CURB20_direction_repair_observation_PASSED.json'
if not p.exists():
 print(json.dumps(dict(epoch=time.time(),pending=True,own_final_not_yet_generated=True,state=j(R/'E1_STATE.json'),no_mutation=True)));raise SystemExit(0)
v=j(p);ck=Path(v['checkpoint']['path']);run=Path(v['run']);pid=v['own_PID_bound_receipt']['pid']
assert ck.is_relative_to(D/'learning_logs') and ck.parent==run and v['source_sha256']==SOURCE_SHA and not v['discarded_preflight']
from curb20_direction_fullsave_cpu import fullsave
info=fullsave(ck);assert info['sha256']==v['checkpoint']['sha256'] and info['direction_state_verified']
assert j(run/'latest_complete.json')['pid']==pid and j(run/'latest_complete.json')['checkpoint']==str(ck)
m=j(run/'run_manifest.json');freeze=j(R/'SOURCE_FREEZE.json')
assert m['source_map']==freeze['sha256'] and m['init_checkpoint_sha256']==SOURCE_SHA
for name,h in m['src_sha256'].items():assert hashlib.sha256((run/'src_snapshot'/name).read_bytes()).hexdigest()==h
b=j(Path(BUDGET));seg=[s for s in b['completed_segments'] if s['pid']==pid]
assert len(seg)==1 and seg==v['unique_completed_segment']
h=v['health'];assert h['actual_physics_callbacks']==h['expected_physics_callbacks']==h['control_steps']*4
assert v['actual_environment_steps']==h['control_steps']*20000 and v['actual_updates']*24==h['control_steps']
markers={q.name:j(q) for q in run.glob('*_STARTUP_VERIFIED.json')}
assert all(x['source_sha256']==SOURCE_SHA for x in markers.values())
direction=markers['E1_CURB_DIRECTION_RESUME_STARTUP_VERIFIED.json']
assert direction['passed'] and direction['explicit_new_episode_direction_scope'] and direction['actual_CUDA_direction_disk_roundtrip_exact'] and direction['saved_source_episode_plus_one_verified']
fresh=j(R/'ENTRY_FRESH_SAME_SCOPE_PASSED.json');assert fresh['passed'] and fresh['actual_control_steps']==fresh['actual_additional_PPO_updates']==0
freshmarkers={q.name:j(q) for q in (D/'fresh_same_scope').glob('*_STARTUP_VERIFIED.json')}
fd=freshmarkers['E1_CURB_DIRECTION_RESUME_STARTUP_VERIFIED.json']
assert fd['passed'] and not fd['explicit_new_episode_direction_scope'] and fd['predecessor_direction_state_restored_exact'] and fd['actual_CUDA_direction_disk_roundtrip_exact']
import supervise_curb20_direction_startup_reviewed_once as ctrl
st=j(R/'E1_STATE.json');superstate=j(ctrl.s.q.ctl.STATE_PATH)
def proc(loc):
 p=Path('/proc')/str(loc['pid'])
 if not p.exists():return None
 a=(p/'stat').read_text().split(') ',1)[1].split()
 return dict(pid=loc['pid'],state=a[0],start_ticks=int(a[19]),argv=[x.decode(errors='replace') for x in (p/'cmdline').read_bytes().split(b'\0') if x],same_original_identity=int(a[19])==loc.get('start_ticks',int(a[19])))
locs=[st['owner'],j(R/'E1_GUARDIAN_STARTED.json'),v['own_PID_bound_receipt']]
procs=[proc(x) for x in locs];exited=all(not p or p['state']=='Z' or not p['same_original_identity'] for p in procs)
locks=[]
for q in (Path(BUDGET).parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with q.open('r+') as f:
  try:fcntl.flock(f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(f.fileno(),fcntl.LOCK_UN)
  except BlockingIOError:free=False
 locks.append(dict(path=str(q),OS_lock_free=free,persistent_file_is_not_held_assertion=True))
published=j(R/'E1_CURB_DIRECTION_ASYNC_PUBLISHED.json') if (R/'E1_CURB_DIRECTION_ASYNC_PUBLISHED.json').exists() else None
assert not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,pending=False,root=str(D),source_SHA=SOURCE_SHA,own_checkpoint=info,actual_finite_tensor_count=info['finite_tensors'],CPU_noCUDA=True,own_PID=pid,
 actual_source_count=len(freeze['sha256']),actual_snapshot_file_count=sum(q.is_file() for q in (run/'src_snapshot').rglob('*')),own_manifest_PID_receipt_snapshot_exact=True,
 own_unique_completed_segment=seg,health=h,actual_updates=v['actual_updates'],actual_environment_steps=v['actual_environment_steps'],startup_markers=markers,fresh_same_scope_direction=fd,
 actual_state=st,actual_processes=procs,locks=locks,active_segment=b['active_segment'],supervisor_active=superstate.get('active_training'),closeout_ready=exited and all(x['OS_lock_free'] for x in locks) and b['active_segment'] is None and not superstate.get('active_training'),
 authorized_training_seconds=b['authorized_training_seconds'],extensions=len(b['budget_extensions']),remaining_seconds=b['remaining_training_seconds'],budget_SHA=hashlib.sha256(Path(BUDGET).read_bytes()).hexdigest(),published=published,
 explicit_new_geometry_entry_direction_disclosed=True,not_PhysX_exactresume=True,no_GPU_or_budget_write=True)))
'''.replace('ROOT',repr(root)).replace('SOURCE_SHA',repr(SHA)).replace('BUDGET',repr(io.B))
        v=run(n,code);p=save('DIRECTION_OWN_FORMAL_CPU_ACTUAL_'+str(time.time_ns())+'.json',v)
        print(json.dumps(dict(report=str(p),passed=v.get('passed'),pending=v.get('pending'),closeout_ready=v.get('closeout_ready'),checkpoint=v.get('own_checkpoint'),updates=v.get('actual_updates'),health=v.get('health'),source_count=v.get('actual_source_count'),snapshot_count=v.get('actual_snapshot_file_count'),published_cases=[x['job_id'] for x in (v.get('published') or {}).get('jobs',[])])))
    finally:io.cleanup(n,w)

if __name__=='__main__':main()

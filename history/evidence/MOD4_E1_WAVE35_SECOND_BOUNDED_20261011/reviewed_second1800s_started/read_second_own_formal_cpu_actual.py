"""Read only own final if actually generated; strict source/startup/save/ledger identity."""
from second_io import *
import ast

def main():
 proof=json.loads(sorted(R.glob('SECOND_OWN_STARTUP_CPU_ACTUAL_[0-9]*.json'))[-1].read_bytes());child=proof['own_child']
 tree=ast.parse((PRIOR/'verify_wave_own_startup_save_cpu_actual.py').read_text(encoding='utf8'))
 startup=next(x.value for x in ast.walk(tree) if isinstance(x,ast.Constant) and isinstance(x.value,str) and x.value.startswith('from pathlib import Path\nimport sys,json,time,torch,hashlib'))
 start=startup.index('startup={};indices=[]');end=startup.index("p=Path(rec['checkpoint']);info=")
 checks=startup[start:end]
 code=r'''from pathlib import Path
import sys,json,time,hashlib,torch,fcntl
D=Path(ROOT_TOKEN);R=D/'reports';sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave35_second_bounded_once as own
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=R/'e1_WAVE35_second_bounded_observation_PASSED.json'
if not p.exists():
 print(json.dumps(dict(epoch=time.time(),pending=True,own_final_not_yet_generated=True,state=j(R/'E1_STATE.json'),no_mutation=True)));raise SystemExit(0)
v=j(p);ck=Path(v['checkpoint']['path']);run=Path(v['run']);rec=j(run/'latest_complete.json');pid=rec['pid'];manifest=j(run/'run_manifest.json');health=v['health']
assert pid==CHILD_PID_TOKEN==v['own_PID_bound_receipt']['pid'] and rec['checkpoint']==str(ck) and ck.parent==run and ck.is_relative_to(D/'learning_logs') and not v['discarded_preflight']
info=own.fullsave(ck);assert info['sha256']==v['checkpoint']['sha256'] and info['finite_tensors']==102
freeze=j(R/'SOURCE_FREEZE.json');assert len(freeze['sha256'])==369 and manifest['source_map']==freeze['sha256'] and manifest['init_checkpoint_sha256']==own.SOURCE_SHA
for name,sha in manifest['src_sha256'].items():assert h(run/'src_snapshot'/name)==sha,name
rolling=j(run/'rolling_source_freeze.json');assert rolling['sha256']==freeze['sha256']
for name,sha in rolling['sha256'].items():assert h(run/'e1_source_snapshot'/name)==sha,name
CHECKS_TOKEN
assert health['control_steps']==v['actual_updates']*24 and v['actual_environment_steps']==health['control_steps']*20000
assert j(run/'RETENTION_COMMAND_ACTUAL.json')['actual_controls']==health['control_steps']
assert h(own.source())==own.SOURCE_SHA
B=Path(BUDGET_TOKEN);b=j(B);seg=[s for s in b['completed_segments'] if s['pid']==pid];assert len(seg)==1 and seg==v['unique_completed_segment']
assert b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7
st=j(R/'E1_STATE.json');locs=[st['owner'],j(R/'E1_GUARDIAN_STARTED.json'),dict(pid=pid,start_ticks=CHILD_START_TOKEN)]
procs=[];exited=True
for loc in locs:
 actual=own.identity(loc['pid']);procs.append(actual);exited=exited and (not actual or actual['state']=='Z' or actual['start_ticks']!=loc['start_ticks'])
locks=[]
for q in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with q.open('r+') as f:
  try:fcntl.flock(f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(f.fileno(),fcntl.LOCK_UN)
  except BlockingIOError:free=False
 locks.append(dict(path=str(q),OS_lock_free=free,persistent_file_is_not_held_assertion=True))
superstate=j(own.m.s.q.ctl.STATE_PATH);pub=R/'E1_143-e1-wave35-second-bounded_ASYNC_PUBLISHED.json';published=j(pub) if pub.exists() else None
assert not torch.cuda.is_initialized()
v=dict(epoch=time.time(),passed=True,pending=False,root=str(D),source_SHA=own.SOURCE_SHA,own_checkpoint=info,actual_finite_tensor_count=102,CPU_noCUDA=True,own_PID=pid,actual_source_count=369,actual_snapshot_file_count=sum(p.is_file() for p in (run/'src_snapshot').rglob('*')),own_source_freeze_file_count=sum(p.is_file() for p in (run/'e1_source_snapshot').rglob('*')),own_manifest_PID_receipt_snapshot_exact=True,own_unique_completed_segment=seg,health=health,actual_updates=v['actual_updates'],actual_environment_steps=v['actual_environment_steps'],startup_markers=startup,actual_state=st,actual_processes=procs,actual_original_processes_exited=exited,locks=locks,active_segment=b['active_segment'],supervisor_active=superstate.get('active_training'),closeout_ready=exited and all(x['OS_lock_free'] for x in locks) and b['active_segment'] is None and not superstate.get('active_training') and st['phase']=='E1_WAVE35_second_bounded_saved_review_ready',authorized_training_seconds=b['authorized_training_seconds'],extensions=len(b['budget_extensions']),remaining_seconds=b['remaining_training_seconds'],budget_SHA=h(B),published=published,same_G3_samecommand_restored_exact=True,not_PhysX_exactresume=True,no_GPU_or_budget_write=True)
print(json.dumps(v))
'''.replace('CHECKS_TOKEN',checks).replace('ROOT_TOKEN',repr(ROOT)).replace('BUDGET_TOKEN',repr(io.B)).replace('CHILD_PID_TOKEN',str(child['pid'])).replace('CHILD_START_TOKEN',str(child['start_ticks']))
 n,w=io.connect_both()
 try:
  v=run(n,code);p=save('SECOND_OWN_FORMAL_CPU_ACTUAL_'+str(time.time_ns())+'.json',v)
  print(json.dumps(dict(report=str(p),passed=v.get('passed'),pending=v.get('pending'),closeout_ready=v.get('closeout_ready'),checkpoint=v.get('own_checkpoint'),updates=v.get('actual_updates'),health=v.get('health'),source_count=v.get('actual_source_count'),snapshot_count=v.get('actual_snapshot_file_count'))))
 finally:io.cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('SECOND_OWN_FORMAL_CPU_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),reader_only_no_GPU_or_budget_replay=True));raise

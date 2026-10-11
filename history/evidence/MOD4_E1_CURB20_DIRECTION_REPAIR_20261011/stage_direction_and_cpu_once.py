from direction_io import *
import traceback,ast
P=D/'payload'
def main():
 save('DIRECTION_STAGE_STARTED.json',dict(epoch=time.time(),root=NEW,only_direction_axis=True,no_new_budget_seconds=0))
 n,w=io.connect_both()
 try:
  with w.open_sftp() as f:
   names=f.listdir('D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs');number=140
   assert not any('-'+str(number)+'-' in x for x in names)
  copied=run(n,'''from pathlib import Path
import json,time,hashlib,shutil,fcntl
old=Path(OLDROOT);new=Path(NEWROOT);E=Path(CENTRAL);B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes())
assert not new.exists();before=B.read_bytes();assert j(B)['active_segment'] is None
assert not any(list((E/d).glob('*-140-*')) for d in ('eval_queue','eval_results','results'))
st=j(old/'reports/E1_STATE.json');assert st['child'] is None and st['phase']=='E1_CURB20_entry_repair_saved_review_ready'
for loc in (st['owner'],j(old/'reports/E1_GUARDIAN_STARTED.json'),j(old/'reports/e1_CURB20_entry_repair_observation_PASSED.json')['own_PID_bound_receipt']):
 p=Path('/proc')/str(loc['pid']);assert not p.exists() or (p/'stat').read_text().split(') ',1)[1].split()[0]=='Z'
for q in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with q.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
freeze=j(old/'reports/SOURCE_FREEZE.json');assert len(freeze['sha256'])==410
new.mkdir();(new/'reports').mkdir()
for name,h in freeze['sha256'].items():
 p=old/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==h;q=new/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for name in ('SOURCE_SELECTED.json','CURB_FOUR_CASE_TEMPLATES.json'):shutil.copy2(old/'reports'/name,new/'reports'/name)
job=dict(epoch=time.time(),number=140,actual_windows_jobs_unused=True,actual_central_queue_results_unused=True)
(new/'reports/CANDIDATE_JOB_UNUSED_ACTUAL.json').write_text(json.dumps(job,indent=2))
assert B.read_bytes()==before
print(json.dumps(dict(epoch=time.time(),source_freeze=freeze,job=job,old410_all_bytes_exact=True,old_actual_exit_locks_free_idle=True,no_GPU_or_budget_action=True)))
'''.replace('OLDROOT',repr(OLD)).replace('NEWROOT',repr(NEW)).replace('CENTRAL',repr(io.E)).replace('BUDGET',repr(io.B)))
  save('DIRECTION_SOURCE410_COPIED.json',copied);hashes=dict(copied['source_freeze']['sha256'])
  with n.open_sftp() as f:
   for p in sorted(P.rglob('*.py')):
    if '__pycache__' in p.parts:continue
    raw=p.read_bytes();ast.parse(raw);name=p.relative_to(P).as_posix();assert name not in hashes;io.put(f,NEW+'/'+name,raw);hashes[name]=H(raw)
   freeze=dict(candidate_root=NEW,sha256=hashes,old410_allbytes_exact=True,new_direction_scope=True)
   io.put(f,NEW+'/reports/SOURCE_FREEZE.json',json.dumps(freeze,indent=2).encode());save('DIRECTION_SOURCE_FREEZE.json',freeze)
  cpu=run(n,'''from pathlib import Path
import sys,json,time,torch
D=Path(NEWROOT);C=D/'isaac/mod4';sys.path.insert(0,str(D));sys.path.insert(0,str(C));torch.set_num_threads(1)
from curb20_direction_target_cpu import verify
v=verify(D);v['epoch']=time.time();(D/'reports/DIRECTION_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2))
import supervise_curb20_direction_once as own
own.verify();own.wait_existing();assert own.D==D and own.R==D/'reports' and own.CODE==C and own.inherited.D==D and own.inherited.R==D/'reports'
assert not torch.cuda.is_initialized()
print(json.dumps(dict(passed=True,component=v,correct_new_import_main_and_Popen_paths=True,no_GPU_or_PPO_dispatch=True)))
'''.replace('NEWROOT',repr(NEW)))
  save('DIRECTION_TARGET_CPU_PASSED.json',cpu);print(json.dumps(dict(root=NEW,source_count=len(hashes),CPU_passed=True,no_GPU_launch=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('DIRECTION_STAGE_OR_CPU_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_once_replay=True));raise

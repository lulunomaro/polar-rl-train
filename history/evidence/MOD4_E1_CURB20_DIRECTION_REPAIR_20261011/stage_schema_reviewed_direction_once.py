from direction_io import *
import traceback
PREVIOUS=NEW
NEW='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_DIRECTION_SCHEMA_REVIEWED_20261011'
def main():
 n,w=io.connect_both()
 try:
  v=run(n,'''from pathlib import Path
import json,sys,time,torch,shutil,hashlib,fcntl
old=Path(PREVROOT);D=Path(NEWROOT);B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes())
assert not D.exists() and not (old/'reports/E1_DISPATCH_STARTED.json').exists() and j(B)['active_segment'] is None
for q in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with q.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
before=B.read_bytes();freeze=j(old/'reports/SOURCE_FREEZE.json');assert len(freeze['sha256'])==420
D.mkdir();(D/'reports').mkdir()
for name,h in freeze['sha256'].items():
 p=old/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==h;q=D/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
name='isaac/mod4/curb20_direction_schema_reviewed_target_cpu.py';p=old/name;shutil.copy2(p,D/name);freeze['sha256'][name]=hashlib.sha256(p.read_bytes()).hexdigest();freeze['candidate_root']=str(D)
for name in ('SOURCE_SELECTED.json','CURB_FOUR_CASE_TEMPLATES.json','CANDIDATE_JOB_UNUSED_ACTUAL.json'):shutil.copy2(old/'reports'/name,D/'reports'/name)
(D/'reports/SOURCE_FREEZE.json').write_text(json.dumps(freeze,indent=2))
C=D/'isaac/mod4';sys.path.insert(0,str(D));sys.path.insert(0,str(C));torch.set_num_threads(1)
from curb20_direction_schema_reviewed_target_cpu import verify
v=verify(D);v['epoch']=time.time();v['actual_actor_critic_separate_schema_verified']=True
(D/'reports/DIRECTION_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2))
import supervise_curb20_direction_once as own
own.verify();own.wait_existing();assert own.D==D and own.R==D/'reports' and own.CODE==C and own.inherited.D==D and own.inherited.R==D/'reports'
assert not torch.cuda.is_initialized() and B.read_bytes()==before
print(json.dumps(dict(passed=True,root=str(D),source_freeze=freeze,component=v,correct_new_import_main_and_Popen_paths=True,no_GPU_or_PPO_dispatch=True,original_CPU_errors_preserved=True)))
'''.replace('PREVROOT',repr(PREVIOUS)).replace('NEWROOT',repr(NEW)).replace('BUDGET',repr(io.B)))
  save('DIRECTION_SCHEMA_TARGET_CPU_PASSED.json',v);save('DIRECTION_ACTIVE_ROOT.json',dict(root=NEW,source_count=len(v['source_freeze']['sha256']),CPU_passed=True,old_CPU_only_root_not_launched=True))
  print(json.dumps(dict(root=NEW,CPU_passed=True,source_count=len(v['source_freeze']['sha256']),no_GPU_launch=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('DIRECTION_SCHEMA_STAGE_CPU_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_budget_write=True));raise

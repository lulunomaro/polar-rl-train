"""Read-only actual split proof CPU admission; add388 isolated formal controller."""
from stage_fresh_process_resume_once import D,R,E,B,PY,connect_both,cleanup,linux_json,H,save,put
from pathlib import Path
import json,time,shlex,traceback
OLD='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_FRESH_PROCESS_REVIEWED_20261011'
NEW='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_SPLIT_STATE_ADMITTED_20261011'
def main():
 save('SPLIT_STATE_STAGE_STARTED.json',dict(epoch=time.time(),trial_id='CURB388-SPLIT-COMPLETED-STATE-CPU-ADMISSION-01',no_GPU_or_budget_action=True,old_fullstate_errors_preserved=True))
 n,w=connect_both()
 try:
  v=linux_json(n,r'''from pathlib import Path
import json,time,hashlib,shutil,fcntl
old=Path(OLD);new=Path(NEW);B=Path(BUDGET);budget=B.read_bytes();j=lambda p:json.loads(p.read_bytes());assert not new.exists()
st=j(old/'reports/E1_STATE.json');att=j(old/'reports/E1_ATTENTION.json');assert not att['own_child_still_alive'] and att['active_segment'] is None
for loc in [st['owner'],st['child'],j(old/'reports/E1_GUARDIAN_STARTED.json')]:
 p=Path('/proc')/str(loc['pid'])
 if p.exists():a=(p/'stat').read_text().split(') ',1)[1].split();assert a[0]=='Z' or int(a[19])!=loc['start_ticks']
l=j(B);assert l['active_segment'] is None and l['authorized_training_seconds']==828000
error=(old/'reports/FRESH_PROCESS_PROBE_ERROR.txt').read_bytes();assert b"'Logger' object has no attribute 'writer'" in error
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
f=j(old/'reports/SOURCE_FREEZE.json');assert len(f['sha256'])==386;new.mkdir();(new/'reports').mkdir()
for name,h in f['sha256'].items():
 p=old/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==h;q=new/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for name in ('SOURCE_SELECTED.json','CURB132_COMPLETE_ACTUAL_REVIEW.json','CURB_REUSED_NATIVE.json','CURB_FOUR_CASE_TEMPLATES.json','CURB_TARGET_FULLSTATE_CPU_PASSED.json','CURB_ENVIRONMENT_VIEW_CPU_PASSED.json','CURB_FRESH_PROCESS_CPU_PASSED.json','REUSED_SMALL128.json','FRESH_PROCESS_BIG_CORE_VERIFIED.json'):
 shutil.copy2(old/'reports'/name,new/'reports'/name)
assert B.read_bytes()==budget
print(json.dumps(dict(epoch=time.time(),source_freeze=f,actual_old386_exit_two_OS_locks_free=True,all386_source_bytes_preserved=True,canonical_SHA=hashlib.sha256(budget).hexdigest(),fresh_probe_no_canonical_segment=True,original_logger_error=dict(path=str(old/'reports/FRESH_PROCESS_PROBE_ERROR.txt'),bytes=len(error),sha256=hashlib.sha256(error).hexdigest(),text=error.decode()))))
'''.replace('Path(OLD)','Path('+repr(OLD)+')').replace('Path(NEW)','Path('+repr(NEW)+')').replace('BUDGET',repr(B)))
  save('SPLIT_STATE_386_COPIED.json',v)
  with n.open_sftp() as f:
   freeze=v['source_freeze'];hashes=dict(freeze['sha256'])
   for p in sorted((D/'split_admission_payload').rglob('*')):
    if not p.is_file():continue
    name=p.relative_to(D/'split_admission_payload').as_posix();raw=p.read_bytes();compile(raw,name,'exec');assert name not in hashes;put(f,NEW+'/'+name,raw);hashes[name]=H(raw)
   assert len(hashes)==388;freeze=dict(freeze,candidate_root=NEW,sha256=hashes,all386_source_bytes_preserved=True,new_CPU_split_actual_admission=True)
   put(f,NEW+'/reports/SOURCE_FREEZE.json',json.dumps(freeze,indent=2).encode());save('SPLIT_STATE_SOURCE_FREEZE.json',freeze)
  code=r'''from pathlib import Path
import sys,json,time,torch
D=Path(ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_curb20_split_state_admission_once as own
own.verify();own.wait_existing();proof=own.admit(D,own.fullsave);proof.update(epoch=time.time(),source_count=388,passed=True,old386_logger_save_error_only_preserved=True,formal_fullsave_and_behavior_still_required=True)
assert not torch.cuda.is_initialized();(D/'reports/CURB_SPLIT_FULLSTATE_CPU_PASSED.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
'''.replace('ROOT',repr(NEW))
  _,o,e=n.exec_command(PY+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:save('SPLIT_STATE_CPU_REJECTED.json',dict(epoch=time.time(),returncode=rc,stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace'),no_GPU_or_budget_action=True));raise RuntimeError('Independent actual split evidence rejected')
  cpu=json.loads(raw);save('SPLIT_STATE_TARGET_CPU_PASSED.json',cpu)
  print(json.dumps(dict(root=NEW,source_count=388,CPU_passed=True,actual384_fullsave_and386_sameCURB_restore_proven=True,partial_probe_save_not_full=True,no_GPU_preflight_repeated=True)))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('SPLIT_STATE_STAGE_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_blind_stage_replay=True));raise

from pathlib import Path
import sys,json,time,importlib,subprocess,traceback,hashlib
from datetime import datetime,timezone,timedelta
from local_archive_capture import capture
import archive_local_temp_stage_once as prepared
D=prepared.D;R=prepared.R;REPO=prepared.REPO;ID=prepared.ID;archive=prepared.archive
DEST=REPO/'history/evidence'/D.name/'local128_lock_read_reviewed_actual'
def main():
 status=archive.gitio.g('status','--porcelain')
 assert status=='?? history/evidence/MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/' and not archive.gitio.g('diff','--cached','--name-only')
 assert not archive.gitio.g('tag','--list','*'+ID) and not DEST.exists()
 assert (R/'LOCAL_TEMP_ARCHIVE_STARTED.json').exists()
 prepared.save('LIVE_LOCK_ARCHIVE_READ_REJECTION_ACTUAL.json',dict(epoch=time.time(),original_reader='archive_local_temp_stage_once.py',error='PermissionError: [Errno 13] Permission denied',actual_path=str(D/'LOCAL_GPU_EXCLUSIVE.lock'),bytes=1,independent_read_onebyte_same_error=True,training_owns_native_byte_lock=True,no_GPU_or_worker_or_lock_mutation=True,partial_original_capture_retained=True,no_record_commit_tag_executed_before_error=True))
 old=archive.gitio.refs();rows,files=capture(DEST)
 partial=[]
 for p in sorted(prepared.DEST.rglob('*')):
  if not p.is_file():continue
  sha=hashlib.sha256(p.read_bytes()).hexdigest();name=p.relative_to(REPO).as_posix();row=dict(source_path=str(p),bytes=p.stat().st_size,sha256=sha,capture='original_failed_partial_capture_also_retained_exact',Git_path=name,archived_sha256=sha);rows.append(row);partial.append(row);files.append(name)
 pp=DEST/'ORIGINAL_FAILED_PARTIAL_CAPTURE_INDEX.json';pp.write_text(json.dumps(dict(epoch=time.time(),entries=partial,original_failed_capture_not_marked_complete=True),indent=2),encoding='utf8');files.append(pp.relative_to(REPO).as_posix())
 sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment');original=rec.git
 def short_git(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+bytes([0]) for v in args[2:]),capture_output=True,check=True);return p.stdout.decode().strip()
  return original(*args)
 rec.git=short_git;sys.argv=['record_experiment.py','--id',ID,'--title','Adapt isolated local5070 full-state Wave50 branch and start saved temporary PPO','--kind','repair','--note-file',str(D/'ACTUAL_LOCAL_ADAPTATION_AND_TEMP_TRAIN_STAGE_REPORT.md'),'--files',*files,'--validation','Explicit Windows128-env fullstate projection; original geometry/107floating actorcriticstdoptimizer/allDRRNG strict CPUCUDA diskrestore. SDK120 and fullrestore48 actual physicalpass. NativeDLL/fsync/CPUproof/observerTOML/liveOSlock reader errors retained. Ownv10 positivePPO fullcheckpoint saved; hourlylocalonly monitor actualverified/remote paused. Canonical reconciliation pending; no kill or sourceoverwrite.','--push'];rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=archive.gitio.g('rev-parse','HEAD');obj=archive.gitio.g('rev-parse',tag);archive.verify(rows,old,head,tag,obj)
 prepared.save('LOCAL_TEMP_STAGE_GIT_RECORDED.json',dict(epoch=time.time(),passed=True,commit=head,tag=tag,tagobject=obj,remote_main_tag_peeled_verified=True,all_old_tags_preserved=len(old),saved_sources=len(rows),push_pending=False,live_OS_lock_unreadable_SHA_unknown=True,receipt_and_future_actual_reports_require_ordinary_supplement=True))
 print(json.dumps(dict(passed=True,commit=head,tag=tag,tagobject=obj,saved_sources=len(rows),old_tags=len(old))))
if __name__=='__main__':
 try:main()
 except BaseException:prepared.save('LOCAL_TEMP_LOCK_REVIEWED_STAGE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),inspectexistingobjects_no_record_tag_commit_replay=True));raise

from pathlib import Path
import sys,json,time,importlib,subprocess,traceback
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_SCUT_WAVE50_GATE_COMPARE_20261012'))
import archive_actual_reference_stage_once as archive
archive.FOLDERS=(D,)
ID='local5070-wave50-fullstate-adapted-temporary-ppo-started'
DEST=REPO/'history/evidence'/D.name/'local128_temp_actual'
def save(name,v):
 p=R/name;assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def main():
 assert not archive.gitio.g('status','--porcelain') and not archive.gitio.g('diff','--cached','--name-only')
 assert not archive.gitio.g('tag','--list','*'+ID) and not DEST.exists()
 assert json.loads((R/'LOCAL_TEMP_HOURLY_MONITOR_ACTUAL_VERIFIED.json').read_bytes())['passed']
 latest=max(R.glob('LOCAL_TRAINING_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]));a=json.loads(latest.read_bytes())
 assert a['own_saved_positive_PPO_CPU']['passed'] and not a['error']
 assert a['own_saved_positive_PPO_CPU']['actual_updates']>=4
 old=archive.gitio.refs();save('LOCAL_TEMP_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_main=archive.gitio.g('rev-parse','HEAD'),old_tags=len(old),actual_ref=str(latest)))
 rows,files=archive.capture(DEST)
 sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment');original=rec.git
 def short_git(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+bytes([0]) for v in args[2:]),capture_output=True,check=True);return p.stdout.decode().strip()
  return original(*args)
 rec.git=short_git
 sys.argv=['record_experiment.py','--id',ID,'--title','Adapt isolated local5070 full-state Wave50 branch and start saved temporary PPO','--kind','repair','--note-file',str(D/'ACTUAL_LOCAL_ADAPTATION_AND_TEMP_TRAIN_STAGE_REPORT.md'),'--files',*files,'--validation','Explicit Windows backend and deterministic128-env projection; original geometry and full actorcriticstdoptimizer/DR/RNG strict CPUCUDA roundtrip. SDK120/fullrestore48 physical probes passed. Retained nativeDLL/SDK/fsync/CPUproof failures. Same128 v10 actual positivePPO/107floating full checkpoint and originalhealth verified. Bounded1800s local-only hourlymonitor verified; remote paused/canonical reconciliation pending.','--push'];rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=archive.gitio.g('rev-parse','HEAD');obj=archive.gitio.g('rev-parse',tag)
 archive.verify(rows,old,head,tag,obj)
 save('LOCAL_TEMP_STAGE_GIT_RECORDED.json',dict(epoch=time.time(),passed=True,commit=head,tag=tag,tagobject=obj,remote_main_tag_peeled_verified=True,all_old_tags_preserved=len(old),saved_sources=len(rows),push_pending=False,receipt_and_future_run_reports_require_ordinary_supplement=True))
 print(json.dumps(dict(passed=True,commit=head,tag=tag,tagobject=obj,saved_sources=len(rows),old_tags=len(old))))
if __name__=='__main__':
 try:main()
 except BaseException:save('LOCAL_TEMP_STAGE_GIT_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),inspect_existingobjects_no_record_tag_commit_replay=True));raise

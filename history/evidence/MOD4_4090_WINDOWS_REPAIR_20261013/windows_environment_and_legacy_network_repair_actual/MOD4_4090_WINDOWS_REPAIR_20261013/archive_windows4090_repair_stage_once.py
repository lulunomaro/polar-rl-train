from pathlib import Path
import sys,time,json,subprocess,importlib,traceback
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_SCUT_WAVE50_GATE_COMPARE_20261012'))
import archive_actual_reference_stage_once as a
ID='wave50-windows4090-env-start-two-legacy-ssh-flood-monitors-retired'
DEST=REPO/'history/evidence'/D.name/'windows_environment_and_legacy_network_repair_actual'
a.FOLDERS=(W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013',W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013',D,W/'MOD4_LOCAL_WAVE50_ACTION_EFFECTIVE_REPAIR_20261013',W/'MOD4_3060_DIRECT_FACTOR_20261013')
def main():
 assert not a.gitio.g('status','--porcelain') and not a.gitio.g('tag','--list','*'+ID) and not DEST.exists()
 for name in ('OLD_LINUX_POLLER_HUMAN_EMERGENCY_STOP_ACTUAL.json','OLD_MIRROR_SSH_FLOOD_HUMAN_EMERGENCY_STOP_ACTUAL.json','WINDOWS4090_AFTER_MIRROR_STOP_NATIVE_SSH_ACTUAL.json'):
  assert json.loads((D/'reports'/name).read_bytes())['passed']
 old=a.gitio.refs();rows,files=a.capture(DEST)
 sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment');original=rec.git
 def short_git(*args):
  if args[:2]==('add','--'):
   r=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in args[2:]),capture_output=True,check=True);return r.stdout.decode().strip()
  return original(*args)
 rec.git=short_git;sys.argv=['record_experiment.py','--id',ID,'--title','Retire two legacy SSH flooding monitors and dispatch isolated Windows4090 environment installation','--kind','repair','--note-file',str(D/'ACTUAL_WINDOWS4090_REPAIR_STAGE_REPORT.md'),'--files',*files,'--validation','Exact idle E1 task retired and XML retained. Additional mirror193 sockets disappeared after exact child stop; wrapper natural exit/sourceSHA unchanged; native Win10 SSH actual restored. Full donor/source/ABI/offset-aware v3 CPU-only strict proofs; old false/raw preserved. Detached CPU environment stage launched; subsequent Python creation failure retained, no GPU/PPO or installed-ready claim. Local pause, new3060 direct-local CPU preparation, canonical pending unchanged.','--push'];rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=a.gitio.g('rev-parse','HEAD');obj=a.gitio.g('rev-parse',tag);a.verify(rows,old,head,tag,obj)
 report=dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,remote_main_tag_peeled_verified=True,all_old_tag_objects_preserved=len(old),actual_tracked_SHA_verified=True,saved_sources=len(rows),later_reports_require_ordinary_supplement=True)
 (D/'reports/WINDOWS4090_REPAIR_STAGE_GIT_RECORDED.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report))
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('WINDOWS4090_STAGE_GIT_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),continue_existing_objects_no_record_tag_commit_replay=True)),encoding='utf8');raise

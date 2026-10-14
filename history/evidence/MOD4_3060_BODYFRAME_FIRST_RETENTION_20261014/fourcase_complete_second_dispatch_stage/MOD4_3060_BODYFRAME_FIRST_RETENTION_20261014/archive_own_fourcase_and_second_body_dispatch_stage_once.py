"""One unique actual stage; later positive saves and closeout are ordinary supplements."""
from pathlib import Path
import importlib,json,subprocess,sys,time,traceback
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;S=W/'MOD4_LINUX_WAVE50_BODYFRAME_SECOND_PREPARE_20261014';R=D/'reports';REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'));import append_large_install_evidence_import_reviewed_git as cap
def main():
 ID='wave50-bodyframe-full-fourcase-reviewed-second-linux20k-started';dest=REPO/'history/evidence'/D.name/'fourcase_complete_second_dispatch_stage'
 assert not cap.g('status','--porcelain') and not dest.exists() and not cap.g('tag','--list','*'+ID)
 actual=json.loads((R/'BODYFRAME_FIRST_F516_THREE_RETENTION_PAIRS_COMPLETE_ACTUAL_CPU_REVIEW.json').read_bytes());assert actual['passed'] and actual['all_three_inherited_full1500_complete'] and not actual['pending']
 decision=json.loads((S/'reports/FOURCASE_SECOND_BODY_SCOPE_DECISION_ACTUAL.json').read_bytes());assert decision['passed'] and decision['all_own_four_cases_actual_complete']
 dispatch=sorted((S/'reports').glob('SECOND_BODY_FORMAL_UNIQUE_DISPATCH_ACTUAL_*.json'));assert len(dispatch)==1 and json.loads(dispatch[0].read_bytes())['code']==0
 old=cap.a.gitio.refs();cap.a.FOLDERS=(D,S);rows,files=cap.capture_streaming(dest)
 sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
 def git(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(x.encode()+b'\0' for x in args[2:]),check=True,capture_output=True);return p.stdout.decode().strip()
  return cap.g(*args)
 rec.git=git
 sys.argv=['record_experiment.py','--id',ID,'--title','Review own f516 three retained skills and start second original Linux20k BODY profile repair window','--kind','training','--note-file',str(D/'BODYFRAME_FIRST_RETAINED_SKILLS_NEW_THREE_CASE_STAGE.md'),'--files',*files,'--validation','Own f516 wholecore195/107/99 separately from ownedBODY source actual SHA; complete original flat80/spin88/world88 seed20261002 1500controls6000callbacks against e3 firstphysics rootq30/parameters recipescapturedRNGqueues/loadedDLL strict pairs, all whole raw twohostSHA query1e-6 contact integral COMhardware audited. Flat reverse error+0.006048 forward-0.000475, ordinary0; negative4pi all8 improve but both signs0/8 and positive stall/regressions retained, ordinary2to1; world61/64 unchanged improved60/regressed29. Finite coordinator actual exited, all parents children and sharedOSlockfree; reused original native120 no GPU replay, frozen0PPO/no charge. Own first300 fulltrace and Wave26/26 support disclosed E1 domain continuation, no numeric graduation gate or qualification. Newsecond3600 formal-only CPU538sourcefreeze target wholef516+BODY diskstorage/strict negatives, original522runtime and normal callbacks unchanged, original canonical/resource guarded; own newparent actual dispatch, startup/positive fullsave not inferred from process. All original parser/compile-scope/schema/import reader errors retained with only unexecuted continuations. No initializer, reward/DR/clock/hardware change or third blind block/70. Large originals pathsizeSHA indexed; later own positive/final/monitor/Gitreceipt ordinary supplement.','--push'];rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag);cap.a.verify(rows,old,head,tag,obj)
 receipt=R/'F516_FOURCASE_SECOND_BODY_STAGE_GIT_RECORDED.json';assert not receipt.exists();receipt.write_text(json.dumps(dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,actual_remote_main_tag_peeled_verified=True,all_oldtags_preserved=len(old),saved_sources=len(rows),later_receipts_require_ordinary_supplement=True),indent=2),encoding='utf8');print(json.dumps(dict(commit=head,tag=tag,tagobject=obj,actual_remote_verified=True,oldtags=len(old),sources=len(rows))))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=R/('F516_STAGE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(error=traceback.format_exc(),continue_existing_objects_only_no_record_tag_commit_replay=True),indent=2),encoding='utf8');raise

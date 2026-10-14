from pathlib import Path
import json,importlib,subprocess,sys,time,traceback
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;S=W/'MOD4_LINUX_WAVE50_BODYFRAME_SECOND_PREPARE_20261014';R=D/'reports';REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'));import append_large_install_evidence_import_reviewed_git as cap
def main():
 ID='wave50-bodyframe-command-resampling-phase-repaired-retained-state-remainder-started';dest=REPO/'history/evidence'/D.name/'resampling_phase_actual_stage';assert not dest.exists() and not cap.g('status','--porcelain') and not cap.g('tag','--list','*'+ID)
 assert json.loads((R/'SECOND_BODY_FAILURE_RETAINED_WHOLE_STATE_AND_COMPLETED_PREFIX_CPU_VERIFIED.json').read_bytes())['passed_retained_checkpoint_only']
 assert json.loads((R/'BODY_RESAMPLE_PHASE_OLD_REJECTION_NEW_DEFER_AND_STABLE_NEGATIVES_CPU_ACTUAL.json').read_bytes())['passed']
 old=cap.a.gitio.refs();cap.a.FOLDERS=(S,D);rows,files=cap.capture_streaming(dest);sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
 def git(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(x.encode()+b'\0' for x in args[2:]),check=True,capture_output=True);return p.stdout.decode().strip()
  return cap.g(*args)
 rec.git=git;sys.argv=['record_experiment.py','--id',ID,'--title','Repair BODY adapter during original command sampler transient and recover remaining second-window allocation','--kind','repair','--note-file',str(D/'RESAMPLING_PHASE_FAILURE_AND_REMAINDER_RECOVERY_STAGE.md'),'--files',*files,'--validation','Original EXIT0-with-Tracebacks/PARENTFAIL retained:1200raw finite continuous, lasthealth4804callbacks four partialextra/no formalFINAL. All53twohost artifacts/source/false/error retained. Complete1a370 whole20k core195/107/99+BODY/46update22.08M/9actorAdam920/all14/sourceepisode+1/saveprefix verified, original unique1129.314s once charged/actualexit-twofcntlFree-canonicalidle. CPU2246 realrows reproduces sampler transient ASSERT, one guard defers until original sampler complete; stable mapping exact and badspeedyawstanding stillreject/allotherAST/RNG/source unchanged. New535source targetCPU/sourcebound2470 remaining second allocation formalonly actuallaunch/all14 restore; firstown405851 oneupdate480k/9actorAdam20 twohost/localCPU verified. Physical12s boundary pending, no newaxis/initializer/DRrewardclockhardware/SDK change/native replay/budget extension/refund/third blind block/qualification. Big originals pathsizeSHA indexed/credentials excluded; laterreports ordinary supplement.','--push'];rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag);cap.a.verify(rows,old,head,tag,obj)
 receipt=R/'RESAMPLING_PHASE_REPAIR_STAGE_GIT_RECORDED.json';assert not receipt.exists();receipt.write_text(json.dumps(dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,actual_remote_main_tag_peeled_verified=True,oldtags_preserved=len(old),sources=len(rows),later_receipts_require_ordinary_supplement=True),indent=2),encoding='utf8');print(json.dumps(dict(commit=head,tag=tag,tagobject=obj,actual_remote_verified=True,oldtags=len(old),sources=len(rows))))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=R/('RESAMPLING_PHASE_STAGE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(error=traceback.format_exc(),continue_existing_objects_only_no_record_tag_commit_replay=True),indent=2),encoding='utf8');raise

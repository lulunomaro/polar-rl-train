"""Record this actual own final and fresh finite evaluation start exactly once."""
from pathlib import Path
import json, importlib, subprocess, sys, time, traceback
from datetime import datetime, timezone, timedelta
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
E=W/'MOD4_3060_BODYFRAME_PHASE_FINAL_FULL80_20261015';RET=W/'MOD4_3060_BODYFRAME_PHASE_FINAL_RETENTION_20261015'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'));import append_large_install_evidence_import_reviewed_git as cap
ID='wave50-bodyframe-remainder-final124-new-fourcase-eval'
def main():
 final=json.loads((R/'PHASE_REPAIR_OWN_FINAL_FULLTRACE_LOCAL_CPU_VERIFIED.json').read_bytes());assert final['passed'] and final['updates']==124 and final['two_locks_free']
 dispatch=json.loads((E/'reports/REFERENCE17B_DEMAND_TASK_STARTED_ACTUAL.json').read_bytes());assert dispatch['task']['unique_start'] and dispatch['no_oldcase_replayed']
 dest=REPO/'history/evidence'/D.name/'own_final124_and_new_fourcase_start_stage'
 assert not dest.exists() and not cap.g('status','--porcelain') and not cap.g('tag','--list','*'+ID)
 old=cap.a.gitio.refs();cap.a.FOLDERS=(D,E,RET);rows,files=cap.capture_streaming(dest)
 sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
 def git(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(x.encode()+b'\0' for x in args[2:]),check=True,capture_output=True);return p.stdout.decode().strip()
  return cap.g(*args)
 rec.git=git
 sys.argv=['record_experiment.py','--id',ID,'--title','Complete repaired BODY20k remainder fullfinal124 and uniquely start fresh frozen four-case evaluation','--kind','training','--note-file',str(D/'OWN_PHASE_FINAL124_AND_NEW_FOURCASE_EVAL_STAGE.md'),'--files',*files,'--validation','Own model32998 cfce fullfinal19894311B core195/107float99perenv20k plus ownedBODY separate. All56artifacts1778985563B twohost SHA, independent CPU all14 startup/disk/episode+1/no repeat initializer, 124updates2976controls59.52Menvsteps11904callbacks actor9/17Adam2480 and all6NPZ continuous/finite/nonresetroot/resetunion/birthhist sourceBODY1512 difference exact; ordinary1/no integrity/noSTOP/closure1.250577mm. Original parentPASS actual parentchildout/guardianEXIT/twofcntlFree/canonicalidle; original unique2503.057271719s once charged, previous1129.314 failure not refunded/recharged. Preserve old EXIT0-with-Tracebacks/PARENTFAIL, partial4804callback classification and all reader errors. Fresh source namespace changes only/no physics threshold change/no old native or case replay. Own new frozen Wave80 task uniquely started; three retained V8 skills CPUprepared, finite coordinator actualCIM62028 sole249 and210 transport while alive, subsequent real results independently recorded. No future pass/qualified50/70/third learning/MoE or budget extension; big originals realpathsizeSHA only credentials excluded.','--push'];rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag);cap.a.verify(rows,old,head,tag,obj)
 receipt=R/'PHASE_FINAL124_AND_FOURCASE_STARTED_STAGE_GIT_RECORDED.json';assert not receipt.exists();receipt.write_text(json.dumps(dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,actual_remote_main_tag_peeled_verified=True,all_oldtags_preserved=len(old),sources=len(rows),later_reports_and_receipt_ordinary_supplement_required=True),indent=2),encoding='utf8');print(json.dumps(dict(commit=head,tag=tag,tagobject=obj,actual_remote_verified=True,all_oldtags=len(old),sources=len(rows))))
if __name__=='__main__':
 try:main()
 except BaseException:
  (R/('PHASE_FINAL_STAGE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),continue_existing_objects_only_no_record_tag_commit_replay=True),indent=2),encoding='utf8');raise

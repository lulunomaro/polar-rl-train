"""Unique current evidence stage, never training or transport to either GPU host."""
from pathlib import Path
import sys,json,time,subprocess,importlib,traceback
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap
ID='wave50-body-axis-reviewed-first-s4-rule-router-native'
DEST=REPO/'history/evidence'/D.name/'fourcase_closeout_first_rule_native_actual'
cap.a.FOLDERS=(D,W/'MOD4_S4_E0_WAVE35_ROUTER_NATIVE_20261015',W/'MOD4_3060_BODYFRAME_PHASE_FINAL_RETENTION_20261015',W/'MOD4_LINUX_BODYFRAME_RESAMPLE_PHASE_REPAIR_20261014',W/'MOD4_3060_BODYFRAME_PHASE_FINAL_FULL80_20261015')
def save(n,v):
 p=R/n;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
def main():
 assert not cap.g('status','--porcelain') and not cap.g('diff','--cached','--name-only')
 assert not cap.g('tag','--list','*'+ID) and not DEST.exists()
 assert json.loads((W/'MOD4_S4_E0_WAVE35_ROUTER_NATIVE_20261015/reports/FIRST_S4_OWN_NATIVE120_WHOLE_PHYSICAL_AND_ROUTER_CPU_ADMITTED.json').read_bytes())['passed']
 assert json.loads((R/'S4_NATIVE_COMPLETE_HOURLY_MONITOR_ACTUAL_BYTEEXACT_VERIFIED.json').read_bytes())['passed']
 old=cap.a.gitio.refs()
 save('BODY_CLOSEOUT_S4_NATIVE_GIT_STAGE_STARTED_ACTUAL.json',dict(epoch=time.time(),id=ID,previous_main=cap.g('rev-parse','HEAD'),old_tags=len(old),no_GPU_budget_or_training_mutation=True))
 rows,files=cap.capture_streaming(DEST)
 sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
 def g(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(s.encode()+b'\0' for s in args[2:]),capture_output=True,check=True);return p.stdout.decode().strip()
  return cap.g(*args)
 rec.git=g
 sys.argv=['record_experiment.py','--id',ID,'--title','Review bounded BODY four cases and admit first frozen S4 rule router native','--kind','evaluation','--note-file',str(D/'ACTUAL_BODY_CLOSEOUT_AND_FIRST_S4_RULE_NATIVE_STAGE_NOTE.txt'),'--files',*files,'--validation','Own completed fourcase raw/physical/pair review; source priority f516 preserved. CPU joint probability/shared input/reset/gradient/disk negatives; own frozen E0+W35 flat120/480 native allraw physical routing admission and actual exit-lockfree. Zero gate updates or budget write. Original rejected drafts/reader errors/large indexes and exact hourly monitor kept.','--push']
 rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID
 head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag);cap.a.verify(rows,old,head,tag,obj)
 report=dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,actual_remote_main_tag_peeled_verified=True,all_old_tags_preserved=len(old),actual_tracked_SHA_verified=True,saved_sources=len(rows),large_originals_retained=True,no_push_pending=True,later_saved_receipt_requires_ordinary_supplement=True)
 save('BODY_CLOSEOUT_FIRST_S4_NATIVE_STAGE_GIT_RECORDED_ACTUAL.json',report);print(json.dumps(report))
if __name__=='__main__':
 try:main()
 except BaseException:
  save('BODY_CLOSEOUT_S4_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_existing_objects_no_rerecord_retag_recommit=True));raise

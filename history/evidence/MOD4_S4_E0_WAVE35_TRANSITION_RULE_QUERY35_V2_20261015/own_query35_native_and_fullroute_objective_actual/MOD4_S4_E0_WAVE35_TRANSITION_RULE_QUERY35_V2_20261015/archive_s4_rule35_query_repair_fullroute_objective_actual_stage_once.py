from pathlib import Path
import sys,json,time,subprocess,importlib,traceback
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'));import append_large_install_evidence_import_reviewed_git as cap
ID='s4-original35-query-repair-rule-fullroute-saved-objective'
DEST=REPO/'history/evidence'/D.name/'own_query35_native_and_fullroute_objective_actual'
cap.a.FOLDERS=(D,W/'MOD4_S4_E0_WAVE35_TRANSITION_RULE_20261015',W/'MOD4_S3_WAVE50_CLOSEOUT_S4_LIVE_ADAPTER_20261015')
def save(n,v):
 p=R/n;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
def main():
 assert not cap.g('status','--porcelain') and not cap.g('tag','--list','*'+ID) and not DEST.exists()
 assert json.loads((R/'S4_RULE35_OWN_NATIVE_AND_FULL_ROUTE_COMPLETE_SCOPE_CPU_ACTUAL.json').read_bytes())['passed_source_initial_scope_review']
 assert json.loads((R/'S4_RULE35_COMPLETE_MONITOR_ACTUAL_TOML_BYTEEXACT_VERIFIED.json').read_bytes())['passed']
 old=cap.a.gitio.refs();save('S4_RULE35_QUERY_REPAIR_FULLROUTE_STAGE_GIT_STARTED_ACTUAL.json',dict(epoch=time.time(),id=ID,previous_main=cap.g('rev-parse','HEAD'),oldtags=len(old),no_GPU_training_budget_mutation=True))
 rows,files=cap.capture_streaming(DEST);sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
 def g(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(s.encode()+b'\0' for s in args[2:]),check=True,capture_output=True);return p.stdout.decode().strip()
  return cap.g(*args)
 rec.git=g;sys.argv=['record_experiment.py','--id',ID,'--title','Repair S4 independent35 query source and review frozen rule fullroute27/27 pairs','--kind','evaluation','--note-file',str(D/'ACTUAL_S4_RULE35_QUERY_REPAIR_FULL_ROUTE_AND_OBJECTIVE_STAGE_NOTE.txt'),'--files',*files,'--validation','Oldpre-control reference50 fail kept. Ownneworiginal35 native120/full1500 data/query/contactCOMhardware/strict1Nbefore-after200mm/shared35-whole6 sourcefreeze/prefix/actualexit-lockfree passed. Forward27/27 reverse27/27 ordinary0. Historicalvariablebatch objective25negatives gradientonly0updates. Originalallreadererrors/unusedsources/monitor byteexact/evidenceindexes retained; gatefullstate and PPO not claimed.','--push'];rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag);cap.a.verify(rows,old,head,tag,obj)
 v=dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,actual_remote_main_tag_peeled_verified=True,all_old_tags_preserved=len(old),actual_tracked_SHA_verified=True,saved_sources=len(rows),large_originals_retained=True,push_pending=False,later_receipt_requires_ordinary_supplement=True);save('S4_RULE35_FULLROUTE_AND_OBJECTIVE_STAGE_GIT_RECORDED_ACTUAL.json',v);print(json.dumps(v))
if __name__=='__main__':
 try:main()
 except BaseException:
  save('S4_RULE35_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_existing_objects_no_rerecord_tag_commit=True));raise

from pathlib import Path
import sys,json,time,subprocess,importlib,traceback
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap
ID='s4-rsl5-joint-gate-fullstate-repairs-first-bounded-dispatch'
DEST=REPO/'history/evidence'/D.name/'joint_gate_restore_repairs_and_first_dispatch_actual'
cap.a.FOLDERS=(D,W/'MOD4_S4_E0_WAVE35_TRANSITION_RULE_QUERY35_V2_20261015')
def save(name,value):
 p=R/name;assert not p.exists();p.write_text(json.dumps(value,indent=2),encoding='utf8')
def main():
 assert not cap.g('status','--porcelain') and not cap.g('tag','--list','*'+ID) and not DEST.exists()
 assert json.loads((R/'CLOSED_S4_ZERO_FULLSTATE_INDEPENDENT_CPU_ADMITTED.json').read_bytes())['passed'] is True
 assert json.loads((R/'S4_FIRST_GATE_TRANSPORT_PENDING_MONITOR_TOML_BYTEEXACT_VERIFIED.json').read_bytes())['passed'] is True
 assert list(R.glob('S4_FIRST_GATE_UNIQUE_DISPATCH_ACTUAL_*.json'))
 old=cap.a.gitio.refs()
 save('S4_JOINT_GATE_FULLSTATE_FIRST_DISPATCH_GIT_STARTED_ACTUAL.json',dict(epoch=time.time(),id=ID,previous_main=cap.g('rev-parse','HEAD'),oldtags=len(old),no_training_budget_or_GPU_mutation=True))
 rows,files=cap.capture_streaming(DEST)
 sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
 def g(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(s.encode()+b'\0' for s in args[2:]),check=True,capture_output=True);return p.stdout.decode().strip()
  return cap.g(*args)
 rec.git=g
 sys.argv=['record_experiment.py','--id',ID,'--title','Integrate S4 joint gate, repair fullstate and dispatch first bounded learner','--kind','deployment',
  '--note-file',str(D/'ACTUAL_S4_RSL5_FULLSTATE_REPAIRS_FIRST_GATE_STAGE_NOTE.txt'),'--files',*files,
  '--validation','Actual RSL5 saved-z/raw joint distribution and supported-sequence CPU gradient-only tests0optimizerupdates; actual target CPU API admitted. Original native120/480 save failure and missingfullraw kept; zero0NaN and cache CPUCUDA failures preserved. Real GPU whole601 then repaired own0 source0681 all151/70/9episode+1/frozen18/privateCUDA/disk/actualexit-locksfree independently verified. Sole2700s firstgate parent uniquely dispatched, firstSSHread TCPtimeout kept; no savedPPO/futurequalification inferred. All source/readers/false/errors/costs/unused/monitor/rawindexes captured.','--push']
 rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag)
 cap.a.verify(rows,old,head,tag,obj)
 result=dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,actual_remote_main_tag_peeled_verified=True,
  all_old_tags_preserved=len(old),actual_tracked_SHA_verified=True,saved_sources=len(rows),large_originals_retained=True,
  push_pending=False,first_gate_saved_PPO_not_yet_independently_observed=True,later_receipt_requires_ordinary_supplement=True)
 save('S4_JOINT_GATE_FULLSTATE_FIRST_DISPATCH_STAGE_GIT_RECORDED_ACTUAL.json',result);print(json.dumps(result))
if __name__=='__main__':
 try:main()
 except BaseException:
  save('S4_JOINT_GATE_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_existing_objects_no_rerecord_tag_commit=True));raise

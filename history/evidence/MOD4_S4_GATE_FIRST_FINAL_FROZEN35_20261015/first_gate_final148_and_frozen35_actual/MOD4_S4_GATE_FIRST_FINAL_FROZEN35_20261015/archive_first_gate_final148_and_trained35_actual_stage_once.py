from pathlib import Path
import sys,json,time,subprocess,importlib,traceback
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap
ID='s4-first-gate-final148-audited-trained35-eval-started'
DEST=REPO/'history/evidence'/D.name/'first_gate_final148_and_frozen35_actual'
cap.a.FOLDERS=(D,W/'MOD4_S4_LINUX_LEARNER_FULLSTATE_ADMISSION_20261015')
def save(name,value):
 p=R/name;assert not p.exists();p.write_text(json.dumps(value,indent=2),encoding='utf8')
def main():
 assert not cap.g('status','--porcelain') and not cap.g('tag','--list','*'+ID) and not DEST.exists()
 assert json.loads((W/'MOD4_S4_LINUX_LEARNER_FULLSTATE_ADMISSION_20261015/reports/S4_FIRST_GATE_CLOSED_ALL_RAW_CPU_VERIFIED.json').read_bytes())['passed'] is True
 assert json.loads((R/'S4_FIRST_TRAINED_GATE35_SHARED_ROUTING_ADMITTED_s4_first_gate_final35_native120_v1.json').read_bytes())['passed'] is True
 assert (R/'S4_FIRST_TRAINED_GATE35_FULL1500_UNIQUE_TASK_DISPATCH_ACTUAL.json').exists()
 old=cap.a.gitio.refs()
 save('S4_FINAL148_AND_TRAINED35_GIT_STARTED_ACTUAL.json',dict(epoch=time.time(),id=ID,previous_main=cap.g('rev-parse','HEAD'),oldtags=len(old),no_training_budget_or_GPU_mutation=True))
 rows,files=cap.capture_streaming(DEST)
 sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
 def g(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(s.encode()+b'\0' for s in args[2:]),check=True,capture_output=True);return p.stdout.decode().strip()
  return cap.g(*args)
 rec.git=g
 sys.argv=['record_experiment.py','--id',ID,'--title','Close first S4 gate148, audit all raw and start trained35 frozen comparison','--kind','evaluation',
  '--note-file',str(D/'ACTUAL_FIRST_S4_FINAL148_AND_NEW_FROZEN35_STAGE_NOTE.txt'),'--files',*files,
  '--validation','Own final148/3552/71.04M/194-113, gate6 critic8 Adam2960 frozen19 exact; all148 raw and7physical prefixes26.86GB CPU hashes finite support-selection/previousaction/resetunion exact20.167M qualified samples; original parent unique2668.750717s closed-exit-twofcntlFree-idle. New source-bound3060 gate native120/480 wholephysical/routing allrowCPU passed, old missingEXIT preserved; own new full1500 dispatched pending. All original collector/readers/errors/source/rawindexes/cost/unused preserved. No auto secondlearning or qualification.','--push']
 rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag)
 cap.a.verify(rows,old,head,tag,obj)
 result=dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,actual_remote_main_tag_peeled_verified=True,
  all_old_tags_preserved=len(old),actual_tracked_SHA_verified=True,saved_sources=len(rows),large_originals_retained=True,
  push_pending=False,first_gate_formal_final148_and_all_raw_independently_verified=True,new_frozen35_full1500_result_not_yet_inferred=True,later_receipt_requires_ordinary_supplement=True)
 save('S4_FIRST_GATE_FINAL148_AND_TRAINED35_STAGE_GIT_RECORDED_ACTUAL.json',result);print(json.dumps(result))
if __name__=='__main__':
 try:main()
 except BaseException:
  save('S4_FINAL148_TRAINED35_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_existing_objects_no_rerecord_tag_commit=True));raise

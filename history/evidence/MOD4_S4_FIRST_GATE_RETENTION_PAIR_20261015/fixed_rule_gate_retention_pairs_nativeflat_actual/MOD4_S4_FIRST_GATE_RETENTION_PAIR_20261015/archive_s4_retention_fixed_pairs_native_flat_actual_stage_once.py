from pathlib import Path
import sys,json,time,subprocess,importlib,traceback
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap
ID='s4-retention-rule-gate-fixed-pairs-native-flat-admitted'
DEST=REPO/'history/evidence'/D.name/'fixed_rule_gate_retention_pairs_nativeflat_actual'
cap.a.FOLDERS=(D,)
def save(name,value):
 p=R/name;assert not p.exists();p.write_text(json.dumps(value,indent=2),encoding='utf8')
def main():
 assert not cap.g('status','--porcelain') and not cap.g('tag','--list','*'+ID) and not DEST.exists()
 assert json.loads((R/'s4_retention_gate_eval_flat_120_v1_S4_ROUTING_CPU_ADMITTED.json').read_bytes())['passed'] is True
 assert json.loads((R/'FIRST_GATE_RETENTION_FIXED_NINE_MONITOR_TOML_UTF8_ACTUAL_VERIFIED.json').read_bytes())['passed'] is True
 assert json.loads((R/'FIRST_GATE_RETENTION_FIXED_NINE_ROOT_CIM_INDEPENDENT_DISPATCH_ACTUAL.json').read_bytes())['native_flat120_actual_CPU_admitted'] is True
 old=cap.a.gitio.refs()
 save('S4_RETENTION_FIXED_NINE_GIT_STARTED_ACTUAL.json',dict(epoch=time.time(),id=ID,previous_main=cap.g('rev-parse','HEAD'),oldtags=len(old),no_training_budget_or_GPU_mutation=True))
 rows,files=cap.capture_streaming(DEST)
 sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
 def g(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(s.encode()+b'\0' for s in args[2:]),check=True,capture_output=True);return p.stdout.decode().strip()
  return cap.g(*args)
 rec.git=g
 sys.argv=['record_experiment.py','--id',ID,'--title','Admit first S4 retention native and start fixed original rule-gate pairs','--kind','evaluation',
  '--note-file',str(D/'ACTUAL_S4_RETENTION_FIXED_NINE_NATIVE_FLAT_STAGE_NOTE.txt'),'--files',*files,
  '--validation','Fixed-source gate on existing real35obs CPU only; new target whole194/113+frozenE0/W35 and all37+476source/SDK hashes verified. Original3physicsmainloopsbyteexact; own new gate-flatnative120/480 physical-query-contactCOMhardware/routing/all24initialfinal/allrowCPU passed. Actualfinite9 creationargv starts new fullruleflat; futurefull6 not inferred, root forbids parallel210/249transport. Original false/limits/oldmissingEXIT preserved, noPPO/canonical/oldcase replay. New native/full tasks only after own source/resource/actualCPU boundary. Monitor sameACTIVEhourlyUTF8exact and local launchpending actualCIM child evidence preserved.','--push']
 rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag)
 cap.a.verify(rows,old,head,tag,obj)
 result=dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,actual_remote_main_tag_peeled_verified=True,
  all_old_tags_preserved=len(old),actual_tracked_SHA_verified=True,saved_sources=len(rows),large_originals_retained=True,
  push_pending=False,first_retention_native_flat120_independently_verified=True,fixed_nine_actual_running_future_full_pairs_not_inferred=True,later_receipt_requires_ordinary_supplement=True)
 save('S4_RETENTION_FIXED_NINE_NATIVEFLAT_STAGE_GIT_RECORDED_ACTUAL.json',result);print(json.dumps(result))
if __name__=='__main__':
 try:main()
 except BaseException:
  save('S4_RETENTION_FIXED_NINE_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_existing_objects_no_rerecord_tag_commit=True));raise

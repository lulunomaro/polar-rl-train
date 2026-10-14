"""Unique actual second full-final/new frozen candidate deployment stage."""
from pathlib import Path
import json,sys,time,subprocess,importlib
from datetime import datetime,timezone,timedelta
import archive_retention_v8_second_sameidentity_actual_stage_once as base
D=base.D;W=base.W;REPO=base.REPO;cap=base.cap
def main():
 ID='wave50-left-second-fullfinal191-reviewed-new-frozen80-started';note=D/'LEFT_SECOND_FINAL191_AND_FROZEN_E3_CANDIDATE_STAGE.md'
 dest=REPO/'history/evidence'/D.name/'left_second_final191_new_e3_candidate_stage'
 assert note.is_file() and not cap.g('status','--porcelain') and not cap.g('tag','--list','*'+ID)
 S=W/'MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014'
 final=json.loads((S/'reports/LEFT_SECOND_OWN_FORMAL_FINAL_CLOSEOUT_CPU_VERIFIED.json').read_bytes());assert final['passed'] and final['saved_updates']==191 and final['canonical_idle'] and final['two_actual_fcntl_free']
 trace=json.loads((D/'reports/LEFT_SECOND_FORMAL_FINAL_FULLTRACE_CPU_ACTUAL_1791963246377865600.json').read_bytes());assert trace['code']==0 and json.loads(trace['stdout'])['passed']
 deploy=json.loads((W/'MOD4_3060_LEFT_SECOND_FULL80_20261014/reports/REFERENCE17B_DEMAND_TASK_STARTED_ACTUAL.json').read_bytes());assert deploy['no_oldcase_replayed'] and deploy['task']['triggers']==0
 old=cap.a.gitio.refs();cap.a.FOLDERS=base.FOLDERS+(W/'MOD4_3060_LEFT_SECOND_FULL80_20261014',W/'MOD4_3060_LEFT_SECOND_RETENTION_20261014');rows,files=cap.capture_streaming(dest)
 sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
 def wrapped(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in args[2:]),check=True,capture_output=True);return p.stdout.decode().strip()
  return cap.g(*args)
 rec.git=wrapped
 sys.argv=['record_experiment.py','--id',ID,'--title','Review actual second full20k191update final and start new source-bound frozen Wave50 full80','--kind','training','--note-file',str(note),'--files',*files,'--validation','Original second sameidentity20k model32825 SHAe3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c actual195tensor107float99perenv/191updates4584controls91.68Msteps18336cb/actor9Adam3820/13strictCPUCUDAroundtrip_episodeplus1/no initializer repeat/541freeze. Complete8NPZ2653234126B full4584control continuity/resetunion/nonresetroot/signedstanding/currentfamily4vsstaticassignment/beforecommand_afterhistory/maxvalid39.99s passed CPU. Ordinary5 basecontact no closure/integrityunknown/nonfinite or STOP, closure1.1723mm/mimic.00169146, timeout-routeoverlap15 unique62403 retained. Original parentPASS and unique3631.690686s once settled, actualparentguardianchildout/twofcntlFree/canonicalidle. New source frozen source-only namespace workerAST constants only;485bundle rows and actualSDK/nativeproof SHA reuse, ownweight copied notDR resume, new47.603MBpackage byteSHA verified/unused case and0trigger uniqueTask; full1500 result pending at dispatch. No oldGPU/native once replay/newPPO/thirdblindduration/70/qualification. Original source2b best observed22/25 and inherited regressions preserved; all original schema/path/systempython/CRLF reader failures, successful independent read fixes, costs/rawindexes/monitor and stage receipts included.','--push']
 rec.main();tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID
 head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag);cap.a.verify(rows,old,head,tag,obj)
 p=D/'reports/LEFT_SECOND_FINAL191_E3_CANDIDATE_STAGE_GIT_RECORDED.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,remote_main_tag_peeled_verified=True,all_old_tags_preserved=len(old),saved_sources=len(rows),later_receipt_ordinary_supplement_required=True),indent=2),encoding='utf8')
 print(json.dumps(dict(commit=head,tag=tag,tagobject=obj,remote_verified=True,saved_sources=len(rows))))
if __name__=='__main__':main()

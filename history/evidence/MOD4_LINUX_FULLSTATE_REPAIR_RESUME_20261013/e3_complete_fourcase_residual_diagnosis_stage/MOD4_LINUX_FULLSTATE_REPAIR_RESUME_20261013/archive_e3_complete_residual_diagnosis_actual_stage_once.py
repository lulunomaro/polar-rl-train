"""Single new actual diagnostic stage. Never re-record after a push error."""
from pathlib import Path
import sys,json,time,subprocess,importlib
from datetime import datetime,timezone,timedelta
import archive_retention_v8_second_sameidentity_actual_stage_once as base
D=base.D;W=base.W;REPO=base.REPO;cap=base.cap
FOLDERS=base.FOLDERS+tuple(W/name for name in (
 'MOD4_3060_LEFT_SECOND_FULL80_20261014','MOD4_3060_LEFT_SECOND_RETENTION_20261014',
 'MOD4_E3_WAVE_RESIDUAL_CPU_20261014','MOD4_E3_POSITIVE_SPIN_RESIDUAL_CPU_20261014',
 'MOD4_E3_YAWPI_FRAME_FACTOR_20261014'))

def main():
 ID='wave50-e3-fourcase-complete-and-yaw-spin-residuals-diagnosed'
 note=D/'E3_COMPLETE_FOURCASE_RESIDUAL_DIAGNOSIS_STAGE.md'
 dest=REPO/'history/evidence'/D.name/'e3_complete_fourcase_residual_diagnosis_stage'
 assert note.is_file() and not cap.g('status','--porcelain') and not cap.g('tag','--list','*'+ID)
 j=json.loads((D/'reports/E3_COMPLETE_FOURCASE_AND_RESIDUAL_SINGLE_AXIS_SCOPE_DECISION_ACTUAL.json').read_bytes())
 assert j['qualified50'] is False and j['qualified70'] is False and j['all_skills_accepted'] is False
 t=json.loads((W/'MOD4_3060_LEFT_SECOND_RETENTION_20261014/reports/SECOND_E3_THREE_RETENTION_PAIRS_COMPLETE_ACTUAL_CPU_REVIEW.json').read_bytes())
 assert t['passed'] is True
 old=cap.a.gitio.refs();cap.a.FOLDERS=FOLDERS;rows,files=cap.capture_streaming(dest)
 sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
 def wrapped(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in args[2:]),check=True,capture_output=True);return p.stdout.decode().strip()
  return cap.g(*args)
 rec.git=wrapped
 sys.argv=['record_experiment.py','--id',ID,'--title','Complete E1 Wave50 model32825 four-case review and diagnose terrain and positive-spin residuals','--kind','diagnostic','--note-file',str(note),'--files',*files,'--validation','Own E3 whole20k model32825 sourcee3 SHA/full195tensor107float99perenv/191updates91.68Msteps and formal13strict/full8NPZ/cost/actualexit already reviewed. New complete Wave50 original80/1500/6000cb is24of27 forward26of27reverse, no passage regression,ordinary1 and allfailedprefix kept. Allthree inherited1500 cases complete twohostSHA/raw/query/contactCOMhardware/nativeSHA/source/DLL/initialrootqparamsRNGqueue pair: flat improves, negative4pi errors improve but bothsigns0of8 originaltol, positive4pi continuousenv51 and orientation73/84 residuals ordinary1to2;world61of64ties with exchanged failures. Finitecoordinator actualabsent and originalsharedOSlockfree rootownerhandoff verified. CPU actual complete91.68M command exposure has no pure-spin andyawmax~2rad/s, not completeancestorclaim or excuse. Fullfailedprefix andfixed-inputgyro-yaw CPU analyses preserve all originalflags, numerical output bounds, sources and errors; no unique causality or50/70/allskills/globalbest claim. Independent new yawpi-BODYsign sameWORLD reset/full25200point footprint CPU fixture/admission preparation and any actual native dispatch receipts captured separately from future pass. Totalplan masterSHA812a verified remainsS3E1, gateuntrained. No new PPO/thirdblindduration/commandDRrewardhardwarethreshold/budget mutation or oldGPU case replay. All saved errors/false/rawindexes/readers/workorders/monitor and ownerreceipts included, credentials excluded and large originals retained.','--push']
 rec.main();tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID
 head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag);cap.a.verify(rows,old,head,tag,obj)
 report=D/'reports/E3_COMPLETE_FOURCASE_RESIDUAL_DIAGNOSTIC_STAGE_GIT_RECORDED.json';assert not report.exists()
 report.write_bytes(json.dumps(dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,remote_main_tag_peeled_verified=True,all_old_tags_preserved=len(old),actual_saved_sources=len(rows),later_receipt_ordinary_supplement_required=True),indent=2).encode())
 print(json.dumps(dict(commit=head,tag=tag,tagobject=obj,remote_verified=True,actual_saved_sources=len(rows))))

if __name__=='__main__':main()

from pathlib import Path
import json,time,sys,subprocess,importlib
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap
def main():
 ID='windows4090-own128-capacity-search-20gb';note=D/'ACTUAL_CAPACITY_SEARCH_STAGE.md';dest=REPO/'history/evidence'/D.name/'actual_capacity_search_stage'
 assert note.exists() and not cap.g('status','--porcelain') and not cap.g('tag','--list','*'+ID)
 old=cap.a.gitio.refs();cap.a.FOLDERS=(D,W/'MOD4_4090_WINDOWS_TEMP20GB_20261013',W/'MOD4_4090_WINDOWS_REPAIR_20261013')
 rows,files=cap.capture_streaming(dest)
 sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
 def wrapped(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in args[2:]),capture_output=True,check=True);return p.stdout.decode().strip()
  return cap.g(*args)
 rec.git=wrapped
 sys.argv=['record_experiment.py','--id',ID,'--title','Measure larger Windows4090 repair environments within20GB; preserve own128 state and all failures','--kind','repair','--note-file',str(note),'--files',*files,'--validation','Independent CPU full107/99 source/storage/RNG/schema, actual native contact-query-COM-hardware and full12 CPUCUDA restore, fullPPO timing/positive ownsave and resource measured. Original errors/false/cost preserved; sole Linuxcanonical unchanged; exact remote evidence snapshots and all old Git objects retained.','--push'];rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag);cap.a.verify(rows,old,head,tag,obj)
 (D/'reports/CAPACITY_SEARCH_STAGE_GIT_RECORDED.json').write_text(json.dumps(dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,remote_main_tag_peeled_verified=True,all_old_tags_preserved=len(old),actual_saved_sources=len(rows),later_receipt_ordinary_supplement_required=True),indent=2),encoding='utf8');print(json.dumps(dict(commit=head,tag=tag,tagobject=obj,remote_verified=True,actual_saved_sources=len(rows))))
if __name__=='__main__':main()

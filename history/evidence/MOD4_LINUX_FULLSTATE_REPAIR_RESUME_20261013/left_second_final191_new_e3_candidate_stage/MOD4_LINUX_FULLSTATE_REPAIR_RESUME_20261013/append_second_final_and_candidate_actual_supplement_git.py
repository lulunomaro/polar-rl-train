"""Capture genuine new final/candidate artifacts, ordinary supplementary commit."""
from pathlib import Path
import json,sys,time,subprocess
import archive_retention_v8_second_sameidentity_actual_stage_once as stage
cap=stage.cap;D=stage.D;REPO=stage.REPO;W=stage.W
def main():
 label=sys.argv[1];assert label.replace('-','').replace('_','').isalnum() and not cap.g('status','--porcelain')
 dest=REPO/'history/evidence'/D.name/label
 old=cap.a.gitio.refs();cap.a.FOLDERS=stage.FOLDERS+(W/'MOD4_3060_LEFT_SECOND_FULL80_20261014',W/'MOD4_3060_LEFT_SECOND_RETENTION_20261014');rows,files=cap.capture_streaming(dest)
 subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in files),check=True,capture_output=True)
 cap.g('commit','-m','Append whole20k second final and frozen candidate actual evidence: '+label);cap.g('push','origin','HEAD')
 head=cap.g('rev-parse','HEAD');cap.a.verify(rows,old,head)
 print(json.dumps(dict(epoch=time.time(),commit=head,remote_main_verified=True,all_old_tags_preserved=len(old),actual_saved_sources=len(rows),tracked_SHA_verified=True)))
if __name__=='__main__':main()

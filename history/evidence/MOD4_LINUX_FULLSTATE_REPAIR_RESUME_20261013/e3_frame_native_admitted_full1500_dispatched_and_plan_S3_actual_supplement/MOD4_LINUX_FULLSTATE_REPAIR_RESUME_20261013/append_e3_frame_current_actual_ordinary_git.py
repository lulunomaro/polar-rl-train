"""Ordinary saved-report supplement after the unique E3 diagnostic stage."""
from pathlib import Path
import json,sys,time,subprocess
import archive_e3_complete_residual_diagnosis_actual_stage_once as stage
cap=stage.cap;D=stage.D;REPO=stage.REPO;W=stage.W

def main():
 label=sys.argv[1];assert label.replace('-','').replace('_','').isalnum()
 dest=REPO/'history/evidence'/D.name/label
 assert not dest.exists() and not cap.g('status','--porcelain')
 old=cap.a.gitio.refs();cap.a.FOLDERS=(D,W/'MOD4_E3_YAWPI_FRAME_FACTOR_20261014')
 rows,files=cap.capture_streaming(dest)
 subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in files),check=True,capture_output=True)
 cap.g('commit','-m','Append actual E3 master-plan position and isolated frame diagnostics: '+label)
 cap.g('push','origin','HEAD')
 head=cap.g('rev-parse','HEAD');cap.a.verify(rows,old,head)
 print(json.dumps(dict(epoch=time.time(),commit=head,remote_main_verified=True,all_old_tags_preserved=len(old),saved_sources=len(rows),tracked_SHA_verified=True,no_new_trial_or_retag=True)))

if __name__=='__main__':main()

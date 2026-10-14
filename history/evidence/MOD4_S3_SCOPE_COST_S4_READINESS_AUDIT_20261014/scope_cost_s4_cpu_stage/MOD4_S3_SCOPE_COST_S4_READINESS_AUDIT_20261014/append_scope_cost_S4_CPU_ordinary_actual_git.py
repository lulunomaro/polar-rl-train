"""Append only saved supplementary evidence; no repeated trial/tag creation."""
from pathlib import Path
import sys,json,time,subprocess
import archive_scope_cost_and_S4_CPU_actual_stage_once as stage
A=stage.A;R=stage.R;REPO=stage.REPO;cap=stage.cap
def main():
 label=sys.argv[1];assert label.replace('_','').replace('-','').isalnum() and not cap.g('status','--porcelain')
 dest=REPO/'history/evidence'/A.name/label;assert not dest.exists()
 old=cap.a.gitio.refs();cap.a.FOLDERS=(A,);rows,files=cap.capture_streaming(dest)
 subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in files),check=True,capture_output=True)
 cap.g('commit','-m','Append actual S3 scope, approved005 cost and S4 CPU preparation evidence: '+label);cap.g('push','origin','HEAD')
 head=cap.g('rev-parse','HEAD');cap.a.verify(rows,old,head)
 print(json.dumps(dict(epoch=time.time(),commit=head,remote_main_verified=True,oldtags_preserved=len(old),saved_sources=len(rows),tracked_SHA_verified=True,no_new_record_or_tag=True)))
if __name__=='__main__':main()

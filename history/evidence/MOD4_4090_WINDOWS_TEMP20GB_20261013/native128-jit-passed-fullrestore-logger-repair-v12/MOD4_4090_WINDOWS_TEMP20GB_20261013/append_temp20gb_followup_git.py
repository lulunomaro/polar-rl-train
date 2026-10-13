from pathlib import Path
import sys,json,time,subprocess
D=Path(__file__).resolve().parent;W=D.parent;R=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap
cap.a.FOLDERS=(*cap.a.FOLDERS,D)
def main():
 label=sys.argv[1];assert label.replace('-','').replace('_','').isalnum()
 dest=R/'history/evidence'/D.name/label
 assert not dest.exists() and not cap.g('status','--porcelain')
 old=cap.a.gitio.refs();rows,files=cap.capture_streaming(dest)
 subprocess.run(['git','-C',str(R),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in files),check=True,capture_output=True)
 cap.g('commit','-m','Append Windows4090 temporary20GB actual repair evidence: '+label)
 cap.g('push','origin','HEAD');head=cap.g('rev-parse','HEAD');cap.a.verify(rows,old,head)
 print(json.dumps(dict(epoch=time.time(),commit=head,remote_main_verified=True,all_old_tag_objects_peeled_preserved=len(old),saved_sources=len(rows),actual_tracked_SHA_verified=True,annotated_stage_objects_unchanged=True,large_originals_retained=True)))
if __name__=='__main__':main()

from pathlib import Path
import sys,json,time,subprocess,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parent;REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_SCUT_WAVE50_GATE_COMPARE_20261012'))
import archive_actual_reference_stage_once as a
a.FOLDERS=(D,W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013')
label=sys.argv[1];assert label.replace('-','').replace('_','').isalnum()
dest=REPO/'history/evidence'/D.name/label
assert not dest.exists() and not a.gitio.g('status','--porcelain')
old=a.gitio.refs();rows,files=a.capture(dest)
subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in files),check=True,capture_output=True)
a.gitio.g('commit','-m','Append actual Wave50 factor evidence: '+label)
a.gitio.g('push','origin','HEAD')
head=a.gitio.g('rev-parse','HEAD');a.verify(rows,old,head)
print(json.dumps(dict(epoch=time.time(),commit=head,remote_main_verified=True,all_old_tag_objects_peeled_preserved=len(old),saved_sources=len(rows),actual_tracked_SHA_verified=True,large_originals_retained=True)))

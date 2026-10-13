from pathlib import Path
import sys,json,time,subprocess
D=Path(__file__).resolve().parent;W=D.parent;R=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_SCUT_WAVE50_GATE_COMPARE_20261012'))
import archive_actual_reference_stage_once as a
def g(*args):
 p=subprocess.run(['git','-c','http.sslBackend=openssl','-C',str(R),*args],capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr;return p.stdout.strip()
a.gitio.g=g
a.FOLDERS=(W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013',W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013',D,W/'MOD4_LOCAL_WAVE50_ACTION_EFFECTIVE_REPAIR_20261013',W/'MOD4_3060_DIRECT_FACTOR_20261013')
label=sys.argv[1];assert label.replace('-','').replace('_','').isalnum()
dest=R/'history/evidence'/D.name/label
assert not dest.exists() and not g('status','--porcelain')
old=a.gitio.refs();rows,files=a.capture(dest)
subprocess.run(['git','-C',str(R),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in files),check=True,capture_output=True)
g('commit','-m','Append actual Windows4090 repair evidence: '+label);g('push','origin','HEAD')
head=g('rev-parse','HEAD');a.verify(rows,old,head)
print(json.dumps(dict(epoch=time.time(),commit=head,remote_main_verified=True,all_old_tag_objects_peeled_preserved=len(old),saved_sources=len(rows),actual_tracked_SHA_verified=True,large_originals_retained=True)))

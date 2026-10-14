from pathlib import Path
import sys,json,time,subprocess
D=Path(__file__).resolve().parent;W=D.parent;R=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap
def main():
    label=sys.argv[1];assert label.replace('-','').replace('_','').isalnum();assert not cap.g('status','--porcelain')
    dest=R/'history/evidence'/D.name/label;old=cap.a.gitio.refs();cap.a.FOLDERS=(D,W/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014',W/'MOD4_3060_LEFT_JOINT_INTERIOR_FACTOR_20261014',W/'MOD4_3060_LEFT_JOINT_MARGIN014_FACTOR_20261014',W/'MOD4_3060_LINUX20K_FINAL_REFERENCE_20261014',W/'MOD4_3060_FULL80_CURRENT_LINUX_FINAL_20261014',W/'MOD4_3060_FULL80_PARAMETER_BOUND_20261014',W/'MOD4_3060_FULL80_FROZEN_CURRENT_20261014',W/'MOD4_3060_LEFT_REPAIR_FULL80_20261014',W/'MOD4_3060_LEFT_REPAIR_RETENTION_20261014',W/'MOD4_LEFT_REPAIR_RESIDUAL_CPU_20261014',W/'MOD4_LEFT_JOINT_CENTER_KEEPSTD_CPU_20261014')
    rows,files=cap.capture_streaming(dest)
    subprocess.run(['git','-C',str(R),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in files),check=True,capture_output=True)
    cap.g('commit','-m','Append left repair final retention failures and CPU residual evidence: '+label);cap.g('push','origin','HEAD')
    head=cap.g('rev-parse','HEAD');cap.a.verify(rows,old,head);print(json.dumps(dict(epoch=time.time(),commit=head,remote_main_verified=True,all_old_tags_preserved=len(old),actual_saved_sources=len(rows),tracked_SHA_verified=True)))
if __name__=='__main__':main()

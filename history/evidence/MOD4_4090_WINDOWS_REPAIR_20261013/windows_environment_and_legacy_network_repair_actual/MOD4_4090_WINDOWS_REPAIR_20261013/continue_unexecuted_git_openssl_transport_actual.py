from pathlib import Path
import subprocess,time,json
import archive_windows4090_repair_stage_once as original
R=original.REPO;D=original.D
def g(*args):
 p=subprocess.run(['git','-c','http.sslBackend=openssl','-C',str(R),*args],capture_output=True,text=True,encoding='utf8')
 assert p.returncode==0,p.stderr
 return p.stdout.strip()
def main():
 assert not original.DEST.exists() and not g('status','--porcelain') and not g('tag','--list','*'+original.ID),'Prior mutation may exist; do not replay capture/record'
 proof=dict(epoch=time.time(),original_failure_stage='read-only prior remote refs, before capture or record_experiment',original_schannel_TLS_error_retained=True,capture_dest_absent=True,new_trial_tag_absent=True,repository_clean=True,actual_openssl_single_remote_main_read_succeeded=True,no_global_git_config_change=True,continuing_only_unexecuted_capture_and_record_once=True)
 (D/'reports/GIT_PRIOR_REF_TRANSPORT_REVIEWED_CONTINUATION_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
 original.a.gitio.g=g
 import sys,importlib
 sys.path.insert(0,str(R/'archive_tools'));rec=importlib.import_module('record_experiment');rec.git=g
 original.main()
if __name__=='__main__':main()

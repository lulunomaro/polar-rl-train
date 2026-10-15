"""Append preserved network/reader errors and actual recovery; no new trial/tag."""
from pathlib import Path
import importlib.util
import json
import subprocess
import time
import traceback

D=Path(__file__).resolve().parent
R=D/'reports'
p=D/'archive_whitev2_native_fixed30_stage_actual_v2_continue_pre_record_once.py'
s=importlib.util.spec_from_file_location('whitev2_postcapture_metadata_only',p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
BASE='e411cb07f275b287f3644a69c4159737a3b0edc3'


def git(*args):
    p=subprocess.run(['git','-c','http.sslBackend=openssl','-c','http.version=HTTP/1.1','-C',str(m.REPO),*args],
                     capture_output=True,text=True,encoding='utf8',timeout=120)
    assert p.returncode==0,p.stderr
    return p.stdout.strip()


def main():
    assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain')
    proof=json.loads((R/'WHITEV2_COMPLETE30_EXISTING_ORDINARY_REMOTE_RECOVERED_V3_ACTUAL.json').read_bytes())
    assert proof['actual_remote_main_stage_tag_original_peeled_all1346oldtags_and_trackedSHA_verified']
    old={}
    for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
        v=line.split();old[v[0]]=(v[1],v[2] if len(v)>2 else v[1])
    assert len(old)==1346
    dest=m.REPO/'history/evidence'/D.name/'ordinary_complete30_original_errors_reader_correction_remote_recovery_v1'
    assert not dest.exists()
    m.g=git;m.cap.g=git;m.cap.a.gitio.g=git;m.N=D
    rows,files=m.capture_previous_scope_metadata_only(dest)
    subprocess.run(['git','-C',str(m.REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],
                   input=b''.join(x.encode()+b'\0' for x in files),capture_output=True,check=True)
    git('commit','-m','Preserve white_v2 upload TLS failures, ordinary tag-reader correction and verified recovery')
    head=git('rev-parse','HEAD');git('push','origin','HEAD')
    # All existing trial tags retain their ORIGINAL peel, not this ordinary HEAD.
    m.cap.a.verify(rows,old,head)
    print(json.dumps(dict(epoch=time.time(),ordinary_commit=head,
        actual_remote_main_all1346oldtags_original_peels_and_trackedSHA_verified=True,
        saved_sources=len(rows),no_new_tag_or_record=True,
        no_GPU_raw_recollection_or_canonical_action=True)))


if __name__=='__main__':
    try:main()
    except BaseException:
        with (R/('WHITEV2_POSTCAPTURE_METADATA_ORDINARY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:
            json.dump(dict(error=traceback.format_exc(),resume_existing_objects_only_ifcommit_created=True,no_record_tag_commit_replay=True),f,indent=2)
        raise

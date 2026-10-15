"""One existing-object recovery after independent nominal CPU work.

Command-local OpenSSL/HTTP1.1; certificate verification and global config stay on.
No record, tag, commit, GPU host transport or budget mutation.
"""
from pathlib import Path
import importlib.util
import json
import subprocess
import time
import traceback

D=Path(__file__).resolve().parent
p=D/'resume_existing_complete30_ordinary_objects_and_verify_actual.py'
s=importlib.util.spec_from_file_location('complete30_existing_recovery_retained',p)
v1=importlib.util.module_from_spec(s)
s.loader.exec_module(v1)


def git(*args):
    p=subprocess.run(['git','-c','http.sslBackend=openssl','-c','http.version=HTTP/1.1',
                      '-C',str(v1.m.REPO),*args],capture_output=True,text=True,encoding='utf8',timeout=120)
    assert p.returncode==0,p.stderr
    return p.stdout.strip()


if __name__=='__main__':
    try:
        v1.m.g=git
        v1.m.cap.g=git
        v1.m.cap.a.gitio.g=git
        v1.main()
    except BaseException:
        with (v1.R/('WHITEV2_COMPLETE30_EXISTING_OPENSSL_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:
            json.dump(dict(error=traceback.format_exc(),existing_commit=v1.HEAD,
                           command_local_OpenSSL_HTTP11_certificate_verification_kept=True,
                           no_record_tag_commit_replay=True,no_GPU_PPO_budget=True),f,indent=2)
        raise

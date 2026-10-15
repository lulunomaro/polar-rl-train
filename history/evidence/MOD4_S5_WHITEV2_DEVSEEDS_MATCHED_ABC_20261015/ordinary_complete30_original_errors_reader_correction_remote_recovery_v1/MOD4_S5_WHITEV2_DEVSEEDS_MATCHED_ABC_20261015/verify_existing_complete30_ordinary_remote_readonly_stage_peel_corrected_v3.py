"""Read-only verify: an ordinary HEAD differs from the unchanged trial tag peel.

V2's generic stage verifier wrongly required the old trial peel == ordinary HEAD.
That reader failure is retained. No push, record, tag, commit or runtime action.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import time
import traceback

D=Path(__file__).resolve().parent
R=D/'reports'
REPO=D.parent/'polar-rl-train'
HEAD='e411cb07f275b287f3644a69c4159737a3b0edc3'
STAGE='57acae57199508c239dc864778cfd791bb4c7fe0'
TAG='trial-20261015-s5-two-devseeds-reviewed-whitev2-frozen-abc-started'
OBJ='0b9f7b0a5b29d4cb124cb8ed40ffa0cca98c6b60'


def git(*args):
    p=subprocess.run(['git','-c','http.sslBackend=openssl','-c','http.version=HTTP/1.1','-C',str(REPO),*args],
                     capture_output=True,text=True,encoding='utf8',timeout=120)
    assert p.returncode==0,p.stderr
    return p.stdout.strip()


def main():
    assert git('rev-parse','HEAD')==HEAD and not git('status','--porcelain')
    local={}
    for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
        v=line.split();local[v[0]]=(v[1],v[2] if len(v)>2 else v[1])
    assert len(local)==1346 and local['refs/tags/'+TAG]==(OBJ,STAGE)
    rows=json.loads((REPO/'history/evidence'/D.name/'ordinary_complete30_two_profile_audit_and_next_admission_v1/REPORT_CAPTURE_INDEX.json').read_bytes())['entries']
    tracked=set(git('ls-files').splitlines())
    count=0
    for row in rows:
        if row.get('Git_path'):
            assert row['Git_path'] in tracked
            assert hashlib.sha256((REPO/row['Git_path']).read_bytes()).hexdigest()==row['archived_sha256']
            count+=1
    remote=dict(line.split()[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines())
    assert remote['refs/heads/main']==HEAD
    assert remote['refs/tags/'+TAG]==OBJ and remote['refs/tags/'+TAG+'^{}']==STAGE
    for name,(obj,peeled) in local.items():
        assert remote[name]==obj and remote.get(name+'^{}',obj)==peeled
    v=dict(epoch=time.time(),existing_ordinary_commit=HEAD,unchanged_stage_commit=STAGE,
           stage_tag=TAG,stage_object=OBJ,
           actual_remote_main_stage_tag_original_peeled_all1346oldtags_and_trackedSHA_verified=True,
           saved_source_entries=len(rows),tracked_rows=count,
           V2_reader_incorrectly_compared_stage_peel_to_ordinary_HEAD_preserved=True,
           read_only_no_push_record_tag_commit_repeated=True,
           command_local_OpenSSL_certificate_verification_kept=True,
           new_postcapture_errors_sources_receipts_still_require_ordinary_supplement=True)
    with (R/'WHITEV2_COMPLETE30_EXISTING_ORDINARY_REMOTE_RECOVERED_V3_ACTUAL.json').open('x',encoding='utf8') as f:
        json.dump(v,f,indent=2)
    print(json.dumps(v))


if __name__=='__main__':
    try:main()
    except BaseException:
        with (R/('WHITEV2_COMPLETE30_READONLY_VERIFY_V3_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:
            json.dump(dict(error=traceback.format_exc(),read_only_no_push_record_tag_commit_GPU_budget=True),f,indent=2)
        raise

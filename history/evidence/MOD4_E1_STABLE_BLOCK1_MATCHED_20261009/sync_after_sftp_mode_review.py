"""Independent evidence-only sync after the original exclusive-mode reader rejection."""
from pathlib import Path
import hashlib,inspect,json,os,sys,time,traceback
import paramiko
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
MASTER='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
def sha(b):return hashlib.sha256(b).hexdigest()
def save(name,v):
    p=R/name;assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def main():
    assert (R/'DIAGNOSIS_SYNC_01_ERROR.json').is_file() and not (R/'METADATA_SYNCED.json').exists()
    proof_source=inspect.getsource(paramiko.SFTPClient.open)
    assert 'if ("w" in mode) or ("+" in mode) or ("a" in mode)' in proof_source and 'if "x" in mode:' in proof_source
    mode='wbx';assert 'w' in mode and 'x' in mode
    sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
    secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret
    sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
    c=connect()
    try:
        with c.open_sftp() as s:
            root='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports/'
            rejected=root+'E1_GENTLE_BLOCK1_MATCHED_REVIEW.json';raw=s.open(rejected).read()
            assert raw==b'','Preserve and inspect unexpected partial; do not overwrite'
            context={}
            for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOE_PLAN_EXECUTION_CURRENT.json'):
                b=s.open(root+name).read();a=json.loads(b);context[name]=dict(sha256=sha(b),bytes=len(b))
                if name=='PLAN_APPROVAL.json':assert a['approved'] and a['approved_plan_sha256']==MASTER and 'MOD4-RM-TERRAIN-CURRICULUM-REVISION-003' in a['plan_annotations']
            uploads=[]
            for local,name in [(R/'REVIEW.json','E1_GENTLE_BLOCK1_MATCHED_ACTUAL_REVIEW.json'),(R/'RETENTION_REGRESSION_DIAGNOSIS.json','E1_GENTLE_BLOCK1_RETENTION_REGRESSION_DIAGNOSIS.json'),(R/'REPORT.md','E1_GENTLE_BLOCK1_MATCHED_REPORT.md')]:
                remote=root+name
                try:s.stat(remote)
                except FileNotFoundError:pass
                else:raise AssertionError('Report exists; independent sync must not overwrite '+remote)
                b=local.read_bytes()
                with s.open(remote,mode) as f:f.write(b)
                assert s.open(remote).read()==b
                uploads.append(dict(source=str(local),remote=remote,bytes=len(b),sha256=sha(b),bytes_exact=True))
            marker='E1-STABLE-BLOCK1-MATCHED-20261009';handoff=root+'LATEST_HANDOFF.md';before=s.open(handoff).read();assert marker.encode() not in before
            addition=('\n\n## '+marker+' actual bounded retention diagnosis\n'
                'Own complete32521 SHA498bd8813bc8957ff0c1f8f306c864472c4175455589ad8f9cd17a1c77bacd10/source313/57snapshot/CPU96 and469updates/225120000envsteps/45024callbacks are verified,7222.999456406s uniquely settled. Four completed3060 cases/full route raw independently reviewed. Gentle signed traversal functional, but inherited world factual63/64->16/64 (all yaw+-2 cross residuals) and negative pure4pi5/8->0/8; do not call mature, harmless residual, or physics fault. See E1_GENTLE_BLOCK1_MATCHED_ACTUAL_REVIEW.json, E1_GENTLE_BLOCK1_RETENTION_REGRESSION_DIAGNOSIS.json and E1_GENTLE_BLOCK1_MATCHED_REPORT.md. The empty E1_GENTLE_BLOCK1_MATCHED_REVIEW.json from rejected Paramiko xb mode is retained; current ACTUAL_REVIEW is the complete independently synced source. Current second block keeps original own fullsave boundary; no hotpatch/kill/clearactive/third gentle block. After actual block2 review, if same systematic regression persists, select earlier balanced complete reviewed E1 source for bounded corrective/progressive work.003 G1 newgeometry ground/contact/reset/fullresume scope required; no quota70/20/10 experiment, paused93/94 or MuJoCo. E0 remains frozen. Protected central active learning/evaluation/budget files unchanged; no canonical transactions.\n').encode()
            assert s.open(handoff).read()==before
            with s.open(handoff,'ab') as f:f.write(addition)
            after=s.open(handoff).read();assert after==before+addition
            for name,v in context.items():assert sha(s.open(root+name).read())==v['sha256'],('Protected metadata changed concurrently',name)
            save('METADATA_SYNCED.json',dict(epoch=time.time(),trial_id=marker,uploads=uploads,original_partial_retained=dict(path=rejected,bytes=0,sha256=sha(b'')),installed_paramiko_open_source_sha256=sha(proof_source.encode()),original_mode='xb',reviewed_explicit_write_exclusive_mode=mode,actual_report_write_and_roundtrip_proven=True,
                central_active_learning_evaluation_budget_files_byte_unchanged=context,handoff_before_sha256=sha(before),handoff_after_sha256=sha(after),append_exact=True,production_GPU_PPO_canonical_transactions=0,new_budget_seconds=0))
            print(json.dumps(dict(synced_complete_review=True,original_empty_report_and_error_retained=True,production_unchanged=True,new_budget_seconds=0)))
    finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
    try:main()
    except Exception:
        save('SYNC_MODE_REVIEW_02_ERROR.json',dict(epoch=time.time(),trial_id='E1-STABLE-BLOCK1-SYNC-MODE-02',error=traceback.format_exc(),do_not_repeat_or_change_training=True));raise

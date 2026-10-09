"""Complete only unexecuted metadata CAS after original remote code literal rejection."""
from pathlib import Path
import os,sys,json,time,hashlib,shlex,traceback,ast
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_G2_MATCHED_CONTINUE_20261010';ER='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports'
def main():
    assert (R/'SYNC_ERROR.json').exists() and not (R/'METADATA_SYNCED.json').exists() and not (R/'LITERAL_REVIEW_SYNC_STARTED.json').exists()
    error=json.loads((R/'SYNC_ERROR.json').read_bytes());assert 'SyntaxError: unterminated string literal' in error['error']
    src=(D/'sync_matched_continuation_once.py').read_bytes();tree=ast.parse(src.decode());texts=[n.value for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str) and 'R=Path(ER);D=Path(ROOT)' in n.value];assert len(texts)==1
    code=texts[0];i=code.index("append=('");k=code.index('\nassert all(',i)
    marker='E1 G2 matched32058 same20mm900s continuation20261010:'
    text='\n\n'+marker+' 123 complete four actual cases/8JSON byteexact/fullterrain NPZ SHA. Forward27/27 reverse26/27 ordinary0, incomplete after-support prefix retained. Oldflat errors.024461027/.043439623, pure+4pi8/8 negative5/8, world63/64 to62/64/cross.053276684 small residual retained; no previous severe collapse and no permanent anti-forgetting/E1/RM graduation. Selected32058/42cdc9d2 CPU96/source329/snapshot62; new330 original329 byteexact plus one unique controller. SameG2 fullterrain and D1D7 optimizer/globalnamed/privateCUDA restore then newepisode, actual startup priority. One900s includes load-save-exit, source330 root MOD4_S3_E1_G2_MATCHED_CONTINUE_20261010;124fourcases after ownfullsave then savedreviewready/noactive, no automatic morePPO before actual review. No repeated CPU/SDK/native/PPOpreflight/clock. Source/own PID/proc/canonical real facts priority, master/RM003002001/budget828000 unchanged/new0. Original metadata code SyntaxError happened before CAS/GPU action; exclusive evidence files were already SHA exact, only missing CAS completed by new literal-verified entry; all source/error/receipts retained Git.\n'
    code=code[:i]+"append="+repr(text)+".encode();assert hp.read_bytes()==hb;tmp=hp.with_name(hp.name+'.G2matched-'+str(time.time_ns()));tmp.write_bytes(hb+append);os.replace(tmp,hp)"+code[k:]
    code=code.replace('Path(ER)','Path('+repr(ER)+')').replace('Path(ROOT)','Path('+repr(ROOT)+')');compile(code,'<reviewed-metadata-CAS>','exec')
    (R/'LITERAL_REVIEW_SYNC_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-MATCHED-METADATA-LITERAL-REPAIR-01',original_source_sha256=H(src),remote_code_SHA=H(code.encode()),remote_code_compiles=True,no_repeat_exclusive_evidence_write=True)),encoding='utf8')
    secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
    try:
        files={'E1_G2_MODEL32058_COMPLETE_MATCHED_REVIEW.json':R/'MATCHED_123_REVIEW.json','SELECTED_E1_G2_MATCHED_CONTINUATION_SOURCE.json':R/'SELECTED_E1_G2_MATCHED_CONTINUATION_SOURCE.json','E1_G2_MATCHED_CONTINUATION_REPORT.md':R/'REPORT.md','NEXT_G2_MATCHED_CONTINUATION_REVIEW_WORK_ORDER.md':R/'NEXT_G2_MATCHED_CONTINUATION_REVIEW_WORK_ORDER.md','E1_G2_MATCHED_CONTINUATION_CURRENT_ACTUAL.json':sorted(R.glob('MATCHED_ACTUAL_*.json'))[-1]}
        with c.open_sftp() as f:
            for n,p in files.items():assert f.open(ER+'/'+n).read()==p.read_bytes(),n
        _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);b=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(b+err).decode(errors='replace');proof=json.loads(b)
        proof.update(trial_id='E1-G2-MATCHED-METADATA-LITERAL-REPAIR-01',original_failed_parser_and_source_preserved=True,only_previously_unexecuted_metadata_CAS_completed=True,files=[dict(name=n,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for n,p in files.items()])
        raw=json.dumps(proof,indent=2).encode();(R/'METADATA_SYNCED.json').write_bytes(raw)
        with c.open_sftp() as f:
            with f.open(ER+'/E1_G2_MATCHED_CONTINUATION_METADATA_SYNCED.json','wbx') as out:out.write(raw)
            assert f.open(ER+'/E1_G2_MATCHED_CONTINUATION_METADATA_SYNCED.json').read()==raw
        print(json.dumps(proof))
    finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
    try:main()
    except Exception:
        (R/'LITERAL_REVIEW_SYNC_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-MATCHED-METADATA-LITERAL-REPAIR-01',error=traceback.format_exc(),no_blind_repeat=True),indent=2),encoding='utf8');raise

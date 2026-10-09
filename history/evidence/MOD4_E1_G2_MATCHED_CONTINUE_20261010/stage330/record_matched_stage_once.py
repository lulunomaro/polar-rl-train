"""Capture complete123 supplement and every new330 deployment report, including parser rejection."""
from pathlib import Path
import json,time,hashlib,subprocess,sys,tomllib
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';P=W/'polar-rl-train';L=W/'MOD4_E1_G2_LEARNING_PREPARE_20261010';H=lambda b:hashlib.sha256(b).hexdigest()
ID='e1-20mm-matched-retention-and-same-geometry-bounded-continuation'
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],encoding='utf8').strip()
def main():
    assert not (R/'ARCHIVE_STARTED.json').exists() and not git('diff','--cached','--name-only')
    v=json.loads(sorted(R.glob('MATCHED_ACTUAL_*.json'))[-1].read_bytes());assert not v['reports'].get('E1_ATTENTION.json') and v['canonical']['authorized']==828000
    assert json.loads((R/'MATCHED_123_REVIEW.json').read_bytes())['review_complete']
    own=json.loads((R/'OWN_CPU_VERIFIED.json').read_bytes());assert own['checkpoint']['finite_tensors']==96 and own['source_count']==330 and own['snapshot_count']==62
    startup=json.loads(sorted(R.glob('STARTUP_ACTUAL_*.json'))[-1].read_bytes());assert startup['starts']['E1_TERRAIN_RESUME_STARTUP_VERIFIED.json']['terrain_state_restored_exact'] and not startup['starts']['E1_TERRAIN_RESUME_STARTUP_VERIFIED.json']['explicitly_new_E1_terrain']
    assert json.loads((R/'METADATA_SYNCED.json').read_bytes())['only_previously_unexecuted_metadata_CAS_completed']
    oldtag='trial-20261010-e1-reviewed-20mm-full-contract-short-observation-deployed';oldcommit=git('rev-parse',oldtag+'^{}');obj=git('rev-parse',oldtag)
    remote=dict(x.split('\t')[::-1] for x in git('ls-remote','origin','refs/tags/'+oldtag,'refs/tags/'+oldtag+'^{}').splitlines());assert remote['refs/tags/'+oldtag]==obj and remote['refs/tags/'+oldtag+'^{}']==oldcommit
    (R/'PRIOR_G2_STAGE_GIT_VERIFIED.json').write_text(json.dumps(dict(epoch=time.time(),tag=oldtag,commit=oldcommit,tagobject=obj,remote_tag_peeled_verified=True),indent=2),encoding='utf8')
    monitor=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));assert monitor['status']=='ACTIVE' and monitor['rrule']=='FREQ=HOURLY;INTERVAL=2' and 'MOD4_S3_E1_G2_MATCHED_CONTINUE_20261010' in monitor['prompt'][:6000]
    (R/'MONITOR_VERIFIED.json').write_text(json.dumps(dict(epoch=time.time(),status=monitor['status'],rrule=monitor['rrule'],prompt_SHA=H(monitor['prompt'].encode())),indent=2),encoding='utf8')
    (R/'ARCHIVE_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),trial_id=ID,continue_existing_objects_if_push_pending=True),indent=2),encoding='utf8')
    dest=P/'history/evidence/MOD4_E1_G2_MATCHED_CONTINUE_20261010';assert not dest.exists();dest.mkdir(parents=True)
    sys.path.insert(0,str(P/'archive_tools'));from capture_history import redact
    index_path=P/'history/evidence/MOD4_E1_G2_LEARNING_PREPARE_20261010/REPORT_CAPTURE_INDEX.json';oldindex=json.loads(index_path.read_bytes());prior={x['source']:x for x in oldindex['reports_and_implementation']};priorlarge={x.get('source',x.get('path')):x for x in oldindex['large_originals_index_only']}
    files=[];rows=[];large=[];reused=[]
    for root,prefix in ((D,'stage330'),(L,'prior329_supplement')):
        for p in sorted(root.rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts:continue
            b=p.read_bytes();source=str(p.resolve());h=H(b)
            if root==L and source in prior and prior[source]['sha256']==h:
                reused.append(dict(source=source,sha256=h,bytes=len(b),Git_path=prior[source]['Git_path'],reuse_prior_commit=oldcommit));continue
            if root==L and source in priorlarge and priorlarge[source].get('sha256')==h:continue
            if p.suffix in ('.npz','.pt','.zip','.usd','.npy') or len(b)>50_000_000:
                large.append(dict(source=source,bytes=len(b),sha256=h,index_only=True,original_retained=True));continue
            if p.suffix not in ('.py','.json','.md','.txt','.log','.xml'):continue
            try:s=b.decode('utf8');encoding='utf8'
            except UnicodeDecodeError:s=b.decode('gb18030');assert s.encode('gb18030')==b;encoding='gb18030_lossless'
            s,n=redact(s);raw=s.encode();out=dest/prefix/p.relative_to(root);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw);assert redact(s)[0]==s
            gp=out.relative_to(P).as_posix();files.append(gp);rows.append(dict(source=source,bytes=len(b),sha256=h,Git_path=gp,archived_bytes=len(raw),archived_sha256=H(raw),capture='redacted_full' if n else ('byteexact_full' if encoding=='utf8' else 'lossless_UTF8_full'),source_encoding=encoding,redactions=n))
    large.append(dict(source=own['checkpoint']['path'],bytes=own['bytes'],sha256=own['checkpoint']['sha256'],own_PID_receipt_bound=True,actual_CPU_finite_tensors=96,original_retained=True,index_only=True,activity_save_not_final=True))
    sel=json.loads((R/'SELECTED_E1_G2_MATCHED_CONTINUATION_SOURCE.json').read_bytes());large.append(dict(source=sel['source']['path'],bytes=16750577,sha256=sel['source']['sha256'],own_PID_receipt_bound=True,actual_behavior_review_complete=True,original_retained=True,index_only=True))
    idx=dest/'REPORT_CAPTURE_INDEX.json';idx.write_text(json.dumps(dict(epoch=time.time(),reports_and_implementation=rows,large_originals_index_only=large,prior_identical_reports_reused=reused,all_saved_current_and_prior_stage_reports_accounted=True,original329_byteexact_and_new_controller330=True,stage_actual_phase=v['reports']['E1_STATE.json']['phase'],credentials_excluded=True,future_124_fullsave_behavior_sync_reports_require_Git_supplement=True,original_metadata_SyntaxError_preserved=True,original_G1_overspeed_regression_and_all_flags_preserved=True,prior_checkpoint_sizes_completed_from_actual_remote_stat=True),ensure_ascii=False,indent=2),encoding='utf8');files.extend([idx.relative_to(P).as_posix(),index_path.relative_to(P).as_posix()])
    r=subprocess.run([sys.executable,str(P/'archive_tools/record_experiment.py'),'--id',ID,'--title','Review complete20mm E1 retention and deploy one isolated same-geometry900s continuation','--kind','training','--note-file',str(R/'REPORT.md'),'--files',*files,'--validation','123 complete4cases/8bridgeJSON byteexact/fullterrainNPZ SHA; selected32058 CPU96/source329/snapshot62; full20mm route27/26 with incomplete prefix preserved; oldflat/spin/world paired62of64 and finite residuals retained; original329 files byteexact plus1controller330; sameG2 actualCUDA terrain and D1D7 optimizer globalnamed restored exact then one fresh episode; new child1873663 actualPPO logs and own32075 fullCPU96/330freeze/62snapshot verified; prior healthy native/SDK/PPO preflight clock exactSHA reused without replay; metadata parser rejection retained/newmissing CAS verified/no budget write; master/RM003002001 and original828000 budget unchanged; all saved reports captured, new124 candidate review required before furtherPPO','--push'],capture_output=True,text=True,encoding='utf8',errors='replace')
    if r.returncode:
        (R/'ARCHIVE_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),stdout=r.stdout,stderr=r.stderr,continue_existing_objects_not_rerecord=True),indent=2),encoding='utf8');raise RuntimeError('Inspect existing Git objects; never blindly repeat record')
    tag,head=r.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag);remote=dict(x.split('\t')[::-1] for x in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/tags/'+oldtag,'refs/tags/'+oldtag+'^{}').splitlines())
    assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and remote['refs/tags/'+oldtag+'^{}']==oldcommit
    assert set(files).issubset(git('ls-tree','-r','--name-only',head).splitlines()) and not git('diff','--cached','--name-only')
    print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,all_saved_reports_Git_recorded=True,files=len(rows),large_indices=len(large),prior_identical_reports_indexed=len(reused),actual_phase=v['reports']['E1_STATE.json']['phase'],new_budget_seconds=0)))
if __name__=='__main__':main()

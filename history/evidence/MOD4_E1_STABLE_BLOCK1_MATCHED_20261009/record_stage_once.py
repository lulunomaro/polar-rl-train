"""Archive all new block1 evaluation/diagnosis/sync reports exactly once."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time,tomllib
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';P=W/'polar-rl-train'
ID='e1-gentle-block1-fullroute-and-systematic-retention-regression-reviewed'
def sha(b):return hashlib.sha256(b).hexdigest()
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],text=True,encoding='utf8').strip()
def main():
    assert not (R/'ARCHIVE_STARTED.json').exists(),'Archive already attempted; resume existing objects if necessary'
    assert not git('tag','--list','trial-'+time.strftime('%Y%m%d')+'-'+ID)
    assert not git('diff','--cached','--name-only'),'Do not modify another staging area'
    master=P/'history/plans/MOD4_MOE_MASTER_PLAN.md';assert sha(master.read_bytes())=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
    sync=json.loads((R/'METADATA_SYNCED.json').read_bytes());assert sync['append_exact'] and sync['actual_report_write_and_roundtrip_proven']
    m=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
    assert m['status']=='ACTIVE' and m['rrule']=='FREQ=HOURLY;INTERVAL=2' and '63/64->16/64' in m['prompt'][:4000] and '\ufffd' not in m['prompt']
    mon=dict(epoch=time.time(),automation_id=m['id'],name=m['name'],status=m['status'],rrule=m['rrule'],target_thread_id=m['target_thread_id'],prompt_sha256=sha(m['prompt'].encode()),actual_block1_retention_regression_and_next_boundary_review_preserved=True,human_original_plan_and003_kept=True,no_mixed20k_candidate_adopted=True,no_healthy_worker_restart_or_training_mutation=True)
    path=R/'MONITOR_VERIFIED.json';assert not path.exists();path.write_text(json.dumps(mon,ensure_ascii=False,indent=2),encoding='utf8')
    path=R/'ARCHIVE_STARTED.json';path.write_text(json.dumps(dict(epoch=time.time(),trial_id=ID,do_not_repeat_record_if_commit_created=True),indent=2),encoding='utf8')
    dest=P/'history/evidence/MOD4_E1_STABLE_BLOCK1_MATCHED_20261009';assert not dest.exists();dest.mkdir(parents=True)
    sys.path.insert(0,str(P/'archive_tools'));from capture_history import redact
    files=[];index=[]
    def capture(p,relative):
        original=p.read_bytes();text=original.decode('utf8');archived,count=redact(text);raw=archived.encode('utf8')
        out=dest/relative;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)
        assert redact(raw.decode('utf8'))[0]==raw.decode('utf8')
        files.append(out.relative_to(P).as_posix())
        index.append(dict(source=str(p.resolve()),source_bytes=len(original),source_sha256=sha(original),Git_path=out.relative_to(P).as_posix(),archived_bytes=len(raw),archived_sha256=sha(raw),capture='redacted_full_text' if count else 'full_byte_exact',redactions=count))
    for p in sorted(D.rglob('*')):
        if p.is_file() and p.suffix in {'.py','.json','.md','.txt','.log'} and '__pycache__' not in p.parts:capture(p,str(p.relative_to(D)))
    baseline=W/'MOD4_S3_E1_ROUTE_BEHAVIOR_CONTINUATION_20261009/reports/actual_cases'
    large=[]
    for kind in ('terrain-flat','retention-flat','retention-spin','retention-world'):
        jid='clk2500-closure-episode-d3-'+('114-e1-terrain32053-flat' if kind=='terrain-flat' else '115-e1-retention32053-'+kind.rsplit('-',1)[-1])
        folder=baseline/jid
        for name in ('probe.json','result.json'):capture(folder/name,'reused_previous32053_cases/'+jid+'/'+name)
        probe=json.loads((folder/'probe.json').read_bytes())
        if 'full_route_raw' in probe:
            raw=folder/probe['full_route_raw']['name'];assert sha(raw.read_bytes())==probe['full_route_raw']['sha256']
            large.append(dict(source=str(raw.resolve()),bytes=raw.stat().st_size,sha256=probe['full_route_raw']['sha256'],kind='previous32053_NPZ_index_only',original_retained=True))
    collected=json.loads((R/'COLLECTED.json').read_bytes())
    for a in collected['files']:
        if a.get('large_artifact_SHA_only_in_Git'):large.append(a)
    ck=collected['passed']['checkpoint'];large.append(dict(source=ck['path'],sha256=ck['sha256'],kind='own_checkpoint_index_only',finite_tensors_in_original_completed_receipt=ck['finite_tensors'],original_retained=True))
    cp=collected['publication']['source'];assert cp['sha256']==ck['sha256'];large.append(dict(source=cp['path'],bytes=cp['bytes'],sha256=cp['sha256'],kind='exact_SHA_evaluation_copy_index_only',original_retained=True))
    idx=dest/'REPORT_CAPTURE_INDEX.json';idx.write_text(json.dumps(dict(epoch=time.time(),reports_and_implementation=index,large_originals_index_only=large,all_saved_stage_reports_captured=True,previous_failures_and_empty_remote_artifact_not_overwritten=True,credentials_excluded=True,report_count=sum(x['Git_path'].endswith(('.json','.md','.txt','.log')) for x in index)),ensure_ascii=False,indent=2),encoding='utf8');files.append(idx.relative_to(P).as_posix())
    cmd=[sys.executable,str(P/'archive_tools/record_experiment.py'),'--id',ID,'--title','Review E1 gentle block1 full route and diagnose systematic inherited-world regression','--kind','evaluation','--note-file',str(R/'REPORT.md'),'--files',*files,'--validation','Own complete32521/source313/57snapshots and unique7222.999456406s segment; four actual same-platform paired cases/8 bridged JSON/full184MB raw and contact-integral/target/root30q audits; signed world63/64->16/64 and negative4pi5/8->0/8 retained; independent metadata-mode repair and all original reader errors recorded; current second block untouched; no new GPU/PPO/budget, monitor2h ACTIVE, master unchanged','--push']
    q=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace')
    if q.returncode:
        # Preserve the error; never re-run record when it may have created objects.
        (R/'ARCHIVE_FIRST_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),exit_code=q.returncode,stdout=q.stdout,stderr=q.stderr,resume_existing_objects_not_record=True),ensure_ascii=False,indent=2),encoding='utf8')
        raise RuntimeError('Archive rejected or push pending; inspect existing Git objects without re-recording')
    tag,head=q.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag)
    remote=dict(x.split('\t')[::-1] for x in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
    assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
    tracked=set(git('ls-tree','-r','--name-only',head).splitlines());assert set(files).issubset(tracked)
    assert not git('diff','--cached','--name-only')
    # Final verification stays in tool output; no endless new unarchived receipt.
    print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,all_saved_stage_reports_tracked=True,captured_files=len(index),large_raw_checkpoints_not_committed=True,monitor_active_2h=True,new_budget_seconds=0),ensure_ascii=True))
if __name__=='__main__':main()

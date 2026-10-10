"""Unique real CURB stage archive, including all saved errors and raw SHA indices."""
from curb_io import *
import subprocess, traceback
P=W/'polar-rl-train'
ID='e1-independent-curb20-mirrored-frozen-route-deployed'
def git(*args):
    return subprocess.check_output(['git','-C',str(P),*args],encoding='utf8').strip()
def capture(dest):
    assert not dest.exists();dest.mkdir(parents=True)
    sys.path.insert(0,str(P/'archive_tools'));from capture_history import redact
    rows=[];large=[];files=[]
    for p in sorted(D.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts:continue
        b=p.read_bytes();source=str(p.resolve());h=H(b)
        if p.suffix.lower() in ('.npz','.pt','.zip','.usd','.npy','.partial') or len(b)>50_000_000:
            large.append(dict(source=source,bytes=len(b),sha256=h,index_only=True,original_retained=True));continue
        assert p.suffix.lower() in ('.py','.md','.json','.txt','.log'),str(p)
        clean,n=redact(b.decode('utf8'));raw=clean.encode();out=dest/p.relative_to(D)
        out.parent.mkdir(parents=True,exist_ok=True);assert not out.exists();out.write_bytes(raw)
        assert redact(clean)[0]==clean
        gp=out.relative_to(P).as_posix();files.append(gp)
        rows.append(dict(source=source,bytes=len(b),sha256=h,Git_path=gp,archived_bytes=len(raw),archived_sha256=H(raw),redactions=n,capture='redacted_full' if n else 'byteexact_full'))
    publication=json.loads((R/'CURB132_PUBLISHED.json').read_bytes())
    for job in publication['jobs']:
        for label,a in job['artifacts'].items():large.append(dict(source=a['path'],bytes=a['bytes'],sha256=a['sha256'],index_only=True,original_retained=True,actual_remote_bytes_SHA_verified=True,role=label))
    for p in R.glob('CURB132_COLLECTED_[0-9]*.json'):
        for x in json.loads(p.read_bytes())['files']:
            if x.get('large_original_index_only'):large.append(dict(source=x['source'],bytes=x['bytes'],sha256=x['sha256'],index_only=True,original_retained=True))
    index=dict(epoch=time.time(),reports_and_implementation=rows,large_originals_index_only=large,
        all_saved_new_CURB_reports_errors_sources_captured=True,credentials_excluded=True,
        old_131_129_128_complete_not_replayed=True,new_budget_seconds=0,
        later_reports_need_ordinary_supplement=True)
    ip=dest/'REPORT_CAPTURE_INDEX.json';ip.write_bytes(json.dumps(index,ensure_ascii=False,indent=2).encode());files.append(ip.relative_to(P).as_posix())
    return index,files
def main():
    assert not git('status','--porcelain') and not (R/'CURB_STAGE_ARCHIVE_STARTED.json').exists()
    assert json.loads((R/'CURB132_SCOPE_METADATA_SYNCED.json').read_bytes())['curb132_scope_synced']
    tags=['trial-20261011-e1-terrain-subexperts-approved-wave-isolation-and-retention-regression',
        'trial-20261010-e1-command-retention-complete-review-and-matched900s-continuation',
        'trial-20261010-e1-flat-command-retention-admitted-and-strict-rng-ownership-repaired',
        'trial-20261010-e1-command-retention-saved-episode-resume-assertion-repaired',
        'trial-20261010-e1-reviewed-35mm-full-contract-scope-and-short-observation-deployed',
        'trial-20261010-e1-matched-retention-tradeoff-and-35mm-frozen-package-repair']
    old={t:dict(commit=git('rev-parse',t+'^{}'),tagobject=git('rev-parse',t)) for t in tags}
    head=git('rev-parse','HEAD');refs=['refs/heads/main']+sum((['refs/tags/'+t,'refs/tags/'+t+'^{}'] for t in tags),[])
    remote=dict(line.split('\t')[::-1] for line in git('ls-remote','origin',*refs).splitlines());assert remote['refs/heads/main']==head
    for t,v in old.items():assert remote['refs/tags/'+t]==v['tagobject'] and remote['refs/tags/'+t+'^{}']==v['commit']
    save('CURB_STAGE_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_remote_main=head,old_tags=old,no_repeat_if_commit_or_tag_created=True))
    index,files=capture(P/'history/evidence'/D.name/'curb132_mirrored_frozen_scope')
    args=[sys.executable,str(P/'archive_tools/record_experiment.py'),'--id',ID,
        '--title','Deploy independent derived20mm mirrored curb frozen route under approved terrain subexpert plan',
        '--kind','deployment','--note-file',str(R/'NEXT_CURB20_FROZEN_AND_INDEPENDENT_LEARNING_WORK_ORDER.md'),
        '--files',*files,'--validation',
        'Approved004 preserved; actualWave366 fullsaved and allparentguardianchildexited/twofcntlOSlocksfree/activeNone/uniquesettled. Full131 regression and7validincompleteprefixes retained, candidate2b4 notqualified or selectedsource. New independentCURB scope selectedcomplete1293c97 CPU102/17615538bytes. Derived20mm unsmoothedverticalriser and150mmstripcontinuousupperplatform mirrored9mtiles. Existing235CPUcomponent reused; newSDKcoordinate186independentrays+2verticalwallhits max9.3675e-17 onlyCPUproof. New283SOURCE_MANIFEST allbytesexact, inherited279members unchanged, fullstepping health forceintegral hardware auditorASTexact. Actual132 frozen80env1500controls15s20260928white3 published tohealthyunchanged3060worker after actualCIMargvcreation/attentionnull/pinnedsteps checks. No4090PPO/launch orcanonicalwrite/extension; fullrawcomplete review and newgeometrySDKnativeCPUCUDAfullrestorefullPPO stillgovernlearningadmission. Explicitnewassignment/privateRNGmigration workorder, nooldloaderrelaxation. Allnewreports/readlocatorerrors/pending/sync/workorder/source captured, largeZIPweightsNPZ indices only. E0Waveprotected/gateuntrained/noS7S8teacher/oldcomplete replay orgraduationclaim.','--push']
    run=subprocess.run(args,capture_output=True,text=True,encoding='utf8',errors='replace')
    if run.returncode:
        save('CURB_STAGE_RECORD_ERROR.json',dict(epoch=time.time(),stdout=run.stdout,stderr=run.stderr,returncode=run.returncode,may_have_committed_do_not_repeat=True));raise RuntimeError('Inspect original Git objects and continue only pending push')
    tag,commit=run.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag)
    remote=dict(line.split('\t')[::-1] for line in git('ls-remote','origin',*refs,'refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
    assert remote['refs/heads/main']==commit and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==commit
    for t,v in old.items():assert remote['refs/tags/'+t]==v['tagobject'] and remote['refs/tags/'+t+'^{}']==v['commit']
    tracked=set(git('ls-tree','-r','--name-only',commit).splitlines());assert set(files)<=tracked
    for row in index['reports_and_implementation']:assert H((P/row['Git_path']).read_bytes())==row['archived_sha256']
    assert not git('status','--porcelain')
    result=dict(epoch=time.time(),tag=tag,commit=commit,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,
        reports_captured=len(index['reports_and_implementation']),large_indices=len(index['large_originals_index_only']),six_original_tag_objects_unchanged=True)
    save('CURB_STAGE_GIT_RECORDED.json',result);print(json.dumps(result))
if __name__=='__main__':
    try:main()
    except Exception:
        if not (R/'CURB_STAGE_ARCHIVE_CALL_ERROR.json').exists():save('CURB_STAGE_ARCHIVE_CALL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_repeat_record_of_committed_stage=True))
        raise

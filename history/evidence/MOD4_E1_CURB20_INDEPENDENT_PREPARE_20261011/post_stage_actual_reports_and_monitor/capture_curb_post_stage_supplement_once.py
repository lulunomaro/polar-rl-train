"""Sync verified stage Git reference, then capture every later saved CURB report."""
from curb_io import *
from record_curb_scope_stage_once import P,git
import subprocess,traceback
def main():
    stage=json.loads((R/'CURB_STAGE_GIT_RECORDED.json').read_bytes())
    assert stage['remote_main_tag_peeled_verified'] and not stage['push_pending']
    assert not git('status','--porcelain') and not (R/'CURB_SUPPLEMENT_STARTED.json').exists()
    save('CURB_SUPPLEMENT_STARTED.json',dict(epoch=time.time(),trial_id='E1-CURB20-POST-STAGE-REPORTS-01',stage=stage,no_new_trial=True))
    n,w=connect_both()
    try:
        with n.open_sftp() as f:
            p=R/'CURB_STAGE_GIT_RECORDED.json';b=p.read_bytes()
            with f.open(E+'/reports/E1_CURB20_132_STAGE_GIT_RECORDED.json','wbx') as out:out.write(b)
            assert f.open(E+'/reports/E1_CURB20_132_STAGE_GIT_RECORDED.json').read()==b
        result=linux_json(n,r'''from pathlib import Path
import json,time,hashlib,os
R=Path(CENTRAL)/'reports';B=Path(BUDGET);budget=B.read_bytes()
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
stage=json.loads((R/'E1_CURB20_132_STAGE_GIT_RECORDED.json').read_bytes());assert stage['remote_main_tag_peeled_verified'] and not stage['push_pending']
cp=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=cp.read_bytes();v=json.loads(before);a=v['terrain_subexpert_revision004']['curb132_frozen_scope'];assert a['actual_published'] and 'git_record' not in a
a['git_record']=dict(stage=stage,post_stage_reports_require_supplement=True)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert cp.read_bytes()==before;tmp=cp.with_name(cp.name+'.CurbGit-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,cp)
hp=R/'LATEST_HANDOFF.md';old=hp.read_bytes();marker='IndependentCURB132 stage Git verified:';assert marker.encode() not in old
msg='\n\n'+marker+' '+stage['tag']+' commit '+stage['commit']+' annotatedobject '+stage['tagobject']+' actualremote main/tag/peeled verified. Allsaved132scope/source/readonlylocatorerrors/pending/sync/workorder/monitorprior and largeindices retained; latercomplete132/readers/monitor/sync receipts must ordinarysupplement. No record/tag/commit replay or GPU/ledger mutation.\n'
assert hp.read_bytes()==old;tmp=hp.with_name(hp.name+'.CurbGit-'+str(time.time_ns()));tmp.write_bytes(old+msg.encode());os.replace(tmp,hp)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),stage_Git_reference_synced=True,protected_master_approval_tracks_RM_canonical_bytes_preserved=True)))
'''.replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)))
        p=save('CURB_STAGE_GIT_METADATA_SYNCED.json',result)
        with n.open_sftp() as f:
            with f.open(E+'/reports/E1_CURB20_132_STAGE_GIT_METADATA_SYNCED.json','wbx') as out:out.write(p.read_bytes())
            assert f.open(E+'/reports/E1_CURB20_132_STAGE_GIT_METADATA_SYNCED.json').read()==p.read_bytes()
    finally:cleanup(n,w)
    known={};knownlarge={}
    for q in (P/'history/evidence').rglob('*CAPTURE_INDEX*.json'):
        try:v=json.loads(q.read_bytes())
        except (ValueError,UnicodeDecodeError):continue
        for row in v.get('reports_and_implementation',[]):
            if row.get('source') and row.get('sha256') and row.get('Git_path'):known[(row['source'],row['sha256'])]=row
        for row in v.get('large_originals_index_only',[]):
            if row.get('source') and row.get('sha256'):knownlarge[(row['source'],row['sha256'])]=q.relative_to(P).as_posix()
    dest=P/'history/evidence'/D.name/'post_stage_actual_reports_and_monitor';assert not dest.exists();dest.mkdir(parents=True)
    sys.path.insert(0,str(P/'archive_tools'));from capture_history import redact
    rows=[];large=[];reuse=[];files=[]
    for p in sorted(D.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts:continue
        b=p.read_bytes();source=str(p.resolve());h=H(b)
        if (source,h) in known:
            reuse.append(dict(source=source,bytes=len(b),sha256=h,Git_path=known[(source,h)]['Git_path'],prior_index_exact=True));continue
        if (source,h) in knownlarge:
            reuse.append(dict(source=source,bytes=len(b),sha256=h,large_index_Git_path=knownlarge[(source,h)],prior_index_exact=True));continue
        if p.suffix.lower() in ('.npz','.pt','.zip','.usd','.npy','.partial') or len(b)>50_000_000 or (p.name.startswith('CURB_NATIVE_ACTUAL_') and len(b)>1_000_000):
            large.append(dict(source=source,bytes=len(b),sha256=h,index_only=True,original_retained=True,reason='Full SDK/native raw physical-state snapshot or large original; compact complete decision and original path/SHA preserved'));continue
        clean,n=redact(b.decode('utf8'));raw=clean.encode();out=dest/p.relative_to(D)
        out.parent.mkdir(parents=True,exist_ok=True);assert not out.exists();out.write_bytes(raw);assert redact(clean)[0]==clean
        gp=out.relative_to(P).as_posix();files.append(gp)
        rows.append(dict(source=source,bytes=len(b),sha256=h,Git_path=gp,archived_bytes=len(raw),archived_sha256=H(raw),redactions=n,capture='redacted_full' if n else 'byteexact_full',post_stage_supplement=True))
    assert rows
    idx=dest/'REPORT_CAPTURE_INDEX.json';idx.write_bytes(json.dumps(dict(epoch=time.time(),reports_and_implementation=rows,large_originals_index_only=large,
        prior_identical_reports_reused=reuse,all_saved_new_CURB_reports_accounted=True,stage_commit=stage['commit'],credentials_excluded=True),ensure_ascii=False,indent=2).encode());files.append(idx.relative_to(P).as_posix())
    subprocess.run(['git','-C',str(P),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b'\0'.join(x.encode() for x in files)+b'\0',capture_output=True,check=True)
    git('commit','-m','Record independent Curb actual scope receipts and current monitoring with retained reader errors')
    run=subprocess.run(['git','-C',str(P),'push','origin','HEAD'],capture_output=True,text=True,encoding='utf8',errors='replace')
    if run.returncode:
        save('CURB_SUPPLEMENT_PUSH_ERROR.json',dict(epoch=time.time(),commit=git('rev-parse','HEAD'),stdout=run.stdout,stderr=run.stderr,continue_original_objects_only=True));raise RuntimeError('Continue original supplement push without recommit')
    refs=['refs/heads/main','refs/tags/'+stage['tag'],'refs/tags/'+stage['tag']+'^{}']
    old=json.loads((R/'CURB_STAGE_ARCHIVE_STARTED.json').read_bytes())['old_tags']
    for t in old:refs+=['refs/tags/'+t,'refs/tags/'+t+'^{}']
    remote=dict(line.split('\t')[::-1] for line in git('ls-remote','origin',*refs).splitlines());head=git('rev-parse','HEAD')
    assert remote['refs/heads/main']==head and remote['refs/tags/'+stage['tag']]==stage['tagobject'] and remote['refs/tags/'+stage['tag']+'^{}']==stage['commit']
    for t,v in old.items():assert remote['refs/tags/'+t]==v['tagobject'] and remote['refs/tags/'+t+'^{}']==v['commit']
    tracked=set(git('ls-tree','-r','--name-only','HEAD').splitlines())
    for row in rows:assert row['Git_path'] in tracked and H((P/row['Git_path']).read_bytes())==row['archived_sha256']
    assert not git('status','--porcelain')
    print(json.dumps(dict(supplement_commit=head,tag=stage['tag'],tagobject=stage['tagobject'],stage_commit=stage['commit'],remote_main_tag_peeled_verified=True,
        push_pending=False,reports=len(rows),all_current_saved_CURB_reports_Git_accounted=True,six_original_tag_objects_unchanged=True)))
if __name__=='__main__':
    try:main()
    except Exception:
        if not (R/'CURB_SUPPLEMENT_ERROR.json').exists():save('CURB_SUPPLEMENT_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_repeat_executed_sync_or_committed_supplement=True))
        raise

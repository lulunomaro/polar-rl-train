"""One hourly read-only partial collection supplement; no new trial or training."""
from route_fixture_io import *
import subprocess
sys.path.insert(0,str(W/'MOD4_SCUT_WAVE50_GATE_COMPARE_20261012'))
import archive_actual_reference_stage_once as archive

def main():
    assert not (R/'CANDIDATE152_PARTIAL_20261012T0504_METADATA_SYNCED.json').exists()
    pick=lambda pattern:max(R.glob(pattern),key=lambda p:int(p.stem.rsplit('_',1)[1]))
    cp=pick('ROUTE443_CANDIDATE_COLLECTED_[0-9]*.json');rp=pick('ROUTE443_CANDIDATE_ACTUAL_REVIEW_[0-9]*.json')
    c=json.loads(cp.read_bytes());a=json.loads(rp.read_bytes())
    assert c['own']['source_count']==443 and c['own']['checkpoint']['finite_tensors']==107
    assert c['actual_worker']['attention'] is None and not a['review_complete'] and len(c['cases'])==2
    assert a['summary']['terrain'] is None and set(a['summary']['retention'])=={'flat','spin'}
    assert {p['phase'] for p in c['pending']}=={'result_not_generated'}
    stamp=str(time.time_ns());files={
      'E1_WAVE50_ROUTE443_CANDIDATE152_ACTUAL_COLLECTION_'+stamp+'.json':cp,
      'E1_WAVE50_ROUTE443_CANDIDATE152_PARTIAL_ACTUAL_REVIEW_'+stamp+'.json':rp}
    n,w=io.connect_both()
    try:
      with n.open_sftp() as f:
        for name,p in files.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
        raw=f.open(io.E+'/reports/MOE_PLAN_EXECUTION_CURRENT.json','rb').read();old=H(raw);current=json.loads(raw)
      scope=current['terrain_subexpert_revision004']['wave50_route_candidate152_actual_scope']
      assert scope['own_source_count']==443 and scope['own_checkpoint_SHA']==c['own']['checkpoint']['sha256']
      scope.update(actual_collection=io.E+'/reports/'+next(k for k in files if 'ACTUAL_COLLECTION' in k),actual_review=io.E+'/reports/'+next(k for k in files if 'PARTIAL_ACTUAL_REVIEW' in k),review_complete=False,pending=a['pending'],flat_and_spin_actual_complete_errorfree_byteSHA_reviewed=True,terrain_and_world_actual_result_pending=True,actual_3060_attention=None)
      nxt=io.E+'/reports/CANDIDATE152_PARTIAL_NEXT_CURRENT_'+stamp+'.json'
      with n.open_sftp() as f:io.put(f,nxt,json.dumps(current,ensure_ascii=False,indent=2).encode())
      synced=run(n,r'''from pathlib import Path
import json,time,hashlib,os
R=Path(E_TOKEN)/'reports';p=R/'MOE_PLAN_EXECUTION_CURRENT.json';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=Path(B_TOKEN);before=h(B)
protected={k:(R/k).read_bytes() for k in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')};assert h(p)==OLD_TOKEN
temp=p.with_name('CANDIDATE152_PARTIAL_'+str(time.time_ns())+'.tmp');temp.write_bytes(Path(NEXT_TOKEN).read_bytes());assert h(p)==OLD_TOKEN;os.replace(temp,p);assert all((R/k).read_bytes()==v for k,v in protected.items())
v=dict(epoch=time.time(),passed=True,current_SHA=h(p),master_approval_tracks_RM004_bytes_exact=True,canonical_SHA_before=before,canonical_SHA_after=h(B),canonical_not_written=True,flat_spin_partial152_actual_synced=True,healthy_pending_no_human_action=True,no_GPU_worker_queue_PPO_or_oldonce_replay=True)
q=R/('E1_WAVE50_CANDIDATE152_PARTIAL_METADATA_SYNCED_'+STAMP_TOKEN+'.json');assert not q.exists();q.write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('E_TOKEN',repr(io.E)).replace('B_TOKEN',repr(io.B)).replace('OLD_TOKEN',repr(old)).replace('NEXT_TOKEN',repr(nxt)).replace('STAMP_TOKEN',repr(stamp)))
      save('CANDIDATE152_PARTIAL_20261012T0504_METADATA_SYNCED.json',synced)
    finally:io.cleanup(n,w)
    repo=W/'polar-rl-train';archive.FOLDERS=(D,PRIOR)
    assert not archive.gitio.g('status','--porcelain') and not archive.gitio.g('diff','--cached','--name-only')
    old_tags=archive.gitio.refs();dest=repo/'history/evidence'/D.name/'candidate152_partial_20261012T0504_supplement'
    rows,files=archive.capture(dest)
    subprocess.run(['git','-C',str(repo),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+b'\0' for p in files),capture_output=True,check=True)
    archive.gitio.g('commit','-m','Supplement candidate152 flat and spin partial actual review')
    archive.gitio.g('push','origin','HEAD');head=archive.gitio.g('rev-parse','HEAD');archive.verify(rows,old_tags,head)
    current={r['source_path']:r for r in rows}
    for folder in archive.FOLDERS:
      for p in folder.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts:continue
        assert current[str(p.resolve())]['sha256']==H(p.read_bytes())
    # Final actual Git verification remains tool output, avoiding receipt recursion.
    print(json.dumps(dict(commit=head,actual_remote_main_verified=True,all_old_tags_preserved=len(old_tags),all_current_saved_sources_reports_SHA_tracked_or_actual_large_index=True,captured_sources=len(rows),no_new_trial_or_tag=True,healthy_terrain_world_pending=True)))

if __name__=='__main__':
    try:main()
    except BaseException:save('CANDIDATE152_PARTIAL_20261012T0504_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),inspect_existing_CAS_Git_objects_no_replay=True));raise

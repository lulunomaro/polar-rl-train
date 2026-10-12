"""Correct retained partial-only metadata flag; full raw and old sync evidence unchanged."""
from route_fixture_io import *
import subprocess
sys.path.insert(0,str(W/'MOD4_SCUT_WAVE50_GATE_COMPARE_20261012'))
import archive_actual_reference_stage_once as archive

def main():
    assert not (R/'COMPLETE152_LEGACY_PENDING_FIELD_ACTUAL_REVIEW.json').exists()
    n,w=io.connect_both()
    try:
      v=run(n,r'''from pathlib import Path
import json,time,hashlib,os
R=Path(E_TOKEN)/'reports';p=R/'MOE_PLAN_EXECUTION_CURRENT.json';B=Path(B_TOKEN);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();raw=p.read_bytes();old=h(p);b=h(B);a=json.loads(raw);scope=a['terrain_subexpert_revision004']['wave50_route_candidate152_actual_scope']
assert scope['review_complete'] and scope['pending']==[] and scope['forward_complete']==12 and scope['reverse_complete']==25
assert scope['terrain_and_world_actual_result_pending'] is True
proof=json.loads(Path(scope['complete_scope_decision']).read_bytes());assert proof['all_four_actual_complete_errorfree_fullraw_reviewed']
before=scope['terrain_and_world_actual_result_pending'];scope['terrain_and_world_actual_result_pending']=False;scope['all_four_actual_complete_errorfree_fullraw_reviewed']=True
protected={k:(R/k).read_bytes() for k in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
temp=p.with_name('COMPLETE152_LEGACY_FLAG_'+str(time.time_ns())+'.tmp');temp.write_bytes(json.dumps(a,ensure_ascii=False,indent=2).encode());assert h(p)==old;os.replace(temp,p);assert all((R/k).read_bytes()==x for k,x in protected.items())
v=dict(epoch=time.time(),passed=True,original_partial_boolean_retained_in_prior_Git_sync=True,original_full_review_complete_and_pending_empty_already_true=True,legacy_terrain_world_pending_before=before,legacy_terrain_world_pending_after=False,current_SHA=h(p),full_complete152_results_not_modified=True,master_approval_tracks_RM004_bytes_exact=True,canonical_SHA_before=b,canonical_SHA_after=h(B),canonical_not_written=True,no_GPU_or_oldonce_replay=True)
q=R/('E1_WAVE50_COMPLETE152_LEGACY_PENDING_FIELD_ACTUAL_REVIEW_'+str(time.time_ns())+'.json');q.write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('E_TOKEN',repr(io.E)).replace('B_TOKEN',repr(io.B)))
      save('COMPLETE152_LEGACY_PENDING_FIELD_ACTUAL_REVIEW.json',v)
    finally:io.cleanup(n,w)
    archive.FOLDERS=(D,W/'MOD4_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012');repo=W/'polar-rl-train'
    assert not archive.gitio.g('status','--porcelain') and not archive.gitio.g('diff','--cached','--name-only')
    old=archive.gitio.refs();dest=repo/'history/evidence'/D.name/'complete152_legacy_metadata_flag_reviewed_supplement'
    rows,files=archive.capture(dest)
    subprocess.run(['git','-C',str(repo),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+b'\0' for p in files),capture_output=True,check=True)
    archive.gitio.g('commit','-m','Supplement complete152 legacy partial-pending metadata correction');archive.gitio.g('push','origin','HEAD');head=archive.gitio.g('rev-parse','HEAD');archive.verify(rows,old,head)
    print(json.dumps(dict(passed=True,commit=head,actual_remote_main_verified=True,all_old_tags_preserved=len(old),complete152_legacy_pending_flag_corrected=True,all_saved_report_source_SHA_tracked_or_actual_large_index=True,no_new_trial_or_GPU=True)))

if __name__=='__main__':
    try:main()
    except BaseException:save('COMPLETE152_LEGACY_PENDING_FIELD_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),inspect_existing_CAS_Git_objects_no_replay=True));raise

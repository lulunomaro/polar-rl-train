"""Review owned PH11 captured text identities for recording; never refresh originals/assets."""
from pathlib import Path
import json,hashlib,traceback
R=Path(__file__).resolve().parent;REPO=(R.parent/'repo-lqr-robust').resolve();P=REPO/'history/experiments/mod4v1_robust_traditional_phase11_SOURCE_PREPARATION'
OUT=R/'PH11_PARENT_INDEX_REVIEW_V2.json';ERR=R/'PH11_PARENT_INDEX_REVIEW_V2_ERROR.json';seen={}
def take(p):
    p=p.resolve();assert p.is_file()and p.stat().st_size<3*1024*1024,str(p)
    assert p.suffix.lower()not in('.jsonl','.o','.axf','.lib','.zip','.exe','.bin','.usd','.usda','.usdc','.tgz','.pyc') or (p==(P/'GIT_READONLY_LEDGER.jsonl').resolve() and p.stat().st_size<65536),str(p)
    key=str(p).casefold()
    if key not in seen:
        raw=p.read_bytes();seen[key]=(raw,dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
    return seen[key]
def js(p):return json.loads(take(p)[0])
def dump(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
def main():
    assert not OUT.exists()and not ERR.exists()
    idx=js(P/'INDEX.json');receipt=js(P/'RECEIPT.json');review=js(P/'REVIEW_INDEX.json');case=js(P/'CASE_RECONCILIATION.json')
    canonical=idx['canonical_REVIEW_INDEX'];assert take(P/'REVIEW_INDEX.json')[1]['SHA']==canonical['SHA']==receipt['REVIEW_INDEX']['SHA']=='39e3bf35260ed3d438e67e4bdb0d589e4a6b6111efa0203bce942ee9766883b5'
    assert take(P/'INDEX.json')[1]['SHA']==receipt['INDEX']['SHA']=='295e6b1dc98fee7d801066d5612bc343268f4a727841908131a70b9e89630ad3'
    assert review['branch']=='mod4v1-lqr-mpc-robust'and review['parent']==receipt['current_parent']=='e176d2a6401fafb9d618a042acba8190023c3273'
    assert review['all_snapshot_bytes_match_captured_source_before']is True and review['no_false_fresh_source_after_assertion']is True
    assert review['original_live_source_after_payload_checks']=='NOT_REACHED_then_NOT_REOPENED_under_savedonly_grant'and receipt['original_source_after_fullhash_NOT_REACHED_AND_NOT_REOPENED']is True
    assert review['all_activeV6_V7_C18_excluded']is True and review['source_capture_schema_error_and_saved_close_preserved']is True
    assert review['Git_mutations']==review['original_helper_execution']==review['ARM_model_PHY_oldQA_Goal_agents']==review['raw_lib_obj_AXF_ZIP_USD_archive_payload_opens_and_hashes']==0
    files=review['files'];assert len(files)==853 and review['summary']==idx['summary']
    rels=[];snap=[]
    for rec in files:
        p=Path(rec['path']).resolve();assert p.is_relative_to(P.resolve())and (REPO/rec['relative']).resolve()==p
        assert '.git'not in p.parts and not any(x in p.parts for x in('STARTUP_STAND_V6','STARTUP_STAND_V7','MOD4_DEPLOYMENT_C3_SHADOW_SEAM_V18'))
        actual=take(p)[1];assert actual['SHA']==rec['SHA']and actual['bytes']==rec['bytes'],rec['relative']
        rels.append(rec['relative'])
        if p.is_relative_to((P/'snapshot').resolve()):snap.append(actual)
    assert len(set(rels))==853 and len(snap)==798 and sum(x['bytes']for x in snap)==17739938
    assert review['summary']['exact_prior_Git_refs']==240 and review['summary']['raw_metadata_paths']==582 and review['summary']['version_gap_claims']==0
    numeric=js(R/'PH11_PARENT_SNAPSHOT_NUMERIC_REVIEW_V1.json');expected=js(R/'PH11_PARENT_CLOSED_EXPECTED_FACTS_V1.json')
    assert numeric['status']=='PASS_PARENT_SIX_COPIED_SMALL_JSONS_IDENTITY_AND_NUMBERS_NOT_WHOLE_SOURCE_SEAL'
    assert case['controls']==numeric['new_controls']==expected['new_cutoff_controls']==381 and case['physics_steps']==numeric['new_physics_steps']==7620
    assert case['formal_false']==2 and case['full_10s_completions']==case['original_gate_true']==0 and len(case['cases'])==2
    assert case['cumulative_context']['actual_controls']==2482 and case['cumulative_context']['actual_physics_steps']==49640 and case['oldV1_ERROR_noresult_notbackfilled']is True
    assert case['target']['actual_link_calls']==1 and case['target']['actual_link_returncode']==0 and case['target']['image_bytes']==629048 and case['target']['C3_hardware_runtime_qualified']is False
    for exp,got in zip(expected['cases'],case['cases']):
        assert exp['case_id']==got['case_id']and exp['controls']==got['controls']and exp['physics_steps']==got['physics_steps']and got['original_gate']is got['complete']is False
    for name in('INDEX.json','REVIEW_INDEX.json','RECEIPT.json'):
        rel=(P/name).relative_to(REPO).as_posix();assert rel not in rels;rels.append(rel)
    assert len(rels)==856
    result=dict(status='PASS_PARENT_CAPTURED_TEXT_INDEX_IDENTITIES_AND_FINITE_ALLOWLIST_NOT_FRESH_LIVE_SOURCE',branch=review['branch'],parent=review['parent'],canonical_index_SHA=take(P/'INDEX.json')[1]['SHA'],review_index_SHA=take(P/'REVIEW_INDEX.json')[1]['SHA'],receipt_SHA=take(P/'RECEIPT.json')[1]['SHA'],indexed_owned_files_verified=853,captured_snapshot_texts=798,captured_snapshot_bytes=17739938,prior_refs_declared=240,raw_metadata_paths_declared=582,new_version_gaps_declared=0,original_full_live_source_after='UNKNOWN_NOT_REACHED_NOT_REFRESHED',source_snapshot_not_rewritten=True,cases=2,controls=381,physics_steps=7620,formalFalse=2,complete10s=0,old_gate_true=0,old_BSP_link_calls=1,old_BSP_link_rc=0,not_new_MOD4_or_hardware_qualification=True,allowed_sourceprep_relative_paths=rels,saved_text_files_hashed_this_review=len(seen),original_sources_raw_lib_obj_image_model_payload_reads=0,controller_import_FK_PHY_oldQA_ARM_Git_calls=0,active_V6_V7_C18_excluded=True,record_helper_staging_commit_push_still_require_separate_parent_authorization=True)
    dump(OUT,result);print(json.dumps({k:result[k]for k in('status','indexed_owned_files_verified','captured_snapshot_texts','captured_snapshot_bytes','controls','physics_steps','old_gate_true','original_full_live_source_after')},indent=2))
if __name__=='__main__':
    try:main()
    except BaseException:
        if not ERR.exists():dump(ERR,dict(status='FIRST_PARENT_INDEX_REVIEW_ERROR_STOP',error=traceback.format_exc(),owned_text_files_read=len(seen),original_asset_PHY_Git_calls=0))
        raise

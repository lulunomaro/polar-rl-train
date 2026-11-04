"""Seal new PH11 owned metadata/snapshot INDEX only. No originalsource/raw/helper/Git execution."""
from pathlib import Path
import hashlib,json,sys,traceback
D=Path(__file__).resolve().parent;W=D.parents[2]
G=Path(r'C:\Users\lulu\AppData\Local\Temp\dsh-spill-N99Hsy\session-de481967f16c\4b44b1905f9c-glob-results.txt')
def rec(p):
 b=p.read_bytes();return dict(path=str(p),relative=p.relative_to(W).as_posix(),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_bytes())
def save(n,x):
 with(D/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def main():
 assert not(D/'REVIEW_INDEX.json').exists()and not(D/'RECEIPT.json').exists()
 m=load(D/'CAPTURE_MINIMUM.json');reg=load(D/'CASE_AND_TARGET_REGISTRY.json');cov=load(D/'OPERATION_COVER_TWO_CASE_AND_SAVED_CLOSURE.json');src=load(D/'SOURCE_MANIFEST.json')
 assert m['source_snapshot_files']==798 and m['source_snapshot_bytes']==17739938 and m['historical_version_gap_claims']==0 and m['current_parent']=='e176d2a6401fafb9d618a042acba8190023c3273'
 expected=Path(cov['ParentExpected']['path']);b=expected.read_bytes();assert hashlib.sha256(b).hexdigest()==cov['ParentExpected']['SHA']and len(b)==cov['ParentExpected']['bytes']
 # Explicit operation-cover evidence authorized by parent; not a new runtime/snapshot source or activeV6 case collection.
 with(D/'OPERATION_PARENT_EXPECTED_EVIDENCE.json').open('xb')as f:f.write(b)
 reconciliation=dict(status='SAVED_CASE_NUMERICS_MATCH_PARENT_INDEPENDENT_SIX_JSONS_NO_NEW_PHYSICS',cases=[{k:x[k]for k in ['case_id','controls','physics_steps','complete','original_gate','formal_result_present','software_failure','first_BALANCE_command_s','stop','fault','end_stable_s']}for x in reg['new_physical_cases']],new_case_count=2,controls=381,physics_steps=7620,formal_false=2,full_10s_completions=0,original_gate_true=0,cumulative_context=reg['cumulative_context'],oldV1_ERROR_noresult_notbackfilled=True,passive3_steps12000_notcontrolled=True,parent_expected=rec(D/'OPERATION_PARENT_EXPECTED_EVIDENCE.json'),original_snapshots_not_rewritten=True,raw_or_model_or_QA_calls=0,target=dict(unique_C162_segmented=[1,39,122],actual_link_calls=1,actual_link_returncode=0,image_bytes=629048,image_producer_SHA=reg['target']['first_actual_link']['image']['SHA'],current165_input_identities_metadata_only=True,C3_hardware_runtime_qualified=False),C17_delivery_then_closing_failure_cause='UNKNOWN_NO_REPLAY')
 assert sum(x['controls']for x in reconciliation['cases'])==381 and sum(x['physics_steps']for x in reconciliation['cases'])==7620
 save('CASE_RECONCILIATION.json',reconciliation)
 paths=[Path(x)for x in G.read_text(encoding='utf-8').splitlines()if x];assert len(paths)==len(set(paths))==849
 extras=[Path(__file__).resolve(),D/'CASE_RECONCILIATION.json',D/'OPERATION_PARENT_EXPECTED_EVIDENCE.json',D/'INDEX_BINDING_INPUT.json']
 save('INDEX_BINDING_INPUT.json',dict(kind='HOST_GLOB_OWN_PREPARATION_TREE_PLUS_KNOWN_NEW_METADATA_NO_SOURCE_DISCOVERY',hostglob=dict(path=str(G),bytes=G.stat().st_size,SHA=hashlib.sha256(G.read_bytes()).hexdigest(),paths=849),known_new_metadata=[str(x)for x in extras],excluded_from_index_self_and_final_covers=['REVIEW_INDEX.json','INDEX.json','RECEIPT.json','seal_index_01.log'],source_refresh_or_capture=0))
 paths=sorted(set(paths+extras),key=lambda p:p.as_posix().casefold());files=[]
 snapshot_pins={x['snapshot_path']:x for x in load(D/'SOURCE_SNAPSHOT_IDENTITY_PINS.json')['snapshot_records']};snapshot_count=0
 for p in paths:
  assert p.resolve().is_relative_to(D.resolve())and p.is_file()and p.suffix.lower()not in('.o','.obj','.elf','.elfbin','.axf','.lib','.zip','.usd','.usda','.usdc','.bin','.exe')
  r=rec(p)
  if p.is_relative_to(D/'snapshot'):
   snapshot_count+=1;e=snapshot_pins[r['relative']];assert r['SHA']==e['SHA']and r['bytes']==e['bytes'];r['role']='immutable_captured_text_snapshot'
  else:r['role']='owned_sourceprep_metadata_code_or_error_evidence'
  files.append(r)
 assert snapshot_count==798 and len(files)==853
 index=dict(status='PH11_LOCAL_SOURCE_ONLY_SAVED_PREFIX_SEALED_READY_FOR_PARENT_REVIEW_NO_RECORD_COMMIT_TAG_PUSH',branch='mod4v1-lqr-mpc-robust',parent=m['current_parent'],scope_FINAL_snapshot_SHA=src['scope_snapshot']['source_SHA'],files=files,summary=dict(indexed_owned_files=len(files),snapshot_text_files=798,snapshot_text_bytes=17739938,exact_prior_Git_refs=m['prior_Git_refs'],raw_metadata_paths=m['raw_metadata_paths'],version_gap_claims=0,new_cases=2,controls=381,physics_steps=7620,formal_false=2,complete_10s=0),all_snapshot_bytes_match_captured_source_before=True,original_live_source_after_payload_checks='NOT_REACHED_then_NOT_REOPENED_under_savedonly_grant',no_false_fresh_source_after_assertion=True,all_activeV6_V7_C18_excluded=True,oldPH10_unknowns_and_encoding_independent=True,source_capture_schema_error_and_saved_close_preserved=True,raw_lib_obj_AXF_ZIP_USD_archive_payload_opens_and_hashes=0,Git_mutations=0,original_helper_execution=0,ARM_model_PHY_oldQA_Goal_agents=0,no_record_or_physics_authority=True)
 save('REVIEW_INDEX.json',index)
 indexrec=rec(D/'REVIEW_INDEX.json')
 save('INDEX.json',dict(status=index['status'],canonical_REVIEW_INDEX=indexrec,summary=index['summary'],self_reference_and_final_cover_not_in_recursive_index=True,ready_for_record=False))
 receipt=dict(status='SEALED_PH11_SOURCE_ONLY_INDEX_AND_SNAPSHOT_FOR_PARENT_REVIEW_NOT_RECORD_OR_GOAL_COMPLETION',INDEX=rec(D/'INDEX.json'),REVIEW_INDEX=indexrec,REVIEW_HANDOFF=rec(D/'REVIEW_HANDOFF.md'),CASE_RECONCILIATION=rec(D/'CASE_RECONCILIATION.json'),source_scope_roots14=True,root_explicit_files23=True,all967_declared_paths_found=True,source_snapshot_files798=798,source_snapshot_bytes17739938=17739938,owned_index_files=853,exact_prior_Git_refs=240,raw_metadata_paths=582,new_unresolved_version_claims=0,saved_snapshot_byte_identities_verified=True,original_source_after_fullhash_NOT_REACHED_AND_NOT_REOPENED=True,cases2_controls381_steps7620_originalgateFalse=True,cumulative6_controls2482_steps49640_ERRORnoresult_preserved=True,current_165_link_identites_not_oldPH10_unknown_rewrite=True,original_error_schema='capture line150 proposed_gate.passed wrong; requiredactualstartup_stand_original_v1_gate exactFalse; originalerrorbytespreserved, no capture rerun',source_capture_calls=1,saved_closure_calls=1,current_parent=m['current_parent'],original_helper_b2fd15_readonly_not_executed=True,Git_mutations=0,ARM_model_PHY_QA_Goal_agents_raw_lib_image_payload_opens_hashes=0,Git_index_mutation_or_commit_stage_reset_checkout_tag_push_calls=0,allactiveV6_V7_C18_and_future_excluded=True,C17_closing_failure_unknown_no_map_replay=True,ready_for_record=False,parent_independent_snapshot_review_and_separate_approval_needed=True)
 save('RECEIPT.json',receipt)
 print(json.dumps(dict(status=receipt['status'],INDEX=rec(D/'INDEX.json'),REVIEW_INDEX=indexrec,REVIEW_HANDOFF=rec(D/'REVIEW_HANDOFF.md'),CASE_RECONCILIATION=rec(D/'CASE_RECONCILIATION.json'),RECEIPT=rec(D/'RECEIPT.json'),owned_index_files=853,snapshot_files=798,snapshot_bytes=17739938,prior_refs=240,raw_metadata=582,new_version_gaps=0,new_cases=2,controls=381,physics_steps=7620,raw_or_Git_mutation_or_PHY=0),ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=D/'INDEX_FIRST_STOP.json'
  if not p.exists():save('INDEX_FIRST_STOP.json',dict(status='STOPPED_FIRST_INDEX_METADATA_FAILURE_NO_REFRESH',error=traceback.format_exc(),source_raw_refresh=0,Gitmutation=0))
  raise

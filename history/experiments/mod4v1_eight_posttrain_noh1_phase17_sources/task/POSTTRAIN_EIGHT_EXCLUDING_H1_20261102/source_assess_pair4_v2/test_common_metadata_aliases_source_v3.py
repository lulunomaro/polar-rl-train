from pathlib import Path
import importlib.util,json,copy
B=Path(__file__).resolve().parent;out=B/'COMMON_METADATA_ALIAS_SYNTHETIC_PROOF_V3.json';assert not out.exists();spec=importlib.util.spec_from_file_location('pair4meta_v2',B/'assess_pair4_retention_closed_metadata_v2.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);rows=[];actual=[]
for i,role in enumerate(m.ROLES):
 mother={'path':'/SYNTHETIC_SOURCE_ONLY/mother_'+role+'.pt','SHA':'a'*64};candidate={'checkpoint':'/SYNTHETIC_SOURCE_ONLY/candidate_'+role+'.pt','SHA':'b'*64,'bytes':17620000,'actual_saved_iteration':32662};selection='FROZEN_MOTHER'if i==0 else'CANDIDATE';rows.append(dict(role=role,selection=selection,new_candidate_artifact=candidate,frozen_mother=mother,selected_artifact=mother if i==0 else candidate,actual_actor_identity={'SHA':candidate['SHA']},actual_execution_complete=True,original_scope={'num_envs':80,'seconds':32. if i==0 else 20.,'controls':1600 if i==0 else 1000},do_not_overwrite_frozen_mother=True,do_not_delete_new_candidate_or_rollback_evidence=True));actual.append(dict(role=role,returncode=0,actual_waited=True,data={'source_cache':{'wholecachedidentity_passed':True,'entire_original_root_and_nested_identity_preserved':True},'optimizer_updates':0}))
result={'rows':rows,'actual_common_control_overlap_seconds':2.};closed={'final':{'rows':actual}};before=copy.deepcopy(result);new=m.common_best_metadata_aliases(result,closed);assert result==before and new['actual_control_windows_overlap_seconds']==2. and all(r['actual_eval_RC']==0 and r['do_not_overwrite_mother_or_failed_candidate']for r in new['rows']);assert new['rows'][0]['selected_source']==rows[0]['frozen_mother']and new['rows'][1]['selected_source']['path']==rows[1]['new_candidate_artifact']['checkpoint'];n=3
for mutate in('wrong_choice','bad_rc','missing_pointer'):
 r=copy.deepcopy(result);c=copy.deepcopy(closed)
 if mutate=='wrong_choice':r['rows'][0]['selected_artifact']=dict(r['rows'][0]['selected_artifact'],SHA='c'*64)
 elif mutate=='bad_rc':c['final']['rows'][0]['returncode']=1
 else:del r['rows'][0]['new_candidate_artifact']['checkpoint']
 try:m.common_best_metadata_aliases(r,c)
 except m.EvidenceError:n+=1
 else:raise AssertionError('Badsyntheticmetadataaccepted '+mutate)
v={'kind':'SOURCE_ONLY_COMMON_ENVELOPE_SYNTHETIC_TEST_NOT_ACTUAL_PAIR4_ASSESSMENT','checks':n,'all_passed':True,'original_assessment_or_selection_changed':False,'actual_result_or_best_file_published':False,'PTOpen_raw_SDK_SSH_C_GO_Git_operations':0};out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v,indent=2))

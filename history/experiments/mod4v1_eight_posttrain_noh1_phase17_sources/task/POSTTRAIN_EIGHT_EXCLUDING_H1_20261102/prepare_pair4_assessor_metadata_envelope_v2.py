"""PureSOURCEmetadatareader compatibility fix beforeactualprocessor, notskillpatch.
Keepsealedv1. Originaltaskfilenameiscase/task.json; commonbest aliasesderive
fromactualvalidatedclosedrows, selectionlogicmethodsremainASTidentical.
"""
from pathlib import Path
import ast,hashlib,json,importlib.util,sys
D=Path(__file__).resolve().parent;old=D/'source_assess_pair4_v1/assess_pair4_retention_closed_metadata_v1.py';raw=old.read_bytes();assert hashlib.sha256(raw).hexdigest()=='2601ddab89f18583ba1b07bbc51bbd8a607b6d9d2d71432d6a28684ad83e89d1';s=raw.decode('utf-8');assert"for leaf in('TASK.json','FINAL.json','SDK_FULL_STDOUT_STDERR.log'):"in s;s=s.replace("for leaf in('TASK.json','FINAL.json','SDK_FULL_STDOUT_STDERR.log'):","for leaf in('task.json','FINAL.json','SDK_FULL_STDOUT_STDERR.log'):").replace("if leaf=='TASK.json':tasks[role]", "if leaf=='task.json':tasks[role]")
func='''def common_best_metadata_aliases(result,closed):
    """Stableoutputenvelopeonly; sourcefacts/selection/oldoriginalfieldskept."""
    rows=[];actual=rows_by_role(closed['final']['rows'],ROLES,'validated actual evaluator')
    def candidate_pointer(item):
        path=item.get('path',item.get('checkpoint'))
        need(isinstance(path,str)and path and len(item['SHA'])==64 and type(item['bytes'])is int,'Actual candidate pointer')
        return dict(path=path,SHA=item['SHA'],bytes=item['bytes'])
    for original in result['rows']:
        r=dict(original);role=r['role'];source=actual[role];cache=source['data']['source_cache'];candidate=candidate_pointer(r['new_candidate_artifact']);mother=dict(r['frozen_mother']);selected=candidate if r['selection']=='CANDIDATE'else mother
        chosen=r['selected_artifact'];need(chosen['SHA']==selected['SHA']and chosen.get('path',chosen.get('checkpoint'))==selected['path'],'Selection alias must preserve original exact choice')
        identity=cache['wholecachedidentity_passed']if role=='W35'else cache['entire_original_root_and_nested_identity_preserved']
        need(source['returncode']==0 and source['actual_waited']is True and r['actual_execution_complete']is True,'Actual RC evidence for alias')
        r.update(actual_eval_RC=source['returncode'],actual_scope_seconds=r['original_scope']['seconds'],actual_controls=r['original_scope']['controls'],source_candidate_SHA=r['actual_actor_identity']['SHA'],new_PPO_updates_in_eval=source['data']['optimizer_updates'],selected_source=selected,candidate_preserved=candidate,frozen_mother_preserved=mother,do_not_overwrite_mother_or_failed_candidate=r['do_not_overwrite_frozen_mother']and r['do_not_delete_new_candidate_or_rollback_evidence'],whole_source_cache_identity_preserved=identity,selection_is_single_fresh80_screen_not_full20k_or_hardware_graduation=True,unpaired_trajectory_after_policy_dependent_resets_not_causal_claim=True,common_metadata_aliases_do_not_change_original_choice=True)
        rows.append(r)
    out=dict(result);out.update(rows=rows,actual_control_windows_overlap_seconds=result['actual_common_control_overlap_seconds'],common_metadata_envelope_added_without_reassessment=True);return out


'''
anchor='def evaluate_closed_files(pointer_path,baseline_path,training_path,contracts_path,reference_path):';assert s.count(anchor)==1;s=s.replace(anchor,func+anchor);anchor='    result=assess_pair4(closed,baseline,training,contracts,tasks,errors,reference)';assert s.count(anchor)==1;s=s.replace(anchor,anchor+'\n    result=common_best_metadata_aliases(result,closed)');t1=ast.parse(raw.decode());t2=ast.parse(s)
for name in('assess_pair4','compare_w35','compare_s50','split_counts','scan_closed_stdout'):
 n1=next(n for n in t1.body if isinstance(n,ast.FunctionDef)and n.name==name);n2=next(n for n in t2.body if isinstance(n,ast.FunctionDef)and n.name==name);assert ast.dump(n1,include_attributes=False)==ast.dump(n2,include_attributes=False),name
B=D/'source_assess_pair4_v2';assert not B.exists();B.mkdir();p=B/'assess_pair4_retention_closed_metadata_v2.py';p.write_text(s,encoding='utf-8',newline='\n');proof=dict(kind='SOURCE_ONLY_METADATA_TASK_CASE_AND_COMMON_ENVELOPE_COMPATIBILITY_NOT_SKILL_OR_RUNTIME_CHANGE',sealed_v1=dict(path=str(old),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()),new_v2=dict(path=str(p),bytes=len(s.encode()),SHA=hashlib.sha256(s.encode()).hexdigest()),erratum='V1readerexpectedTASK.jsonbutactualoriginalsupervisorwriteslowercasetask.json; V1exposedselected_artifact/new_candidate_artifactinsteadsharedpublisherselected_source/candidate_preserved. Fixedmetadataaliasesonly, not selection.',unchanged_selection_methods_AST=['assess_pair4','compare_w35','compare_s50','split_counts','scan_closed_stdout'],new_aliases_must_derive_from_actual_closed_RC0_cache_and_original_selection=True,actual_pending_assessment_run_or_fake_best=False,model_raw_SDK_SSH_C_GO_or_Git_operations=0);(B/'SOURCE_COMPATIBILITY_PROOF_V2.json').write_text(json.dumps(proof,indent=2),encoding='utf-8');print(p);print(json.dumps(proof,indent=2))

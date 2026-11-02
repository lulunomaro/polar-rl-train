"""MetadataONLY E2historical18s gap vssaved24s numericcycle predicate.
OldV3/MDV2/refs/seals/plans/descriptors/MOCK remain byteexact. No model/SDK/MOCK.
"""
from pathlib import Path
import copy,hashlib,json,time,traceback
B=Path(__file__).resolve().parent;T=B.parent

def H(raw):return hashlib.sha256(raw).hexdigest()
def metadata(p):
 raw=p.read_bytes();return dict(path=str(p),bytes=len(raw),SHA=H(raw))
def newjson(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 return metadata(p)

def main():
 oldpaths=[B/'ORIGINAL_ACCEPTANCE_CONTRACT_MATRIX_FINAL_V3.json',B/'ACCEPTANCE_CONTRACT_MATRIX_SOURCE_ONLY_FINAL_V2.md',B/'NEWPLANT_SOURCE_ONLY_REPLAY_PLANS_FINAL_V2.json',B/'emitted_future_descriptors_final_v2/E2_FUTURE_SOURCE_ONLY_REPLAY_TASK.json',B/'FINAL_SOURCE_ONLY_ACCEPTANCE_INDEX_V1.json',T/'ORIGINAL_SKILL_ACCEPTANCE_CONTRACT_SOURCE_ONLY_HANDOFF_V1.json',T/'ORIGINAL_SKILL_ACCEPTANCE_SOURCE_ONLY_ALL_ERRORS_ARCHIVE_PENDING_V1.json',B/'ACCEPTANCE_PREDICATE_SEMANTIC_MOCK_PROOF_V1.json',B/'acceptance_predicates_sourceonly_v1.py']
 before=[metadata(p) for p in oldpaths];v3=json.loads(oldpaths[0].read_bytes());v4=copy.deepcopy(v3);oldrow=next(x for x in v3['rows'] if x['lineage']=='E2');row=next(x for x in v4['rows'] if x['lineage']=='E2');quote=oldrow['saved_evidence_gaps'][0]
 assert quote=='No original numeric skill pass tolerances or per-command success rule is present in the saved texts; do not invent a globalMAE pass threshold.'
 original18=v3['references']['E2_SAVED18S'];assert quote==original18['original_values']['/pending'][0]
 current='CURRENT_SCOPE: The later24s E2_CYCLES.emit numeric per-cycle predicate IS SAVED (along0.5+/-0.05m/s, cross+/-0.05m/s, yawerror+/-0.2rad/s; complete andnotterm/notimeout). The remaininggap is an overallskillgraduation/population/cohort acceptance rule; no posthocaggregate passrate.'
 historical=dict(kind='HISTORICAL_QUOTE_RETAINED_ONLY_FOR_E2_SAVED18S',quote=quote,reference_id='E2_SAVED18S',reference_path=original18['path'],reference_SHA=original18['SHA'],JSON_pointer='/pending/0',not_a_current24s_numeric_predicate_gap=True)
 clarification=dict(kind='E2_18S_HISTORICAL_QUOTE_VS24S_SAVED_PERCYCLE_PREDICATE',historical=historical,current_numeric_predicate_reference='E2_CYCLES',source_function='E2Cycles213.emit',source_path=v3['references']['E2_CYCLES']['path'],source_SHA=v3['references']['E2_CYCLES']['SHA'],original_numeric_predicate=copy.deepcopy(oldrow['original_metric_predicate']),remaining_current_gap='Overallskillgraduation/population/cohort acceptance rule, not per-cycle numericpredicate.',no_posthoc_aggregate_passrate=True,original_predicate_unchanged=True,original_MOCK29_not_rerun=True,no_model_or_SDK_calls=True)
 row['saved_evidence_gaps'][0]=current;row['historical_saved_evidence_gap_quotes']=[historical];row['scope_clarification']=clarification
 v4['schema']='mod4.original_acceptance_contract_SOURCEONLY.v4';v4['E2_metadata_scope_erratum']=dict(old_matrix_SHA=before[0]['SHA'],change='Onlyscope qualifier/currentgaplabel+historicalquote retention; no metric/predicate/numeric/runtime/source/reference edits')
 assert v4['references']==v3['references'] and v4['original_function_excerpts']==v3['original_function_excerpts']
 assert row['original_metric_predicate']==oldrow['original_metric_predicate']
 assert [r for r in v4['rows'] if r['lineage']!='E2']==[r for r in v3['rows'] if r['lineage']!='E2']
 outputs=[];outputs.append(newjson(B/'ORIGINAL_ACCEPTANCE_CONTRACT_MATRIX_FINAL_V4.json',v4))
 plan2=json.loads(oldpaths[2].read_bytes());plan3=copy.deepcopy(plan2);e2=next(p for p in plan3['plans'] if p['lineage']=='E2');assert e2['exact_saved_evidence_gaps'][0]==quote;e2['exact_saved_evidence_gaps'][0]=current;e2['historical_saved_evidence_gap_quotes']=[historical];e2['metadata_scope_clarification']=clarification
 assert [p for p in plan3['plans'] if p['lineage']!='E2']==[p for p in plan2['plans'] if p['lineage']!='E2']
 outputs.append(newjson(B/'NEWPLANT_SOURCE_ONLY_REPLAY_PLANS_FINAL_V3.json',plan3))
 descriptor=json.loads(oldpaths[3].read_bytes());newdescriptor=copy.deepcopy(descriptor);assert newdescriptor['exact_saved_evidence_gaps'][0]==quote;newdescriptor['exact_saved_evidence_gaps'][0]=current;newdescriptor['historical_saved_evidence_gap_quotes']=[historical];newdescriptor['metadata_scope_clarification']=clarification;newdescriptor['revision_status']='NEW_UNUSED_METADATA_ONLY_NO_RUNTIME_OR_DESCRIPTOR_EXECUTION'
 dest=B/'emitted_future_descriptors_metadata_only_v3';dest.mkdir(exist_ok=False);outputs.append(newjson(dest/'E2_FUTURE_SOURCE_ONLY_REPLAY_TASK.json',newdescriptor))
 md=oldpaths[1].read_text(encoding='utf-8');needle='|E2|Original18s sampledprofiles measured; ownfull24s signed4 observed originalmanyfalse, NOT fullskillaccepted|native24/192/48集成PASS；非长技能|'+quote+'|';replacement='|E2|Original18s sampledprofiles measured; ownfull24s signed4 observed originalmanyfalse, NOT fullskillaccepted|native24/192/48集成PASS；非长技能|24s signed4逐cycle数值predicate已保存；当前缺overall graduation/cohort rule，不设事后总体通过率。|';assert md.count(needle)==1;md=md.replace(needle,replacement,1)
 md+='\n## E2范围澄清（仅metadata追加）\n旧18s原gap逐字保留为historical quote：`'+quote+'`。它仅描述 **E2_SAVED18S**，不再泛指本次已经join的24s worldpredicate。\n\n后续24s **E2_CYCLES.emit** 已保存沿向0.5±0.05m/s、横向±0.05m/s、yaw误差±0.2rad/s，且complete、notterm、nottimeout的逐cycle判据；当前缺项是overall毕业/cohort接受规则，不增事后聚合通过率。原predicate函数、29项已执行MOCK及所有原seal均未改未重跑。\n\n[当前V4机器矩阵](<'+(B/'ORIGINAL_ACCEPTANCE_CONTRACT_MATRIX_FINAL_V4.json').as_posix()+'>) · [当前V3计划metadata](<'+(B/'NEWPLANT_SOURCE_ONLY_REPLAY_PLANS_FINAL_V3.json').as_posix()+'>)\n'
 md=md.replace('最终机器矩阵使用FINAL_V3、依赖表FINAL_V2','前版机器矩阵为FINAL_V3、依赖表仍FINAL_V2；本次scope澄清使用FINAL_V4',1).replace('[最终机器矩阵](<','[旧V3机器矩阵（保留）](<',1)
 mdpath=B/'ACCEPTANCE_CONTRACT_MATRIX_SOURCE_ONLY_FINAL_V3.md'
 with mdpath.open('x',encoding='utf-8') as f:f.write(md)
 outputs.append(metadata(mdpath));outputs.append(newjson(B/'E2_HISTORICAL18S_CURRENT24S_SCOPE_ERRATUM_V1.json',clarification))
 after=[metadata(p) for p in oldpaths];assert before==after
 delta=dict(kind='SOURCE_ONLY_E2_SCOPE_LABEL_CLARIFICATION_DELTA_NOT_RUNTIME',old_seals_and_outputs_preserved=before,new_unused_metadata_outputs=outputs,producer_source=metadata(Path(__file__)),changed_semantic_paths=['/rows/E2/saved_evidence_gaps/0 scopequalifier only','/rows/E2/historical_saved_evidence_gap_quotes append','/plans/E2/exact_saved_evidence_gaps/0 scopequalifier only','/E2futuredescriptor/exact_saved_evidence_gaps/0 scopequalifier only','MD E2tablegap scopequalifier'],unchanged=['all originalrefs/JSONquotevalues','allnumericpredicate/functions','other8lineages','49sourcefunctions/48refs/46dependencyrows','all priorseals','29semanticMOCKproof andpuremodulebytes'],prior_MOCK29_reexecutions=0,model_stat_read_hash_decode=0,SSH_SDK_GPU_GO_canonical_PPO_calls=0,W35_live_excluded=True,parent_phase9_delta_Gitpending=True,child_commit_push=False)
 index=T/'ORIGINAL_SKILL_ACCEPTANCE_E2_SCOPE_CLARIFICATION_DELTA_INDEX_V1.json';newjson(index,delta)
 print(json.dumps(dict(delta_index=str(index),SHA=H(index.read_bytes()),new_metadata_files=len(outputs),old_artifacts_byte_unchanged=True,predicate_unchanged=True,MOCK_reexecutions=0,SDK_model_calls=0),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('E2_SCOPE_ERRATUM_ORIGINAL_READER_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),model_SDK_MOCK_operations=0),f,indent=2)
  raise

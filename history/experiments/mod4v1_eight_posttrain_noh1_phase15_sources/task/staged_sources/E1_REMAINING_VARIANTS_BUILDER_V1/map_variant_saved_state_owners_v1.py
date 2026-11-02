"""Local savedmetadata/source AST rootkey->save/load/audit ownership, no PT."""
from pathlib import Path
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent;T=B.parent.parent;W=Path(r'C:\Users\lulu\Desktop\claude\mjcf');R=W/'MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016/reports';I=W/'MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016/reports';RT='runtime/isaac/mod4/'

def H(raw):return hashlib.sha256(raw).hexdigest()
def main():
 protectedCPU=R/'FINAL878_THREE_COMPLETE_MODELS_LOCAL_CPU_AND_ACTUAL_CLOSURE_VERIFIED.json';tensorCPU=R/'FINAL878_LITERAL_TENSOR_BYTES_AND_OPTIMIZER_TREE_THREE_RANK_CPU_SUPPLEMENT.json';finalCPU=I/'FIRST_CURB_SLOPE_FINAL_MODELS_AND_EXACT_DISTINCT_INTERVAL_COST_CPU_ACTUAL.json';firstCPU=I/'THREE_DISTINCT_EXPERT_FIRST_FULL_MODELS_ACTUAL_LOCAL_CPU_VERIFIED.json';reports=[]
 for p in [protectedCPU,tensorCPU,finalCPU,firstCPU]:
  raw=p.read_bytes();reports.append(dict(path=str(p),bytes=len(raw),SHA=H(raw),kind='SAVED_JSON_ONLY_NOT_NEW_CPU_DECODE'))
 pp=json.loads(protectedCPU.read_bytes());tp=json.loads(tensorCPU.read_bytes());fp=json.loads(finalCPU.read_bytes());ip=json.loads(firstCPU.read_bytes());results=[]
 for name in ['CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE_INDEPENDENT50']:
  root=T/'staged_sources'/('E1_'+name+'_40050_MOD4V1_SOURCE_V2');meta=json.loads((root/'VARIANT_SOURCE_METADATA.json').read_bytes());join=json.loads((root/'EXACT_EXECUTED_SOURCE_PACKAGE_JOIN_V1.json').read_bytes());inputs={r['relative']:r for r in join['inputs']};canonical=T/'staged_sources'/('E1_'+join['baseline_canonical']+'_40050_MOD4V1_SOURCE_V1');cp=json.loads((canonical/'E1_FULLSTATE_REVERSE_CACHE_ADAPTER_AST_PROOF_V1.json').read_bytes());proofs={r['relative']:r for r in cp['checks']};ownerrows=[];helperproof=[]
  helpers=['sensor_a0_runtime.py','sensor_resume_contract.py','feedback_delay_checkpoint.py','action_delay_checkpoint.py','spring_pressure_checkpoint.py','gas_damping_checkpoint.py','chassis_pd_checkpoint.py',meta['original_helper']+'.py']
  savedroot={'actor_state_dict':dict(owner='OriginalRSL5runner.save/load',load_audit='sensor_resume_contract.resume_sensor_new_episode asserts allkeys/tensors'), 'critic_state_dict':dict(owner='OriginalRSL5runner.save/load',load_audit='sensor_resume_contract.resume_sensor_new_episode asserts allkeys/tensors'),'optimizer_state_dict':dict(owner='OriginalRSL5runner.save/load',load_audit='sensor_resume_contract asserts 17state tensor+nonTensor/paramgroup exact'),'iter':dict(owner='OriginalRSL5runner.save/load',load_audit='sensor_resume_contract actualiteration equality'),'infos':dict(owner='OriginalRSL5runner.save/load',load_audit='Completefuturecache preserve, no physicalowner')} 
  for fn in helpers:
   rel=RT+fn;orig=(root/'original_exact'/rel).read_bytes();derived=(root/rel).read_bytes();tree=ast.parse(orig);s=orig.decode('utf-8-sig');saves={};loads={}
   for node in ast.walk(tree):
    if isinstance(node,ast.Subscript) and isinstance(node.value,ast.Name) and node.value.id=='ck' and isinstance(node.slice,ast.Constant) and isinstance(node.slice.value,str):
     target=saves if isinstance(node.ctx,ast.Store) else loads;target.setdefault(node.slice.value,[]).append(node.lineno)
   for key,lines in saves.items():savedroot[key]=dict(owner=fn,save_lines=sorted(set(lines)),direct_load_lines=sorted(set(loads.get(key,[]))),load_audit='Exactoriginalhelper unchanged under cache ASTadapter; see asserts/calls below',original_source_SHA=H(orig))
   assertions=[dict(line=n.lineno,expression=ast.get_source_segment(s,n.test)) for n in ast.walk(tree) if isinstance(n,ast.Assert)]
   ownerrows.append(dict(helper=fn,original_SHA=H(orig),derived_SHA=H(derived),save_rootkeys=saves,direct_load_rootkeys=loads,original_assertions=assertions))
   if rel in proofs:
    z=proofs[rel];reverse=derived.decode('utf-8-sig').replace('from e1_pinned_source_v1 import cached_load,cached_H,cached_source_owns,runner_source_load_scope\n','',1)
    for site in z['purpose_sites']:reverse=reverse.replace(site['derived'],site['original'],1)
    assert ast.dump(ast.parse(reverse),include_attributes=False)==ast.dump(tree,include_attributes=False),rel
    helperproof.append(dict(relative=rel,original_SHA=H(orig),reverse_cache_adapter_AST_exact=True,original_source_input_same_SHA_as_canonical=True))
   else:
    # sensor_a0 noTorchload source transformation still canonicaladapter entry.
    assert ast.dump(ast.parse(derived),include_attributes=False)==ast.dump(tree,include_attributes=False)
    helperproof.append(dict(relative=rel,original_SHA=H(orig),AST_original_unchanged=True))
  knownNonTensor=[k for k in savedroot if 'resume_contract' in k or k.endswith('initial_source_sha256') or k in ('independent_terrain_expert','E1_terrain_state_legacy_command_ranges_are_noneligible_gentle_only','E1_current_command_profile','E1_CURB_entry_reset_identity')]
  for k in knownNonTensor:savedroot[k]['load_audit']='Historicalrecipe/profile/metadata immutable in completecache; currentknown owner re-emits onfutureSAVE. Allunknownroot/nesteddictfields passthrough retained, effects not invented.'
  if name=='CURB_PROTECTED878':
   producer=root/'original_exact/producer/distributed_rank_worker_v1.py';row=next(r for r in pp['rows'] if r['rank']==0);tr=next(r for r in tp['rows'] if r['rank']==0);assert row['SHA']==meta['original_source_SHA']==tr['full_checkpoint_SHA'];state=tr['three_parameter_optimizer_trees']['optimizer_state_dict'];assert len(state['state'])==17
   evidence=dict(final_own_SHA=row['SHA'],saved_final_tensors=row['tensors'],saved_perenv_tensor_schema=row['perenv_tensor_schema'],saved_Adam17=row['Adam_states'],saved_Adamstep=row['Adamstep'],full_actor_critic_optimizer_tree=tr['three_parameter_optimizer_trees'],same_actor_allthree_ranks=True,independent_actor_count=1,rank1_2_fullcheckpoint_notseparateSlopeActor=True)
   extras={'distributed_rank_contract':dict(owner='producer.distributed_rank_worker_v1.save',producer_line=81,known_fields=['world_size','rank','task','per_rank_envs','global_envs','source_SHA','explicit_source_stream_fork_after_strict_restore'],new_load_owner='variant_extra_state_runtime_v2.restore_extra_before_original_reset',new_save_owner='merge_extra_into_own_save',before_after_audit='finish_extra_after_original_reset',future_rank_fork_or_NCCL=False)}
  else:
   job=0 if name=='CURB_INDEPENDENT113' else 1;producer=root/'original_exact/producer/expert_independent_worker_v1.py';row=next(r for r in fp['closed_models'] if r['job']==job);fr=next(r for r in ip['rows'] if r['job']==job);assert row['SHA']==meta['original_source_SHA'];fields=fr['new_scope_extra_state_preserved'];assert len(fields)==(6 if job==0 else 5)
   evidence=dict(final_own_SHA=row['SHA'],saved_final_tensors=row['tensor_counts'],saved_Adamstep=row['Adam_step'],saved_final_allfinite=row['all_model_runtime_tensors_finite'],SAMEexecuted_savecode_as_first_closed_model=True,first_closed_different_SHA_not_substituted=fr['SHA'],first_closed_saved_extra_fieldlist=fields,first_closed17Adam=fr['all17Adam_first_update'],final_rootkey_values_not_decoded_now=True)
   extras={key:dict(owner='producer.expert_independent_worker_v1.save',producer_line=37,new_load_owner='variant_extra_state_runtime_v2.restore_extra_before_original_reset',new_save_owner='merge_extra_into_own_save',before_after_audit='finish_extra_after_original_reset',known_scope_fields=fields if key.endswith('scope_state') else 'HistoricalentireTASK dict, GPUUUID NOT futurebinding',all_unknown_extra_fields_retained=True) for key in meta['extra_root_keys']}
  for k,v in extras.items():savedroot[k]=v
  sourceP=producer.read_bytes();assert meta['extra_root_keys'][0] in sourceP.decode();mapping=dict(kind='SOURCE_AND_SAVED_CPU_EVIDENCE_ROOTKEY_OWNER_MAP_NOT_NEW_MODEL_PASS',variant=name,original_source_SHA=meta['original_source_SHA'],source_derived_rootkey_inventory=sorted(savedroot),source_derived_inventory_NOT_a_saved_full_rootkey_list=True,rootkey_owner_map=savedroot,original_helper_assertions_and_paths=ownerrows,helper_reverse_AST=helperproof,extra_producer=dict(path=str(producer),SHA=H(sourceP)),saved_evidence_reports=reports,saved_CPU_evidence=evidence,gaps=[dict(kind='SAVED_EVIDENCE_INVENTORY_GAP',detail='Savedfinal report has tensor schemas/counts/finite/Adam but no full nonTensorrootkeyinventory/values. Sourcewritechain maps knownkeys; arbitraryotherrootkeys/unknownphysicalowners remain UNKNOWNpending samefuture completeCPUcache, preserved not assumedabsent.'),dict(kind='FUTURE_ACTUAL_REQUIRED',detail='No actualPT/stat/hash/decode nor SDK inthisphase; LR/iteration ifabsent remainUNKNOWN, newasset skill notqualified.')],unknown_passthrough='Original sourceunknownroot/nesteddictkeys survive futureSAVE; currentknownactor/optimizer/history leaves win, unknownphysicaleffects not claimed',PT_SSH_SDK_GPU_operations=0)
  with (root/'SAVED_EVIDENCE_ROOTKEY_HELPER_OWNER_MAP_V1.json').open('x',encoding='utf-8') as f:json.dump(mapping,f,indent=2)
  results.append(dict(variant=name,source_derived_keys=len(savedroot),helpers_AST_exact=len(helperproof),ownextras=meta['extra_root_keys'],saved_rootinventory_gap_explicit=True));print(json.dumps(results[-1],indent=2))
 with (B/'THREE_VARIANT_SAVED_EVIDENCE_OWNERSHIP_SUMMARY_V1.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='SOURCE_ONLY_THREE_VARIANT_SAVE_LOAD_AUDIT_MAP',variants=results,PT_operations=0),f,indent=2)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('OWNER_MAP_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),PT_SDK_operations=0),f,indent=2)
  raise

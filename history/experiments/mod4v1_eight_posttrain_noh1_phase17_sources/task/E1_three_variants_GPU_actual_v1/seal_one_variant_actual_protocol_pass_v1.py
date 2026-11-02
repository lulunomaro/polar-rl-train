"""Localactual collection reader/seal, no SDK/PT/stat/hash/decode of binaries."""
from pathlib import Path
import argparse,hashlib,json,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;C=T/'E1_three_variants_CPU_actual_v1'

def main():
 p=argparse.ArgumentParser();p.add_argument('--variant',choices=['CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE_INDEPENDENT50'],required=True);p.add_argument('--native-collection',type=Path,required=True);p.add_argument('--fresh-collection',type=Path,required=True);a=p.parse_args();name=a.variant
 native=json.loads(a.native_collection.read_bytes());fresh=json.loads(a.fresh_collection.read_bytes());f=native['files'];d=f['gpu1/out/E1_NATIVE24_192PHYSICS_48FEEDBACK_NOUPDATE_COMPLETE.json'];close=f['PARENT_EXIT_SCOPE.json'];core1=f['gpu1/out/E1_CORE_BEFORE.json'];core2=f['gpu1/out/E1_CORE_AFTER.json'];first=f['gpu1/out/VARIANT_FIRST_BEFORE_CONTROL.json'];extra=f['gpu1/out/VARIANT_EXTRA_FULLSTATE_RESUME_STARTUP_VERIFIED.json'];reads=f['gpu1/out/E1_SOURCE_FINAL_READ_COUNTS.json'];cpu=json.loads((C/(name+'_CPU_FOUR_LEAF_ACTUAL_COMPLETE.json')).read_bytes());owner=json.loads((C/(name+'_ACTUAL_FULL_NESTED_OWNER_AUDIT_V1.json')).read_bytes());actual=cpu['actual_source_metadata']
 for col in [fresh,native]:
  final=col['files']['FINAL.json'];cl=col['files']['PARENT_EXIT_SCOPE.json'];row=final['rows'][0];assert final['passed'] and row['returncode']==0 and row['actual_waited'] and not row['error_json_exists'];assert cl['all_own_children_waited'] and cl['original_private_lock_released'] and cl['original_shared_lock_released'] and cl['all_partialleases_released'] and not cl['errors']
 assert native['canonical']==fresh['canonical']==name and d['passed'] and d['canonical']==name
 assert d['num_envs']==20000 and d['controls']==24 and d['physics_callbacks']==192 and d['feedback_samples']==48 and d['one_original_fresh_reset']==1 and d['core_before_after_exact']
 assert core1['core']==core2['core'] and all(v==0 for v in d['forbidden_calls'].values())
 assert d['actual_source_counters']==dict(iteration=actual['original_iteration'],LR=actual['original_LR'],STD6=actual['original_STD6'],Adam_steps=[actual['original_17Adam_step']])
 assert reads['source_SHA']==cpu['new_typed_source']['SHA'] and reads['original_source_SHA']==cpu['original_source']['SHA'];assert reads['selected_source_physical_byte_reads']==reads['selected_source_SHA_calculations']==reads['selected_source_decodes']==1 and reads['four_leaf_migration']['migration_calls_in_SDK']==0
 assert extra['variant']==name and extra['all_complete_saved_extras_exact'] and extra['extra_reset_physics_RNG_calls']==0 and extra['after_original_reset']['all_saved_extra_fields_before_after_exact']
 assert first['variant']==name and first['selected_typed_source_SHA']==cpu['new_typed_source']['SHA'] and first['all_actual_root_nested_owners_mapped'] and first['passthrough_only_is_NOT_physical_apply'] and first['unknown_root_or_nested_preserve_only_fields']==[]
 assert d['actual_mild_DR_audit_before']['actual_parameters_pass'] and d['actual_mild_DR_audit_after']['actual_parameters_pass']
 required={'SENSOR_RESUME_STARTUP_VERIFIED.json','DELAY_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json','VARIANT_EXTRA_FULLSTATE_RESUME_STARTUP_VERIFIED.json'}
 names={Path(k).name:k for k in f};assert required<=set(names)
 if name=='CURB_PROTECTED878':assert first['rank0_only20kshard_NOTall60k'] and not first['NCCL_merge_fork']
 report=dict(kind='EXPLICIT_FROZEN_VARIANT_ACTUAL_CPU_FRESH_NATIVE24_PROTOCOL_PASS_NOT_SKILL',variant=name,original_source_SHA=cpu['original_source']['SHA'],new_typed_source=cpu['new_typed_source'],actual_source_metadata=actual,CPU_counts=cpu['counts'],source_owner_unknown=[],actual_scope='Onlyoriginalrank0 complete20k shard; historicalworld3/60k contract retained; NOT all60k restore' if name=='CURB_PROTECTED878' else 'Ownindependentfixedaxis complete20k state preserved',fresh_collection=str(a.fresh_collection),native_collection=str(a.native_collection),actual_GPU_UUID=f['CHILDREN.json'][0]['GPU_UUID'],native_child=f['CHILDREN.json'][0],native_root=native['remote_root'],first_before_control=first,source_counts=reads,extra_actual_resume_receipt=extra,complete9_original_and_extra_helper_receipts=[dict(path=names[n],SHA=next(r['SHA'] for r in native['collected_file_index'] if r['relative']==names[n])) for n in sorted(required)],core_before_after_treeSHA=core1['core']['tree_SHA'],STD17Adam_LR_iteration_beforeafter_exact=True,controls=24,physics=192,feedback=48,ONEoriginalreset=1,forbidden_calls=d['forbidden_calls'],closewait_originalEX_finiteSH_release=close,not_skill_or_birthinertia_or_fullhardwareDR_or_allhistory_graduation=True,no_productionGO_PPO_canonical_budget=True,parent_Gitpending=True,child_commit_push=False)
 out=T/(name+'_ACTUAL_CPU_FRESH_NATIVE24_PROTOCOL_HANDOFF_V1.json')
 with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(handoff=str(out),SHA=hashlib.sha256(out.read_bytes()).hexdigest(),variant=name,actualpassed=True,native_root=native['remote_root'],core_treeSHA=report['core_before_after_treeSHA'],unknownowner=[],leases_released=True),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('VARIANT_ACTUAL_SEAL_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),PT_SDK_operations=0,no_replay=True),f,indent=2)
  raise

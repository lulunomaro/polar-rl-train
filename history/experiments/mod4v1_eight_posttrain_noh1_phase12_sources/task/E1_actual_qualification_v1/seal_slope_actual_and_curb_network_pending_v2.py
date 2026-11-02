"""After actualterminal collection seal SLOPE branch; CURBnetworkpending explicit.
Local originalJSON/source only. No new PT/stat/hash/decode/SSH/SDK/GPU/Git.
"""
from pathlib import Path
import argparse,hashlib,json
B=Path(__file__).resolve().parent;T=B.parent
p=argparse.ArgumentParser();p.add_argument('--collection',type=Path,required=True);a=p.parse_args()
def ld(p):return json.loads(Path(p).read_text(encoding='utf-8'))
c=ld(a.collection);f=c['files'];final=f['FINAL.json'];closed=f['PARENT_EXIT_SCOPE.json'];row=final['rows'][0];assert final['passed'] and row['returncode']==0 and row['actual_waited'] and not row['error_json_exists'];assert closed['all_own_children_waited'] and closed['original_private_lock_released'] and closed['original_shared_lock_released'] and not closed['errors']
P='gpu1/out/';d=f[P+'E1_NATIVE24_192PHYSICS_48FEEDBACK_NOUPDATE_COMPLETE.json'];before=f[P+'E1_CORE_BEFORE.json'];after=f[P+'E1_CORE_AFTER.json'];reads=f[P+'E1_SOURCE_FINAL_READ_COUNTS.json'];first=f[P+'E1_FULLRESTORE_BEFORE_NATIVE24.json'];cpu=ld(B/'SLOPE135_CPU_FOUR_LEAF_ACTUAL_COMPLETE.json');fresh=ld(T/'reports/SLOPE135_actual_case_collect_20261102_054541/COLLECTION.json')
assert d['passed'] and d['num_envs']==20000 and d['controls']==24 and d['physics_callbacks']==192 and d['feedback_samples']==48 and d['one_original_fresh_reset']==1
assert d['core_before_after_exact'] and before['core']==after['core'] and all(v==0 for v in d['forbidden_calls'].values())
assert reads['selected_source_physical_byte_reads']==reads['selected_source_SHA_calculations']==reads['selected_source_decodes']==1 and reads['source_SHA']==cpu['new_typed_source']['SHA']
assert reads['four_leaf_migration']['migration_calls_in_SDK']==0
actual=d['actual_source_counters'];assert actual['iteration']==32069 and actual['LR']==6.666666666666667e-05 and actual['Adam_steps']==[642980] and actual['STD6']==cpu['actual_source_metadata']['original_STD6']
assert d['actual_mild_DR_audit_before']['actual_parameters_pass'] and d['actual_mild_DR_audit_after']['actual_parameters_pass'] and d['nominal_guard']['original_fresh_reset_calls']==1
assert fresh['files']['FINAL.json']['passed'] and fresh['files']['PARENT_EXIT_SCOPE.json']['original_private_lock_released'] and fresh['files']['PARENT_EXIT_SCOPE.json']['original_shared_lock_released']
required={'SENSOR_RESUME_STARTUP_VERIFIED.json','DELAY_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json'}
actualfiles={Path(k).name:k for k in f};assert required<=set(actualfiles)
curb=ld(B/'CURB141_EXACT_TUNNEL_STAT_V4.json');assert curb['source_byte_reads_hashes_decodes']==0
summary=dict(kind='SLOPE135_CANONICAL_ACTUAL_CPU_TYPED_FRESH_NATIVE24_PASS_CURB141_NETWORK_PENDING',SLOPE135=dict(status='ACTUAL_PROTOCOL_PASS_NOT_LONG_SKILL',original_source_SHA=cpu['original_source']['SHA'],typed_source=cpu['new_typed_source'],CPU_receipt=str(B/'SLOPE135_CPU_FOUR_LEAF_ACTUAL_COMPLETE.json'),CPU_counts=cpu['counts'],actual_source_metadata=cpu['actual_source_metadata'],CUDA16byte_rng_preserved_no_CPU_CUDArestore=True,fresh_collection=str(T/'reports/SLOPE135_actual_case_collect_20261102_054541/COLLECTION.json'),native_collection=str(a.collection),native_root=c['remote_root'],GPU_UUID=f['CHILDREN.json'][0]['GPU_UUID'],actual_native_readcounts=reads,actual_counters=actual,controls=24,physics=192,feedback=48,ONE_original_reset=1,fullhelper_receipts=[dict(file=actualfiles[n],SHA=next(r['SHA'] for r in c['collected_file_index'] if r['relative']==actualfiles[n])) for n in sorted(required)],core_before_after_exact=True,forbidden_calls=d['forbidden_calls'],original_closewaitrelease=closed,oldGPU1case='Onlymetadatawaiter cancelled withPIDcreationguard beforetoken/children; rawwait/cancel retained, no SDKreplay'),CURB141=dict(status='EXACT_ORIGINAL_PATH_STAT_UNOBTAINED_NETWORK_NOT_MODEL_MISSING',expected_SHA=curb['expected_SHA'],exact_original_path=curb['source_path'],direct_and_approved_tunnel_errors_preserved=True,source_byte_reads_hashes_decodes=0,CPU_purpose_unconsumed=True,actual_typed_or_SDK_not_done=True,no_actor_substitute=True),boundaries=dict(canonical_budget_productionGO_PPO=False,independent_backend_or_birthinertia_claim=False,long_SLOPE5_or_CURB_skill_graduation=False,D6='Originalgasdamping only',other_frozen878_113_50_df0_actual_operations=0,student_GPU1_or_foreignprocess_touched=False),parent_Git_append_archive_pending=True,child_commit_push=False)
out=T/'SLOPE135_ACTUAL_PROTOCOL_PASS_CURB141_NETWORK_PENDING_HANDOFF_v1.json'
with out.open('x',encoding='utf-8') as file:json.dump(summary,file,ensure_ascii=False,indent=2)
files=[]
for file in B.rglob('*'):
 if file.suffix.lower() in ('.pt','.pth','.npz','.usd','.zip','.onnx','.safetensors','.pyc'):continue
 if file.is_file():
  raw=file.read_bytes();files.append(dict(path=str(file),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
for file in [out,a.collection]:
 raw=file.read_bytes();files.append(dict(path=str(file),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
index=T/'E1_ACTUAL_CPU_SLOPE_PROTOCOL_AND_ALL_ERRORS_ARCHIVE_PENDING_v1.json'
with index.open('x',encoding='utf-8') as file:json.dump(dict(kind='E1_ACTUAL_PHASE_ARCHIVE_PENDING_ALL_ERRORS_NOT_ONLY_SUCCESS',files=files,report_directories_include='Allnew reports/SLOPE135_* and CURB141_* plus E1_exact* and originalcollector directories; nooriginalrawfalseoverwrite',binary_paths_size_SHA_only=True,selected_PT_extra_archive_read=False,child_Gitcommit_push=False,all_actual_SLOPE_children_closed_waited_leases_released=True,CURB_not_falsely_closed=True),file,ensure_ascii=False,indent=2)
print(json.dumps(dict(handoff=str(out),handoff_SHA=hashlib.sha256(out.read_bytes()).hexdigest(),archive_index=str(index),archive_index_SHA=hashlib.sha256(index.read_bytes()).hexdigest(),files=len(files),status='SLOPEactualpass_CURBnetworkpending'),indent=2))

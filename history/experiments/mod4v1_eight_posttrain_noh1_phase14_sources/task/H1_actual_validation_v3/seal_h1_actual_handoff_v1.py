"""Seal actual H1 evidence AFTER collection. Local JSON/source only, no PT/SSH/SDK."""
from pathlib import Path
import argparse,hashlib,json
B=Path(__file__).resolve().parent;T=B.parent
p=argparse.ArgumentParser();p.add_argument('--collection',type=Path,required=True);a=p.parse_args()
def ld(p):return json.loads(Path(p).read_text(encoding='utf-8'))
loc=ld(B/'CURRENT_N20K_CASE.json');c=ld(a.collection);assert c['remote_root']==loc['remote_root'];f=c['files'];final=f['FINAL.json'];closed=f['PARENT_EXIT_SCOPE.json'];assert final['passed'] and final['rows'][0]['returncode']==0 and final['rows'][0]['actual_waited'];assert closed['all_own_children_waited'] and closed['original_private_lock_released'] and closed['original_shared_lock_released'] and not closed['errors']
P='gpu1/control_out/'
result=f[P+'MOD4V1_NORMAL_H1_NATIVE24_192PHYSICS_48FEEDBACK_NOUPDATE.json'];before=f[P+'H1_CORE_AND_DR_BEFORE.json'];after=f[P+'H1_CORE_AND_DR_AFTER.json'];reads=f[P+'SOURCE_FINAL_READ_COUNTS.json'];initial=f[P+'MOD4V1_NORMAL_H1_FULLRESTORE_BEFORE_MEAN_ACTION.json']
assert result['passed'] and result['num_envs']==20000 and result['controls']==24 and result['physics_callbacks']==192 and result['feedback100Hz_samples']==48
assert before['core']==after['core'] and after['core_before_after_exact'] and result['core_before_after_exact']
assert after['core']['iteration']==41448 and after['core']['alg_LR']==.00038443359375000017
assert all(g['lr']==.00038443359375000017 for g in after['core']['param_groups'])
assert all(v==0 for v in after['forbidden_calls'].values()) and result['source_17Adam_step']==832460
assert reads['selected_source_physical_byte_reads']==reads['selected_source_SHA_calculations']==reads['selected_source_decodes']==1 and reads['source_bytes']==16879851
assert result['new_asset_nominal_guard']['original_fresh_reset_calls']==1 and after['one_original_fresh_reset']==1
assert initial['actual_reward_manager_dt_probe']['dt']==.02 and all(r['public_age100Hz_plus2_or_selected_reset0'] for r in result['per_control'])
assert before['actual_mild_DR_audit']['actual_parameters_pass'] and after['actual_mild_DR_audit']['actual_parameters_pass']
assert f[P+'ENV_CLOSE_RETURNED.json']['closed'] and P+'APP_CLOSING.json' in f and P+'NORMAL_H1_NATIVE24_ORIGINAL_EXCEPTION_BEFORE_APP_CLOSE.json' not in f
freshloc=ld(B/'FRESH80_RECONCILIATION_LOCATOR.json');fresh=ld(freshloc['local_report']);assert fresh['passed_actual_fresh_worker_and_clean_release'] and fresh['actual_original_final_summary_passed'] is False
summary=dict(kind='H1_NORMAL_MOD4V1_NEWASSET_FRESH80_AND_TYPED71DB20K_NATIVE24_NOUPDATE_ACTUAL_HANDOFF',fresh80=dict(actual_worker_passed=True,original_parent_reader_false_preserved=True,reconciliation_report=freshloc['local_report'],root=fresh['remote_root'],child_pid=fresh['original_terminal_row']['pid'],controls=24,physics=192,feedback=48,PT_and_actor_and_optimizer=0),whole20k=dict(collection_path=str(a.collection),root=loc['remote_root'],parent=loc['parent'],child=f['CHILDREN.json'][0],source_SHA=result['source_SHA'],source_bytes=reads['source_bytes'],source_physical_reads=1,source_SHA_calculations=1,source_decodes=1,stored_iteration=41448,Adam17=832460,LR=after['core']['alg_LR'],raw_STD6=after['core']['raw_STD6'],core_before_after_exact=True,forbidden_calls=after['forbidden_calls'],original_fresh_resets=1,controls=24,physics=192,feedback=48,actualRewardManager_dt=.02,publicPhase_age100Hz_plus2=True,actual_mild_DR_before_pass=True,actual_mild_DR_after_pass=True,close_wait_release=closed),source_and_failure_history=dict(sourceV1_index=str(T/'staged_sources/H1_NORMAL_MOD4V1_SOURCE_V1/FINAL_SOURCE_INDEX.json'),sourceV2_index=str(T/'staged_sources/H1_NORMAL_MOD4V1_SOURCE_V2/FINAL_SOURCE_INDEX.json'),actualmother453_manifest_SHA='97cdcde4a891359a5f1209fdad1614bf87629e0c3d3a40ce9018dc1fe9e2426b',first_fresh_failure='Missingprobe basename; RC2, noSDK/PT',second_fresh_failure='Old700->517c compatibility excludedbae; actualerror despiteRC0; noPT',third_fresh_metadata_error='ActualSDKPASS correctH1_FRESH80_COMPLETE; parentwrongNATIVH1_NORMAL4 name retainedfalse; append-only reconciled, noSDKreplay',CPU_noupdate_derivation_failure='Indentanchor, noSDK/PT; separateV2 AST-equivalent prep',reader_misses_preserved=True),qualification=dict(interface=[35,38,6],clock=[50,100,.0025,32,4],USD_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',contract_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755',closure_m=.01,mimic_rad=.01,source400N50_inherited_not_retyped=True,D6='Originalgasdamping only; not alljointfriction',getter='Componentmemory not independentbackend',independent_birth_inertia_claim=False,skill270mm_graduation=False,full_hardware_calibration=False,productionGO_or_PPO=False,canonical_access=False,foreignGPU0_or_parentW35scope_touched=False),archive='Parent append-only archive pending; child noGitcommit/push')
path=T/'H1_NORMAL_MOD4V1_ACTUAL_HANDOFF_v1.json'
with path.open('x',encoding='utf-8') as out:json.dump(summary,out,ensure_ascii=False,indent=2)
files=[]
for folder in ['H1_actual_validation_v1','H1_actual_validation_v2','H1_actual_validation_v3','staged_sources/H1_NORMAL_MOD4V1_BUILDER_V1','staged_sources/H1_NORMAL_MOD4V1_SOURCE_V1','staged_sources/H1_NORMAL_MOD4V1_SOURCE_V2']:
 for file in (T/folder).rglob('*'):
  if file.suffix.lower() in ('.pt','.pth','.npz','.usd','.zip','.onnx','.safetensors'):continue
  if file.is_file():
   raw=file.read_bytes();files.append(dict(path=str(file),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
for file in [path,a.collection,Path(freshloc['local_report']),T/'reports/H1_typed71db_transport_actual_20261102_040952.json']:
 raw=file.read_bytes();files.append(dict(path=str(file),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
idx=T/'H1_NORMAL_MOD4V1_ACTUAL_ARCHIVE_PENDING_INDEX_v1.json'
with idx.open('x',encoding='utf-8') as out:json.dump(dict(kind='H1_ALL_NEW_SOURCE_CONTROL_ERRORS_ACTUAL_REPORTS_ARCHIVE_PENDING',files=files,reports_to_include_parent_scoped_H1_glob='reports/H1_* json plus H1_fresh_collect_* and H1_n20k_collect_* directories; retain original raw files',large_nonmodel_bundles='Only recorded stagebundle realpath/size/SHA; no archivecontent',new_model_source_and_startup_PT='Original remote paths only; never extraPTread for archive',child_commit_or_push=False),out,ensure_ascii=False,indent=2)
print(json.dumps(dict(status='H1_ACTUAL_NEWASSET_NOUPDATE_PASS_NOT_SKILL',handoff=str(path),handoff_SHA=hashlib.sha256(path.read_bytes()).hexdigest(),archive_index=str(idx),archive_index_SHA=hashlib.sha256(idx.read_bytes()).hexdigest(),files=len(files),no_remaining_SDK_child_by_original_parent=True),indent=2))

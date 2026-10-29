"""Final source-only seal. No binary/model/stat/source environment operations."""
from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent;L=B.parent;P=L/'NEW86_W35_ADAPTED92_N20K_PROFILE_REGRESSION_SOURCE_V1'
INDEX='FROZEN_E2_93_NEW86_PROFILE_DOMAIN_SOURCE_INDEX_V1.json'
def H(raw):return hashlib.sha256(raw).hexdigest()
def put(n,v):
 with (B/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def parsed(p):return ast.parse(p.read_bytes())
def func(tree,name):return next(x for x in ast.walk(tree) if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.name==name)
def equal(a,b):return ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
def main():
 assert not (B/INDEX).exists()
 m=json.loads((B/'E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes());proof=json.loads((B/'E2_BOUND_SOURCE_DERIVATION_ACTUAL.json').read_bytes());test=json.loads((B/'reports/E2_FRESH_SYNTHETIC_CPU_AND_SOURCE_AST_ACTUAL_V1.json').read_bytes());assert test['passed'] and test['count']==32
 source75=L/'W35_PROFILE_PANEL210_TENSORDICT_SNAPSHOT_REPAIR_UNUSED_SOURCE_20261029_V3/w35_profile_env_domain_panel_v1.py';old=parsed(source75);new=parsed(B/'lossless_snapshot_pinned75d683.py')
 assert equal(func(old,'_snapshot'),func(new,'_snapshot')) and equal(func(old,'encode_snapshot_mapping_key'),func(new,'encode_snapshot_mapping_key'))
 assert (B/'project_clone_launch_helpers_v1.py').read_bytes()==(P/'project_clone_launch_helpers_v1.py').read_bytes()
 # Invert the declared derivation exactly, including the native24-success extension.
 derivations=[]
 for row in proof['derivations']:
  original=Path(row['source']).read_bytes();text=original.decode('utf8')
  for x in row['literal_replacements']:assert text.count(x['old'])==x['count'];text=text.replace(x['old'],x['new'])
  assert H(text.encode())==row['target_SHA']
  if row.get('required_native24_success_extension'):
   oldvalue='and result.exists() and not errs';newvalue="and result.exists() and (out/'ACTUAL_NATIVE24_E2_40050_CLOCK_QUEUE.json').exists() and not errs";assert text.count(oldvalue)==1;text=text.replace(oldvalue,newvalue)
  actual=(B/row['target']).read_bytes();assert actual.decode('utf8')==text,row['target'];derivations.append(dict(source=row['source'],target=row['target'],source_SHA=H(original),selected_final_SHA=H(actual),literal_forward_reconstruction_passed=True))
 # Input rows are reused by exact metadata. Do not touch their binary paths here.
 original_manifest=L/'E2_PPO50_gas400_source_preparation_20261028/E2_COMPLETE_INSTALL_MANIFEST_V1.json';base=json.loads(original_manifest.read_bytes());by={x['relative']:x for x in m['files']}
 original_rows=[]
 for row in base['files']:
  if row['relative'].endswith('.pt') or row['relative']=='E2_PPO50_gas400_finite_worker_v1.py':continue
  assert by[row['relative']]==row;original_rows.append(row['relative'])
 final=by['source/E2_ADAPTED93_FINAL92.pt'];assert final['bytes']==14615089 and final['SHA']==m['model_SHA'] and 'b3ae94df' in final['SHA']
 selected=[r['relative'] for r in m['files'] if Path(r['local_path']).parent==B]
 for name in selected:
  raw=(B/name).read_bytes();assert by[name]['bytes']==len(raw) and by[name]['SHA']==H(raw),name
 executable={n:H((B/n).read_bytes()) for n in selected if n.endswith('.py')}
 for p in B.glob('*.py'):parsed(p)
 clone=L/'NEW_HOST_VERIFIED_BUNDLE_EXTRACT_RELOCATION_SOURCE_V1/reports/ROOT_VERIFIED_EXTRACT_RELOCATION_RETURNED_ACTUAL.json';sdk=L/'NORMAL_H1_NEW86_PROJECT_WHOLECPU_NATIVE24_ADMISSION_SOURCE_V2_LIGHT_POLICY/reports/NEW86_NORMAL_H1_WHOLECPU_CUDA_NATIVE24_ORIGINAL_RETURNED_ACTUAL.json'
 # Existing TEXT receipt pinning does not repeat clone/CUDA/model qualification.
 cp=json.loads(clone.read_bytes());sp=json.loads(sdk.read_bytes());assert cp['passed_extract_relocate_only'] and cp['all_control_SSH_closed'] and sp['passed_actual_wholeCPU_CUDA_fullrestore_native24_only'] and sp['private_EX_released']
 put('E2_FINAL_SOURCE_ONLY_RECONCILIATION_AND_INVERSE_PROOF_ACTUAL.json',dict(passed=True,derived_transport_forward_reconstruction=derivations,common_clone_environment_and_loader_exact_bytes=True,SDK_runtime_input_rows_metadata_unchanged=len(original_rows),only_initial_E2_PT_row_replaced_by_qualified93_metadata=True,binary_PT_USD_NPZ_stat_read=False,snapshot_generic_function_AST_exact_to_actual75d=True,actual75d_source=str(source75),actual75d_source_SHA=H(source75.read_bytes()),actual_target_TensorDict_0141_prior_W35_source_API_pass_reused=True,local_fresh_TensorDict_0151_test_is_not_target_API_proof=True,actual_new_E2_target_CPU_metadata_CUDA_fullrestore_native24_900controls_pending=True,no_remote_or_model_or_SDK_calls=True))
 put('SOURCE_PREPARATION_TOOL_NOTES_ACTUAL.json',dict(saved_apply_patch_output_truncation='New telemetry file existed and was verified by AST; patch not rerun blindly.',source_lookup_missing_path_errors='Three guessed source basenames did not exist; corrected by exact known module source text. No remote/SDK/model access.',all_previous_pending_savepoint_and_errors_preserved=True,no_trial_or_tag_created=True))
 files=[]
 for p in sorted(B.rglob('*')):
  if p.is_file():
   assert p.suffix in ('.py','.json','.md'),str(p);raw=p.read_bytes();files.append(dict(relative=p.relative_to(B).as_posix(),bytes=len(raw),SHA=H(raw)))
 value=dict(status='FROZEN_SOURCE_ONLY_PREPARED_UNUSED_NOT_TARGET_ADMITTED',entry='upload_admit_detach_NEW86_E2_final93_profiles_secure_stdin_UNUSED_once_v1.py',entry_SHA=executable['upload_admit_detach_NEW86_E2_final93_profiles_secure_stdin_UNUSED_once_v1.py'],manifest_local_filename='E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json',manifest_SHA=H((B/'E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes()),executable_source_SHAs=executable,clone_receipt_SHA=H(clone.read_bytes()),actual_clone_CUDA_SDK_receipt_SHA=H(sdk.read_bytes()),files=files,source_model_SHA=m['model_SHA'],original_17_Adam=859300,original_LR=.00022500000000000002,requested_controls=900,warmup_controls=100,steady_controls=800,num_envs=20000,maximum_worker_seconds=1680,maximum_supervisor_wait_seconds=1800,CPU_fresh_synthetic_checks=32,metadata_admission_PT_loads=0,actual_original_CUDA_restore_chain_still_mandatory=True,no_learning_GO_owner_ledger_or_normalizer_update=True,no_graduation_or_complete_WM_dataset=True,Git_status='EXPLICIT_PENDING ordinary root supplement; no trial/tag')
 put(INDEX,value);print(json.dumps(dict(passed=True,index=INDEX,SHA=H((B/INDEX).read_bytes()),files=len(files),entry_SHA=value['entry_SHA'],source_only=True)))
if __name__=='__main__':main()

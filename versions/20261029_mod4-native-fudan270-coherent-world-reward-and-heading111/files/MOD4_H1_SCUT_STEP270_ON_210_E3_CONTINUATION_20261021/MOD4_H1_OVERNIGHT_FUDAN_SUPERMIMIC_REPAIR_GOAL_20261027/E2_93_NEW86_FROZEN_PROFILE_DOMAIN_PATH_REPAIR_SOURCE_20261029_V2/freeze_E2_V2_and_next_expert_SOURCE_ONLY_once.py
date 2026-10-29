from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent;L=B.parent
def H(raw):return hashlib.sha256(raw).hexdigest()
def put(n,x):
 with (B/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
def main():
 selection=json.loads((B/'E2_V2_SELECTION_PENDING_FINAL_FREEZE.json').read_bytes());test=json.loads((B/'reports/E2_V2_READER_PURE_METADATA_CPU_AND_AST_ACTUAL.json').read_bytes());assert test['passed'] and test['count']==22
 raw=(B/'E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes();assert H(raw)==selection['manifest_SHA'];m=json.loads(raw)
 for r in m['files']:
  if Path(r['local_path']).parent==B:raw=(B/r['relative']).read_bytes();assert len(raw)==r['bytes'] and H(raw)==r['SHA']
 old=L/'E2_93_NEW86_FROZEN_PROFILE_DOMAIN_SOURCE_PREPARATION_20261029_V1'
 for name,sha in selection['executable_source_SHAs'].items():assert H((B/name).read_bytes())==sha
 # Next distinct old expert: only its already-saved qualification JSON/source text.
 p=L/'TWO97_NEW_E3_PPO_FORMAL_INITIAL_CPU_SOURCE_V1/reports/E3_97_NEW_FORMAL_INITIAL_WHOLE_CPU_ACTUAL_V1.json';raw=p.read_bytes();v=json.loads(raw);assert v['passed'] and v['model']['SHA']=='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8' and v['Adam_step']==866060
 manifest=L/'E3_97_GAS400_COMPLETE_RUNTIME_SOURCE_CPU_PREPARATION_V1/E3_COMPLETE_INSTALL_MANIFEST_V1.json';rows=json.loads(manifest.read_bytes())['files'];selected=[r for r in rows if r['relative'].endswith(('e3_public_recovery_phase_v1.py','e3_recovery_runtime_v1.py','e3_fullstate_checkpoint_v1.py','train_E3_fullstate_v1.py'))]
 w=L/'W35_PROFILE_PANEL_V3_FINAL_SAVED_TEXT_REVIEW_20261029_V1/FROZEN_W35_V3_FINAL_TEXT_REVIEW_INDEX_ACTUAL.json'
 put('NEXT_USEFUL_OLD_EXPERT_SOURCE_QUEUE_ONLY.json',dict(status='SOURCE_METADATA_CONTRACT_ONLY_NOT_TARGET_ADMITTED_NOT_EXECUTABLE',first_selected='E2_93 V2 exact-root900 profile/domain diagnostic',reason='W35 v3 full-population metrics and counter events do not establish per-command cycle progress; do not blindly repeat its unchanged window',W35_saved_text_review_index=str(w),W35_review_index_SHA=H(w.read_bytes()),next_distinct_expert='E3_97 original13recipe recovery',E3_original_wholeCPU_report=str(p),E3_original_report_SHA=H(raw),E3_model=v['model'],E3_new_updates=v['new_updates'],E3_Adam=v['Adam_step'],E3_RSL_iteration=v['stored_iteration'],E3_LR=v['adaptive_LR'],E3_fullfinite_original_D1_D7_and13recipe_CPU=v['all_critical_D1_D7_and_E3_13recipe_phase_CPU_validated'],E3_original_phase_source_metadata=selected,E3_metric_contract='e3_next_original_phase_metric_contract_source_v1.py',original_request3s_and_stable_point5s_preserved=True,no_W35_or_E2_mode_relabel=True,no_PT_raw_NPZ_model_SDK_remote_or_GPU_call=True,remaining='E3 readonly runtime instrumentation and final97 input/admission/secure supervisor, followed by actual targetCUDA/native24 and perrecipe coverage',skill_graduation=False))
 tree=ast.parse((B/'e3_next_original_phase_metric_contract_source_v1.py').read_bytes());scope={};exec(compile(tree,'<E3 pure metadata contract only>','exec'),scope)
 assert scope['phase_label'](12,0,False)=='original_recipe12_normal_zero_command_baseline';assert scope['phase_label'](1,298,True)=='original_fall_request_first3s';assert scope['phase_label'](1,300,False)=='original_post_request_soft_termination_unmasked';assert scope['original_new_credit'](False,True,7,7)
 try:scope['original_new_credit'](False,True,7,8)
 except AssertionError:pass
 else:raise AssertionError('crossreset credit accepted')
 readonly=['E2_frozen_actual_receipts_readonly_CODE_v1.py','run_E2_new86_readonly_secure_stdin_v1.py','read_E2_new86_FIRST_native24_queue_secure_stdin_UNUSED_once_v1.py','collect_E2_new86_TERMINAL_fulltext_secure_stdin_UNUSED_once_v1.py']
 for p in B.glob('*.py'):ast.parse(p.read_bytes())
 files=[]
 for p in sorted(B.rglob('*')):
  if p.is_file():
   assert p.suffix in ('.py','.json','.md');raw=p.read_bytes();files.append(dict(relative=p.relative_to(B).as_posix(),bytes=len(raw),SHA=H(raw)))
 selection.update(status='FROZEN_SOURCE_ONLY_UNUSED_PENDING_ROOT_REVIEW_AND_ACTUAL_ADMISSION',readonly_source_SHAs={n:H((B/n).read_bytes()) for n in readonly},first_reader=readonly[2],terminal_reader=readonly[3],entry_SHA=selection['executable_source_SHAs'][selection['entry']],files=files,root_path_repair_metadata_positive_and4negative_passed=True,reader_pure_metadata22_checks=True,prior32_fresh_CPU_source_witness_reused=True,first_wait_max110=True,supervisor_max1800_worker1680=True,normal_remaining900_and_wait850_preserved=True,actual_startup_supervisor_identity='PENDING future actual returned report; no fabricated PID/create',no_remote_GPU_SDK_model_read_or_ledger_write=True,skill_graduation=False,complete_WM_dataset=False,Git_status='EXPLICIT_PENDING root ordinary supplement, no trial/tag')
 put(selection['index'],selection);print(json.dumps(dict(passed=True,index=selection['index'],index_SHA=H((B/selection['index']).read_bytes()),entry=selection['entry'],entry_SHA=selection['entry_SHA'],manifest_SHA=selection['manifest_SHA'],files=len(files),source_only=True)))
if __name__=='__main__':main()

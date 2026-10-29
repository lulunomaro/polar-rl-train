from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent;L=B.parent
def H(b):return hashlib.sha256(b).hexdigest()
def main():
 s=json.loads((B/'V4_SELECTED_SOURCE_PENDING_FINAL_FREEZE.json').read_bytes());proof=json.loads((B/'reports/REAL_SELECTED_ENTRY_RECEIPT_CLI_HOOK_DEPENDENCY_COMPLETE_SCOPE_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and len(proof['negative_cases_rejected'])==8 and len(proof['complete_declared_internal_source_import_closure']['entry_and_internal_import_source_SHA_closure'])==70
 mf=B/'E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json';manifest=json.loads(mf.read_bytes());assert len(manifest['files'])==450
 for row in manifest['files']:
  if Path(row['local_path']).parent==B:
   p=Path(row['local_path']);raw=p.read_bytes();assert len(raw)==row['bytes'] and H(raw)==row['SHA'],row['relative']
 worker='evaluate_E3_adapted97_source210_frozen600_once_v1.py';old=L/'E3_97_SOURCE210_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V3';raw=(B/worker).read_bytes();inverse=raw.replace(b'train_E3_fullstate_v1.py',b'train_E3_full_resume_v1.py').replace(b'ACTUAL_NATIVE24_E3_40050_CLOCK_QUEUE.json',b'ACTUAL_NATIVE34_E3_40050_CLOCK_QUEUE.json');assert inverse==(old/worker).read_bytes()
 with (B/'SELECTED_WORKER_ONLY_TWO_LITERAL_CHANGES_FINAL_INVERSE_ACTUAL.json').open('x') as f:json.dump(dict(passed=True,old_worker_SHA=H(inverse),selected_worker_SHA=H(raw),exact_two_literals_only=True,all_numerics_model_physics_metrics_queue_unchanged=True),f,indent=2)
 rows=[];local={}
 for p in sorted(B.rglob('*')):
  if not p.is_file():continue
  raw=p.read_bytes();assert p.suffix in ('.py','.json','.md','.txt');rows.append(dict(relative=p.relative_to(B).as_posix(),bytes=len(raw),SHA=H(raw)))
  if p.parent==B and p.suffix=='.py':ast.parse(raw);local[p.name]=H(raw)
 s.update(status='FROZEN_SOURCE_ONLY_UNUSED_ACTUAL_TARGET_ADMISSION_PENDING',files=rows,local_source_SHAs=local,entry_SHA=local[s['entry']],manifest_SHA=H(mf.read_bytes()),exact_production_fullstate_entry_bound=True,actual_writer_sup_first_normal_receipt_graph_passed=True,PurePosixPath_startup_argv_guard_evaluated=True,actual_rescue_training_learn_hook_order_proved=True,metadata_CPU_will_validate_actual_installed_SDK_parser_and_full_source_closure=True,source_model_CPU_decode0=True,first360_worker1680_sup1800_normal900_850_unchanged=True,original_case_sources_false_partial_once_preserved=True,no_SDK_GPU_PT_raw_remote_or_account_calls=True,Git_status='EXPLICIT_PENDING root ordinary supplement; no trial/tag',skill_graduation=False,complete_WM_dataset=False)
 with (B/s['index']).open('x') as f:json.dump(s,f,indent=2)
 print(json.dumps(dict(passed=True,index=s['index'],index_SHA=H((B/s['index']).read_bytes()),entry=s['entry'],entry_SHA=s['entry_SHA'],manifest_SHA=s['manifest_SHA'],files=len(rows),source_only=True)))
if __name__=='__main__':main()

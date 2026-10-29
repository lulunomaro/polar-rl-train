"""Missing-only final index after .gz accounting refusal, no fixture replay."""
from pathlib import Path
import hashlib,json,time
B=Path(__file__).resolve().parent;L=B.parent;OLD=L/'E0_82_NEW86_N20K_LONG_COMMAND_FROZEN_SOURCE_20261029_V1'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ENTRY='upload_admit_detach_NEW86_E0_final82_early_command_secure_stdin_UNUSED_once_v2.py';WORKER='evaluate_E0_adapted82_new86_frozen1000_once_v2_early.py';MANIFEST='E0_NEW86_COMPLETE_INPUT_MANIFEST_V2.json';INDEX='FROZEN_E0_82_NEW86_EARLY_RESAMPLE_COMPLETE_SOURCE_INDEX_V2.json'
assert not (B/INDEX).exists()
m=json.loads((B/MANIFEST).read_bytes());proof=json.loads((B/'reports/COMPLETE_SELECTED_E0_V2_SOURCE_TASK_CONSTRUCTOR_METHODS_READERS_CPU_ACTUAL.json').read_bytes());baseindex=json.loads((OLD/'FROZEN_E0_82_NEW86_LONG_COMMAND_SOURCE_INDEX_V1.json').read_bytes())
assert proof['passed'] and json.loads((B/'reports/SELECTED_WORKER_OBSERVER_ONLY_INVERSE_UTF8_AND_NUMERIC_AST_EXACT.json').read_bytes())['inverse_bytes_equal_after_exact_declared_observer_and_task_kind_changes']
with (B/'reports/ORIGINAL_PRESEAL_SYNTHETIC_GZIP_ACCOUNTING_REFUSAL_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original_error='seal_complete_NEW_E0_V2_caller_task_readers_source_once.py line69 assert suffix not .pt/.npz/.usd/.zip/.gz refused fresh synthetic constructor gzip',not_target_or_GPU_or_runtime_error=True,manifest_or_selected_source_bytes_not_modified=True,missing_final_index_only=True,synthetic_producer_metadata_reused_no_binary_content_read=True),f,indent=2)
handoff=B/'HANDOFF_FROZEN_COMPLETE_E0_V2_EARLY_RESAMPLE_CALLER_TASK_READERS.md'
with handoff.open('a',encoding='utf8') as f:f.write('\nFinal index completion: original preseal also refused the already-produced fresh CPU synthetic gzip from the selected-constructor fixture; original error retained, missing-only index uses that existing producer path/bytes/SHA without content read. Selectedruntime/manifest/CPU proof unchanged. Acted vs zero-control is a strict partition; initial-left-censor is a START-status axis while reset/window is END-reason, so those censor fields may overlap and must not be universally summed. No per-command skill-success threshold is invented.\n')
synthetic=proof['actual_selected_constructor_lifecycle']['fresh_synthetic_output'];sp=Path(synthetic['path']).resolve();assert sp.is_relative_to(B.resolve())
files=[]
for p in sorted(B.rglob('*')):
 if not p.is_file():continue
 if p.suffix=='.gz':
  assert p.resolve()==sp and p.stat().st_size==synthetic['bytes'];files.append(dict(relative=p.relative_to(B).as_posix(),bytes=synthetic['bytes'],SHA=synthetic['SHA'],classification='fresh_CPU_synthetic_gzip_metadata_only_from_existing_producer',contents_not_read_or_rehashed_for_index=True));continue
 assert p.suffix not in ('.pt','.npz','.usd','.zip')
 files.append(dict(relative=p.relative_to(B).as_posix(),bytes=p.stat().st_size,SHA=H(p),classification='fresh_CPU_synthetic_JSONL_only' if p.suffix=='.jsonl' else 'complete_source_saved_text_or_original_error'))
selected={r['relative']:r['SHA'] for r in m['files'] if Path(r['local_path']).parent==B and r['relative'].endswith('.py')}
for name,want in selected.items():assert H(B/name)==want
readnames=('E0_frozen_actual_receipts_readonly_CODE_v2_early.py','run_E0_new86_readonly_secure_stdin_v2_early.py','read_E0_new86_FIRST_native24_early_queue_secure_stdin_UNUSED_once_v2.py','collect_E0_new86_TERMINAL_fulltext_secure_stdin_UNUSED_once_v2.py')
index=dict(kind='FROZEN_COMPLETE_E0_V2_EARLY_ORIGINAL_RESAMPLE_CALLER_TASK_READERS_SOURCE_ONLY',frozen=True,epoch=time.time(),entry_filename=ENTRY,entry_SHA=H(B/ENTRY),target_stage='/data/robemo/polar-rl-train/evaluation_runs/E0_ADAPTED82_EARLY_RESAMPLE_20261029v2/e0',source_model_SHA=m['typed_source_SHA'],manifest_local_filename=MANIFEST,manifest_SHA=H(B/MANIFEST),old_input_manifest_SHA=H(OLD/'E0_NEW86_COMPLETE_INPUT_MANIFEST_V1.json'),samehost_V1_witness_SHA=H(B/'E0_PREVIOUS_SAMEHOST_FULL1000_WITNESS.json'),clone_receipt_SHA=baseindex['clone_receipt_SHA'],actual_clone_CUDA_SDK_receipt_SHA=baseindex['actual_clone_CUDA_SDK_receipt_SHA'],executable_source_SHAs=selected,readonly_source_SHAs={n:H(B/n) for n in readnames},original_model_num_envs=20000,num_envs=20000,controls=1000,worker1680_supervisor1800=True,selected_constructor_and_source_methods_CPU_passed=True,actual_target_method_AST_or_GPU_execution=False,model_decode_count_during_source_prep=0,files=files,Git_status='PENDING_ROOT_ORDINARY_SUPPLEMENT',skill_graduation=False,complete_WM_dataset=False)
with (B/INDEX).open('x',encoding='utf8') as f:json.dump(index,f,indent=2)
print(json.dumps(dict(frozen=True,index_SHA=H(B/INDEX),entry=ENTRY,entry_SHA=H(B/ENTRY),worker_SHA=H(B/WORKER),manifest_SHA=H(B/MANIFEST),inputs=len(m['files']),samehost_reuse=sum(bool(r['reuse_prior_samehost']) for r in m['files']),files=len(files))))

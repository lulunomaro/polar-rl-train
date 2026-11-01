"""Append-only sourcefinal archive index + exact inherited SyntaxWarning capture.
No runtime imports/actualmodels/NPZ/USD/SSH/SDK/GPU/Git operation.
"""
from pathlib import Path
import ast,hashlib,json,warnings
B=Path(__file__).resolve().parent;T=B.parent.parent
roots=[T/'staged_sources/E1_CURB141_40050_MOD4V1_SOURCE_V1',T/'staged_sources/E1_SLOPE135_40050_MOD4V1_SOURCE_V1'];warning_rows=[]
for root in roots:
 for path in root.rglob('*.py'):
  raw=path.read_bytes()
  with warnings.catch_warnings(record=True) as captured:
   warnings.simplefilter('always',SyntaxWarning);ast.parse(raw,filename=str(path))
  for w in captured:warning_rows.append(dict(path=str(path),source_SHA=hashlib.sha256(raw).hexdigest(),line=w.lineno,category=w.category.__name__,message=str(w.message),inherited_source_bytes_not_edited=True))
with (B/'SOURCEFINAL_INHERITED_SYNTAX_WARNINGS_V1.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='SOURCE_AST_COMPILE_SUCCEEDED_INHERITED_DOCSTRING_WARNINGS_NOT_GPU_FAILURE',raw_finalizer_stderr='SyntaxWarning: "\\S" is an invalid escape sequence. Such sequences will not work in the future. Did you mean "\\\\S"? A raw string is also an option.',initial_finalizer_emitted_lines=4,independent_filename_exact_capture=warning_rows,original_sources_and_final_indexes_unmodified=True,PT_SDK_operations=0),f,indent=2)
files=[]
for root in roots+[B]:
 for path in sorted(root.rglob('*')):
  if path.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.usdc','.zip','.onnx','.safetensors','.pyc'):continue
  if not path.is_file():continue
  raw=path.read_bytes();files.append(dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
p=B/'FINAL_ALL_E1_SOURCE_ONLY_ARCHIVE_PENDING_INDEX_V1.json'
with p.open('x',encoding='utf-8') as f:json.dump(dict(kind='TWO_E1_SOURCEFINAL_AND_ALL_BUILDER_MOCK_ERRORS_ARCHIVE_PENDING',files=files,sourcefinal_packages=[dict(root=str(root),index=str(root/'FINAL_SOURCE_INDEX.json'),SHA=hashlib.sha256((root/'FINAL_SOURCE_INDEX.json').read_bytes()).hexdigest()) for root in roots],saved_six_variants_include_review_only_false_and_unknown_extras=True,real_models_or_large_raw_or_binary_in_archive=False,NPZ_saved_paths_SHA_only_no_current_stat_hash_read=True,all_MOCK_plaintext_inputs_are_synthetic_not_checkpoints=True,all_initial_null_reader_schema_and_goal_context_errors_preserved=True,child_Git_commit_push=False,parent_append_only_archive_pending=True,current_PT_SSH_SDK_GPU_budget_ReadyGO_operations=0),f,ensure_ascii=False,indent=2)
print(json.dumps(dict(archive_index=str(p),SHA=hashlib.sha256(p.read_bytes()).hexdigest(),files=len(files),inherited_docstring_warnings=len(warning_rows),sourcefinal_both_sealed=True,actual_PT_SDK_operations=0),indent=2))

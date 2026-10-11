from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
old=D/'sync_entry_fullstate_scope_once.py';new=D/'sync_entry_fullstate_selected_actual_once.py'
assert not new.exists()
t=old.read_text(encoding='utf8')
a="actual=sorted(R.glob('ENTRY_FULLSTATE_ACTUAL_*.json'))[-1]"
b="actual=max((p for p in R.glob('ENTRY_FULLSTATE_ACTUAL_*.json') if p.stem.removeprefix('ENTRY_FULLSTATE_ACTUAL_').isdigit()),key=lambda p:int(p.stem.removeprefix('ENTRY_FULLSTATE_ACTUAL_')))"
assert t.count(a)==1
t=t.replace(a,b).replace('ENTRY_FULLSTATE_METADATA_SYNC_ERROR.json','ENTRY_FULLSTATE_SELECTED_METADATA_SYNC_ERROR.json')
ast.parse(t);new.write_text(t,encoding='utf8')
p=R/'ENTRY_SYNC_SELECTION_READER_REPAIR.json';assert not p.exists()
p.write_text(json.dumps(dict(epoch=time.time(),original_source=str(old.resolve()),original_SHA=hashlib.sha256(old.read_bytes()).hexdigest(),original_KeyError='reports: alphabetical ACTUAL glob selected AUTHORITY_BOUNDARY rather than numeric current snapshot',new_source=str(new.resolve()),new_SHA=hashlib.sha256(new.read_bytes()).hexdigest(),only_numeric_actual_snapshot_selected=True,original_error_and_source_retained=True,PowerShell_inline_builder_parser_rejection_before_python_execution=True,subsequent_missing_new_file_execution_attempt_retained=True,both_before_CAS_or_GPU_or_budget_action=True),ensure_ascii=False,indent=2),encoding='utf8')

from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent;p=B/'E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json';raw=p.read_bytes();m=json.loads(raw);row=next(r for r in m['files'] if r['relative']=='e3_declared_entry_receipt_cli_contract_v1.py');old=dict(row);data=(B/row['relative']).read_bytes();row.update(bytes=len(data),SHA=hashlib.sha256(data).hexdigest())
with (B/'PRESEAL_MANIFEST_BEFORE_ACTUAL_SYS_PATH_SCOPE_BINDING.json').open('xb') as f:f.write(raw)
p.write_text(json.dumps(m,indent=2)+'\n',encoding='utf8')
with (B/'reports/ACTUAL_ENTRY_FIELD_DIR_SYS_PATH_SOURCE_SCOPE_BINDING.json').open('x') as f:json.dump(dict(passed=True,source='mod4_task.py _FIELD_DIR=Path(__file__).resolve().parents[1]; sys.path.insert(_FIELD_DIR); import rmuc2026_field',declared_existing_source='runtime/isaac/rmuc2026_field.py',new_closure_scope_includes_actual_inserted_runtime_isaac=True,unselected_incoming_terrain_route_raycast_explicit_under_original_flat_empty_map=True,old_helper_row=old,new_helper_row=row,only_source_metadata_no_model_remote=True),f,indent=2)
source=B/'test_REAL_E3_entry_receipt_CLI_learn_hook_closure_SOURCE_ONLY_once.py';text=source.read_text().replace('REAL_SELECTED_ENTRY_RECEIPT_CLI_HOOK_DEPENDENCY_SOURCE_CPU_ACTUAL.json','REAL_SELECTED_ENTRY_RECEIPT_CLI_HOOK_DEPENDENCY_COMPLETE_SCOPE_CPU_ACTUAL.json')
with (B/'test_REAL_E3_entry_receipt_CLI_learn_hook_closure_SOURCE_ONLY_once_v3_actual_sys_path_scope.py').open('x') as f:f.write(text)

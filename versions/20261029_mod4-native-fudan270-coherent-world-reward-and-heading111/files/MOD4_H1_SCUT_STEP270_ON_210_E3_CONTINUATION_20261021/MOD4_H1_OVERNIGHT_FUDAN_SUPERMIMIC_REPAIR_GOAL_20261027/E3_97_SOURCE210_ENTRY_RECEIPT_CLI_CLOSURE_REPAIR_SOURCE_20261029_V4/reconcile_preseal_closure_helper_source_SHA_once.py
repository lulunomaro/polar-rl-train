from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent;p=B/'E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json';raw=p.read_bytes();m=json.loads(raw);name='e3_declared_entry_receipt_cli_contract_v1.py';row=next(r for r in m['files'] if r['relative']==name);old=dict(row);data=(B/name).read_bytes();row.update(bytes=len(data),SHA=hashlib.sha256(data).hexdigest())
with (B/'PRESEAL_MANIFEST_BEFORE_COMPLETE_CLOSURE_HELPER_RECONCILIATION.json').open('xb') as f:f.write(raw)
p.write_text(json.dumps(m,indent=2)+'\n',encoding='utf8')
with (B/'reports/LOCAL_INITIAL_SOURCE_CLOSURE_STALE_PRESEAL_ROW_ERROR_ACTUAL.json').open('x') as f:json.dump(dict(passed=False,original_error='declared_import_closure assert current PY SHA == sealed row SHA',phase='local source-only test; no SDK/App/model/remote',reason='Helper source expanded closure roots after preliminary manifest assembly; strict self-source verification correctly rejected stale row',old_row=old,new_row=row,only_one_own_source_metadata_row_updated=True,old_manifest_retained=True),f,indent=2)
oldtest=B/'test_REAL_E3_entry_receipt_CLI_learn_hook_closure_SOURCE_ONLY_once.py';text=oldtest.read_text()
with (B/'test_REAL_E3_entry_receipt_CLI_learn_hook_closure_SOURCE_ONLY_once_v2_manifest_bound.py').open('x') as f:f.write(text)

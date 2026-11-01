from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent;T=N.parent;S=N/'source';D=N/'draft_before_use';D.mkdir(exist_ok=False)
p=S/'authority231.py';old=p.read_text('utf8');(D/p.name).write_text(old,encoding='utf8')
assert "current['run_id']"in old
s=old.replace("current['run_id']","current['go']['w35_72']['run_id']");ast.parse(s);p.write_text(s,encoding='utf8')
R=N/'reports';j=json.loads((T/'W35_RM70_QUALIFIED_CONTINUATION_AND_LOSSLESS_EVAL_SOURCE_V227_20261101/D_BEFORE_USE_CWD_REPAIR_SOURCE/reports/ROOT227D_ORIGINAL_SOLO_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json').read_bytes())
assert 'run_id'not in j['current'] and j['current']['go']['w35_72']['run_id']=='W35_QUALIFIED343E_CONTINUE227D_20261101_0712'
report=dict(epoch=time.time(),passed=True,pre_use_original_source_preserved=str(D/p.name),actual_saved_schema='OriginalOWNER_CURRENT lacks top-levelrun_id;run_id is signedGO.w35_72.run_id. ExactfullGO equality remains required.',saved_current_schema_join_passed=True,no_model_raw_remote_GPU_calls=True,source_AST=True,additional_source_locator_error='LOCALread of V2root/INSTALL_SOURCE_V2.json returnedFileNotFound before execution;actualfile discovered underreports by rg;no remote purpose consumed.')
(R/'ROOT231_PRE_USE_ORIGINAL_CURRENT_SCHEMA_AND_SOURCE_PATH_REVIEW.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))

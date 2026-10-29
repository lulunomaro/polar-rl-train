from pathlib import Path
import ast,json
C=Path(__file__).resolve().parent;p=C/'test_BOTH_actual_selected_constructors_and_ground_source_CPU_once.py';raw=p.read_bytes();text=raw.decode()
old="files=list(D.glob('*readonly_CODE*.py'));assert len(files)==1"
new="files=[D/('E2_frozen_actual_receipts_readonly_CODE_v4.py' if role=='E2' else 'E3_source210_actual_receipts_readonly_CODE_v3.py')];assert files[0].is_file()"
assert text.count(old)==1;text=text.replace(old,new)
old="cpu=next(D.glob('*target*metadata_admission*.py'))";new="cpu=D/('E2_new86_target_source_SDK_metadata_admission_v1.py' if role=='E2' else 'E3_source210_target_source_SDK_metadata_admission_v1.py')";assert text.count(old)==1;text=text.replace(old,new)
text=text.replace("'ACTUAL_SELECTED_CONSTRUCTOR_API_FIXTURE'","'ACTUAL_SELECTED_CONSTRUCTOR_API_FIXTURE_V2'") if False else text.replace("'_ACTUAL_SELECTED_CONSTRUCTOR_API_FIXTURE'","'_ACTUAL_SELECTED_CONSTRUCTOR_API_FIXTURE_V2'")
ast.parse(text)
with (C/'test_BOTH_actual_selected_constructors_and_ground_source_CPU_once_v2_exact_paths.py').open('xb') as f:f.write(text.encode())
with (C/'reports/LOCAL_V1_READER_FILE_GLOB_ASSERTION_REPAIR_METADATA.json').open('x') as f:json.dump(dict(phase='after E2 actual selected constructor/API fixture completed; before its report/reader checks',original_error='AssertionError len(files)==1 from local venv Windows long-path Path.glob',selected_test_only_delta='explicit exact selected CODE/CPU basenames, fresh fixture output namespace V2',target_selected_sources_unchanged=True,no_oldmodel_SDK_GPU_remote=True),f,indent=2)

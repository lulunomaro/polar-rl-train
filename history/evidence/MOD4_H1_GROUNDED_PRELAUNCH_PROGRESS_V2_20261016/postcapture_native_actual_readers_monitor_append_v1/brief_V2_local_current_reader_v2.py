"""Local-only corrected brief; never contacts hosts or changes runtime."""
from pathlib import Path
import json,time
D=Path(__file__).resolve().parent
failure=D/'reports/V2_LOCAL_BRIEF_UNMATCHED_PAREN_READER_ORIGINAL_ERROR_ACTUAL.json'
if not failure.exists():
 failure.write_text(json.dumps(dict(epoch=time.time(),original_attempt='Local Python -c compact GO/STARTUP/errors brief ended with one extra closing parenthesis after print(json.dumps(dict(...))))',original_error="SyntaxError: unmatched ')'",original_CPU_script_not_parsed_no_runtime_or_network_or_GPU_effect=True,independent_reader_only_correction='Separate parsed script removes the extra final parenthesis; underlying source data/runtime unchanged'),indent=2),encoding='utf8')
v=json.loads((D/'reports/V2_NATIVE_CPU_FIRST_IMMUTABLE_LOCAL_CURRENT_ACTUAL.json').read_bytes())
print(json.dumps(dict(epoch=v['epoch'],GO=[x for x in v['files'] if x['path'].endswith('/GO_PRODUCTION.json')],startup=[x for x in v['files'] if x['path'].endswith('/production/STARTUP_H1_SOURCE_ACTUAL.json')],errors=[x for x in v['files'] if 'ERROR' in x['path']])))

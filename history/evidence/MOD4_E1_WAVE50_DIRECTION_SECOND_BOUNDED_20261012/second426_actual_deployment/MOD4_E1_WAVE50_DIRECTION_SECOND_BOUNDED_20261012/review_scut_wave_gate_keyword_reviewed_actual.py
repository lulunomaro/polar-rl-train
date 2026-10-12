"""Continue only the unexecuted source review after a pre-execution keyword syntax refusal."""
from pathlib import Path
import json,time,hashlib
D=Path(__file__).resolve().parent;original=D/'review_scut_wave_gate_actual.py';raw=original.read_bytes()
p=D/'reports/SCUT_GATE_PREEXEC_KEYWORD_SYNTAX_REJECTION.json'
if not p.exists():
    p.write_bytes(json.dumps(dict(epoch=time.time(),original_source=str(original),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),error='SyntaxError: invalid decimal literal; dict keyword started with 15s at line32',rejected_before_import_report_write_GPU_or_budget=True,independent_continuation_only_unexecuted_review=True),indent=2).encode())
s=raw.decode('utf8');assert s.count('15s_at_03_command_is_project_test_not_SCUT_standard=')==1
s=s.replace('15s_at_03_command_is_project_test_not_SCUT_standard=','window15s_at_03_command_is_project_test_not_SCUT_standard=')
exec(compile(s,'<SCUT-gate-keyword-reviewed-readonly>','exec'),dict(__file__=__file__,__name__='__main__'))

"""Independent filename-normalization repair; the first preparer stays unchanged."""
from pathlib import Path
import json
import time

B = Path(__file__).resolve().parent
old = B / 'preserve_tested_v1_and_stage_backend_guard_v2.py'
source = old.read_text(encoding='utf8')
anchor = "expected = report['source_sha']['payload_v1/birth_bodyframe_reset_adapter_v1.py']"
replacement = "expected = {k.replace(chr(92), '/'): v for k, v in report['source_sha'].items()}['payload_v1/birth_bodyframe_reset_adapter_v1.py']"
assert source.count(anchor) == 1
# Execute the independent reader as a new source artifact. The original failed
# preparer is not rewritten or re-run.
fixed = B / 'preserve_tested_v1_backend_v2_exact_normalized_actual.py'
assert not fixed.exists()
fixed.write_text(source.replace(anchor, replacement), encoding='utf8')
error = B / 'reports/SOURCE_VERSION_PREPARER_ORIGINAL_READER_ERRORS.json'
assert not error.exists()
error.write_text(json.dumps(dict(epoch=time.time(),
    original_inline_shell_error='SyntaxError: parenthesis was never closed before file mutation',
    original_saved_preparer=str(old),
    original_saved_preparer_error="KeyError: payload_v1/birth_bodyframe_reset_adapter_v1.py (Windows report uses backslash separators)",
    original_preparer_failed_before_any_mutation=True,
    independent_fix='Normalize relative metadata path separators only; exact source bytes and expected SHA stay authoritative',
    no_GPU_PPO_budget_or_original_trial_repeat=True), indent=2), encoding='utf8')
exec(compile(fixed.read_bytes(), str(fixed), 'exec'), dict(__file__=str(fixed), __name__='__main__'))

"""Keep the exact tested version; stage the stronger backend guard separately."""
from pathlib import Path
import hashlib
import json
import time

B = Path(__file__).resolve().parent
f = B / 'payload_v1/birth_bodyframe_reset_adapter_v1.py'
current = f.read_bytes()
old = current.replace(
    b"    assert proof['native_setter_readback_required'] is True\n    assert proof['independent_xyzw_heading_witness_verified'] is True",
    b"    assert proof['native_setter_selected_rows_exact'] is True")
report = json.loads((B / 'reports/BODYFRAME_WHOLE20K_RESET_COMMAND_SAVE_CHAIN_CPU_ACTUAL.json').read_bytes())
expected = report['source_sha']['payload_v1/birth_bodyframe_reset_adapter_v1.py']
assert hashlib.sha256(old).hexdigest() == expected
v2 = f.with_name('birth_bodyframe_reset_adapter_v2.py')
assert not v2.exists()
v2.write_bytes(current)
f.write_bytes(old)
ck = B / 'payload_v1/birth_bodyframe_full_checkpoint_v1.py'
ck.write_bytes(ck.read_bytes().replace(b'from birth_bodyframe_reset_adapter_v1 import',
                                     b'from birth_bodyframe_reset_adapter_v2 import'))
output = B / 'reports/BACKEND_GUARD_V2_SOURCE_VERSION_ACTUAL.json'
assert not output.exists()
output.write_text(json.dumps(dict(epoch=time.time(), original_tested_v1_source_restored_to_exact_report_SHA=expected,
    new_v2_SHA=hashlib.sha256(current).hexdigest(),
    reason='Pre-placement getter+xyzw heading verification and required setter witness are separate from actual post-placement getter verification. Do not claim a setter result in advance.',
    v1_original_CPU_trial_not_repeated=True, new_v2_CPU_and_GPU_admission_pending=True,
    prior_inline_PowerShell_quoting_error='SyntaxError: parenthesis was never closed, before any file mutation; independent saved Python script used to avoid shell quoting.',
    no_GPU_or_PPO_or_budget=True), indent=2), encoding='utf8')
print(json.dumps(dict(v1_SHA_exact=True, new_v2_SHA=hashlib.sha256(current).hexdigest())))

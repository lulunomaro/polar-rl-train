"""Retain original compile rejection; repair only the unexecuted new worker."""
from pathlib import Path
import hashlib
import json
import time

B = Path(__file__).resolve().parent; P = B / 'payload_v1'
old = P / 'bodyframe_native_worker_v1.py'
source = old.read_bytes()
try:
    compile(source, str(old), 'exec')
except SyntaxError as exc:
    error = dict(message=str(exc), lineno=exc.lineno, offset=exc.offset, text=exc.text)
else:
    raise AssertionError('Original compile rejection is not present')
before = b"qualified50=False, formal_learning_admitted=False)), indent=2), encoding='utf8')"
after = b"qualified50=False, formal_learning_admitted=False), indent=2), encoding='utf8')"
assert source.count(before) == 1
new = P / 'bodyframe_native_worker_v2.py'
assert not new.exists()
new.write_bytes(source.replace(before, after))
compile(new.read_bytes(), str(new), 'exec')
original_preparer = B / 'prepare_native_template_and_next_work_order_CPU.py'
preparer = original_preparer.read_text(encoding='utf8')
preparer = preparer.replace("for p in P.glob('*.py'):", "for p in P.glob('*.py'):\n    if p.name == 'bodyframe_native_worker_v1.py':\n        continue")
preparer = preparer.replace("(P / 'bodyframe_native_worker_v1.py')", "(P / 'bodyframe_native_worker_v2.py')")
fixed = B / 'prepare_native_template_and_next_work_order_CPU_v2.py'
assert not fixed.exists(); fixed.write_text(preparer, encoding='utf8')
receipt = B / 'reports/NATIVE_WORKER_V1_COMPILE_REJECTION_V2_PREPARED_ACTUAL.json'
assert not receipt.exists()
receipt.write_text(json.dumps(dict(epoch=time.time(), original_compile_error=error,
    original_source=str(old), original_SHA=hashlib.sha256(source).hexdigest(),
    independent_fixed_source=str(new), independent_SHA=hashlib.sha256(new.read_bytes()).hexdigest(),
    only_fix='Remove one unmatched closing parenthesis in COMPLETE JSON write',
    fixed_compile_passed=True, no_remote_target_or_GPU_PPO_budget_action=True,
    original_preparer_not_rerun=True, original_source_preserved=True), indent=2), encoding='utf8')
exec(compile(fixed.read_bytes(), str(fixed), 'exec'), dict(__file__=str(fixed), __name__='__main__'))

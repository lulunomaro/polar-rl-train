"""Stage independent native-array bridge versions; preserve all tested sources."""
from pathlib import Path
import hashlib
import json
import time

B = Path(__file__).resolve().parent; P = B / 'payload_v1'
old = P / 'birth_bodyframe_reset_adapter_v2.py'; new = P / 'birth_bodyframe_reset_adapter_v3.py'
assert not new.exists()
raw = old.read_text(encoding='utf8')
anchor = "def tensor(v):\n    return v.torch if hasattr(v, 'torch') else v"
replace = "def tensor(v):\n    if isinstance(v, torch.Tensor): return v\n    if hasattr(v, 'torch'): return v.torch\n    import warp as wp\n    return wp.to_torch(v)"
assert raw.count(anchor) == 1
new.write_text(raw.replace(anchor, replace), encoding='utf8')
oldck = P / 'birth_bodyframe_full_checkpoint_v1.py'; newck = P / 'birth_bodyframe_full_checkpoint_v2.py'
assert not newck.exists()
newck.write_bytes(oldck.read_bytes().replace(b'from birth_bodyframe_reset_adapter_v2 import', b'from birth_bodyframe_reset_adapter_v3 import'))
oldworker = P / 'bodyframe_native_worker_v2.py'; newworker = P / 'bodyframe_native_worker_v3.py'
assert not newworker.exists()
newworker.write_bytes(oldworker.read_bytes().replace(b'from birth_bodyframe_full_checkpoint_v1 import', b'from birth_bodyframe_full_checkpoint_v2 import'))
for p in (new, newck, newworker): compile(p.read_bytes(), str(p), 'exec')
receipt = B / 'reports/LINUX_ACTIVE_NATIVE_ARRAY_BRIDGE_V3_PREPARED.json'
assert not receipt.exists()
receipt.write_text(json.dumps(dict(epoch=time.time(), reason='Actual native view may return Warp array rather than Torch or SDK Tensor; use identity conversion only, no installed package edit',
    no_RL_reset_command_math_change=True, old_sources_preserved=True,
    active_files={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (new, newck, newworker)},
    new_GPU_or_PPO_started=False), indent=2), encoding='utf8')
print(json.dumps(dict(active_v3_compiled=True)))

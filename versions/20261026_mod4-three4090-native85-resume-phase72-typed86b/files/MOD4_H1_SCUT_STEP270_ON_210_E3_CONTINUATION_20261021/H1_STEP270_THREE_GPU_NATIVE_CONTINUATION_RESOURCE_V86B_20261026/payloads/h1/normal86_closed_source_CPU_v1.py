"""Normal86 ready loader; preserves the original node import and ready kinds."""
from pathlib import Path
import hashlib
import json


def load(spec, B):
    from normal86_source_guard_v1 import check_payload, read_bound_metadata, validate_origin, ready_value, H, read, exact_worker_delta
    B=Path(B);key=spec['key'];check_payload(B,key,spec)
    binding,data=read_bound_metadata(B);validate_origin(binding,data)
    # Prefix preservation and exact inventory pin all original runtime, assets,
    # trace, physical guards and save/reset chain. Worker delta is also decoded
    # independently, never allowed by a directory-wide exception.
    old_name='h1_step270_production_worker_v1.py' if key=='h1' else 'recovery_worker.py'
    contract=read(B/'NORMAL86_SOURCE_CONTRACT_ACTUAL.json')
    reference=bytes.fromhex(contract['original_worker_utf8_hex']).decode('utf8')
    exact_worker_delta(reference,(B/old_name).read_text('utf8'),key)
    fresh=read(B/'NORMAL86_INSTALLED_SOURCE_SDK_CPU_ADMITTED_ACTUAL.json')
    value=ready_value(spec,fresh,H(B/'NORMAL86_SOURCE_BINDING_ACTUAL.json'))
    return dict(value=value,SHA=hashlib.sha256(json.dumps(value,indent=2).encode()).hexdigest(),
        actual_CPU_waited_EXIT0=True,fresh_installed_CPU_report_SHA=H(B/'NORMAL86_INSTALLED_SOURCE_SDK_CPU_ADMITTED_ACTUAL.json'))

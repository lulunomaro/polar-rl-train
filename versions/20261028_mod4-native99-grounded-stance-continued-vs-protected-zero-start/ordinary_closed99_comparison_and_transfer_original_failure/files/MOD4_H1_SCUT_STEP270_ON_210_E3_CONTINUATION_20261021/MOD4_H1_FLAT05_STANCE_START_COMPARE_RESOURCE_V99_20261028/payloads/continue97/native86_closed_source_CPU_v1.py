"""Consume fresh installed86 CPU receipts under a typed native role; no training."""
from pathlib import Path
import hashlib
import json


def load(spec, B):
    from native86_source_guard_v1 import check_payload, ready_value, read, H
    from native_continuation_v1 import read_pinned_metadata_bundle, admit_closed_source
    B = Path(B)
    check_payload(B, spec)
    binding, metadata = read_pinned_metadata_bundle(B / 'NATIVE_CONTINUATION_BINDING_ACTUAL.json')
    for name in ('reference_artifact_SHA', 'adapter_CPU_report_SHA', 'objective_contract_SHA'):
        assert spec[name] == binding['producer'][name], 'Native learned source lineage differs: ' + name
    # Closure metadata remains old85 original truth. This is not a new physical
    # readback; the bridge compares fresh30 ordered names before learning.
    admit_closed_source(binding, current_runtime_order=metadata['runtime_order'],
        current_runtime_objective=read(B / 'native_source_metadata/NATIVE85M2_RUNTIME_OBJECTIVE_CONTRACT_ACTUAL.json'), **metadata)
    sdk = read(B / 'TARGET_NATIVE86_SOURCE_SDK_CPU_ADMITTED_ACTUAL.json')
    unit = read(B / 'reports/NATIVE_H1_FUDAN_REFERENCE_INSTALLED_CPU_V86_ACTUAL.json')
    contract = read(B / 'NATIVE86_SOURCE_CONTRACT_ACTUAL.json')
    value = ready_value(spec, sdk, unit, contract)
    return dict(value=value, SHA=hashlib.sha256(json.dumps(value, indent=2).encode()).hexdigest(),
                actual_CPU_waited_EXIT0=True,
                fresh_SDK_CPU_report_SHA=H(B / 'TARGET_NATIVE86_SOURCE_SDK_CPU_ADMITTED_ACTUAL.json'),
                fresh_reference_CPU_report_SHA=H(B / 'reports/NATIVE_H1_FUDAN_REFERENCE_INSTALLED_CPU_V86_ACTUAL.json'))

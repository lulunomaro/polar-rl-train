"""Preserve CPUv1 exact source bytes from the known final-only anchor delta."""
from pathlib import Path
import hashlib
import json
P = Path(__file__).resolve().parent
raw = (P / 'temporary_state_binding.py').read_bytes()
text = raw.decode()
block = """    assert type(b['CPU_prepared_only']) is bool and type(b['actual_runtime_metadata_bound']) is bool
    assert b['CPU_prepared_only'] is not b['actual_runtime_metadata_bound']
    if b['actual_runtime_metadata_bound']:
        assert set(b['bound_Linux_runtime_metadata']) == set(STATES)
        for state in STATES:
            assert same(_metadata(ck[state]), b['bound_Linux_runtime_metadata'][state]), (state, 'Bound Linux metadata anchor')
"""
assert text.count(block) == 1
text = text.replace(block, '')
new = """                    approved_code_binding_changes=changes, code_binding_profile='linux_Sim6_Lab6_once_v1',
                    bound_Linux_runtime_metadata={state: copy.deepcopy(_metadata(out[state])) for state in STATES})"""
old = "                    approved_code_binding_changes=changes, code_binding_profile='linux_Sim6_Lab6_once_v1')"
assert text.count(new) == 1
restored = text.replace(new, old).encode()
sha = hashlib.sha256(restored).hexdigest()
assert sha == '1ded790db51df4857ff786dff5d4cebd91a6fec38a1d1aed089fdfbe4aea5847'
p = P / 'temporary_state_binding_CPU_v1_original_preserved.py'
assert not p.exists()
p.write_bytes(restored)
r = dict(path=str(p), bytes=p.stat().st_size, sha256=sha,
         exact_source_bytes_match_saved_CPU_v1_manifest=True,
         recovered_from_exact_final_delta_no_experiment_rerun=True,
         original_prewrite_rejections=[
             'Root updated payload_v2 to final587e before read: old1ded assert refused before write',
             'Inline PowerShell quoting ParserError before Python execution: no filesystem mutation'])
q = P / 'CPU_V1_SOURCE_PRESERVATION_ACTUAL.json'
assert not q.exists()
q.write_text(json.dumps(r, indent=2))
print(json.dumps(r))

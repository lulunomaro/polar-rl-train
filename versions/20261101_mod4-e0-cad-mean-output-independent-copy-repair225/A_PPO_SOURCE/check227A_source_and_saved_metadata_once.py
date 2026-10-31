"""New227A AST + selected saved JSON identity join only; no runtime imports."""
from pathlib import Path
import ast
import hashlib
import json
import time
import traceback

A = Path(__file__).resolve().parent
T = A.parent.parent


def put(p, v):
    with p.open('x', encoding='utf8') as f:
        json.dump(v, f, indent=2, allow_nan=False)


def main():
    purpose = json.loads((A/'reports/CPU227A_PURPOSE_FROZEN.json').read_bytes())
    put(A/'reports/CPU227A_ONCE_CONSUMED.json', dict(epoch=time.time(), ID=purpose['ID']))
    for r in purpose['sources']:
        raw = Path(r['path']).read_bytes()
        assert len(raw) == r['bytes'] and hashlib.sha256(raw).hexdigest() == r['SHA']
        ast.parse(raw, filename=r['path'])
    from contract227 import metadata, qualified, SHA, ITER, ADAM, LR
    P = T/'W35_SOLO_INSTALL_FIRST_AND_CLOSED_READERS_SOURCE_V219_20261101/reports'
    closing, cr = metadata(P/'ROOT219V3_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
    cpu, qr = metadata(P/'ROOT219V3_NEW_W35_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json')
    q = qualified(closing, cpu, qr['SHA'])
    # Receipt truth is read from saved metadata; no model bytes are touched.
    assert (q['source_SHA'], q['source_iteration'], q['source_Adam_step'], q['source_LR']) == (SHA, ITER, ADAM, LR)
    put(A/'reports/CPU227A_SOURCE_AND_QUALIFIED_JOIN_ACTUAL.json', dict(passed=True,
        ID=purpose['ID'], source_AST_count=len(purpose['sources']), saved_JSON_reads=2,
        selected_qualified_source=q, saved_reports=[cr,qr],
        first_expected_iteration=32405, first_expected_Adam17=649740,
        first_expected_new_transitions=480000, old_fixtures_replayed=0,
        PT_NPZ_USD_raw_Torch_SDK_GPU_SSH_Git_calls=0,
        actual_runtime_training_or_skill_test=False))


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        put(A/'reports/CPU227A_ORIGINAL_ERROR.json', dict(passed=False, error=traceback.format_exc()))
        raise

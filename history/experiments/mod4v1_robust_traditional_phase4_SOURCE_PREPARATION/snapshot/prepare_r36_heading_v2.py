"""New R36 source version and zero-physics serialization/prefix preflight.
R35 source and its four lost postprocessing outcomes remain unchanged.
"""
from pathlib import Path
import ast
import argparse
import hashlib
import json
import tempfile
import numpy as np
from physics_bridge import ROOT, load_gain
from sensor_core_v4 import Estimate
from streamed_trace_rows_v1 import StreamedRows, scalar_default

parser = argparse.ArgumentParser()
parser.add_argument('--receipt-dir', required=True, type=Path)
args = parser.parse_args()
D = args.receipt_dir.resolve()
D.mkdir(parents=True, exist_ok=False)

def fresh(path, content):
    with path.open('x', encoding='utf-8', newline='\n') as f:
        f.write(content)

def receipt(path, value):
    fresh(path, json.dumps(value, indent=2, allow_nan=False, default=scalar_default))

s = (ROOT/'heading_hold_controller_v1.py').read_text(encoding='utf-8')
old = 'active = abs(yaw_rate) < 1e-6 and abs(x[8]) < 2.'
assert s.count(old) == 1
s = s.replace(old, 'active = bool(abs(yaw_rate) < 1e-6 and abs(x[8]) < 2.)')
s = '"""R36: only native-bool log serialization repair; same control equations."""\n' + s
ast.parse(s)
fresh(ROOT/'heading_hold_controller_v2.py', s)

s = (ROOT/'run_heading_hold_case_v1.py').read_text(encoding='utf-8')
s = s.replace('heading_hold_controller_v1', 'heading_hold_controller_v2')
s = s.replace('from sensor_core_v4 import StateEstimator,Estimate,wrap',
              'from sensor_core_v4 import StateEstimator,Estimate,wrap\nfrom streamed_trace_rows_v1 import StreamedRows,scalar_default')
assert s.count('started=time.perf_counter();rows=[];') == 1
s = s.replace('started=time.perf_counter();rows=[];',
              "started=time.perf_counter();rows=StreamedRows(out/'trace.jsonl');")
s = s.replace("ROOT/'heading_hold_controller_v2.py',", "ROOT/'heading_hold_controller_v2.py',ROOT/'streamed_trace_rows_v1.py',")
s = s.replace('json.dump(v,f,indent=2,allow_nan=False)',
              'json.dump(v,f,indent=2,allow_nan=False,default=scalar_default)')
lines = s.splitlines(keepends=True)
i = next(i for i, line in enumerate(lines) if line.lstrip().startswith("with(out/'trace.jsonl').open('xb')"))
assert lines[i+1].lstrip().startswith('for row in rows:')
assert 'trace_hash.update(raw)' in lines[i+2]
del lines[i:i+3]
s = ''.join(lines)
s = s.replace("'bytes':trace_bytes,'SHA':trace_hash.hexdigest()",
              "'bytes':rows.bytes,'SHA':rows.sha.hexdigest()")
s = s.replace("'producer_streamed_once':True", "'producer_streamed_once':True,'persisted_before_memory':True")
lines = s.splitlines(keepends=True)
i = next(i for i, line in enumerate(lines) if line.lstrip().startswith("with(out/'partial_trace.jsonl')"))
assert lines[i+1].lstrip().startswith('for rr in rows:')
assert lines[i+2].lstrip().startswith("dump(out/'ERROR.json'")
lines[i:i+3] = ["   dump(out/'ERROR.json',dict(error=error,persisted_rows=len(rows),physics_callbacks=p.tick_phys if p is not None else None,trace_path=str(rows.path),trace_prefix_SHA=rows.sha.hexdigest(),trace_prefix_bytes=rows.bytes,no_samepurpose_retry=True));raise\n"]
s = ''.join(lines)
s = s.replace("truth_mode=cfg.get('feedback','sensors')=='truth_diagnostic';", "truth_mode=cfg.get('feedback','sensors')=='truth_diagnostic';assert not truth_mode,'R36 sensor-only';")
s = s.replace("NEW_PYTHON_outerheading_TRAIN_notC_H4_or_hardware", "R36_NEW_PYTHON_heading_TRAIN_streamed_notC_H4_or_hardware")
ast.parse(s)
fresh(ROOT/'run_heading_hold_case_v2.py', s)

from heading_hold_controller_v2 import GroundController
checks = 0
def check(condition):
    global checks
    checks += 1
    assert condition, checks

g = load_gain(ROOT/'nominal_gain_v1.json')
for k in (0., 2., 4.):
    c = GroundController(g, dict(position_weight=25., position_leash=1., heading_hold_k=k))
    x = np.r_[g['q'], np.zeros(7)]
    x[:3] = 0.
    e = Estimate(x, 0., np.zeros(3), np.array([0.,0.,9.81]), 0., np.zeros(2), 0., 0., 0., 1.)
    c.command(e, 0., 0.)
    check(type(c.heading_log['active']) is bool)
    check(json.loads(json.dumps(c.heading_log, default=scalar_default))['active'] is True)
    e.state14[1] = .1
    c.command(e, 0., 0.)
    check(abs(c.heading_log['correction_rad_s'] + .1*k) < 1e-12)
    check(c.heading_log['world_position_used'] is False)
    c.command(e, 0., 1.)
    check(c.heading_log['active'] is False)
    check(c.heading_log['correction_rad_s'] == 0.)
    e.sensor_age_s = float('nan')
    check(np.array_equal(c.command(e, 0., 0.), np.zeros(6)))
    check(json.loads(json.dumps(c.heading_log))['reason'] == 'invalid_estimate')

rows = StreamedRows(D/'prefix_test.jsonl')
rows.append(dict(heading_control=dict(active=np.bool_(True)), n=np.int64(7), x=np.float32(.25)))
check(len(rows) == 1)
check(json.loads(rows.path.read_text()) == dict(heading_control=dict(active=True), n=7, x=.25))
check(rows.sha.hexdigest() == hashlib.sha256(rows.path.read_bytes()).hexdigest())
check(rows.bytes == rows.path.stat().st_size)
for invalid in (dict(x=float('nan')), dict(x=object())):
    saved = (rows.bytes, rows.sha.hexdigest(), rows.path.read_bytes())
    try:
        rows.append(invalid)
    except (ValueError, TypeError):
        pass
    else:
        raise AssertionError('invalid trace field accepted')
    check(len(rows) == 1)
    check(saved == (rows.bytes, rows.sha.hexdigest(), rows.path.read_bytes()))
receipt(D/'EXPECTED_PREFIX_ABORT.json', dict(persisted_rows=len(rows), trace_prefix_SHA=rows.sha.hexdigest(), trace_prefix_bytes=rows.bytes, expected_injected_software_error=True, physics_steps=0))

failed = []
for seed in (0, 201, 202, 203):
    out = ROOT/'results'/f'r35_heading_k0_{seed}'
    check(out.exists())
    check(not (out/'result.json').exists())
    failed.append(dict(case=out.name, classification='POSTPHYSICS_TRACE_SERIALIZATION_ERROR_NOT_ROBOT_SCORE', controls_verified=None, physics_callbacks_verified=None, configured_physics_upper_bound=24000, no_replay_for_bookkeeping=True))
receipt(D/'R35_FAILURE_REFERENCE.json', dict(rows=failed, source_logs=str(ROOT/'batches/r35_heading27'), only_failed_control_configuration_was_baseline_k0=True, unstarted_gain2_and_gain4=True))
sources = []
for path in (Path(__file__), ROOT/'heading_hold_controller_v2.py', ROOT/'run_heading_hold_case_v2.py', ROOT/'streamed_trace_rows_v1.py'):
    raw = path.read_bytes()
    sources.append(dict(path=str(path), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest()))
receipt(D/'PRECHECK_RESULT.json', dict(checks=checks, failures=0, physics_steps=0, runner_ast_ok=True, prefix_survives_type_and_nonfinite_errors=True, sources=sources))
print(json.dumps(dict(checks=checks, failures=0, physics_steps=0, status='R36_READY')))

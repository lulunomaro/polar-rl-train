"""Freeze NEW268 source/purpose metadata. This preparation imports no Torch."""
from pathlib import Path
import ast
import hashlib
import json
import time

N = Path(__file__).resolve().parent
T = N.parent
R = N / 'reports'
S255 = T / 'D435I_SUPERMIMIC_NATIVE_WM50_CONTEXT40_SOURCE_V255_20261101'
S259 = T / 'FUDAN_LITERAL_SUPERMIMIC_REWARD_MEMORY_SOURCE_V259_20261101'
native = T / 'MOD4_H1_MATLAB_REFERENCE_IMAGINATION_TRACKING_RESOURCE_V165_20261030/payloads_v2/seed27/source'
literal = T / 'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package'
refs = [S255 / 'native_depth_world_model50_v255.py',
        S255 / 'INDEX255_NATIVE_DEPTH_WM50_SOURCE_FROZEN.json',
        S259 / 'literal_imagination259.py',
        S259 / 'INDEX259_LITERAL_IMAGINATION_SOURCE_FROZEN.json',
        native / 'supermimic_wheel_leg_v3/augmented_wheel_leg_world_model_v1.py',
        native / 'supermimic_wheel_leg_v3/geometry.py',
        native / 'supermimic_wheel_leg_v3/networks.py',
        native / 'supermimic_wheel_leg_v3/replay.py',
        native / 'compact_episode_static31_v1.py',
        native / 'static_dynamic_delay_contract_v1.py',
        native / 'native_wheel_leg_bridge_v4.py',
        literal / 'jump194_sdk.py', literal / 'jump194_boundary.py',
        literal / 'mod4_literal_math184_v2.py',
        literal / 'literal_original_methods.py', literal / 'literal_original_config.py']


def row(path):
    data = path.read_bytes()
    return dict(path=str(path), bytes=len(data), SHA=hashlib.sha256(data).hexdigest())


def write(path, value):
    with path.open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2, allow_nan=False)


# Execute ONLY the pure literal schema function, extracted from the source AST.
# This avoids importing its tensor module during source/purpose preparation.
source = (N / 'measured_state224_v268.py').read_text(encoding='utf8')
tree = ast.parse(source)
schema_function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'schema_metadata')
scope = dict(SCHEMA_ID='OWN_MOD4_PHYSICAL73_AUX151_MEASURED224_V268', FORCE_SCALE_N=400.)
exec(compile(ast.Module(body=[schema_function], type_ignores=[]), '<pure268_schema>', 'exec'), scope)
write(N / 'SCHEMA268_MEASURED224_AUX151.json', scope['schema_metadata']())
write(N / 'SOURCE268_PINNED_REFERENCE_BINDINGS.json', dict(
    epoch=time.time(), kind='SOURCE_ONLY_PINNED_REFERENCE_JOIN_NOT_TARGET_ADMISSION',
    references=[row(p) for p in refs], original255_259_mutations=0,
    imports=dict(source255_directory=str(S255), source259_directory=str(S259), native_source_directory=str(native)),
    derivation=dict(native_SE3='unchanged augmented native step/targets/state_error',
        base127='native bridge env-local position, SDK xyzw->native wxyz, physical73 + contact18/applied_torque30/old_processed6',
        own_L0_theta='actual own_virtual_legs v2 branch; measured labels required',
        force='WORLD contact sensor31 in robot.body_names order -> R^T force / fixed400N',
        motor_efforts='existing applied_torque30 at packed91:121; named measured motor ID selection only'),
    actual267_finished_assumed=False, actual_metadata_GPU_model_read_admission=False))
source_files = sorted(N.glob('*.py')) + [N / 'SCHEMA268_MEASURED224_AUX151.json', N / 'SOURCE268_PINNED_REFERENCE_BINDINGS.json']
write(R / 'FROZEN268_NEW_MEASURED224_SYNTHETIC_CPU_PURPOSE.json', dict(
    purpose_ID='NEW268_MEASURED224_AUX151_NATIVE_WM50_H32_SYNTHETIC_CPU_ONCE', epoch=time.time(),
    source_files=[row(p) for p in source_files],
    source255_directory=str(S255), source259_directory=str(S259), native_source_directory=str(native),
    exact_counts=dict(fixture_runs=1, synthetic_envs=2, controls=32, pairs=64,
        supervised_synthetic_WM_optimizer_updates=1, Pi_optimizer_updates=0,
        actual_model_raw_asset_reads=0, actual_SDK_GPU_remote_calls=0,
        original255_259_fixture_runs=0, checkpoint_serializations=0),
    purposes=['new224/aux151 layout roundtrip and no missing measurement fallback',
        'native SE3/loss/replay inheritance with unchanged context40',
        'predicted original frame: WORLD forces from BODY, named existing efforts, currentBODY position difference',
        'reject legacy127, wrong binding/clock/shape/nonfinite and unavailable future depth policy context',
        'one64pair synthetic H32 supervised WM-only update; not actual learning'],
    context_boundary='Later measured depth9 is supervised WM replay context ONLY; Pi anchor-belief context remains EXPLICIT_PENDING',
    synthetic_only=True, no_skill_or_runtime_qualification=True))
print(json.dumps(dict(purpose_frozen=True, source_files=len(source_files), reference_files=len(refs),
                      Torch_SDK_GPU_model_raw_import_or_reads=0)))

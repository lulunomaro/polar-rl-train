"""Injection-only materialized-volume function, never a native-size guarantee.
Old complete fixtures run once each ONLY when parent explicitly invokes this API.
No loader, payload output, module mutation, native entry or reader-cap change.
"""
from pathlib import Path
import hashlib
import json
import random
import sys

LIMIT = 64 * 1024 * 1024
SOURCE_PINS = {
    'b4_fixture': (28309, '027d478f1d58d8a862d9077b18f2f42717486cc2d56b8ad91e8c64a8ee73d607'),
    'c2_fixture': (14088, 'b43c4bc2b8790b4bafc05eefb33063047ba6c17173a8c12b9944e16de417f3cc'),
    'worker': (20227, '448929f7574eea90a323935684b67501927896de10f6518987c4ad783898f941'),
    'parent': (9336, 'd5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41'),
    'contract': (10906, 'cc85300dfe62fbb33bb7c072b2adbc40d865c08ac45df663425ca658bd74e0a3'),
    'observer': (16708, '944c6e0cbc91e881c8c205bc78ee3b1aecf8ade877b7b97711dd6acebe93569e'),
    'runtime': (19099, '5495edd4704f67bd77226e895d33cdd4d96c0c51621b962e95e2af1a23431faa'),
    'codec': (22318, '77c007fb0b17088b54bb0c115913159c7a9bf99f50f29a0b203dea483f0d1ee4'),
    'passive': (37157, 'ddead70de7cb1e01acc79899320c0aaadd9c217cd7ba35e9e9f4a00f03c54745'),
}

def _source_digest(paths):
    assert set(paths) == set(SOURCE_PINS)
    for key, pin in SOURCE_PINS.items():
        assert Path(paths[key]).suffix == '.py'
        raw = Path(paths[key]).read_bytes()
        assert (len(raw), hashlib.sha256(raw).hexdigest()) == pin, key
    return hashlib.sha256(json.dumps(SOURCE_PINS, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def _origin(function, path):
    assert function.__name__ == function.__qualname__ == 'run_fixture'
    assert function.__globals__.get('run_fixture') is function
    assert Path(function.__globals__['__file__']).resolve() == Path(path).resolve()
    assert Path(function.__code__.co_filename).resolve() == Path(path).resolve()

def _json_stat(value, style='producer'):
    assert style in ('producer', 'raw', 'canonical')
    options = dict(ensure_ascii=True, allow_nan=False, sort_keys=style != 'producer')
    if style == 'producer': options['indent'] = 2
    if style == 'canonical': options['separators'] = (',', ':')
    digest, size = hashlib.sha256(), 0
    for text in json.JSONEncoder(**options).iterencode(value):
        chunk = text.encode('utf-8'); size += len(chunk); digest.update(chunk)
    return dict(bytes=size, SHA256=digest.hexdigest(), within_original_64MiB=size <= LIMIT)

def _collect(b4_run, b4_args, b4_kwargs, c2_run, c2_args, c2_kwargs, finish_code):
    saved, phase, prior = {}, 'b4', sys.getprofile()
    def observe(frame, event, arg):
        if event != 'return': return
        if phase == 'b4' and frame.f_code is finish_code and 'sensor' not in saved and type(arg) is dict:
            ledger = arg.get('control_ledger')
            if (type(ledger) is dict and ledger.get('requested_controls') == ledger.get('recorded_controls') == 64
                    and ledger.get('all_controls_observed') is True and ledger.get('normal_channel_records') == 640
                    and arg.get('metadata_retention_complete') is True):
                saved['sensor'] = arg
        elif phase == 'c2' and frame.f_code is c2_run.__code__ and type(arg) is dict:
            wire = frame.f_locals.get('wire')
            if type(wire) is dict: saved['c2'] = wire
    try:
        sys.setprofile(observe)
        b4_result = b4_run(*b4_args, **b4_kwargs)
        phase = 'c2'
        c2_result = c2_run(*c2_args, **c2_kwargs)
    finally:
        sys.setprofile(prior)
    assert set(saved) == {'sensor', 'c2'}, 'normal complete return objects were not observed'
    return saved['sensor'], saved['c2'], b4_result, c2_result, sys.getprofile() is prior

def _versions(value, tensor_type):
    if isinstance(value, tensor_type):
        assert str(value.device) == 'cpu'
        return [(id(value), value._version, tuple(value.shape), str(value.dtype), str(value.device))]
    items = value.values() if type(value) is dict else value if type(value) in (list, tuple) else ()
    return [entry for item in items for entry in _versions(item, tensor_type)]

def _pack(sensor, c2_wire, scaffold=None):
    scaffold = {} if scaffold is None else scaffold
    case = dict(scaffold.get('case', {}), sensor=sensor)
    case['actuation'] = dict(case.get('actuation', {}), **c2_wire)
    terminal = dict(scaffold.get('terminal', {}), data=case)
    group = dict(scaffold.get('group', {}), terminal=[terminal])
    return dict(CASE=_json_stat(case), GROUP=_json_stat(group))

def run_size_fixture(*, torch_module, codec_module, passive_module, codec, source_paths,
                     b4_run, b4_args=(), b4_kwargs=None, c2_run, c2_args=(), c2_kwargs=None, scaffold=None):
    """Parent supplies complete original callables/modules and a published CPU codec instance.
    Optional scaffold has JSON-ready case/terminal/group metadata; no epoch is invented.
    Only stats are returned. No ABI validation or completeness/native bound is claimed.
    """
    assert __debug__
    before = _source_digest(source_paths)
    _origin(b4_run, source_paths['b4_fixture']); _origin(c2_run, source_paths['c2_fixture'])
    for module, key in ((codec_module, 'codec'), (passive_module, 'passive')):
        assert Path(module.__file__).resolve() == Path(source_paths[key]).resolve()
    assert type(codec) is codec_module.CaptureCodec and codec.tensor_type is torch_module.Tensor
    assert codec.materialize.__func__ is codec_module.CaptureCodec.materialize
    rng, python_rng = torch_module.get_rng_state(), random.getstate()
    sensor, c2_wire, old_b4, old_c2, restored = _collect(
        b4_run, b4_args, {} if b4_kwargs is None else b4_kwargs,
        c2_run, c2_args, {} if c2_kwargs is None else c2_kwargs, passive_module.PassiveCapture.finish.__code__)
    assert old_b4.get('status') == 'PASS' and old_c2.get('controls') == 64 and restored
    versions = _versions(sensor, torch_module.Tensor)
    sensor_wire = codec.materialize(sensor)
    canonical = [_json_stat(value, 'canonical') for value in (sensor_wire, c2_wire)]
    scaffold_digest = None if scaffold is None else _json_stat(scaffold, 'canonical')
    result = dict(kind='TYPED_CAPTURE_MATERIALIZED_SIZE_PROFILE_V1', status='SIZE_PROFILE_COMPLETE', controls=64,
        purpose='MATERIALIZED_VOLUME_REUSE_ONCE_NOT_NEW_OLD_SUITE_QUALIFICATION', old_fixture_calls={'b4': 1, 'c2': 1},
        basis='LOWER_BOUND_SYNTHETIC_SERIALIZATION_NOT_FULL_NATIVE_BOUND', native_size_guarantee=False,
        component_raw_JSON={key: _json_stat(value, 'raw') for key, value in (('sensor', sensor_wire), ('C2_full_wire', c2_wire))},
        canonical_components=canonical, lower_bound_synthetic=_pack(sensor_wire, c2_wire),
        encoding='UTF8 ensure_ascii=True allow_nan=False indent=2; internal LF, no trailing LF; no automatic capture_metadata_epoch',
        C2_extra_exception_pressure_retained=True, profile_restored=restored, Gate1='UNKNOWN', stage2_GO=False)
    c2_raw = result['component_raw_JSON']['C2_full_wire']
    assert (c2_raw['bytes'], c2_raw['SHA256']) == (old_c2['wire_bytes'], old_c2['wire_sha256'])
    if scaffold is not None:
        result['exact_supplied_synthetic_scaffold'] = _pack(sensor_wire, c2_wire, scaffold)
        result['scaffold_scope'] = 'EXACT_SUPPLIED_SYNTHETIC_OBJECTS_ONLY_NOT_ABI_OR_NATIVE_COMPLETENESS'
    assert canonical == [_json_stat(value, 'canonical') for value in (sensor_wire, c2_wire)]
    assert scaffold_digest == (None if scaffold is None else _json_stat(scaffold, 'canonical'))
    assert versions == _versions(sensor, torch_module.Tensor)
    assert torch_module.equal(rng, torch_module.get_rng_state()) and python_rng == random.getstate()
    assert before == _source_digest(source_paths)
    result.update(source_PINs_before_after=before, owned_identity_metadata_versions_unchanged=True,
                  materialized_inputs_digest_unchanged=True, global_RNG_unchanged=True)
    return result

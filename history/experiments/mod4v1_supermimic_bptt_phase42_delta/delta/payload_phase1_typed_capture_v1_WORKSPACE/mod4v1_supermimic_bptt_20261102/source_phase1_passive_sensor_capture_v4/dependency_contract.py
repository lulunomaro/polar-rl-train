"""V4 fixed-complete typed-source checks. Pre-install only, not a callback.

Expected pins are the unchanged frozen B3 publication, never imported-module
inference. Optional overrides must equal that complete JSON literal tree with
exact types. Only positional-default and the two named module-constant OUTER
containers use the explicitly documented tuple-to-JSON-list representation.
B3 capture layout/hooks and B2 four-reset/MRO source checks remain unchanged.
"""
import hashlib
import inspect
import json
from pathlib import Path
import sys

from source_api import sha, verify_class, verify_callable
from field_snapshot import FieldSnapshot

HERE = Path(__file__).resolve().parent
FIXED_PINS_BYTES = 19153
FIXED_PINS_SHA256 = '5cd6c770c7f3541308201389f721b43f9e7c681199443c9a2f80d2f80347e452'
FIXED_KEYSETS = {
    'codec_constants': frozenset(('ROLES', 'CHANNEL_WIDTHS', 'INTEGER_DTYPES')),
    'codec_classes': frozenset(('CaptureError', 'CaptureCodec', 'ControlLedger')),
    'codec_functions': frozenset((
        '_need', '_metadata', '_clock', '_clock_key',
        'CaptureCodec.__init__', 'CaptureCodec.capture', 'CaptureCodec.validate_owned',
        'CaptureCodec._validate_tree', 'CaptureCodec.materialize',
        'ControlLedger.__init__', 'ControlLedger._active', 'ControlLedger.begin',
        'ControlLedger.normal_sample', 'ControlLedger.pre_reset', 'ControlLedger.reset',
        'ControlLedger.end', 'ControlLedger.finish',
    )),
    'field_functions': frozenset(('__init__', 'rows', 'ids', 'mask', 'state')),
}


def _same_literal_tree(actual, expected):
    """Compare only exact JSON builtins; never arbitrary __eq__/repr/coercion.

    The caller performs any documented OUTER tuple/list normalization first.
    Nested tuples, subclasses and arbitrary objects are deliberately unmatched.
    """
    kind = type(expected)
    if type(actual) is not kind:
        return False
    if kind is dict:
        if any(type(key) is not str for key in actual) or any(type(key) is not str for key in expected):
            return False
        if set(actual) != set(expected):
            return False
        return all(_same_literal_tree(actual[key], expected[key]) for key in expected)
    if kind is list:
        return len(actual) == len(expected) and all(
            _same_literal_tree(left, right) for left, right in zip(actual, expected))
    if kind in (type(None), str, bool, int, float):
        return actual == expected
    return False


def _check_pin_keysets(pins):
    if type(pins) is not dict or any(type(key) is not str for key in pins):
        raise ValueError('Exact published pins dictionary required')
    for name, keys in FIXED_KEYSETS.items():
        collection = pins.get(name)
        if (type(collection) is not dict or any(type(key) is not str for key in collection)
                or set(collection) != keys):
            raise ValueError('Complete fixed published keyset required: ' + name)


def _published_pins(override):
    raw = (HERE / 'CODEC_SOURCE_PINS.json').read_bytes()
    if len(raw) != FIXED_PINS_BYTES or hashlib.sha256(raw).hexdigest() != FIXED_PINS_SHA256:
        raise ValueError('Frozen published expected pins bytes/SHA changed')
    expected = json.loads(raw)
    _check_pin_keysets(expected)
    if override is not None:
        _check_pin_keysets(override)
        if not _same_literal_tree(override, expected):
            raise ValueError('Override must exactly match the complete published pins and types')
    # Always use this fresh fixed-file tree, never caller-owned override values.
    return expected


def _function(value, expected, module, owner=None):
    if inspect.ismethod(value):
        if owner is not None and value.__self__ is not owner:
            raise ValueError('Typed method belongs to a different owner')
        fn = value.__func__
    else:
        fn = value
    if not inspect.isfunction(fn) or hasattr(fn, '__wrapped__'):
        raise ValueError('Exact published typed function required, no unwrap skip')
    if fn.__globals__ is not module.__dict__ or fn.__closure__:
        raise ValueError('Typed function globals/closure changed')
    # Only None is normalized. The __defaults__ OUTER tuple is JSON's list.
    defaults = () if fn.__defaults__ is None else fn.__defaults__
    if type(defaults) is not tuple or not _same_literal_tree(list(defaults), expected['literal_defaults']):
        raise ValueError('Typed positional defaults changed')
    kwdefaults = {} if fn.__kwdefaults__ is None else fn.__kwdefaults__
    if not _same_literal_tree(kwdefaults, expected['literal_kwdefaults']):
        raise ValueError('Typed keyword defaults changed')
    return verify_callable(fn, expected)


def verify_typed_dependency(snapshot, ledger, *, dependency_pins=None):
    """Fixed, complete, type-strict dependency binding before any MDP assignment.

    None loads only the fixed publication. An override is compatibility input,
    not authority: every key/value/type must match the complete fixed tree.
    Deployment paths may differ; pinned source/code/module/owner checks remain.
    """
    pins = _published_pins(dependency_pins)
    if pins.get('kind') != 'B3_TYPED_SOURCE_DEPENDENCY_PINS_V1' or pins.get('publisher_final') is not True:
        raise ValueError('Final published typed source pins required')
    module = sys.modules.get(pins['codec_module'])
    if module is None or sha(module.__file__) != pins['codec_source_sha256']:
        raise ValueError('Published typed codec module/source mismatch')
    if type(snapshot) is not FieldSnapshot or type(snapshot.codec) is not vars(module)['CaptureCodec']:
        raise ValueError('Exact V3 FieldSnapshot and published CaptureCodec required')
    if type(ledger) is not vars(module)['ControlLedger'] or ledger.codec is not snapshot.codec:
        raise ValueError('Exact published same-codec ControlLedger required')
    if type(snapshot.codec.n) is not int or snapshot.codec.n != 80:
        raise ValueError('Typed source lineage requires N80')
    codec = snapshot.codec
    ids = codec.witness_env_ids
    if (type(ids) is not tuple or not 1 <= len(ids) <= 8
            or any(type(item) is not int or not 0 <= item < 80 for item in ids)
            or len(set(ids)) != len(ids)):
        raise ValueError('Declared witness metadata changed')
    if (not isinstance(codec.tensor_type, type)
            or not isinstance(codec.witness_index, codec.tensor_type)
            or tuple(codec.witness_index.shape) != (len(ids),)
            or str(codec.witness_index.dtype) != 'torch.int64'):
        raise ValueError('Existing witness index metadata changed')
    if type(ledger.controls) is not int or ledger.controls not in (64, 128):
        raise ValueError('Control ledger cap must be 64 or 128')
    if type(ledger.run_id) is not str or not ledger.run_id:
        raise ValueError('Explicit run ID required')
    if type(ledger._packs) is not list or ledger._packs or ledger._open is not None or ledger._finished is not False:
        raise ValueError('Install requires an unused existing control ledger')
    for name, expected in pins['codec_constants'].items():
        actual = vars(module).get(name)
        # Only these published OUTER tuple constants have JSON-list form.
        if name in ('ROLES', 'INTEGER_DTYPES'):
            if type(actual) is not tuple:
                raise ValueError('Published typed module constant changed: ' + name)
            actual = list(actual)
        if not _same_literal_tree(actual, expected):
            raise ValueError('Published typed module constant changed: ' + name)
    class_receipts = {name: verify_class(vars(module)[name], expected)
                      for name, expected in pins['codec_classes'].items()}
    receipts = {}
    for qualname, expected in pins['codec_functions'].items():
        if '.' in qualname:
            class_name, method = qualname.split('.')
            cls = vars(module)[class_name]
            owner = snapshot.codec if class_name == 'CaptureCodec' else ledger
            value = getattr(owner, method)
            if not inspect.ismethod(value) or value.__func__ is not vars(cls)[method]:
                raise ValueError('Typed class descriptor/instance method changed: ' + qualname)
            receipts[qualname] = _function(value, expected, module, owner)
        else:
            receipts[qualname] = _function(vars(module)[qualname], expected, module)
    field_module = sys.modules.get(FieldSnapshot.__module__)
    if field_module is None or vars(field_module).get('FieldSnapshot') is not FieldSnapshot:
        raise ValueError('FieldSnapshot module binding changed')
    if vars(field_module).get('CaptureCodec') is not vars(module)['CaptureCodec']:
        raise ValueError('FieldSnapshot resolves a different CaptureCodec')
    verify_class(FieldSnapshot, pins['field_class'])
    for name, expected in pins['field_functions'].items():
        value = getattr(snapshot, name)
        if not inspect.ismethod(value) or value.__func__ is not vars(FieldSnapshot)[name]:
            raise ValueError('Explicit field method changed: ' + name)
        receipts['FieldSnapshot.' + name] = _function(value, expected, field_module, snapshot)
    return dict(kind='V4_TYPED_SOURCE_BINDING_INSPECTION_V1', source_revision=4, source_only=True,
                capture_schema_compatibility='PASSIVE_SENSOR_CAPTURE_V3_UNCHANGED',
                expected_pins_sha256=FIXED_PINS_SHA256,
                native_enabled=False, exact=False, publisher_final=True,
                codec_source_sha256=pins['codec_source_sha256'], classes=class_receipts,
                checked_functions=receipts,
                witness_mapping='CALLER_DECLARED_INDEX_BINDING_NOT_READBACK',
                actual_MDP_calls=0, actual_tensor_index_readback=False)

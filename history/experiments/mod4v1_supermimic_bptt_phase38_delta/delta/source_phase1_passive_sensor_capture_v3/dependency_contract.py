"""V3 fail-closed typed-source checks. Pre-install only, not a callback.

Reads fixed NEW SOURCE pins; never discovers a replacement expected SHA from
whatever happens to be imported. No SDK/MDP call, tensor readback or device index
construction. B2 source_api and its exact four-reset-layer contract are retained.
"""
import inspect
import json
from pathlib import Path
import sys

from source_api import sha, verify_class, verify_callable
from field_snapshot import FieldSnapshot

HERE = Path(__file__).resolve().parent


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
    if list(fn.__defaults__ or ()) != expected['literal_defaults']:
        raise ValueError('Typed positional defaults changed')
    if (fn.__kwdefaults__ or {}) != expected['literal_kwdefaults']:
        raise ValueError('Typed keyword defaults changed')
    return verify_callable(fn, expected)


def verify_typed_dependency(snapshot, ledger, *, dependency_pins=None):
    """Reject a stale/unknown codec BEFORE assignment of the first MDP wrapper.

    Source pins are made only after the independent publisher's final seal.
    The installed module may have a deployment path different from source pins;
    source bytes, line/signature/live compiled code and actual owner/module bind.
    """
    pins = (json.loads((HERE / 'CODEC_SOURCE_PINS.json').read_text(encoding='utf-8'))
            if dependency_pins is None else dependency_pins)
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
        if vars(module).get(name) != expected:
            # JSON turns tuple constants into lists; only the declared tuple
            # constants may use this one explicit metadata representation.
            if name not in ('ROLES', 'INTEGER_DTYPES') or tuple(vars(module).get(name, ())) != tuple(expected):
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
    return dict(kind='V3_TYPED_SOURCE_BINDING_INSPECTION_V1', source_only=True,
                native_enabled=False, exact=False, publisher_final=True,
                codec_source_sha256=pins['codec_source_sha256'], classes=class_receipts,
                checked_functions=receipts,
                witness_mapping='CALLER_DECLARED_INDEX_BINDING_NOT_READBACK',
                actual_MDP_calls=0, actual_tensor_index_readback=False)

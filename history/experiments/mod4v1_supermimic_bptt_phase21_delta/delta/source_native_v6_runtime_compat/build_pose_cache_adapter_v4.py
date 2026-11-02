"""Build NEW source-only V4 adapter from pinned sealed V3; never import SDK."""
from __future__ import annotations
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / 'source_pose_cache_runtime_adapter_v3' / 'pose_cache_runtime_adapter_v3.py'
EXPECTED = '73145a1caa7819e0938e66e53a1bb0be73e48d0d06c3cf9cd5dc76e9f0862209'
OUTPUT = HERE / 'pose_cache_runtime_adapter_v4.py'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def replace_once(text, old, new):
    assert text.count(old) == 1, ('literal uniqueness', old[:80], text.count(old))
    return text.replace(old, new, 1)

def main():
    raw = SOURCE.read_bytes()
    assert sha(raw) == EXPECTED, ('sealed V3 source differs', sha(raw))
    old = raw.decode('utf-8')
    new = old.replace('reset-pose cache adapter SOURCE v3.', 'reset-pose cache adapter SOURCE v4 (native stale-sentinel compatibility).', 1)
    new = new.replace('install_pose_cache_runtime_adapter_v3', 'install_pose_cache_runtime_adapter_v4')
    new = replace_once(new, '"ROOT_DERIVED_BUFFERS"]', '"ROOT_DERIVED_BUFFERS", "SOURCE_CODE_VERSION",\n            "install_pose_cache_runtime_adapter_v3"]\n\nSOURCE_CODE_VERSION = "POSE_CACHE_RUNTIME_ADAPTER_V4_NATIVE_NEGATIVE_INFINITY_STALE_V1"')
    new = replace_once(new,
'''def _number(value, name, *, clock=None):
    # No tensor.item(), array coercion, GPU sync, custom numeric conversion.
    if type(value) not in (int, float) or not math.isfinite(value):
        raise PoseCacheAdapterError("NON_NATIVE_FINITE_TIMESTAMP", name)
    if clock is None:
        if value < 0:
            raise PoseCacheAdapterError("NEGATIVE_CLOCK", name)
    elif value != -1.0 and not (0.0 <= value <= clock):
        raise PoseCacheAdapterError("OUT_OF_RANGE_BUFFER_TIMESTAMP", name)
    return value''',
'''def _number(value, name, *, clock=None):
    # No tensor.item(), array coercion, GPU sync, custom numeric conversion.
    if type(value) not in (int, float):
        raise PoseCacheAdapterError("NON_NATIVE_FINITE_TIMESTAMP", name)
    # Original active ChassisCOMSDK.invalidate_COM_dependent_cache writes this
    # exact built-in float sentinel. It is legal ONLY for a buffer, never clock.
    if clock is not None and type(value) is float and value == -math.inf:
        return value
    if not math.isfinite(value):
        raise PoseCacheAdapterError("NON_NATIVE_FINITE_TIMESTAMP", name)
    if clock is None:
        if value < 0:
            raise PoseCacheAdapterError("NEGATIVE_CLOCK", name)
    elif value != -1.0 and not (0.0 <= value <= clock):
        raise PoseCacheAdapterError("OUT_OF_RANGE_BUFFER_TIMESTAMP", name)
    return value''')
    new = replace_once(new, '    found, payloads, stamps = [], [], {}', '    found, payloads, stamps, stamp_types = [], [], {}, {}')
    new = replace_once(new,
'        stamps[name] = _number(_plain(buf, "timestamp"), name, clock=clock)',
'''        value = _number(_plain(buf, "timestamp"), name, clock=clock)
        stamp_types[name] = type(value).__module__ + "." + type(value).__qualname__
        # Encode metadata only; preserve the actual SDK timestamp untouched.
        stamps[name] = (dict(kind="STALE_SENTINEL", value="NEGATIVE_INFINITY",
                             python_type="builtins.float", actual_native_value_read=True)
                        if type(value) is float and value == -math.inf else value)''')
    new = replace_once(new,
'    return dict(clock=clock, timestamps=stamps), tuple(found), tuple(payloads)',
'''    return dict(clock=clock, clock_python_type=type(clock).__module__ + "." + type(clock).__qualname__,
                timestamps=stamps, timestamp_python_types=stamp_types), tuple(found), tuple(payloads)''')
    new = new.replace('PINNED_INSTANCE_POSE_CACHE_ADAPTER_V3', 'PINNED_INSTANCE_POSE_CACHE_ADAPTER_V4')
    new = replace_once(new,
'        return dict(kind="PINNED_INSTANCE_POSE_CACHE_ADAPTER_V4", event=name,',
'        return dict(kind="PINNED_INSTANCE_POSE_CACHE_ADAPTER_V4", source_code_version=SOURCE_CODE_VERSION, event=name,')
    new = replace_once(new,
'        _emit_preserving(receipt_callback, dict(kind="PINNED_INSTANCE_POSE_CACHE_ADAPTER_V4", event="install_rejected",',
'        _emit_preserving(receipt_callback, dict(kind="PINNED_INSTANCE_POSE_CACHE_ADAPTER_V4", source_code_version=SOURCE_CODE_VERSION, event="install_rejected",')
    new += '\n\n# Logical ABI alias: V5 worker/installer may keep their sealed import spelling.\n# The installed source SHA and every event source_code_version identify V4.\ninstall_pose_cache_runtime_adapter_v3 = install_pose_cache_runtime_adapter_v4\n'
    before, after = ast.parse(old), ast.parse(new)
    def functions(tree):
        return {node.name: node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    bf, af = functions(before), functions(after)
    protected = ['_plain', '_mro_names', '_source', '_bound_owner', '_validate_binding', '_emit_preserving', '_Pins', 'PoseCacheAdapterError']
    for name in protected:
        assert ast.dump(bf[name], include_attributes=False) == ast.dump(af[name], include_attributes=False), name
    old_methods = {node.name: node for node in bf['PoseCacheAdapterHandle'].body if isinstance(node, ast.FunctionDef)}
    new_methods = {node.name: node for node in af['PoseCacheAdapterHandle'].body if isinstance(node, ast.FunctionDef)}
    for name in old_methods:
        if name != '_event':
            assert ast.dump(old_methods[name], include_attributes=False) == ast.dump(new_methods[name], include_attributes=False), name
    compile(new, str(OUTPUT), 'exec')
    payload = new.encode('utf-8')
    with OUTPUT.open('xb') as handle:
        handle.write(payload)
    patch = ''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile=str(SOURCE), tofile=str(OUTPUT)))
    with (HERE / 'POSE_CACHE_SENTINEL_DIFF_V4.patch').open('x', encoding='utf-8', newline='\n') as handle:
        handle.write(patch)
    assert SOURCE.read_bytes() == raw
    receipt = dict(kind='SOURCE_ONLY_ADAPTER_V4_BUILD_NOT_SDK_INSTALL', source_path=str(SOURCE), source_SHA256=EXPECTED,
                   output=str(OUTPUT), bytes=len(payload), SHA256=sha(payload), protected_binding_helpers_AST_identical=protected,
                   protected_handle_methods_AST_identical=[name for name in old_methods if name != '_event'],
                   only_additional_numeric_value='buffer builtins.float negative infinity; clock excluded',
                   diagnostic_nonfinite_values_are_tagged_not_JSON_numbers=True,
                   legacy_install_v3_name_is_alias=True, sealed_source_unchanged=True,
                   SDK_imports=0, Torch_imports=0, native_installations=0, native_steps=0,
                   gravity_threshold_changes=0, physics_changes=0, C_reads_writes=0, Git_operations=0)
    with (HERE / 'BUILD_POSE_CACHE_ADAPTER_V4.json').open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write('\n')
    print(json.dumps(receipt, ensure_ascii=False))

if __name__ == '__main__':
    main()

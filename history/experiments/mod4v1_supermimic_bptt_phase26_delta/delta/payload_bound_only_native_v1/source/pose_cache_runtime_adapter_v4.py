"""Pinned, instance-only reset-pose cache adapter SOURCE v4 (native stale-sentinel compatibility).

This module imports stdlib only. Import does not discover a robot or install a
hook. The caller must construct a NEW native instance, then install before its
ONE original explicit reset. No past binding or runtime success is asserted.
Other write APIs are not wrapped. The original writer, quaternion conversion,
gravity guard, physics, reset, observations, sensor history and RNG stay owned
by their original code. Callback must only write small new-job JSON metadata.
"""
from __future__ import annotations

import ast
import copy
from dataclasses import dataclass
import hashlib
import inspect
import math
from pathlib import Path
import sys
from types import FunctionType, MemberDescriptorType, MethodType
from typing import Callable
import weakref

__all__ = ["PoseCacheAdapterError", "PoseCacheAdapterHandle",
           "install_pose_cache_runtime_adapter_v4", "EXPECTED_SOURCE_SHA256",
           "ROOT_DERIVED_BUFFERS", "SOURCE_CODE_VERSION",
            "install_pose_cache_runtime_adapter_v3"]

SOURCE_CODE_VERSION = "POSE_CACHE_RUNTIME_ADAPTER_V4_NATIVE_NEGATIVE_INFINITY_STALE_V1"

ROOT_DERIVED_BUFFERS = (
    "_projected_gravity_b", "_heading_w", "_root_link_vel_w", "_root_com_pose_w",
    "_root_link_lin_vel_b", "_root_link_ang_vel_b",
    "_root_com_lin_vel_b", "_root_com_ang_vel_b",
)
_METHOD = "write_root_state_to_sim"
_DELEGATES = ("write_root_link_pose_to_sim_index", "write_root_com_velocity_to_sim_index")
_MISSING = object()

@dataclass(frozen=True)
class _Pins:
    asset_module: str
    asset_owner: str
    asset_sha256: str
    asset_bytes: int
    data_module: str
    data_class: str
    data_sha256: str
    data_bytes: int

# No public API permits overriding these pins. Tests use an explicitly patched
# private policy with hashes of their OWN fake source, never an SDK import.
_PINNED = _Pins(
    "isaaclab_physx.assets.articulation.articulation", "Articulation",
    "47d96553282b389493e69f691b8dcbfeb98997a5a80b88c2571c60ba8b58cb6d", 220628,
    "isaaclab_physx.assets.articulation.articulation_data", "ArticulationData",
    "43a31992353ad3a500024d0ec908d5b253ada7a0aac9a1cd2261466e10bda4ff", 91275,
)
EXPECTED_SOURCE_SHA256 = {
    "articulation.py": _PINNED.asset_sha256,
    "articulation_data.py": _PINNED.data_sha256,
}

class PoseCacheAdapterError(RuntimeError):
    def __init__(self, code: str, detail: str = ""):
        self.code = code
        super().__init__(code + (": " + detail[:400] if detail else ""))


def _plain(obj, name):
    """Read a plain Python field/slot, never evaluate an SDK property getter."""
    value = inspect.getattr_static(obj, name, _MISSING)
    if value is _MISSING:
        raise PoseCacheAdapterError("MISSING_FIELD", name)
    if isinstance(value, MemberDescriptorType):
        return object.__getattribute__(obj, name)
    if hasattr(type(value), "__get__"):
        raise PoseCacheAdapterError("NON_PLAIN_FIELD", name)
    return value


def _number(value, name, *, clock=None):
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
    return value


def _mro_names(cls):
    return [base.__module__ + "." + base.__qualname__ for base in cls.__mro__]


def _source(cls, module_name, class_name, sha256, byte_count):
    if cls.__module__ != module_name or cls.__qualname__ != class_name:
        raise PoseCacheAdapterError("CLASS_IDENTITY_MISMATCH", cls.__module__ + "." + cls.__qualname__)
    module = sys.modules.get(module_name)
    module_file = None if module is None else vars(module).get("__file__")
    if not module_file:
        raise PoseCacheAdapterError("SOURCE_OR_MODULE_FILE_MISSING", module_name)
    try:
        filename = inspect.getsourcefile(cls)
    except (OSError, TypeError) as exc:
        raise PoseCacheAdapterError("SOURCE_OR_MODULE_FILE_MISSING", module_name) from exc
    if not filename:
        raise PoseCacheAdapterError("SOURCE_OR_MODULE_FILE_MISSING", module_name)
    path = Path(filename).resolve(strict=True)
    if path != Path(module_file).resolve(strict=True) or path.suffix != ".py":
        raise PoseCacheAdapterError("SOURCE_MODULE_FILE_MISMATCH", module_name)
    payload = path.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    if len(payload) != byte_count or actual != sha256:
        raise PoseCacheAdapterError("SOURCE_PIN_MISMATCH", module_name + " SHA=" + actual)
    tree = ast.parse(payload, filename=str(path))
    node = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name), None)
    if node is None:
        raise PoseCacheAdapterError("SOURCE_CLASS_MISSING", class_name)
    return dict(module=module_name, qualname=class_name, source_file=str(path),
                bytes=len(payload), SHA256=actual), node


def _bound_owner(robot, name):
    bound = getattr(robot, name)
    if not isinstance(bound, MethodType) or bound.__self__ is not robot or not isinstance(bound.__func__, FunctionType):
        raise PoseCacheAdapterError("NOT_ORIGINAL_BOUND_METHOD", name)
    owner = next((cls for cls in type(robot).__mro__ if vars(cls).get(name) is bound.__func__), None)
    if owner is None:
        raise PoseCacheAdapterError("METHOD_NOT_DEFINED_IN_ACTUAL_MRO", name)
    return bound, owner


def _validate_binding(robot):
    pins = _PINNED
    bound, owner = _bound_owner(robot, _METHOD)
    asset_receipt, asset_ast = _source(owner, pins.asset_module, pins.asset_owner,
                                       pins.asset_sha256, pins.asset_bytes)
    for name in (_METHOD,) + _DELEGATES:
        method, actual_owner = _bound_owner(robot, name)
        if actual_owner is not owner:
            raise PoseCacheAdapterError("DELEGATE_OWNER_MISMATCH", name)
        node = next((n for n in asset_ast.body if isinstance(n, ast.FunctionDef) and n.name == name), None)
        function = method.__func__
        if node is None or node.decorator_list or function.__module__ != pins.asset_module:
            raise PoseCacheAdapterError("METHOD_SOURCE_SHAPE_MISMATCH", name)
        if function.__qualname__ != pins.asset_owner + "." + name:
            raise PoseCacheAdapterError("METHOD_QUALNAME_MISMATCH", name)
        if Path(function.__code__.co_filename).resolve(strict=True) != Path(asset_receipt["source_file"]):
            raise PoseCacheAdapterError("METHOD_CODE_FILE_MISMATCH", name)
        if function.__code__.co_firstlineno != node.lineno:
            raise PoseCacheAdapterError("METHOD_SOURCE_LINE_MISMATCH", name)
    # The inspected Articulation.data property only returns self._data. Reading
    # the field directly avoids even this SDK property access.
    data = _plain(robot, "_data")
    data_type = type(data)
    data_receipt, _ = _source(data_type, pins.data_module, pins.data_class,
                              pins.data_sha256, pins.data_bytes)
    if _plain(data, "__backend_name__") != "physx":
        raise PoseCacheAdapterError("BACKEND_MISMATCH")
    receipt = dict(asset_actual_type=type(robot).__module__ + "." + type(robot).__qualname__,
                   asset_actual_MRO=_mro_names(type(robot)), writer_owner=asset_receipt,
                   writer_name=_METHOD, checked_delegates=list(_DELEGATES),
                   bound_writer=dict(self_is_this_robot=True, func_is_MRO_definition=True,
                                     module=bound.__func__.__module__, qualname=bound.__func__.__qualname__,
                                     code_filename=str(Path(bound.__func__.__code__.co_filename).resolve()),
                                     code_firstlineno=bound.__func__.__code__.co_firstlineno),
                   data_actual_type=data_type.__module__ + "." + data_type.__qualname__,
                   data_actual_MRO=_mro_names(data_type), data_source=data_receipt,
                   backend="physx", checked_this_new_instance=True,
                   past_worker_binding_claim=None)
    return bound, data, receipt


def _snapshot(data, buffers=None, arrays=None):
    clock = _number(_plain(data, "_sim_timestamp"), "_sim_timestamp")
    found, payloads, stamps, stamp_types = [], [], {}, {}
    for index, name in enumerate(ROOT_DERIVED_BUFFERS):
        buf = _plain(data, name)
        array = _plain(buf, "data")
        if array is None:
            raise PoseCacheAdapterError("BUFFER_DATA_MISSING", name)
        if buffers is not None and (buf is not buffers[index] or array is not arrays[index]):
            raise PoseCacheAdapterError("BUFFER_OR_DATA_IDENTITY_CHANGED", name)
        value = _number(_plain(buf, "timestamp"), name, clock=clock)
        stamp_types[name] = type(value).__module__ + "." + type(value).__qualname__
        # Encode metadata only; preserve the actual SDK timestamp untouched.
        stamps[name] = (dict(kind="STALE_SENTINEL", value="NEGATIVE_INFINITY",
                             python_type="builtins.float", actual_native_value_read=True)
                        if type(value) is float and value == -math.inf else value)
        found.append(buf); payloads.append(array)
    return dict(clock=clock, clock_python_type=type(clock).__module__ + "." + type(clock).__qualname__,
                timestamps=stamps, timestamp_python_types=stamp_types), tuple(found), tuple(payloads)


def _emit_preserving(callback, event, primary):
    try:
        callback(copy.deepcopy(event))
    except BaseException as callback_error:
        if hasattr(primary, "add_note"):
            primary.add_note("adapter receipt callback also failed: " + type(callback_error).__name__)


class PoseCacheAdapterHandle:
    """One new robot instance. Single-threaded reset/write precondition.

    receipt() returns metadata only. uninstall() restores the previous INSTANCE
    binding, never a class/global/SDK source; it does not restore stale stamps.
    """
    def __init__(self, robot, original, data, binding, callback, before, buffers, arrays):
        self._robot_ref = weakref.ref(robot)
        self._original_ref = weakref.WeakMethod(original)
        self._data = data
        self._buffers, self._arrays = buffers, arrays
        self._binding, self._callback = binding, callback
        namespace = object.__getattribute__(robot, "__dict__")
        if not isinstance(namespace, dict):
            raise PoseCacheAdapterError("INSTANCE_DICTIONARY_REQUIRED")
        self._previous_instance_value = namespace.get(_METHOD, _MISSING)
        self._active = False
        self._failed = False
        self._in_call = False
        self._calls = self._returned = self._invalidations = self._failures = self._callback_failures = 0
        self._last = dict(event="validated_not_installed", before=before)
        def wrapped(this_robot, *args, **kwargs):
            if this_robot is not self._robot_ref():
                raise PoseCacheAdapterError("WRONG_INSTANCE")
            return self._invoke(*args, **kwargs)
        self._wrapped_function = wrapped
        self._bound_wrapper = MethodType(wrapped, robot)

    def _event(self, name, **metadata):
        return dict(kind="PINNED_INSTANCE_POSE_CACHE_ADAPTER_V4", source_code_version=SOURCE_CODE_VERSION, event=name,
                    write_call_count=self._calls, original_return_count=self._returned,
                    invalidated_write_count=self._invalidations, failure_count=self._failures,
                    callback_failure_count=self._callback_failures,
                    extra_getter_samples=0, extra_steps=0, extra_resets=0,
                    extra_observation_computes=0, extra_RNG_draws=0, **metadata)

    def _emit(self, event):
        self._last = copy.deepcopy(event)
        try:
            self._callback(copy.deepcopy(event))
        except BaseException as exc:
            self._callback_failures += 1
            raise PoseCacheAdapterError("RECEIPT_CALLBACK_FAILED", type(exc).__name__) from exc

    def _check_data(self):
        robot = self._robot_ref()
        if robot is None or _plain(robot, "_data") is not self._data:
            raise PoseCacheAdapterError("ROBOT_OR_DATA_IDENTITY_CHANGED")
        return _snapshot(self._data, self._buffers, self._arrays)[0]

    def _invoke(self, *args, **kwargs):
        if not self._active or self._failed or self._in_call:
            raise PoseCacheAdapterError("INACTIVE_FAILED_OR_REENTRANT_ADAPTER")
        self._in_call = True
        self._calls += 1
        try:
            try:
                before = self._check_data()
            except BaseException as exc:
                self._failures += 1
                _emit_preserving(self._callback, self._event("adapter_rejected_before_write", error_type=type(exc).__name__, error=str(exc)[:400]), exc)
                raise
            original = self._original_ref()
            if original is None:
                raise PoseCacheAdapterError("ORIGINAL_INSTANCE_EXPIRED")
            try:
                result = original(*args, **kwargs)
            except BaseException as exc:
                self._failures += 1
                _emit_preserving(self._callback, self._event("original_writer_raised", before=before, error_type=type(exc).__name__), exc)
                raise
            self._returned += 1
            try:
                after_write = self._check_data()
                if after_write["clock"] != before["clock"]:
                    raise PoseCacheAdapterError("WRITER_ADVANCED_CLOCK")
                # The ONLY SDK data mutation in this adapter. No getter, update,
                # pose/joint/velocity write, simulation forward, reset or RNG.
                for buf in self._buffers:
                    object.__setattr__(buf, "timestamp", -1.0)
                after = self._check_data()
                if after["clock"] != before["clock"] or any(v != -1.0 for v in after["timestamps"].values()):
                    raise PoseCacheAdapterError("INVALIDATION_POSTCONDITION_FAILED")
                self._invalidations += 1
            except BaseException as exc:
                self._failures += 1
                _emit_preserving(self._callback, self._event("adapter_rejected_after_write", before=before, error_type=type(exc).__name__, error=str(exc)[:400]), exc)
                raise
            self._emit(self._event("write_returned_and_invalidated", before=before, after=after))
            return result
        except BaseException:
            self._failed = True  # sticky: even a caller that catches must not resume writes
            raise
        finally:
            self._in_call = False

    def receipt(self):
        return copy.deepcopy(dict(active=self._active, failed_sticky=self._failed, binding=self._binding,
                                  counters=self._event("counters"), last_event=self._last))

    def uninstall(self):
        if not self._active or self._in_call:
            raise PoseCacheAdapterError("INACTIVE_OR_BUSY_UNINSTALL")
        robot = self._robot_ref()
        current = None if robot is None else getattr(robot, _METHOD)
        if not isinstance(current, MethodType) or current.__func__ is not self._wrapped_function or current.__self__ is not robot:
            raise PoseCacheAdapterError("INSTANCE_BINDING_CHANGED")
        if self._previous_instance_value is _MISSING:
            delattr(robot, _METHOD)
        else:
            setattr(robot, _METHOD, self._previous_instance_value)
        self._active = False
        self._emit(self._event("uninstalled"))


def install_pose_cache_runtime_adapter_v4(robot, *, receipt_callback: Callable[[dict], None]) -> PoseCacheAdapterHandle:
    """Install on a NEW constructed instance, before the original ONE reset.

    Public API has no skip/verified=True or pin-override argument. Actual bound
    writer/defining MRO/source bytes and exact data type/source are checked now.
    Callback must persist small metadata only in the NEW job's own directory.
    Callback failure is fail-closed; install failure restores the prior binding.
    """
    if not callable(receipt_callback):
        raise PoseCacheAdapterError("RECEIPT_CALLBACK_REQUIRED")
    try:
        original, data, binding = _validate_binding(robot)
        before, buffers, arrays = _snapshot(data)
        handle = PoseCacheAdapterHandle(robot, original, data, binding, receipt_callback, before, buffers, arrays)
    except BaseException as exc:
        _emit_preserving(receipt_callback, dict(kind="PINNED_INSTANCE_POSE_CACHE_ADAPTER_V4", source_code_version=SOURCE_CODE_VERSION, event="install_rejected",
                         error_type=type(exc).__name__, error=str(exc)[:400], installed=False,
                         past_worker_binding_claim=None), exc)
        raise
    setattr(robot, _METHOD, handle._bound_wrapper)
    handle._active = True
    try:
        handle._emit(handle._event("installed", binding=binding, before=before, after=before,
                                   other_write_APIs_wrapped=False))
    except BaseException:
        if handle._previous_instance_value is _MISSING:
            delattr(robot, _METHOD)
        else:
            setattr(robot, _METHOD, handle._previous_instance_value)
        handle._active = False
        raise
    return handle


# Logical ABI alias: V5 worker/installer may keep their sealed import spelling.
# The installed source SHA and every event source_code_version identify V4.
install_pose_cache_runtime_adapter_v3 = install_pose_cache_runtime_adapter_v4

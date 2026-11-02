"""SOURCE ONLY: explicit parent-provided pose-cache installer BEFORE original reset.

No SDK/Torch, getters, reset, RNG, lock, budget or process work at import. The real
adapter remains agent82's separately pinned artifact; this module invents no cache
repair, quaternion convention or threshold. Without a descriptor it is a no-op.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from resume_runtime_contracts_v3 import (
    FINAL_KIND, LIFECYCLE_KIND, BASELINE_ACTOR_VIEW, RAW35_ACTOR_VIEW,
    PinnedOwnFullCheckpoint, validate_worker_variant, load_decoded_full_checkpoint_once,
    resolve_future_bridge_adapter, preserve_worker_error, close_original_resources,
    evaluate_waited_worker, require,
    bind_future_task_extensions as _bind_actor_variant,
)


def validate_pose_cache_installer_descriptor(value):
    require(isinstance(value, dict), 'explicit pose-cache installer descriptor required')
    require(value.get('kind') == 'POSE_CACHE_RUNTIME_ADAPTER_V3', 'pose-cache installer kind differs')
    require(value.get('module') == 'pose_cache_runtime_adapter_v3', 'separately owned installer module differs')
    require(value.get('symbol') == 'install_pose_cache_runtime_adapter_v3', 'stable installer API differs')
    require(value.get('source_relative') == 'worker_sources/pose_cache_runtime_adapter_v3.py', 'owned installer source path differs')
    sha = value.get('SHA')
    require(isinstance(sha, str) and len(sha) == 64 and all(c in '0123456789abcdef' for c in sha), 'pinned installer SHA required')
    require(type(value.get('bytes')) is int and value['bytes'] > 0, 'pinned installer byte size required')
    require(value.get('install_timing') == 'after_build_env_before_only_original_reset', 'installer timing differs')
    return dict(value)


def bind_future_task_extensions(task, entry):
    output = _bind_actor_variant(task, entry)
    if entry.get('pose_cache_runtime_adapter') is not None:
        require(output.get('bridge_adapter') is None, 'select stable pose installer or a different bridge adapter, not both')
        output['pose_cache_runtime_adapter'] = validate_pose_cache_installer_descriptor(entry['pose_cache_runtime_adapter'])
    return output


def install_optional_pose_cache_runtime_adapter(env, task, job_root, *, callback):
    value = task.get('pose_cache_runtime_adapter')
    if value is None:
        return None, dict(adapter_requested=False, install_calls=0,
                          bridge_quaternion_and_threshold_unchanged=True)
    descriptor = validate_pose_cache_installer_descriptor(value)
    root = Path(job_root).resolve()
    source = (root / descriptor['source_relative']).resolve()
    require(source.is_relative_to((root / 'worker_sources').resolve()), 'installer escaped owned worker sources')
    manifest = json.loads((root / 'INSTALL_MANIFEST.json').read_bytes())
    require(any(item.get('relative') == descriptor['source_relative']
                and item.get('SHA') == descriptor['SHA'] and item.get('bytes') == descriptor['bytes']
                for item in manifest['files']), 'installer is not the explicit manifest-pinned source')
    raw = source.read_bytes()
    require(len(raw) == descriptor['bytes'] and hashlib.sha256(raw).hexdigest() == descriptor['SHA'], 'installer source byte identity differs')
    require(descriptor['module'] not in sys.modules, 'installer module already loaded; no duplicate automatic installation')
    spec = importlib.util.spec_from_file_location(descriptor['module'], source)
    require(spec is not None and spec.loader is not None, 'installer import specification missing')
    module = importlib.util.module_from_spec(spec)
    sys.modules[descriptor['module']] = module
    spec.loader.exec_module(module)
    install = getattr(module, descriptor['symbol'], None)
    require(callable(install), 'stable installer callable missing')
    # Stable API from parent: no getter/sensor/command/obs probes here.
    handle = install(env.scene['robot'], receipt_callback=callback)
    return handle, dict(adapter_requested=True, install_calls=1,
                        module=descriptor['module'], source_SHA=descriptor['SHA'], source_bytes=len(raw),
                        timing=descriptor['install_timing'],
                        bridge_quaternion_and_threshold_unchanged=True,
                        actual_instance_adapter_validation='DELEGATED_TO_PINNED_ADAPTER_NATIVE_EVIDENCE_PENDING')

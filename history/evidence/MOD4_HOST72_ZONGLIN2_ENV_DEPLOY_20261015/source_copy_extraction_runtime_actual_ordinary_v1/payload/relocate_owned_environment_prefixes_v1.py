"""Relocate only the new copy, retaining original archive and explicit before/after hashes."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import subprocess
import time
import traceback

ROOT = Path('/home/lc01/Zonglin Li/zonglin2')
ENV = ROOT / 'envs/mod4'
PROJECT = ROOT / 'src/fangzhen_linux'
OLD_ENV = '/home/egde/anaconda3/envs/fangzhen-isaaclab'
OLD_PROJECT = '/home/egde/fangzhen_linux'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert ROOT.resolve() == ROOT and ENV.is_dir() and PROJECT.is_dir()
    assert (ROOT / 'audit/EXTRACTION_V1_COMPLETE.json').exists()
    marker = ROOT / 'audit/PREFIX_RELOCATION_V1_STARTED.json'
    assert not marker.exists()
    with marker.open('x') as f:
        json.dump(dict(epoch=time.time(), source_prefix=OLD_ENV, target_prefix=str(ENV),
            only_new_copy_modified=True, original_archive_retained=True), f, indent=2)
    helper = ROOT / 'tools/conda_pack_prefixes_official.py'
    assert sha(helper) == 'bb54053d8d680aeeaf5164cd8cb06b9de5722137e4453eb1f4cc6cba4017501a'
    spec = importlib.util.spec_from_file_location('official_conda_pack_prefixes', helper)
    prefix = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prefix)
    seen, changes = set(), []
    for metadata in sorted((ENV / 'conda-meta').glob('*.json')):
        record = json.loads(metadata.read_bytes())
        for row in record.get('paths_data', {}).get('paths', []):
            if not row.get('prefix_placeholder'):
                continue
            p = ENV / row['_path']
            if p in seen or not p.is_file() or p.is_symlink():
                continue
            seen.add(p)
            assert str(p.resolve()).startswith(str(ENV) + '/')
            old = sha(p)
            prefix.update_prefix(str(p), str(ENV), OLD_ENV, row.get('file_mode', 'text'))
            new = sha(p)
            if old != new:
                changes.append(dict(path=str(p), old_SHA=old, new_SHA=new, mode=row.get('file_mode', 'text'),
                    official_prefix_relocation_only=True))
    site = ENV / 'lib/python3.12/site-packages'
    candidates = list((ENV / 'bin').glob('*')) + list(site.glob('__editable__*finder.py'))
    candidates += list((ENV / 'etc/conda').rglob('*')) if (ENV / 'etc/conda').is_dir() else []
    for p in candidates:
        if not p.is_file() or p.is_symlink() or p.stat().st_size > 2*1024*1024:
            continue
        assert str(p.resolve()).startswith(str(ENV) + '/')
        raw = p.read_bytes()
        if b'\0' in raw:
            continue
        data = raw.replace(OLD_ENV.encode(), str(ENV).encode()).replace(OLD_PROJECT.encode(), str(PROJECT).encode())
        if raw != data:
            p.write_bytes(data)
            changes.append(dict(path=str(p), old_SHA=hashlib.sha256(raw).hexdigest(),
                new_SHA=hashlib.sha256(data).hexdigest(), editable_or_text_source_path_relocation_only=True))
    wrapper = ROOT / 'run-python-native.sh'
    assert not wrapper.exists()
    text = '''#!/bin/bash
set -euo pipefail
ulimit -c 0
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
mkdir -p -- "$ROOT/state/runtime"
chmod 700 -- "$ROOT/state/runtime"
unset PYTHONPATH PYTHONHOME LD_LIBRARY_PATH
export HOME="$ROOT/home"
export XDG_CACHE_HOME="$ROOT/cache" XDG_CONFIG_HOME="$ROOT/config"
export XDG_DATA_HOME="$ROOT/home/.local/share" XDG_STATE_HOME="$ROOT/state"
export XDG_RUNTIME_DIR="$ROOT/state/runtime"
export TMPDIR="$ROOT/tmp" TMP="$ROOT/tmp" TEMP="$ROOT/tmp"
export PIP_CACHE_DIR="$ROOT/cache/pip" CONDA_PKGS_DIRS="$ROOT/cache/conda"
export TORCH_HOME="$ROOT/cache/torch" CUDA_CACHE_PATH="$ROOT/cache/cuda"
export TRITON_CACHE_DIR="$ROOT/cache/triton" WARP_CACHE_PATH="$ROOT/cache/warp"
export NUMBA_CACHE_DIR="$ROOT/cache/numba" MPLCONFIGDIR="$ROOT/cache/matplotlib"
export PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
export CONDA_PREFIX="$ROOT/envs/mod4"
export PATH="$CONDA_PREFIX/bin:/usr/local/bin:/usr/bin:/bin"
cd -- "$ROOT"
exec "$CONDA_PREFIX/bin/python" -B "$@"
'''
    wrapper.write_text(text)
    os.chmod(str(wrapper), 0o700)
    v = dict(epoch=time.time(), complete=True, changes=changes,
        official_prefix_source_SHA=sha(helper), new_copy_only=True, source_archive_retained=True,
        environment=str(ENV), project=str(PROJECT), native_launcher=str(wrapper),
        launcher_supports_space_in_parent_path=True, no_existing_user_profile_or_environment_modified=True,
        original_conda_bin_entrypoint_shebang_space_caveat='Use owned quoted run-python launcher, not direct shebang entrypoints.',
        no_driver_system_install_deletion_or_training=True)
    with (ROOT / 'audit/PREFIX_RELOCATION_V1_COMPLETE.json').open('x') as f:
        json.dump(v, f, indent=2)
    print(json.dumps(dict(complete=True, relocated_files=len(changes), launcher=str(wrapper))), flush=True)


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        with (ROOT / ('audit/PREFIX_RELOCATION_V1_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json')).open('x') as f:
            json.dump(dict(error=traceback.format_exc(), original_archive_and_new_copy_retained=True,
                           no_delete_or_blind_replay=True), f, indent=2)
        raise

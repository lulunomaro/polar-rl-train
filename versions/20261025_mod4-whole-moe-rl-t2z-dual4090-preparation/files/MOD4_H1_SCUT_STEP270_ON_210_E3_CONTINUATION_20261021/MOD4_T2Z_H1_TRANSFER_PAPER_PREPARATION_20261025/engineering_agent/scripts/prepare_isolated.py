#!/usr/bin/env python3
"""Finite, explicit CPU-only preparation. No training, CUDA API, SSH, or rollout."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

ROOT = Path('/home/lc01/Zonglin Li/zonglin2/research/T2Z_H1_TRANSFER_PREP_20261025')
COMMIT = 'c72f051f5cffcb1f372a32bc488df273556d39b9'
URL = 'https://github.com/T2-z-latent-optimization/T2-z.git'
COMPAT = Path('/home/lc01/Zonglin Li/zonglin2/compat/glibc240')
GUARD = 25 * 1024**3


def receipt(root, stage, status, **fields):
    out = root / 'receipts'
    out.mkdir(parents=True, exist_ok=True)
    p = out / f'{time.time_ns()}_{stage}_{uuid.uuid4().hex[:8]}.json'
    data = dict(stage=stage, status=status, epoch=time.time(), source_commit=COMMIT,
                root=str(root), CPU_only=True, GPU_queried=False, training_started=False,
                archive_status='PENDING_ROOT_GIT', **fields)
    with p.open('x') as stream:
        json.dump(data, stream, indent=2)
    print(json.dumps(dict(receipt=str(p), status=status)))


def check_root(root):
    if root.resolve() != ROOT or str(root) != str(ROOT):
        raise RuntimeError('Only the exact approved research root is permitted')
    root.mkdir(parents=True, exist_ok=True)
    # Refuse an approved directory that has become a symlink to elsewhere.
    if root.resolve() != ROOT:
        raise RuntimeError('Research root resolves outside approved path')


def free_guard(root, anticipated=0):
    free = shutil.disk_usage(root).free
    if free - anticipated < GUARD:
        raise RuntimeError('Existing25GiB disk guard: own preparation stopped')
    return free


def run(argv, root, env, timeout=300, cwd=None):
    free_guard(root)
    # Fixed official URLs only, never token-bearing command arguments or logs.
    proc = subprocess.run(argv, env=env, cwd=cwd, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, timeout=timeout, check=False)
    log = root / 'receipts' / f'{time.time_ns()}_command.log'
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_bytes(proc.stdout)
    if proc.returncode:
        raise RuntimeError(f'Command failed rc={proc.returncode}; retained log={log.name}')
    return proc.stdout.decode(errors='replace')


def child_environment(root):
    # No shell tracing, credential lookup, inherited PYTHONPATH, global pip config,
    # or CUDA enumeration. Token/cookie/password/key variables are not propagated.
    allowed = ('PATH', 'LANG', 'LC_ALL', 'HOME', 'USER', 'SHELL', 'SSL_CERT_FILE', 'SSL_CERT_DIR')
    env = {k: os.environ[k] for k in allowed if k in os.environ}
    env.update(CUDA_VISIBLE_DEVICES='', NVIDIA_VISIBLE_DEVICES='none',
               OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1',
               NUMEXPR_NUM_THREADS='1', PYTHONNOUSERSITE='1', PYTHONDONTWRITEBYTECODE='1',
               PIP_CONFIG_FILE='/dev/null', PIP_NO_INPUT='1', PIP_DISABLE_PIP_VERSION_CHECK='1',
               PIP_CACHE_DIR=str(root/'cache/pip'), CONDA_PKGS_DIRS=str(root/'cache/conda'),
               CONDA_ENVS_PATH=str(root/'envs'), CONDARC='/dev/null', HF_HOME=str(root/'cache/huggingface'),
               HF_HUB_DISABLE_TELEMETRY='1', HF_HUB_DISABLE_IMPLICIT_TOKEN='1',
               XDG_CACHE_HOME=str(root/'cache/xdg'), TMPDIR=str(root/'staging'),
               GIT_TERMINAL_PROMPT='0', GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null')
    for d in ('cache/pip', 'cache/conda', 'cache/huggingface', 'cache/xdg', 'staging'):
        (root/d).mkdir(parents=True, exist_ok=True)
    return env


def py_command(python, *arguments):
    # Read-only reuse of the approved custom loader; no compatibility files copied,
    # rewritten, or borrowed from envs/mod4. Base libraries belong to new Python.
    loader = COMPAT/'ld-linux-x86-64.so.2'
    if not loader.is_file():
        raise RuntimeError('Existing glibc240 loader missing; do not install system libraries')
    prefix = python.parent.parent
    return [str(loader), '--library-path', f'{COMPAT}:{prefix}/lib:{ROOT}/bootstrap311/lib',
            str(python), '-B', *arguments]


def stage_source(root, env):
    src = root/'source'
    if not src.exists():
        src.mkdir()
        run(['git', 'init', str(src)], root, env, timeout=30)
    if not (src/'.git').is_dir():
        raise RuntimeError('Existing source is not an isolated Git working directory')
    if not (src/'README.md').is_file():
        run(['git', '-C', str(src), 'fetch', '--depth=1', URL, COMMIT], root, env, timeout=300)
        run(['git', '-C', str(src), 'checkout', '--detach', 'FETCH_HEAD'], root, env, timeout=60)
    head = run(['git', '-C', str(src), 'rev-parse', 'HEAD'], root, env, timeout=10).strip()
    dirty = run(['git', '-C', str(src), 'status', '--porcelain'], root, env, timeout=10).strip()
    if head != COMMIT or dirty:
        raise RuntimeError('Pinned source mismatch or dirty: preserve and investigate; no reset')
    receipt(root, 'source', 'SOURCE_PIN_VERIFIED', commit=head, free_bytes=free_guard(root))


def stage_environment(root, env, args):
    src = root/'source'
    head = run(['git', '-C', str(src), 'rev-parse', 'HEAD'], root, env, timeout=10).strip()
    if head != COMMIT:
        raise RuntimeError('Source stage required first')
    # Conservative estimate, not a new policy guard or measured allocation.
    free_guard(root, anticipated=35*1024**3)
    base = root/'bootstrap311/bin/python'
    if not base.is_file():
        conda = Path(args.conda)
        if not conda.is_file():
            raise RuntimeError('Known historical conda candidate absent; do not alter another environment')
        run([str(conda), 'create', '--yes', '--prefix', str(root/'bootstrap311'),
             '--override-channels', '--channel', 'https://repo.anaconda.com/pkgs/main',
             'python=3.11', 'pip'], root, env, timeout=args.command_timeout)
    version = run(py_command(base, '-c', 'import sys; print(sys.version_info[:2])'), root, env, timeout=20)
    if '(3, 11)' not in version:
        raise RuntimeError('Isolated Python must be3.11')
    vpy = root/'.venv/bin/python'
    if not vpy.is_file():
        run(py_command(base, '-m', 'venv', '--copies', str(root/'.venv')), root, env, timeout=60)
    wrapper = root/'run-t2z-python.sh'
    content = '#!/bin/bash\nset -euo pipefail\n' + \
        'R="/home/lc01/Zonglin Li/zonglin2/research/T2Z_H1_TRANSFER_PREP_20261025"\n' + \
        'C="/home/lc01/Zonglin Li/zonglin2/compat/glibc240"\n' + \
        'export PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1\nunset PYTHONPATH LD_PRELOAD\n' + \
        'exec "$C/ld-linux-x86-64.so.2" --library-path "$C:$R/.venv/lib:$R/bootstrap311/lib" "$R/.venv/bin/python" -B "$@"\n'
    if wrapper.exists() and wrapper.read_text() != content:
        raise RuntimeError('Existing wrapper differs: retained, no overwrite')
    if not wrapper.exists():
        wrapper.write_text(content)
        wrapper.chmod(0o755)
    run(py_command(vpy, '-m', 'pip', 'install', '--only-binary=:all:', '--index-url',
                   'https://download.pytorch.org/whl/cu128', 'torch==2.8.0',
                   'torchvision==0.23.0', 'torchaudio==2.8.0'), root, env, timeout=args.command_timeout)
    # Upstream has floating requirements. Capture the realized resolver result;
    # do not call it a prevalidated lock. No source builds are allowed silently.
    run(py_command(vpy, '-m', 'pip', 'install', '--only-binary=:all:', '--index-url',
                   'https://pypi.org/simple', '-r', str(src/'requirements.txt'),
                   'huggingface_hub>=0.34,<1.0'), root, env, timeout=args.command_timeout)
    run(py_command(vpy, '-m', 'pip', 'check'), root, env, timeout=30)
    freeze = run(py_command(vpy, '-m', 'pip', 'freeze', '--all'), root, env, timeout=30)
    lock = root/'receipts'/f'{time.time_ns()}_resolved_requirements.txt'
    lock.write_text(freeze)
    receipt(root, 'environment', 'INSTALLED_CPU_IMPORT_NOT_YET_CHECKED',
            python=str(vpy), resolved_requirements=str(lock), free_bytes=free_guard(root),
            GPU_driver_compatibility='UNTESTED', no_system_or_mod4_environment_modified=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage', choices=['source', 'environment'])
    p.add_argument('--root', type=Path, default=ROOT)
    p.add_argument('--conda', default='/home/lc01/miniconda3/bin/conda')
    p.add_argument('--command-timeout', type=int, default=600)
    args = p.parse_args()
    if not (30 <= args.command_timeout <= 1800):
        p.error('Command timeout must be bounded30..1800seconds')
    check_root(args.root)
    env = child_environment(args.root)
    try:
        if args.stage == 'source':
            stage_source(args.root, env)
        else:
            stage_environment(args.root, env, args)
    except Exception as exc:
        # Do not persist raw subprocess environment or arbitrary network errors.
        receipt(args.root, args.stage, 'FAILED_PRESERVED', error_type=type(exc).__name__,
                reason=str(exc)[:600])
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

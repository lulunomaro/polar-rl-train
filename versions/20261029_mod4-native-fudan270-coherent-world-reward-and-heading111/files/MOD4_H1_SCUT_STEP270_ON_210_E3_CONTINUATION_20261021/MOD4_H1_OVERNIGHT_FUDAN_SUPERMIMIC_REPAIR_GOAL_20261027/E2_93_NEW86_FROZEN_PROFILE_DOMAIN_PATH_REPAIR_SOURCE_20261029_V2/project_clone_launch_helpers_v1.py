from pathlib import Path
import hashlib, os
GPU = 'GPU-90a66ae2-f536-7033-79c0-487536ae36d3'

def H(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def own_identity(pid):
    p = Path('/proc') / str(pid)
    try:
        raw = (p / 'stat').read_text()
        a = raw[raw.rfind(')') + 2:].split()
        boot = next((int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime ')))
        return dict(pid=pid, creation=boot + int(a[19]) / os.sysconf('SC_CLK_TCK'), exe=os.readlink(p / 'exe'), argv=[os.fsdecode(x) for x in (p / 'cmdline').read_bytes().split(bytes([0])) if x], cwd=os.readlink(p / 'cwd'))
    except FileNotFoundError:
        return dict(pid=pid, initial_spawn_already_exited=True, worker_self_identity_required=True)

def environment(J, D, gpu):
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=GPU if gpu else '', PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1', PYTHONUNBUFFERED='1', OMNI_KIT_ACCEPT_EULA='YES', ISAACSIM_ACCEPT_EULA='Y')
    for k in ('PYTHONHOME', 'PYTHONPATH', 'LD_PRELOAD', 'LD_LIBRARY_PATH'):
        env.pop(k, None)
    names = {'HOME': 'home', 'TMPDIR': 'tmp', 'TMP': 'tmp', 'TEMP': 'tmp', 'XDG_CACHE_HOME': 'cache', 'XDG_CONFIG_HOME': 'config', 'XDG_DATA_HOME': 'data', 'XDG_STATE_HOME': 'state', 'XDG_RUNTIME_DIR': 'state/runtime', 'CUDA_CACHE_PATH': 'cache/nv', 'TORCH_HOME': 'cache/torch', 'PIP_CACHE_DIR': 'cache/pip', 'CONDA_PKGS_DIRS': 'cache/conda', 'TRITON_CACHE_DIR': 'cache/triton', 'WARP_CACHE_PATH': 'cache/warp', 'NUMBA_CACHE_DIR': 'cache/numba', 'MPLCONFIGDIR': 'cache/matplotlib', '__GL_SHADER_DISK_CACHE_PATH': 'cache/gl'}
    for k, rel in names.items():
        assert (J / rel).resolve().is_relative_to(J)
        env[k] = str(J / rel)
    env['CONDA_PREFIX'] = str(D / 'envs/mod4')
    env['PATH'] = str(D / 'envs/mod4/bin') + ':/usr/local/bin:/usr/bin:/bin'
    return env

def argv(D, worker, args):
    return [str(D / 'compat/glibc240/ld-linux-x86-64.so.2'), '--library-path', str(D / 'compat/glibc240') + ':' + str(D / 'envs/mod4/lib'), str(D / 'envs/mod4/bin/python'), '-u', '-B', str(worker)] + args

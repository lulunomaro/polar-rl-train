"""ROOT217 remote finite parent. Executed once through the existing transport.

No training/account/model actions. A timeout leaves the child's inherited EX FD
intact and reports failure; the consumed PID990366 permission is never reused.
"""
from pathlib import Path
import fcntl, hashlib, json, os, psutil, re, shutil, subprocess, time, traceback

B = Path(v['job'])
owned = Path('/home/lc01/Zonglin Li/zonglin2')
gpu = v['GPU_UUID']
assert B.resolve().is_relative_to((owned / 'tasks').resolve())


def put(name, value):
    with (B / name).open('x', encoding='utf8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


for row in v['files']:
    path = B / row['relative']
    assert path.resolve().is_relative_to(B.resolve()) and path.stat().st_size == row['bytes']
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    assert digest == row['SHA'], row['relative']
put('ROOT217_SOURCE_AND_BINARY_POSTCOPY_ACTUAL.json', dict(
    epoch=time.time(), passed=True, files=v['files'], necessary_postcopy_passes=1,
    source_checkpoint_opens=0, no_account_write=True))
put('RM70_BINARY_INSTALL_ACTUAL.json', dict(actual_postcopy_fullSHA_verified=True,
    files=[dict(relative=row['relative'].removeprefix('original_field/'),
                bytes=row['bytes'], SHA=row['SHA'])
           for row in v['files'] if row['relative'].startswith('original_field/')]))

lock = (owned / 'state' / ('three_expert_v2_' + gpu + '.lock')).open('rb+')
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
p = None
rc = None
error = None
resource = None
identity = None
started = time.time()
try:
    with (owned / 'state/finite_environment_validation.lock').open('rb+') as shared:
        fcntl.flock(shared, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(shared, fcntl.LOCK_UN)
    line = subprocess.check_output(['nvidia-smi', '-i', gpu,
        '--query-gpu=uuid,name,memory.free,utilization.gpu',
        '--format=csv,noheader,nounits'], text=True).strip()
    fields = [part.strip() for part in line.split(',')]
    ram = psutil.virtual_memory().available
    disk = shutil.disk_usage(B).free
    assert fields[0] == gpu and fields[1] == 'NVIDIA GeForce RTX 4090'
    assert int(fields[2]) > 15669 and int(fields[3]) <= 30
    assert ram > 32 * 1024**3 and disk > 25 * 1024**3
    resource = dict(epoch=time.time(), GPU_line=line, RAM_available=ram,
                    disk_free=disk, private_EX=True)
    put('ROOT217_RESOURCE_BEFORE_NEW_TASK_ACTUAL.json', resource)
    task = dict(v['task'], GPU_UUID=gpu,
        actual_parent_exclusive_control_GPU_private_shared_admission=True)
    put('MATERIAL0PT214_TASK.json', task)
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=gpu,
        PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1',
        OMNI_KIT_ACCEPT_EULA='YES', ISAACSIM_ACCEPT_EULA='Y')
    for name in ('PYTHONHOME', 'PYTHONPATH', 'LD_PRELOAD', 'RANK',
                 'LOCAL_RANK', 'WORLD_SIZE', 'MASTER_ADDR', 'MASTER_PORT'):
        env.pop(name, None)
    for name, suffix in {'HOME':'home', 'TMPDIR':'tmp', 'TMP':'tmp', 'TEMP':'tmp',
        'XDG_CACHE_HOME':'cache', 'XDG_CONFIG_HOME':'config', 'XDG_DATA_HOME':'data',
        'XDG_STATE_HOME':'state', 'XDG_RUNTIME_DIR':'state/runtime',
        'CUDA_CACHE_PATH':'cache/cuda', 'WARP_CACHE_PATH':'cache/warp',
        'TORCH_HOME':'cache/torch'}.items():
        target = B / 'private' / suffix
        target.mkdir(parents=True, exist_ok=True)
        env[name] = str(target)
    argv = [str(owned / 'run-python.sh'), '-u', '-B',
            str(B / 'runtime/isaac/mod4/material0pt214.py'), '--job-root', str(B)]
    with (B / 'ROOT217_FULL_STDOUT_STDERR.log').open('xb') as out:
        p = subprocess.Popen(argv, cwd=B, env=env, stdin=subprocess.DEVNULL,
            stdout=out, stderr=subprocess.STDOUT, pass_fds=(lock.fileno(),),
            start_new_session=True, close_fds=True)
    q = psutil.Process(p.pid)
    identity = dict(pid=q.pid, creation=q.create_time(), exe=q.exe(),
                    argv=q.cmdline(), cwd=q.cwd())
    put('ROOT217_ORIGINAL_WORKER_IDENTITY_BEFORE_WAIT.json', identity)
    rc = p.wait(timeout=1800)
    put('ROOT217_ORIGINAL_WAITED_EXIT_ACTUAL.json', dict(epoch=time.time(),
        returncode=rc, actual_waited=True, identity=identity))
except BaseException:
    error = traceback.format_exc()
    put('ROOT217_PARENT_ORIGINAL_ERROR.json', dict(error=error,
        no_automatic_retry=True, no_signals_or_unknown_PID_actions=True))
finally:
    waited = p is None or p.poll() is not None
    if waited:
        fcntl.flock(lock, fcntl.LOCK_UN)
    lock.close()
    put('ROOT217_PRIVATE_EX_EXIT_SCOPE_ACTUAL.json', dict(epoch=time.time(),
        all_own_children_waited=waited, private_EX_released=waited,
        timeout_does_not_authorize_termination=True,
        inherited_EX_FD_retained_if_original_child_alive=True))

output = B / 'material0pt214'
native_path = output / 'MATERIAL0PT214_NATIVE_RETURNED_ACTUAL.json'
native = json.loads(native_path.read_bytes()) if native_path.is_file() else None
metadata_path = output / 'MATERIAL214_PHASE_AND_SETTER_EVENTS.jsonl'
events = []
if metadata_path.is_file():
    events = [json.loads(line) for line in metadata_path.read_text('utf8').splitlines() if line]
phases = {event.get('phase') for event in events if event['kind'] == 'PHASE_BOUNDARY'}
required_phases = {'AFTER_FULL20K_ENV_CONSTRUCTION', 'AFTER_FRESH20K_RESET',
    'AFTER_OWN_SAME_VALUE_MILD_MATERIAL_REAPPLY', 'AFTER_ORIGINAL_NEW_EPISODE_RESET',
    'AFTER_8_NATIVE_CONTROLS', 'APP_CLOSING'}
terrain_rows = [event['terrain'] for event in events if 'terrain' in event]
terrain_checks = []
for terrain in terrain_rows:
    signatures = list(terrain.get('bound_material_attributes', {}).values())
    terrain_checks.append(bool(
        terrain.get('traversed_instance_proxy_collision_meshes') == 20000 and
        terrain.get('missing_material_bindings') == 0 and
        terrain.get('material_API_prim_count') == 1 and
        len(terrain.get('distinct_bound_material_paths', [])) == 1 and
        len(signatures) == 1 and
        abs(float(signatures[0].get('physics:staticFriction', -1)) - .9) < 1e-6 and
        abs(float(signatures[0].get('physics:dynamicFriction', -1)) - .8) < 1e-6 and
        abs(float(signatures[0].get('physics:restitution', -1))) < 1e-6))
full_log = B / 'ROOT217_FULL_STDOUT_STDERR.log'
stdout = full_log.read_bytes().decode('utf8', 'replace') if full_log.is_file() else ''
material_errors = [line for line in stdout.splitlines()
    if re.search(r'PxPhysics::createMaterial|limit\s+of\s*64K\s+materials\s+reached', line, re.I)]
result = dict(epoch=time.time(), started_epoch=started,
    passed=bool(rc == 0 and waited and not error and native and native.get('passed')
        and required_phases <= phases and terrain_checks and all(terrain_checks)
        and not material_errors),
    returncode=rc, all_own_children_waited=waited, private_EX_released=waited,
    parent_error=error, original_worker_identity=identity, resource=resource,
    native_result=native, actual_material_limit_error_count=len(material_errors),
    original_material_error_lines=material_errors, phase_evidence_complete=required_phases <= phases,
    missing_required_phases=sorted(required_phases - phases),
    actual_original_shared_CAD_material_checks=terrain_checks,
    PhysX_material_handle_count='UNKNOWN_NOT_USD_PRIM_COUNT',
    model_reads=0, actor_calls=0, optimizer_updates=0, account_writes=0,
    E0_not_signalled_or_modified=True, full_RM70_skill=False,
    PPO_fullstate_restore_or_first_update=False)
put('ROOT217_COMPLETE_ORIGINAL_PARENT_ACTUAL.json', result)
texts = []
for folder in (B, output, output / 'new_layout'):
    for path in sorted(folder.iterdir()) if folder.is_dir() else []:
        if path.is_file() and path.suffix in ('.json', '.jsonl', '.log', '.usda'):
            raw = path.read_bytes()
            texts.append(dict(path=str(path), bytes=len(raw),
                SHA=hashlib.sha256(raw).hexdigest(), UTF8=raw.decode('utf8', 'replace')))
result['full_UTF8'] = texts
print(json.dumps(result, allow_nan=False))

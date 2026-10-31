"""ROOT new full-scale model-free purpose, frozen214 source and existing210authority.

Nothing in the running E0 task or its writer/account is modified. PID990366
termination permission was consumed; this caller contains no termination path.
"""
from pathlib import Path
import argparse, ast, hashlib, importlib.util, json, os, subprocess, sys, time, traceback

N = Path(__file__).resolve().parent
T = N.parent
W = T.parent
R = N / 'reports'
S = T / 'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031'
F = T / 'W35_FULL_RM70_MATERIAL_LIMIT_REPAIR_SOURCE_V214_20261101'
K = T / 'W35_USER_AUTHORIZED_EXACT_PROCESS_TERMINATION_V216_20261101'
J = '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_RM70_SHARED_MATERIAL_20K_20261101v217/zeroPT_admission'


def read(path):
    return json.loads(Path(path).read_bytes())


def H(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(name, value):
    with (R / name).open('x', encoding='utf8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


AUTH = """from pathlib import Path
import json,hashlib,psutil,time
P=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=P.read_bytes();c=json.loads(raw)
x=v['binding'];O=Path(x['owner']['root']);cur=json.loads((O/'OWNER_CURRENT.json').read_bytes());ident=json.loads((O/'OWNER_IDENTITY.json').read_bytes())
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
assert c['active_segment']['owner_parent_pid']==x['owner']['pid'] and ident['creation']==x['owner']['creation']
assert cur['go']==x['go'] and x['run_id']=='PARALLEL210_E0_3H_RM70_1H_1793463669094560900'
p=psutil.Process(x['owner']['pid']);assert p.create_time()==x['owner']['creation'] and p.exe()==x['owner']['exe'] and p.cmdline()==x['owner']['argv'] and p.cwd()==x['owner']['cwd']
try:
 q=psutil.Process(990366);assert q.create_time()!=1793463868.49 or q.status()==psutil.STATUS_ZOMBIE
except psutil.NoSuchProcess:pass
assert cur['rows']['w35_72']['phase']=='terminal' and cur['rows']['w35_72']['returncode']==-9
print(json.dumps(dict(epoch=time.time(),passed=True,current_owner_pid=p.pid,current_owner_creation=p.create_time(),run_id=x['run_id'],go=cur['go'],original_W35_worker_OUT=True,canonical_SHA=hashlib.sha256(raw).hexdigest(),no_C_write=True,no_E0_change=True)))
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root-lease-label', required=True)
    args = parser.parse_args()
    assert args.root_lease_label.startswith('ROOT217_EXCLUSIVE_20K_MATERIAL_')
    prior_exit = read(K / 'reports/ROOT216_ORIGINAL_POST_SIGNAL_EXIT_AND_NODE_RECEIPTS_ACTUAL.json')
    assert prior_exit['private_EX_free'] and prior_exit['original_worker_status']['original_out']
    assert read(K / 'reports/ROOT216_EXIT_COLLECTION_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease'] == 'FREE'
    assert H(F / 'INDEX214_FROZEN.json') == '8a27849574f33e5d7e0c619526ddfead25ac57c54bede975315082e2a25ce171'
    frozen = read(F / 'INDEX214_FROZEN.json')
    contract = read(F / 'reports/TARGET214_REQUIRED_20K_ZERO_PT_PURPOSE.json')
    rows = {}
    production = read(S / 'PACKAGE210_W35_MANIFEST.json')
    for row in production['files']:
        relative = row['relative']
        if not (relative.startswith(('runtime/', 'original_field/')) or relative == 'original_run_manifest.json'):
            continue
        assert Path(relative).suffix.lower() != '.pt'
        path = Path(row['local_path']) if row.get('local_path') else S / row['local_relative']
        assert path.stat().st_size == row['bytes'], relative
        if path.suffix.lower() not in ('.pt', '.npz', '.usd', '.usdc', '.usda'):
            assert H(path) == row['SHA'], str(path)
        rows[relative] = dict(relative=relative, local=str(path), bytes=row['bytes'], SHA=row['SHA'])
    selected_names = {'config214.py', 'field214.py', 'material0pt214.py',
                      'material214.py', 'mild_dr214.py', 'restore214.py', 'usd214.py'}
    for row in frozen['files']:
        if row['relative'].startswith('source/') and Path(row['relative']).name in selected_names:
            path = Path(row['path'])
            assert path.stat().st_size == row['bytes'] and H(path) == row['SHA']
            ast.parse(path.read_bytes(), filename=str(path))
            relative = 'runtime/isaac/mod4/' + path.name
            rows[relative] = dict(relative=relative, local=str(path), bytes=row['bytes'], SHA=row['SHA'])
    assert selected_names <= {Path(relative).name for relative in rows}
    rows = list(rows.values())
    worker_SHA = contract['entry']['SHA']
    assert next(row['SHA'] for row in rows if row['relative'] == 'runtime/isaac/mod4/material0pt214.py') == worker_SHA
    parent_path = N / 'root217_material_parent.py'
    code = parent_path.read_text('utf8')
    ast.parse(code)
    assert 'SIGKILL' not in code and 'send_signal' not in code
    binding = read(S / 'reports/KNOWN_ACTIVE210_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json')
    query = r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'install217_20k_shared_material_zeroPT_once|collect216_original_|terminate216_only_|stop215_exact_|launch210_|collect210_|prepare212_|install211_|install209_|launch209_|install208_|launch208_' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
    result = subprocess.run(['pwsh.exe', '-NoProfile', '-Command', query], capture_output=True,
        text=True, encoding='utf8', check=True)
    cim = json.loads(result.stdout) if result.stdout.strip() else []
    cim = cim if isinstance(cim, list) else [cim]
    own = [row for row in cim if row['ProcessId'] == os.getpid()]
    other = [row for row in cim if row['ProcessId'] != os.getpid()]
    put('ROOT217_FRESH_LOCAL_EXACT_CIM.json', dict(epoch=time.time(), PID=os.getpid(),
        exe=sys.executable, argv=sys.argv, rows=cim, other_known_control_finites=other))
    assert len(own) == 1 and own[0]['ExecutablePath'].lower() == sys.executable.lower()
    assert own[0]['CreationDate'] and not other
    assert str(Path(__file__).resolve()).lower().replace('\\', '/') in own[0]['CommandLine'].lower().replace('\\', '/')
    put('ROOT217_SOURCE_AND_PURPOSE_ONCE_CONSUMED_BEFORE_NETWORK.json', dict(
        epoch=time.time(), root_lease_label=args.root_lease_label,
        source214_index_SHA=H(F / 'INDEX214_FROZEN.json'), parent_SHA=H(parent_path),
        original_task_contract=contract, files=rows, source_checkpoint_reads=0,
        original_RESET_COLLISION_BANK_constructor_loads=1, original_CAD_query_constructor_loads=1,
        source_binary_postcopy_hash_passes=1, actual_phase_metadata_JSONL_pass=1,
        full_owned_stdout_and_new_reports_capture=True, max_parent_wait=1800,
        no_new_PPO_or_writer_or_account_or_E0_change=True,
        original_exact_990366_termination_permission_consumed_not_reused=True))
    wrapper = module('material217_transport', T / 'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
    sys.path.insert(0, str(W / 'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
    import deploy_two50_reconciled_original_writer_once as d
    client = None
    transport = None
    previous = None
    secret = None
    try:
        transport, previous = wrapper.install()
        sec = module('material217_memory', W / 'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')
        secret = sec.recover()
        client = d.connect72(secret)
        secret = None
        put('ROOT217_FRESH72_EXACT_ACTIVE210_BEFORE_MODEL_FREE_TASK.json',
            d.code(client, d.PY72, AUTH, dict(binding=binding), timeout=45))
        create = """from pathlib import Path
import json
B=Path(v['job']);assert B.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve());B.mkdir(parents=True,exist_ok=False)
print(json.dumps(dict(passed=True,new_root=str(B),new_namespace_only=True)))"""
        put('ROOT217_NEW_NAMESPACE_CREATED.json', d.code(client, d.PY72, create, dict(job=J), timeout=30))
        sf = client.open_sftp()
        sf.get_channel().settimeout(120)
        try:
            made = set()
            for row in rows:
                current = J
                for bit in row['relative'].split('/')[:-1]:
                    current += '/' + bit
                    if current not in made:
                        try:
                            sf.mkdir(current)
                        except OSError:
                            sf.stat(current)
                        made.add(current)
                sf.put(row['local'], J + '/' + row['relative'])
            sf.put(str(parent_path), J + '/root217_material_parent.py')
        finally:
            sf.close()
        print(json.dumps(dict(epoch=time.time(), status='NEW20K_MODEL_FREE_SHARED_MATERIAL_PROBE_ENTERED',
            E0_unchanged=True, no_model_or_PPO=True, maximum_original_wait_seconds=1800)), flush=True)
        result = d.code(client, d.PY72, code, dict(job=J, files=rows,
            GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',
            task=contract['task_fields']), timeout=1920)
        put('ROOT217_ORIGINAL_20K_SHARED_MATERIAL_NATIVE_OR_ERROR_RETURNED_ACTUAL.json', result)
        print(json.dumps({key: result[key] for key in ('passed', 'returncode',
            'all_own_children_waited', 'private_EX_released', 'parent_error',
            'actual_material_limit_error_count', 'missing_required_phases',
            'actual_original_shared_CAD_material_checks')}), flush=True)
    finally:
        secret = None
        if client is not None:
            client.close()
            client = None
        if transport is not None:
            transport.SESSION = previous
        put('ROOT217_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json', dict(epoch=time.time(),
            all_owned_SSH_closed=client is None,
            SESSION_restored=transport is None or transport.SESSION is previous,
            global_serial_control_client_lease='FREE'))


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        put('ROOT217_LOCAL_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json', dict(
            error=traceback.format_exc(), no_automatic_replay=True))
        raise

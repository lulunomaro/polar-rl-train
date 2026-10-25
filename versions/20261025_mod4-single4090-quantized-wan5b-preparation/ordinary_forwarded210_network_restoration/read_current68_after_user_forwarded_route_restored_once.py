"""New missing-only current68 reader after human restored SSH route. Never run old reader."""
from pathlib import Path
import ast, hashlib, json, os, sys, time, traceback

Q = Path(__file__).resolve().parent
T, W = Q.parent, Q.parent.parent
R = Q / 'reports'
N = T / 'H1_STEP270_REWARD_SAGITTAL_TUCK_V6A_RESOURCE_V68_20261025'

def put(name, value):
    with (R / name).open('x', encoding='utf8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)

put('CURRENT68_FORWARDED_ROUTE_RESTORED_READER_STARTED_ACTUAL.json', {
    'epoch': time.time(), 'pid': os.getpid(), 'argv': sys.argv,
    'source_endpoint': ['10.24.5.27', 4090],
    'scope': 'Existing68 own text, exact own process identities, original budget read, released-lock check only',
})
try:
    auth = json.loads((R / 'USER_FORWARD4090_INTERNAL22_STRICT_SSH_RETURNED_ACTUAL.json').read_bytes())
    assert auth['SSH_authenticated'] and auth['original_host_key_matches'] and auth['connection_actual_returned']
    old = N / 'read_current68_owner_H1_original_account_after_network_retry_once.py'
    raw = old.read_bytes()
    module = ast.parse(raw.decode('utf8'))
    codes = [node.value.value for node in module.body if isinstance(node, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == 'CODE' for t in node.targets)
             and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)]
    assert len(codes) == 1
    q = json.loads((N / 'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes())
    meta = json.loads((N / 'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes())
    sys.path.insert(0, str(W / 'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
    import deploy_two50_reconciled_original_writer_once as d
    sys.path.insert(0, str(Q))
    import strict_user_forwarded_original210_transport_v1 as route
    c = route.connect()
    try:
        result = d.code(c, route.PY, codes[0], {'q': q, 'metadata': meta}, timeout=45)
    finally:
        c.close()
    result['forwarded_route'] = {'host': route.HOST, 'port': route.PORT, 'original_identity': route.ORIGINAL_HOST}
    result['reader_remote_CODE_SHA'] = hashlib.sha256(codes[0].encode()).hexdigest()
    result['original_failed_reader_not_reexecuted'] = {'path': str(old), 'SHA': hashlib.sha256(raw).hexdigest(), 'method': 'AST extract remote CODE only, no import/runpy'}
    result['connection_actual_returned'] = True
    put('CURRENT68_FORWARDED_ROUTE_RESTORED_READER_RETURNED_ACTUAL.json', result)
    snaps = result['snapshots']
    print(json.dumps({'strict_original_pin_authenticated': True,
                      'current68_completed_original_segments': result['original_account_summary']['current68_completed_original_segments'],
                      'remaining_actual_snapshot': result['original_account_summary']['remaining_actual_snapshot'],
                      'active_segment': result['original_account_summary']['active_segment'],
                      'own_process_identity_snapshot': result['actual_own_process_identity_snapshot'],
                      'original_lock_snapshot': result['original_lock_snapshot'],
                      'H1_FINAL': snaps['H1_FINAL'],
                      'cohort_final_exists': snaps['cohort_final'].get('exists', True),
                      'owner_exit_exists': snaps['owner_exit'].get('exists', True),
                      'connection_actual_returned': True}, ensure_ascii=False))
except BaseException:
    put('CURRENT68_FORWARDED_ROUTE_RESTORED_READER_ORIGINAL_ERROR_ACTUAL.json', {
        'epoch': time.time(), 'error': traceback.format_exc(),
        'no_canonical_write_or_new_writer_or_training_change': True,
    })
    raise

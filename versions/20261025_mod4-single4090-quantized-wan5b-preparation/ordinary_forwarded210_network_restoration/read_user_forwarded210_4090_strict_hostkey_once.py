"""User changed forwarded internal port to 22; authenticate only after original pin matches."""
from pathlib import Path
import base64, hashlib, json, os, socket, sys, time, traceback
import paramiko

Q = Path(__file__).resolve().parent
W = Q.parent.parent
R = Q / 'reports'
ENDPOINT = ('10.24.5.27', 4090)
ORIGINAL = '10.24.4.210'

def put(name, value):
    with (R / name).open('x', encoding='utf8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)

put('USER_FORWARD4090_INTERNAL22_STRICT_SSH_STARTED_ACTUAL.json', {
    'epoch': time.time(), 'pid': os.getpid(), 'argv': sys.argv,
    'human': '已经修改到22', 'endpoint': list(ENDPOINT),
    'original_pinned_host': ORIGINAL,
})

result = {'endpoint': list(ENDPOINT), 'started_epoch': time.time(),
          'tcp_connected': False, 'original_host_key_matches': False,
          'SSH_authenticated': False, 'remote_commands_executed': 0,
          'no_training_budget_lock_model_or_GPU_change': True}
transport = sock = secret = None
try:
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    expected = client.get_host_keys().lookup(ORIGINAL)
    if expected is None:
        expected = client._system_host_keys.lookup(ORIGINAL)
    assert expected, 'Original host pin is required'
    sock = socket.create_connection(ENDPOINT, timeout=10)
    result['tcp_connected'] = True
    transport = paramiko.Transport(sock)
    options = transport.get_security_options()
    options.key_types = tuple(k for k in options.key_types if k in expected)
    assert options.key_types, 'No common original pinned host-key algorithm'
    transport.start_client(timeout=12)
    key = transport.get_remote_server_key()
    result['SSH_banner'] = transport.remote_version
    result['host_key_type'] = key.get_name()
    result['host_key_SHA256'] = 'SHA256:' + base64.b64encode(hashlib.sha256(key.asbytes()).digest()).decode().rstrip('=')
    assert key.get_name() in expected and key.asbytes() == expected[key.get_name()].asbytes(), 'Forwarded server does not match original host pin; credentials not sent'
    result['original_host_key_matches'] = True
    sys.path.insert(0, str(W / 'RM2026_TERRAIN_AUDIT_20261009'))
    from reuse_authorized_session_transport import recover
    secret, _ = recover('RM_SSH_PASSWORD')
    assert secret
    transport.auth_timeout = 12
    transport.auth_password('egde', secret, fallback=False)
    secret = None
    assert transport.is_authenticated()
    result['SSH_authenticated'] = True
except BaseException as e:
    result['error_type'] = type(e).__name__
    result['original_error'] = traceback.format_exc()
finally:
    secret = None
    if transport is not None:
        transport.close()
    elif sock is not None:
        sock.close()
result['finished_epoch'] = time.time()
result['connection_actual_returned'] = True
put('USER_FORWARD4090_INTERNAL22_STRICT_SSH_RETURNED_ACTUAL.json', result)
print(json.dumps({k: v for k, v in result.items() if k != 'original_error'}, ensure_ascii=False))

"""Original210 identity through human router forwarding; original credentials and pins only."""
from pathlib import Path
import sys
import paramiko

W = Path(__file__).resolve().parents[2]
HOST, PORT, ORIGINAL_HOST = '10.24.5.27', 4090, '10.24.4.210'
PY = '/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'

def connect():
    c = paramiko.SSHClient()
    c.load_system_host_keys()
    c.set_missing_host_key_policy(paramiko.RejectPolicy())
    expected = c._system_host_keys.lookup(ORIGINAL_HOST)
    assert expected, 'Original210 pinned host keys required'
    alias = '[' + HOST + ']:' + str(PORT)
    existing = c._system_host_keys.lookup(alias)
    if existing:
        assert all(k in expected and v.asbytes() == expected[k].asbytes() for k, v in existing.items())
    for key_type, key in expected.items():
        c.get_host_keys().add(alias, key_type, key)
    sys.path.insert(0, str(W / 'RM2026_TERRAIN_AUDIT_20261009'))
    from reuse_authorized_session_transport import recover
    secret, _ = recover('RM_SSH_PASSWORD')
    assert secret
    try:
        c.connect(HOST, port=PORT, username='egde', password=secret,
                  look_for_keys=False, allow_agent=False, timeout=12,
                  banner_timeout=12, auth_timeout=12)
        key = c.get_transport().get_remote_server_key()
        assert key.get_name() in expected and key.asbytes() == expected[key.get_name()].asbytes()
        assert c.get_transport().is_authenticated()
        c.get_transport().set_keepalive(15)
        return c
    except BaseException:
        c.close()
        raise
    finally:
        secret = None

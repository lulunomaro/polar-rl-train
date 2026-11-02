from pathlib import Path
import json, shlex, sys
import paramiko
W = Path(__file__).resolve().parent.parent
PY = '<string-1>'

def connect():
    sys.path.insert(0, str(W / '<string-2>'))
    from reuse_authorized_session_transport import recover
    secret, _ = recover('<string-3>')
    assert secret
    c = paramiko.SSHClient()
    c.load_system_host_keys()
    c.set_missing_host_key_policy(paramiko.RejectPolicy())
    assert c._system_host_keys.lookup('<string-4>')
    try:
        c.connect('<string-5>', username='<string-6>', password=secret, look_for_keys=False, allow_agent=False, timeout=15, banner_timeout=15, auth_timeout=15)
        c.get_transport().set_keepalive(15)
        key = c.get_transport().get_remote_server_key()
        assert c._system_host_keys.lookup('<string-7>')[key.get_name()].asbytes() == key.asbytes()
        return c
    finally:
        secret = None

def code(c, source, payload=None, timeout=90):
    v = dict(payload or {}, code=source)
    i, o, e = c.exec_command(shlex.quote(PY) + '<string-8>' + shlex.quote('<string-9>'), timeout=timeout)
    i.write(json.dumps(v) + '<string-10>')
    i.flush()
    i.channel.shutdown_write()
    v.clear()
    raw = o.read().decode()
    error = e.read().decode()
    rc = o.channel.recv_exit_status()
    assert rc == 0, (rc, error, raw)
    return json.loads(raw)
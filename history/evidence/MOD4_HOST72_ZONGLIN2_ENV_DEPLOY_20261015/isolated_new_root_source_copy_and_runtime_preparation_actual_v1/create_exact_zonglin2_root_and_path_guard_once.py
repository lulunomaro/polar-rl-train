"""Create only the human-named target directory; never delete or overwrite."""
from pathlib import Path
import getpass
import hashlib
import json
import shlex
import time
import traceback
import paramiko

D = Path(__file__).resolve().parent
R = D / 'reports'
W = D.parent
ROOT = '/home/lc01/Zonglin Li/zonglin2'
CODE = r'''
from pathlib import Path
import json,os,shutil,subprocess,time
base=Path('/home/lc01/Zonglin Li');assert base.is_dir() and not base.is_symlink()
root=base/'zonglin2';assert not root.exists() and not root.is_symlink(),'Existing target: inspect before reusing, never overwrite.'
assert base.resolve()==base and root.resolve().parent==base
os.umask(0o077);root.mkdir()
for name in ('audit','downloads','envs','src','assets','cache','tmp','logs','home','config','state'):
 (root/name).mkdir()
v=dict(epoch=time.time(),root=str(root.resolve()),base=str(base.resolve()),new_directory_created=True,
 no_existing_item_deleted_or_overwritten=True,all_remote_writes_must_resolve_below_root=True,
 original_base_names=sorted(p.name for p in base.iterdir() if p.name!='zonglin2'),
 free_bytes=shutil.disk_usage(root).free,os_release=Path('/etc/os-release').read_text(),
 glibc=subprocess.check_output(['getconf','GNU_LIBC_VERSION'],text=True).strip(),
 no_system_driver_userprofile_conda_or_existing_environment_mutation=True)
(root/'audit/ROOT_CREATED_ACTUAL.json').write_text(json.dumps(v,indent=2))
print(json.dumps(v))
'''


def main():
    R.mkdir(exist_ok=True)
    assert not (R / 'TARGET_ZONGLIN2_ROOT_CREATED_ACTUAL.json').exists()
    prev = json.loads((W / 'MOD4_HOST72_DUAL4090_ENV_READONLY_20261015/reports/HOST72_READONLY_DISCOVERY_ACTUAL.json').read_bytes())
    c = paramiko.SSHClient()
    c.load_system_host_keys()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    password = getpass.getpass('Host72 SSH password (hidden, not saved): ')
    try:
        c.connect(prev['host'], username=prev['user'], password=password, timeout=15, auth_timeout=20,
                  banner_timeout=20, allow_agent=False, look_for_keys=False)
        password = None
        assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest() == prev['remote_host_key_SHA256_hex']
        _, so, se = c.exec_command('python3 -B -c ' + shlex.quote(CODE), timeout=35)
        out, err, rc = so.read(), se.read(), so.channel.recv_exit_status()
        assert rc == 0, dict(returncode=rc, stderr=err.decode())
        value = json.loads(out)
        with (R / 'TARGET_ZONGLIN2_ROOT_CREATED_ACTUAL.json').open('x', encoding='utf8') as f:
            json.dump(value, f, indent=2, ensure_ascii=False)
        print(json.dumps(value, ensure_ascii=False), flush=True)
    finally:
        password = None
        c.close()


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        R.mkdir(exist_ok=True)
        with (R / ('TARGET_ROOT_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json')).open('x', encoding='utf8') as f:
            json.dump(dict(error=traceback.format_exc(), no_deletion_or_blind_retry=True), f, indent=2)
        raise

"""Private userspace ABI support inside zonglin2 only, after an actual native ABI failure."""
from pathlib import Path
import getpass
import hashlib
import io
import json
import shlex
import sys
import tarfile
import time
import traceback
import paramiko

D = Path(__file__).resolve().parent
W = D.parent
R = D / 'reports'
ROOT = '/home/lc01/Zonglin Li/zonglin2'
sys.path.insert(0, str(W / 'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as t


def main():
    actual = json.loads((R / 'TARGET_NATIVE_CPU_ABI_AND_SOURCE_V1_ACTUAL.json').read_bytes())
    assert 'GLIBC_' in json.dumps(actual), 'Only use for an observed GLIBC ABI error; no speculative system replacement.'
    assert not (R / 'PRIVATE_GLIBC_COPY_COMPLETE_ACTUAL.json').exists()
    prior = json.loads((W / 'MOD4_HOST72_DUAL4090_ENV_READONLY_20261015/reports/HOST72_READONLY_DISCOVERY_ACTUAL.json').read_bytes())
    c = paramiko.SSHClient()
    c.load_system_host_keys()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    password = getpass.getpass('Host72 SSH password (hidden, not saved): ')
    src = sf = None
    try:
        c.connect(prior['host'], username=prior['user'], password=password, timeout=15,
            auth_timeout=20, banner_timeout=20, allow_agent=False, look_for_keys=False)
        password = None
        assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest() == prior['remote_host_key_SHA256_hex']
        src = t.connect()
        code = r'''
from pathlib import Path
import io,os,sys,tarfile
names=['ld-linux-x86-64.so.2','libc.so.6','libm.so.6','libdl.so.2','libpthread.so.0','librt.so.1','libutil.so.1','libresolv.so.2','libnss_dns.so.2','libnss_files.so.2']
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|gz') as z:
 for name in names:
  p=Path('/lib/x86_64-linux-gnu')/name
  if not p.exists():
   if name.startswith('libnss_'):continue
   raise FileNotFoundError(str(p))
  actual=p.resolve();data=actual.read_bytes();m=tarfile.TarInfo(name);m.size=len(data);m.mode=0o755;z.addfile(m,io.BytesIO(data))
 p=Path('/usr/share/doc/libc6/copyright')
 if p.exists():
  data=p.read_bytes();m=tarfile.TarInfo('copyright');m.size=len(data);m.mode=0o644;z.addfile(m,io.BytesIO(data))
'''
        si, so, se = src.exec_command('PYTHONDONTWRITEBYTECODE=1 ' + shlex.quote(t.PY) + ' -B -', timeout=60)
        si.write(code)
        si.flush()
        si.channel.shutdown_write()
        data, err, rc = so.read(), se.read(), so.channel.recv_exit_status()
        assert rc == 0, err.decode('utf8','replace')
        source_sha = hashlib.sha256(data).hexdigest()
        sf = c.open_sftp()
        sf.mkdir(ROOT + '/compat')
        sf.mkdir(ROOT + '/compat/glibc240')
        with sf.open(ROOT + '/downloads/source4090_private_glibc240_v1.tar.gz', 'wx') as f:
            f.write(data)
        members = []
        with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as z:
            for member in z:
                assert member.isfile() and '/' not in member.name and '..' not in member.name
                b = z.extractfile(member).read()
                dest = ROOT + '/compat/glibc240/' + member.name
                with sf.open(dest, 'wx') as f:
                    f.write(b)
                sf.chmod(dest,member.mode)
                with sf.open(dest,'rb') as f:
                    assert hashlib.sha256(f.read()).hexdigest() == hashlib.sha256(b).hexdigest()
                members.append(dict(path=dest,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
        native = sf.open(ROOT+'/run-python-native.sh','r').read().decode()
        old = 'exec "$CONDA_PREFIX/bin/python" -B "$@"'
        new = 'exec "$ROOT/compat/glibc240/ld-linux-x86-64.so.2" --library-path "$ROOT/compat/glibc240:$CONDA_PREFIX/lib" "$CONDA_PREFIX/bin/python" -B "$@"'
        assert native.count(old) == 1
        wrapper = native.replace(old,new)
        with sf.open(ROOT+'/run-python-compat.sh','wx') as f:
            f.write(wrapper.encode())
        sf.chmod(ROOT+'/run-python-compat.sh',0o700)
        v = dict(epoch=time.time(),source_private_bundle_SHA=source_sha,bytes=len(data),members=members,
            wrapper=ROOT+'/run-python-compat.sh',only_new_owned_copy_and_private_userspace_loader=True,
            actual_CPU_GPU_runtime_still_requires_validation=True,
            no_system_libc_driver_kernel_NVIDIA_driver_libraries_userprofile_install_or_deletion=True,
            original_native_ABI_failure_and_archive_retained=True)
        with sf.open(ROOT+'/audit/PRIVATE_GLIBC_COPY_COMPLETE_ACTUAL.json','wx') as f:
            f.write(json.dumps(v,indent=2).encode())
        with (R/'PRIVATE_GLIBC_COPY_COMPLETE_ACTUAL.json').open('x',encoding='utf8') as f:
            json.dump(v,f,indent=2)
        print(json.dumps(dict(copied=True,files=len(members),bytes=len(data),source_SHA=source_sha,
            no_system_or_driver_change=True)),flush=True)
    finally:
        password = None
        if sf:sf.close()
        t.close(src)
        c.close()


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        with (R/('PRIVATE_GLIBC_COPY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:
            json.dump(dict(error=traceback.format_exc(),all_originals_retained=True,
                no_system_modification_delete_or_blind_replay=True),f,indent=2)
        raise

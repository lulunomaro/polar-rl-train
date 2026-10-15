"""Root-owned source4090 -> host72 stream relay. All target writes are under zonglin2.

Original archives and files are retained. No deletion, source mutation, install,
simulation, training, process signal, system profile or driver modification.
"""
from pathlib import Path
import getpass
import hashlib
import json
import os
import shlex
import subprocess
import sys
import time
import traceback
import paramiko

D = Path(__file__).resolve().parent
R = D / 'reports'
W = D.parent
ROOT = '/home/lc01/Zonglin Li/zonglin2'
ARCHIVE = ROOT + '/downloads/source4090_environment_and_lab_v1.tar.gz'
SOURCE_ENV = '/home/egde/anaconda3/envs/fangzhen-isaaclab'
SOURCE_PROJECT = '/home/egde/fangzhen_linux'
LAB = 'third_party/IsaacLab-3.0.0-beta2.patch1'
sys.path.insert(0, str(W / 'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as source_transport


def put(name, value, unique=True):
    p = R / name
    with p.open('x' if unique else 'w', encoding='utf8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)


def remote_json(client, code, timeout=120, python='python3'):
    si, so, se = client.exec_command(shlex.quote(python) + ' -B -', timeout=timeout)
    si.write(code)
    si.flush()
    si.channel.shutdown_write()
    out, err = so.read(), se.read()
    rc = so.channel.recv_exit_status()
    if rc:
        raise RuntimeError(json.dumps(dict(returncode=rc, stderr=err.decode('utf8','replace'))))
    return json.loads(out)


def main():
    assert not (R / 'SOURCE4090_TO_ZONGLIN2_TRANSFER_STARTED.json').exists(), 'Consumed transfer: inspect actual partial/complete before any continuation.'
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
        target = remote_json(c, 'ROOT=' + repr(ROOT) + '\nARCHIVE=' + repr(ARCHIVE) + r'''
from pathlib import Path
import json,shutil
r=Path(ROOT);assert r.resolve()==r and r.is_dir() and not r.is_symlink()
assert Path(ARCHIVE).resolve().is_relative_to(r) if hasattr(Path(ARCHIVE),'is_relative_to') else str(Path(ARCHIVE).resolve()).startswith(str(r)+'/')
assert not Path(ARCHIVE).exists()
assert shutil.disk_usage(r).free>140*1024**3
print(json.dumps(dict(root=str(r),free_bytes=shutil.disk_usage(r).free,new_archive=True)))
''')
        src = source_transport.connect()
        context = dict(environment=SOURCE_ENV, project=SOURCE_PROJECT, lab=LAB)
        inventory = remote_json(src, 'C=' + repr(context) + r'''
from pathlib import Path
import hashlib,json,os,subprocess,time
e=Path(C['environment']);p=Path(C['project']);lab=p/C['lab']
assert e.is_dir() and lab.is_dir()
paths=['isaac','robot','cad','scripts','train',C['lab']]
assert all((p/x).is_dir() for x in paths)
meta={str(x.relative_to(e)):hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted((e/'conda-meta').glob('*.json'))}
print(json.dumps(dict(epoch=time.time(),environment=str(e),project=str(p),project_paths=paths,
 environment_conda_metadata_SHA=meta,
 source_sizes=subprocess.check_output(['du','-sb',str(e),*[str(p/x) for x in paths]],text=True),
 no_source_file_write=True)))
''', python=source_transport.PY)
        ci = subprocess.run(['powershell','-NoProfile','-Command',
            '$p=Get-CimInstance Win32_Process -Filter "ProcessId = '+str(os.getpid())+'";$p|Select-Object ProcessId,CreationDate,CommandLine|ConvertTo-Json -Compress'],
            capture_output=True,text=True,encoding='utf8',check=True)
        started = dict(epoch=time.time(), pid=os.getpid(), actual_CIM=json.loads(ci.stdout),
            argv=sys.argv, root=ROOT, archive=ARCHIVE, source=inventory, target=target,
            sole_human_authorized210_to72_copy_relay_owner_while_actual_alive=True,
            no249_connection_PPO_or_budget=True, no_deletion_or_existing_file_overwrite=True,
            script_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
        put('SOURCE4090_TO_ZONGLIN2_TRANSFER_STARTED.json', started)
        remote_json(c, 'ROOT=' + repr(ROOT) + '\nV=' + repr(started) + r'''
from pathlib import Path
import json
r=Path(ROOT);p=r/'audit/SOURCE4090_TRANSFER_INTENT_ACTUAL.json';assert not p.exists()
p.write_text(json.dumps(V,indent=2));print(json.dumps(dict(intent_saved=True)))
''')
        args = ['tar','--warning=no-file-ignored','--exclude=__pycache__','--exclude=*.pyc',
                '-I','gzip -1','-cf','-','-C',str(Path(SOURCE_ENV).parent),Path(SOURCE_ENV).name,
                '-C',SOURCE_PROJECT,*inventory['project_paths']]
        _, so, se = src.exec_command(shlex.join(args), timeout=90)
        so.channel.settimeout(90)
        sf = c.open_sftp()
        sf.get_channel().settimeout(90)
        f = sf.open(ARCHIVE, 'wx')
        f.set_pipelined(True)
        h = hashlib.sha256()
        count = 0
        last = begin = time.time()
        with f:
            while True:
                block = so.read(1024*1024)
                if not block:
                    break
                f.write(block)
                h.update(block)
                count += len(block)
                if time.time()-last >= 20:
                    progress = dict(epoch=time.time(), pid=os.getpid(), phase='source_to_target_archive_stream',
                        compressed_bytes=count, elapsed_seconds=time.time()-begin,
                        mean_MiB_s=count/(time.time()-begin)/1024**2)
                    put('SOURCE4090_TO_ZONGLIN2_TRANSFER_CURRENT.json',progress,False)
                    print(json.dumps(progress),flush=True)
                    last = time.time()
        error = se.read().decode('utf8','replace')
        rc = so.channel.recv_exit_status()
        put('SOURCE4090_ARCHIVE_STREAM_EXIT_ACTUAL.json',dict(epoch=time.time(),returncode=rc,stderr=error,
            compressed_bytes=count,sha256=h.hexdigest(),original_archive_retained=True))
        assert rc == 0, error
        verify = remote_json(c, 'ROOT=' + repr(ROOT) + '\nARCHIVE=' + repr(ARCHIVE) + r'''
from pathlib import Path
import hashlib,json,time
p=Path(ARCHIVE);h=hashlib.sha256()
with p.open('rb') as f:
 for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
v=dict(epoch=time.time(),path=str(p),bytes=p.stat().st_size,sha256=h.hexdigest(),archive_retained=True)
q=Path(ROOT)/'audit/SOURCE_ARCHIVE_STREAM_SHA_ACTUAL.json';assert not q.exists();q.write_text(json.dumps(v,indent=2))
print(json.dumps(v))
''', timeout=240)
        assert verify['bytes'] == count and verify['sha256'] == h.hexdigest()
        complete = dict(epoch=time.time(), archive=verify, source=inventory, stream_elapsed_seconds=time.time()-begin,
            source_stream_target_SHA_exact=True, source_unchanged_readonly=True,
            no_extraction_or_runtime_admission_claimed=True, no_deletion_or_PPO_budget=True)
        put('SOURCE4090_TO_ZONGLIN2_TRANSFER_COMPLETE.json', complete)
        print(json.dumps(complete),flush=True)
    finally:
        password = None
        if sf:sf.close()
        source_transport.close(src)
        c.close()


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        put('SOURCE4090_TO_ZONGLIN2_TRANSFER_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json',
            dict(epoch=time.time(),error=traceback.format_exc(),no_delete_or_blind_transfer_replay=True,
                 original_partial_archive_retained=True,credentials_not_saved=True))
        raise

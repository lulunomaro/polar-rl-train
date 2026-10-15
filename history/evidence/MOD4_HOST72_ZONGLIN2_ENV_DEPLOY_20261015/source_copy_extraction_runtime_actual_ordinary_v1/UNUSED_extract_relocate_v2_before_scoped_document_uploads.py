"""One bounded target-only extraction/relocation sequence after complete stream SHA."""
from pathlib import Path
import getpass
import hashlib
import json
import shlex
import subprocess
import os
import sys
import time
import traceback
import threading
import paramiko

D = Path(__file__).resolve().parent
R = D / 'reports'
W = D.parent
ROOT = '/home/lc01/Zonglin Li/zonglin2'


def put(name, value, unique=True):
    with (R / name).open('x' if unique else 'w', encoding='utf8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)


def main():
    complete = json.loads((R / 'SOURCE4090_TO_ZONGLIN2_TRANSFER_V2_COMPLETE.json').read_bytes())
    assert complete['source_stream_target_SHA_exact']
    assert not (R / 'ZONGLIN2_EXTRACT_RELOCATE_NATIVE_CHECK_V2_STARTED.json').exists()
    prior = json.loads((W / 'MOD4_HOST72_DUAL4090_ENV_READONLY_20261015/reports/HOST72_READONLY_DISCOVERY_ACTUAL.json').read_bytes())
    c = paramiko.SSHClient()
    c.load_system_host_keys()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    password = getpass.getpass('Host72 SSH password (hidden, not saved): ')
    sf = None
    try:
        c.connect(prior['host'], username=prior['user'], password=password, timeout=15,
                  auth_timeout=20, banner_timeout=20, allow_agent=False, look_for_keys=False)
        password = None
        assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest() == prior['remote_host_key_SHA256_hex']
        ci = subprocess.run(['powershell','-NoProfile','-Command',
            '$p=Get-CimInstance Win32_Process -Filter "ProcessId = '+str(os.getpid())+'";$p|Select-Object ProcessId,CreationDate,CommandLine|ConvertTo-Json -Compress'],
            capture_output=True,text=True,encoding='utf8',check=True)
        put('ZONGLIN2_EXTRACT_RELOCATE_NATIVE_CHECK_V2_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),
            actual_CIM=json.loads(ci.stdout),argv=sys.argv,archive=complete['archive'],
            target72_transport_owner_while_actual_creationargv_alive=True,no_PPO_budget_or_deletion=True))
        sf = c.open_sftp()
        sf.get_channel().settimeout(90)
        try:
            sf.mkdir(ROOT + '/tools')
        except IOError:
            st = sf.lstat(ROOT + '/tools')
            assert st.st_mode & 0o170000 == 0o040000
        uploads = [(D/'payload/tools/conda_pack_prefixes_official.py',ROOT+'/tools/conda_pack_prefixes_official.py')]
        names = ('preflight_source_archive_paths_inside_zonglin2_v1.py','extract_source_archive_inside_zonglin2_v1.py','relocate_owned_environment_prefixes_v1.py',
                 'check_relocated_environment_native_CPU_v1.py')
        uploads += [(D/'payload'/name,ROOT+'/audit/'+name) for name in names]
        for source, target in uploads:
            assert target.startswith(ROOT+'/') and '..' not in Path(target).parts
            with sf.open(target, 'wx') as f:
                f.write(source.read_bytes())
        commands = []
        for name in names:
            _, so, se = c.exec_command('python3 -B '+shlex.quote(ROOT+'/audit/'+name), timeout=3600)
            errors = []
            thread = threading.Thread(target=lambda:errors.append(se.read()),daemon=True)
            thread.start()
            out = []
            for raw in so:
                out.append(raw)
                print(raw.rstrip(), flush=True)
            thread.join()
            rc = so.channel.recv_exit_status()
            value = dict(epoch=time.time(),script=name,returncode=rc,stdout=''.join(out),
                         stderr=b''.join(errors).decode('utf8','replace'))
            put('ZONGLIN2_COMMAND_'+name.removesuffix('.py')+'_ACTUAL.json',value)
            commands.append(value)
            assert rc == 0, value['stderr']
        for name in ('EXTRACTION_V1_COMPLETE.json','PREFIX_RELOCATION_V1_COMPLETE.json',
                     'NATIVE_CPU_ABI_AND_SOURCE_V1_ACTUAL.json'):
            with sf.open(ROOT+'/audit/'+name,'rb') as f:
                value = json.loads(f.read())
            put('TARGET_'+name,value)
        put('ZONGLIN2_EXTRACT_RELOCATE_NATIVE_CHECK_V2_COMPLETE.json',dict(epoch=time.time(),
            commands=[dict(script=x['script'],returncode=x['returncode']) for x in commands],
            files_deployed=True,actual_CPU_ABI_result_must_be_read=True,no_GPU_ready_claim_from_copy=True,
            no_deletion_or_outside_root_write_PPO_budget=True))
    finally:
        password = None
        if sf:sf.close()
        c.close()


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        put('ZONGLIN2_EXTRACT_RELOCATE_NATIVE_CHECK_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',
            dict(epoch=time.time(),error=traceback.format_exc(),no_delete_or_blind_replay=True,
                 original_archive_and_partial_files_retained=True))
        raise

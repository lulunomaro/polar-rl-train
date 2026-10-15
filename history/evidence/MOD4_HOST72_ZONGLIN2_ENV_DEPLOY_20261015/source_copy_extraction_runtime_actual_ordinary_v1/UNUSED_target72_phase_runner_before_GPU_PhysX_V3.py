"""Run one genuinely unused prepared target phase, after actual prior admission."""
from pathlib import Path
import argparse
import getpass
import hashlib
import json
import shlex
import time
import traceback
import threading
import paramiko

D = Path(__file__).resolve().parent
W = D.parent
R = D / 'reports'
ROOT = '/home/lc01/Zonglin Li/zonglin2'


def put(name, value):
    with (R / name).open('x', encoding='utf8') as f:
        json.dump(value,f,indent=2,ensure_ascii=False)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--phase',required=True,choices=['compat-cpu','finite-sdk'])
    a=p.parse_args()
    if a.phase=='compat-cpu':
        assert (R/'PRIVATE_GLIBC_COPY_COMPLETE_ACTUAL.json').exists()
        source='check_relocated_environment_compat_CPU_v2.py'
        remote_report='COMPAT_CPU_ABI_AND_SOURCE_V2_ACTUAL.json'
    else:
        candidates=[R/'TARGET_COMPAT_CPU_ABI_AND_SOURCE_V2_ACTUAL.json',R/'TARGET_NATIVE_CPU_ABI_AND_SOURCE_V1_ACTUAL.json']
        cpu=next(json.loads(x.read_bytes()) for x in candidates if x.exists())
        assert cpu['returncode']==0 and cpu['result']['SDK_SimulationApp_import']['passed']
        assert all(cpu['result']['imports'][x]['passed'] for x in ('torch','tensordict','rsl_rl'))
        assert cpu['result']['packages']['torch']=='2.10.0+cu128'
        source='validate_owned_environment_CUDA_and_SDK_finite_v2_headless.py'
        remote_report='FINITE_DEPLOYMENT_VALIDATION_V2_HEADLESS_COMPLETE.json'
    prefix='OWNED72_'+a.phase.upper().replace('-','_')
    assert not (R/(prefix+'_STARTED.json')).exists()
    prev=json.loads((W/'MOD4_HOST72_DUAL4090_ENV_READONLY_20261015/reports/HOST72_READONLY_DISCOVERY_ACTUAL.json').read_bytes())
    c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    password=getpass.getpass('Host72 SSH password (hidden, not saved): ')
    sf=None
    try:
        c.connect(prev['host'],username=prev['user'],password=password,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False)
        password=None
        assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()==prev['remote_host_key_SHA256_hex']
        sf=c.open_sftp();sf.get_channel().settimeout(60)
        dest=ROOT+'/audit/'+source
        with sf.open(dest,'wx') as f:f.write((D/'payload'/source).read_bytes())
        put(prefix+'_STARTED.json',dict(epoch=time.time(),phase=a.phase,source_SHA=hashlib.sha256((D/'payload'/source).read_bytes()).hexdigest(),
            target=dest,all_writes_in_owned_zonglin2=True,no_delete_signal_PPO_or_budget=True))
        _,so,se=c.exec_command('python3 -B '+shlex.quote(dest),timeout=600)
        errors=[]
        t=threading.Thread(target=lambda:errors.append(se.read()),daemon=True);t.start()
        out=so.read();t.join();err=b''.join(errors);rc=so.channel.recv_exit_status()
        put(prefix+'_COMMAND_ACTUAL.json',dict(epoch=time.time(),returncode=rc,stdout=out.decode('utf8','replace'),stderr=err.decode('utf8','replace')))
        # Preserve every owned audit and log at this boundary, including actual failures.
        collected=[]
        for folder in ('audit','logs'):
            for stat in sf.listdir_attr(ROOT+'/'+folder):
                if stat.st_mode & 0o170000 != 0o100000:continue
                remote=ROOT+'/'+folder+'/'+stat.filename
                if stat.filename.endswith('.py') or stat.st_size>8*1024*1024:continue
                with sf.open(remote,'rb') as f:b=f.read()
                local=D/'actual_target72'/prefix/folder/stat.filename;local.parent.mkdir(parents=True,exist_ok=True)
                assert not local.exists();local.write_bytes(b)
                collected.append(dict(remote_path=remote,local_path=str(local),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
                if stat.filename==remote_report:
                    put('TARGET_'+remote_report,json.loads(b))
        put(prefix+'_BOUNDARY_COLLECTED_ACTUAL.json',dict(epoch=time.time(),returncode=rc,files=collected,
            actual_result_not_inferred_from_dispatch_or_file_copy=True,no_delete_or_budget=True))
        print(json.dumps(dict(phase=a.phase,returncode=rc,collected_files=len(collected),report=remote_report,
            actual_expected_report_collected=any(x['remote_path'].endswith('/'+remote_report) for x in collected))),flush=True)
        assert rc==0,'Read preserved actual command and audit/log outputs before any continuation.'
    finally:
        password=None
        if sf:sf.close()
        c.close()


if __name__=='__main__':
    try:main()
    except BaseException:
        put('OWNED72_PHASE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),
            no_delete_signal_or_blind_phase_replay=True,all_existing_owned_outputs_retained=True))
        raise

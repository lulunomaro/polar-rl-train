"""One pinned read-only Stage11 receipt collection. Credentials enter only stdin."""
from pathlib import Path
import base64
import hashlib
import json
import os
import shlex
import socket
import stat
import sys
import time
import paramiko

HERE = Path(__file__).resolve().parent
REPORTS = HERE / 'reports'
ROOT = '/data/robemo/polar-rl-train'
RUN = ROOT + '/setup_runs/W35_VENDOR_TORCH211_COHERENT_RUNTIME_20261028_V11'
PIN = '8adc87f3e75eb307a2429fa97b68761e09c0636b0eea684c71894438757c788b'
OLD = HERE.parent / 'NEW_HOST_STAGE11_COHERENT_VENDOR_TORCH211_SOURCE_V1'

REMOTE_CODE = r'''
from pathlib import Path
import json, os, stat, time
ROOT=Path('/data/robemo/polar-rl-train')
RUN=ROOT/'setup_runs/W35_VENDOR_TORCH211_COHERENT_RUNTIME_20261028_V11'
assert ROOT.resolve()==ROOT and RUN.resolve()==RUN and not ROOT.is_symlink() and not RUN.is_symlink()
m=json.loads((ROOT/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_bytes())
assert m['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700' and m['authorized_root']==str(ROOT)
m=json.loads((RUN/'SETUP_RUN_OWNER.json').read_bytes())
assert m['root']==str(ROOT) and m['new_run']==str(RUN)
def load(name):
 p=RUN/name
 if not p.exists():return None
 assert p.resolve()==p and stat.S_ISREG(p.lstat().st_mode)
 return json.loads(p.read_bytes())
launch=load('DETACHED_LAUNCH_ACTUAL.json')
assert launch['supervisor']==expected['supervisor'] and launch['installer']==expected['installer']
terminal=load('SUPERVISOR_TERMINAL_ACTUAL.json');ending=load('SUPERVISOR_EXIT_ACTUAL.json')
boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '))
def known_status(row):
 p=Path('/proc')/str(row['pid'])
 try:raw=(p/'stat').read_text()
 except FileNotFoundError:return dict(expected=row,original_out=True,status='absent')
 fields=raw[raw.rfind(')')+2:].split();creation=boot+int(fields[19])/os.sysconf('SC_CLK_TCK')
 if creation!=row['creation']:return dict(expected=row,original_out=True,status='PID_reused_no_other_identity_read')
 if fields[0]=='Z':return dict(expected=row,original_out=True,status='nonexecuting_zombie')
 actual=dict(pid=row['pid'],creation=creation,exe=os.readlink(p/'exe'),argv=[os.fsdecode(x) for x in (p/'cmdline').read_bytes().split(bytes([0])) if x],root=os.readlink(p/'cwd'))
 assert actual==row,'known original identity changed'
 return dict(expected=row,original_out=False,status='still_executing_exact_owned_identity')
rows=[expected['supervisor'],expected['installer']]
if terminal is not None:
 assert terminal['supervisor']==expected['supervisor']
 for row in terminal['owned_pip_identities']:
  assert row['root']==str(RUN) and row['pid']>0 and row['creation']>=expected['installer']['creation']
  assert row['exe'].startswith(str(ROOT)+'/') or row['exe']=='/usr/bin/python3.12'
  assert ('-m' in row['argv'] and 'pip' in row['argv']) or row['argv'][1:3]==['-B','-c']
  rows.append(row)
identities=[known_status(row) for row in rows]
inventory=[]
for directory in (RUN,RUN/'logs'):
 if not directory.exists():continue
 assert directory.resolve()==directory and not directory.is_symlink()
 for p in sorted(directory.iterdir()):
  s=p.lstat()
  if stat.S_ISREG(s.st_mode) and (p.suffix in ('.json','.jsonl','.log','.txt') or p.name=='official_exact_CUDA128_links.html'):
   inventory.append(dict(path=str(p),bytes=s.st_size,mtime_ns=s.st_mtime_ns))
print(json.dumps(dict(epoch=time.time(),read_only=True,terminal=terminal,exit=ending,installer_original_error=load('INSTALLER_ORIGINAL_ERROR_ACTUAL.json'),packages_receipt=load('STAGE11_PACKAGES_AND_SOURCE_REGISTRATION_PASSED_ACTUAL.json'),identities=identities,all_original_recorded_out=all(x['original_out'] for x in identities),terminal_observed=terminal is not None and ending is not None,inventory=inventory,no_GPU_model_import_launch_ledger_or_server_write=True)))
'''

def save(name, value):
    with (REPORTS / name).open('x', encoding='utf8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)

def main():
    assert time.time() >= 1793182832.880596, 'original Stage11 1800s supervisor budget plus 1s before terminal collection'
    REPORTS.mkdir(exist_ok=True)
    save('STAGE11_READONLY_ENTRY_ENTERED_ACTUAL.json', dict(epoch=time.time(),pid=os.getpid(),entry=str(Path(__file__).resolve()),maximum_after_stdin_seconds=120,remote_write=False))
    print('READY_FOR_SINGLE_STDIN_JSON', flush=True)
    req = json.loads(sys.stdin.readline())
    assert set(req)=={'host','username','password'} and req['host']=='10.50.0.86' and req['username']=='robemo'
    secret=req.pop('password'); transport=None; sftp=None
    deadline=time.monotonic()+120
    def remaining():
        left=deadline-time.monotonic()
        assert left>0, 'finite_readonly_deadline'
        return min(25,left)
    try:
        receipt=OLD/'reports/STAGE11_DETACHED_INSTALLER_LAUNCHED_RETURNED_ACTUAL.json';raw=receipt.read_bytes();assert hashlib.sha256(raw).hexdigest()=='126b32a15656317ef75676bfb2f3bacb6fd9255468b99e9780af277c7576c5c9'
        expected=json.loads(raw)
        assert expected['supervisor']['pid']==510728 and expected['supervisor']['creation']==1793181031.11
        assert expected['installer']['pid']==510729 and expected['installer']['creation']==1793181031.16
        sock=socket.create_connection((req['host'],22),timeout=15)
        transport=paramiko.Transport(sock);transport.banner_timeout=15;transport.auth_timeout=15;transport.start_client(timeout=15)
        actual=hashlib.sha256(transport.get_remote_server_key().asbytes()).hexdigest()
        assert actual==PIN, 'PIN_MISMATCH_BEFORE_AUTH'
        transport.auth_password(req['username'],secret,fallback=False);secret=None
        print(json.dumps(dict(stage='PINNED_READONLY_AUTHENTICATED',epoch=time.time(),public_hostkey_SHA=actual)),flush=True)
        channel=transport.open_session(timeout=15)
        code='expected='+repr({k:expected[k] for k in ('supervisor','installer')})+'\n'+REMOTE_CODE
        channel.exec_command('/usr/bin/python3 -B -c '+shlex.quote(code));channel.settimeout(remaining())
        out=channel.makefile('rb').read();err=channel.makefile_stderr('rb').read();rc=channel.recv_exit_status()
        save('STAGE11_READONLY_REMOTE_ORIGINAL_RESULT_ACTUAL.json',dict(returncode=rc,stdout=out.decode('utf8'),stderr=err.decode('utf8')))
        assert rc==0, 'readonly_receipt_or_identity_guard_failed'
        value=json.loads(out);save('STAGE11_READONLY_TERMINAL_AND_IDENTITIES_ACTUAL.json',value)
        sftp=paramiko.SFTPClient.from_transport(transport)
        target=REPORTS/'complete_original_UTF8_reports';target.mkdir()
        rows=[];last=0
        for row in value['inventory']:
            sftp.get_channel().settimeout(remaining())
            path=row['path'];assert path.startswith(RUN+'/')
            attrs=sftp.lstat(path);assert stat.S_ISREG(attrs.st_mode)
            before=(attrs.st_size,attrs.st_mtime)
            name=hashlib.sha256(path.encode()).hexdigest()[:20]+'_'+path.rsplit('/',1)[-1]
            local=target/name;digest=hashlib.sha256();count=0
            with sftp.open(path,'rb') as source,local.open('xb') as dest:
                while True:
                    remaining();block=source.read(256*1024)
                    if not block:break
                    dest.write(block);digest.update(block);count+=len(block)
            attrs=sftp.stat(path);after=(attrs.st_size,attrs.st_mtime)
            stable=before==after and count==before[0]
            try:local.read_text(encoding='utf8');utf8=True
            except UnicodeDecodeError:utf8=False
            item=dict(remote_path=path,local_path=str(local),bytes=count,SHA=digest.hexdigest(),before_stat=before,after_stat=after,complete_original_bytes=stable,UTF8_decodable=utf8)
            rows.append(item);save('FULL_TEXT_ROW_'+str(len(rows)).zfill(3)+'_ACTUAL.json',item)
            assert stable,'own text changed during readonly snapshot; retained bytes, no retry'
            if time.monotonic()-last>=15:
                print(json.dumps(dict(stage='FULL_ORIGINAL_TEXT_RETAINED',files=len(rows),epoch=time.time())),flush=True);last=time.monotonic()
        proof=dict(passed_readonly_collection=True,epoch=time.time(),terminal_observed=value['terminal_observed'],all_original_recorded_out=value['all_original_recorded_out'],installer_passed=None if value['terminal'] is None else value['terminal']['passed'],terminal=value['terminal'],exit=value['exit'],original_error=value['installer_original_error'],packages_receipt=value['packages_receipt'],full_original_texts=rows,no_remote_write_no_GPU_model_GO_or_account=True,actual_SDK_CUDA_restore_native_and_PPO_not_proved_by_package_metadata=True)
        save('STAGE11_READONLY_TERMINAL_FULL_LOGS_RETURNED_ACTUAL.json',proof)
        print(json.dumps({k:v for k,v in proof.items() if k not in ('full_original_texts','terminal','exit','original_error','packages_receipt')}),flush=True)
    except BaseException as e:
        message=str(e)
        if secret:message=message.replace(secret,'[REDACTED]')
        save('STAGE11_READONLY_LOCAL_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error_type=type(e).__name__,error=message,partial_preserved=True,no_retry=True))
        print(json.dumps(dict(stage='ORIGINAL_READONLY_ERROR',error_type=type(e).__name__,error=message)),flush=True)
        raise SystemExit(1)
    finally:
        secret=None
        if sftp:sftp.close()
        if transport:transport.close()

if __name__=='__main__':main()

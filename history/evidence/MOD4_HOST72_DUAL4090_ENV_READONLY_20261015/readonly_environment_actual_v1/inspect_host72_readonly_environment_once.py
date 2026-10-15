"""Authorized read-only host inspection. Password is entered hidden and never stored."""
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
HOST, USER = '10.24.0.72', 'lc01'

DISCOVERY = r'''
import json,os,pathlib,platform,shutil,subprocess,sys,time
def run(argv,timeout=20):
 try:
  p=subprocess.run(argv,capture_output=True,text=True,timeout=timeout)
  return dict(argv=argv,returncode=p.returncode,stdout=p.stdout[:24000],stderr=p.stderr[:4000])
 except Exception as e:return dict(argv=argv,error=type(e).__name__+': '+str(e))
home=pathlib.Path.home()
envs=[]
p=home/'.conda/environments.txt'
if p.exists():envs += [x.strip() for x in p.read_text().splitlines() if x.strip()]
roots=[]
for root in [home/'miniconda3',home/'anaconda3',home/'miniforge3',pathlib.Path('/opt/conda'),pathlib.Path('/opt/miniconda3')]:
 if root.is_dir():
  roots.append(str(root));envs.append(str(root))
  if (root/'envs').is_dir():envs += [str(x) for x in (root/'envs').iterdir() if x.is_dir()]
conda=shutil.which('conda')
if conda:
 cr=run([conda,'env','list','--json'])
 try:envs+=json.loads(cr.get('stdout','{}')).get('envs',[])
 except Exception:pass
else:cr=None
disks=[]
for path in ['/',str(home),'/mnt','/data','/workspace','/tmp']:
 if pathlib.Path(path).exists():
  v=shutil.disk_usage(path);disks.append(dict(path=path,total=v.total,used=v.used,free=v.free))
project_candidates=[]
for base in [home,pathlib.Path('/data'),pathlib.Path('/workspace'),pathlib.Path('/opt')]:
 if not base.is_dir():continue
 try:
  for p in base.iterdir():
   if p.is_dir() and any(k in p.name.lower() for k in ['isaac','sim','rl','robot','fangzhen','mod4','conda','miniforge']):project_candidates.append(str(p))
 except PermissionError:pass
v=dict(epoch=time.time(),hostname=platform.node(),os=platform.platform(),machine=platform.machine(),
 user=os.getlogin() if os.environ.get('LOGNAME') is None else os.environ['LOGNAME'],
 python=dict(path=sys.executable,version=sys.version),cpu_count=os.cpu_count(),
 nvidia_smi=run(['nvidia-smi']),
 gpu=run(['nvidia-smi','--query-gpu=index,name,uuid,driver_version,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu,power.draw,power.limit,compute_mode','--format=csv,noheader,nounits']),
 gpu_processes=run(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name,used_gpu_memory','--format=csv,noheader,nounits']),
 cpu=run(['lscpu']),memory=run(['free','-b']),disks=disks,
 nvcc=run(['nvcc','--version']) if shutil.which('nvcc') else dict(found=False),
 conda=cr,conda_roots=roots,environment_paths=sorted(set(envs)),project_candidates=sorted(set(project_candidates)),
 docker=run(['docker','ps','--format','{{.Names}}\t{{.Image}}\t{{.Status}}']) if shutil.which('docker') else dict(found=False),
 proc_version=pathlib.Path('/proc/version').read_text() if pathlib.Path('/proc/version').exists() else None,
 no_training_simulation_package_install_process_signal_or_budget_action=True)
print(json.dumps(v))
'''


def put(name, value):
    with (R / name).open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)


def main():
    R.mkdir(exist_ok=True)
    assert not (R / 'HOST72_READONLY_DISCOVERY_ACTUAL.json').exists(), 'Existing result: read it before any new connection.'
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    password = getpass.getpass('SSH password (hidden, not saved): ')
    try:
        client.connect(HOST, username=USER, password=password, timeout=15, auth_timeout=20,
                       banner_timeout=20, allow_agent=False, look_for_keys=False)
        password = None
        key = client.get_transport().get_remote_server_key()
        fingerprint = hashlib.sha256(key.asbytes()).hexdigest()
        _, stdout, stderr = client.exec_command('uname -a', timeout=20)
        kernel, error, rc = stdout.read().decode(), stderr.read().decode(), stdout.channel.recv_exit_status()
        assert rc == 0, dict(uname_error=error, returncode=rc)
        command = 'python3 -c ' + shlex.quote(DISCOVERY)
        _, stdout, stderr = client.exec_command(command, timeout=120)
        output, error, rc = stdout.read().decode(), stderr.read().decode(), stdout.channel.recv_exit_status()
        assert rc == 0, dict(discovery_stderr=error, returncode=rc)
        value = dict(host=HOST, user=USER, epoch=time.time(), remote_host_key_type=key.get_name(),
                     remote_host_key_SHA256_hex=fingerprint, kernel=kernel,
                     discovery=json.loads(output), stderr=error, password_not_stored=True,
                     inspection_source_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
        put('HOST72_READONLY_DISCOVERY_ACTUAL.json', value)
        print(json.dumps(value, ensure_ascii=False), flush=True)
    finally:
        password = None
        client.close()


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        R.mkdir(exist_ok=True)
        put('HOST72_READONLY_DISCOVERY_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json',
            dict(epoch=time.time(), error=traceback.format_exc(), password_not_stored=True,
                 no_training_simulation_install_signal_or_budget=True))
        raise

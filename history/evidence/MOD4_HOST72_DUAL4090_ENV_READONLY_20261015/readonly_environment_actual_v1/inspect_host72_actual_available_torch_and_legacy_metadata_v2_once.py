"""Read actual installed Torch; retain the empty-named-env and legacy-reader failures."""
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
REMOTE = r'''
import json,pathlib,subprocess,time
def run(argv,timeout=30):
 try:
  p=subprocess.run(argv,capture_output=True,text=True,timeout=timeout)
  return dict(argv=argv,returncode=p.returncode,stdout=p.stdout[:24000],stderr=p.stderr[:6000])
 except Exception as e:return dict(argv=argv,error=type(e).__name__+': '+str(e))
legacy_code=r"""
import sys,json,importlib.util,pkg_resources
keys=('torch','numpy','tensordict','rsl','isaac','omni','gymnasium','mujoco','warp')
pkgs={d.project_name:d.version for d in pkg_resources.working_set if d.project_name.lower().startswith(keys)}
origins={}
for name in ('isaaclab','isaacsim','omni','rsl_rl','tensordict'):
 try:
  s=importlib.util.find_spec(name);origins[name]=None if s is None else str(s.origin)
 except Exception as e:origins[name]=dict(error=type(e).__name__+': '+str(e))
print(json.dumps(dict(python=sys.executable,version=sys.version,packages=pkgs,module_resolution_only=origins)))
"""
legacy=[run([str(pathlib.Path.home()/'miniconda3/envs'/n/'bin/python'),'-B','-c',legacy_code],20) for n in ('4DGS','ed3dgs','evogs')]
code=r"""
import sys,json,torch
v=dict(python=sys.executable,torch=torch.__version__,torch_path=torch.__file__,built_cuda=torch.version.cuda,cudnn=torch.backends.cudnn.version(),cuda_available=torch.cuda.is_available(),device_count=torch.cuda.device_count(),no_tensor_allocation_or_GPU_kernel=True)
v['devices']=[dict(index=i,name=torch.cuda.get_device_name(i),total_memory=torch.cuda.get_device_properties(i).total_memory,capability=torch.cuda.get_device_capability(i)) for i in range(v['device_count'])]
print(json.dumps(v))
"""
actual=[run([p,'-B','-c',code],40) for p in ['/opt/anaconda3/bin/python',str(pathlib.Path.home()/'Zonglin Li/worldmodel/server-work/envs/l2t/bin/python')]]
for row in legacy+actual:
 try:row['actual']=json.loads(row.pop('stdout'))
 except Exception:pass
print(json.dumps(dict(epoch=time.time(),legacy_metadata=legacy,actual_torch_CUDA_enumeration=actual,
 no_install_training_simulation_tensor_allocation_signal_or_budget=True)))
'''


def put(name, value):
    with (R / name).open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)


def main():
    assert not (R / 'HOST72_AVAILABLE_TORCH_LEGACY_METADATA_V2_ACTUAL.json').exists()
    prior = json.loads((R / 'HOST72_READONLY_DISCOVERY_ACTUAL.json').read_bytes())
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    password = getpass.getpass('SSH password (hidden, not saved): ')
    try:
        client.connect(prior['host'], username=prior['user'], password=password, timeout=15,
                       auth_timeout=20, banner_timeout=20, allow_agent=False, look_for_keys=False)
        password = None
        assert hashlib.sha256(client.get_transport().get_remote_server_key().asbytes()).hexdigest() == prior['remote_host_key_SHA256_hex']
        _, stdout, stderr = client.exec_command('python3 -c ' + shlex.quote(REMOTE), timeout=150)
        output, error, rc = stdout.read().decode(), stderr.read().decode(), stdout.channel.recv_exit_status()
        assert rc == 0, dict(returncode=rc, stderr=error)
        value = dict(epoch=time.time(), host=prior['host'], details=json.loads(output), stderr=error,
            prior_empty_pytorch_env_ModuleNotFound_and_legacy_importlib_metadata_errors_preserved=True,
            password_not_stored=True)
        put('HOST72_AVAILABLE_TORCH_LEGACY_METADATA_V2_ACTUAL.json', value)
        print(json.dumps(value, ensure_ascii=False), flush=True)
    finally:
        password = None
        client.close()


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        put('HOST72_TORCH_LEGACY_V2_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json',
            dict(epoch=time.time(), error=traceback.format_exc(), password_not_stored=True))
        raise

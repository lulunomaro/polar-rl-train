"""One bounded read-only software inventory, using existing interpreters only."""
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
import json,os,pathlib,subprocess,sys,time
home=pathlib.Path.home()
def run(argv,timeout=20):
 try:
  p=subprocess.run(argv,capture_output=True,text=True,timeout=timeout)
  return dict(argv=argv,returncode=p.returncode,stdout=p.stdout[:32000],stderr=p.stderr[:4000])
 except Exception as e:return dict(argv=argv,error=type(e).__name__+': '+str(e))
paths=set(ENV_PATHS)
for root in [pathlib.Path('/opt/anaconda3'),home/'miniconda3']:
 if (root/'bin/python').exists():paths.add(str(root))
 if (root/'envs').is_dir():
  try:paths.update(str(x) for x in (root/'envs').iterdir() if (x/'bin/python').exists())
  except PermissionError:pass
code=r"""
import sys,json,importlib.metadata as m,importlib.util
keys=('torch','numpy','tensordict','rsl','isaac','omni','gymnasium','mujoco','warp','nvidia-cuda','nvidia-cudnn','triton')
pkgs={}
for d in m.distributions():
 name=d.metadata.get('Name','')
 if name.lower().startswith(keys):pkgs[name]=d.version
origins={}
for name in ('torch','isaaclab','isaacsim','omni','rsl_rl','tensordict'):
 try:
  s=importlib.util.find_spec(name);origins[name]=None if s is None else dict(origin=s.origin,locations=list(s.submodule_search_locations or []))
 except Exception as e:origins[name]=dict(error=type(e).__name__+': '+str(e))
print(json.dumps(dict(python=sys.executable,version=sys.version,packages=pkgs,module_resolution_only=origins)))
"""
inventories=[]
for p in sorted(paths):
 py=pathlib.Path(p)/'bin/python'
 if not py.exists():inventories.append(dict(environment=p,python_missing=True));continue
 v=run([str(py),'-B','-c',code],20)
 try:v['inventory']=json.loads(v.pop('stdout'))
 except Exception:pass
 inventories.append(v)
candidate=home/'miniconda3/envs/pytorch_env/bin/python'
torch_code=r"""
import json,torch
v=dict(torch=torch.__version__,torch_path=torch.__file__,built_cuda=torch.version.cuda,cudnn=torch.backends.cudnn.version(),cuda_available=torch.cuda.is_available(),device_count=torch.cuda.device_count(),not_a_compute_benchmark=True)
v['devices']=[dict(index=i,name=torch.cuda.get_device_name(i),total_memory=torch.cuda.get_device_properties(i).total_memory,capability=torch.cuda.get_device_capability(i)) for i in range(v['device_count'])]
print(json.dumps(v))
"""
torch_actual=run([str(candidate),'-B','-c',torch_code],35) if candidate.exists() else dict(python_missing=True)
try:torch_actual['actual']=json.loads(torch_actual.pop('stdout'))
except Exception:pass
matches=[]
for root in [home,pathlib.Path('/data'),pathlib.Path('/opt'),home/'.local/share/ov/pkg']:
 if not root.is_dir():continue
 for current,dirs,files in os.walk(root):
  rel=pathlib.Path(current).relative_to(root)
  if len(rel.parts)>=3:dirs[:]=[];continue
  dirs[:]=[x for x in dirs if x not in ('.git','node_modules','__pycache__','site-packages','.cache','miniconda3','anaconda3')]
  for name in dirs:
   if any(k in name.lower() for k in ('isaac','omniverse','mod4','fangzhen')):matches.append(str(pathlib.Path(current)/name))
v=dict(epoch=time.time(),os_release=pathlib.Path('/etc/os-release').read_text(),
 interpreter_inventories=inventories,pytorch_env_actual_torch_import_and_CUDA_device_enumeration=torch_actual,
 no_GPU_kernel_allocation_benchmark_or_simulation_launched=True,
 isaac_related_paths_at_bounded_depth=sorted(set(matches)),search_not_exhaustive=True,
 gpu_topology=run(['nvidia-smi','topo','-m']),
 data_path_access=dict(exists=pathlib.Path('/data').exists(),readable=os.access('/data',os.R_OK),writable_permission_metadata=os.access('/data',os.W_OK)),
 current_gpu=run(['nvidia-smi','--query-gpu=index,name,memory.used,utilization.gpu','--format=csv,noheader,nounits']),
 no_package_install_remote_file_write_training_signal_or_budget=True)
print(json.dumps(v))
'''


def put(name, value):
    with (R / name).open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)


def main():
    assert not (R / 'HOST72_PYTHON_SIM_STACK_READONLY_ACTUAL.json').exists()
    previous = json.loads((R / 'HOST72_READONLY_DISCOVERY_ACTUAL.json').read_bytes())
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    password = getpass.getpass('SSH password (hidden, not saved): ')
    try:
        client.connect(previous['host'], username=previous['user'], password=password, timeout=15,
                       auth_timeout=20, banner_timeout=20, allow_agent=False, look_for_keys=False)
        password = None
        key = client.get_transport().get_remote_server_key()
        assert hashlib.sha256(key.asbytes()).hexdigest() == previous['remote_host_key_SHA256_hex']
        code = 'ENV_PATHS=' + repr(previous['discovery']['environment_paths']) + '\n' + REMOTE
        _, stdout, stderr = client.exec_command('python3 -c ' + shlex.quote(code), timeout=240)
        output, error, rc = stdout.read().decode(), stderr.read().decode(), stdout.channel.recv_exit_status()
        assert rc == 0, dict(returncode=rc, stderr=error)
        value = dict(epoch=time.time(), host=previous['host'], user=previous['user'],
                     previous_discovery_SHA=hashlib.sha256((R / 'HOST72_READONLY_DISCOVERY_ACTUAL.json').read_bytes()).hexdigest(),
                     details=json.loads(output), stderr=error, password_not_stored=True)
        put('HOST72_PYTHON_SIM_STACK_READONLY_ACTUAL.json', value)
        details = value['details']
        print(json.dumps(dict(report='HOST72_PYTHON_SIM_STACK_READONLY_ACTUAL.json',
            inventories=details['interpreter_inventories'], actual_torch=details['pytorch_env_actual_torch_import_and_CUDA_device_enumeration'],
            isaac_related_paths=details['isaac_related_paths_at_bounded_depth'],
            gpu_topology=details['gpu_topology'], data_access=details['data_path_access']), ensure_ascii=False), flush=True)
    finally:
        password = None
        client.close()


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        put('HOST72_PYTHON_SIM_STACK_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json',
            dict(epoch=time.time(), error=traceback.format_exc(), password_not_stored=True,
                 no_training_simulation_install_signal_or_budget=True))
        raise

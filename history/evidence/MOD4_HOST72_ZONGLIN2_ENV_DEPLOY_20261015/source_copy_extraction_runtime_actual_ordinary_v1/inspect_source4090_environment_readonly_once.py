"""Read the authorized source4090 stack only; no source files are written."""
from pathlib import Path
import hashlib
import json
import shlex
import sys
import time
import traceback

D = Path(__file__).resolve().parent
R = D / 'reports'
W = D.parent
sys.path.insert(0, str(W / 'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as t

CODE = r'''
from pathlib import Path
import importlib.metadata as m,importlib.util,json,os,platform,subprocess,sys,time,sysconfig
def run(argv,timeout=50):
 try:
  p=subprocess.run(argv,capture_output=True,text=True,timeout=timeout)
  return dict(argv=argv,returncode=p.returncode,stdout=p.stdout[:16000],stderr=p.stderr[:3000])
 except Exception as e:return dict(argv=argv,error=type(e).__name__+': '+str(e))
packages={}
for d in m.distributions():
 name=d.metadata.get('Name','')
 if name.lower().startswith(('torch','tensordict','rsl','isaac','omni','warp','numpy','nvidia-cuda')):
  packages[name]=dict(version=d.version,location=str(d.locate_file('')))
origins={}
for name in ('isaaclab','isaacsim','omni','rsl_rl','torch'):
 try:
  s=importlib.util.find_spec(name);origins[name]=None if s is None else dict(origin=s.origin,locations=list(s.submodule_search_locations or []))
 except Exception as e:origins[name]=dict(error=type(e).__name__+': '+str(e))
site=Path(sysconfig.get_paths()['purelib'])
pth=[dict(name=p.name,text=p.read_text(errors='replace')) for p in sorted(site.glob('*.pth'))]
project=Path('/home/egde/fangzhen_linux')
print(json.dumps(dict(epoch=time.time(),python=sys.executable,prefix=sys.prefix,version=sys.version,
 os_release=Path('/etc/os-release').read_text(),glibc=platform.libc_ver(),packages=packages,
 module_resolution_only=origins,editable_path_files=pth,
 prefix_disk=run(['du','-sb',sys.prefix]),project_disk=run(['du','-sb',str(project)]),
 source_project_top_names=sorted(p.name for p in project.iterdir()) if project.exists() else None,
 source_gpu=run(['nvidia-smi','--query-gpu=name,driver_version,memory.used,utilization.gpu','--format=csv,noheader,nounits']),
 source_compute_processes=run(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader']),
 tools={x:importlib.util.find_spec(x) is not None for x in ('conda_pack','pip','zstandard')},
 readonly_no_source_write_install_GPU_training_or_budget=True)))
'''


def main():
    R.mkdir(exist_ok=True)
    assert not (R / 'SOURCE4090_ENVIRONMENT_READONLY_ACTUAL.json').exists()
    c = None
    try:
        c = t.connect()
        si, so, se = c.exec_command('PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= ' + shlex.quote(t.PY) + ' -B -', timeout=150)
        si.write(CODE)
        si.flush()
        si.channel.shutdown_write()
        out, err = so.read(), se.read()
        rc = so.channel.recv_exit_status()
        assert rc == 0, dict(returncode=rc, stderr=err.decode('utf8','replace'))
        value = dict(epoch=time.time(), actual=json.loads(out), stderr=err.decode(), source_readonly=True)
        with (R / 'SOURCE4090_ENVIRONMENT_READONLY_ACTUAL.json').open('x', encoding='utf8') as f:
            json.dump(value, f, indent=2, ensure_ascii=False)
        print(json.dumps(value, ensure_ascii=False), flush=True)
    finally:
        t.close(c)


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        R.mkdir(exist_ok=True)
        with (R / ('SOURCE4090_READONLY_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json')).open('x', encoding='utf8') as f:
            json.dump(dict(error=traceback.format_exc(), no_retry_source_mutation_or_budget=True), f, indent=2)
        raise

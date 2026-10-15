"""Publish owned entrypoints only after actual two-GPU Lab/PhysX completion and exit."""
from pathlib import Path
import fcntl,hashlib,json,os,subprocess,time
ROOT=Path('/home/lc01/Zonglin Li/zonglin2')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2*1024*1024),b''):h.update(b)
 return h.hexdigest()
def write_new(p,s,mode=0o600):
 assert str(p.resolve()).startswith(str(ROOT)+'/')
 with p.open('x') as f:f.write(s)
 os.chmod(str(p),mode)
def main():
 assert ROOT.resolve()==ROOT
 ready=json.loads((ROOT/'audit/LAB_PHYSX_V7_COMPLETE_ACTUAL.json').read_bytes());assert ready['passed'] and ready['both_natural_exit0']
 for gpu in (0,1):
  assert json.loads((ROOT/('audit/TORCH_GPU'+str(gpu)+'_TINY_KERNEL_COMPLETE_ACTUAL.json')).read_bytes())['passed']
  assert json.loads((ROOT/('audit/LAB_GPU'+str(gpu)+'_PHYSX_V7_DATA_COMPLETE_ACTUAL.json')).read_bytes())['passed']
 processes=[]
 for a in sorted((ROOT/'audit').glob('*STARTED.json')):
  x=json.loads(a.read_bytes());pid=x.get('pid')
  if not pid:continue
  p=Path('/proc')/str(pid);row=dict(receipt=str(a),pid=pid,actual_proc_exists=p.exists())
  if p.exists():
   try:
    cmd=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace');row['actual_cmdline']=cmd
    row['same_owned_root_process_alive']=str(ROOT) in cmd
   except FileNotFoundError:row['exited_during_read']=True
  assert not row.get('same_owned_root_process_alive',False),row
  processes.append(row)
 with (ROOT/'state/finite_environment_validation.lock').open('rb+') as f:
  fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);lock_free=True;fcntl.flock(f,fcntl.LOCK_UN)
 n=subprocess.run(['nvidia-smi','--query-gpu=index,name,uuid,driver_version,memory.total,memory.used,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True)
 c=subprocess.run(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name','--format=csv,noheader'],capture_output=True,text=True,check=True)
 baseline={'.agents','.codex','.git','4dgs_research_reset_r0','ADC-GS','ADC-GS-master','ADC-GS-origin','CERTEDIT4D_CODEX_MASTER_PROMPT.md','CertEdit4D','__pycache__','bfa_candidate_sources','ec4dgs_workspace','tri_comp_4dgs_phase0','worldmodel'}
 actual={p.name for p in ROOT.parent.iterdir()};assert baseline<=actual
 launcher='''#!/bin/bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
exec "$ROOT/run-python-compat.sh" "$@"
'''
 write_new(ROOT/'run-python.sh',launcher,0o700)
 owned_app='''"""Owned per-application launch configuration; no installed SDK source edits."""
from isaaclab.app import AppLauncher
class Zonglin2AppLauncher(AppLauncher):
    def _create_app(self):
        self._sim_app_config["enable_crashreporter"] = False
        self._sim_app_config["extra_args"] = ["--/crashreporter/preserveDump=true", "--/crashreporter/enabled=false", "--/app/renderer/enabled=false", "--/renderer/enabled=false", "--/app/window/enabled=false"]
        super()._create_app()
'''
 write_new(ROOT/'tools/zonglin2_app_launcher.py',owned_app)
 readme='''# zonglin2 — isolated source4090 environment

Validated in this directory on 2026-10-15 (actual timestamps in audit/).
Python3.12.14, Torch2.10.0+cu128, TensorDict0.14.1, RSL5.0.1,
Isaac Sim distribution6.0.1.0, Lab distribution6.1.14. Actual Lab imports
from src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source.

Both RTX4090s passed actual CUDA arithmetic and, sequentially, Lab headless
GPU PhysX24-step falling-box checks with finite CUDA poses/velocities,
physical UUID verification and natural EXIT0. Lab runtime imports passed.
This validates this physics-only environment; no MOD4 robot, full-state
restore, training, rendering, cameras or deadline qualification is claimed.

```bash
cd '/home/lc01/Zonglin Li/zonglin2'
./run-python.sh -c 'import torch; print(torch.__version__, torch.cuda.device_count())'
CUDA_VISIBLE_DEVICES=0 ./run-python.sh your_script.py
# Select the second physical GPU with CUDA_VISIBLE_DEVICES=1.
```

Use the quoted launcher, including for `-m pip`. Direct copied shebang
entrypoints and activating the conda copy alone do not provide the private
libc loader and may fail because the parent path contains a space.
run-python.sh uses a private glibc2.40 loader in compat/glibc240; no system
glibc or NVIDIA driver was upgraded. All HOME/XDG/cache/tmp writes are
redirected below this directory. Source host and existing environments
were read-only. All original archives and failed probes are retained.

For IsaacLab applications use the headless AppLauncher path, not the
default graphics-heavy SimulationApp/legacy World startup. The initial
default startup failed and remains recorded. A reusable owned launch-config
subclass is tools/zonglin2_app_launcher.py; it uses supported SimulationApp
settings to disable crash reporting, preserve inherited historical dumps,
and request no rendering. It changes no installed source or physics logic.
Both successful probes under audit/owned_Lab_gpu[01]_physics_v7.py show the
exact validated initialization and cleanup. These once-only audit probes
are retained evidence and must not be re-executed in place.

No training job is running as part of this deployment. Old runtime logs
copied from the source retain their original paths and are historical.
'''
 write_new(ROOT/'README.md',readme)
 artifacts=[]
 for p in (ROOT/'run-python.sh',ROOT/'run-python-native.sh',ROOT/'run-python-compat.sh',ROOT/'README.md',ROOT/'tools/zonglin2_app_launcher.py',ROOT/'audit/EXTRACTED_FILE_SHA_V1.jsonl'):
  artifacts.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p),original_retained=True))
 archive=json.loads((ROOT/'audit/SOURCE_ARCHIVE_V2_STREAM_SHA_ACTUAL.json').read_bytes())
 assert Path(archive['path']).stat().st_size==archive['bytes']
 v=dict(epoch=time.time(),status='DEPLOYED_HEADLESS_TWO_GPU_LAB_PHYSX_VALIDATED',root=str(ROOT),
  source_archive_actual_path_size_SHA=archive,artifacts=artifacts,actual_process_exit_snapshots=processes,
  actual_validation_fcntl_free=lock_free,actual_GPU_snapshot=n.stdout,actual_compute_snapshot=c.stdout,
  original_base_entries_still_present=sorted(baseline),all_owned_installation_and_runtime_paths_below_root=True,
  no_manual_deletion_system_driver_profile_original_environment_or_source_mutation=True,
  private_userspace_GLIBC_support_only=True,both_CUDA_and_headless_Lab_GPU_PhysX_actual_passed=True,
  original_native_GLIBC_V3_default_scene_V4_Warp_V5_metadata_V6_prebootstrap_errors_retained=True,
  historical_copied_crash_metadata_is_not_current_target_training=True,
  source_old_absolute_home_exists_on_target=Path('/home/egde').exists(),no_training_PPO_budget_or_MOD4_full_contract_admission=True)
 with (ROOT/'audit/ZONGLIN2_DEPLOYMENT_CLOSURE_V1_ACTUAL.json').open('x') as f:json.dump(v,f,indent=2)
 print(json.dumps(v),flush=True)
if __name__=='__main__':main()

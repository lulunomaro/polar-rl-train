from pathlib import Path
import os,psutil
GPU='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python3.12'
def own_identity(pid):
 q=psutil.Process(pid);return dict(pid=q.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),cwd=q.cwd())
def environment(J,gpu):
 env=dict(os.environ,CUDA_VISIBLE_DEVICES=GPU if gpu else '',PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
 for k in ('PYTHONHOME','PYTHONPATH','LD_PRELOAD'):env.pop(k,None)
 for k,n in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda','PIP_CACHE_DIR':'cache/pip','TRITON_CACHE_DIR':'cache/triton','WARP_CACHE_PATH':'cache/warp','NUMBA_CACHE_DIR':'cache/numba','MPLCONFIGDIR':'cache/matplotlib','__GL_SHADER_DISK_CACHE_PATH':'cache/gl'}.items():
  p=J/n;assert p.resolve().is_relative_to(J);p.mkdir(parents=True,exist_ok=True);env[k]=str(p)
 return env

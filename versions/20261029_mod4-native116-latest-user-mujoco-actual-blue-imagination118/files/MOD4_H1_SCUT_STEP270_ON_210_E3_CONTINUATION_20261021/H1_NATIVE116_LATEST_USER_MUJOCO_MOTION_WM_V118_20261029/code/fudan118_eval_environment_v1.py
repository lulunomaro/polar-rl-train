"""Original environment function, exact AST; scratch J is new eval-owned path."""
from pathlib import Path
import os
J=None
def bind_private_job_root(path):
 global J
 J=Path(path);J.mkdir(parents=True,exist_ok=False)
def environment(spec,cpu=False):
 e=dict(os.environ)
 for k in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):e.pop(k,None)
 for n in ('home','tmp','cache','config','data'):(J/n).mkdir(exist_ok=True)
 e.update(CUDA_VISIBLE_DEVICES='' if cpu else spec['GPU_UUID'],HOME=str(J/'home'),TMPDIR=str(J/'tmp'),XDG_CACHE_HOME=str(J/'cache'),XDG_CONFIG_HOME=str(J/'config'),XDG_DATA_HOME=str(J/'data'),PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y');return e

"""Small new read-only SDK reward weight/dt source purpose, no import/SDK run."""
from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parent;D=R/'discovery/sdk_reward_scale_v1';out=R/'reports/SDK_REWARD_SCALE_SOURCE_READ_V1.json';assert not D.exists()and not out.exists();D.mkdir(parents=True)
ref=json.loads((R/'reports/SDK_REWARD_COMMAND_SOURCE_READ_V1.json').read_bytes());base=ref['root_from_actual_prior_spec'];sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp();rows=[]
try:
 for rel in ('managers/reward_manager.py','envs/mdp/rewards.py'):
  with s.open(base+'/'+rel,'rb')as f:raw=f.read()
  assert len(raw)<1_000_000
  dest=D/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);rows.append(dict(relative=rel,remote=base+'/'+rel,path=str(dest),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
 value=dict(kind='REFERENCED_REWARD_WEIGHT_DT_SOURCE_ONLY',files=rows,actual_live_backend_binding=None,SDK_GPU_PT_raw_C_GO_or_mutation_operations=0);out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(out);print(json.dumps(value,indent=2))
finally:s.close();c.close()

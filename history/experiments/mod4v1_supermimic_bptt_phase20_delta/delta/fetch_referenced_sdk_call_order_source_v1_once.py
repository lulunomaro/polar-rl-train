"""Read only three SDK source facades and directly named base counterparts.
Package root is bound by earlier actual top-level find_spec metadata, not guessed.
No import of SDK, App, GPU libraries, source models, logs, or canonical.
"""
from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parent;D=R/'discovery/sdk_reward_command_call_order_v1';out=R/'reports/SDK_REWARD_COMMAND_SOURCE_READ_V1.json';assert not D.exists()and not out.exists()
T=R.parent/'mod4v1_experts_fulldr_rm70_20261101';spec=json.loads((T/'diagnostics/W35_SDK_DATA_GETTER_ORIGIN_SOURCE_V1/ACTUAL_MODULE_SPEC_SOURCE_READ_V2.json').read_bytes());assert not spec['SDK_imported'];base=spec['search_locations'][0]
sys.path.insert(0,str(T));from project_connector import connect72
paths=('envs/manager_based_rl_env.py','managers/command_manager.py','envs/mdp/observations.py','envs/base_manager_based_rl_env.py','envs/base_manager_based_env.py','managers/base_command_manager.py','envs/mdp/base_observations.py')
D.mkdir(parents=True);c=connect72();s=c.open_sftp();rows=[]
try:
 for relative in paths:
  remote=base+'/'+relative
  try:
   with s.open(remote,'rb')as f:raw=f.read()
  except FileNotFoundError:rows.append(dict(relative=relative,remote=remote,status='named_base_counterpart_absent_not_inferred'));continue
  assert len(raw)<1_000_000
  dest=D/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);rows.append(dict(relative=relative,remote=remote,path=str(dest),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),status='actual_source_bytes_read_no_import'))
 value=dict(kind='REFERENCED_SDK_CALL_ORDER_SOURCE_NO_RUNTIME_BINDING_CLAIM',root_from_actual_prior_spec=base,source_spec_reference=str(T/'diagnostics/W35_SDK_DATA_GETTER_ORIGIN_SOURCE_V1/ACTUAL_MODULE_SPEC_SOURCE_READ_V2.json'),files=rows,actual_live_backend_method_binding=None,SDK_App_GPU_PT_raw_GO_lock_C_operations=0)
 out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(out);print(json.dumps(value,indent=2))
finally:s.close();c.close()

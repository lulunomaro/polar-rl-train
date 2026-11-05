"""Read only the known SDK Python ABI files needed for the SCUT source port; no imports/runtime."""
from pathlib import Path
import json,sys,hashlib,time
D=Path(__file__).resolve().parent;out=D/'sdk_scut_alignment_abi_source_v1';assert not out.exists();out.mkdir();sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
root='/home/lc01/Zonglin Li/zonglin2/src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab';names=['managers/reward_manager.py','envs/manager_based_rl_env.py','managers/command_manager.py','envs/mdp/commands/velocity_command.py','managers/action_manager.py'];rows=[];c=connect72();s=c.open_sftp()
try:
 for rel in names:
  assert rel.endswith('.py')and'..'not in rel
  with s.open(root+'/'+rel,'rb')as f:b=f.read()
  p=out/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);rows.append(dict(source=root+'/'+rel,local=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
finally:s.close();c.close()
r=dict(kind='CURRENT_KNOWN_SDK_SOURCE_ABI_READBACK_NOT_RUNTIME_TEST',epoch=time.time(),rows=rows,model_raw_GPU_SDK_execution_C_or_foreign_operations=0);(out/'SOURCE_RECEIPT.json').write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r,indent=2))

"""Read only the current SDK array-view and quaternion math source; never execute SDK."""
from pathlib import Path
import json,sys,hashlib
D=Path(__file__).resolve().parent;out=D/'sdk_scut_tensor_math_abi_source_v1';assert not out.exists();sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
root='/home/lc01/Zonglin Li/zonglin2/src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/';c=connect72();s=c.open_sftp();items=[]
try:
 names=s.listdir(root+'utils/warp');rels=['utils/math.py','utils/warp/__init__.py'];rels += ['utils/warp/'+x for x in names if x.endswith('.py')and('proxy'in x.lower())]
 for rel in rels:
  with s.open(root+rel,'rb')as f:raw=f.read()
  p=out/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);items.append(dict(source=root+rel,local=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
finally:s.close();c.close()
(out/'SOURCE_RECEIPT.json').write_text(json.dumps(dict(kind='SOURCE_ONLY_CURRENT_SDK_TENSOR_AND_QUATERNION_ABI_NOT_RUNTIME_PROOF',rows=items,SDK_model_GPU_C_operations=0),indent=2),encoding='utf8');print(json.dumps(items,indent=2))

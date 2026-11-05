"""Follow the fetched ArticulationData factory's explicit imports; read two Python sources only."""
from pathlib import Path
import json,sys,time,hashlib
D=Path(__file__).resolve().parent;out=D/'sdk_scut_joint_data_abi_source_v2';assert not out.exists();base='/home/lc01/Zonglin Li/zonglin2/src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source';targets={'base_articulation_data.py':base+'/isaaclab/isaaclab/assets/articulation/base_articulation_data.py','physx_articulation_data.py':base+'/isaaclab_physx/isaaclab_physx/assets/articulation/articulation_data.py'}
sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp();rows=[];blobs={}
try:
 for name,path in targets.items():
  with s.open(path,'rb')as f:raw=f.read()
  blobs[name]=raw;rows.append(dict(source=path,local=str(out/name),bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest()))
finally:s.close();c.close()
out.mkdir()
for name,raw in blobs.items():(out/name).write_bytes(raw)
r=dict(kind='EXPLICIT_IMPORTED_PHYSX_DATA_PYTHON_SOURCE_NOT_LIVE_ABI_PROOF',epoch=time.time(),rows=rows,SDK_execute_model_GPU_C_foreign_operations=0);(out/'SOURCE_RECEIPT.json').write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r,indent=2))

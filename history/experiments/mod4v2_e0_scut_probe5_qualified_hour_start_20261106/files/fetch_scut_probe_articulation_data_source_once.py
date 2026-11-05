"""Fetch one known SDK Python source to diagnose the closed probe's tensor ABI; no SDK execution."""
from pathlib import Path
import json,sys,hashlib,time
D=Path(__file__).resolve().parent;out=D/'sdk_scut_joint_data_abi_source_v1';assert not out.exists();src='/home/lc01/Zonglin Li/zonglin2/src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/assets/articulation/articulation_data.py'
pointer=json.loads((D/'E0_SCUT_PROBE_CLOSED_RESULT_PATH.json').read_bytes());closed=json.loads(Path(pointer['path']).read_bytes());m=closed['metadata'];assert closed['closed']is True and all(m['OWNER_EXIT_ACTUAL.json'][k]is True for k in('all_own_children_waited','original_cost_settled','original_private_finite_authority_leases_released'))and m['OUTER_OWNER_WAIT_ACTUAL.json']['original_owner_reaped']is True
sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 with s.open(src,'rb')as f:raw=f.read()
finally:s.close();c.close()
out.mkdir();p=out/'articulation_data.py';p.write_bytes(raw);r=dict(kind='CLOSED_SCUT_PROBE_SDK_JOINT_DATA_SOURCE_NOT_RUNTIME_READBACK',source=src,local=str(p),bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest(),epoch=time.time(),model_GPU_SDK_runtime_or_C_operations=0);(out/'SOURCE_RECEIPT.json').write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r,indent=2))

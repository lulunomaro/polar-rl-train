"""One own closed-purpose wrapper source readback; no SDK import, model or runtime operations."""
from pathlib import Path
import sys,json,hashlib
D=Path(__file__).resolve().parent;out=D/'e0_hour_actual_recipe_sources/mod4_env.py';assert not out.exists();stage=json.loads((D/'STAGE_E0_HOUR_WINDOW_RESULT.json').read_bytes());closed=json.loads(Path(json.loads((D/'E0_HOUR_WINDOW_CLOSED_RESULT_PATH.json').read_bytes())['path']).read_bytes());assert closed['closed']is True and closed['root']==stage['root']and closed['metadata']['OUTER_OWNER_WAIT_ACTUAL.json']['original_owner_reaped']is True
sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp();source=stage['root']+'/roles/E0/runtime/isaac/mod4/mod4_env.py'
try:
 with s.open(source,'rb')as f:b=f.read()
finally:s.close();c.close()
out.write_bytes(b);r=dict(source=source,local=str(out),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),own_closed_source_only=True,model_raw_GPU_SDK_execution_C_or_foreign_operations=0);(D/'E0_HOUR_MOD4_WRAPPER_SOURCE_RECEIPT.json').write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r,indent=2))

"""Bounded closed-window error/source diagnosis, no new SDK/model/C/GO.
Read actual linked buffer sources and own new secondary error sidefiles only.
"""
from pathlib import Path
import json,sys,hashlib
R=Path(__file__).resolve().parent;out=R/'reports/A1_V5_CLOSED_TIMESTAMP_APPCLOSE_DIAGNOSIS_V1.json';D=R/'discovery/sdk_warp_timestamp_actual_v4';assert not out.exists()and not D.exists();D.mkdir(parents=True);prior=json.loads((R/'reports/A1_NATIVE_V5_ACTUAL_NONPT_STAGE_V1.json').read_bytes());root=prior['root'];closed=json.loads((R/'reports/ACTUAL_A1_NATIVE_V5_20261102_215643/CLOSED_RESULT.json').read_bytes());assert closed['parent_exit']['all_own_children_waited']and closed['parent_exit']['original_cost_settled']
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
base='/home/lc01/Zonglin Li/zonglin2/src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/utils/buffers';c=connect72();s=c.open_sftp();sources=[];errors=[]
try:
 names=sorted(s.listdir(base));selected=[n for n in names if n.endswith('.py')and('warp'in n.lower()or'timestamp'in n.lower())];assert 1<=len(selected)<=8
 for name in selected:
  assert '/'not in name and'\\'not in name
  with s.open(base+'/'+name,'rb')as f:raw=f.read()
  assert len(raw)<500_000;dest=D/name;dest.write_bytes(raw);sources.append(dict(remote=base+'/'+name,path=str(dest),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
 for row in closed['rows']:
  paths=((row.get('actual_parent_waited')or{}).get('semantic_result')or{}).get('error_sidefiles',[])
  for path in paths:
   assert path.startswith(root+'/roles/'+row['role']+'/production/')and path.endswith('.json')
   if '/WORKER_ERROR_SECONDARY_'not in path:continue
   with s.open(path,'rb')as f:raw=f.read()
   assert len(raw)<256_000;dest=D/(row['role']+'_'+Path(path).name);dest.write_bytes(raw);errors.append(dict(role=row['role'],remote=path,path=str(dest),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=json.loads(raw)))
 value=dict(kind='CLOSED_V5_REAL_TIMESTAMP_AND_CLOSE_ERRORS_SOURCE_DIAGNOSIS',closed_root=root,buffer_directory_names=names,source_files=sources,secondary_errors=errors,SDK_model_GPU_C_GO_lock_signal_operations=0);out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value,indent=2))
finally:s.close();c.close()

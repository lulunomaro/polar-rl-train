"""Read only this live purpose's immutable source and selected configuration, not models/state/authority."""
from pathlib import Path
import json,sys,hashlib,posixpath
D=Path(__file__).resolve().parent;stage=json.loads((D/'STAGE_E0_HOUR_WINDOW_RESULT.json').read_bytes());root=stage['root'];job=root+'/roles/E0';out=D/'E0_HOUR_CURRENT_RECIPE_SOURCE_READBACK_V1.json';dest=D/'e0_hour_actual_recipe_sources';assert not out.exists()and not dest.exists();sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
client=connect72();s=client.open_sftp()
def raw(path):
 assert path.startswith(job+'/') and path.endswith(('.py','.json'))
 with s.open(path,'rb')as f:return f.read()
try:
 task=json.loads(raw(job+'/TASK.json'));manifest=task.get('original_run_manifest');manifest=manifest if manifest and manifest.startswith('/')else posixpath.join(job,manifest or'original_run_manifest.json');env=task.get('original_env')or json.loads(raw(manifest))['env'];selected={k:v for k,v in env.items()if k.startswith(('RM_','SCUT_','MOD4_','MOD4V1_','OWN_'))};sources={}
 for name in('scut_flat_rescue.py','mod4_task.py','train_mod4v1_e0.py','config_mod4v1_e0.py','chassis_pd_training_env.py'):
  path=job+'/runtime/isaac/mod4/'+name
  try:b=raw(path)
  except FileNotFoundError:sources[name]={'path':path,'present':False};continue
  sources[name]={'path':path,'present':True,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'text':b.decode('utf8')}
finally:s.close();client.close()
dest.mkdir();index={}
for name,row in sources.items():
 index[name]={k:v for k,v in row.items()if k!='text'}
 if row['present']:(dest/name).write_text(row['text'],encoding='utf8',newline='\n')
r=dict(kind='OWN_ACTIVE_E0_IMMUTABLE_SOURCE_AND_SELECTED_ENV_NOT_LIVE_REWARD_TENSOR_PROOF',root=root,role=task['role'],selected_original_environment=selected,source_manifest_path=manifest,sources=index,model_raw_GPU_SDK_C_or_foreign_operations=0,no_running_source_or_config_modified=True);out.write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r,indent=2))

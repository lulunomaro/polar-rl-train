"""New diagnostic-input identity purpose: four exact producer JSONs, no model/raw/SDK/C."""
from pathlib import Path
import sys,json,hashlib,importlib.util,time
R=Path(__file__).resolve().parent;out=R/'reports/REPLAY_DIAGNOSTIC_ACTUAL_FINAL_TASK_PINS_V1.json';marker=R/'REPLAY_DIAGNOSTIC_METADATA_PIN_V1_STARTED_ONCE.json';assert not out.exists()and not marker.exists()
p=R/'source_replay_consistency_diagnostic_v1/replay_consistency_diagnostic_v1.py';raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()=='a372478e40d1eb0b569f1f6c86d45f285031ab5399e00efe61b20bdc2f462eec';spec=importlib.util.spec_from_file_location('_pinned_diagnostic_metadata_contract',p);d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
marker.write_text(json.dumps(dict(epoch=time.time(),kind='FOUR_EXACT_PRODUCER_JSON_INPUT_PINS_ONLY',selected_checkpoint_or_raw_reads=0),indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp();value=dict(kind='ACTUAL_PRODUCER_FINAL_TASK_DIAGNOSTIC_INPUT_PINS_V1',roles={},selected_model_or_raw_or_SDK_GPU_canonical_operations=0)
try:
 for role in ('E3','W35'):
  job,final_path,checkpoint=d.role_paths(role);items={};objects={}
  for key,path in (('FINAL',final_path),('TASK',job+'/TASK.json')):
   st=s.stat(path);assert 0<st.st_size<16*1024*1024
   with s.open(path,'rb')as f:data=f.read()
   assert len(data)==st.st_size;obj=json.loads(data);items[key]=dict(path=path,bytes=len(data),SHA256=hashlib.sha256(data).hexdigest());objects[key]=obj
  d.validate_final(objects['FINAL'],role)
  for k,v in dict(role=role,role_key=d.OWN[role]['role_key'],run_id=d.RUN,num_envs=1024,asset_SHA=d.ASSET,contract_SHA=d.CONTRACT).items():d.need(d.same_json_type_value(objects['TASK'].get(k),v),'TASK metadata differs: '+k)
  value['roles'][role]=dict(files=items,actual_final_contract_passed=True,actual_task_identity_passed=True,producer_counts=objects['FINAL']['counts'],checkpoint_producer_metadata=objects['FINAL']['checkpoint'],seed=objects['TASK']['seed'],snapshot_is_not_a_new_checkpoint_read=True)
  out.write_text(json.dumps(value,indent=2),encoding='utf-8')
 value['all_four_actual_JSON_pins_and_predecode_contracts_passed']=True;out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value,indent=2))
except BaseException as e:
 value['error']=dict(type=type(e).__name__,message=str(e));out.write_text(json.dumps(value,indent=2),encoding='utf-8');raise
finally:s.close();c.close()

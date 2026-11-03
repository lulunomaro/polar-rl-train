"""NEW exact original-worker metadata location diagnosis, not preflight replay.
The first attempted nested JSONs were absent. Original E1 worker consumes ROOT
E1_CANONICAL_SOURCE_METADATA.json; only these two source JSONs are read here.
"""
from pathlib import Path
import hashlib,json,sys,time
R=Path(__file__).resolve().parent;out=R/'reports/GOOD_HOLDOUT_RUNTIME_ROOT_CANONICAL_METADATA_DIAGNOSIS_V2.json';dest=R/'discovery/good_holdout_runtime_root_metadata_v2';assert not out.exists()and not dest.exists();H=lambda b:hashlib.sha256(b).hexdigest();prev=json.loads((R/'reports/GOOD_HOLDOUT_SELECTED_RUNTIME_CANONICAL_METADATA_DIAGNOSIS_V1.json').read_bytes());assert len(prev['rows'])==2 and all(x['status']=='NOT_FOUND'for x in prev['rows']);root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700';dest.mkdir();rows=[]
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 for role in('CURB_PROTECTED878','SLOPE135'):
  path=root+'/runtimes/'+role+'/E1_CANONICAL_SOURCE_METADATA.json'
  try:
   with s.open(path,'rb')as f:raw=f.read(262145)
  except FileNotFoundError:rows.append(dict(role=role,path=path,status='NOT_FOUND',read_attempts=1));continue
  assert 0<len(raw)<=262144;sha=H(raw);v=json.loads(raw);assert type(v)is dict;p=dest/(role+'_E1_CANONICAL_SOURCE_METADATA.json')
  with p.open('xb')as f:f.write(raw)
  rows.append(dict(role=role,path=path,status='READ_ORIGINAL_ROOT_METADATA_ONCE',bytes=len(raw),SHA256=sha,local_path=str(p),original_canonical=v.get('canonical'),canonical_equals_role=v.get('canonical')==role,keys=list(v),read_count=1,hash_count=1,decode_count=1))
finally:s.close();c.close()
v=dict(kind='GOOD_HOLDOUT_ORIGINAL_WORKER_ROOT_METADATA_FUNCTIONAL_DIAGNOSIS_V2',epoch=time.time(),rows=rows,original_nested_metadata_failure_preserved=True,actual_model_raw_trajectory_static_bank_SDK_GPU_C_lock_signal_or_parent_operations=0,gate1='UNKNOWN',stage2_GO=False)
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))

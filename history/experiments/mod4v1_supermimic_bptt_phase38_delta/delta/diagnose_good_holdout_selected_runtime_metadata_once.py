"""NEW functional metadata-input diagnosis after D4 preflight stopped.
Only the two exact original E1 canonical JSONs; no model/static bank/SDK/resource.
"""
from pathlib import Path
import hashlib,json,sys,time
R=Path(__file__).resolve().parent;out=R/'reports/GOOD_HOLDOUT_SELECTED_RUNTIME_CANONICAL_METADATA_DIAGNOSIS_V1.json';dest=R/'discovery/good_holdout_selected_runtime_metadata_v1';assert not out.exists()and not dest.exists();H=lambda b:hashlib.sha256(b).hexdigest();failed=json.loads((R/'reports/GOOD_HOLDOUT_D4_SEED20260929_ACTUAL_PREFLIGHT_V1.json').read_bytes());assert failed['returncode']==1 and 'actual selected E1 canonical metadata differs'in failed['stderr'];wire=(R/'discovery/good_holdout_original_plan_wire_v1/ACTUAL_ORIGINAL_GROUP_PLAN_WIRE.json').read_bytes();assert H(wire)=='a78cbaf8961264f16bdd1007dbab72a0fb442fae080978f057e52fef1dfd7fd1';plan=json.loads(wire);roles={x['role']:x for x in plan['roles']};root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700';rel='runtime/isaac/mod4/E1_CANONICAL_SOURCE_METADATA.json';dest.mkdir();rows=[]
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 for role in('CURB_PROTECTED878','SLOPE135'):
  runtime=roles[role]['runtime_root'];assert runtime==root+'/runtimes/'+role;path=runtime+'/'+rel
  try:
   with s.open(path,'rb')as f:raw=f.read(262145)
  except FileNotFoundError:rows.append(dict(role=role,path=path,status='NOT_FOUND',read_attempts=1));continue
  assert 0<len(raw)<=262144;sha=H(raw);value=json.loads(raw);assert type(value)is dict;local=dest/(role+'_E1_CANONICAL_SOURCE_METADATA.json')
  with local.open('xb')as f:f.write(raw)
  rows.append(dict(role=role,path=path,status='READ_ORIGINAL_WHOLE_METADATA_ONCE',bytes=len(raw),SHA256=sha,local_path=str(local),original_canonical_field=value.get('canonical'),canonical_field_python_type=type(value.get('canonical')).__name__,canonical_equals_role=value.get('canonical')==role,keys=list(value),read_count=1,hash_count=1,decode_count=1))
finally:s.close();c.close()
v=dict(kind='GOOD_HOLDOUT_ACTUAL_SELECTED_RUNTIME_CANONICAL_METADATA_FUNCTIONAL_DIAGNOSIS_V1',epoch=time.time(),source_failed_root=failed['root'],rows=rows,actual_model_raw_trajectory_static_bank_SDK_GPU_C_lock_signal_or_parent_operations=0,old_failed_preflights_unchanged=True,gate1='UNKNOWN',stage2_GO=False)
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))

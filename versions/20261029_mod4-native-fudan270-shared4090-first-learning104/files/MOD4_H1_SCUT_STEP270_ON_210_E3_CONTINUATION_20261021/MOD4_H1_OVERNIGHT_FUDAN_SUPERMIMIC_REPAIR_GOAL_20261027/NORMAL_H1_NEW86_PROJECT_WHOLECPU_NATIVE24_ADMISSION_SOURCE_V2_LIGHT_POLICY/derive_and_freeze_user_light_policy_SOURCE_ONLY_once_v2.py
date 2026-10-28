"""V2 source only. Preserve V1, change only specified GPU predicate + bindings."""
from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;L=B.parent;OLD=L/'NORMAL_H1_NEW86_PROJECT_WHOLECPU_NATIVE24_ADMISSION_SOURCE_V1'
def H(x):return hashlib.sha256(x).hexdigest()
def main():
 assert not (B/'FROZEN_NORMAL_H1_NEW86_ADMISSION_SOURCE_INDEX_V2.json').exists();(B/'reports').mkdir(exist_ok=True)
 previous=json.loads((OLD/'FROZEN_NORMAL_H1_NEW86_ADMISSION_SOURCE_INDEX_V1.json').read_bytes())
 for name,want in previous['executable_source_SHAs'].items():assert H((OLD/name).read_bytes())==want
 control_old=OLD/'remote_project_source_and_waited_admission_v1.py';raw=control_old.read_bytes()
 needle=b"ready=idle and row[0]==GPU and row[1]=='NVIDIA GeForce RTX 4090' and int(row[2])>15669 and available>32*1024**3 and shutil.disk_usage(ROOT).free>25*1024**3"
 replacement=b"ready=row[0]==GPU and row[1]=='NVIDIA GeForce RTX 4090' and int(row[2])>15669 and int(row[3])<=30 and available>32*1024**3 and shutil.disk_usage(ROOT).free>25*1024**3"
 assert raw.count(needle)==1;new=raw.replace(needle,replacement);assert new.replace(replacement,needle)==raw;ast.parse(new)
 control=B/'remote_project_source_and_waited_admission_v2_user_light_GPU.py';control.write_bytes(new)
 # Same runtime/model/CPU/GPU worker inputs; no model or binary is opened here.
 for name in ('target_normal_H1_whole_source_SDK_CPU_once_v1.py','target_normal_H1_CUDA_fullrestore_frozen_native24_once_v1.py'):(B/name).write_bytes((OLD/name).read_bytes())
 entry_old=OLD/'upload_and_admit_NEW86_normal_H1_wholeCPU_native24_secure_stdin_UNUSED_once_v1.py';entry=entry_old.read_bytes();ops=[
  (b'FROZEN_NORMAL_H1_NEW86_ADMISSION_SOURCE_INDEX_V1.json',b'FROZEN_NORMAL_H1_NEW86_ADMISSION_SOURCE_INDEX_V2.json'),
  (b'remote_project_source_and_waited_admission_v1.py',b'remote_project_source_and_waited_admission_v2_user_light_GPU.py'),
  (b'NORMAL_H1_PPO86B40050_WHOLECPU_NATIVE24_20261029v1',b'NORMAL_H1_PPO86B40050_WHOLECPU_NATIVE24_20261029v2')]
 for a,b in ops:assert entry.count(a)>0;entry=entry.replace(a,b)
 inverse=entry
 for a,b in reversed(ops):inverse=inverse.replace(b,a)
 assert inverse==entry_old.read_bytes();ast.parse(entry)
 entry_name='upload_and_admit_NEW86_normal_H1_wholeCPU_native24_secure_stdin_UNUSED_once_v2_user_light_GPU.py';(B/entry_name).write_bytes(entry)
 mf=OLD/'NORMAL_H1_ADMISSION_COMPLETE_INPUT_MANIFEST_V1.json';assert H(mf.read_bytes())==previous['manifest_SHA'];m=json.loads(mf.read_bytes());m['resource_policy_extension']=dict(kind='user_authorized_small_existing_compute_v2',original_manifest_SHA=previous['manifest_SHA'],free_MiB_strictly_greater_than=15669,util_percent_at_most=30,selected_compute_UUID_rows_may_be_nonempty=True,no_unknown_PID_query_or_thirdparty_change=True,private_EX_RAM32GiB_disk25GiB_and_all_other_code_unchanged=True,remote_coordinator_SHA=H(new))
 target=B/'NORMAL_H1_ADMISSION_COMPLETE_INPUT_MANIFEST_V1.json';target.write_text(json.dumps(m,indent=2)+'\n')
 executable={p.name:H(p.read_bytes()) for p in B.glob('*.py') if p.name!='derive_and_freeze_user_light_policy_SOURCE_ONLY_once_v2.py'}
 for p in B.glob('*.py'):
  tree=ast.parse(p.read_bytes())
  for n in tree.body:
   if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str) and any(isinstance(x,ast.Name) and x.id=='AUTH' for x in n.targets):ast.parse(n.value.value)
 value=dict(previous);value.update(status='FROZEN_UNUSED_SOURCE_ONLY_V2_USER_LIGHT_GPU',epoch=time.time(),entry_filename=entry_name,entry_SHA=executable[entry_name],manifest_SHA=H(target.read_bytes()),executable_source_SHAs=executable,base_V1_source_index_SHA=H((OLD/'FROZEN_NORMAL_H1_NEW86_ADMISSION_SOURCE_INDEX_V1.json').read_bytes()),resource_policy_extension=m['resource_policy_extension'])
 proof=dict(epoch=time.time(),source_only=True,old_coordinator_SHA=H(raw),new_coordinator_SHA=H(new),exact_inverse_single_resource_predicate_bytes=True,old_predicate=needle.decode(),new_predicate=replacement.decode(),all_other_coordinator_AST_and_bytes_unchanged=True,entry_only_new_source_index_coordinator_basename_new_namespace_bindings=True,entry_inverse_bytes=True,CPU_GPU_workers_byteidentical=True,453_input_rows_bytevalue_unchanged=m['files']==json.loads(mf.read_bytes())['files'],no_model_raw_USD_NPZ_GPU_or_network=True,not_actual_GPU_idle_or_native24_or_PPO_proof=True)
 (B/'V2_EXACT_USER_LIGHT_GPU_RESOURCE_DELTA_SOURCE_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
 out=B/'FROZEN_NORMAL_H1_NEW86_ADMISSION_SOURCE_INDEX_V2.json';out.write_text(json.dumps(value,indent=2)+'\n')
 print(json.dumps(dict(entry=str(B/entry_name),entry_SHA=value['entry_SHA'],index=str(out),index_SHA=H(out.read_bytes()),manifest_SHA=value['manifest_SHA'],exact_single_predicate_inverse=True,no_target_execution=True)))
if __name__=='__main__':main()

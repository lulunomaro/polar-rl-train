"""Assemble exact qualified W35 inputs and secure entry; no model/data/network."""
from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;L=B.parent
def H(x):return hashlib.sha256(x).hexdigest()
def main():
 oldmf=L/'W35_210_V2_PRECLOSE_EXCEPTION_DIAGNOSTIC_SOURCE_V1/W35_V2_PRECLOSE_COMPLETE_INPUT_MANIFEST.json';m=json.loads(oldmf.read_bytes());rows={r['relative']:dict(r) for r in m['files']};assert len(rows)==467
 cpu=B/'W35_new86_target_FINAL92_source_SDK_CPU_admission_v1.py';raw=cpu.read_bytes();needle=b"report=root/'W35_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V1.json';assert not report.exists()";replacement=needle+b"\n from project_clone_launch_helpers_v1 import own_identity\n with (root/'W35_CPU_OWN_WORKER_IDENTITY.json').open('x') as f:json.dump(own_identity(os.getpid()),f,indent=2)";assert raw.count(needle)==1;new=raw.replace(needle,replacement);assert new.replace(replacement,needle)==raw;ast.parse(new);cpuname='W35_new86_target_FINAL92_source_SDK_CPU_admission_v2_self_identity.py';(B/cpuname).write_bytes(new)
 del rows['detached_W35_frozen_eval_private210_supervisor_once_v1.py']
 for name in ('evaluate_W35_adapted92_originalN20K_frozen_profiles_once_v1.py','detached_W35_new86_frozen_profile_supervisor_once_v1.py',cpuname,'project_clone_launch_helpers_v1.py'):
  p=B/name;raw=p.read_bytes();ast.parse(raw);rows[name]=dict(relative=name,local_path=str(p.resolve()),bytes=len(raw),SHA=H(raw),index_kind='new86 source binding, original behavioral loop literal preserved')
 model=rows['source/W35_ADAPTED92_FINAL78.pt'];assert model['SHA']=='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f' and model['bytes']==17619013
 mf=B/'W35_NEW86_COMPLETE_INPUT_MANIFEST_V1.json';m.update(kind='NEW86_W35_ADAPTED92_FINAL78_FROZEN_N20K_PROFILE_INPUT_V1',files=list(rows.values()),typed_source_SHA=model['SHA'],prior_failed210_input_manifest_SHA=H(oldmf.read_bytes()),target_backend='new86',coverage=dict(controls=1200,policy_dt=.02,warmup_controls=100,steady_controls=1100,G3_families=5,nearest250_selected_pose=34,original_task_commands_and_criteria_retained=True,skill_graduation=False),source_only=True);mf.write_text(json.dumps(m,indent=2)+'\n')
 source=L/'NORMAL_H1_NEW86_PROJECT_WHOLECPU_NATIVE24_ADMISSION_SOURCE_V2_LIGHT_POLICY/upload_and_admit_NEW86_normal_H1_wholeCPU_native24_secure_stdin_UNUSED_once_v2_user_light_GPU.py';raw=source.read_bytes();assert H(raw)=='4e9bc93f9433a6da245e40bbfd3f84326d08e831b27ec9f9de4c71c334c4e14b';entry=raw.decode()
 for a,b in [
 ('FROZEN_NORMAL_H1_NEW86_ADMISSION_SOURCE_INDEX_V2.json','FROZEN_NEW86_W35_FROZEN_PROFILE_SOURCE_INDEX_V1.json'),
 ('NORMAL_H1_ADMISSION_COMPLETE_INPUT_MANIFEST_V1.json','W35_NEW86_COMPLETE_INPUT_MANIFEST_V1.json'),
 ('remote_project_source_and_waited_admission_v2_user_light_GPU.py','remote_W35_new86_profile_install_and_detach_v1.py'),
 ('/validation_runs/NORMAL_H1_PPO86B40050_WHOLECPU_NATIVE24_20261029v2','/evaluation_runs/W35_ADAPTED92_N20K_PROFILE_20261029v1/w35'),
 ('NEW86_NORMAL_H1','NEW86_W35'),('NEW86_normalH1','NEW86_W35'),('SAME_FINITE_NEW86_W35_SOURCE_CPU_NATIVE24','SAME_FINITE_NEW86_W35_SOURCE_CPU_DETACHED_PROFILES')]:
  assert a in entry,a;entry=entry.replace(a,b)
 # Prior normal-H1 native24 is a fixed runtime/robot-SDK witness only; no model reuse.
 lines=entry.splitlines(keepends=True);indices=[i for i,s in enumerate(lines) if s.lstrip().startswith('sdkpath=')];assert len(indices)==1
 lines[indices[0]]=" sdkpath=L/'NORMAL_H1_NEW86_PROJECT_WHOLECPU_NATIVE24_ADMISSION_SOURCE_V2_LIGHT_POLICY/reports/NEW86_NORMAL_H1_WHOLECPU_CUDA_NATIVE24_ORIGINAL_RETURNED_ACTUAL.json';assert H(sdkpath)==index['actual_clone_CUDA_SDK_receipt_SHA'];normal=json.loads(sdkpath.read_bytes());assert normal['passed_actual_wholeCPU_CUDA_fullrestore_native24_only'] and normal['private_EX_released']\n"
 entry=''.join(lines);a="dict(clone_complete=clone['complete'],known_cube_waited_record=scene)";b="dict(clone_complete=clone['complete'],normal_whole_result=normal)";assert entry.count(a)==1;entry=entry.replace(a,b)
 assert '1500' in entry and '1140' in entry;entry=entry.replace('1500','600').replace('1140','150');entryname='upload_admit_detach_NEW86_W35_final92_frozen_profiles_secure_stdin_UNUSED_once_v1.py';ast.parse(entry);(B/entryname).write_text(entry,encoding='utf8')
 # Source-only checks of every executable and embedded canonical reader.
 selected=(entryname,'remote_W35_new86_profile_install_and_detach_v1.py','evaluate_W35_adapted92_originalN20K_frozen_profiles_once_v1.py','detached_W35_new86_frozen_profile_supervisor_once_v1.py',cpuname,'project_clone_launch_helpers_v1.py')
 for name in selected:
  tree=ast.parse((B/name).read_bytes())
  for n in tree.body:
   if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str) and any(isinstance(t,ast.Name) and t.id=='AUTH' for t in n.targets):ast.parse(n.value.value)
 clone=L/'NEW_HOST_VERIFIED_BUNDLE_EXTRACT_RELOCATION_SOURCE_V1/reports/ROOT_VERIFIED_EXTRACT_RELOCATION_RETURNED_ACTUAL.json';normal=L/'NORMAL_H1_NEW86_PROJECT_WHOLECPU_NATIVE24_ADMISSION_SOURCE_V2_LIGHT_POLICY/reports/NEW86_NORMAL_H1_WHOLECPU_CUDA_NATIVE24_ORIGINAL_RETURNED_ACTUAL.json';assert json.loads(normal.read_bytes())['passed_actual_wholeCPU_CUDA_fullrestore_native24_only']
 proof=dict(epoch=time.time(),source_and_AUTH_AST_passed=True,prior_model_bank_USD_bytes_not_opened=True,model_source_producer=dict(path=model['local_path'],bytes=model['bytes'],SHA=model['SHA'],new_updates=78,Adam648360=True,LR=.00011390625000000003),all_original_W35_behavioral_loop_and_native24_retained=True,CPU_self_identity_exact_inverse_bytes=True,known104_active_readonly_supported=True,project_only_cloned_direct_loader_helpers_actual_prior_native24_passed=True,finite_GPU_worker_not_yet_started=True,source_only_not_crosshost_pass_or_graduation=True)
 (B/'NEW86_W35_SOURCE_AST_AND_LITERAL_INPUT_BINDINGS_ACTUAL.json').write_text(json.dumps(proof,indent=2)+'\n')
 index=dict(status='FROZEN_UNUSED_SOURCE_ONLY_NEW86_W35_DETACHED_REGRESSION',epoch=time.time(),entry_filename=entryname,entry_SHA=H((B/entryname).read_bytes()),manifest_SHA=H(mf.read_bytes()),input_file_count=len(rows),executable_source_SHAs={n:H((B/n).read_bytes()) for n in selected},clone_receipt_SHA=H(clone.read_bytes()),actual_clone_CUDA_SDK_receipt_SHA=H(normal.read_bytes()),maximum_control_seconds_after_stdin=600,CPU_wait120_and_cleanup30=True,detached_worker_max1680_and_supervisor_wait1800_cleanup45=True,no_training_GO_optimizer_or_C_write=True,actual_GPU_native24_fullcoverage_and_original_criteria_review_pending=True,source_proof=proof,Git='root ordinary pending; no actual trial/tag by child')
 out=B/'FROZEN_NEW86_W35_FROZEN_PROFILE_SOURCE_INDEX_V1.json';out.write_text(json.dumps(index,indent=2)+'\n');print(json.dumps(dict(entry=str(B/entryname),entry_SHA=index['entry_SHA'],index=str(out),index_SHA=H(out.read_bytes()),manifest_SHA=index['manifest_SHA'],inputs=len(rows),source_only=True)))
if __name__=='__main__':main()

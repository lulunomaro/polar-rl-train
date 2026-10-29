from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent;L=B.parent;OLD=L/'E3_97_SOURCE210_FROZEN_RECIPE_DOMAIN_ADMISSION_SOURCE_20261029_V1'
OLDJOB='/mnt/mod4_linux_durable_20261013/MOD4_E3_ADAPTED97_RECIPE_DOMAIN_20261029v1/e3';JOB=OLDJOB.replace('20261029v1','20261029v2')
ENTRY='install_E3_source210_frozen_recipe_metadata_detach_UNUSED_once_v2_canonicalWorkerPython.py';REMOTE='remote_E3_source210_verify_metadata_CPU_and_detach_v2.py';INDEX='FROZEN_E3_97_SOURCE210_RECIPE_DOMAIN_SOURCE_INDEX_V2.json'
RENAMES={'install_E3_source210_frozen_recipe_metadata_detach_UNUSED_once_v1.py':ENTRY,'remote_E3_source210_verify_metadata_CPU_and_detach_v1.py':REMOTE,'E3_source210_actual_receipts_readonly_CODE_v1.py':'E3_source210_actual_receipts_readonly_CODE_v2.py','run_E3_source210_readonly_v1.py':'run_E3_source210_readonly_v2.py','read_E3_source210_FIRST_native24_recipe_queue_UNUSED_once_v1.py':'read_E3_source210_FIRST_native24_recipe_queue_UNUSED_once_v2.py','collect_E3_source210_TERMINAL_recipe_fulltext_UNUSED_once_v1.py':'collect_E3_source210_TERMINAL_recipe_fulltext_UNUSED_once_v2.py'}
CONVERTER="""def worker_python_from_control_alias(control_python):
 alias='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
 canonical='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python3.12'
 assert control_python in (alias,canonical),'Unexpected original210 control Python alias'
 return canonical

"""
def H(b):return hashlib.sha256(b).hexdigest()
def write(n,b):
 with (B/n).open('xb') as f:f.write(b)
def put(n,v):write(n,(json.dumps(v,indent=2)+'\n').encode())
def main():
 (B/'reports').mkdir(exist_ok=True);old=json.loads((OLD/'FROZEN_E3_97_SOURCE210_RECIPE_DOMAIN_SOURCE_INDEX_V1.json').read_bytes());m=json.loads((OLD/'E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes());names={Path(r['local_path']).name for r in m['files'] if Path(r['local_path']).parent==OLD}
 names.update(RENAMES);names.update(('AUTH72_CURRENT_KNOWN_OWNER_READONLY_CODE_v1.py','PRE210_UNUSED_MOUNT_LIGHT_RESOURCE_CODE_v1.py'));records=[]
 for n in sorted(names):
  raw=(OLD/n).read_bytes();name=RENAMES.get(n,n);text=raw.decode();rebase=[]
  for a,b in [(OLDJOB,JOB),('FROZEN_E3_97_SOURCE210_RECIPE_DOMAIN_SOURCE_INDEX_V1.json',INDEX)]+list(RENAMES.items()):
   if a in text:rebase.append((a,b,text.count(a)));text=text.replace(a,b)
  rebased=text;inverse=rebased
  for a,b,count in reversed(rebase):inverse=inverse.replace(b,a)
  assert inverse.encode()==raw,(n,'namespace inverse')
  if n=='install_E3_source210_frozen_recipe_metadata_detach_UNUSED_once_v1.py':
   needle='def main():\n';assert text.count(needle)==1;text=text.replace(needle,CONVERTER+needle)
   oldcall='dict(job=JOB,python=route.PY,authority=authority';newcall='dict(job=JOB,python=worker_python_from_control_alias(route.PY),control_route_PY=route.PY,authority=authority';assert text.count(oldcall)==1;text=text.replace(oldcall,newcall)
   needle='client=route.connect();pre=';added="put('E3_V2_CONTROL_ROUTE_AND_SUBMITTED_WORKER_PYTHON_ACTUAL.json',dict(epoch=time.time(),control_route_PY=route.PY,submitted_workerpython=worker_python_from_control_alias(route.PY),target_JOB_literal=JOB,control_transport_uses_original_route_PY=True,strict_remote_predicate_unchanged=True,no_secret=True))\n  "+needle;assert text.count(needle)==1;text=text.replace(needle,added)
   inv=text.replace(added,needle).replace(newcall,oldcall).replace(CONVERTER,'');assert inv==rebased
  if n=='remote_E3_source210_verify_metadata_CPU_and_detach_v1.py':
   needle="assert v['python']=='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python3.12'"
   extra="\n binding=dict(control_route_PY=v['control_route_PY'],submitted_workerpython=v['python'],JOB=str(JOB),actual_JOB_resolve=str(J.resolve()),actual_workerpython_resolve=str(Path(v['python']).resolve()),no_secret=True);put(J,'E3_V2_TARGET_PUBLIC_PYTHON_JOB_BINDING_METADATA_ACTUAL.json',binding)"
   assert text.count(needle)==1;text=text.replace(needle,needle+extra)
   needle="return dict(passed_source_CPU_and_detached_only=";assert text.count(needle)==1;text=text.replace(needle,"return dict(public_interpreter_job_binding=binding,passed_source_CPU_and_detached_only=")
   oldtail="if __name__=='__main__':print(json.dumps(main(v)))";newtail="""if __name__=='__main__':
 try:print(json.dumps(main(v)))
 except BaseException:
  print(json.dumps(dict(original_remote_error_public_binding=dict(control_route_PY=v.get('control_route_PY'),submitted_workerpython=v.get('python'),submitted_JOB=v.get('job'),expected_JOB=str(JOB),actual_JOB_resolve=str(Path(v['job']).resolve()),actual_workerpython_resolve=str(Path(v['python']).resolve())),no_secret=True)),file=sys.stderr)
  raise""";assert text.count(oldtail)==1;text=text.replace(oldtail,newtail)
   inv=text.replace(newtail,oldtail).replace('return dict(public_interpreter_job_binding=binding,passed_source_CPU_and_detached_only=',needle).replace(extra,'');assert inv==rebased
  if n.endswith('.py'):ast.parse(text)
  write(name,text.encode());records.append(dict(old=str(OLD/n),old_SHA=H(raw),new=name,new_SHA=H(text.encode()),namespace_replacements=[dict(old=a,new=b,count=c) for a,b,c in rebase],namespace_inverse_exact=True,additional_conversion_and_public_metadata_inverse_exact=n in RENAMES and n in (list(RENAMES)[0],list(RENAMES)[1])))
 rows=[]
 for r in m['files']:
  x=dict(r)
  if Path(r['local_path']).parent==OLD:
   name=RENAMES.get(Path(r['local_path']).name,Path(r['local_path']).name);raw=(B/name).read_bytes();x.update(local_path=str(B/name),bytes=len(raw),SHA=H(raw))
  rows.append(x)
 m.update(files=rows,target_root=JOB,source_version='V2_control_route_alias_worker_canonical_metadata_repair',V1_upload_loop_completed_but_target_fullSHA_not_reached=True)
 write('E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json',(json.dumps(m,indent=2)+'\n').encode())
 failure=OLD/'reports/E3_SOURCE210_INSTALL_ORIGINAL_ERROR_1793245488212667500.json';raw=failure.read_bytes();put('V1_ACTUAL_ALIAS_FAILURE_AND_PARTIAL_UPLOAD_RETAINED_REFERENCE.json',dict(original_failure_path=str(failure),original_failure_SHA=H(raw),V1_target_root=OLDJOB,V1_uploaded444=True,V1_target_fullSHA_verification_passed=False,CPU_App_model_GPU_not_started=True,strict_remote_worker_python_predicate_rejected_control_alias=True,old_once_source_partial_unchanged=True))
 prior=OLD/'reports/E3_SOURCE210_FRESH_ORIGINAL_PHASE_CPU_TARGET_AST_AND_READERS_ACTUAL.json';write('PRIOR30_PHASE_AST_READER_CPU_PROOF_UNCHANGED.json',prior.read_bytes())
 put('V2_NAMESPACE_CANONICAL_WORKER_SOURCE_EXACT_DERIVATION_PROOF.json',dict(passed=True,records=records,worker_model_physics_metrics_queue_unchanged=True,control_SSH_python_unchanged=True,remote_strict_canonical_predicate_unchanged=True,no_PT_raw_binary_SDK_GPU_remote_call=True))
 put('V2_SELECTED_SOURCE_PENDING_FINAL_FREEZE.json',dict(entry=ENTRY,remote=REMOTE,index=INDEX,target_root=JOB,manifest_SHA=H((B/'E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes()),first_reader=RENAMES[old['first_reader']],terminal_reader=RENAMES[old['terminal_reader']],model_SHA=old['model_SHA']))
 print(json.dumps(dict(passed=True,source_only=True,files=len(rows),target=JOB,entry=ENTRY)))
if __name__=='__main__':main()

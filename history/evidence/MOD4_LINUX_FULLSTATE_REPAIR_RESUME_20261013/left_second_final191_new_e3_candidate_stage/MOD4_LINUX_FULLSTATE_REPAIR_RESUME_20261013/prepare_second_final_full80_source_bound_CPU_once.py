"""New source-only frozen full80 scope; no transport or GPU in preparation."""
from pathlib import Path
import json,time,hashlib,shutil,zipfile,ast
D=Path(__file__).resolve().parent;W=D.parent;OLD=W/'MOD4_3060_LEFT_REPAIR_FULL80_20261014';S=W/'MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014'
N=W/'MOD4_3060_LEFT_SECOND_FULL80_20261014';OLD_SHA='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971';SHA='e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c'
def H(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 final=json.loads((S/'reports/LEFT_SECOND_OWN_FORMAL_FINAL_CLOSEOUT_CPU_VERIFIED.json').read_bytes());assert final['passed'] and final['own_final']['sha256']==SHA and final['actual_parent_guardian_child_exit'] and final['two_actual_fcntl_free'] and final['canonical_idle']
 cpu=json.loads((S/'reports/LEFT_SECOND_OWN_POSITIVE_WEIGHT_LOCAL_CPU_VERIFIED_1791963221095120000.json').read_bytes());assert cpu['passed'] and cpu['saved_state']['saved_updates']==191
 trace=json.loads((D/'reports/LEFT_SECOND_FORMAL_FINAL_FULLTRACE_CPU_ACTUAL_1791963246377865600.json').read_bytes());assert trace['code']==0 and json.loads(trace['stdout'])['passed']
 own=Path(cpu['own_local_checkpoint']['local_path']);assert H(own)==SHA
 assert not N.exists();N.mkdir();Q=N/'payload';R=N/'reports';R.mkdir()
 shutil.copytree(OLD/'payload',Q,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 legacy=Q/'source/model_32635_left_repair.pt';assert H(legacy)==OLD_SHA;shutil.copyfile(own,legacy);assert H(legacy)==SHA
 worker=Q/'paired_full80_parameter_bound_v2.py';original=worker.read_text();new=original.replace(OLD_SHA,SHA).replace('MOD4_3060_LEFT_REPAIR_FULL80_20261014','MOD4_3060_LEFT_SECOND_FULL80_20261014');assert new!=original;compile(new,str(worker),'exec');worker.write_text(new,encoding='utf8')
 # Only policy-source SHA and namespace string constants change; physical AST is identical.
 a=ast.parse(original);b=ast.parse(new)
 for node in ast.walk(b):
  if isinstance(node,ast.Constant) and node.value==SHA:node.value=OLD_SHA
  if isinstance(node,ast.Constant) and node.value=='MOD4_3060_LEFT_SECOND_FULL80_20261014':node.value='MOD4_3060_LEFT_REPAIR_FULL80_20261014'
 assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
 oldmanifest=json.loads((OLD/'payload/REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json').read_bytes());rows=[]
 for row in oldmanifest['file_rows']:
  p=Q/row['relative'];assert p.is_file();h=H(p)
  if p not in (worker,legacy):assert h==row['sha256'],row['relative']
  rows.append(dict(relative=row['relative'],bytes=p.stat().st_size,sha256=h))
 m=dict(protocol=oldmanifest['protocol'],actual_native120_admission=oldmanifest['actual_native120_admission'],only_new_firstphysics_readonly_initial_snapshot=True,physical_control_loop_AST_exact=True,actual_candidate_final_source_SHA=SHA,actual_final_updates=191,source_name_legacy_only_actual_model32825_disclosed=True,previous_manifest_SHA=H(OLD/'payload/REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'),new_scope_policy_only_frozen_no_PPO=True,actual_fullstate_final_review=dict(path=str(S/'reports/LEFT_SECOND_OWN_FORMAL_FINAL_CLOSEOUT_CPU_VERIFIED.json'),sha256=H(S/'reports/LEFT_SECOND_OWN_FORMAL_FINAL_CLOSEOUT_CPU_VERIFIED.json')),file_rows=rows)
 mp=Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json';mp.write_text(json.dumps(m,indent=2),encoding='utf8')
 z=N/'FULL80_FROZEN1500_SOURCE_V1.zip'
 with zipfile.ZipFile(z,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as out:
  for p in sorted(Q.rglob('*')):
   if p.is_file():out.write(p,p.relative_to(Q).as_posix())
 prep=dict(epoch=time.time(),CPU_prepared=True,source_SHA=SHA,source_own_final=str(own),whole20k_full107finite=True,actor9changed_Adam3820_actual=True,final_actual_saved_updates=191,actual_training_fulltrace_review_receipt=str(D/'reports/LEFT_SECOND_FORMAL_FINAL_FULLTRACE_CPU_ACTUAL_1791963246377865600.json'),worker=dict(path=str(worker),sha256=H(worker)),runtime=dict(path=str(Q/'full80_runtime_native_v1.py'),sha256=H(Q/'full80_runtime_native_v1.py')),manifest=dict(path=str(mp),sha256=H(mp)),package=dict(path=str(z),bytes=z.stat().st_size,sha256=H(z)),original_full80_backend_native_and_physical_scope_SHA_reused=True,only_new_frozen_policy_source_and_namespace=True,full1500_GPU_NOT_launched=True,qualified50=False)
 (R/'FULL80_NATIVE_CPU_PORT_PREPARED_ACTUAL.json').write_text(json.dumps(prep,indent=2),encoding='utf8')
 replacements=[('MOD4_3060_LEFT_REPAIR_FULL80_20261014','MOD4_3060_LEFT_SECOND_FULL80_20261014'),('native3060_left_repair_final_full80_frozen1500_v1','native3060_left_second_final_full80_frozen1500_v1'),('MOD4_LeftRepairFinalFull80_20261014_Frozen1500_v1','MOD4_LeftSecondFinalFull80_20261014_Frozen1500_v1'),(OLD_SHA,SHA)]
 for name in ('deploy_left_repair_final_full80_unique_once.py','collect_left_full80_bounded_transport_actual.py','review_full80_full1500_CPU_actual.py','review_full80_original_route_prefix_CPU_actual.py'):
  src=(OLD/name).read_text()
  for a,b in replacements:src=src.replace(a,b)
  compile(src,str(N/name),'exec');(N/name).write_text(src,encoding='utf8')
 direct=(OLD/'review_left_full80_direct_original_prefix_actual.py').read_text().replace("MOD4_3060_FULL80_FROZEN_CURRENT_20261014/reports/","MOD4_3060_LEFT_REPAIR_FULL80_20261014/reports/")
 (N/'review_second_full80_direct_best2b_prefix_actual.py').write_text(direct,encoding='utf8');compile(direct,'directbest2b','exec')
 (R/'SECOND_FULL80_SOURCE_ONLY_NAMESPACE_CPU_PREPARED_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),source_actual_final_SHA=SHA,new_namespace=str(N),all_485_source_rows_checked=len(rows),source_and_namespace_AST_only_change=True,reused_original_native120_not_replayed=True,other_runtime_geometry_physics_and_installedSDK_exact=True,original_best2b_unchanged=True,new_full80_unused_not_yet_GPU=True,package=prep['package']),indent=2),encoding='utf8')
 print(json.dumps(dict(new_root=str(N),package=prep['package'],prepared=True,GPU_launched=False)))
if __name__=='__main__':main()

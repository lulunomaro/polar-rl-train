"""CPU-only new source/namespace preparation. No transport, SDK or GPU imports."""
from pathlib import Path
import ast, hashlib, json, shutil, time, zipfile
D=Path(__file__).resolve().parent;W=D.parent;OLD=W/'MOD4_3060_LEFT_REPAIR_RETENTION_20261014';Q=D/'payload';R=D/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
NEW='MOD4_3060_LEFT_SECOND_RETENTION_20261014';SHA='e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c'
def save(p,v):
 assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2),encoding='utf8')
def main():
 assert not Q.exists();R.mkdir(parents=True,exist_ok=True)
 S=W/'MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014'
 final=json.loads((S/'reports/LEFT_SECOND_OWN_FORMAL_FINAL_CLOSEOUT_CPU_VERIFIED.json').read_bytes())
 assert final['passed'] and final['actual_parent_guardian_child_exit'] and final['two_actual_fcntl_free'] and final['canonical_idle']
 source=json.loads((S/'reports/LEFT_SECOND_OWN_POSITIVE_SAVED_ACTUAL_1791963199228502100.json').read_bytes())['two_host_byteSHA_exact'][0]
 path=Path(source['local_path']);assert H(path)==SHA and path.stat().st_size==19044152
 m=json.loads((OLD/'payload/RETENTION_CPU_MANIFEST_V8.json').read_bytes());Q.mkdir()
 for row in m['package_files_v8']:
  p=OLD/'payload'/row['relative'];assert H(p)==row['sha256'];target=Q/row['relative'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 shutil.copytree(OLD/'payload/cpu_contracts',Q/'cpu_contracts',ignore=shutil.ignore_patterns('__pycache__'))
 worker=Q/'retention_worker_v8.py';old=worker.read_text(encoding='utf8');assert old.count("lease['namespace']=='MOD4_3060_LEFT_REPAIR_RETENTION_20261014'")==1
 worker.write_text(old.replace("lease['namespace']=='MOD4_3060_LEFT_REPAIR_RETENTION_20261014'","lease['namespace']=='"+NEW+"'"),encoding='utf8')
 for row in m['package_files_v8']:
  row.update(bytes=(Q/row['relative']).stat().st_size,sha256=H(Q/row['relative']))
 m['sources']['left_second_e3']=dict(local_path=str(path),remote_path='D:/MOD4_async_eval/'+NEW+'/payload/source/model_32825_left_second.pt',sha256=SHA,bytes=19044152)
 m['second_retention_CPU_prepared']=dict(namespace=NEW,source_SHA=SHA,baseline_source_SHA=m['sources']['left_repair2b']['sha256'],only_namespace_source_and_unusedcase_identity_changed=True,original_all_physics_mainloop_and_contracts_exact=True,new_native_requested=False,reuse_native_120_contract=True,approved_GPU=False,dispatch_executed=False,actual_future_results_pending=True)
 save(Q/'RETENTION_CPU_MANIFEST_V8.json',m);(Q/'source').mkdir();shutil.copy2(path,Q/'source/model_32825_left_second.pt')
 for kind in ('flat','spin','world'):
  native=OLD/'reports'/f'retention_baseline1aa_{kind}_120_v8_FULL_CPU_REVIEW.json';v=json.loads(native.read_bytes())['result'];assert v['kind']==kind and v['steps']==120 and v['data']['complete_data_contract']
  p=sorted((OLD/'reports').glob(f'retention_repair2b_{kind}_1500_v8_CURRENT_ACTUAL_*.json'))[-1];collection=json.loads(p.read_bytes())
  rows=collection['collected_files'];assert all(row['two_host_byteSHA_exact'] for row in rows)
  probe=next(row for row in rows if row['relative'].endswith(f'attempts/retention_repair2b_{kind}_1500_v8/output/probe.json'))
  attempt=str(Path(probe['local_path']).parent.parent)
  boundary=OLD/'reports'/f'retention_repair2b_{kind}_1500_v8_INDEPENDENT_BOUNDARY.json';b=json.loads(boundary.read_bytes());assert b['actual_parent_absent'] and b['actual_child_absent'] and b['shared_OS_lock_free']
  save(R/(kind+'_BASELINE_AND_REUSED_NATIVE_INPUTS_CPU_PREPARED.json'),dict(kind=kind,native_proof=str(native),native_proof_SHA=H(native),baseline_attempt=attempt,baseline_boundary=str(boundary),baseline_boundary_SHA=H(boundary),baseline_collection=str(p),baseline_collection_SHA=H(p),baseline_checkpoint_SHA='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971',new_checkpoint_SHA=SHA,prepared_only=True))
 dispatcher=(OLD/'dispatch_new_retention_v8_CPU_schema_reviewed_case_actual.py').read_text(encoding='utf8').replace('MOD4_3060_LEFT_REPAIR_RETENTION_20261014',NEW)
 start=dispatcher.index('SOURCES={');end=dispatcher.index('\nH=lambda',start)
 dispatcher=dispatcher[:start]+"SOURCES={'second_e3':(ROOT+'/payload/source/model_32825_left_second.pt',"+repr(SHA)+")}\n"+dispatcher[end:]
 dispatcher=dispatcher.replace("p.add_argument('--native-proof');a=p.parse_args()","p.add_argument('--native-proof');p.add_argument('--execute-root-dispatch',action='store_true');a=p.parse_args();assert a.execute_root_dispatch,'Explicit root execution flag required';assert a.steps==1500")
 dispatcher=dispatcher.replace(" assert json.loads((R/'PLANE_METADATA_V7_INDEPENDENT_ACTUAL_CPU_REVIEW.json').read_bytes())['actual_new_metadata_query_consistency_review']\n assert json.loads((R/'RETENTION_V8_REPRESENTED_REFERENCE_SYNTHETIC_CPU_PASSED.json').read_bytes())['passed_CPU_synthetic_only']"," assert json.loads((R/'SECOND_RETENTION_CPU_PREPARED_ACTUAL.json').read_bytes())['CPU_prepared_no_remote_or_GPU']")
 (D/'dispatch_new_second_retention_case_actual.py').write_text(dispatcher,encoding='utf8')
 collector=(OLD/'collect_retention_V8_actual_boundary.py').read_text(encoding='utf8').replace('MOD4_3060_LEFT_REPAIR_RETENTION_20261014',NEW)
 collector=collector.replace("a.add_argument('--case',required=True);a=a.parse_args();","a.add_argument('--case',required=True);a.add_argument('--execute-root-readonly-collection',action='store_true');a=a.parse_args();assert a.execute_root_readonly_collection,'Explicit root readonly collection flag required';")
 (D/'collect_second_retention_actual_boundary.py').write_text(collector,encoding='utf8')
 reviewer=(OLD/'review_retention_full_actual_CPU_v8.py').read_text(encoding='utf8')
 reviewer=reviewer.replace("assert baseline['checkpoint_sha256']=='1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06'","assert baseline['checkpoint_sha256']=='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971'")
 reviewer=reviewer.replace("assert result['checkpoint_sha256']=='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971'","assert result['checkpoint_sha256']=='"+SHA+"'")
 reviewer=reviewer.replace('LEFT_REPAIR_RETENTION_V8_REPRESENTED_REFERENCE_ACTUAL_CPU_REVIEW','LEFT_SECOND_RETENTION_V8_REPRESENTED_REFERENCE_ACTUAL_CPU_REVIEW')
 (D/'review_second_retention_full_actual_CPU.py').write_text(reviewer,encoding='utf8')
 for kind in ('flat','spin','world'):
  for name in (f'retention_{kind}_native_v8.py','retention_native_witness_v8.py','retention_plane_reference_v8.py','retention_parent_v8.py'):
   assert (Q/name).read_bytes()==(OLD/'payload'/name).read_bytes()
 assert ast.dump(ast.parse(worker.read_text().replace(NEW,'MOD4_3060_LEFT_REPAIR_RETENTION_20261014')),include_attributes=False)==ast.dump(ast.parse((OLD/'payload/retention_worker_v8.py').read_text()),include_attributes=False)
 for p in list(D.glob('*.py'))+list(Q.rglob('*.py')):compile(p.read_text(encoding='utf8'),str(p),'exec')
 z=D/'SECOND_RETENTION_V8_SOURCE_PAYLOAD_CPU_PREPARED.zip';assert not z.exists()
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as out:
  for row in m['package_files_v8']:out.write(Q/row['relative'],row['relative'])
  out.write(Q/'RETENTION_CPU_MANIFEST_V8.json','RETENTION_CPU_MANIFEST_V8.json');out.write(Q/'source/model_32825_left_second.pt','source/model_32825_left_second.pt')
 save(R/'SECOND_RETENTION_CPU_PREPARED_ACTUAL.json',dict(epoch=time.time(),CPU_prepared_no_remote_or_GPU=True,original_physics_witness_three_main_bytes_exact=True,worker_only_namespace_AST_exact=True,reused_native120_all_three_actual_data_pass=True,source_complete_file_SHA=SHA,source_bytes=19044152,final_closeout_report=str(S/'reports/LEFT_SECOND_OWN_FORMAL_FINAL_CLOSEOUT_CPU_VERIFIED.json'),final_closeout_SHA=H(S/'reports/LEFT_SECOND_OWN_FORMAL_FINAL_CLOSEOUT_CPU_VERIFIED.json'),package=dict(path=str(z),bytes=z.stat().st_size,sha256=H(z)),manifest_SHA=H(Q/'RETENTION_CPU_MANIFEST_V8.json'),newsource_or_case_results_pending=True,no_PPO_budgetwrite_or_qualification=True,Git_pending_root_stage_archive=True))
 print(json.dumps(dict(prepared=str(R/'SECOND_RETENTION_CPU_PREPARED_ACTUAL.json'),package=str(z),no_remote_no_GPU=True)))
if __name__=='__main__':main()

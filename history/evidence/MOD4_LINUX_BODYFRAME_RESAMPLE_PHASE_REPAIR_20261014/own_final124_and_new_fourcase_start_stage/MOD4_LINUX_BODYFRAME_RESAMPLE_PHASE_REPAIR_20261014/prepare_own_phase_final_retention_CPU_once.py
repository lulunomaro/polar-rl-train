"""New own-final three candidate scopes; preserve all original V8 physical code."""
from pathlib import Path
import ast, hashlib, json, shutil, zipfile, time, traceback
D=Path(__file__).resolve().parent;W=D.parent
OLD=W/'MOD4_3060_BODYFRAME_FIRST_RETENTION_20261014'
NATIVE=W/'MOD4_3060_LEFT_REPAIR_RETENTION_20261014'
NEW=W/'MOD4_3060_BODYFRAME_PHASE_FINAL_RETENTION_20261015'
SHA='cfcefb1c46b33d6028bf6663921fac12a58a5abfdba782e1480a18ac84de541b'
BASE='f5166509d297814e3c3fe4f457ae064d9b02a8bd62702914759dc430f20d2139'
OLDER='e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c'
SOURCE_ID='bodyframe_phase_final_cf'
PREFIX='BODYFRAME_PHASE_FINAL_RETENTION'
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):
 assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2),encoding='utf8')
def write(p,s):
 assert not p.exists(),str(p);compile(s,str(p),'exec');p.write_text(s,encoding='utf8')
def replacements(s):
 return s.replace(OLD.name,NEW.name).replace(BASE,SHA).replace('bodyframe_first_f516',SOURCE_ID).replace('model_32830_bodyframe_first.pt','model_32998_bodyframe_phase_final.pt').replace('BODYFRAME_FIRST_RETENTION',PREFIX).replace('f516_retention_source_CPU_validator_v1','phase_final_retention_source_CPU_validator_v1')
def main():
 proof=D/'reports/PHASE_REPAIR_OWN_FINAL_FULLTRACE_LOCAL_CPU_VERIFIED.json';final=json.loads(proof.read_bytes());assert final['passed'] and final['two_locks_free'] and final['actual_parent_guardian_child_out']
 source=Path(final['own_checkpoint']['path']);assert h(source)==final['own_checkpoint']['sha256']==SHA
 prior=OLD/'reports/BODYFRAME_FIRST_F516_THREE_RETENTION_PAIRS_COMPLETE_ACTUAL_CPU_REVIEW.json'
 oldreview=json.loads(prior.read_bytes());assert oldreview['passed'] and oldreview['all_three_inherited_full1500_complete'] and not oldreview['pending']
 assert not NEW.exists();Q=NEW/'payload';R=NEW/'reports';Q.mkdir(parents=True);R.mkdir()
 m=json.loads((OLD/'payload/RETENTION_CPU_MANIFEST_V8.json').read_bytes())
 for row in m['package_files_v8']:
  p=OLD/'payload'/row['relative'];assert h(p)==row['sha256'] and p.stat().st_size==row['bytes'];dest=Q/row['relative'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 shutil.copytree(OLD/'payload/cpu_contracts',Q/'cpu_contracts',ignore=shutil.ignore_patterns('__pycache__'))
 worker=Q/'retention_worker_v8.py';s=worker.read_text();worker.write_text(s.replace(OLD.name,NEW.name),encoding='utf8')
 assert ast.dump(ast.parse(worker.read_text().replace(NEW.name,OLD.name)),include_attributes=False)==ast.dump(ast.parse(s),include_attributes=False)
 oldval=Q/'f516_retention_source_CPU_validator_v1.py';newval=Q/'phase_final_retention_source_CPU_validator_v1.py';write(newval,oldval.read_text().replace(BASE,SHA))
 for row in m['package_files_v8']:
  if row['relative']==oldval.name:row['relative']=newval.name
  p=Q/row['relative'];row.update(bytes=p.stat().st_size,sha256=h(p))
 # The copied old validator remains an explicit historical file, excluded from this new bundle.
 m['sources'][SOURCE_ID]=dict(local_path=str(source),remote_path='D:/MOD4_async_eval/'+NEW.name+'/payload/source/model_32998_bodyframe_phase_final.pt',sha256=SHA,bytes=source.stat().st_size)
 m['phase_final_retention_CPU_prepared']=dict(namespace=NEW.name,source_SHA=SHA,baseline_source_SHA=BASE,core_and_owned_body_separate=True,original_physics_mainloop_and_contracts_exact=True,new_native_requested=False,reuse_native_120_contract=True,approved_GPU=False,dispatch_executed=False,actual_future_results_pending=True,wholefinal_CPU_closeout_SHA=h(proof))
 save(Q/'RETENTION_CPU_MANIFEST_V8.json',m);(Q/'source').mkdir();shutil.copy2(source,Q/'source/model_32998_bodyframe_phase_final.pt')
 for kind in ('flat','spin','world'):
  native=NATIVE/'reports'/f'retention_baseline1aa_{kind}_120_v8_FULL_CPU_REVIEW.json';v=json.loads(native.read_bytes())['result'];assert v['kind']==kind and v['steps']==120 and v['data']['complete_data_contract']
  case=f'retention_bodyframe_first_f516_{kind}_1500_v8';collection=max((OLD/'reports').glob(case+'_CURRENT_ACTUAL_*.json'),key=lambda p:p.stat().st_mtime_ns);rows=json.loads(collection.read_bytes())['collected_files'];assert all(row['two_host_byteSHA_exact'] for row in rows)
  probe=next(row for row in rows if row['relative'].endswith(f'attempts/{case}/output/probe.json'));attempt=str(Path(probe['local_path']).parent.parent)
  boundary=OLD/'reports'/(case+'_INDEPENDENT_BOUNDARY.json');bv=json.loads(boundary.read_bytes());assert bv['actual_parent_absent'] and bv['actual_child_absent'] and bv['shared_OS_lock_free']
  review=OLD/'reports'/(case+'_FULL_CPU_REVIEW.json');rv=json.loads(review.read_bytes())['result']['candidate'];assert rv['checkpoint_sha256']==BASE and rv['data']['complete_data_contract'] and rv['steps']==1500
  save(R/(kind+'_BASELINE_AND_REUSED_NATIVE_INPUTS_CPU_PREPARED.json'),dict(kind=kind,native_proof=str(native),native_proof_SHA=h(native),baseline_attempt=attempt,baseline_boundary=str(boundary),baseline_boundary_SHA=h(boundary),baseline_collection=str(collection),baseline_collection_SHA=h(collection),baseline_full_review=str(review),baseline_full_review_SHA=h(review),baseline_checkpoint_SHA=BASE,new_checkpoint_SHA=SHA,prepared_only=True))
 for name in ('transport_249_own_f516_retention.py','dispatch_new_bodyframe_retention_case_actual.py','collect_bodyframe_retention_actual_boundary.py','upload_bodyframe_retention_source_namespace_CPU_once.py','run_bodyframe_retention_fixed_three_candidate_batch_once.py'):
  s=replacements((OLD/name).read_text())
  if name.startswith('transport'):name='transport_249_own_phase_final_retention.py'
  if name.startswith('run_'):name='run_phase_final_retention_fixed_three_candidate_batch_once.py'
  s=s.replace('transport_249_own_f516_retention','transport_249_own_phase_final_retention')
  write(NEW/name,s)
 s=(OLD/'review_bodyframe_retention_full_actual_CPU.py').read_text()
 s=s.replace("baseline['checkpoint_sha256']=='"+OLDER+"'","baseline['checkpoint_sha256']=='"+BASE+"'").replace("result['checkpoint_sha256']=='"+BASE+"'","result['checkpoint_sha256']=='"+SHA+"'").replace('BODYFRAME_FIRST_RETENTION_V8','BODYFRAME_PHASE_FINAL_RETENTION_V8')
 write(NEW/'review_bodyframe_retention_full_actual_CPU.py',s)
 s=(OLD/'aggregate_bodyframe_retention_complete_actual_CPU.py').read_text()
 s=s.replace("BASE='"+OLDER+"';OWN='"+BASE+"'","BASE='"+BASE+"';OWN='"+SHA+"'")
 s=s.replace("PREVIOUS=W/'MOD4_3060_LEFT_SECOND_RETENTION_20261014'","PREVIOUS=W/'"+OLD.name+"'")
 s=s.replace('BODYFRAME_FIRST_F516_THREE_RETENTION','BODYFRAME_PHASE_FINAL_CF_THREE_RETENTION').replace('BODYFRAME_FIRST_RETENTION_FIXED',PREFIX+'_FIXED').replace("name=f'retention_bodyframe_first_f516_{kind}_1500_v8'","name=f'retention_"+SOURCE_ID+"_{kind}_1500_v8'").replace("f'retention_second_e3_{kind}_1500_v8'","f'retention_bodyframe_first_f516_{kind}_1500_v8'")
 write(NEW/'aggregate_phase_final_retention_complete_actual_CPU.py',s)
 for kind in ('flat','spin','world'):
  for name in ('retention_'+kind+'_native_v8.py','retention_native_witness_v8.py','retention_parent_v8.py','retention_plane_reference_v8.py'):
   assert (Q/name).read_bytes()==(OLD/'payload'/name).read_bytes()
 for p in list(NEW.glob('*.py'))+list(Q.rglob('*.py')):compile(p.read_text(),str(p),'exec')
 z=NEW/'BODYFRAME_PHASE_FINAL_RETENTION_V8_SOURCE_PAYLOAD_CPU_PREPARED.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as out:
  for row in m['package_files_v8']:out.write(Q/row['relative'],row['relative'])
  out.write(Q/'RETENTION_CPU_MANIFEST_V8.json','RETENTION_CPU_MANIFEST_V8.json');out.write(Q/'source/model_32998_bodyframe_phase_final.pt','source/model_32998_bodyframe_phase_final.pt')
 save(R/(PREFIX+'_CPU_PREPARED_ACTUAL.json'),dict(epoch=time.time(),CPU_prepared_no_remote_or_GPU=True,original_physics_witness_three_main_bytes_exact=True,worker_only_namespace_AST_exact=True,reused_native120_all_three_actual_data_pass=True,source_complete_file_SHA=SHA,source_bytes=source.stat().st_size,final_closeout_report=str(proof),final_closeout_SHA=h(proof),previous_f516_full_three_review_SHA=h(prior),package=dict(path=str(z),bytes=z.stat().st_size,sha256=h(z)),manifest_SHA=h(Q/'RETENTION_CPU_MANIFEST_V8.json'),newsource_or_case_results_pending=True,no_PPO_budgetwrite_or_qualification=True,Git_pending_root_stage_archive=True))
 print(json.dumps(dict(prepared=str(R/(PREFIX+'_CPU_PREPARED_ACTUAL.json')),package=str(z),no_remote_no_GPU=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('PHASE_RETENTION_CPU_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_SSH_GPU=True),indent=2),encoding='utf8');raise

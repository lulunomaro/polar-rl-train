"""Prepare only genuinely new f516 retained-skill cases, using completed e3 baselines."""
from pathlib import Path
import ast, hashlib, json, shutil, time, zipfile, traceback
D=Path(__file__).resolve().parent;W=D.parent;OLD=W/'MOD4_3060_LEFT_SECOND_RETENTION_20261014';NATIVE=W/'MOD4_3060_LEFT_REPAIR_RETENTION_20261014';E=W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014';B=W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014';R=D/'reports';Q=D/'payload'
NEW=D.name;OLDNAME=OLD.name;SHA='f5166509d297814e3c3fe4f457ae064d9b02a8bd62702914759dc430f20d2139';BASE='e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):
 assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2),encoding='utf8')
def newtext(name,text):
 p=D/name;assert not p.exists();compile(text,str(p),'exec');p.write_text(text,encoding='utf8')
def main():
 assert not Q.exists();R.mkdir(parents=True,exist_ok=True)
 final_path=B/'reports/BODYFRAME_OWN_FINAL_FULLTRACE_LOCAL_CPU_VERIFIED.json';final=json.loads(final_path.read_bytes());assert final['passed'] and final['whole_core']==dict(floating_finite=107,perenv=99,tensors=195,saved_envs=20000,original_scope_identities_consistent=True,CPU_logical_only_not_GPU_fullrestore=True)
 source=Path(final['own_checkpoint']['path']);assert H(source)==SHA==final['own_checkpoint']['sha256'] and source.stat().st_size==19894311
 prior_complete=json.loads((OLD/'reports/SECOND_E3_THREE_RETENTION_PAIRS_COMPLETE_ACTUAL_CPU_REVIEW.json').read_bytes());assert prior_complete['passed'] and prior_complete['all_three_inherited_full1500_complete'] and not prior_complete['pending']
 m=json.loads((OLD/'payload/RETENTION_CPU_MANIFEST_V8.json').read_bytes());Q.mkdir()
 for row in m['package_files_v8']:
  p=OLD/'payload'/row['relative'];assert H(p)==row['sha256'];target=Q/row['relative'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 shutil.copytree(OLD/'payload/cpu_contracts',Q/'cpu_contracts',ignore=shutil.ignore_patterns('__pycache__'))
 worker=Q/'retention_worker_v8.py';text=worker.read_text(encoding='utf8');assert text.count("lease['namespace']=='"+OLDNAME+"'")==1
 worker.write_text(text.replace("lease['namespace']=='"+OLDNAME+"'","lease['namespace']=='"+NEW+"'"),encoding='utf8')
 for row in m['package_files_v8']:row.update(bytes=(Q/row['relative']).stat().st_size,sha256=H(Q/row['relative']))
 validator=E/'payload/bodyframe_owned_CPU_state_validation_v1.py';shutil.copy2(validator,Q/validator.name)
 vtext='''"""CPU source admission; frozen evaluation does not restore training DR or BODY state."""
from pathlib import Path
import hashlib, torch
from bodyframe_owned_CPU_state_validation_v1 import KEY,validate
SOURCE_SHA="f5166509d297814e3c3fe4f457ae064d9b02a8bd62702914759dc430f20d2139"
def validate_path(path):
 p=Path(path);assert p.stat().st_size==19894311 and hashlib.sha256(p.read_bytes()).hexdigest()==SOURCE_SHA
 ck=torch.load(p,map_location='cpu',weights_only=False);validate(ck[KEY])
 assert ck['E1_WAVE50_BODYFRAME_OWN_GPU_SOURCE']['actual_GPU_fullrestore'] is True
 assert torch.equal(ck[KEY]['bound_episode'],ck['E1_terrain_state']['episode'])
 assert ck['E1_terrain_state']['num_envs']==20000 and len(ck['actor_state_dict'])==9
 assert ck['LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION']['profile']=='left_initial_joint_margin014_std1_v1'
 core={k:v for k,v in ck.items() if k not in (KEY,'E1_WAVE50_BODYFRAME_OWN_GPU_SOURCE')};values=[]
 def walk(x):
  if isinstance(x,torch.Tensor):values.append(x)
  elif isinstance(x,dict):
   for v in x.values():walk(v)
  elif isinstance(x,(list,tuple)):
   for v in x:walk(v)
 walk(core);assert len(values)==195 and sum(v.is_floating_point() for v in values)==107
 assert sum(v.ndim>0 and v.shape[0]==20000 for v in values)==99
 assert all(v.device.type=='cpu' and (not v.is_floating_point() or torch.isfinite(v).all().item()) for v in values)
 assert not torch.cuda.is_initialized()
 return dict(source_whole20k_195_107_99_CPU_verified=True,source_owned_body_state_independently_validated=True,legacy_counts_apply_to_core_only=True,source_SHA=SOURCE_SHA,source_bytes=p.stat().st_size,no_CUDA_or_trainingDR_resume=True)
'''
 (Q/'f516_retention_source_CPU_validator_v1.py').write_text(vtext,encoding='utf8')
 for name in (validator.name,'f516_retention_source_CPU_validator_v1.py'):
  m['package_files_v8'].append(dict(relative=name,bytes=(Q/name).stat().st_size,sha256=H(Q/name)))
 m['sources']['bodyframe_first_f516']=dict(local_path=str(source),remote_path='D:/MOD4_async_eval/'+NEW+'/payload/source/model_32830_bodyframe_first.pt',sha256=SHA,bytes=19894311)
 m['bodyframe_first_retention_CPU_prepared']=dict(namespace=NEW,source_SHA=SHA,baseline_source_SHA=BASE,core_and_owned_body_separate=True,only_namespace_source_and_unusedcase_identity_changed=True,original_all_physics_mainloop_and_contracts_exact=True,new_native_requested=False,reuse_native_120_contract=True,approved_GPU=False,dispatch_executed=False,actual_future_results_pending=True)
 save(Q/'RETENTION_CPU_MANIFEST_V8.json',m);(Q/'source').mkdir();shutil.copy2(source,Q/'source/model_32830_bodyframe_first.pt')
 for kind in ('flat','spin','world'):
  native=NATIVE/'reports'/f'retention_baseline1aa_{kind}_120_v8_FULL_CPU_REVIEW.json';v=json.loads(native.read_bytes())['result'];assert v['kind']==kind and v['steps']==120 and v['data']['complete_data_contract']
  case=f'retention_second_e3_{kind}_1500_v8';collection=sorted((OLD/'reports').glob(case+'_CURRENT_ACTUAL_*.json'))[-1];rows=json.loads(collection.read_bytes())['collected_files'];assert all(row['two_host_byteSHA_exact'] for row in rows)
  probe=next(row for row in rows if row['relative'].endswith(f'attempts/{case}/output/probe.json'));attempt=str(Path(probe['local_path']).parent.parent)
  boundary=OLD/'reports'/(case+'_INDEPENDENT_BOUNDARY.json');bv=json.loads(boundary.read_bytes());assert bv['actual_parent_absent'] and bv['actual_child_absent'] and bv['shared_OS_lock_free']
  review=OLD/'reports'/(case+'_FULL_CPU_REVIEW.json');rv=json.loads(review.read_bytes())['result']['candidate'];assert rv['checkpoint_sha256']==BASE and rv['data']['complete_data_contract'] and rv['steps']==1500
  save(R/(kind+'_BASELINE_AND_REUSED_NATIVE_INPUTS_CPU_PREPARED.json'),dict(kind=kind,native_proof=str(native),native_proof_SHA=H(native),baseline_attempt=attempt,baseline_boundary=str(boundary),baseline_boundary_SHA=H(boundary),baseline_collection=str(collection),baseline_collection_SHA=H(collection),baseline_full_review=str(review),baseline_full_review_SHA=H(review),baseline_checkpoint_SHA=BASE,new_checkpoint_SHA=SHA,prepared_only=True))
 transport='''from pathlib import Path
import sys
W=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'))
import transport_249_bodyframe_current_terminal_role_v3 as base
PY=base.PY;ROOT='D:/MOD4_async_eval/MOD4_3060_BODYFRAME_FIRST_RETENTION_20261014'
connect=base.connect;close=base.close;py=base.py;ps=base.ps
def guard_code():
 base.ROOT=ROOT
 return base.guard_code()
'''
 newtext('transport_249_own_f516_retention.py',transport)
 for name in ('dispatch_new_second_retention_case_actual.py','collect_second_retention_actual_boundary.py','run_second_retention_fixed_three_candidate_batch_once.py','upload_second_retention_source_namespace_CPU_once.py'):
  s=(OLD/name).read_text(encoding='utf8').replace(OLDNAME,NEW).replace('second_e3','bodyframe_first_f516').replace('model_32825_left_second.pt','model_32830_bodyframe_first.pt').replace(BASE,SHA).replace('SECOND_RETENTION','BODYFRAME_FIRST_RETENTION')
  s=s.replace("sys.path.insert(0,str(W/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014'))","sys.path.insert(0,str(D))").replace('import transport_249_only as t','import transport_249_own_f516_retention as t')
  if name.startswith('upload'):
   start=s.index("source=P/'source/model_32830_bodyframe_first.pt'");end=s.index('result=dict(',start)
   s=s[:start]+"import sys\nsys.path.insert(0,str(P))\nfrom f516_retention_source_CPU_validator_v1 import validate_path\nsource=P/'source/model_32830_bodyframe_first.pt';owned=validate_path(source)\n"+s[end:]
   s=s.replace('source_whole20k_195_107_99_CPU_verified=True,','source_whole20k_195_107_99_CPU_verified=True,source_owned_body_state_independently_validated=True,legacy_counts_apply_to_core_only=True,')
  if name.startswith('dispatch'):
   anchor="ck=torch.load(CHECKPOINT,map_location='cpu',weights_only=False);assert ck['E1_terrain_state']['num_envs']==20000 and not torch.cuda.is_initialized()"
   assert s.count(anchor)==1;s=s.replace(anchor,"import sys\nsys.path.insert(0,str(P))\nfrom f516_retention_source_CPU_validator_v1 import validate_path\nowned=validate_path(CHECKPOINT)")
   s=s.replace('targetCPU_source_and_SDK_exact=True,no_GPU=True','targetCPU_source_and_SDK_exact=True,owned_body_CPU_validated=True,no_GPU=True')
  newtext(name.replace('second_retention','bodyframe_retention'),s.replace('second_retention','bodyframe_retention'))
 reviewer=(OLD/'review_second_retention_full_actual_CPU.py').read_text(encoding='utf8').replace("baseline['checkpoint_sha256']=='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971'","baseline['checkpoint_sha256']=='"+BASE+"'").replace("result['checkpoint_sha256']=='"+BASE+"'","result['checkpoint_sha256']=='"+SHA+"'").replace('LEFT_SECOND_RETENTION_V8','BODYFRAME_FIRST_RETENTION_V8')
 newtext('review_bodyframe_retention_full_actual_CPU.py',reviewer)
 agg=(OLD/'aggregate_second_retention_complete_actual_CPU.py').read_text(encoding='utf8')
 agg=agg.replace("BASE='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971';OWN='"+BASE+"'","BASE='"+BASE+"';OWN='"+SHA+"'")
 agg=agg.replace("OLD=W/'MOD4_3060_LEFT_REPAIR_RETENTION_20261014'","OLD=W/'MOD4_3060_LEFT_REPAIR_RETENTION_20261014';PREVIOUS=W/'MOD4_3060_LEFT_SECOND_RETENTION_20261014'")
 agg=agg.replace('SECOND_E3_THREE_RETENTION','BODYFRAME_FIRST_F516_THREE_RETENTION').replace('SECOND_RETENTION_FIXED','BODYFRAME_FIRST_RETENTION_FIXED').replace("name=f'retention_second_e3_{kind}_1500_v8'","name=f'retention_bodyframe_first_f516_{kind}_1500_v8'")
 agg=agg.replace("a.D=OLD;cases['baseline_'+kind]=a.actual_case_provenance(OLD/'reports',f'retention_repair2b_{kind}_1500_v8',b)","a.D=PREVIOUS;cases['baseline_'+kind]=a.actual_case_provenance(PREVIOUS/'reports',f'retention_second_e3_{kind}_1500_v8',b)\n  a.D=OLD")
 newtext('aggregate_bodyframe_retention_complete_actual_CPU.py',agg)
 for kind in ('flat','spin','world'):
  for name in (f'retention_{kind}_native_v8.py','retention_native_witness_v8.py','retention_plane_reference_v8.py','retention_parent_v8.py'):
   assert (Q/name).read_bytes()==(OLD/'payload'/name).read_bytes()
 assert ast.dump(ast.parse(worker.read_text().replace(NEW,OLDNAME)),include_attributes=False)==ast.dump(ast.parse((OLD/'payload/retention_worker_v8.py').read_text()),include_attributes=False)
 for p in list(D.glob('*.py'))+list(Q.rglob('*.py')):compile(p.read_text(encoding='utf8'),str(p),'exec')
 z=D/'BODYFRAME_FIRST_RETENTION_V8_SOURCE_PAYLOAD_CPU_PREPARED.zip';assert not z.exists()
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as out:
  for row in m['package_files_v8']:out.write(Q/row['relative'],row['relative'])
  out.write(Q/'RETENTION_CPU_MANIFEST_V8.json','RETENTION_CPU_MANIFEST_V8.json');out.write(Q/'source/model_32830_bodyframe_first.pt','source/model_32830_bodyframe_first.pt')
 save(R/'BODYFRAME_FIRST_RETENTION_CPU_PREPARED_ACTUAL.json',dict(epoch=time.time(),CPU_prepared_no_remote_or_GPU=True,original_physics_witness_three_main_bytes_exact=True,worker_only_namespace_AST_exact=True,reused_native120_all_three_actual_data_pass=True,source_complete_file_SHA=SHA,source_bytes=19894311,final_closeout_report=str(final_path),final_closeout_SHA=H(final_path),previous_e3_full_three_review_SHA=H(OLD/'reports/SECOND_E3_THREE_RETENTION_PAIRS_COMPLETE_ACTUAL_CPU_REVIEW.json'),package=dict(path=str(z),bytes=z.stat().st_size,sha256=H(z)),manifest_SHA=H(Q/'RETENTION_CPU_MANIFEST_V8.json'),newsource_or_case_results_pending=True,no_PPO_budgetwrite_or_qualification=True,Git_pending_root_stage_archive=True,operational_reader_error_preserved='Initial rg quoted Windows wildcards returned invalid path; independent -g directory search only, no mutation or GPU')))
 print(json.dumps(dict(prepared=str(R/'BODYFRAME_FIRST_RETENTION_CPU_PREPARED_ACTUAL.json'),package=str(z),no_remote_no_GPU=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(exist_ok=True);save(R/('PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_SSH_GPU=True));raise

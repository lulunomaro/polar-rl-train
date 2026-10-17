"""Independent pre-dispatch coverage review. Preserve V1; add explicit DR/phase readbacks."""
from pathlib import Path
import ast,os,json,time,hashlib,shutil,zipfile,sys,traceback,types,copy
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,numpy as np
B=Path(__file__).resolve().parent;R=B/'reports';A=B/'e3_closed85_frozen_prepared_v1/payload';E=B/'e3_closed85_frozen_prepared_v2';Q=E/'payload';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not E.exists();E.mkdir();shutil.copytree(A,Q,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 loop=Q/'e3_frozen_recovery_loop_v1.py';s=loop.read_text('utf8');needle="w=env._retention_native_witness;rows=w.rows";assert s.count(needle)==1;s=s.replace(needle,"w=env._retention_native_witness;rows=w.rows\n from nominal_parameter_audit import parameter_audit\n parameter_readback=parameter_audit(env);assert parameter_readback['profile']=='white_v3' and parameter_readback['actual_parameters_pass']\n CONTEXT['save']('E3_ACTUAL_WHITE_V3_AND_DR_READBACK.json',dict(actual_parameter_audit=parameter_readback,physical_action_delay=env._physics_action_delay.audit(),chassis_PD=env.chassis_pd_audit(),sensor_recipe=env._sensor_mild.receipt(),feedback_delay=env.feedback_delay_recipe(),fresh104_DR_not_source20000_restore=True))");s=s.replace("result=dict(case_id=args.case_id,source_SHA=args.checkpoint_sha,steps=args.steps,", "result=dict(case_id=args.case_id,source_SHA=args.checkpoint_sha,seed=args.seed,profile=args.dr_profile,steps=args.steps,");loop.write_text(s,encoding='utf8',newline='\n')
 witness=Q/'e3_native_witness_v1.py';s=witness.read_text('utf8');needle="w.phase.update({'E3_'+key:cpu(v) for key,v in e.e3_frame.items()});e.e3_frame=None";assert s.count(needle)==1;s=s.replace(needle,"w.phase.update({'E3_'+key:cpu(v) for key,v in e.e3_frame.items()});w.phase.update({ 'E3_phase_'+key:cpu(getattr(e.recovery,key)) for key in ('recipe','age','peak','stable','credited','request')});e.e3_frame=None");witness.write_text(s,encoding='utf8',newline='\n')
 worker=Q/'e3_frozen_worker_v2.py';worker.write_text((A/'e3_frozen_worker_v1.py').read_text('utf8').replace('E3_CLOSED85_FROZEN_COMPLETE_MANIFEST_V1','E3_CLOSED85_FROZEN_COMPLETE_MANIFEST_V2').replace('E3_CLOSED85_PUBLIC03_FROZEN_V1_20261017','E3_CLOSED85_PUBLIC03_FROZEN_V2_20261017'),encoding='utf8',newline='\n')
 parent=Q/'e3_frozen_parent_v2.py';parent.write_text((A/'e3_frozen_parent_v1.py').read_text('utf8').replace('e3_frozen_worker_v1.py','e3_frozen_worker_v2.py').replace('E3_CLOSED85_FROZEN_COMPLETE_MANIFEST_V1','E3_CLOSED85_FROZEN_COMPLETE_MANIFEST_V2'),encoding='utf8',newline='\n')
 # Execute the actual 104-ray function against a read-only fake query. It must
 # save incomplete/bad rows, reject bad native results, never use a hit as reference.
 path=Q/'e3_plane_reference_104_v1.py';tree=ast.parse(path.read_text('utf8'));fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='query_current_positions');events=[]
 def comparison(reference,hit):return dict(represented_query_within_original_1e6=abs(hit['position'][2])<=1e-6,normal_crosscheck_maxabs=abs(hit['normal'][2]-1.))
 ns=dict(np=np,serialize_raycast_hit=lambda h:h,plain=lambda x:x,compare_actual_hit_readonly=comparison);exec(compile(ast.Module(body=[fun],type_ignores=[]),'actual_query104_CPU','exec'),ns)
 class Query:
  def __init__(self,bad=None):self.bad=bad;self.calls=0
  def raycast_all(self,origin,direction,distance,callback):
   self.calls+=1
   if self.bad=='missing':return False
   h=dict(position=[origin[0],origin[1],2e-6 if self.bad=='offset' else 0.],normal=[0.,0.,2. if self.bad=='normal' else 1.]);callback(h)
   if self.bad=='duplicate':callback(h)
   return True
 xy=np.zeros((104,2),np.float32);resolve=lambda h:dict(resolved_plane_path='/World/ground/geometry/mesh',identity_resolution='fake_CPU_only');q=Query();v,rows=ns['query_current_positions'](q,xy,'CPU',{'independent':True},resolve,lambda v:events.append(copy.deepcopy(v)));assert q.calls==104 and len(rows)==104 and events[-1]['complete_all_envs']
 negative=[]
 for bad in ('missing','offset','normal','duplicate'):
  saved=[]
  try:ns['query_current_positions'](Query(bad),xy,'CPU',{'independent':True},resolve,lambda v:saved.append(copy.deepcopy(v)))
  except AssertionError:assert saved and len(saved[-1]['all_rays'])==1;negative.append(bad)
  else:raise AssertionError('Bad query accepted')
 # Check actual prefix saver losslessly retains extra E3 physical NaN/partial4.
 ns2={};exec(compile((Q/'e2_frozen_prefix_guard_v4.py').read_text('utf8'),'existing_prefix_guard_CPU','exec'),ns2)
 tmp=E/'CPU_failed_prefix_fixture';tmp.mkdir();w=types.SimpleNamespace(rows=[],sub=[{'E3_all31_force':np.full((104,31,3),np.nan),'force':np.zeros((104,2,3))}],args=types.SimpleNamespace(steps=120));saved={};ns2['save_failed_prefix']({'env':types.SimpleNamespace(_retention_native_witness=w)},tmp,lambda n,v:saved.update({n:v}));z=np.load(tmp/'FAILED_VALID_PREFIX_ORIGINAL_ARRAYS.npz');assert np.isnan(z['physical_E3_all31_force']).all() and saved['FAILED_VALID_PREFIX_ACTUAL.json']['actual_physics_rows']==1 and saved['FAILED_VALID_PREFIX_ACTUAL.json']['actual_control_rows']==0
 # Source actor/phase/plant remain unchanged between the two prepared namespaces.
 unchanged=('source/E3_closed85.pt','recovery_closed85_single35_public03_perenv_CPU_v2.py','recovery_closed85_source_guard_v1.py','frozen_shared/runtime/isaac/mod4/e3_recovery_runtime_v1.py','frozen_shared/runtime/isaac/mod4/e3_public_recovery_phase_v1.py','e2_frozen_prefix_guard_v4.py')
 for name in unchanged:assert H(A/name)==H(Q/name)
 manifest=json.loads((A/'E3_CLOSED85_FROZEN_COMPLETE_MANIFEST_V1.json').read_bytes());rows=[]
 for p in sorted(x for x in Q.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.py':ast.parse(p.read_text('utf8'))
  rows.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
 manifest.update(version=2,files=rows,package_files_v8=[dict(relative=r['relative'],bytes=r['bytes'],sha256=r['SHA']) for r in rows],explicit_readonly_DR_and_pre_reset_phase_readbacks_added=True,original_V1_prepared_unexecuted_retained=True)
 mf=Q/'E3_CLOSED85_FROZEN_COMPLETE_MANIFEST_V2.json';mf.write_text(json.dumps(manifest,indent=2),encoding='utf8');bundle=E/'E3_CLOSED85_COMPLETE_FROZEN_PAYLOAD_V2.zip'
 with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for row in rows:z.write(Q/row['relative'],row['relative'])
  z.write(mf,mf.name)
 out=dict(epoch=time.time(),passed_pre_dispatch_actual_query104_prefix_and_source_coverage_CPU=True,original_V1_package_preserved_not_dispatched=True,original_V1_missing_explicit_DR_and_pre_reset_stable_credited_fields_corrected_before_GPU=True,query104_actual_source_positive_and_four_negative_cases=negative,query_bad_row_durable_persist_pre_reject=True,partial1physics0control_E3_NaN_preserved=True,extra_readbacks_do_not_change_policy_physics_reward_reset_or_DR=True,unchanged_source_SHA_pairs=[dict(relative=n,SHA=H(Q/n)) for n in unchanged],manifest=dict(path=str(mf),bytes=mf.stat().st_size,SHA=H(mf)),package=dict(path=str(bundle),bytes=bundle.stat().st_size,SHA=H(bundle)),files=len(rows),no249_upload_or_GPU_or_Task=True,actual_runtime_callback_CPU_reader_and_resource_identity_then_unused_native120_required=True)
 with (R/'E3_FROZEN_V2_QUERY104_PREFIX_AND_DR_PHASE_READBACK_COVERAGE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(V2_CPU_prepared=True,files=len(rows),query_negatives=len(negative),no_GPU=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('E3_FROZEN_V2_COVERAGE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU=True),f,indent=2)
  raise

"""Complete isolated source payload, declared strict eval guards, CPU only; no target dispatch."""
from pathlib import Path
import ast,json,time,hashlib,shutil,sys,types,traceback,zipfile
import numpy as np
G=Path(__file__).resolve().parent;W=G.parent;F=W/'MOD4_THREE_EXPERTS_HEALTHY_FOLLOWUP_V3_20261017';V=W/'MOD4_THREE_EXPERTS_RECOVERED_FULL_FINAL_CONTINUATION_20261017';S=W/'MOD4_S5_NOMINAL_AUDIT_SOURCE_ADAPTER_CPU_20261015/payload';R=G/'reports';E=G/'e2_closed109_frozen_prepared_v3';Q=E/'payload';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not E.exists();E.mkdir();shutil.copytree(S,Q,ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.pt','*.pth','*.npz','*.partial'))
 # Include exact static reset assets excluded by generic data filtering, without copying old models.
 for p in S.rglob('*.npz'):
  q=Q/p.relative_to(S);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 C=F/'e2_closed109_frozen_components_v2';proof=json.loads((F/'reports/E2_CLOSED109_FROZEN_CONTROLLER_COMPONENTS_AND_ROUTE_SOURCE_CPU_V2_ACTUAL.json').read_bytes());assert proof['passed_source_controller_components_CPU_only'];originals=[]
 for p in C.iterdir():
  if not p.is_file():continue
  q=Q/p.name
  if q.exists():
   historical=Q/'historical_original_components'/p.name;historical.parent.mkdir(exist_ok=True);shutil.copy2(q,historical);originals.append(dict(path=str(q),old_SHA=H(q),historical=str(historical)))
  shutil.copy2(p,q)
 for name in ('e2_frozen_prefix_guard_v3.py','e2_frozen_worker_v3.py'):shutil.copy2(G/name,Q/name)
 # Minimal observer-only edits. Original SDK/task/actuator/DR sources remain exact.
 p=Q/'retention_native_witness_v8.py';text=p.read_text('utf8');historical=Q/'historical_original_components/CPU_COMPONENT_V2_retention_native_witness_v8.py';shutil.copy2(p,historical);changes={"CONTEXT={}":"CONTEXT={}\nfrom e2_frozen_prefix_guard_v3 import check_physics,check_control,check_reasons,declared_config","self.names=tuple(e.termination_manager.active_terms)":"self.names=tuple(e.termination_manager.active_terms);check_reasons(self.names)","h=actual_substep_hardware_and_COM(e);r=e.scene['robot']":"h=actual_substep_hardware_and_COM(e);check_physics(h);r=e.scene['robot']","self.rows.append(row);self.episode+=":"self.rows.append(row);check_control(row);self.episode+=","e=ChassisPDMod4Env(cfg=cfg);e._retention_native_witness=Witness(e,args);return e":"CONTEXT['declared_eval_integrity_guard']=declared_config(cfg)\n e=ChassisPDMod4Env(cfg=cfg);CONTEXT['env']=e;e._retention_native_witness=Witness(e,args);return e"}
 for a,b in changes.items():assert text.count(a)==1,(a,text.count(a));text=text.replace(a,b)
 ast.parse(text);p.write_text(text,encoding='utf8')
 parent=(S/'retention_parent_v8.py').read_text('utf8');assert parent.count('retention_worker_v8.py')==2;parent=parent.replace('retention_worker_v8.py','e2_frozen_worker_v3.py').replace('RETENTION_CPU_MANIFEST_V8.json','E2_CLOSED109_FROZEN_COMPLETE_MANIFEST_V3.json');ast.parse(parent);(Q/'e2_frozen_parent_v3.py').write_text(parent,encoding='utf8')
 recipe=json.loads((V/'E2_CLOSED109_SIGNED4_WORLD_V0P5_FROZEN_RECIPE_CPU_V1.json').read_bytes());source=Path(recipe['source']['path']);assert H(source)==recipe['source']['SHA'];src=Q/'source/E2_closed109.pt';src.parent.mkdir(exist_ok=True);shutil.copy2(source,src);(Q/'E2_CLOSED109_SIGNED4_RECIPE_EXACT_CPU_V1.json').write_bytes((V/'E2_CLOSED109_SIGNED4_WORLD_V0P5_FROZEN_RECIPE_CPU_V1.json').read_bytes())
 env=json.loads((Q/'frozen_shared/provenance/original459_run_manifest.json').read_bytes())['env'];env={k:str(v) for k,v in env.items() if k.startswith('RM_')};assert env['RM_SPIN_STAGE']=='world_directional_v1' and env['RM_DR_OFF']=='1' and float(env.get('RM_EPISODE_S',20))>=15 and float(env.get('RM_JUMP_SCRIPT_PROB','0'))==0;env.update(RM_MILD_DR_PROFILE='white_v3',RM_SPIN_MAX_RAD_S='4.0',RM_SPIN_WORLD_PROGRESS_M_S='0.5')
 from e2_frozen_prefix_guard_v3 import check_physics,check_control,check_reasons,declared_config,save_failed_prefix
 good=dict(arrays={'force':np.zeros((88,2,3),dtype=np.float32)},COM_frame_error_m=0.);check_physics(good);row=dict(mimic=np.zeros(88),post_reset_mimic=np.zeros(88),raw=np.zeros((88,6)));check_control(row);check_reasons(('time_out','closure','mimic'));cfg=types.SimpleNamespace(terminations=types.SimpleNamespace(closure=types.SimpleNamespace(params={'threshold':.002}),mimic=types.SimpleNamespace(params={'threshold':.05})));decl=declared_config(cfg);assert cfg.terminations.mimic.params['threshold']==.01 and cfg.terminations.closure.params['threshold']==.002
 negatives=[]
 for name in ('COM_above1e5','COM_nonfinite','mimic_above01','postreset_mimic_above01','nonfinite_control','unknown_termination','closure_threshold_changed'):
  try:
   if name=='COM_above1e5':check_physics(dict(good,COM_frame_error_m=.0000101))
   elif name=='COM_nonfinite':check_physics(dict(good,COM_frame_error_m=float('nan')))
   elif name=='mimic_above01':check_control(dict(row,mimic=np.array([.0101])))
   elif name=='postreset_mimic_above01':check_control(dict(row,post_reset_mimic=np.array([.0101])))
   elif name=='nonfinite_control':check_control(dict(row,raw=np.array([float('nan')])))
   elif name=='unknown_termination':check_reasons(('mimic','unknown'))
   else:declared_config(types.SimpleNamespace(terminations=types.SimpleNamespace(closure=types.SimpleNamespace(params={'threshold':.003}),mimic=cfg.terminations.mimic)))
  except AssertionError:negatives.append(name)
  else:raise AssertionError(name)
 fixture=E/'CPU_failed_prefix_fixture';fixture.mkdir();saved={};fake=types.SimpleNamespace(rows=[dict(x=np.array([float('nan')]),mimic=np.array([.011]))],sub=[dict(force=np.zeros((2,3)))]*3,args=types.SimpleNamespace(steps=1500));pv=save_failed_prefix(dict(env=types.SimpleNamespace(_retention_native_witness=fake)),fixture,lambda n,v:saved.setdefault(n,v));assert pv['actual_control_rows']==1 and pv['actual_physics_rows']==3 and not pv['not_full_requested_scope_pass'] is False
 with np.load(pv['raw']['path'],allow_pickle=False) as z:assert np.isnan(z['control_x'][0,0])
 (fixture/'CPU_ONLY_FIXTURE_SCOPE.json').write_text(json.dumps(dict(CPU_fixture_not_simulation_or_failed_robot=True,preserved_arrays=pv),indent=2),encoding='utf8')
 files=[]
 for p in sorted(x for x in Q.rglob('*') if x.is_file()):
  if p.suffix=='.py':ast.parse(p.read_text('utf8'))
  files.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
 manifest=dict(version=3,source=recipe['source'],source_relative='source/E2_closed109.pt',source_guard='e2_closed109_source_guard_v1.py',source_fixture_no20k_DR_or_optimizer_GPUrestore=True,env=env,recipe=recipe,files=files,package_files_v8=[dict(relative=r['relative'],bytes=r['bytes'],sha256=r['SHA']) for r in files],declared_integrity_guard=decl,original_payload_sources_preserved=True,new_components_not_actual_GPU_native_or_fullroute_pass=True)
 mf=Q/'E2_CLOSED109_FROZEN_COMPLETE_MANIFEST_V3.json';mf.write_text(json.dumps(manifest,indent=2),encoding='utf8');bundle=E/'E2_CLOSED109_COMPLETE_FROZEN_PAYLOAD_V3.zip'
 with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for p in sorted(x for x in Q.rglob('*') if x.is_file()):z.write(p,p.relative_to(Q).as_posix())
 report=dict(epoch=time.time(),passed_complete_isolated_payload_CPU_only=True,payload=str(Q),manifest=dict(path=str(mf),bytes=mf.stat().st_size,SHA=H(mf)),package=dict(path=str(bundle),bytes=bundle.stat().st_size,SHA=H(bundle)),source=recipe['source'],source_files=len(files),worker=dict(path=str(Q/'e2_frozen_worker_v3.py'),SHA=H(Q/'e2_frozen_worker_v3.py')),parent=dict(path=str(Q/'e2_frozen_parent_v3.py'),SHA=H(Q/'e2_frozen_parent_v3.py')),CPU_integrity_negative_cases=negatives,CPU_failed_prefix_preserves_nonfinite_original_and_actual1control3callbacks_without_padding=True,CPU_fixture_not_GPU_or_real_failure=True,declared_guard=decl,observer_edits=changes,historical_source_copies=originals,profile_white_v3_seed60928_signed4_88env11groups_actual_new_recipe=True,no_actual_target_upload_or_GPU_or_MSVC_lock_or_native_or_skill_pass=True,pending=['Actual target current resource/MSVCRT/desktop identity and installed SDK/DLL/fullsource CPU.','Explicit unused native120 lease then independent nativeCPU/source9STD/35/actions/query/contactCOMhardware/exit+lock proof.','Only after native admitted unusedfull1500/6000cb; fullphysical/queryCPU+validprefix and legacyfalse separate.','New dispatch must bind all new manifest/worker/parent/source/case hashes and scope; do not run old S5/curb wrappers or consume old Task.'],all_originals_retained=True)
 with (R/'E2_CLOSED109_COMPLETE_FROZEN_PAYLOAD_STRICT_PREFIX_GUARDS_CPU_V3_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(complete_payload_CPU=True,files=len(files),packagebytes=bundle.stat().st_size,source_SHA=recipe['source']['SHA'],negative_cases=len(negatives),GPU_not_dispatched=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('E2_COMPLETE_PAYLOAD_CPU_V3_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),all_partial_sources_retained_no_GPU_or_target_mutation=True),f,indent=2)
  raise

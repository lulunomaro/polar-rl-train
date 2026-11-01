"""Prepare NEWactualvariant runtime after CPUownerunknown=[]; source/text only.
Uses each OWN exactsourcefinal; commontypedcache/Kitboot mechanics not tasksubstitute.
"""
from pathlib import Path
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;C=T/'E1_three_variants_CPU_actual_v1';OLD=T/'E1_actual_qualification_v1';NO={'.pt','.pth','.ckpt','.npz','.npy','.usd','.zip','.onnx','.safetensors','.pyc'}

def main():
 commonCache=(OLD/'SLOPE135_ACTUAL_TYPED_SOURCE_V1/runtime/isaac/mod4/e1_pinned_source_v1.py').read_bytes();launcher=(OLD/'SLOPE135_ACTUAL_TYPED_SOURCE_V1/runtime/isaac/mod4/launcher_mod4v1_e1_actual.py').read_bytes();native=(OLD/'SLOPE135_ACTUAL_TYPED_SOURCE_V1/worker_n20k_typed_noupdate.py').read_text(encoding='utf-8');fresh=(OLD/'e1_fresh80_actual_worker_v1.template.py').read_text(encoding='utf-8')
 supervisor=(OLD/'supervise_e1_actual_bounded_v1.py').read_text(encoding='utf-8');a="plan['canonical'] in ('CURB141','SLOPE135')";assert supervisor.count(a)==1;supervisor=supervisor.replace(a,"plan['canonical'] in ('CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE_INDEPENDENT50')",1);compile(supervisor,'threeGPU1supervisor','exec')
 with (B/'supervise_variant_gpu1_actual.py').open('x',encoding='utf-8') as f:f.write(supervisor)
 for name in ['CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE_INDEPENDENT50']:
  source=T/'staged_sources'/('E1_'+name+'_40050_MOD4V1_SOURCE_V2');root=B/(name+'_ACTUAL_TYPED_SOURCE_V1');cpu=(C/(name+'_CPU_FOUR_LEAF_ACTUAL_COMPLETE.json')).read_bytes();audit=(C/(name+'_ACTUAL_FULL_NESTED_OWNER_AUDIT_V1.json')).read_bytes();aj=json.loads(audit);cj=json.loads(cpu);assert cj['passed'] and not aj['unmapped_active_or_schema_fields'] and not aj['missing_source_reference_files'] and aj['all_actual_rootkeys_mapped'];root.mkdir(exist_ok=False)
  inputs=[]
  for p in source.rglob('*'):
   if p.suffix.lower() in NO:continue
   if not p.is_file():continue
   raw=p.read_bytes();rel=p.relative_to(source);dst=root/rel;dst.parent.mkdir(parents=True,exist_ok=True)
   with dst.open('xb') as f:f.write(raw)
   inputs.append(dict(relative=str(rel),SHA=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
  rt=root/'runtime/isaac/mod4';p=rt/'e1_pinned_source_v1.py';old=p.read_bytes();p.write_bytes(commonCache)
  with (rt/'launcher_mod4v1_e1_actual.py').open('xb') as f:f.write(launcher)
  meta=json.loads((root/'E1_CANONICAL_SOURCE_METADATA.json').read_bytes());entry=rt/meta['entry'];before=entry.read_text(encoding='utf-8');changed=before
  imports=['from isaaclab.app import AppLauncher  # noqa: E402','from zonglin2_app_launcher import Zonglin2AppLauncher as AppLauncher  # noqa: E402'];hits=[x for x in imports if x in before];assert len(hits)==1;changed=changed.replace(hits[0],'from launcher_mod4v1_e1_actual import E1IsolatedAppLauncher as AppLauncher  # noqa: E402',1);compile(changed,str(entry),'exec');entry.write_text(changed,encoding='utf-8',newline='')
  for fn in ['build_env','runner_config']:
   trees=[ast.parse(v) for v in [before,changed]];nodes=[next(n for n in tr.body if isinstance(n,ast.FunctionDef) and n.name==fn) for tr in trees];assert ast.dump(nodes[0],include_attributes=False)==ast.dump(nodes[1],include_attributes=False)
  # CPUreceipt outsidecheckpoint; selectedtyped49f5/083b/4a5a cache NOretype.
  with (root/'CPU_FOUR_LEAF_ACTUAL_COMPLETE.json').open('xb') as f:f.write(cpu)
  with (root/'CPU_FULL_NESTED_OWNER_AUDIT.json').open('xb') as f:f.write(audit)
  s=native.replace("str(root/'lib')","str(root/'producer/lib')")
  anchor="   runner.alg.actor.eval();runner.alg.critic.eval();obs=runner.env.get_observations();guard.check_observations(obs);start=int(env._sim_step_counter)"
  assert s.count(anchor)==1
  extra="""   extra_path=out/'VARIANT_EXTRA_FULLSTATE_RESUME_STARTUP_VERIFIED.json';extra_actual=json.loads(extra_path.read_bytes());assert extra_actual['all_complete_saved_extras_exact'] and extra_actual['extra_reset_physics_RNG_calls']==0
   cpu_owner=json.loads((root/'CPU_FULL_NESTED_OWNER_AUDIT.json').read_bytes());assert cpu_owner['all_actual_rootkeys_mapped'] and not cpu_owner['unmapped_active_or_schema_fields']
   put('VARIANT_FIRST_BEFORE_CONTROL.json',dict(variant=meta['canonical'],original_source_SHA=task['original_source_SHA'],selected_typed_source_SHA=task['source_SHA'],actual_core=actual,source_cache=cache.receipt(),loaded_extra_before_ONE_original_reset_and_after_audit=extra_actual,original8_fullhelper_receipts=sorted(p.name for p in out.glob('*STARTUP_VERIFIED.json')),actual_rootkey_count=cpu_owner['actual_rootkey_count'],all_actual_root_nested_owners_mapped=True,passthrough_only_is_NOT_physical_apply=True,unknown_root_or_nested_preserve_only_fields=[],original_knownstate_and_namedRNG_applied_by_original_helpers=True,rank0_only20kshard_NOTall60k=meta['canonical']=='CURB_PROTECTED878',NCCL_merge_fork=False,independent113_source_saved_reset_direction=meta['canonical']=='CURB_INDEPENDENT113',nominal_guard=guard.receipt(),birthinertia_or_skill_graduation=False))
"""
  s=s.replace(anchor,extra+anchor,1);compile(s,'typedVariantWorker','exec')
  with (root/'worker_n20k_typed_noupdate.py').open('x',encoding='utf-8') as f:f.write(s)
  s=fresh;anchor="  command=env.command_manager.get_term('twist');assert command._dt==.02";assert s.count(anchor)==1
  addition="""  if meta['canonical'] in ('CURB_INDEPENDENT113','SLOPE_INDEPENDENT50'):
   from independent_expert_axis_v1 import bind_after_restore
   bind_after_restore(env,'CURB20' if meta['canonical']=='CURB_INDEPENDENT113' else 'SLOPE5')
"""
  s=s.replace(anchor,addition+anchor,1);compile(s,'freshVariantWorker','exec')
  with (root/'worker_fresh80_noPT.py').open('x',encoding='utf-8') as f:f.write(s)
  table=[]
  for fn in ['worker_fresh80_noPT.py','worker_n20k_typed_noupdate.py']:
   tree=ast.parse((root/fn).read_bytes());names=sorted({n.args[0].value for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='put' and n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str)})
   table.append(dict(worker=fn,rows=[dict(worker_put=n,parent_expected='gpu1/out/'+n,collector_expected='gpu1/out/'+n,full_basename_equal=True) for n in names]))
  with (root/'ACTUAL_BASENAME_INTERFACE_TABLE_V1.json').open('x',encoding='utf-8') as f:json.dump(dict(variant=name,interfaces=table,all_full_basenames_equal=True,no_global_role_substring_replacement=True),f,indent=2)
  with (root/'NEW_ACTUAL_TYPED_RUNTIME_DERIVATION_V1.json').open('x',encoding='utf-8') as f:json.dump(dict(variant=name,original_sourcefinal=str(source/'FINAL_SOURCE_INDEX.json'),original_sourcefinal_SHA=hashlib.sha256((source/'FINAL_SOURCE_INDEX.json').read_bytes()).hexdigest(),source_inputs=inputs,originalcache_SHA=hashlib.sha256(old).hexdigest(),new_typedonly_cache_SHA=hashlib.sha256(commonCache).hexdigest(),extra_first_before_control=True,source_cpu_owner_unknown=[],no_actual_PT_or_SDK_in_builder=True),f,indent=2)
  print(json.dumps(dict(variant=name,root=str(root),typed_source=cj['new_typed_source'],CPU_owner_unknown=[],actual_PT_SDK_operations_in_builder=0),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('GPU_ACTUAL_SOURCE_BUILDER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),PT_SDK_operations=0),f,indent=2)
  raise

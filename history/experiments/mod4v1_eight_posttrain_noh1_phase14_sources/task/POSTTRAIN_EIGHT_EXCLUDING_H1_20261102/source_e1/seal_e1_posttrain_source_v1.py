"""SealSOURCEonly delivery and originaltrainingimportgraphs. No model/SDK I/O."""
from pathlib import Path
import ast,hashlib,json,sys
from e1_posttrain_contract import REQUIRED_TASK_KEYS,ADMISSION_KIND,GENERATION
from e1_posttrain_make_task import PARENT_INJECT_KEYS,SOURCE_PIN_KEYS
B=Path(__file__).resolve().parent;T=B.parents[1];H=lambda b:hashlib.sha256(b).hexdigest()
def info(p):
 r=p.read_bytes();return dict(path=str(p),bytes=len(r),SHA=H(r))
def put(name,v):
 p=B/name
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 return info(p)
inv=json.loads((B/'FOUR_E1_POSTTRAIN_TRAINER_RESTORE_SAVE_INTERFACE_INVENTORY_V1.json').read_bytes());origin=json.loads((T/'E1_FOUR_WORKERS_REMOTE_NONPT_ORIGIN_DELTA_V1.json').read_bytes());proof=json.loads((B/'FOUR_E1_POSTTRAIN_AST_SCHEMA_STDLIB_MOCK_PROOF_V2.json').read_bytes());assert proof['passed'] and proof['tests']==116 and proof['physical_model_byte_stat_hash_decode']==0
bundle=B/'runtime_bundle';bundle.mkdir(exist_ok=False);runtime=[]
for name in ('worker_e1_posttrain_full20k_original_ppo_v1.py','e1_posttrain_contract.py','e1_posttrain_state_tools.py'):
 p=B/name;r=p.read_bytes();tree=ast.parse(r);compile(tree,str(p),'exec')
 with (bundle/name).open('xb') as f:f.write(r)
 runtime.append(info(bundle/name))
external_prefixes={'isaaclab','isaaclab_physx','isaaclab_rl','isaacsim','carb','omni','pxr','warp','torch','numpy','trimesh','rsl_rl','tensordict','gymnasium','psutil','scipy','packaging','matplotlib','PIL','sympy','mjlab'}
graphs=[]
for case in inv['cases']:
 role=case['role'];root=Path(case['local_runtime_source_root']);mod=root/'runtime/isaac/mod4';search=[mod,root/'runtime',root/'lib',root/'producer/lib',root];queue=[case['original_entry'].removesuffix('.py'),case['restore_helper'],'mod4_task','e1_pinned_source_v1','mod4v1_fresh_dr_guard','rescue_training','e1_terrain_training_health'];done={};unresolved={};external=set();todo=list(queue)
 while todo:
  name=todo.pop();key=name.split('.')[0]
  if key in done:continue
  p=next((d/(key+'.py') for d in search if (d/(key+'.py')).is_file()),None)
  if p is None:
   if key in sys.stdlib_module_names or key in external_prefixes:external.add(name)
   else:unresolved.setdefault(key,[]).append('ROOT_IMPORT')
   continue
  raw=p.read_bytes();tree=ast.parse(raw,filename=str(p));compile(tree,str(p),'exec');imports=[]
  for n in ast.walk(tree):
   if isinstance(n,ast.Import):imports.extend(a.name for a in n.names)
   elif isinstance(n,ast.ImportFrom) and n.module:imports.append(n.module)
  row=dict(module=key,**info(p),AST_SHA=H(ast.dump(tree,include_attributes=False).encode()),all_top_and_lazy_imports=sorted(set(imports)));done[key]=row
  for dep in imports:
   child=dep.split('.')[0]
   if child in sys.stdlib_module_names or child in external_prefixes:external.add(dep);continue
   q=next((d/(child+'.py') for d in search if (d/(child+'.py')).is_file()),None)
   if q is not None:todo.append(child)
   else:unresolved.setdefault(child,[]).append(dict(importer=str(p),module=dep))
 o=next(x for x in origin['rows'] if x['role']==role)
 graphs.append(dict(role=role,new_runtime_additions=runtime,original_entry=case['original_entry'],restore_helper=case['restore_helper'],original_native_root=o['complete_remote_native_nonPT_source_root'],nodes=list(done.values()),external_original_environment_packages=sorted(external),unresolved_local_or_package_candidates=unresolved,source_scope='ASTincludeslazyimportsbutdynamicPath/data/modulecallsmustreusecompleteoriginalnativeRoot/metadata; noSDKpackagecaptureoractualimportpassclaimed',complete_original_nonPT_stage_metadata_entries=len(o['complete_nonPT_files_METADATA_ONLY']),complete_nonPT_stage_metadata_reference=info(T/'E1_FOUR_WORKERS_REMOTE_NONPT_ORIGIN_DELTA_V1.json')))
graph=put('FOUR_E1_POSTTRAIN_ORIGINAL_MODULE_DEPENDENCY_GRAPH_V1.json',dict(kind='SOURCE_AST_ORIGINAL_TRAINING_IMPORTS_AND_NATIVE_ROOT_DATA_REFERENCE',rows=graphs,source_only=True,all_real_model_SDK_operations=0))
worker_tree=ast.parse((B/'worker_e1_posttrain_full20k_original_ppo_v1.py').read_bytes());workerkeys=sorted({n.slice.value for n in ast.walk(worker_tree) if isinstance(n,ast.Subscript) and isinstance(n.value,ast.Name) and n.value.id=='task' and isinstance(n.slice,ast.Constant) and isinstance(n.slice.value,str)})
assert set(workerkeys)<=set(REQUIRED_TASK_KEYS)|{'source_Adam_step','source_Adam17'}
contract=put('PARENT_TASK_GO_ADMISSION_REQUIRED_FIELDS_V1.json',dict(kind='SOURCE_CONTRACT_NO_ACTUAL_ADMISSION_GO_OR_CANONICAL',required_task_fields=list(REQUIRED_TASK_KEYS),required_task_count=len(REQUIRED_TASK_KEYS),worker_all_literal_Task_keys=workerkeys,parent_inject_keys=list(PARENT_INJECT_KEYS),source_pin_keys=list(SOURCE_PIN_KEYS),Adam_alias='source_Adam_step or source_Adam17 required; ifbothmustagree, no default',admission_kind=ADMISSION_KIND,canonical_generation=GENERATION,admission_required_fields=['kind','run_id','role_key','GPU_UUID','source_SHA','asset_USD_SHA','asset_contract_SHA','actual_original_private_GPU_EX_held_by_original_parent','actual_original_shared_finite_env_SH_held','actual_current_canonical_owner_and_budget_admission_passed','canonical_binding'],canonical_binding_required_fields=['path','generation','owner_run_id','owner_parent_pid','one_original_writer'],GO_required_fields=['run_id','role_key','GPU_UUID','source_model_SHA','one_original_writer','original_owner_pid','root_admission_SHA','asset_USD_SHA','asset_contract_SHA','num_envs','policy_hz','feedback_hz','physics_dt','TGS','source_iteration','input_Adam','max_parent_seconds','save_deadline','nominal_end_epoch','exit_headroom_seconds'],original_owner_source=info(T/'w35_mod4v1_finite_original_owner_v4.py'),no_alg_update_budget_hook=True,parent_original_charge_values_only=True,actual_builder=info(B/'e1_posttrain_make_task.py'),fixture_example=info(B/'PARENT_TASK_ADMISSION_GO_SCHEMA_FIXTURE_MOCK_ONLY_V1.json'),templates_index=info(B/'UNUSED_TASK_TEMPLATES_V1/SOURCE_ONLY_DESCRIPTOR_INDEX_V1.json')))
errors=put('SOURCE_ERRORS_SCOPE_AND_ARCHIVE_PENDING_V1.json',dict(kind='SOURCEONLY_ALLERRORS_AND_GAPS_RETAINED',new_actual_trials=0,new_source_execution_errors=[],prior_relevant_errors=[dict(path=str(T/'E1_ORIGINAL_G4_DEPENDENCY_ADDON_SOURCE_V1/PRIOR_13_FILE_COMPLETENESS_APPEND_ONLY_ERRATUM_V1.json'),scope='PriorN80CURB13lazyimportclosureomission; exactG4addonreservedforskillreplay, nottraininggeometry'),dict(path=str(T/'NINE_E1_ALLOCATION_ONLY_SOURCE_REVIEW_V1/SOURCE_REVIEW_READER_ERROR_V1.json'),scope='PriorGBKsourceReadererrorpreserved,separatefromnewtraining'),dict(path=str(T/'E1_PARALLEL_V1_PROOF_SCOPE_ERRATUM_AND_V2_TASK_CONTRACT_V1.json'),scope='PriorTaskschema/noactualadmissionMOCKboundarypreserved')],source_prepublication_review_fixes=['Rejectedabstractbind_training_windowproposalafterparentexactaccountingcontract; noauthorityhookinruntime','Preservedactualcachedeepcopyroutealreadyinoriginalhelper; nofakealiasSDKtest','Best-efforterrorSaveafterselected_sourcecontextrequiredreactivatingsamecache; fixedbeforefirstMOCK,noPTre-read','Noactualschemaorreadererrorsinthisnewsourceproof; V1proof90retained,V2proof116addsrequiredseed/Taskassemblernegatives'],known_gaps=['Noactual20-updatePPO/gradient/backwardGPUfitqualificationbythischild','NoactualTorchCPUstepaliasexperiment; proofisoriginalcacheASTplusstdlibworstcase','ParentactualROOT/GO/leases/canonicalbalanceremainexternal; descriptorNotReadyisnotadmission','OriginalcompleteRootdynamicData/runtime/SDKdependenciesmustbestagedasjoinedproof, graphnotunqualifiedwholeenvironmentcompleteness','S50originalacceptedmetricgap; nooverallgraduationrateornewnumericalthreshold'],parent_Git_phase_archive_append_pending=True,child_Git_writes=0,alloldseals_consumedonce_Runtimeerrors_unchanged=True))
files=[]
for p in sorted(B.rglob('*')):
 if not p.is_file():continue
 assert p.suffix.lower() in ('.py','.json','.md'),('Unexpectednontextartifact',str(p))
 files.append(info(p))
index=put('FINAL_FOUR_E1_POSTTRAIN_SOURCE_INDEX_V1.json',dict(kind='SOURCE_READY_FOR_PARENT_REVIEW_ACTUAL_TASK_NOT_GO',H1_excluded=True,roles=[c['role'] for c in inv['cases']],runtime_bundle=runtime,worker_CLI='python -B WORKER --job-root NEW_UNUSED_FULL_RUNTIME_ROOT --task PARENT_ACTUAL_TASK --out NEW_UNUSED_OUTPUT_DIR',requested_max_additional_updates=20,wallcap_parent_max_seconds=3900,source_interface_inventory=info(B/'FOUR_E1_POSTTRAIN_TRAINER_RESTORE_SAVE_INTERFACE_INVENTORY_V1.json'),proof=info(B/'FOUR_E1_POSTTRAIN_AST_SCHEMA_STDLIB_MOCK_PROOF_V2.json'),dependency_graph=graph,required_parent_contract=contract,archive_pending=errors,files=files,source_model_byte_stat_hash_decode_SDK_SSH_GPU_canonical_GO_PPO_operations=0,parent_files_oldsource_groups_or_once_edited=False,source_handoff=info(B/'SOURCE_HANDOFF.md')))
print(json.dumps(dict(index=index,runtime_bundle=runtime,required_task_fields=len(REQUIRED_TASK_KEYS),original_module_nodes=[dict(role=x['role'],nodes=len(x['nodes']),unresolved=list(x['unresolved_local_or_package_candidates'])) for x in graphs],mock_tests=116,PT_SDK_operations=0),indent=2))

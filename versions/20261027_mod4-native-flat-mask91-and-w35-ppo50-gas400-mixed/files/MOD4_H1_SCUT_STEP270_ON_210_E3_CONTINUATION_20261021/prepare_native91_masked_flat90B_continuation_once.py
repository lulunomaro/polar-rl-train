from pathlib import Path
import ast,copy,hashlib,json,pprint,runpy,shutil,time,traceback
T=Path(__file__).resolve().parent
O=T/'MOD4_H1_FLAT05_NATIVE_SINGLE72_RESOURCE_V90B_20261027'
N=T/'MOD4_H1_FLAT05_MASK_AWARE_MIXED72_RESOURCE_V91_20261027'
L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
F=L/'flat91_mask_aware_goal_conditioning_source_v1'
JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_MASK_AWARE_2610v91/h1'
SHA='8b0ef2b6c60f4453ebb46a9718133e54e33cad5985ddd96459e479d10fc5ef43'
KIND='MOD4_NATIVE90B_H1_MASK_AWARE_FLAT91_TYPED_SOURCE_CPU_V1'

def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)
def write(p,s):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(s,encoding='utf8')
def replace_def(s,name,new):
 node=next(n for n in ast.parse(s).body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
 lines=s.splitlines(keepends=True);return ''.join(lines[:node.lineno-1])+new.rstrip()+'\n'+''.join(lines[node.end_lineno:])

def main():
 assert not N.exists();N.mkdir();R=N/'reports';R.mkdir();B=N/'payload';B.mkdir();P=N/'controllers';P.mkdir()
 put(R/'NATIVE91_PREPARATION_STARTED_ACTUAL.json',dict(epoch=time.time(),new_source_purpose=True,no_remote=True,no_model_decode=True))
 closed=read(O/'reports/FLAT90B_COMPLETE_FINAL_OR_PARTIAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json')
 qual=read(O/'reports/FLAT90B_FORMAL_NATIVE_FULLSTATE_INITIAL_CPU_AND_COST_ACTUAL.json')
 assert qual['passed'] and closed['published']['SHA']==SHA and closed['canonical_None']
 pub=closed['published']['original_producer'];base=runpy.run_path(str(O/'payload/source/native88C_flat_pins_v1.py'))
 oldtask=read(O/'payload/job0/TASK.json');oldmf=read(O/'payload/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 for row in oldmf['files']:
  rel=row['relative'];src=O/'payload'/rel;dest=B/rel;dest.parent.mkdir(parents=True,exist_ok=True)
  if rel=='job0/source/'+oldtask['source_filename']:continue
  shutil.copy2(src,dest)
 nativefile='H1_native90B_qualified_h1.pt';shutil.copy2(Path(closed['published']['local_path']),B/'job0/source'/nativefile)
 pins=copy.deepcopy(base['SOURCE_PINS'])
 pins.update(final=pub,native_contract=base['NATIVE_CONTRACT'],producer=pub['producer'],source_migration_window=pub['native88_migration_window'])
 contract=copy.deepcopy(base['NATIVE_CONTRACT'])
 contract['goal_conditioning']=dict(encoding='mod4.flat91.mask_aware_after_normalization.v1',source_networks_SHA=H(F/'supermimic_wheel_leg_v3/networks.py'),source_helper_SHA=H(F/'flat91_mask_aware_goal_conditioning_v1.py'),normalization_buffers_and_parameters_restored_literal=True)
 text='"""Exact qualified90B metadata, no PT decode in source builder."""\n'
 for name,value in [('SOURCE_PINS',pins),('NATIVE_CONTRACT',contract),('FLAT_OBJECTIVE_SHA',base['FLAT_OBJECTIVE_SHA']),('FLAT_OBJECTIVE_CONTRACT',base['FLAT_OBJECTIVE_CONTRACT'])]:text+=name+'='+pprint.pformat(value,width=120,sort_dicts=False)+'\n'
 write(B/'source/native90B_mask91_pins_v1.py',text)
 # Preserve the exact old validator in a separate namespace for historical lineage.
 shutil.copy2(O/'payload/source/native88C_flat_pins_v1.py',B/'source/native90B_prior_flat_pins_v1.py')
 oldmig=(O/'payload/source/native88C_to_flat_migration_v1.py').read_text('utf8')
 write(B/'source/native90B_prior_migration_validation_v1.py',oldmig.replace('from native88C_flat_pins_v1 import','from native90B_prior_flat_pins_v1 import',1))
 s=oldmig.replace('from native88C_flat_pins_v1 import','from native90B_mask91_pins_v1 import',1)
 for a,b in [("'a9bf6dca376e9d570ef0a6e2c15604f38656c4ebfedaa829a34830ee57c73aaf'",repr(SHA)),('64690','78410'),('6469','7841'),('6341','7649'),("'MOD4_own_flat5cm_native400_continuation'","'MOD4_own_flat5cm_mask91_native400_continuation'"),("'MOD4_NATIVE88C_H1_TO_FLAT05_TYPED_SOURCE_CPU_V1'",repr(KIND)),('mod4.native88C_to_flat05.objective_window.v1','mod4.native90B_to_flat05_mask91.objective_window.v1'),('9223a53e7bf85a0dc3505cc46c0eb33d04fc35a9bf85e7ffe0e4fbd03e1e46c3',base['FLAT_OBJECTIVE_SHA'])]:s=s.replace(a,b)
 s=replace_def(s,'validate_source','''def validate_source(full,expected_source_contract,expected_args,expected_progress,expected_reference_SHA):
 from native90B_prior_migration_validation_v1 import verify_saved_migration as verify_prior
 require(exact_plain(expected_source_contract,SOURCE_PINS['native_contract']),'exact qualified90B source contract')
 require(exact_plain(expected_args,SOURCE_PINS['native_args']),'exact saved architecture/args')
 require(exact_plain(expected_progress,{k:SOURCES['h1'][k] for k in ('updates','world_updates','policy_updates')}),'exact90B source progress')
 require(expected_reference_SHA==SOURCE_REFERENCE_SHA,'exact source flat reference')
 pub=full['UniSuperMimic_publication'];native=full['UniSuperMimic_H1_test']
 verify_prior(full,pub)
 require(exact_plain(full['UniSuperMimic_test_contract'],SOURCE_PINS['native_contract']),'qualified90B contract, no old88C loader')
 require(exact_plain(pub['producer'],SOURCE_PINS['producer']),'qualified90B producer literal')
 require(exact_plain(pub['native88_migration_window'],SOURCE_PINS['source_migration_window']),'qualified90B migration literal')
 require(exact_plain(native['args'],expected_args),'config literal')
 require(native['iteration']==pub['native_iteration']==7841 and pub['world_updates']==78410 and pub['policy_updates']==7649,'exact90B global counters')
 for name,steps,count,betas in [('opt_wm',78410,14,(.9,.999)),('opt_pi',7649,20,(.9,.95)),('opt_v',152980,6,(.9,.999))]:
  opt=native[name];require(len(opt['state'])==count and {int(x['step']) for x in opt['state'].values()}=={steps},'native90B optimizer '+name)
  require(all(tuple(x['betas'])==betas for x in opt['param_groups']),'native betas '+name)
 require(len(full['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in full['optimizer_state_dict']['state'].values()}=={832460},'separate literal frozenRSL832460')
 return native,pub
''')
 s=s.replace("source=validate_role_source(key,task['source_SHA'],task['source_progress'])","source=validate_role_source(key,task['source_SHA'],task['source_progress'])\n require(task.get('goal_encoding_changed_from90B') is True and go.get('goal_encoding_changed_from90B') is True,'explicit masked goal migration')")
 write(B/'source/native88C_to_flat_migration_v1.py',s)
 shutil.copy2(F/'supermimic_wheel_leg_v3/networks.py',B/'source/supermimic_wheel_leg_v3/networks.py')
 shutil.copy2(F/'flat91_mask_aware_goal_conditioning_v1.py',B/'source/flat91_mask_aware_goal_conditioning_v1.py')
 task=copy.deepcopy(oldtask);task.update(id='MOD4_H1_FLAT05_MASK_AWARE_V91',source_SHA=SHA,source_filename=nativefile,source_progress=dict(updates=7841,world_updates=78410,policy_updates=7649),source_native_iteration=7841,source_native_contract=pins['native_contract'],goal_encoding_changed_from90B=True,goal_conditioning=contract['goal_conditioning'])
 task['source_qualification_kind']=KIND
 guard=(B/'native_flat90_source_guard_v1.py').read_text('utf8').replace("dict(updates=6469,world_updates=64690,policy_updates=6341)","dict(updates=7841,world_updates=78410,policy_updates=7649)").replace('mod4.native.flat05.complete_source.v1','mod4.native.flat05.mask91.complete_source.v1')
 write(B/'native_flat90_source_guard_v1.py',guard)
 entry=B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py'
 s=entry.read_text('utf8').replace("method='MOD4_own_flat5cm_native400_continuation'","method='MOD4_own_flat5cm_mask91_native400_continuation'")
 s=s.replace("source_reference_artifact_SHA='9223a53e7bf85a0dc3505cc46c0eb33d04fc35a9bf85e7ffe0e4fbd03e1e46c3'","source_reference_artifact_SHA='"+base['FLAT_OBJECTIVE_SHA']+"'")
 s=s.replace("native_architecture_fresh=False,original_source_cost_and_physical_save_chain_preserved=True,","native_architecture_fresh=False,original_source_cost_and_physical_save_chain_preserved=True,\n        goal_encoding_changed_from90B=True,goal_conditioning=task['goal_conditioning'],")
 write(entry,s)
 # SDK/initial-fullstate program keeps the actual old SDK checks and one load each.
 cpu=B/'target_native_flat90_source_sdk_CPU_once.py';s=cpu.read_text('utf8').replace('initial_loads=dict(native88C=1,normal86=1)','initial_loads=dict(native90B=1,normal86=1)')
 s=s.replace("require(not torch.cuda.is_initialized(),'CPU admission unexpectedly initialized CUDA')","from flat91_mask_aware_goal_conditioning_v1 import masked_goal_conditioning,validate_goal_source\n goal=mdp.goal(torch.tensor([210]),10);validate_goal_source(goal);conditioned=masked_goal_conditioning(pi.goal_norm(goal),goal).reshape(1,10,146)\n require((conditioned[...,13:73]==0).all() and (conditioned[...,73:]==goal.reshape(1,10,146)[...,73:]).all(),'actual source mask-aware conditioning')\n require(not torch.cuda.is_initialized(),'CPU admission unexpectedly initialized CUDA')")
 s=s.replace('source_native_args_exact=True,initial_loads=','mask_aware_goal_source_CPU_passed=True,goal_conditioning=task[\'goal_conditioning\'],source_native_args_exact=True,initial_loads=')
 write(cpu,s)
 oldc=read(O/'payload/FLAT90_SOURCE_CONTRACT_ACTUAL.json');c=copy.deepcopy(oldc)
 c.update(schema='mod4.native.flat05.mask91.complete_source.v1',source_SHA=SHA,goal_conditioning=contract['goal_conditioning'])
 c['protected_current88C_files']={rel:sha for rel,sha in c['protected_current88C_files'].items() if rel not in ('source/supermimic_wheel_leg_v3/networks.py',)}
 # Explicit old/new network derivation is independently pinned, not blanket relaxation.
 c['prior_networks_SHA']=H(O/'payload/source/supermimic_wheel_leg_v3/networks.py');c['selected_mask_networks_SHA']=H(F/'supermimic_wheel_leg_v3/networks.py')
 c['approved_python']={p.relative_to(B).as_posix():H(p) for p in B.rglob('*.py')}
 write(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json',json.dumps(c,indent=2))
 task['flat_source_contract_SHA']=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');write(B/'job0/TASK.json',json.dumps(task,indent=2))
 rows=[];oldrows={r['relative']:r for r in oldmf['files']}
 for p in sorted(B.rglob('*')):
  if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
  rel=p.relative_to(B).as_posix()
  if p.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):
   if rel=='job0/source/'+nativefile:row=dict(relative=rel,bytes=closed['published']['bytes'],SHA=SHA)
   else:
    row=oldrows[rel];assert p.stat().st_size==row['bytes']
  else:row=dict(relative=rel,bytes=p.stat().st_size,SHA=H(p))
  rows.append(row)
 mf=copy.deepcopy(oldmf);mf.update(source_SHA=SHA,files=rows);write(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',json.dumps(mf,indent=2))
 # Keep controller/node filenames for original ABI, change only typed protocol constants.
 for p in (O/'controllers').glob('*.py'):shutil.copy2(p,P/p.name)
 protocol=(P/'flat90_protocol_v1.py').read_text('utf8')
 for a,b in [("MOD4_H1_FLAT05_NATIVE_2610v90b",'MOD4_H1_FLAT05_MASK_AWARE_2610v91'),('a9bf6dca376e9d570ef0a6e2c15604f38656c4ebfedaa829a34830ee57c73aaf',SHA),('dict(updates=6469,world_updates=64690,policy_updates=6341)','dict(updates=7841,world_updates=78410,policy_updates=7649)'),('MOD4_NATIVE88C_H1_TO_FLAT05_TYPED_SOURCE_CPU_V1',KIND)]:protocol=protocol.replace(a,b)
 protocol=protocol.replace("for k in ('worker_SHA'","require(s.get('goal_encoding_changed_from90B') is True,'new mask-aware input encoding')\n for k in ('worker_SHA'",1)
 protocol=protocol.replace("flat05_objective_changed_from_native88C=True,actual_H1_flat05_scope_admitted=True","flat05_objective_changed_from_native88C=True,goal_encoding_changed_from90B=True,actual_H1_flat05_scope_admitted=True")
 write(P/'flat90_protocol_v1.py',protocol);write(P/'h1_next72_protocol.py',protocol)
 # New mixed launcher receives complete h1 spec directly, no single-slot boundcfg used.
 request_fields=dict(key='h1',nativeflat90=True,native_continuation=True,source_SHA=SHA,source_progress=task['source_progress'],source_Adamstep=832460,bootstrap_source_SHA=task['bootstrap_source_SHA'],native_seed=27,native_reference_SHA=task['native_reference_SHA'],source_native_iteration=7841,GPU_UUID=task['GPU_UUID'],execution_backend='target72',private_lock='/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_'+task['GPU_UUID']+'.lock',job_root=JOB,python='/home/lc01/Zonglin Li/zonglin2/run-python.sh',production_script='h1_native_flat90_worker_v1.py',max_parent_seconds=3900,exit_headroom_seconds=300,owner_authority_generation='MOD4_SINGLE_WRITER72_20261026',num_envs=4096,policy_hz=100,source_qualification_kind=KIND,changed_plant700_to_nominal400=False,flat05_objective_changed_from_native88C=True,goal_encoding_changed_from90B=True,gas400_parameter_source_contract_SHA=task['gas400_parameter_source_contract_SHA'],CPU_path=JOB+'/job0/FLAT90_SOURCE_SDK_CPU_ACTUAL.json',CPU_proof_path=JOB+'/job0/FLAT90_SOURCE_CPU_WAITED_ACTUAL.json',payload_manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'),payload_manifest_path=JOB+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json',source_contract_path=JOB+'/FLAT90_SOURCE_CONTRACT_ACTUAL.json',actual_gas400_asset_composition_report_SHA=task['actual_gas400_asset_composition_report_SHA'],own_step_objective_qualification_SHA=task['own_step_objective_qualification_SHA'],worker_SHA=H(B/'h1_native_flat90_worker_v1.py'))
 put(R/'NATIVE91_SOURCE_PREPARED_ACTUAL.json',dict(epoch=time.time(),task=task,manifest_SHA=request_fields['payload_manifest_SHA'],source_contract_SHA=request_fields['source_contract_SHA'],h1_spec_pending_actual_CPU_and_controller=request_fields,qualified_native90B_source=closed['published'],local_native_source_read_or_hash=False,small_source_only=True,not_installed_or_GO=True))
 for p in [*B.rglob('*.py'),*P.glob('*.py')]:ast.parse(p.read_bytes())
 put(R/'NATIVE91_FULL_SOURCE_AST_PREPARED_ACTUAL.json',dict(passed=True,all_manifested_Python_AST=True,source_only_no_actual_SDK_yet=True,changed_networks_H1_only=True))
 # Correct previous root reader's mistaken tail-gap inference from existing text only.
 e=pub['original_H1_events']['flat_real_physics_events'];assert e['callbacks']==3494*4
 put(R/'CLOSED90B_TERMINAL_FLAT_COUNTER_FOUND_EXISTING_TEXT_ADDENDUM_ACTUAL.json',dict(epoch=time.time(),prior_root_scope_report_retained=True,prior_missing_three_tail_claim_incorrect=True,actual_existing_field='published.original_producer.original_H1_events.flat_real_physics_events',formal_complete_controls=3494,callbacks=e['callbacks'],events=e['lifetime'],diagnostic_errors=e['diagnostic_errors'],no_model_or_raw_read=True,no_observed_flat_success=True))
 print(json.dumps(dict(prepared=True,new_native_source=SHA,Python_AST_passed=True,actual_install_pending=True)))

if __name__=='__main__':
 try:main()
 except BaseException:
  if (N/'reports').is_dir():put(N/'reports'/('NATIVE91_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(traceback=traceback.format_exc(),no_retry_old_once=True))
  raise

"""Only local data-driven sourcepayloads for four unconsumed experts. No SSH/owner/GPU/SDK/selectedPT/C/GO. Roles never replaced inside code/keys."""
from pathlib import Path
import ast,sys,json,hashlib
D=Path(__file__).resolve().parent;R=D.parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(D/'source_e1_v2'));from e1_historical_proof_normalizer import build_role_spec
BASE=D/'parent_source/original_budget_and_asset_refs';USD='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3';CONTRACT='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755';source=json.loads((D/'parent_source/E2_E3_VALIDATED_ROLE_SPECS_V2.json').read_bytes());out=D/'parent_source/GENERIC_PAIR2_PAIR3_LOCAL_PAYLOAD_INDEX_V2.json';assert not out.exists();groups=[]

def copy_source(src,dst,expected=None):
 p=Path(src);assert p.suffix.lower()not in{'.pt','.pth','.ckpt','.safetensors','.onnx','.pyc','.partial'};raw=p.read_bytes();digest=hashlib.sha256(raw).hexdigest();assert expected is None or digest==expected
 if p.suffix=='.py':ast.parse(raw.decode('utf-8-sig'))
 dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(raw);return dict(path=str(dst),relative=None,bytes=len(raw),SHA=digest)

for idx,erole,e1role in((2,'E2','CURB_INDEPENDENT113'),(3,'E3','SLOPE135')):
 e=next(x for x in source['rows']if x['role']==erole);run=e['run_id'];remote=e['future_group_root_not_created'];payload=D/('PAIR'+str(idx)+'_GENERIC_V2_DATA_PAYLOAD');assert not payload.exists();payload.mkdir();e1=build_role_spec(e1role,remote+'/roles/'+e1role,run);specs=[e,e1];entries=[]
 for name,src in(('eight_posttrain_original_owner_v1.py',D/'parent_source/eight_posttrain_original_owner_v1.py'),('stage_generic_nonpt_roles_v2.py',D/'parent_source/stage_generic_nonpt_roles_v2.py'),('three_slot_common_v1.py',BASE/'three_slot_common_v1.py'),('single_writer72_authority_V85M_source.py',BASE/'single_writer72_authority_V85M_source.py')):copy_source(src,payload/name)
 for s in specs:
  role=s['role'];job=remote+'/roles/'+role;role_payload=payload/'uploads'/role;role_payload.mkdir(parents=True);sp=s['source_pin'];assert role not in('E0','CURB_PROTECTED878','H1')and sp['SHA']==s['source_model_metadata']['SHA'];assert s['normalized_proof']['whole_state_restore_passed']and s['normalized_proof']['historical_reference_not_newtrainingpass']
  if s['source_family']=='e0_e2_e3':
   for f in s['runtime_source_files']:copy_source(f['path'],role_payload/f['relative'],f['SHA'])
   proof=s['historical_raw_proof'];copy_source(proof['path'],role_payload/'evidence/ORIGINAL_EXACT_SOURCE_FULL20K_RAW.json',proof['SHA']);required=s['required_immutable_files'];template={};got={};argv=s['worker_argv'];stop=s['stop_relative'];updates=s['final_updates_key']
  else:
   for path in s['runtime_source_paths']:copy_source(path,role_payload/Path(path).name)
   copy_source(D/'source_e1/e1_posttrain_make_task.py',role_payload/'e1_posttrain_make_task.py')
   for f in s['payload_source_inputs']:copy_source(f['local_path'],role_payload/f['payload_relative'],f['SHA'])
   proof=s['historical_raw_proof'];copy_source(proof['path'],role_payload/'evidence/ORIGINAL_EXACT_SOURCE_FULL20K_RAW.json',proof['SHA']);required=[dict(relative=name)for name in s['required_immutable_metadata']];template=s['task_template'];template.update(new_job_root=job,asset_dir=job+'/runtime/assets');got=dict(source_iteration=sp['iteration'],input_Adam=sp['Adam17'],source_qualification_kind=template['kind']);argv=['{JOB}/worker_e1_posttrain_full20k_original_ppo_v1.py','--job-root','{JOB}','--task','{JOB}/TASK.json','--out','{JOB}/production'];stop='STOP_AFTER_SAVE.json';updates='completed_actual_updates'
  for n in('NEW_ASSET_NATIVE_ACTUAL.json','RM70_SCOPE_REUSE_ACTUAL.json'):copy_source(BASE/'evidence'/n,role_payload/'evidence'/n)
  assets=R.parent/'mod4_usd_scut_fudan_20261101/candidates/v1/assets'
  for n,h in(('robot.usd',USD),('import_contract.json',CONTRACT)):copy_source(assets/n,role_payload/'runtime/assets'/n,h)
  p=role_payload/'evidence/PRIOR_FULL20K_REFERENCE.json';p.write_text(json.dumps(s['normalized_proof'],indent=2),encoding='utf-8')
  entry=dict(role=role,role_key='posttrain_'+role.lower()+'_72',source_family=s['source_family'],base_root=s['base_root'],job_root=job,source_SHA=sp['SHA'],source_model_metadata=s['source_model_metadata'],task_template=template,go_template=got,max_additional_updates=20,num_envs=20000,max_parent_seconds=3900,save_after_seconds=3600,exit_headroom_seconds=300,manifest_file='INSTALL_MOD4V1_POSTTRAIN_ACTUAL.json',actual_prior_full20k_proof_file='evidence/PRIOR_FULL20K_REFERENCE.json',native0pt_evidence_file='evidence/NEW_ASSET_NATIVE_ACTUAL.json',target_source_SDK_receipt_file='evidence/ORIGINAL_EXACT_SOURCE_FULL20K_RAW.json',historical_geometry_evidence_file='evidence/RM70_SCOPE_REUSE_ACTUAL.json',source_contract_AST_MOCK_passed=True,source_contract_not_SDK_pass_claim=True,required_immutable_files=required,worker_argv=argv,final_file='production/FINAL.json',stop_relative=stop,final_updates_key=updates)
  assert entry['native0pt_evidence_file']=='evidence/NEW_ASSET_NATIVE_ACTUAL.json'and entry['source_family']in('e0_e2_e3','e1');assert not any(k.startswith(('native2pt','native3pt'))for k in entry);entries.append(entry)
 plan=dict(run_id=run,H1_excluded=True,entries=entries,source_stage_not_training_pass=True,prepared_not_dispatched_or_admitted=True,firstpair_frozen_retention_still_required=True)
 (payload/'SOURCE_PLAN.json').write_text(json.dumps(plan,indent=2),encoding='utf-8');(payload/'SCHEDULE_PUBLIC.json').write_text(json.dumps({'experts':{x['role_key']:{'max_parent_seconds':3900,'GPU_UUID':['GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'][i]}for i,x in enumerate(entries)}},indent=2),encoding='utf-8');groups.append(dict(pair=idx,root=remote,run_id=run,local_payload=str(payload),roles=[x['role']for x in entries],source_models_SDK_SSH_GO_C_or_lock_operations=0,remote_root_created=False))
report=dict(kind='DATA_DRIVEN_LOCAL_SOURCE_PAYLOADS_PAIR2_3_NOT_ACTUAL_DISPATCH',groups=groups,source_models_stat_hash_decode=0,role_text_replacement=False,firstpair_not_retrained=True);out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(out);print(json.dumps(report,indent=2))

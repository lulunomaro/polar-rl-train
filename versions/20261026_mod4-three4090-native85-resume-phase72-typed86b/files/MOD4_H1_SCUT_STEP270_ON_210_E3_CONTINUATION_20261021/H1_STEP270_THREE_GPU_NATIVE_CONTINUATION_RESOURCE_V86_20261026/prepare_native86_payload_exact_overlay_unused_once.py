"""Bind the actual native85 source into a new payload. No model load/hash/GO."""
from pathlib import Path
import copy,hashlib,importlib.util,json,shutil,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;J=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026';P=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026';A=J/'agent_native86_typed_source_worker_cpu_20261026/candidate_overlay';R=N/'reports';D=N/'payloads/e2'
def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def row(path,relative):return dict(relative=relative,bytes=path.stat().st_size,SHA=H(path))
def put(name,value):
 with (R/name).open('x',encoding='utf8') as stream:json.dump(value,stream,indent=2)
def main():
 assert not D.exists();D.mkdir(parents=True)
 old=P/'payloads/e2';manifest=json.loads((old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());baseline={r['relative']:r for r in manifest['files']}
 assert H(old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')=='f7e259393fc05cc8aa0ff8b7c2f2658dcc8c202436ba85d9a629409cd96445cd'
 for item in manifest['files']:
  src=old/item['relative'];dst=D/item['relative'];assert src.is_file() and not src.is_symlink() and src.stat().st_size==item['bytes'];assert dst.resolve().is_relative_to(D.resolve());dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 for source in A.rglob('*'):
  if source.is_file():
   dest=D/source.relative_to(A);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
 contract=json.loads((D/'NATIVE86_SOURCE_CONTRACT_ACTUAL.json').read_bytes())
 assert contract['source_review_revision']==4
 for name in ('three_slot_common_v1.py','forwarded_original_owner_control_v1.py','three_real_gpu_resource_v1.py'):
  source=N/'controllers_v2'/name;shutil.copyfile(source,D/name);item=row(D/name,name);item['original_SHA']=baseline[name]['SHA'];contract['controller_replacements'].append(item)
 shutil.copyfile(N/'controllers_v2/mixed86_protocol_v1.py',D/'mixed86_protocol_v1.py')
 contract['controller_additions']=[row(D/'mixed86_protocol_v1.py','mixed86_protocol_v1.py')]
 task=json.loads((D/'job0/TASK.json').read_bytes());task.update(id=N.name+'_e2',key='e2',GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',execution_backend='target72',native_continuation=True,native_continuation_restore_required=True,
  source_SHA='94e7f272176b4a7c485b50c1ac61f95a3ecd4460ee6a73034f9e7a47a57045af',source_filename='native85_final.pt',source_Adamstep=829700,
  bootstrap_source_SHA='8bb9869ac683550c1e7be1c9dffae9a5eac022e0de0fc8f251cd2005cfa6d4c6',bootstrap_Adam=829700,source_native_iteration=68,window_start_world_updates=680,window_start_policy_updates=58,
  source_owned_updates=68,source_owned_completed_updates=68,exact_closed_source_updates=68,source_parent_production_root='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2',
  previous_PPO83B_fields_are_frozen_bootstrap_provenance=True,typed_source_not_production_H1_or_E2=True)
 assert 'manifest_SHA' not in task and 'native_source_contract_SHA' not in task
 (D/'job0/TASK.json').write_text(json.dumps(task,indent=2),'utf8')
 item=row(D/'job0/TASK.json','job0/TASK.json');item['original_SHA']=baseline['job0/TASK.json']['SHA'];contract['metadata_replacements']=[item]
 contract['source_only']=False;contract['root_payload_prepared_actual_not_installed']=True
 contract['actual_installed86_SDK_CPU_passed']=False
 (D/'NATIVE86_SOURCE_CONTRACT_ACTUAL.json').write_text(json.dumps(contract,indent=2),'utf8')
 native=P/'current_native_H1_method_fullstate/e2/native_supermimic_H1_final.pt';assert native.stat().st_size==140492265
 shutil.copyfile(native,D/'job0/source/native85_final.pt')
 updated=copy.deepcopy(manifest);updated.update(source_SHA=task['source_SHA'],source_filename=task['source_filename'],bootstrap_filename=manifest['source_filename'],bootstrap_SHA=task['bootstrap_source_SHA'],bootstrap_Adam=829700,source_Adamstep=829700,kind='UNISUPERMIMIC_FUDAN_NATIVE85_TYPED_CONTINUATION_V86',not_production_source=True)
 rows=copy.deepcopy(baseline)
 for item in contract['overlay_files']:rows[item['relative']]=item
 for item in contract['controller_replacements']+contract['metadata_replacements']:rows[item['relative']]={k:item[k] for k in ('relative','bytes','SHA')}
 for item in contract['controller_additions']:rows[item['relative']]=item
 rows['NATIVE86_SOURCE_CONTRACT_ACTUAL.json']=row(D/'NATIVE86_SOURCE_CONTRACT_ACTUAL.json','NATIVE86_SOURCE_CONTRACT_ACTUAL.json')
 rows['job0/source/native85_final.pt']=dict(relative='job0/source/native85_final.pt',bytes=140492265,SHA=task['source_SHA'])
 updated['files']=[rows[k] for k in sorted(rows)];(D/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(updated,indent=2),'utf8')
 q=json.loads((P/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());spec=copy.deepcopy(q['specs']['e2']);spec.update(source_SHA=task['source_SHA'],source_filename=task['source_filename'],bootstrap_source_SHA=task['bootstrap_source_SHA'],native_continuation=True,native_continuation_restore_required=True,
  source_native_iteration=68,window_start_world_updates=680,window_start_policy_updates=58,manifest_SHA=H(D/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),native_source_contract_SHA=H(D/'NATIVE86_SOURCE_CONTRACT_ACTUAL.json'),candidate_pins=contract['candidate_pins'],owner_authority_generation='MOD4_SINGLE_WRITER72_20261026',
  previous_runtime_root=task['source_parent_production_root'],displaced_runtime_root=task['source_parent_production_root'],source_origin_runtime_root=task['source_parent_production_root'])
 module_spec=importlib.util.spec_from_file_location('native86_payload_local_nonmodel_guard',D/'native86_source_guard_v1.py');m=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(m)
 checked=m.check_payload(D,spec,verify_model_bytes=False)
 put('NATIVE86_EXACT_PAYLOAD_SOURCE_BINDING_LOCAL_NONMODEL_CPU_ACTUAL.json',dict(epoch=time.time(),passed=checked['passed'],scope='full exact source inventory and model stat/producer pins; no PT load or local model hash',payload=str(D),root='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_three_gpu_native_cont_2610v86/e2',spec=spec,
  native_source=dict(path='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/job0/production/native_supermimic_H1_final.pt',bytes=140492265,SHA=task['source_SHA']),manifest_files=len(updated['files']),no_actual_installed86_SDK_or_Task_GO=True,typed_bootstrap_separate=True))
 print(json.dumps({'native_payload_prepared':True,'files':len(updated['files']),'manifest_SHA':spec['manifest_SHA'],'no_GO':True}))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('NATIVE86_PAYLOAD_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_remote_or_runtime_or_budget_change=True,no_retry_same_payload_root=True));raise

from pathlib import Path
import copy,hashlib,importlib.util,json,shutil,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;P=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026';P83=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026';A=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026/agent_normal86_H1_E3_typed_source_cpu_20261026/candidate_overlays';R=N/'reports'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def row(p,r):return dict(relative=r,bytes=p.stat().st_size,SHA=H(p))
def main():
 sources={key:json.loads((root/'reports'/name).read_bytes()) for key,root,name in [('h1',P83,'THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'),('recovery',P,'V85M2_SINGLE72_NATIVE_E3_AND_ACTUAL_COST_CPU_ACTUAL.json')]}
 q83=json.loads((P83/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());q85=json.loads((P/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());results={}
 for key in ('h1','recovery'):
  donor=(P83 if key=='h1' else P)/('payloads/'+key);D=N/('payloads/'+key);assert not D.exists();D.mkdir(parents=True)
  m=json.loads((donor/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());oldrows={r['relative']:r for r in m['files']};overlay=A/key
  for item in m['files']:
   source=donor/item['relative'];target=D/item['relative'];assert source.is_file() and source.stat().st_size==item['bytes'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
  for source in overlay.rglob('*'):
   if source.is_file():
    target=D/source.relative_to(overlay);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
  c=json.loads((D/'NORMAL86_SOURCE_CONTRACT_ACTUAL.json').read_bytes());binding=json.loads((D/'NORMAL86_SOURCE_BINDING_ACTUAL.json').read_bytes())
  model=sources[key]['models'][key];final=model['final'];newname=c['source_filename'];assert final['SHA']==binding['source_SHA']
  actual=Path(final['local_path']);assert actual.is_file() and actual.stat().st_size==final['bytes'];shutil.copyfile(actual,D/('job0/source/'+newname))
  for name in ('three_slot_common_v1.py','forwarded_original_owner_control_v1.py','three_real_gpu_resource_v1.py'):
   shutil.copyfile(N/'controllers_v2'/name,D/name);item=row(D/name,name);item['original_SHA']=oldrows[name]['SHA'];c['controller_replacements'].append(item)
  shutil.copyfile(N/'controllers_v2/mixed86_protocol_v1.py',D/'mixed86_protocol_v1.py');c['controller_additions']=[row(D/'mixed86_protocol_v1.py','mixed86_protocol_v1.py')]
  task=json.loads((D/'job0/TASK.json').read_bytes());task.update(id=N.name+'_'+key,key=key,normal86_continuation=True,source_SHA=final['SHA'],source_filename=newname,source_Adamstep=model['Adam'],GPU_UUID=('GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e' if key=='h1' else 'GPU-c27eecbd-6838-7290-1cd2-37e34522213d'),execution_backend=('source210' if key=='h1' else 'target72'),policy_hz=(100 if key=='h1' else 50),source_policy_hz=(100 if key=='h1' else 50),source_owned_updates=model['updates'],source_owned_completed_updates=model['updates'],exact_closed_source_updates=model['updates'])
  assert 'manifest_SHA' not in task and 'normal_source_contract_SHA' not in task
  (D/'job0/TASK.json').write_text(json.dumps(task,indent=2),'utf8');item=row(D/'job0/TASK.json','job0/TASK.json');item['original_SHA']=oldrows['job0/TASK.json']['SHA'];c['metadata_replacements']=[item]
  c['actual_installed86_SDK_CPU']=False;c['root_payload_prepared_not_GO']=True
  (D/'NORMAL86_SOURCE_CONTRACT_ACTUAL.json').write_text(json.dumps(c,indent=2),'utf8')
  rows=copy.deepcopy(oldrows)
  for item in c['overlay_files']:rows[item['relative']]=item
  for item in c['controller_replacements']+c['metadata_replacements']:rows[item['relative']]={k:item[k] for k in ('relative','bytes','SHA')}
  for item in c['controller_additions']:rows[item['relative']]=item
  rows['NORMAL86_SOURCE_CONTRACT_ACTUAL.json']=row(D/'NORMAL86_SOURCE_CONTRACT_ACTUAL.json','NORMAL86_SOURCE_CONTRACT_ACTUAL.json');rows['job0/source/'+newname]=dict(relative='job0/source/'+newname,bytes=final['bytes'],SHA=final['SHA'])
  m.update(source_SHA=final['SHA'],source_filename=newname,source_Adamstep=model['Adam'],files=[rows[k] for k in sorted(rows)])
  (D/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(m,indent=2),'utf8')
  spec=copy.deepcopy((q83 if key=='h1' else q85)['specs'][key]);spec.update(normal86_continuation=True,source_SHA=final['SHA'],source_filename=newname,source_Adamstep=model['Adam'],manifest_SHA=H(D/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),normal_source_contract_SHA=H(D/'NORMAL86_SOURCE_CONTRACT_ACTUAL.json'),owner_authority_generation='MOD4_SINGLE_WRITER72_20261026',previous_runtime_root=(str(Path(final['path']).parents[2]).replace('\\','/')),previous_exit_kind='node')
  if key=='h1':spec['owner_control_dependency_binding_SHA']=H(D/'OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json')
  sp=importlib.util.spec_from_file_location('local_normal86_'+key,D/'normal86_source_guard_v1.py');guard=importlib.util.module_from_spec(sp);sp.loader.exec_module(guard)
  checked=guard.check_payload(D,spec,verify_model_bytes=False)
  results[key]=dict(passed=checked['passed'],payload=str(D),root=('/mnt/mod4_linux_durable_20261013/H1step270_three_gpu_native_cont_2610v86b/h1' if key=='h1' else '/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_three_gpu_native_cont_2610v86b/recovery'),spec=spec,source=final,original_manifest_SHA=H(donor/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),new_manifest_SHA=spec['manifest_SHA'],no_actual_target_SDK_or_GO=True)
 with (R/'NORMAL86B_H1_E3_EXACT_PAYLOADS_LOCAL_NONMODEL_SOURCE_PREPARED_ACTUAL.json').open('x',encoding='utf8') as stream:json.dump(dict(epoch=time.time(),passed=True,roles=results,no_model_load_or_local_model_hash=True,no_remote_or_GO=True),stream,indent=2)
 print(json.dumps({'normal_payloads_prepared':list(results),'no_GO':True}))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('NORMAL86B_PAYLOAD_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as stream:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_remote_or_runtime_or_budget_change=True,no_retry_same_payload_root=True),stream,indent=2)
  raise

from pathlib import Path
import ast,copy,hashlib,json,shutil,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;P=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86_20261026';R=N/'reports';R.mkdir(exist_ok=True);D=N/'payloads/e2'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def row(p,r):return dict(relative=r,bytes=p.stat().st_size,SHA=H(p))
def main():
 assert not D.exists();D.mkdir(parents=True);old=P/'payloads/e2';m=json.loads((old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());before=copy.deepcopy(m)
 for item in m['files']:
  src=old/item['relative'];dst=D/item['relative'];assert src.is_file() and src.stat().st_size==item['bytes'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 shutil.copytree(P/'controllers_v2',N/'controllers_v2')
 for path in (N/'controllers_v2/mixed86_protocol_v1.py',D/'mixed86_protocol_v1.py'):
  raw=path.read_bytes().decode('utf8');assert raw.count("NAMESPACE='H1step270_three_gpu_native_cont_2610v86'")==1;path.write_bytes(raw.replace("NAMESPACE='H1step270_three_gpu_native_cont_2610v86'","NAMESPACE='H1step270_three_gpu_native_cont_2610v86b'").encode())
 target=D/'target_native86_source_sdk_cpu_review_v1.py';raw=target.read_bytes();text=raw.decode();anchor="sys.path[:0] = [str(B), str(B / 'source')]";assert text.count(anchor)==1
 changed=text.replace(anchor,"sys.path[:0] = [str(B), str(B / 'source'), str(B / 'source/sm_deps')]",1);target.write_bytes(changed.encode())
 # The only CPU entry change is an extra already-pinned dependency import path.
 normalized=changed.replace("sys.path[:0] = [str(B), str(B / 'source'), str(B / 'source/sm_deps')]",anchor,1)
 assert ast.dump(ast.parse(normalized),include_attributes=False)==ast.dump(ast.parse(text),include_attributes=False)
 task_path=D/'job0/TASK.json';task=json.loads(task_path.read_bytes());task['id']=N.name+'_e2';task_path.write_text(json.dumps(task,indent=2),'utf8')
 contract_path=D/'NATIVE86_SOURCE_CONTRACT_ACTUAL.json';c=json.loads(contract_path.read_bytes());old_cpu=hashlib.sha256(raw).hexdigest();new_cpu=H(target)
 for item in c['overlay_files']:
  if item['relative']==target.name:item.update(bytes=target.stat().st_size,SHA=new_cpu)
 replaced=[]
 for key,value in c['candidate_pins'].items():
  if value==old_cpu:c['candidate_pins'][key]=new_cpu;replaced.append(key)
 assert len(replaced)==1
 for item in c['controller_additions']:
  if item['relative']=='mixed86_protocol_v1.py':item.update(bytes=(D/item['relative']).stat().st_size,SHA=H(D/item['relative']))
 for item in c['metadata_replacements']:
  if item['relative']=='job0/TASK.json':item.update(bytes=task_path.stat().st_size,SHA=H(task_path))
 c.update(source_review_revision=6,preGO86_actual_CPU_rich_import_error_preserved=True,CPU_path_only_fix_in_new_namespace=True)
 contract_path.write_text(json.dumps(c,indent=2),'utf8')
 for item in m['files']:
  if item['relative'] in (target.name,'mixed86_protocol_v1.py','job0/TASK.json','NATIVE86_SOURCE_CONTRACT_ACTUAL.json'):item.update(bytes=(D/item['relative']).stat().st_size,SHA=H(D/item['relative']))
 manifest_path=D/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';manifest_path.write_text(json.dumps(m,indent=2),'utf8')
 q=json.loads((P/'reports/NATIVE86_FINALIZED_LOCAL_PAYLOAD_V5_SOURCE_PREPARED_ACTUAL.json').read_bytes());q.update(payload=str(D),root='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_three_gpu_native_cont_2610v86b/e2',source_review_revision=6,previous_failed_preGO_namespace='H1step270_three_gpu_native_cont_2610v86/e2')
 q['spec'].update(manifest_SHA=H(manifest_path),native_source_contract_SHA=H(contract_path),candidate_pins=c['candidate_pins'])
 with (R/'NATIVE86B_FINALIZED_LOCAL_PAYLOAD_V6_SOURCE_PREPARED_ACTUAL.json').open('x',encoding='utf8') as out:json.dump(q,out,indent=2)
 for name in ('OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json','REVERSE210_OWNER72_TRANSPORT_CPU_FINITE_RETURNED_ACTUAL.json','EXPANDED210_OWNER72_DEPS_V2_ACTUAL_CPU_FINITE_RETURNED_ACTUAL.json'):
  shutil.copyfile(P/'reports'/name,R/name)
 with (R/'NATIVE86B_CPU_IMPORT_PATH_ONLY_FIX_SOURCE_REVIEW_ACTUAL.json').open('x',encoding='utf8') as out:json.dump(dict(epoch=time.time(),source_only=True,previous_original_CPU_error='ModuleNotFoundError rich after source/bootstrap load and RSL roundtrip, preGO with no fee',old_CPU_source_SHA=old_cpu,new_CPU_source_SHA=new_cpu,exact_AST_path_insertion_only=True,candidate_pin_keys_changed=replaced,old_payload_manifest_SHA=H(old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),new_manifest_SHA=H(manifest_path),no_reward_physics_model_or_optimizer_changes=True,no_model_hash_or_load=True,no_overwrite_original86_target_or_errors=True,no_GO=True),out,indent=2)
 print(json.dumps({'new_namespace':'86b','CPU_entry_only_dependency_path_fix':True,'no_GO':True}))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('ORIGINAL_86B_PREP_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as out:json.dump(dict(error=traceback.format_exc(),no_remote_or_training=True),out,indent=2)
  raise

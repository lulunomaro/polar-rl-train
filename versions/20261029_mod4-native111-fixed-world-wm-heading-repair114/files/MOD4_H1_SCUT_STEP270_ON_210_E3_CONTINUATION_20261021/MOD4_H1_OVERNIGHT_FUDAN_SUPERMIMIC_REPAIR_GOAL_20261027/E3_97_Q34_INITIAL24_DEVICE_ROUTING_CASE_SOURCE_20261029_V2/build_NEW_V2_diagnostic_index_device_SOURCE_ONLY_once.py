"""New namespace, only diagnostic index-device route + bound metadata/readers."""
from pathlib import Path
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent;L=B.parent
OLD=L/'E3_97_Q34_INITIAL24_ORIGINAL_QUERY_CASE_SOURCE_20261029_V1'
OLDJOB='/mnt/mod4_linux_durable_20261013/MOD4_E3_ADAPTED97_Q34_INITIAL24_ORIGINAL_QUERY_20261029v1/e3'
JOB='/mnt/mod4_linux_durable_20261013/MOD4_E3_ADAPTED97_Q34_INITIAL24_DEVICE_ROUTE_20261029v2/e3'
K0='MOD4_E3_ADAPTED97_SOURCE210_Q34_INITIAL24_ORIGINAL_QUERY_V1';K='MOD4_E3_ADAPTED97_SOURCE210_Q34_INITIAL24_DEVICE_ROUTE_V2'
IDX0='FROZEN_E3_Q34_INITIAL24_COMPLETE_SOURCE_INDEX_V1.json';IDX='FROZEN_E3_Q34_INITIAL24_DEVICE_ROUTE_COMPLETE_SOURCE_INDEX_V2.json'
MF='E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json';HOOK='e3_declared_fall_existing_query_observer_v1.py'
WORK='evaluate_E3_adapted97_source210_initial24_original_queries_once_v1.py'
operations=[]
def H(b):return hashlib.sha256(b).hexdigest()
def put(n,v):
 with (B/n).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2)
def write(n,b):
 with (B/n).open('xb') as f:f.write(b)
def change(s,a,b,count=1):
 assert s.count(a)==count,(a,s.count(a),count);operations.append(dict(old=a,new=b,count=count));return s.replace(a,b)
def main():
 m=json.loads((OLD/MF).read_bytes());copy_names={Path(row['local_path']).name for row in m['files'] if Path(row['local_path']).parent==OLD}
 copy_names|={'install_E3_source210_frozen_recipe_metadata_detach_UNUSED_once_v4_exactEntryReceipt.py','run_E3_source210_readonly_v4.py','read_E3_source210_FIRST_native24_recipe_queue_UNUSED_once_v4.py','collect_E3_source210_TERMINAL_recipe_fulltext_UNUSED_once_v4.py','AUTH72_CURRENT_KNOWN_OWNER_READONLY_CODE_v1.py','PRE210_UNUSED_MOUNT_LIGHT_RESOURCE_CODE_v1.py','remote_E3_source210_verify_metadata_CPU_and_detach_v4_exactEntryReceipt.py'}
 perfile=[]
 for name in sorted(copy_names):
  source=(OLD/name).read_bytes();s=source.decode();start=len(operations)
  for a,b in ((OLDJOB,JOB),(K0,K),(IDX0,IDX)):
   if a in s:s=change(s,a,b,s.count(a))
  if name==HOOK:
   defs="""def diagnostic_select(t,value,index):
    # Index dtype follows the index, never the floating target tensor.
    assert t.is_tensor(index) and index.dtype in (t.long,t.bool)
    return value[index.to(device=value.device,dtype=index.dtype)]

def diagnostic_outside_actual_limits(q,limits):
    # This copy is diagnostic-only; neither original cache q nor limits changes.
    compare_q=q.to(device=limits.device)
    return (compare_q[None]<limits[:,:,0])|(compare_q[None]>limits[:,:,1])

"""
   s=change(s,'class ExistingQueryObserver:',defs+'class ExistingQueryObserver:')
   s=change(s,'self.e.recovery.age[self.ids]','diagnostic_select(self.t,self.e.recovery.age,self.ids)')
   s=change(s,'self.e.recovery.recipe[selected]','diagnostic_select(self.t,self.e.recovery.recipe,selected)')
   s=change(s,'self.gas_limits[selected]','diagnostic_select(self.t,self.gas_limits,selected)')
   s=change(s,'((q[None]<limits[:,:,0])|(q[None]>limits[:,:,1]))','diagnostic_outside_actual_limits(q,limits)')
   s=change(s,'c._quat[recipe]','diagnostic_select(self.t,c._quat,recipe)')
   s=change(s,'c._minimum[recipe]','diagnostic_select(self.t,c._minimum,recipe)',2)
   s=change(s,'self.e.scene.env_origins[selected,2]','diagnostic_select(self.t,self.e.scene.env_origins,selected)[:,2]')
   s=change(s,'self.e._rescue_reset_q[selected]','diagnostic_select(self.t,self.e._rescue_reset_q,selected)')
   s=change(s,'observer.t.isin(ids,observer.ids)','observer.t.isin(ids,observer.ids.to(device=ids.device,dtype=ids.dtype))',2)
   s=change(s,'q30=q[mask],dq30=dq[mask]','q30=diagnostic_select(observer.t,q,mask),dq30=diagnostic_select(observer.t,dq,mask)')
   s=change(s,'root13=state[mask]','root13=diagnostic_select(observer.t,state,mask)')
   s=change(s,'value=result[observer.ids]','value=diagnostic_select(observer.t,result,observer.ids)')
   s=change(s,'pp[ids]','diagnostic_select(self.t,pp,ids)',2)
   s=change(s,'qq[ids]','diagnostic_select(self.t,qq,ids)',2)
   s=change(s,'e.recovery.recipe[ids]','diagnostic_select(self.t,e.recovery.recipe,ids)')
   s=change(s,'e.episode_length_buf[ids]','diagnostic_select(self.t,e.episode_length_buf,ids)')
   s=change(s,'{k:v[ids] for k,v in errors.items()}','{k:diagnostic_select(self.t,v,ids) for k,v in errors.items()}')
  if name=='selected_original_query_API_fixture_v1.py':
   s=change(s,"proof=dict(passed=True", "from diagnostic_device_route_fixture_v2 import run_device_route_fixture\n route_proof=run_device_route_fixture(helper,t)\n proof=dict(device_routing_fresh_CPU_and_label_proxy=route_proof,passed=True")
  if name=='E3_source210_actual_receipts_readonly_CODE_v4.py':
   # Keep the old overall diagnostic gate, but distinguish physical completion.
   container=ast.parse(s);code=next(ast.literal_eval(n.value) for n in container.body if isinstance(n,ast.Assign));before_code=code
   code=change(code,"full=full_coverage(passed_execution,result)","full=full_coverage(passed_execution,result)\nphysical_execution=bool(settled and tt.get('returncode')==0 and tt.get('actual_worker_waited') and not tt.get('deadline_terminated') and passed_native and not errors)\nphysical24=full_coverage(physical_execution,result)")
   code=change(code,'requested24_initial_controls_complete=full,','requested24_initial_controls_complete=full,requested24_controls_physically_completed=physical24,physical24_does_not_imply_diagnostic_valid=True,')
   s='"""V2 original diagnostic gate retained; actual24 physical count separated."""\nCODE='+repr(code)+'\n'
  if name.endswith('.py'):ast.parse(s)
  write(name,s.encode());perfile.append(dict(name=name,source_SHA=H(source),target_SHA=H(s.encode()),operations=operations[start:]))
 newsha=H((B/HOOK).read_bytes())
 p=B/'e3_initial_query_integration_contract_v1.py';old=p.read_bytes();s=old.decode();assert s.count('b7cf6da873ab661563f5b924108f23ca4d36636da8caace4eb1174864bcf2c48')==1;s=s.replace('b7cf6da873ab661563f5b924108f23ca4d36636da8caace4eb1174864bcf2c48',newsha);p.write_bytes(s.encode());perfile.append(dict(name=p.name,source_SHA=H(old),target_SHA=H(s.encode()),operations=[dict(old='b7cf6da873ab661563f5b924108f23ca4d36636da8caace4eb1174864bcf2c48',new=newsha,count=1)],after_initial_namespace_rebase=True))
 contract=json.loads((B/'E3_INITIAL_QUERY_SOURCE_CONTRACT.json').read_bytes());contract.update(hook_SHA=newsha,diagnostic_index_device_routing='target_tensor_device_and_index_original_long_or_bool_dtype',comparison_q_copy_to_limits_device_only=True,actual_V1_native24_passed_diagnostic_failed=True);(B/'E3_INITIAL_QUERY_SOURCE_CONTRACT.json').write_bytes((json.dumps(contract,indent=2)+'\n').encode())
 m['target_root']=m['target_stage']=JOB;m['kind']='E3_97_initial24_original_query_device_route_source_v2';m['source_version']='NEW V2 diagnostic-only index routes; old V1 actual false preserved';m['diagnostic_index_device_routing']=contract['diagnostic_index_device_routing']
 for row in m['files']:
  if Path(row['local_path']).parent==OLD:
   p=B/Path(row['local_path']).name;row.update(local_path=str(p),bytes=p.stat().st_size,SHA=H(p.read_bytes()))
 p=B/'diagnostic_device_route_fixture_v2.py';assert p.is_file();m['files'].append(dict(relative=p.name,local_path=str(p),bytes=p.stat().st_size,SHA=H(p.read_bytes()),index_kind='new_device_route_fresh_CPU_proxy_source'))
 put(MF,m);put('EXACT_V2_DIAGNOSTIC_INDEX_AND_NAMESPACE_SOURCE_INVERSE_OPERATIONS.json',dict(files=perfile,model_NPZ_USD_raw_stat_hash_content_or_SDK_host_GPU_calls=False))
 actualpath=OLD/'reports/E3_SOURCE210_FIRST_ORIGINAL_RETURNED_ACTUAL.json';raw=actualpath.read_bytes();a=json.loads(raw);require=a['passed_first_actual_E3_CUDA_fullrestore_native24_queue'];assert require and not a['passed_original_query_diagnostic'] and a['original_terminal']['returncode']==0
 put('V1_ACTUAL_NATIVE24_PASS_QUERY_DEVICE_ERROR_PRESERVED_EVIDENCE.json',dict(original_report_path=str(actualpath),original_report_bytes=len(raw),original_report_SHA=H(raw),actual24_fullrestore_native24_passed=require,old_reader_requested24_flag_false=a['requested24_initial_controls_complete'],that_flag_combines_diagnostic_not_physical_step_count=True,original_terminal_allout=a['original_terminal_and_allownout_proven'],original_RC=a['original_terminal']['returncode'],original_error_strings=a['original_query_diagnostic']['errors'],saved_error_string_count=len(a['original_query_diagnostic']['errors']),saved_query_records=len(a['original_query_diagnostic']['records']),normal_collector_untouched=True))
 print(json.dumps(dict(source_prepared=True,inputs=len(m['files']),hook_SHA=newsha,target=JOB)))
if __name__=='__main__':
 try:main()
 except BaseException:put('SOURCE_V2_BUILD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),source_only=True));raise

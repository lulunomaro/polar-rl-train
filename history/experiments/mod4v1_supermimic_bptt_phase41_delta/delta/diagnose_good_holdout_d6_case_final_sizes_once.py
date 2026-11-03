"""NEW functional case-FINAL byte/schema diagnosis after actual close.
Never replays an evaluation or changes any production metadata/size predicate.
"""
from pathlib import Path
import sys,json,hashlib,shlex,time
R=Path(__file__).resolve().parent;out=R/'reports/GOOD_HOLDOUT_D6_CASE_FINAL_SIZE_DIAGNOSIS_V1.json';marker=R/'PAPER_ALIGNED_REBUILD_20261103/GOOD_HOLDOUT_D6_CASE_FINAL_SIZE_DIAGNOSIS_STARTED_ONCE.json';assert not out.exists()and not marker.exists();facts=json.loads((R/'reports/GOOD_HOLDOUT_D6_SEED20260929_CLOSED_FAILURE_FACTS_V1.json').read_bytes());e=facts['parent_exit'];assert not facts['passed_closed_execution']and e['all_own_children_waited']and e['errors']==[]and e['original_single_GPU_private_EX_released']and e['original_global_finite_EX_released']and facts['actual_outer_wait']['actual_parent_p_wait_returned']and facts['actual_outer_wait']['returncode']==1;root=facts['root'];config=dict(kind='NEW_GOOD_HOLDOUT_D6_FUNCTIONAL_WHOLE_CASE_BYTE_SIZE_DIAGNOSIS',epoch=time.time(),root=root,purpose='DIAGNOSE_EXACT_FAILED_CASE_JSON_BOUND_AND_FIELD_SIZES_NOT_STATUS_GIT_OR_REGRADING',actual_closed_result_SHA256=facts['closed_result_SHA256'],production_predicates_and_failed_results_unchanged=True)
with marker.open('x',encoding='utf8')as f:json.dump(config,f,indent=2)
code="""from pathlib import Path
import json,hashlib,time
root=Path(ROOT);rows=[]
def size(value,indent=None):return len(json.dumps(value,indent=indent,allow_nan=False).encode())
for role in('CURB_PROTECTED878','SLOPE135'):
 path=root/'cases'/role/'FINAL.json'
 with path.open('rb')as stream:raw=stream.read(8*1024*1024+1)
 assert len(raw)<=8*1024*1024;sha=hashlib.sha256(raw).hexdigest();v=json.loads(raw);before=hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest();fields=sorted([dict(field=k,compact_value_bytes=size(x),indented_value_bytes=size(x,2),type=type(x).__name__,length=len(x)if type(x)in(dict,list,str)else None)for k,x in v.items()],key=lambda x:x['compact_value_bytes'],reverse=True)
 nested={k:sorted([dict(field=n,compact_value_bytes=size(z),type=type(z).__name__,length=len(z)if type(z)in(dict,list,str)else None)for n,z in v[k].items()],key=lambda x:x['compact_value_bytes'],reverse=True)[:15]for k in('fresh_fullDR_before','fresh_fullDR_after','source_cache','metrics')if type(v.get(k))is dict};after=hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest();assert before==after
 rows.append(dict(role=role,path=str(path),physical_file_opens=1,whole_raw_hashes=1,JSON_decodes=1,bytes=len(raw),SHA256=sha,canonical_SHA256=before,input_canonical_unchanged=True,actual_top_fields=len(v),compact_object_bytes=size(v),indented_object_bytes=size(v,2),top_field_sizes=fields[:20],nested_field_sizes=nested,original_case_counts={k:v.get(k)for k in('controls','physics','feedback','actor_calls','optimizer_updates')},original_kind=v.get('kind'),original_passed_execution_flag_not_new_qualification=v.get('passed_execution'),original_env_close_returned=v.get('env_close_returned'),original_262144_limit_exceeded=len(raw)>262144,original_failed_results_regraded=False))
print(json.dumps(dict(epoch=time.time(),kind='ACTUAL_GOOD_CASE_FINAL_BYTE_SCHEMA_DIAGNOSIS_NOT_NEW_QUALIFICATION',roles=rows,original_files_written=0,production_bounds_changed=False,models_raw_trajectory_SDK_C_or_resource_operations=0),indent=2))
""".replace('ROOT',repr(root))
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=120);i.close();stdout=o.read().decode('utf8','replace');stderr=e.read().decode('utf8','replace');rc=o.channel.recv_exit_status();result=dict(config,returncode=rc,stderr=stderr)
 if rc==0:result['receipt']=json.loads(stdout)
 else:result['stdout']=stdout
 with out.open('x',encoding='utf8')as f:json.dump(result,f,indent=2)
 print(json.dumps(result,indent=2));assert rc==0,stderr
finally:c.close()

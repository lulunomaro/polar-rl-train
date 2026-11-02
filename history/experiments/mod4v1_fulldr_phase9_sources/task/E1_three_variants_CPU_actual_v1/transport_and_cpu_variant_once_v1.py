"""Exact savedphysical byte transport and separate actualCPUonce perexplicitvariant.
No SDK/GPUquery/lease/canonical/7b/210 route. Originalsource NEVER overwritten.
"""
from pathlib import Path
import argparse,ast,datetime,hashlib,json,shlex,sys,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;sys.path.insert(0,str(T));from project_connector import connect72
BASE='/home/lc01/Zonglin Li/zonglin2'

def main():
 p=argparse.ArgumentParser();p.add_argument('--variant',choices=['CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE_INDEPENDENT50'],required=True);a=p.parse_args();name=a.variant
 locator=json.loads((B/'THREE_EXACT_SOURCE_PHYSICAL_STAT_V1.json').read_bytes());record=next(x for x in locator['sources'] if x['variant']==name);assert record['exists'];source=Path(record['path']);assert not (B/(name+'_ACTUAL_CPU_LOCATION.json')).exists()
 package=T/'staged_sources'/('E1_'+name+'_40050_MOD4V1_SOURCE_V2');worker=B/'cpu_variant_four_leaf_schema_audit_once_v1.py';pure=package/'runtime/isaac/mod4/e1_four_leaf_migration_v1.py';owner=package/'SAVED_EVIDENCE_ROOTKEY_HELPER_OWNER_MAP_V1.json'
 for p in [worker,pure]:compile(p.read_bytes(),str(p),'exec')
 stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());transportPurpose=name+'_EXACT_ORIGINAL_BYTE_TRANSPORT_'+stamp;cpuPurpose=name+'_COMPLETE_CPU4LEAF_FULLSCHEMA_'+stamp;transport=BASE+'/tasks/'+transportPurpose;cpuRoot=BASE+'/tasks/MOD4V1_'+cpuPurpose;remoteSource=transport+'/'+name+'_ORIGINAL_FULLSOURCE_PRESERVED.pt'
 report=dict(kind='EXPLICIT_VARIANT_TRANSPORT_AND_SEPARATE_ACTUAL_CPU_PURPOSE',variant=name,source_record=record,transport_purpose=transportPurpose,CPU_purpose=cpuPurpose,remote_original_copy=remoteSource,CPU_root=cpuRoot,local_original_byte_reads=0,local_original_SHA_calculations=0,local_decodes=0,SDK_GPUquery_budget_canonical_operations=0);client=sf=None
 try:
  st=source.stat();assert st.st_size==record['expected_bytes'] and st.st_mtime_ns==record['mtime_ns']
  with source.open('rb') as f:raw=f.read();report['local_original_byte_reads']+=1
  sha=hashlib.sha256(raw).hexdigest();report['local_original_SHA_calculations']+=1;assert sha==record['expected_SHA'] and len(raw)==record['expected_bytes']
  client=connect72();sf=client.open_sftp();sf.mkdir(transport)
  with sf.open(remoteSource,'wx') as f:f.write(raw)
  after=source.stat();assert after.st_size==st.st_size and after.st_mtime_ns==st.st_mtime_ns;report.update(original_size_mtime_unchanged=True,remote_transport_written_bytes=sf.stat(remoteSource).st_size);assert report['remote_transport_written_bytes']==len(raw)
  with sf.open(transport+'/TRANSPORT_ACTUAL_RECEIPT.json','wx') as f:f.write(json.dumps(report,indent=2))
  sf.mkdir(cpuRoot)
  for p,n in [(worker,'cpu_worker.py'),(pure,'e1_four_leaf_migration_v1.py'),(owner,'SOURCE_OWNER_MAP.json')]:sf.put(str(p),cpuRoot+'/'+n)
  task=dict(kind='E1_EXPLICIT_VARIANT_ACTUAL_CPU_FOUR_LEAF_ONCE_V1',canonical=name,role=record['role'],purpose=cpuPurpose,source_path=remoteSource,source_SHA=sha,source_bytes=len(raw),transport_receipt=transport+'/TRANSPORT_ACTUAL_RECEIPT.json',no_CUDA_or_SDK_or_NCCL_or_merge=True)
  with sf.open(cpuRoot+'/CPU_TASK.json','wx') as f:f.write(json.dumps(task,indent=2))
  command='env CUDA_VISIBLE_DEVICES='+shlex.quote('')+' '+shlex.quote(BASE+'/run-python.sh')+' -u -B '+shlex.quote(cpuRoot+'/cpu_worker.py')+' --task '+shlex.quote(cpuRoot+'/CPU_TASK.json')
  i,o,e=client.exec_command(command,timeout=240);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();report.update(CPU_returncode=rc,CPU_stdout=stdout,CPU_stderr=stderr)
  outputs={}
  for n in ['CPU_PURPOSE_CONSUMED.json','CPU_FOUR_LEAF_ACTUAL_COMPLETE.json','CPU_COMPLETE_ROOT_AND_NESTED_SCHEMA_OWNER_AUDIT.json','CPU_FOUR_LEAF_ORIGINAL_ERROR.json']:
   try:
    with sf.open(cpuRoot+'/'+n,'rb') as f:data=f.read()
   except OSError as err:
    if getattr(err,'errno',None)==2:continue
    raise
   dest=B/(name+'_'+n)
   with dest.open('xb') as f:f.write(data)
   outputs[n]=json.loads(data)
  report['original_CPU_JSON']=outputs
  assert rc==0 and outputs.get('CPU_FOUR_LEAF_ACTUAL_COMPLETE.json',{}).get('passed') is True and 'CPU_FOUR_LEAF_ORIGINAL_ERROR.json' not in outputs
  result=outputs['CPU_FOUR_LEAF_ACTUAL_COMPLETE.json'];report.update(status='ACTUAL_CPU_FOURLEAF_PASS_ROOT_OWNER_AUDIT_METADATA_PENDING',actual_source_metadata=result['actual_source_metadata'],new_typed_source=result['new_typed_source'],rootkey_diff=result['actual_rootkey_diff'],known_extra_schema=result['known_variant_extra_schema'],unknown_root_or_extra_owner=result['unmapped_root_or_extra_owner'],counts=result['counts'])
  with (B/(name+'_ACTUAL_CPU_LOCATION.json')).open('x',encoding='utf-8') as f:json.dump(dict(CPU_root=cpuRoot,transport_root=transport,new_typed_source=result['new_typed_source'],actual_metadata=result['actual_source_metadata'],rootkey_diff=result['actual_rootkey_diff'],CPU_result_path=str(B/(name+'_CPU_FOUR_LEAF_ACTUAL_COMPLETE.json'))),f,indent=2)
 except BaseException:report.update(status='TRANSPORT_OR_ACTUAL_CPU_OR_READER_ERROR',error=traceback.format_exc());raise
 finally:
  if sf:sf.close()
  if client:client.close()
  dest=T/'reports'/(name+'_CPU_fourleaf_fullschema_actual_'+stamp+'.json');dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ('original_CPU_JSON','CPU_stdout','actual_source_metadata')},ensure_ascii=False,indent=2));print('REPORT',dest)
if __name__=='__main__':main()

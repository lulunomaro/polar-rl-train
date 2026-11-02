"""Independent exact24b byte transport then ONE separately consumed72CPU purpose.
Never alter original, no SDK/GPU/budget/canonical; no repeated selectedsource read.
"""
from pathlib import Path
import ast,datetime,hashlib,json,shlex,sys,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;sys.path.insert(0,str(T));from project_connector import connect72
SOURCE=Path(r'C:\Users\lulu\Desktop\claude\mjcf\MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016\train_payload\job1\source\source.pt');SHA='24b18846fcff1e0b8da7fd478314fca9cd2ed2b97461ca34f65ef5b7c7ff2411';BYTES=17615794;BASE='/home/lc01/Zonglin Li/zonglin2'

def main():
 assert not (B/'SLOPE135_ACTUAL_CPU_LOCATION.json').exists()
 stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());transportPurpose='SLOPE135_EXACT24B_BYTE_TRANSPORT_'+stamp;cpuPurpose='SLOPE135_24B_COMPLETE_CPU_FOUR_LEAF_'+stamp
 remote=BASE+'/tasks/'+transportPurpose;cpuRoot=BASE+'/tasks/MOD4V1_'+cpuPurpose;remoteSource=remote+'/SLOPE135_ORIGINAL24B_PRESERVED_SOURCE.pt'
 report=dict(kind='SLOPE135_EXACT_TRANSPORT_AND_SEPARATE_CPU_PURPOSE',transport_purpose=transportPurpose,CPU_purpose=cpuPurpose,source_path=str(SOURCE),source_SHA=SHA,source_bytes=BYTES,remote_original_copy=remoteSource,CPU_root=cpuRoot,local_original_byte_reads=0,local_original_SHA_calculations=0,local_decodes=0,SDK_GPU_budget_canonical_operations=0);client=sf=None
 try:
  for p in [B/'cpu_four_leaf_typed_once_v1.py',T/'staged_sources/E1_SLOPE135_40050_MOD4V1_SOURCE_V1/runtime/isaac/mod4/e1_four_leaf_migration_v1.py']:compile(p.read_bytes(),str(p),'exec')
  st=SOURCE.stat();assert st.st_size==BYTES
  with SOURCE.open('rb') as f:raw=f.read();report['local_original_byte_reads']+=1
  actual=hashlib.sha256(raw).hexdigest();report['local_original_SHA_calculations']+=1;assert len(raw)==BYTES and actual==SHA
  client=connect72();sf=client.open_sftp();sf.mkdir(remote)
  with sf.open(remoteSource,'wx') as f:f.write(raw)
  after=SOURCE.stat();assert after.st_size==st.st_size and after.st_mtime_ns==st.st_mtime_ns
  report['original_size_mtime_unchanged']=True;report['transport_actual_remote_bytes']=sf.stat(remoteSource).st_size;assert report['transport_actual_remote_bytes']==BYTES
  with sf.open(remote+'/TRANSPORT_ACTUAL_RECEIPT.json','wx') as f:f.write(json.dumps({k:v for k,v in report.items() if k!='CPU_root'},indent=2))
  sf.mkdir(cpuRoot)
  for p,rel in [(B/'cpu_four_leaf_typed_once_v1.py','cpu_four_leaf_typed_once_v1.py'),(T/'staged_sources/E1_SLOPE135_40050_MOD4V1_SOURCE_V1/runtime/isaac/mod4/e1_four_leaf_migration_v1.py','e1_four_leaf_migration_v1.py')]:sf.put(str(p),cpuRoot+'/'+rel)
  task=dict(kind='E1_CANONICAL_ACTUAL_CPU_FOUR_LEAF_ONCE_V1',canonical='SLOPE135',role='E1_SLOPE',purpose=cpuPurpose,source_path=remoteSource,source_SHA=SHA,source_bytes=BYTES,separate_transport_receipt=remote+'/TRANSPORT_ACTUAL_RECEIPT.json',no_SDK_or_GPU=True)
  with sf.open(cpuRoot+'/CPU_TASK.json','wx') as f:f.write(json.dumps(task,indent=2))
  command='env CUDA_VISIBLE_DEVICES='+shlex.quote('')+' '+shlex.quote(BASE+'/run-python.sh')+' -u -B '+shlex.quote(cpuRoot+'/cpu_four_leaf_typed_once_v1.py')+' --task '+shlex.quote(cpuRoot+'/CPU_TASK.json')
  i,o,e=client.exec_command(command,timeout=180);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();report.update(CPU_actual_returncode=rc,CPU_actual_stdout=stdout,CPU_actual_stderr=stderr)
  originals={}
  for n in ['CPU_PURPOSE_CONSUMED.json','CPU_FOUR_LEAF_ACTUAL_COMPLETE.json','CPU_FOUR_LEAF_ORIGINAL_ERROR.json']:
   try:
    with sf.open(cpuRoot+'/'+n,'rb') as f:data=f.read()
   except OSError as error:
    if getattr(error,'errno',None)==2:continue
    raise
   dest=B/('SLOPE135_'+n)
   with dest.open('xb') as f:f.write(data)
   originals[n]=json.loads(data)
  report['original_CPU_JSON']=originals
  assert rc==0 and originals.get('CPU_FOUR_LEAF_ACTUAL_COMPLETE.json',{}).get('passed') is True and 'CPU_FOUR_LEAF_ORIGINAL_ERROR.json' not in originals
  result=originals['CPU_FOUR_LEAF_ACTUAL_COMPLETE.json'];report.update(status='SLOPE135_ACTUAL_CPU_PASS_NO_GPU',actual_source_metadata=result['actual_source_metadata'],new_typed_source=result['new_typed_source'],counts=result['counts'])
  with (B/'SLOPE135_ACTUAL_CPU_LOCATION.json').open('x',encoding='utf-8') as f:json.dump(dict(CPU_root=cpuRoot,transport_root=remote,new_typed_source=result['new_typed_source'],actual_metadata=result['actual_source_metadata']),f,indent=2)
 except BaseException:report.update(status='SLOPE135_TRANSPORT_OR_CPU_ERROR',error=traceback.format_exc());raise
 finally:
  if sf:sf.close()
  if client:client.close()
  dest=T/'reports'/('SLOPE135_transport_CPU_actual_'+stamp+'.json');dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ('CPU_actual_stdout','original_CPU_JSON')},ensure_ascii=False,indent=2));print('REPORT',dest)
if __name__=='__main__':main()

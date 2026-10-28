"""Single local finite, one86 stdin ingress, alternating closed source/target SSH."""
from pathlib import Path
import argparse,hashlib,importlib.util,io,json,re,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';PRODUCER='c0d830df0635917f199f3c5e3a3498b7934eb57355dfb24d567eeb99349f7c36'
DOWNLOAD=B/'download_verified_runtime_chunks_to_F_resume128_bounded_batch_once_v2.py';UPLOAD=B/'upload_verified_F_runtime_batch_to86_four_channels_stdin_once_v2.py'
REPORT=B.parent/'NEW_HOST_PROVEN72_RUNTIME_BUNDLE_READONLY_COLLECTION_SOURCE_V1/reports/PROVEN72_RUNTIME_EXPORT_FIRST_COLLECTION_FOOTPRINT_ABI_ACTUAL.json'
def put(name,value):
 R.mkdir(parents=True,exist_ok=True)
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
def emit(**values):
 v=dict(epoch=time.time(),**values)
 with (R/'SERIAL_RUNTIME_DRIVER_PROGRESS_ACTUAL.jsonl').open('a') as f:f.write(json.dumps(v)+chr(10))
 print(json.dumps(v),flush=True)
def module(name,path,want):
 assert hashlib.sha256(path.read_bytes()).hexdigest()==want
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def completed(producer):
 done=set()
 for p in R.glob('BATCH_*_TRIPLE_HOST_COMPLETE_ACTUAL.json'):
  v=json.loads(p.read_bytes());row=v['receiver'];match=re.fullmatch('runtime72_chunk([0-9]{4})[.]gz',Path(row['path']).name)
  if not match:continue
  i=int(match[1]);assert i<len(producer['chunks']) and row['producer_SHA']==PRODUCER and row['SHA']==producer['chunks'][i]['SHA'] and row['postcopy_receiver_full_SHA'] and v['source_Windows_receiver_full_SHA_equal'];done.add(i)
 return done
def main():
 p=argparse.ArgumentParser();p.add_argument('--start-chunk',type=int,default=1);a=p.parse_args();assert a.start_chunk>=1
 source=json.loads(REPORT.read_bytes());producer=source['producer'];assert source['bundle_passed'] and source['all_original_recorded_out'] and producer['producer_SHA']==PRODUCER
 done=completed(producer);assert all(i in done for i in range(a.start_chunk)),'prior prefix not receiver-verified; no network or stdin'
 ident='SERIAL_RUNTIME_DRIVER_FROM_'+str(a.start_chunk).zfill(4);put(ident+'_ENTERED_BEFORE_STDIN_ACTUAL.json',dict(epoch=time.time(),producer_SHA=PRODUCER,start_chunk=a.start_chunk,maximum_after_stdin_seconds=1800,reserved_seconds_before_new_source_target_pair=480,each_source_or_upload_cap=240,source_single_SFTP_prefetch128=True,target_one_Transport_max4_SFTP_channels=True,secret_single_STDIN_memory_only=True,no_GPU_model_or_account=True))
 print('READY_FOR_SINGLE_STDIN_JSON',flush=True);req=json.loads(sys.stdin.readline());assert set(req)=={'host','username','password'} and req['host']=='10.50.0.86' and req['username']=='robemo';secret=req.pop('password');deadline=time.monotonic()+1800;start=time.monotonic();next_chunk=a.start_chunk;phase='load_sources';original_stdin=sys.stdin;original_argv=sys.argv;stages=[];error=None
 try:
  dl=module('owned_runtime_download128',DOWNLOAD,'4ff9cf239f4a9cfc8b083e7d06614fced4ec166b36a9aa896c0f7722fbf07999');up=module('owned_runtime_upload_four_channels',UPLOAD,'234bbe10640ea47abe2adf5d32f129b99d3981cb0fc3582ae2887c001de50009')
  while next_chunk<len(producer['chunks']):
   done=completed(producer)
   while next_chunk in done:next_chunk+=1
   if next_chunk>=len(producer['chunks']):break
   remaining=deadline-time.monotonic()
   if remaining<480:emit(stage='PENDING_ORIGINAL_DRIVER_RESERVE',remaining_seconds=remaining,next_chunk=next_chunk);break
   count=min(4,len(producer['chunks'])-next_chunk);batch='BATCH_'+str(next_chunk).zfill(4)+'_'+str(count).zfill(2)+'_T128';receipt=R/(batch+'_RETURNED_ACTUAL.json')
   phase='download_'+batch
   if not receipt.exists():
    emit(stage='SOURCE72_BATCH_START',first=next_chunk,count=count,remaining_seconds=remaining);sys.argv=[str(DOWNLOAD),'--first-chunk',str(next_chunk),'--count',str(count)]
    try:dl.main()
    finally:sys.argv=original_argv
   value=json.loads(receipt.read_bytes());assert value['passed'] and value['source_connection_closed_in_finally'] and value['producer_SHA']==PRODUCER and len(value['chunks'])==count
   emit(stage='SOURCE72_RETURNED_AND_CLOSED_BEFORE86',first=next_chunk,count=count)
   phase='upload_'+batch;buffer=io.StringIO(json.dumps(dict(req,password=secret)))
   sys.argv=[str(UPLOAD),'--download-receipt',str(receipt)];sys.stdin=buffer
   try:
    emit(stage='TARGET86_BATCH_USES_MEMORY_STDIN_NO_FURTHER_INGRESS',first=next_chunk,count=count);up.main()
   finally:
    sys.stdin=original_stdin;sys.argv=original_argv;buffer.seek(0);buffer.truncate(0);buffer.close()
   returned=R/(batch+'_UPLOAD86P4_RETURNED_ACTUAL.json');target=json.loads(returned.read_bytes());assert target['passed'] and target['producer_SHA']==PRODUCER
   done=completed(producer);assert all(i in done for i in range(next_chunk,next_chunk+count));stages.append(dict(first=next_chunk,count=count,download_receipt=str(receipt),upload_receipt=str(returned)));next_chunk+=count
   emit(stage='TARGET86_RETURNED_AND_CLOSED_BEFORE_NEXT72',next_chunk=next_chunk,verified_chunks=len(done),total_chunks=len(producer['chunks']),elapsed_seconds=time.monotonic()-start)
 except BaseException:
  error=traceback.format_exc()
  if secret:error=error.replace(secret,'[REDACTED]')
  put(ident+'_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),phase=phase,error=error,failed_no_automatic_retry=True,partial_and_original_reports_preserved=True))
 finally:
  secret=None;sys.stdin=original_stdin;sys.argv=original_argv
 done=completed(producer);complete=len(done)==len(producer['chunks']);result=dict(epoch=time.time(),passed=error is None,all_chunks_receiver_verified=complete,verified_chunks=sorted(done),total_chunks=len(producer['chunks']),next_pending_chunk=next((i for i in range(len(producer['chunks'])) if i not in done),None),producer_SHA=PRODUCER,stages=stages,error=error,elapsed_after_single_stdin_seconds=time.monotonic()-start,actual_finite_returned=True,source_and_target_connections_sequential_after_stage_finally=True,no_password_in_argv_disk_reports_or_output=True,packages_not_yet_extracted_or_SDK_admitted=True,no_GPU_or_budget_or_other_writer=True)
 put(ident+'_RETURNED_ACTUAL.json',result);emit(stage='DRIVER_RETURNED',passed=result['passed'],all_chunks_receiver_verified=complete,verified_chunks=len(done),next_pending_chunk=result['next_pending_chunk'])
 if error:raise SystemExit(1)
if __name__=='__main__':
 try:main()
 except BaseException:
  if not isinstance(sys.exc_info()[1],SystemExit):put('SERIAL_DRIVER_PRE_ENTRY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True))
  raise

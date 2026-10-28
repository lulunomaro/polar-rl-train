"""One86 connection only, after source download exited. Secret only stdin memory."""
from pathlib import Path
import argparse,hashlib,json,os,shlex,socket,stat,sys,time,traceback
import paramiko,threading,concurrent.futures
EMIT_LOCK=threading.Lock()
B=Path(__file__).resolve().parent;R=B/'reports';L=B.parent
ROOT='/data/robemo/polar-rl-train';TARGET=ROOT+'/runtime_migrations/proven72_20261028_v1';LOCAL=Path('F:/MOD4_PROVEN72_RUNTIME_TRANSFER_20261028_V1')
PIN='8adc87f3e75eb307a2429fa97b68761e09c0636b0eea684c71894438757c788b'
PRODUCER_SHA='c0d830df0635917f199f3c5e3a3498b7934eb57355dfb24d567eeb99349f7c36'
SOURCE_REPORT=L/'NEW_HOST_PROVEN72_RUNTIME_BUNDLE_READONLY_COLLECTION_SOURCE_V1/reports/PROVEN72_RUNTIME_EXPORT_FIRST_COLLECTION_FOOTPRINT_ABI_ACTUAL.json'
PRE=r'''
from pathlib import Path
import json,shutil,time
R=Path('/data/robemo/polar-rl-train');B=R/'runtime_migrations/proven72_20261028_v1'
assert R.resolve()==R and not R.is_symlink();m=json.loads((R/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_bytes());assert m['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700' and m['host']=='10.50.0.86' and m['username']=='robemo' and m['authorized_root']==str(R)
assert B.resolve().is_relative_to(R);marker=B/'OWN_PROVEN72_RUNTIME_RECEIVER.json'
if B.exists():assert B.resolve()==B and not B.is_symlink() and json.loads(marker.read_bytes())['producer_SHA']==v['producer_SHA']
else:
 B.mkdir(parents=True,mode=0o700)
 with marker.open('x') as f:json.dump(dict(root=str(B),source='USER requested exact proven72 environment snapshot',producer_SHA=v['producer_SHA'],no_global_changes=True),f,indent=2)
C=B/'chunks';C.mkdir(exist_ok=True);assert C.resolve()==C and not C.is_symlink()
free=shutil.disk_usage(R).free;required=v['compressed_bytes']+v['uncompressed_input_bytes']+1024**3;assert free>required,'actual new86 disk capacity insufficient'
for row in v['files']:
 assert row['name'].startswith('runtime72_chunk') and row['name'].endswith('.gz') and '/' not in row['name'] and '\\' not in row['name']
 assert not (C/row['name']).exists() and not (C/(row['name']+'.partial')).exists()
print(json.dumps(dict(passed=True,epoch=time.time(),root=str(B),actual_free_bytes=free,required_capacity_bytes=required,no_Torch_SDK_GPU_or_training=True)))
'''
VERIFY=r'''
from pathlib import Path
import hashlib,json,os,time
B=Path('/data/robemo/polar-rl-train/runtime_migrations/proven72_20261028_v1');assert B.resolve()==B
assert json.loads((B/'OWN_PROVEN72_RUNTIME_RECEIVER.json').read_bytes())['producer_SHA']==v['producer_SHA']
row=v['row'];p=B/'chunks'/(row['name']+'.partial');target=B/'chunks'/row['name'];assert p.resolve()==p and not p.is_symlink() and not target.exists() and p.stat().st_size==row['bytes']
with p.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
assert digest==row['SHA'];os.rename(p,target)
receipt=dict(passed=True,epoch=time.time(),producer_SHA=v['producer_SHA'],path=str(target),bytes=row['bytes'],SHA=digest,postcopy_receiver_full_SHA=True,no_package_activation_or_global_write=True)
with (B/('CHUNK_'+row['name']+'_RECEIVER_ACTUAL.json')).open('x') as f:json.dump(receipt,f,indent=2)
print(json.dumps(receipt))
'''
def put(n,v):
 R.mkdir(parents=True,exist_ok=True)
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def emit(v):
 with EMIT_LOCK:
  with (R/'UPLOAD86P4_PROGRESS_ACTUAL.jsonl').open('a') as f:f.write(json.dumps(v)+chr(10))
  print(json.dumps(v),flush=True)
def main():
 R.mkdir(parents=True,exist_ok=True);p=argparse.ArgumentParser();p.add_argument('--download-receipt',type=Path,required=True);a=p.parse_args();dr=a.download_receipt.resolve();assert dr.is_relative_to(R.resolve()) and dr.name.startswith('BATCH_') and dr.name.endswith('_RETURNED_ACTUAL.json')
 download=json.loads(dr.read_bytes());assert download['passed'] and download['actual_finite_returned'] and download['source_connection_closed_in_finally'];rows=download['chunks'];assert 1<=len(rows)<=4
 source_raw=SOURCE_REPORT.read_bytes();source=json.loads(source_raw);assert source['bundle_passed'] and source['all_original_recorded_out'];producer=source['producer'];assert producer['producer_SHA']==download['producer_SHA']==PRODUCER_SHA
 inputs=[x for x in source['full_original_texts'] if x['path'].endswith('/PROVEN72_RUNTIME_EXPORT_INPUT_SCOPE_ACTUAL.json')];assert len(inputs)==1 and inputs[0]['stable'];input_bytes=json.loads(inputs[0]['UTF8'])['logical_input_bytes']
 files=[]
 for row in rows:
  p=Path(row['local_path']).resolve();assert p.parent==LOCAL.resolve() and p.name=='runtime72_chunk'+str(row['chunk_index']).zfill(4)+'.gz' and p.stat().st_size==row['bytes'];assert row['twohost_producer_and_received_full_SHA'];files.append(dict(name=p.name,local_path=str(p),bytes=row['bytes'],SHA=row['SHA']))
 batch=dr.name[:-len('_RETURNED_ACTUAL.json')];put(batch+'_UPLOAD86P4_ENTERED_BEFORE_STDIN_ACTUAL.json',dict(epoch=time.time(),local_download_receipt=str(dr),source_producer_SHA=producer['producer_SHA'],files=files,maximum_after_stdin_seconds=240,no_source72_connection=True,secret_only_STDIN_memory=True));print('READY_FOR_SINGLE_STDIN_JSON',flush=True)
 req=json.loads(sys.stdin.readline());assert set(req)=={'host','username','password'} and req['host']=='10.50.0.86' and req['username']=='robemo';secret=req.pop('password');t=None;sf=None;deadline=time.monotonic()+240
 def left():
  seconds=deadline-time.monotonic();assert seconds>0,'original upload finite deadline';return min(25,seconds)
 def run(code,args):
  ch=t.open_session(timeout=15);ch.exec_command('/usr/bin/python3 -B -c '+shlex.quote("import sys,json;v=json.loads(sys.stdin.readline());exec(v['code'])"));ch.settimeout(left());inp=ch.makefile_stdin('wb');inp.write((json.dumps(dict(args,code=code))+'\n').encode());inp.flush();ch.shutdown_write();out=ch.makefile('rb').read().decode();err=ch.makefile_stderr('rb').read().decode();rc=ch.recv_exit_status();assert rc==0,(err,out);return json.loads(out)
 try:
  sock=socket.create_connection((req['host'],22),timeout=15);t=paramiko.Transport(sock);t.banner_timeout=15;t.auth_timeout=15;t.start_client(timeout=15);actual=hashlib.sha256(t.get_remote_server_key().asbytes()).hexdigest();assert actual==PIN,'PIN_MISMATCH_BEFORE_AUTH';t.auth_password(req['username'],secret,fallback=False);secret=None
  pre=run(PRE,dict(producer_SHA=producer['producer_SHA'],compressed_bytes=producer['compressed_bytes'],uncompressed_input_bytes=input_bytes,files=files));put(batch+'_UPLOAD86P4_SCOPE_DISK_ADMISSION_ACTUAL.json',pre);copied=[];stop=threading.Event();errors=[]
  def send(row):
   channel=None;count=0;h=hashlib.sha256();last=0;remote=TARGET+'/chunks/'+row['name']+'.partial'
   try:
    assert not stop.is_set(),'another owned channel failed; later writes stopped'
    channel=paramiko.SFTPClient.from_transport(t,window_size=64*1024**2,max_packet_size=32768);channel.get_channel().settimeout(left());p=Path(row['local_path']);before=p.stat()
    with p.open('rb') as src,channel.open(remote,'wx') as dst:
     dst.set_pipelined(True)
     while True:
      assert not stop.is_set(),'another owned channel failed; later writes stopped'
      channel.get_channel().settimeout(left());data=src.read(1024**2)
      if not data:break
      dst.write(data);h.update(data);count+=len(data)
      if time.monotonic()-last>=20:emit(dict(stage='ACTUAL_F_TO86_SAME_TRANSPORT_PARALLEL_CHANNEL',filename=row['name'],written_bytes=count,expected_bytes=row['bytes'],epoch=time.time(),maximum_channels=4));last=time.monotonic()
    after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns) and count==row['bytes'] and h.hexdigest()==row['SHA'];return row
   except BaseException:
    stop.set();put(batch+'_'+row['name']+'_UPLOAD86P4_CHANNEL_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),receiver_partial_path=remote,logical_bytes_written=count,local_stream_prefix_SHA=h.hexdigest(),no_retry_delete_or_other_process_signal=True));raise
   finally:
    if channel:channel.close()
  timer=threading.Timer(max(0.,deadline-time.monotonic()),t.close);timer.daemon=True;timer.start()
  try:
   with concurrent.futures.ThreadPoolExecutor(max_workers=min(4,len(files))) as pool:
    pending=[pool.submit(send,row) for row in files]
    for future in concurrent.futures.as_completed(pending):
     try:future.result()
     except BaseException as error:errors.append(str(error));stop.set()
   assert not errors,'owned parallel upload failed; all channels joined: '+repr(errors)
   for row in files:
    got=run(VERIFY,dict(producer_SHA=producer['producer_SHA'],row={k:row[k] for k in ('name','bytes','SHA')}));copied.append(got);put(batch+'_'+row['name']+'_TRIPLE_HOST_COMPLETE_ACTUAL.json',dict(download=next(x for x in rows if Path(x['local_path']).name==row['name']),receiver=got,source_Windows_receiver_full_SHA_equal=True))
  finally:timer.cancel()
  put(batch+'_UPLOAD86P4_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,actual_finite_returned=True,producer_SHA=producer['producer_SHA'],receiver_chunks=copied,packages_not_yet_extracted_or_activated=True,SDK_CUDA_or_training_not_proved=True,no_source72_connection_or_global_environment_write=True));emit(dict(passed_upload_only=True,batch=batch,files=len(copied),bytes=sum(x['bytes'] for x in copied),SDK_ready=False))
 except BaseException as e:
  message=str(e)
  if secret:message=message.replace(secret,'[REDACTED]')
  put(batch+'_UPLOAD86P4_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error_type=type(e).__name__,error=message,source_and_receiver_partial_bytes_preserved=True,no_automatic_retry_delete_or_overwrite=True));raise
 finally:
  secret=None
  if sf:sf.close()
  if t:t.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('UPLOAD_ENTRY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise

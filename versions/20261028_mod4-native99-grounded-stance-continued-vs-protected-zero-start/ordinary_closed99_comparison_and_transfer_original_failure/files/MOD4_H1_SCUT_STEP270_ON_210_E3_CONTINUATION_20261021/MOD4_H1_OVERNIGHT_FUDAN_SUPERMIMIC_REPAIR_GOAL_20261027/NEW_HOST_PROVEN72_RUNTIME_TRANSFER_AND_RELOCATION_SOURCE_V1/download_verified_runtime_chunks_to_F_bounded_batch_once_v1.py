"""Source72 -> new F: artifact staging only. No86 session, GPU or package install."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,importlib.util,json,os,shutil,socket,stat,sys,time,traceback
import paramiko
B=Path(__file__).resolve().parent;R=B/'reports';L=B.parent;T=L.parent;W=T.parent
REMOTE='/home/lc01/Zonglin Li/zonglin2/runtime_exports/MOD4_PROVEN72_RUNTIME_FOR86_20261028_V1'
LOCAL=Path('F:/MOD4_PROVEN72_RUNTIME_TRANSFER_20261028_V1');PIN='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
PRODUCER_SHA='c0d830df0635917f199f3c5e3a3498b7934eb57355dfb24d567eeb99349f7c36'
REPORT=L/'NEW_HOST_PROVEN72_RUNTIME_BUNDLE_READONLY_COLLECTION_SOURCE_V1/reports/PROVEN72_RUNTIME_EXPORT_FIRST_COLLECTION_FOOTPRINT_ABI_ACTUAL.json'
def put(n,v):
 R.mkdir(parents=True,exist_ok=True)
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 p=argparse.ArgumentParser();p.add_argument('--first-chunk',type=int,required=True);p.add_argument('--count',type=int,default=1);a=p.parse_args();assert a.first_chunk>=0 and 1<=a.count<=4
 raw=REPORT.read_bytes();source=json.loads(raw);assert source['bundle_passed'] and source['terminal_observed'] and source['all_original_recorded_out'] and source['exit']['own_lock_released'];producer=source['producer'];assert producer['passed'] and producer['producer_SHA']==PRODUCER_SHA;chunks=producer['chunks'];assert a.first_chunk<len(chunks);selected=chunks[a.first_chunk:a.first_chunk+a.count];assert selected
 assert all(PurePosixPath(x['path']).parent==PurePosixPath(REMOTE) and 0<x['bytes']<=512*1024**2 and len(x['SHA'])==64 for x in selected)
 assert sum(x['bytes'] for x in chunks)==producer['compressed_bytes']
 batch='BATCH_'+str(a.first_chunk).zfill(4)+'_'+str(len(selected)).zfill(2);key=REMOTE+'|'+producer['producer_SHA'];free=shutil.disk_usage('F:/').free;needed=sum(x['bytes'] for x in selected);assert free>needed+1024**3,'actual F capacity insufficient, no copy'
 if not LOCAL.exists():
  LOCAL.mkdir();(LOCAL/'OWN_RUNTIME_ARTIFACT_STAGING_MARKER.json').write_text(json.dumps(dict(purpose='MOD4 proven72 runtime transfer artifacts only',source_key=key,artifact_root=str(LOCAL))))
 else:assert json.loads((LOCAL/'OWN_RUNTIME_ARTIFACT_STAGING_MARKER.json').read_bytes())['source_key']==key
 put(batch+'_ENTERED_BEFORE_NETWORK_ACTUAL.json',dict(epoch=time.time(),source_report_path=str(REPORT),source_report_SHA=hashlib.sha256(raw).hexdigest(),producer_SHA=producer['producer_SHA'],selected=selected,local_root=str(LOCAL),actual_free_F_bytes=free,needed_copy_bytes=needed,maximum_finite_seconds=240,no_C_drive_large_copy=True))
 deadline=time.monotonic()+240
 def left():
  q=deadline-time.monotonic();assert q>0,'original chunk batch finite deadline';return min(25,q)
 wrapper=module('same_memory_compressed_for_artifact_batch',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install();secret=None;t=None;sf=None;copied=[]
 try:
  sec=module('same72_memory_for_artifact_batch',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();sock=socket.create_connection(('10.24.0.72',22),timeout=15);t=paramiko.Transport(sock);t.banner_timeout=15;t.auth_timeout=15;t.start_client(timeout=15);actual=hashlib.sha256(t.get_remote_server_key().asbytes()).hexdigest();assert actual==PIN,'PIN_MISMATCH_BEFORE_AUTH';t.auth_password('lc01',secret,fallback=False);secret=None;sf=paramiko.SFTPClient.from_transport(t);sf.get_channel().settimeout(left())
  with sf.open(REMOTE+'/PROVEN72_RUNTIME_BUNDLE_COMPLETE_PRODUCER_ACTUAL.json','rb') as f:actual_producer_raw=f.read()
  actual_producer=json.loads(actual_producer_raw);assert actual_producer==producer
  for i,row in enumerate(selected,a.first_chunk):
   sf.get_channel().settimeout(left());remote=row['path'];st=sf.lstat(remote);assert stat.S_ISREG(st.st_mode) and st.st_size==row['bytes'];before=(st.st_size,st.st_mtime)
   dest=LOCAL/('runtime72_chunk'+str(i).zfill(4)+'.gz');partial=LOCAL/(dest.name+'.'+batch+'.partial');assert not dest.exists() and not partial.exists();h=hashlib.sha256();count=0;last=0
   try:
    with sf.open(remote,'rb') as src,partial.open('xb') as dst:
     src.prefetch(file_size=row['bytes'],max_concurrent_requests=16)
     while True:
      sf.get_channel().settimeout(left());block=src.read(1024**2)
      if not block:break
      dst.write(block);h.update(block);count+=len(block)
      if time.monotonic()-last>=20:print(json.dumps(dict(stage='ACTUAL_SOURCE72_TO_F_CHUNK',chunk=i,copied_bytes=count,expected_bytes=row['bytes'],epoch=time.time())),flush=True);last=time.monotonic()
    afterstat=sf.stat(remote);assert before==(afterstat.st_size,afterstat.st_mtime) and count==row['bytes'] and h.hexdigest()==row['SHA'];partial.rename(dest)
   except BaseException:
    put(batch+'_CHUNK_'+str(i).zfill(4)+'_ORIGINAL_PARTIAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),partial_path=str(partial),actual_prefix_bytes=count,actual_prefix_SHA=h.hexdigest(),original_remote=row,partial_preserved=True,no_automatic_retry_or_delete=True));raise
   receipt=dict(chunk_index=i,source=dict(row),local_path=str(dest),bytes=count,SHA=h.hexdigest(),twohost_producer_and_received_full_SHA=True,source_before_after_stat_unchanged=True)
   put(batch+'_CHUNK_'+str(i).zfill(4)+'_COMPLETE_ACTUAL.json',receipt);copied.append(receipt)
  put(batch+'_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,actual_finite_returned=True,source_connection_closed_in_finally=True,producer_SHA=producer['producer_SHA'],source_report_SHA=hashlib.sha256(raw).hexdigest(),chunks=copied,no_86_connection_or_training_GPU_or_budget=True));print(json.dumps(dict(passed=True,batch=batch,chunks=len(copied),bytes=sum(x['bytes'] for x in copied),no_86_connection_yet=True)))
 finally:
  secret=None
  if sf:sf.close()
  if t:t.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('DOWNLOAD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry_delete_or_original_source_mutation=True));raise

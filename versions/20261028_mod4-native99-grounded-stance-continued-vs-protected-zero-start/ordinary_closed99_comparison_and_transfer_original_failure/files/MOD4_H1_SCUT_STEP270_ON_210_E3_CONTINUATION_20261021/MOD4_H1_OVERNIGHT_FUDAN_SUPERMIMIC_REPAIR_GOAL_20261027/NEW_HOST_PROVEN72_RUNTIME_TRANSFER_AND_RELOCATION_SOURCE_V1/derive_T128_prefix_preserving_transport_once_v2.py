from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;old=B/'download_verified_runtime_chunks_to_F_bounded_batch_once_v1.py';s=old.read_text()
changes=[("batch='BATCH_'+str(a.first_chunk).zfill(4)+'_'+str(len(selected)).zfill(2)","batch='BATCH_'+str(a.first_chunk).zfill(4)+'_'+str(len(selected)).zfill(2)+'_T128'"),('deadline=time.monotonic()+240','batch_started=time.monotonic();deadline=batch_started+240'),('sf=paramiko.SFTPClient.from_transport(t);','sf=paramiko.SFTPClient.from_transport(t,window_size=64*1024**2,max_packet_size=32768);'),('max_concurrent_requests=16','max_concurrent_requests=128')]
for a,b in changes:assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
anchor="   try:\n    with sf.open(remote,'rb') as src,partial.open('xb') as dst:\n     src.prefetch(file_size=row['bytes'],max_concurrent_requests=128)"
replacement='''   prefix=0;network_bytes=0;network_started=None
   try:
    if i==0:
     prior=json.loads((R/'BATCH_0000_01_CHUNK_0000_ORIGINAL_PARTIAL_ERROR_ACTUAL.json').read_bytes());assert prior['original_remote']==row and prior['partial_preserved']
     priorpath=Path(prior['partial_path']).resolve();assert priorpath.parent==LOCAL.resolve() and priorpath.name==dest.name+'.BATCH_0000_01.partial';beforeprefix=priorpath.stat();assert beforeprefix.st_size==prior['actual_prefix_bytes']<row['bytes']
     with priorpath.open('rb') as srcprefix,partial.open('xb') as dstprefix:
      while True:
       left();block=srcprefix.read(1024**2)
       if not block:break
       dstprefix.write(block);h.update(block);count+=len(block)
     afterprefix=priorpath.stat();assert (beforeprefix.st_size,beforeprefix.st_mtime_ns)==(afterprefix.st_size,afterprefix.st_mtime_ns) and count==prior['actual_prefix_bytes'] and h.hexdigest()==prior['actual_prefix_SHA'];prefix=count
     put(batch+'_OLD_PREFIX_COPY_VERIFIED_ACTUAL.json',dict(original_path=str(priorpath),original_bytes=count,original_prefix_SHA=h.hexdigest(),new_attempt_path=str(partial),original_partial_unchanged=True,no_network_redownload_of_prefix=True))
    network_started=time.monotonic()
    with sf.open(remote,'rb') as src,partial.open('ab' if prefix else 'xb') as dst:
     if prefix:src.seek(prefix)
     src.prefetch(file_size=row['bytes'],max_concurrent_requests=128)'''
assert s.count(anchor)==1;s=s.replace(anchor,replacement)
s=s.replace('h.update(block);count+=len(block)\n      if time.monotonic()', 'h.update(block);count+=len(block);network_bytes+=len(block)\n      if time.monotonic()')
oldprogress="copied_bytes=count,expected_bytes=row['bytes'],epoch=time.time()";newprogress="logical_complete_bytes=count,network_new_bytes=network_bytes,reused_prefix_bytes=prefix,expected_bytes=row['bytes'],epoch=time.time()";assert s.count(oldprogress)==1;s=s.replace(oldprogress,newprogress)
anchor="source_before_after_stat_unchanged=True)";assert s.count(anchor)==1;s=s.replace(anchor,"source_before_after_stat_unchanged=True,reused_prefix_bytes=prefix,network_new_bytes=network_bytes,network_suffix_elapsed_seconds=time.monotonic()-network_started,transport_prefetch_requests=128,transport_channel_window_bytes=64*1024**2)")
s=s.replace("bytes=sum(x['bytes'] for x in copied),no_86_connection_yet=True", "bytes=sum(x['bytes'] for x in copied),reused_prefix_bytes=sum(x['reused_prefix_bytes'] for x in copied),network_new_bytes=sum(x['network_new_bytes'] for x in copied),batch_elapsed_seconds=time.monotonic()-batch_started,no_86_connection_yet=True")
s=s.replace("chunks=copied,no_86_connection_or_training_GPU_or_budget=True", "chunks=copied,batch_elapsed_seconds=time.monotonic()-batch_started,reused_prefix_bytes=sum(x['reused_prefix_bytes'] for x in copied),network_new_bytes=sum(x['network_new_bytes'] for x in copied),no_86_connection_or_training_GPU_or_budget=True")
ast.parse(s);p=B/'download_verified_runtime_chunks_to_F_resume128_bounded_batch_once_v2.py'
with p.open('x',encoding='utf8') as f:f.write(s)
v=dict(epoch=time.time(),source_AST_passed=True,original_source_SHA=hashlib.sha256(old.read_bytes()).hexdigest(),new_source_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),same_240s_512MiB_singleSSH_original_producer_pins=True,source_immutable_producer_and_received_full_SHA_still_required=True,original_partial_and_false_report_preserved=True,new_attempt_prefix_copy_SHA_and_stat_verified=True,only_transport_window_prefetch_and_declared_verified_prefix_continuation_changed=True,new_channel_window_bytes=64*1024**2,bounded_prefetch_requests=128,maximum_inflight_SFTP_payload_bytes=128*32768,no_actual_network_in_deriver=True)
with (B/'FROZEN_T128_PREFIX_PRESERVING_SOURCE_INDEX_V2.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
print(json.dumps(v))

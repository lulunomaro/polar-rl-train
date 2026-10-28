"""Candidate only: owned detached1800s pull, no packages/models/GPU/ledger."""
from pathlib import Path
import hashlib,hmac,http.client,json,os,re,secrets,shutil,signal,ssl,stat,sys,time,traceback
ROOT=Path('/data/robemo/polar-rl-train');BASE=ROOT/'runtime_migrations/proven72_20261028_v1';B=Path(__file__).resolve().parent
PRODUCER='c0d830df0635917f199f3c5e3a3498b7934eb57355dfb24d567eeb99349f7c36'

def put(n,v):
 with (B/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)

def emit(**v):
 value=dict(epoch=time.time(),**v)
 with (B/'DIRECT_PULL_PROGRESS_ACTUAL.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(value)+chr(10))
 print(json.dumps(value),flush=True)

def identity():
 p=Path('/proc/self');raw=(p/'stat').read_text();v=raw[raw.rfind(')')+2:].split();boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '));return dict(pid=os.getpid(),creation=boot+int(v[19])/os.sysconf('SC_CLK_TCK'),exe=os.readlink(p/'exe'),argv=[os.fsdecode(x) for x in (p/'cmdline').read_bytes().split(bytes([0])) if x],cwd=os.getcwd())

def stable(st):return (st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns)

def main():
 assert ROOT.resolve()==ROOT and BASE.resolve()==BASE and B.resolve()==B and B.is_relative_to(BASE) and not B.is_symlink()
 m=json.loads((ROOT/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_bytes());assert m['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700' and m['authorized_root']==str(ROOT)
 cfg=json.loads(sys.stdin.readline());assert cfg['maximum_seconds']==1800 and cfg['actual_probe_pass_binding']['passed'] is True and cfg['producer']['producer_SHA']==PRODUCER and cfg['producer']['passed']
 assert json.loads((BASE/'OWN_PROVEN72_RUNTIME_RECEIVER.json').read_bytes())['producer_SHA']==PRODUCER and json.loads((B/'OWN_DIRECT_PULL_ATTEMPT_MARKER.json').read_bytes())['run_id']==cfg['run_id']
 ep=cfg['endpoint'];assert ep['data_enable'] and ep['advertised_host']=='10.24.0.72' and ep['actual_OS_selected_port']!=29754 and ep['producer_SHA']==PRODUCER
 rows=cfg['producer']['chunks'];assert len(rows)==29 and sum(x['bytes'] for x in rows)==cfg['producer']['compressed_bytes']==15158703068
 for i,row in enumerate(rows):assert Path(row['path']).name=='runtime72.tar.gz.chunk'+str(i).zfill(4) and 0<row['bytes']<=512*1024**2 and re.fullmatch('[0-9a-f]{64}',row['SHA'])
 key=bytes.fromhex(cfg.pop('hmac_key_hex'));assert len(key)==32;context=ssl.create_default_context(cadata=ep['public_certificate_pem']);context.check_hostname=True;context.verify_mode=ssl.CERT_REQUIRED
 free=shutil.disk_usage(ROOT).free;required=cfg['producer']['compressed_bytes']+cfg['logical_input_bytes']+1024**3;assert free>required
 C=B/'chunks';C.mkdir(mode=0o700);assert C.resolve()==C
 started=time.time();deadline=min(started+1800,ep['deadline_epoch']-15);assert deadline>started;me=identity();result=None;active=[None];whole=hashlib.sha256();completed=[];network=0;reused=0;previous_verified=0
 def expired(signum,frame):raise TimeoutError('owned direct pull original1800s/source deadline bound')
 signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,deadline-started)
 put('DIRECT_PULL_WORKER_IDENTITY_AND_BUDGET_ACTUAL.json',dict(epoch=started,identity=me,run_id=cfg['run_id'],producer_SHA=PRODUCER,maximum_seconds=1800,actual_deadline_epoch=deadline,source_endpoint=ep,actual_free_bytes=free,required_capacity_bytes=required,no_GPU_model_package_or_canonical_operation=True))
 emit(stage='OWNED_DIRECT_PULL_STARTED',identity=me,actual_deadline_epoch=deadline)
 def request(path,offset=0):
  left=deadline-time.time();assert left>0;conn=http.client.HTTPSConnection(ep['advertised_host'],ep['actual_OS_selected_port'],timeout=min(30,left),context=context);active[0]=conn;conn.connect();assert hashlib.sha256(conn.sock.getpeercert(binary_form=True)).hexdigest()==ep['certificate_SHA'],'TLS_PIN_MISMATCH_BEFORE_HMAC'
  nonce=secrets.token_hex(16);expires=str(int(min(time.time()+60,ep['deadline_epoch']-1)));rangevalue='bytes='+str(offset)+'-' if offset else '';message='GET\n'+path+'\n'+rangevalue+'\n'+expires+'\n'+nonce+'\n'+PRODUCER;headers={'X-Mod4-Expires':expires,'X-Mod4-Nonce':nonce,'X-Mod4-HMAC':hmac.new(key,message.encode(),hashlib.sha256).hexdigest()}
  if offset:headers['Range']=rangevalue
  conn.request('GET',path,headers=headers);return conn,conn.getresponse()
 try:
  for i,row in enumerate(rows):
   name='runtime72_chunk'+str(i).zfill(4)+'.gz';old=BASE/'chunks'/name;oldpartial=BASE/'chunks'/(name+'.partial');partial=C/(name+'.partial');final=C/name;digest=hashlib.sha256();count=0;prefix=0;oldproof=None;begin=time.monotonic();last=0
   if old.exists():
    assert i==0 and old.resolve()==old and not old.is_symlink();receipt=json.loads((BASE/('CHUNK_'+name+'_RECEIVER_ACTUAL.json')).read_bytes());assert receipt['passed'] and receipt['producer_SHA']==PRODUCER and receipt['SHA']==row['SHA'] and receipt['bytes']==row['bytes'];before=old.stat();assert stat.S_ISREG(before.st_mode) and before.st_size==row['bytes']
    with old.open('rb') as f:
     while True:
      block=f.read(1024**2)
      if not block:break
      digest.update(block);whole.update(block);count+=len(block)
    assert stable(before)==stable(old.stat()) and count==row['bytes'] and digest.hexdigest()==row['SHA'];previous_verified+=count;published=old
   else:
    with partial.open('xb') as out:
     if oldpartial.exists():
      assert i in {1,2,3,4} and oldpartial.resolve()==oldpartial and not oldpartial.is_symlink();before=oldpartial.stat();assert stat.S_ISREG(before.st_mode) and 0<before.st_size<=row['bytes']
      with oldpartial.open('rb') as src:
       while True:
        block=src.read(1024**2)
        if not block:break
        out.write(block);digest.update(block);whole.update(block);count+=len(block)
      assert stable(before)==stable(oldpartial.stat()) and count==before.st_size;prefix=count
      conn,response=request('/prefix/'+str(i).zfill(4)+'/'+str(prefix))
      try:
       raw=response.read(65537);assert response.status==200 and len(raw)<=65536;proof=json.loads(raw);assert proof['producer_SHA']==PRODUCER and proof['chunk_index']==i and proof['prefix_bytes']==prefix and proof['prefix_SHA']==digest.hexdigest() and proof['expected_full_SHA']==row['SHA'] and proof['source_stat_unchanged']
      finally:conn.close();active[0]=None
      oldproof=dict(original_path=str(oldpartial),original_stat=list(stable(before)),original_prefix_SHA=digest.hexdigest(),source_prefix_proof=proof,new_attempt_path=str(partial),old_partial_untouched=True);put('CHUNK_'+str(i).zfill(4)+'_COPIED_PREFIX_SOURCE_MATCH_ACTUAL.json',oldproof);reused+=prefix
     if count<row['bytes']:
      conn,response=request('/chunk/'+str(i).zfill(4),count)
      try:
       assert response.status==(206 if count else 200) and int(response.getheader('Content-Length'))==row['bytes']-count and response.getheader('X-Mod4-Producer')==PRODUCER and response.getheader('X-Mod4-Chunk-SHA')==row['SHA']
       if count:assert response.getheader('Content-Range')=='bytes '+str(count)+'-'+str(row['bytes']-1)+'/'+str(row['bytes'])
       while count<row['bytes']:
        block=response.read(min(1024**2,row['bytes']-count));assert block;out.write(block);digest.update(block);whole.update(block);count+=len(block);network+=len(block)
        if time.monotonic()-last>=20:emit(stage='DIRECT72_TO86_HTTPS_CHUNK_SUFFIX',chunk=i,complete_bytes=count,reused_prefix_bytes=prefix,total_network_new_bytes=network,expected_bytes=row['bytes']);last=time.monotonic()
      finally:conn.close();active[0]=None
     out.flush();os.fsync(out.fileno())
    assert count==row['bytes'] and digest.hexdigest()==row['SHA'];partial.rename(final);published=final
   rec=dict(passed=True,epoch=time.time(),chunk_index=i,path=str(published),bytes=count,SHA=digest.hexdigest(),producer_SHA=PRODUCER,receiver_full_SHA_equal_producer=True,reused_old_partial_prefix_bytes=prefix,old_prefix_proof=oldproof,original_verified_chunk0_unchanged=i==0,network_new_bytes=0 if i==0 else count-prefix,elapsed_seconds=time.monotonic()-begin)
   put('CHUNK_'+str(i).zfill(4)+'_DIRECT_RECEIVER_FULL_SHA_ACTUAL.json',rec);completed.append(rec)
   emit(stage='CHUNK_RECEIVER_FULL_SHA_VERIFIED',chunk=i,bytes=count,SHA=digest.hexdigest(),copied_old_prefix_bytes=prefix,elapsed_seconds=rec['elapsed_seconds'])
  assert sum(x['bytes'] for x in completed)==cfg['producer']['compressed_bytes'] and whole.hexdigest()==PRODUCER
  result=dict(passed_all_artifact_chunks_only=True,epoch=time.time(),producer_SHA=PRODUCER,compressed_bytes=sum(x['bytes'] for x in completed),whole_ordered_archive_SHA=whole.hexdigest(),chunks=completed,network_new_bytes=network,reused_copied_prefix_bytes=reused,previously_verified_chunk0_bytes=previous_verified,original_partial_files_unchanged=True,no_extraction_relocation_SDK_CUDA_or_training_proof=True)
  put('DIRECT_RECEIVER_ALL29_CHUNKS_FULL_SHA_COMPLETE_ACTUAL.json',result)
 except BaseException:
  result=dict(passed_all_artifact_chunks_only=False,epoch=time.time(),error=traceback.format_exc(),producer_SHA=PRODUCER,verified_completed_chunks=completed,network_new_bytes=network,reused_copied_prefix_bytes=reused,all_old_and_new_partial_bytes_preserved=True,no_automatic_retry_overwrite_delete_or_system_change=True);put('DIRECT_PULL_ORIGINAL_ERROR_ACTUAL.json',result)
 finally:
  signal.setitimer(signal.ITIMER_REAL,0)
  if active[0]:active[0].close()
  key=None;put('DIRECT_PULL_TERMINAL_ACTUAL.json',dict(epoch=time.time(),identity=me,run_id=cfg['run_id'],passed_artifact_only=bool(result and result.get('passed_all_artifact_chunks_only')),result_file='DIRECT_RECEIVER_ALL29_CHUNKS_FULL_SHA_COMPLETE_ACTUAL.json' if result and result.get('passed_all_artifact_chunks_only') else 'DIRECT_PULL_ORIGINAL_ERROR_ACTUAL.json',all_HTTP_connections_closed=True,no_GPU_model_package_or_canonical_operation=True))
 print(json.dumps(dict(passed_all_artifacts_only=bool(result and result.get('passed_all_artifact_chunks_only')),actual_worker_returning=True,no_SDK_proof=True)),flush=True)
 if not result or not result.get('passed_all_artifact_chunks_only'):raise SystemExit(2)

if __name__=='__main__':
 try:main()
 except SystemExit:raise
 except BaseException:put('DIRECT_PULL_PRE_TRANSFER_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise

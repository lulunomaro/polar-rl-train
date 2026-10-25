"""Finite four-reader public HTTP to memory to one SFTP writer. No local weight copy or model execution."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,sys,time,traceback,urllib.request,urllib.error
Q=Path(__file__).resolve().parent;T=Q.parent;W=T.parent;R=Q/'reports'
p=argparse.ArgumentParser();p.add_argument('batch',choices=[str(i).zfill(2) for i in range(1,11)]);a=p.parse_args();ID='Q8_WINDOWS_MEMORY_RELAY_V2_'+a.batch
SIZE=5400179040;SHA='57bece983817ab2f957546683bb670f13be7d99022d45674840cd999a050ea8f'
ROOT='/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025'
PART=ROOT+'/models/quantized/Wan2.2-TI2V-5B-Q8_0.gguf.part'
URL='https://hf-mirror.com/QuantStack/Wan2.2-TI2V-5B-GGUF/resolve/57437632ddd08bdcbd1508c866aa22e126ed51d2/Wan2.2-TI2V-5B-Q8_0.gguf?download=true'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
PRE=r'''
from pathlib import Path
import hashlib,json,os,psutil,shutil,time
B=Path(v['root']);part=Path(v['part']);target=part.with_suffix('')
assert B.resolve()==B and part.resolve().is_relative_to(B) and not part.is_symlink() and not target.exists()
assert (B/'FULL13_DOWNLOAD_CANCELLED_BY_HUMAN_20261025.json').is_file()
active=[]
for p in psutil.process_iter(['pid','cmdline']):
 try:
  argv=p.info['cmdline'] or []
  if p.pid!=os.getpid() and any(str(B/'preparation_helpers')+'/' in x and ('download_' in x) for x in argv):active.append(p.info['pid'])
 except psutil.Error:pass
assert not active,'Only one own downloader may write this research root'
part.parent.mkdir(exist_ok=True);exists=part.exists();st=part.stat() if exists else None
if st:assert st.st_nlink==1 and st.st_size<=v['size']
offset=st.st_size if st else 0;assert shutil.disk_usage(B).free-(v['size']-offset)>25*1024**3
with (B/'receipts'/(v['id']+'_STARTED.json')).open('x') as f:json.dump(dict(epoch=time.time(),id=v['id'],part=str(part),offset=offset,expected_bytes=v['size'],expected_SHA=v['sha'],no_local_weight_copy=True),f,indent=2)
print(json.dumps(dict(epoch=time.time(),offset=offset,exists=exists,free_bytes=shutil.disk_usage(B).free,metadata=None if st is None else dict(inode=st.st_ino,device=st.st_dev,mtime_ns=st.st_mtime_ns,bytes=st.st_size))))
'''
POST=r'''
from pathlib import Path
import hashlib,json,os,shutil,struct,time
B=Path(v['root']);part=Path(v['part']);assert not part.is_symlink() and part.stat().st_nlink==1
actual=part.stat().st_size;assert actual==v['offset']+v['new_bytes'] and actual<=v['size']
result=dict(epoch=time.time(),id=v['id'],part=str(part),actual_bytes=actual,new_bytes=v['new_bytes'],expected_bytes=v['size'],expected_SHA=v['sha'],no_GPU_model_load_training_or_budget_write=True,Windows_memory_relay_no_local_weight_copy=True,network_result=v['network'],free_bytes=shutil.disk_usage(B).free)
if actual==v['size']:
 h=hashlib.sha256()
 with part.open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 assert h.hexdigest()==v['sha'],'Pinned full Q8 SHA mismatch; partial preserved'
 with part.open('rb') as f:magic,version,tensors,metadata=struct.unpack('<4sIQQ',f.read(24))
 assert magic==b'GGUF' and version in (2,3) and tensors>0
 target=part.with_suffix('');assert not target.exists();part.rename(target)
 result.update(status='COMPLETE_FULL_SHA_AND_GGUF_HEADER_VERIFIED',path=str(target),producer_SHA=h.hexdigest(),GGUF_version=version,tensor_count=tensors,metadata_fields=metadata)
else:result.update(status='FINITE_PARTIAL_RETAINED',not_complete_or_SHA_verified=True)
with (B/'receipts'/(v['id']+'_FINAL.json')).open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(result))
'''
try:
 put(ID+'_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,scope='Exact one Q8 file only; remote direct timeout original retained',max_seconds=90))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None
 args=dict(root=ROOT,part=PART,id=ID,size=SIZE,sha=SHA);sf=None;stream=None;new_bytes=0;network={};started=time.monotonic()
 try:
  pre=d.code(c,d.PY72,PRE,args,timeout=45);put(ID+'_REMOTE_PREFLIGHT_ACTUAL.json',pre)
  try:
   from concurrent.futures import ThreadPoolExecutor
   sf=c.open_sftp();sf.get_channel().settimeout(60);stream=sf.open(PART,'ab' if pre['exists'] else 'wx');stream.set_pipelined(True)
   def fetch_range(begin,end):
    request=urllib.request.Request(URL,headers={'User-Agent':'Mozilla/5.0','Range':'bytes='+str(begin)+'-'+str(end),'Accept-Encoding':'identity'})
    with urllib.request.urlopen(request,timeout=25) as response:
     assert response.status==206 and response.headers.get('Content-Range','').startswith('bytes '+str(begin)+'-'),'Exact pinned Range origin required'
     data=response.read(end-begin+1);assert len(data)==end-begin+1,'Incomplete fixed range; retained prefix is unchanged'
     return data
   failed=None
   with ThreadPoolExecutor(max_workers=4) as pool:
    while pre['offset']+new_bytes<SIZE and time.monotonic()-started<90:
     begin=pre['offset']+new_bytes
     ranges=[(s,min(s+8*1024**2-1,SIZE-1)) for s in range(begin,min(begin+4*8*1024**2,SIZE),8*1024**2)]
     futures=[pool.submit(fetch_range,s,e) for s,e in ranges]
     for future in futures:
      try:data=future.result()
      except Exception as e:
       failed=dict(error_type=type(e).__name__,reason_type=type(getattr(e,'reason',None)).__name__,HTTP_status=getattr(e,'code',None));break
      stream.write(data);new_bytes+=len(data)
     if failed:break
   stream.close();stream=None;sf.close();sf=None
   network=dict(transport='Four bounded public byte-range readers, one contiguous SFTP writer',finite_seconds=90,max_buffered_bytes=4*8*1024**2,network_error=failed)
  except (urllib.error.URLError,TimeoutError) as e:
   network=dict(error_type=type(e).__name__,reason_type=type(getattr(e,'reason',None)).__name__,HTTP_status=getattr(e,'code',None),no_signed_URL_logged=True)
  finally:
   if stream:stream.close()
   if sf:sf.close()
  if pre['exists'] or new_bytes:
   result=d.code(c,d.PY72,POST,dict(args,offset=pre['offset'],new_bytes=new_bytes,network=network),timeout=180)
  else:result=dict(epoch=time.time(),status='NO_BYTES_NETWORK_FAILURE_PRESERVED',network_result=network,expected_bytes=SIZE,expected_SHA=SHA,new_bytes=0)
  put(ID+'_RETURNED_ACTUAL.json',result);print(json.dumps(result))
 finally:c.close()
except BaseException:
 put(ID+'_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_local_weight_disk_copy_or_training=True));raise

"""Exactly one pinned Q8_0 file. Anonymous finite download; no model execution."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,struct,time,urllib.request,urllib.error
ROOT=Path('/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025')
REPO='QuantStack/Wan2.2-TI2V-5B-GGUF';REV='57437632ddd08bdcbd1508c866aa22e126ed51d2'
NAME='Wan2.2-TI2V-5B-Q8_0.gguf';SIZE=5400179040
SHA='57bece983817ab2f957546683bb670f13be7d99022d45674840cd999a050ea8f'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--batch',required=True,choices=[str(i).zfill(2) for i in range(1,11)]);a=p.parse_args()
 assert ROOT.resolve()==ROOT and ROOT.is_dir();R=ROOT/'receipts';ID='SINGLE4090_Q8_ONLY_BATCH_'+a.batch
 with (R/(ID+'_STARTED.json')).open('x') as f:json.dump(dict(epoch=time.time(),repo=REPO,revision=REV,file=NAME,expected_bytes=SIZE,expected_SHA=SHA,finite_seconds=600,old_full13_cancelled=True),f,indent=2)
 target=ROOT/'models/quantized'/NAME;target.parent.mkdir(parents=True,exist_ok=True);part=target.with_name(NAME+'.part')
 assert target.resolve().is_relative_to(ROOT) and part.resolve().is_relative_to(ROOT)
 result=dict(epoch=time.time(),repo=REPO,revision=REV,file=NAME,path=str(target),expected_bytes=SIZE,expected_SHA=SHA,format='GGUF Q8_0',single4090_candidate_not_GPU_fit_proof=True,no_model_load_training_GPU_or_budget_write=True,original_full13_download_cancelled=True,transport_host='hf-mirror.com',official_identity='https://huggingface.co/'+REPO+'/blob/'+REV+'/'+NAME)
 started=time.monotonic();new_bytes=0;rc=0
 try:
  if target.exists():
   assert target.is_file() and not target.is_symlink() and target.stat().st_size==SIZE
   result.update(status='ALREADY_PRESENT_REQUIRES_SAVED_PRODUCER_RECEIPT',actual_bytes=SIZE)
  else:
   assert not part.is_symlink();offset=part.stat().st_size if part.exists() else 0;assert 0<=offset<=SIZE
   if part.exists():assert part.stat().st_nlink==1
   assert shutil.disk_usage(ROOT).free-(SIZE-offset)>25*1024**3
   if offset<SIZE:
    headers={'User-Agent':'Mozilla/5.0'}
    if offset:headers['Range']='bytes='+str(offset)+'-'
    url='https://hf-mirror.com/'+REPO+'/resolve/'+REV+'/'+NAME+'?download=true'
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(urllib.request.Request(url,headers=headers),timeout=20) as response:
     if offset:assert response.status==206 and response.headers.get('Content-Range','').startswith('bytes '+str(offset)+'-')
     with part.open('ab' if part.exists() else 'xb') as f:
      while offset<SIZE and time.monotonic()-started<600:
       assert shutil.disk_usage(ROOT).free-4*1024**2>25*1024**3
       b=response.read(min(4*1024**2,SIZE-offset))
       if not b:break
       f.write(b);offset+=len(b);new_bytes+=len(b)
      f.flush();os.fsync(f.fileno())
   if offset==SIZE:
    actual=digest(part);assert actual==SHA,'Pinned complete model SHA mismatch; partial retained'
    with part.open('rb') as f:header=f.read(24)
    magic,version,tensors,kv=struct.unpack('<4sIQQ',header);assert magic==b'GGUF' and version in (2,3) and tensors>0
    assert not target.exists();part.rename(target)
    result.update(status='COMPLETE_FULL_SHA_AND_GGUF_HEADER_VERIFIED',actual_bytes=SIZE,producer_SHA=actual,GGUF_version=version,tensor_count=tensors,metadata_fields=kv)
   else:result.update(status='FINITE_PARTIAL_RETAINED',partial_path=str(part),actual_bytes=offset,not_complete_or_SHA_verified=True)
 except urllib.error.URLError as e:
  rc=1;result.update(status='NETWORK_ERROR_PARTIAL_PRESERVED',error_type=type(e).__name__,reason_type=type(getattr(e,'reason',None)).__name__,HTTP_status=getattr(e,'code',None))
 except Exception as e:
  rc=1;result.update(status='ORIGINAL_ERROR_PRESERVED',error_type=type(e).__name__)
  if isinstance(e,AssertionError):result['reason']=str(e)
 result.update(new_bytes=new_bytes,elapsed_seconds=time.monotonic()-started,free_bytes_after=shutil.disk_usage(ROOT).free)
 with (R/(ID+'_FINAL.json')).open('x') as f:json.dump(result,f,indent=2)
 print(json.dumps(result));return rc
if __name__=='__main__':raise SystemExit(main())

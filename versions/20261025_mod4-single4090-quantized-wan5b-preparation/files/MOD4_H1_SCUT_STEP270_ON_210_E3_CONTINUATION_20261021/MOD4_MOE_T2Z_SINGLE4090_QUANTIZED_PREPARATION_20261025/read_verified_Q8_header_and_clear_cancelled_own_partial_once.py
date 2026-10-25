"""Read actual GGUF index only; discard this phase's cancelled full-weight fragment."""
from pathlib import Path
import importlib.util,json,os,sys,time,traceback
Q=Path(__file__).resolve().parent;T=Q.parent;W=T.parent;R=Q/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r'''
from pathlib import Path
import collections,fcntl,json,math,os,psutil,shutil,stat,struct,time
B=Path('/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025');R=B/'receipts';P=B/'models/quantized/Wan2.2-TI2V-5B-Q8_0.gguf'
assert P.resolve().is_relative_to(B) and not P.is_symlink() and P.stat().st_size==5400179040
proof=v['complete'];assert proof['actual_bytes']==5400179040 and proof['producer_SHA']=='57bece983817ab2f957546683bb670f13be7d99022d45674840cd999a050ea8f'
def unpack(f,fmt):
 n=struct.calcsize(fmt);raw=f.read(n);assert len(raw)==n;return struct.unpack(fmt,raw)[0]
def string(f):
 n=unpack(f,'<Q');assert n<=4*1024**2;raw=f.read(n);assert len(raw)==n;return raw.decode('utf8')
scalar={0:'<B',1:'<b',2:'<H',3:'<h',4:'<I',5:'<i',6:'<f',7:'<?',10:'<Q',11:'<q',12:'<d'}
def value(f,kind):
 if kind in scalar:return unpack(f,scalar[kind])
 if kind==8:return string(f)
 if kind==9:
  sub=unpack(f,'<I');n=unpack(f,'<Q');assert n<=100000;return [value(f,sub) for _ in range(n)]
 raise RuntimeError('Unknown GGUF metadata primitive; preserved without interpreting weight data')
with P.open('rb') as f:
 magic=f.read(4);version=unpack(f,'<I');count=unpack(f,'<Q');fields=unpack(f,'<Q');assert magic==b'GGUF' and version in (2,3) and 0<count<100000 and fields<10000
 metadata={}
 for _ in range(fields):key=string(f);metadata[key]=value(f,unpack(f,'<I'))
 tensors=[]
 for _ in range(count):
  name=string(f);dimensions=unpack(f,'<I');assert 0<dimensions<=8
  shape=[unpack(f,'<Q') for _ in range(dimensions)];qtype=unpack(f,'<I');offset=unpack(f,'<Q');assert all(x>0 for x in shape)
  tensors.append(dict(name=name,GGUF_shape=shape,torch_reversed_shape=list(reversed(shape)),qtype=qtype,data_relative_offset=offset))
 header_bytes=f.tell();alignment=int(metadata.get('general.alignment',32));assert alignment>0
 data_offset=((header_bytes+alignment-1)//alignment)*alignment;assert data_offset<P.stat().st_size
counts=dict(collections.Counter(x['qtype'] for x in tensors));assert counts.get(8,0)>0
result=dict(epoch=time.time(),model_path=str(P),model_bytes=P.stat().st_size,producer_SHA=proof['producer_SHA'],no_second_full_weight_hash=True,GGUF_version=version,header_bytes_read=header_bytes,GGUF_data_offset=data_offset,tensor_count=count,metadata=metadata,qtype_counts=counts,tensors=tensors,actual_metadata_only_no_weight_tensor_or_GPU_load=True,DiffSynth_MOE_T2z_full_key_mapping_and_single4090_fit_pending=True)
with (R/'SINGLE4090_Q8_ACTUAL_GGUF_METADATA_CPU.json').open('x') as f:json.dump(result,f,indent=2)
# This is the sole known unfinished VAE download from the cancelled full13 plan.
# No completed model, original checkpoint, source, log or training raw is deleted.
old=B/'models/Wan2.2-TI2V-5B/Wan2.2_VAE.pth.part';assert old.resolve().is_relative_to(B)
cleanup=dict(epoch=time.time(),path=str(old),scope='Cancelled own incomplete full-weight download only',no_training_FINAL_or_source_removed=True)
if old.exists():
 assert not old.is_symlink();s=old.stat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1
 original=json.loads((R/'VERIFIED_PUBLIC_CACHE_BATCH_01_FINAL.json').read_bytes())['downloader'];row=next(x for x in original['results'] if x['destination']=='models/Wan2.2-TI2V-5B/Wan2.2_VAE.pth')
 active=[]
 for p in psutil.process_iter(['pid','cmdline']):
  try:
   if p.pid!=os.getpid() and any(str(B/'preparation_helpers')+'/' in x and 'download_' in x for x in p.info['cmdline'] or []):active.append(p.info['pid'])
  except psutil.Error:pass
 assert not active and row['status']=='PARTIAL_RETAINED'
 if s.st_size!=row['bytes']:cleanup.update(status='REFUSED_PARTIAL_SIZE_CHANGED',actual_bytes=s.st_size,producer_partial_bytes=row['bytes'])
 else:
  cleanup.update(status='INTENT_EXACT_OWN_CANCELLED_PARTIAL',bytes=s.st_size,allocated_bytes=s.st_blocks*512,inode=s.st_ino,device=s.st_dev,mtime_ns=s.st_mtime_ns,nlink=s.st_nlink,source_receipt=str(R/'VERIFIED_PUBLIC_CACHE_BATCH_01_FINAL.json'))
  with (R/'SINGLE4090_Q8_CANCELLED_OWN_FULLWEIGHT_PARTIAL_CLEANUP_INTENT.json').open('x') as f:json.dump(cleanup,f,indent=2)
  with old.open('rb') as f:
   fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);t=os.fstat(f.fileno());u=old.stat();assert (t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns,t.st_nlink)==(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,1)==(u.st_dev,u.st_ino,u.st_size,u.st_mtime_ns,u.st_nlink)
   old.unlink()
  assert not old.exists();cleanup['status']='EXACT_OWN_CANCELLED_PARTIAL_REMOVED'
else:cleanup['status']='ALREADY_ABSENT_NO_DELETE'
cleanup['fresh_free_bytes']=shutil.disk_usage(B).free
with (R/'SINGLE4090_Q8_CANCELLED_OWN_FULLWEIGHT_PARTIAL_CLEANUP_ACTUAL.json').open('x') as f:json.dump(cleanup,f,indent=2)
print(json.dumps(dict(metadata=result,own_cancelled_partial_cleanup=cleanup)))
'''
try:
 results=[json.loads(p.read_bytes()) for p in R.glob('Q8_WINDOWS_MEMORY_RELAY_*_RETURNED_ACTUAL.json')]
 results += [v['download_result'] for p in R.glob('SINGLE4090_Q8_BATCH_*_RETURNED_ACTUAL.json') if isinstance((v:=json.loads(p.read_bytes())).get('download_result'),dict)]
 complete=next(x for x in results if x.get('status')=='COMPLETE_FULL_SHA_AND_GGUF_HEADER_VERIFIED')
 put('VERIFIED_Q8_METADATA_AND_OWN_CANCELLED_PARTIAL_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,no_model_training=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None
 try:value=d.code(c,d.PY72,CODE,dict(complete=complete),timeout=90)
 finally:c.close()
 put('VERIFIED_Q8_METADATA_AND_OWN_CANCELLED_PARTIAL_RETURNED_ACTUAL.json',value)
 print(json.dumps(dict(model_bytes=value['metadata']['model_bytes'],tensor_count=value['metadata']['tensor_count'],qtype_counts=value['metadata']['qtype_counts'],header_only_no_model_load=True,cleanup=value['own_cancelled_partial_cleanup'])))
except BaseException:
 put('Q8_METADATA_OR_OWN_CANCELLED_PARTIAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise

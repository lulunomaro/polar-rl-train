"""Missing-only continuation of the returned public JSON-chunk download failure."""
from pathlib import Path
import hashlib,importlib.util,json,os,sys,time,traceback,urllib.request,base64
J=Path(__file__).resolve().parent;T=J.parent;W=T.parent;R=J/'reports'
sp=importlib.util.spec_from_file_location('v1_source_definitions_only',J/'prepare72_and_capture_pinned_Fudan_jump_reference_CPU_finite_unused_once.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);d=m.d;read=m.read
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CHECK_PARTIAL=r'''
from pathlib import Path
import fcntl,json,os,psutil,shutil,time
B=Path(v['root']);assert B.parent==Path('/home/lc01/Zonglin Li/zonglin2/research') and B.is_dir() and not B.is_symlink();assert not (B/'FOREIGN_REFERENCE_CPU_STARTED_ACTUAL.json').exists() and not (B/'.venv_reference_cpu').exists() and not (B/'reference_capture').exists()
assert not any(p.pid!=os.getpid() and any(a.startswith(str(B)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
assert shutil.disk_usage(B).free>25*1024**3 and psutil.virtual_memory().available>8*1024**3
out=[]
for r in v['completed']:
 p=B/'vendor/fudan_rl_wheel_leg'/r['path'];s=p.stat();assert not p.is_symlink() and s.st_size==r['bytes'] and s.st_nlink==1;out.append(dict(path=str(p),bytes=s.st_size,inode=s.st_ino,device=s.st_dev,mtime_ns=s.st_mtime_ns,metadata_only_not_rehashed=True))
for r in v['missing']:
 p=B/'vendor/fudan_rl_wheel_leg'/r['path'];assert not p.exists() and not p.with_suffix(p.suffix+'.partial').exists()
print(json.dumps(dict(epoch=time.time(),own_reference_processes_actual_out=True,no_previous_CPU_rollout_started=True,existing_completed_files_metadata=out,missing_count=len(v['missing']),no_model_redownload_or_known_hash_reexecution=True)))
'''
def public_bytes(row):
 attempts=[];revision='8204e853dfd2ed06d85a322e1a998c3d20a3be2c'
 for host in ('cdn.jsdelivr.net','fastly.jsdelivr.net'):
  url='https://'+host+'/gh/yly-true/fudan_rl_wheel_leg@'+revision+'/'+row['path']
  try:
   request=urllib.request.Request(url,headers={'User-Agent':'MOD4-pinned-reference-missing-two-v3','Accept':'application/octet-stream'})
   with urllib.request.urlopen(request,timeout=35) as response:
    blocks=[];size=0
    while True:
     block=response.read(256*1024)
     if not block:break
     size+=len(block);assert size<=row['bytes'];blocks.append(block)
    raw=b''.join(blocks)
   assert len(raw)==row['bytes'] and hashlib.sha1(b'blob '+str(len(raw)).encode()+bytes([0])+raw).hexdigest()==row['Git_blob_SHA1']
   return raw,attempts+[dict(url=url,transport_mirror_only_primary_pinned_Git_blob_SHA1_matches=True)]
  except BaseException:attempts.append(dict(url=url,error=traceback.format_exc()))
 raise RuntimeError(json.dumps(attempts))

def main():
 failures=list(R.glob('FUDAN_REFERENCE_MISSING_ONLY_V2_ORIGINAL_ERROR_*.json'));assert len(failures)==1;error=read(failures[0]);completed=error['transferred'];assert len(completed)==22 and 'TimeoutError' in error['error'];plan=read(R/'PINNED_FOREIGN_REFERENCE_ASSET_DOWNLOAD_PLAN_SOURCE_ONLY_ACTUAL.json');done={r['path'] for r in completed};missing=[r for r in plan['files'] if r['path'] not in done];assert len(missing)==2
 put('FUDAN_REFERENCE_MISSING_ONLY_V3_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,original_failure=str(failures[0]),known_completed_not_redownloaded=completed,missing_files=missing,new_raw_media_stream_transport_not_old_JSON_batch_replay=True,no_native_training_GO=True))
 sp=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(sp);sp.loader.exec_module(memory);secret=memory.recover();c=None;transferred=list(completed)
 try:
  c=d.connect72(secret);secret=None;remote=plan['remote_root'];put('FUDAN_REFERENCE_V3_PARTIAL22_FRESH_METADATA_AND_NO_OWN_RUN_ACTUAL.json',d.code(c,d.PY72,CHECK_PARTIAL,dict(root=remote,completed=completed,missing=missing),timeout=60));sf=c.open_sftp();sf.get_channel().settimeout(60)
  try:
   for row in missing:
    raw,attempts=public_bytes(row);target=remote+'/vendor/fudan_rl_wheel_leg/'+row['path'];current='/'
    for part in target.split('/')[1:-1]:
     current=current.rstrip('/')+'/'+part
     try:sf.stat(current)
     except FileNotFoundError:assert current.startswith(remote+'/');sf.mkdir(current)
    digest=hashlib.sha256(raw).hexdigest()
    with sf.open(target+'.partial','wx') as out:out.set_pipelined(True);out.write(raw);out.flush()
    sf.rename(target+'.partial',target);raw=None;r=dict(row,SHA=digest,remote_path=target,transport_attempts=attempts);transferred.append(r);put('PINNED_PUBLIC_ASSET_'+str(len(transferred)).zfill(2)+'_TRANSFERRED_ACTUAL.json',r)
  finally:sf.close()
  result=d.code(c,d.PY72,m.VERIFY_SETUP_RUN,dict(root=remote,files=transferred,driver_SHA=hashlib.sha256((J/'fudan_original_jump_headless_CPU_reference_v1.py').read_bytes()).hexdigest()),timeout=1150);put('FUDAN_ORIGINAL_JUMP_CPU_REFERENCE_REMOTE_RESULT_ACTUAL.json',result)
  local=J/'actual_72_reference_text';local.mkdir();data=J/'actual_72_reference_artifacts';data.mkdir();sf=c.open_sftp();received=[]
  try:
   for row in result['texts']:
    path=local/row['relative'];path.parent.mkdir(parents=True,exist_ok=True);sf.get(row['path'],str(path));assert path.stat().st_size==row['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest()==row['SHA']
   assert sum(r['bytes'] for r in result['small_artifacts'])<=32*1024**2
   for row in result['small_artifacts']:
    rel=Path(row['path']).relative_to(Path(remote)/'reference_capture');assert row['bytes']<=8*1024**2 and '..' not in rel.parts;path=data/rel;path.parent.mkdir(parents=True,exist_ok=True);sf.get(row['path'],str(path));assert path.stat().st_size==row['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest()==row['SHA'];received.append(dict(row,local_path=str(path),twohost_complete_SHA=True))
  finally:sf.close()
  put('FUDAN_ORIGINAL_JUMP_CPU_REFERENCE_FINITE_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_returned=True,own_reference_child_actual_out=result['own_reference_child_actual_out'],reference_returncode=result['reference_returncode'],texts_collected=len(result['texts']),small_artifacts=received,assets=transferred,CPU_foreign_reference_not_our_skill_or_native_training=True,no_native_or_our_model_promotion=True,known_first22_assets_not_redownloaded=True,first_remote_full_SHA_verification_after_all_complete=True))
  print(json.dumps(dict(returned=True,reference_returncode=result['reference_returncode'],assets=len(transferred),small_reference_artifacts=len(received),no_GPU_training=True)))
 except BaseException:
  put('FUDAN_REFERENCE_MISSING_ONLY_V3_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),transferred=transferred,no_same_once_replay=True,own_reference_out_only_if_exit_receipt=True));raise
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':main()

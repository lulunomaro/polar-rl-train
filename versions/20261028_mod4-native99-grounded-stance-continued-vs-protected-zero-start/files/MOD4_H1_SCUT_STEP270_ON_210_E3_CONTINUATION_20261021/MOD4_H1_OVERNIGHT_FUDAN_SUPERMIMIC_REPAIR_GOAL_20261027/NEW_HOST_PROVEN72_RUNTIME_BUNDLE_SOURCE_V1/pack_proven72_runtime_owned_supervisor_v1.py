"""Bounded read-only source snapshot -> NEW owned archive chunks; no policies/GPU."""
from pathlib import Path
import fcntl,hashlib,importlib.metadata as md,json,os,signal,stat,subprocess,sys,time,traceback
SOURCE=Path('/home/lc01/Zonglin Li/zonglin2');ENV=SOURCE/'envs/mod4';COMPAT=SOURCE/'compat/glibc240'
SDK=SOURCE/'src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1'
RUN=Path(__file__).resolve().parent;CHUNK=512*1024**2
PY=[str(COMPAT/'ld-linux-x86-64.so.2'),'--library-path',str(COMPAT)+':'+str(ENV/'lib'),str(ENV/'bin/python'),'-S','-B','-u']
def put(n,v):
 with (RUN/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def status(pid):
 raw=(Path('/proc')/str(pid)/'stat').read_text();f=raw[raw.rfind(')')+2:].split();boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '));return f[0],boot+int(f[19])/os.sysconf('SC_CLK_TCK')
def ident(pid):
 state,c=status(pid);p=Path('/proc')/str(pid);v=dict(pid=pid,creation=c,exe=os.readlink(p/'exe'),argv=[os.fsdecode(x) for x in (p/'cmdline').read_bytes().split(bytes([0])) if x],root=os.readlink(p/'cwd'));assert status(pid)[1]==c;return v
def out(row):
 try:s,c=status(row['pid']);return c!=row['creation'] or s=='Z'
 except FileNotFoundError:return True
def H(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def progress(stage,**v):
 x=dict(stage=stage,epoch=time.time(),**v)
 with (RUN/'PACK_PROGRESS_ACTUAL.jsonl').open('a') as f:f.write(json.dumps(x)+chr(10))
 print(json.dumps(x),flush=True)
def environment():
 e=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1');e.pop('PYTHONPATH',None);e.pop('PYTHONHOME',None);e.pop('LD_LIBRARY_PATH',None);e.pop('LD_PRELOAD',None)
 for k,v in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','CUDA_CACHE_PATH':'cache/cuda','TORCH_HOME':'cache/torch'}.items():
  p=RUN/v;assert p.resolve().is_relative_to(RUN);p.mkdir(parents=True,exist_ok=True);e[k]=str(p)
 return e
def scope():
 assert SOURCE.resolve()==SOURCE and RUN.resolve().is_relative_to(SOURCE/'runtime_exports') and not SOURCE.is_symlink() and not RUN.is_symlink() and sys.flags.no_site
 assert json.loads((RUN/'OWN_RUNTIME_EXPORT_MARKER.json').read_bytes())['root']==str(RUN)
 assert H(SOURCE/'run-python.sh')=='50f9b0c07ac574c7b094007db94c548ddfc9f1df16b68ad8bfca6392b2a49492'
 assert H(SOURCE/'run-python-compat.sh')=='5c3debdc6abf832d3ff1006a85a9c7bd41dbcd6eb4e049b89bd2b6df01f348a0'
 assert ENV.is_dir() and COMPAT.is_dir() and (SDK/'source').is_dir() and (SDK/'apps').is_dir()
def pack():
 import shutil
 scope();env=environment();site=ENV/'lib/python3.12/site-packages';versions={d.metadata['Name'].lower().replace('_','-'):d.version for d in md.distributions(path=[str(site)]) if d.metadata.get('Name')}
 expected={'torch':'2.10.0+cu128','torchvision':'0.25.0+cu128','isaacsim':'6.0.1.0','isaaclab':'6.1.14','rsl-rl-lib':'5.0.1','numpy':'2.5.2','packaging':'23.2','coverage':'7.6.1'};assert all(versions[k]==v for k,v in expected.items())
 put('ORIGINAL_WORKING_RUNTIME_VERSION_SNAPSHOT_ACTUAL.json',dict(expected=expected,actual={k:versions[k] for k in expected},Requires_Dist_conflicts_preserved_not_repaired=True,no_pip_install_or_dependency_resolution=True,no_Torch_SDK_or_GPU_import=True))
 blocked_suffix={'.pt','.pth.tar','.onnx','.npz','.npy','.pkl','.pickle','.ckpt','.safetensors','.bag','.mcap','.mp4','.avi'}
 kit=ENV/'lib/python3.12/site-packages/isaacsim/kit'
 blocked_roots={kit/'data/documents',kit/'data/cache',kit/'cache',kit/'.cache'}
 roots=[ENV,COMPAT,SOURCE/'run-python.sh',SOURCE/'run-python-compat.sh',SDK/'source',SDK/'apps']
 for name in ['LICENSE','LICENSE.md','LICENSE.txt','LICENSES','NOTICE','README.md','VERSION','pyproject.toml']:
  p=SDK/name
  if p.exists():roots.append(p)
 names=[];excluded=[];files=0;total=0;links=0;directories=0;stack=list(roots)
 while stack:
  p=stack.pop();rel=p.relative_to(SOURCE)
  if p in blocked_roots or p.name=='.git':excluded.append(dict(relative=rel.as_posix(),reason='exact user data/cache or git directory; not read'));continue
  if any(p.name.lower().endswith(x) for x in blocked_suffix) or (p.name.lower().endswith('.pth') and p.parent.name!='site-packages'):excluded.append(dict(relative=rel.as_posix(),reason='policy/raw name excluded before stat/content'));continue
  st=p.lstat()
  if stat.S_ISLNK(st.st_mode):
   target=os.readlink(p);resolved=(p.parent/target).resolve();assert not os.path.isabs(target) and resolved.is_relative_to(SOURCE),'unapproved external/absolute runtime symlink';names.append(rel.as_posix());links+=1
  elif stat.S_ISDIR(st.st_mode):
   names.append(rel.as_posix());directories+=1
   with os.scandir(p) as it:stack.extend(Path(x.path) for x in it)
  elif stat.S_ISREG(st.st_mode):names.append(rel.as_posix());files+=1;total+=st.st_size
  else:excluded.append(dict(relative=rel.as_posix(),reason='nonregular socket/device/FIFO not copied'))
 free=shutil.disk_usage(RUN).free;required=int(total*1.02)+CHUNK;assert free>required,'insufficient owned export filesystem capacity'
 listing=RUN/'INPUT_PATHS_NUL_ARTIFACT';digest=hashlib.sha256()
 with listing.open('xb') as f:
  for name in sorted(set(names)):
   raw=os.fsencode(name)+bytes([0]);f.write(raw);digest.update(raw)
 put('PROVEN72_RUNTIME_EXPORT_INPUT_SCOPE_ACTUAL.json',dict(roots=[str(x) for x in roots],files=files,logical_input_bytes=total,relative_symlinks=links,directories=directories,source_disk_free_before_archive=free,required_worst_archive_capacity=required,excluded=excluded,raw_path_list_artifact=dict(path=str(listing),bytes=listing.stat().st_size,SHA=digest.hexdigest()),vendor_gzip_zip_and_Kit_runtime_resources_retained=True,all_environment_libraries_code_unchanged=True,SDK_editable_and_bin_prefix_relocation_pending_on_new86_copy_only=True,no_existing_policy_or_training_raw_content_or_stat=True))
 tar=['/usr/bin/tar','--format=pax','--pax-option=delete=atime,delete=ctime','--atime-preserve=system','--no-recursion','--null','--verbatim-files-from','-C',str(SOURCE),'-T',str(listing),'-cf','-']
 pigz=['/usr/bin/pigz','-p','2','-1','-c'];chunks=[];archive_hash=hashlib.sha256();written=0;f=None;chunk_hash=None;size=0;last=0
 with (RUN/'TAR_FULL_STDERR.log').open('xb') as te,(RUN/'PIGZ_FULL_STDERR.log').open('xb') as pe:
  a=subprocess.Popen(tar,cwd=RUN,env=env,stdout=subprocess.PIPE,stderr=te,close_fds=True);ar=ident(a.pid);put('EXACT_OWN_TAR_IDENTITY_ACTUAL.json',ar)
  b=subprocess.Popen(pigz,cwd=RUN,env=env,stdin=a.stdout,stdout=subprocess.PIPE,stderr=pe,close_fds=True);a.stdout.close();br=ident(b.pid);put('EXACT_OWN_PIGZ_IDENTITY_ACTUAL.json',br)
  def close_chunk():
   nonlocal f,chunk_hash,size
   f.close();path=RUN/('runtime72.tar.gz.chunk'+str(len(chunks)).zfill(4));os.rename(str(path)+'.partial',path);chunks.append(dict(path=str(path),bytes=size,SHA=chunk_hash.hexdigest()));f=None;size=0
  try:
   while True:
    block=b.stdout.read(1024**2)
    if not block:break
    archive_hash.update(block);written+=len(block);offset=0
    while offset<len(block):
     if f is None:
      path=RUN/('runtime72.tar.gz.chunk'+str(len(chunks)).zfill(4)+'.partial');f=path.open('xb');chunk_hash=hashlib.sha256();size=0
     take=min(CHUNK-size,len(block)-offset);piece=block[offset:offset+take];f.write(piece);chunk_hash.update(piece);size+=take;offset+=take
     if size==CHUNK:close_chunk()
    if time.time()-last>=25:progress('OWNED_RUNTIME_TAR_PIGZ_PACKING',compressed_bytes=written,closed_chunks=len(chunks),logical_input_bytes=total,pigz_threads=2);last=time.time()
   if f is not None:close_chunk()
   rcb=b.wait();rca=a.wait();put('ORIGINAL_TAR_PIGZ_WAITED_ACTUAL.json',dict(tar=dict(identity=ar,returncode=rca,actual_waited=True),pigz=dict(identity=br,returncode=rcb,actual_waited=True)));assert rca==rcb==0,'original tar/pigz error retained; no complete bundle'
  finally:
   if f is not None:f.close()
 put('PROVEN72_RUNTIME_BUNDLE_COMPLETE_PRODUCER_ACTUAL.json',dict(passed=True,epoch=time.time(),format='single gzip tar stream split into ordered512MiB chunks',compressed_bytes=written,producer_SHA=archive_hash.hexdigest(),chunks=chunks,source_versions=expected,input_manifest=str(RUN/'PROVEN72_RUNTIME_EXPORT_INPUT_SCOPE_ACTUAL.json'),source_libraries_and_metadata_unmodified=True,source_sdk_runtime_and_licenses_included=True,original_Requires_Dist_conflicts_preserved=True,no_models_GPU_GO_or_budget=True,new86_transfer_extraction_relocation_and_SDK_admission_pending=True))
def supervise():
 scope();budget=json.loads((RUN/'PACK_BUDGET.json').read_bytes())['max_seconds'];assert budget==1800;env=environment();me=ident(os.getpid());put('EXPORT_SUPERVISOR_IDENTITY_ACTUAL.json',me);lock=(RUN/'OWN_EXPORT.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);put('OWN_EXPORT_LOCK_ACQUIRED_ACTUAL.json',dict(epoch=time.time(),supervisor=me,budget_seconds=budget));p=None;timed=False;rc=None;error=None;child=None
 try:
  with (RUN/'PACK_WORKER_FULL.log').open('xb') as f:
   p=subprocess.Popen(PY+[str(Path(__file__).resolve()),'--pack'],cwd=RUN,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);child=ident(p.pid);put('EXPORT_WORKER_IDENTITY_ACTUAL.json',child)
   try:rc=p.wait(timeout=budget)
   except subprocess.TimeoutExpired:timed=True
 except BaseException:error=traceback.format_exc()
 finally:
  rows=[]
  for name in ['EXACT_OWN_TAR_IDENTITY_ACTUAL.json','EXACT_OWN_PIGZ_IDENTITY_ACTUAL.json']:
   if (RUN/name).exists():rows.append(json.loads((RUN/name).read_bytes()))
  if child and ((p is not None and p.poll() is None) or any(not out(x) for x in rows)):
   if not out(child):assert status(child['pid'])[1]==child['creation']
   assert all(out(x) or os.getpgid(x['pid'])==child['pid'] for x in rows);os.killpg(child['pid'],signal.SIGTERM)
   try:rc=p.wait(timeout=15)
   except subprocess.TimeoutExpired:os.killpg(child['pid'],signal.SIGKILL);rc=p.wait(timeout=15)
   until=time.time()+10
   while time.time()<until and any(not out(x) for x in rows):time.sleep(.1)
   live=[x for x in rows if not out(x)]
   if live:
    assert all(os.getpgid(x['pid'])==child['pid'] for x in live);os.killpg(child['pid'],signal.SIGKILL);until=time.time()+10
    while time.time()<until and any(not out(x) for x in live):time.sleep(.1)
  allout=all(out(x) for x in rows)
  put('EXPORT_SUPERVISOR_TERMINAL_ACTUAL.json',dict(epoch=time.time(),passed=rc==0 and not timed and error is None and allout and (RUN/'PROVEN72_RUNTIME_BUNDLE_COMPLETE_PRODUCER_ACTUAL.json').exists(),returncode=rc,actual_child_waited=p is not None and p.poll() is not None,deadline_terminated=timed,error=error,supervisor=me,worker=child,recorded_tar_pigz=rows,all_recorded_own_children_out=allout,no_source_env_library_or_permission_writes=True))
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close();put('EXPORT_SUPERVISOR_EXIT_ACTUAL.json',dict(epoch=time.time(),own_lock_released=True,no_unknown_process_inspected_or_signalled=True))
if __name__=='__main__':
 if sys.argv[1:]==['--supervise']:supervise()
 elif sys.argv[1:]==['--pack']:
  try:pack()
  except BaseException:put('EXPORT_PACK_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),partial_files_preserved=True));raise
 else:raise SystemExit('exact owned role required')

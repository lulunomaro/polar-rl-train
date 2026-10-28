"""One <=120s known72 read-only environment inventory. No GPU, PT or ledger."""
from pathlib import Path
import hashlib,importlib.util,json,os,shlex,socket,sys,time,traceback
import paramiko
B=Path(__file__).resolve().parent;R=B/'reports';L=B.parent;T=L.parent;W=T.parent
PIN='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
CODE=r'''
from pathlib import Path
import collections,hashlib,importlib.metadata as md,json,os,platform,stat,subprocess,sys,sysconfig,time
START=time.monotonic();DEADLINE=START+102
ROOT=Path('/home/lc01/Zonglin Li/zonglin2');ENV=ROOT/'envs/mod4';COMPAT=ROOT/'compat/glibc240';LAUNCH=ROOT/'run-python.sh'
assert ENV.is_dir() and COMPAT.is_dir() and LAUNCH.is_file() and sys.flags.no_site
EXCLUDED={'.pt','.pth.tar','.onnx','.npz','.npy','.pkl','.pickle','.ckpt','.safetensors','.bag','.mcap','.mp4','.avi','.zst','.zip','.tar','.gz'}
def allowed_name(n):return not any(n.lower().endswith(x) for x in EXCLUDED)
def text(p,maxbytes=262144):
 assert p.suffix not in EXCLUDED and p.resolve().is_relative_to(ROOT)
 with p.open('rb') as f:raw=f.read(maxbytes+1)
 assert len(raw)<=maxbytes
 return dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8'))
def cmd(argv):
 assert time.monotonic()<DEADLINE
 p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=min(12,max(1,DEADLINE-time.monotonic())))
 return dict(argv=argv,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
def inventory(root):
 stack=[root];files=0;total=0;excluded=0;symlinks=[];toplevel=collections.defaultdict(lambda:dict(files=0,bytes=0));partial=False;dirs=0
 while stack:
  if time.monotonic()>=DEADLINE-15:partial=True;break
  d=stack.pop();dirs+=1
  with os.scandir(d) as entries:
   for e in entries:
    if not allowed_name(e.name):excluded+=1;continue
    p=Path(e.path);rel=p.relative_to(root);group=rel.parts[0]
    if e.is_symlink():
     target=os.readlink(p);resolved=os.path.normpath(os.path.join(str(p.parent),target))
     if len(symlinks)<10000:symlinks.append(dict(relative=rel.as_posix(),target=target,resolved=resolved,inside_environment=os.path.commonpath([str(root),resolved])==str(root)))
    elif e.is_dir(follow_symlinks=False):stack.append(p)
    elif e.is_file(follow_symlinks=False):
     s=e.stat(follow_symlinks=False);files+=1;total+=s.st_size;toplevel[group]['files']+=1;toplevel[group]['bytes']+=s.st_size
 return dict(root=str(root),regular_files_excluding_named_policy_raw_archives=files,logical_bytes=total,excluded_filename_count_no_stat_or_content=excluded,directories_visited=dirs,partial_time_bound=partial,not_binary_policy_model_inventory=True,toplevel=dict(toplevel),symlinks=symlinks,symlink_list_truncated=len(symlinks)==10000)
version='python'+str(sys.version_info.major)+'.'+str(sys.version_info.minor);site=ENV/'lib'/version/'site-packages';assert site.is_dir()
distributions=[]
for dist in md.distributions(path=[str(site)]):
 name=dist.metadata.get('Name');versionstr=dist.version
 if name:distributions.append(dict(name=name,version=versionstr,metadata_path=str(dist._path)))
known={x['name'].lower().replace('_','-'):x for x in distributions};metadatas=[]
for name in ['torch','torchvision','isaacsim','isaacsim-core','isaacsim-kernel','isaaclab','isaaclab-rl','rsl-rl-lib','numpy','packaging','coverage']:
 row=known.get(name)
 if row:
  p=Path(row['metadata_path'])/'METADATA'
  if p.is_file() and p.resolve().is_relative_to(ENV):metadatas.append(text(p))
registrations=[]
for p in sorted(site.iterdir()):
 if p.name.endswith('.pth') and p.is_file() and not p.is_symlink():registrations.append(text(p,65536))
scripts=[];prefix=str(ROOT)
for name in ['python','python3','python3.12','pip','pip3','isaacsim','isaaclab','activate','activate.csh','activate.fish']:
 p=ENV/'bin'/name
 if p.is_symlink():scripts.append(dict(path=str(p),symlink=os.readlink(p)))
 elif p.is_file() and name not in ('python','python3','python3.12'):
  with p.open('rb') as f:raw=f.read(65536)
  if raw.startswith(b'#!') or name.startswith('activate'):scripts.append(dict(path=str(p),prefix_occurrences=raw.decode('utf8',errors='replace').count(prefix),UTF8=raw.decode('utf8',errors='replace'),maximum_first_bytes=65536))
elf=[]
for p in [ENV/'bin/python3.12',site/'torch/lib/libtorch_cpu.so',site/'torch/lib/libtorch_cuda.so',COMPAT/'lib/ld-linux-x86-64.so.2']:
 if p.exists():elf.append(cmd(['/usr/bin/readelf','-d',str(p)]))
value=dict(epoch=time.time(),scope='read-only known72 runtime environment; python -S no site registrations executed',source_root=str(ROOT),source_env=str(ENV),source_compat=str(COMPAT),launcher=text(LAUNCH),python=dict(executable=sys.executable,prefix=sys.prefix,base_prefix=sys.base_prefix,version=sys.version,SOABI=sysconfig.get_config_var('SOABI'),MULTIARCH=sysconfig.get_config_var('MULTIARCH'),LIBDIR=sysconfig.get_config_var('LIBDIR'),LDLIBRARY=sysconfig.get_config_var('LDLIBRARY'),libc_confstr=os.confstr('CS_GNU_LIBC_VERSION'),no_site=sys.flags.no_site),OS=dict(uname=list(os.uname()),os_release=Path('/etc/os-release').read_text()),source_prefix_environment={k:os.environ.get(k) for k in ('LD_LIBRARY_PATH','LD_PRELOAD','PYTHONHOME','PYTHONPATH','PATH')},distribution_versions=sorted(distributions,key=lambda x:x['name']),selected_full_package_METADATA=metadatas,source_registration_pth_fulltext=registrations,selected_bin_shebangs_or_links=scripts,selected_ELF_dynamic_sections=elf,system_glibc_metadata=cmd(['/usr/bin/getconf','GNU_LIBC_VERSION']),env_inventory=inventory(ENV),compat_inventory=inventory(COMPAT),no_Torch_SDK_GPU_model_raw_or_ledger_access=True,no_source_file_write=True)
value['elapsed_seconds']=time.monotonic()-START;print(json.dumps(value))
'''
def put(n,v):
 R.mkdir(parents=True,exist_ok=True)
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 put('READONLY_KNOWN72_ENV_PORTABILITY_ENTRY_ENTERED_ACTUAL.json',dict(epoch=time.time(),PID=os.getpid(),script=str(Path(__file__).resolve()),maximum_remote_seconds=120,no_GPU_or_budget=True))
 wrapper=module('same_compressed_for_runtime_readonly_only',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install();secret=None;t=None
 try:
  sec=module('same_password_in_memory_only_for_runtime_readonly',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover()
  sock=socket.create_connection(('10.24.0.72',22),timeout=15);t=paramiko.Transport(sock);t.banner_timeout=15;t.auth_timeout=15;t.start_client(timeout=15);actual=hashlib.sha256(t.get_remote_server_key().asbytes()).hexdigest();assert actual==PIN,'PIN_MISMATCH_BEFORE_AUTH';t.auth_password('lc01',secret,fallback=False);secret=None
  print(json.dumps(dict(stage='PINNED_READONLY72_RUNTIME_METADATA',epoch=time.time())),flush=True)
  ch=t.open_session(timeout=15);ch.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -u -B -S -c '+shlex.quote(CODE));ch.settimeout(120);out=ch.makefile('rb').read();err=ch.makefile_stderr('rb').read();rc=ch.recv_exit_status();put('KNOWN72_ENV_PORTABILITY_ORIGINAL_REMOTE_RESULT_ACTUAL.json',dict(returncode=rc,stdout=out.decode(),stderr=err.decode()));assert rc==0,'read-only environment metadata failed'
  v=json.loads(out);put('KNOWN72_ENV_PORTABILITY_FOOTPRINT_ABI_ACTUAL.json',v);print(json.dumps(dict(actual_returned=True,returncode=rc,elapsed_seconds=v['elapsed_seconds'],env_logical_bytes=v['env_inventory']['logical_bytes'],compat_logical_bytes=v['compat_inventory']['logical_bytes'],env_partial=v['env_inventory']['partial_time_bound'],compat_partial=v['compat_inventory']['partial_time_bound'],no_GPU_model_or_source_writes=True)))
 finally:
  secret=None
  if t:t.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('KNOWN72_ENV_PORTABILITY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise

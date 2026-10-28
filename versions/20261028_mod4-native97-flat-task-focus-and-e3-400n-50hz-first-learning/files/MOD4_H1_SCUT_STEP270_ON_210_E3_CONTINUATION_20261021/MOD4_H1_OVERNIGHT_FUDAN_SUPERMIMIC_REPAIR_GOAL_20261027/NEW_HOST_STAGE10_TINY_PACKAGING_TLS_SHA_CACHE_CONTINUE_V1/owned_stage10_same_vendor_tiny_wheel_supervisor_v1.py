"""Bounded owned HTTP/pip supervisor. No GPU/model/actor/account access."""
from pathlib import Path
from html.parser import HTMLParser
import fcntl,hashlib,json,os,signal,subprocess,sys,time,traceback,urllib.request,urllib.parse
import urllib.error
ROOT=Path('/data/robemo/polar-rl-train');RUN=Path(__file__).resolve().parent;S1=ROOT/'setup_runs/W35_PINNED_ENV_STAGE1_20261027_V1';S4=ROOT/'setup_runs/W35_PINNED_ENV_STAGE4_FRESH_DNS_20261028_V4';S7=ROOT/'setup_runs/W35_PINNED_ENV_STAGE7B_VENDOR_TEST_SPLIT_20261028_V7B';VENV=ROOT/'runtime_envs/vendor_sim601_torch210_lab_test_split_v2'
def put(name,value):
 with (RUN/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
def status(pid):
 raw=(Path('/proc')/str(pid)/'stat').read_text();fields=raw[raw.rfind(')')+2:].split();boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '));return fields[0],boot+int(fields[19])/os.sysconf('SC_CLK_TCK')
def ident(pid):
 state,creation=status(pid);base=Path('/proc')/str(pid);value=dict(pid=pid,creation=creation,exe=os.readlink(base/'exe'),argv=[os.fsdecode(x) for x in (base/'cmdline').read_bytes().split(bytes([0])) if x],root=os.readlink(base/'cwd'));assert status(pid)[1]==creation;return value
def own_out(row):
 try:
  state,creation=status(row['pid']);return creation!=row['creation'] or state=='Z'
 except FileNotFoundError:return True
def emit(stage,**values):
 row=dict(stage=stage,epoch=time.time(),**values)
 with (RUN/'INSTALLER_PROGRESS_ACTUAL.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(row)+chr(10))
 print(json.dumps(row),flush=True)
def H(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def scope():
 assert ROOT.resolve()==ROOT and RUN.resolve().is_relative_to(ROOT) and not ROOT.is_symlink()
 assert json.loads((ROOT/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_bytes())['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700'
 assert json.loads((VENV/'MOD4_VENDOR_RUNTIME_OWNER.json').read_bytes())['created_by_run']==str(S7)
 prior=ROOT/'setup_runs/W35_PINNED_ENV_STAGE9_VENDOR_PACKAGING26_20261028_V9';t=json.loads((prior/'SUPERVISOR_TERMINAL_ACTUAL.json').read_bytes());x=json.loads((prior/'SUPERVISOR_EXIT_ACTUAL.json').read_bytes());launch=json.loads((prior/'DETACHED_LAUNCH_ACTUAL.json').read_bytes())
 assert t['actual_child_waited'] and not t['passed'] and t['all_recorded_pip_children_out_or_nonexecuting'] and x['own_runtime_install_lock_released']
 assert launch['supervisor']['pid']==507459 and launch['supervisor']['creation']==1793171422.08 and launch['installer']['pid']==507460 and launch['installer']['creation']==1793171422.13
 assert all(own_out(row) for row in [launch['supervisor'],launch['installer'],*t['owned_pip_identities']])
 assert 'Temporary failure in name resolution' in (prior/'logs/joint_all_runtime_resolution.log').read_text()
 assert not (VENV/'lib/python3.12/site-packages/000_mod4_exact72_source_registration.pth').exists()
def environment():
 env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',PIP_CONFIG_FILE='/dev/null',PIP_DISABLE_PIP_VERSION_CHECK='1')
 for k,v in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda','TRITON_CACHE_DIR':'cache/triton','HF_HOME':'cache/hf','MPLCONFIGDIR':'cache/mpl','PYTHONUSERBASE':'home/.local'}.items():
  p=RUN/v;assert p.resolve().is_relative_to(ROOT);p.mkdir(parents=True,exist_ok=True);env[k]=str(p)
 return env
class Links(HTMLParser):
 def __init__(self):super().__init__();self.rows=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.rows.append(dict(attrs))
def fetch_kit_resume():
 index='https://pypi.nvidia.com/isaacsim-extscache-kit/'
 with urllib.request.urlopen(index,timeout=20) as response:html=response.read(2*1024**2);final=response.url
 (RUN/'OFFICIAL_KIT_INDEX_UTF8.txt').write_bytes(html);links=Links();links.feed(html.decode('utf8'))
 name='isaacsim_extscache_kit-6.0.1.0-cp312-none-manylinux_2_35_x86_64.whl';matches=[]
 for row in links.rows:
  url=urllib.parse.urljoin(final,row.get('href',''));u=urllib.parse.urlsplit(url)
  if urllib.parse.unquote(u.path).endswith('/'+name):matches.append(url)
 assert len(matches)==1;url=matches[0];u=urllib.parse.urlsplit(url);assert u.scheme=='https';sha=urllib.parse.parse_qs(u.fragment)['sha256'][0];assert len(sha)==64
 house=RUN/'vendor_wheelhouse';house.mkdir();candidates=[p for p in (S7/'tmp').rglob(name) if p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(S7)]
 part=max(candidates,key=lambda p:p.stat().st_size) if candidates else house/(name+'.part')
 offset=part.stat().st_size if part.exists() else 0
 put('KIT_ORIGINAL_PARTIAL_AND_PUBLISHED_SOURCE_ACTUAL.json',dict(path=str(part),original_bytes=offset,original_prefix_SHA=H(part) if offset else None,official_index=index,url=url,published_SHA=sha,TLS_CA_and_hostname_validation=True,source_7B_prefix_preserved_no_copy=True))
 headers={'Range':'bytes='+str(offset)+'-'} if offset else {}
 request=urllib.request.Request(urllib.parse.urldefrag(url)[0],headers=headers)
 try:response=urllib.request.urlopen(request,timeout=30)
 except urllib.error.HTTPError as e:
  if not (offset and e.code==416 and H(part)==sha):raise
  response=None
 if response is not None:
  with response:
   if offset:
    assert response.status==206 and response.headers.get('Content-Range','').startswith('bytes '+str(offset)+'-'),'Range not honored; original partial retained, no automatic restart'
   else:assert response.status==200
   header=response.headers.get('Content-Range');total=int(header.split('/')[-1]) if header else int(response.headers['Content-Length'])
   put('KIT_RANGE_TLS_RESPONSE_ACTUAL.json',dict(status=response.status,Content_Range=header,expected_complete_bytes=total,original_prefix_bytes=offset,verified_TLS=True))
   count=offset;last=0
   with part.open('ab' if offset else 'xb') as f:
    while True:
     block=response.read(1024**2)
     if not block:break
     f.write(block);count+=len(block)
     if time.time()-last>=25:emit('OFFICIAL_KIT_RANGE_DOWNLOAD',complete_bytes=count,expected_bytes=total,reused_prefix_bytes=offset);last=time.time()
   assert count==total
 assert H(part)==sha,'completed official kernel-extension cache SHA differs'
 target=house/name;os.link(part,target)
 put('KIT_COMPLETE_TLS_PUBLISHED_SHA_ACTUAL.json',dict(passed=True,path=str(target),original_path_retained=str(part),bytes=target.stat().st_size,SHA=sha,official_url=url,no_redownload_completed_Torch_or_vision=True))
 return target
def install():
 scope();env=environment();(RUN/'logs').mkdir();emit('MISSING_TINY_OFFICIAL_WHEEL_AND_SAME_VENDOR_DEPENDENCIES',no_GPU_model_or_account=True)
 S9=ROOT/'setup_runs/W35_PINNED_ENV_STAGE9_VENDOR_PACKAGING26_20261028_V9';sdk=S9/'sdk';constraints=S9/'EXPLICIT_VENDOR_RUNTIME_CONSTRAINTS.txt'
 assert 'packaging==26.0' in constraints.read_text()
 old=ROOT/'setup_runs/W35_PINNED_ENV_STAGE8_DETACHED_VENDOR_INSTALL_20261028_V8';kp=json.loads((old/'KIT_COMPLETE_TLS_PUBLISHED_SHA_ACTUAL.json').read_bytes());kit=Path(kp['path']);assert kp['passed'] and kp['SHA']=='35b64cf35ce3d31875ef43025f243c8bd03e29cb28fe844b0cd06b76ba535714' and kit.stat().st_size==kp['bytes']==5879615742
 house=RUN/'tiny_official_wheelhouse';house.mkdir()
 def bounded_TLS(url,label):
  for attempt in range(1,4):
   try:
    emit('OFFICIAL_TLS_NETWORK_ATTEMPT',label=label,attempt=attempt,url=url)
    with urllib.request.urlopen(url,timeout=20) as r:
     assert urllib.parse.urlsplit(r.url).scheme=='https';raw=r.read(2*1024**2+1);assert len(raw)<=2*1024**2
    return raw
   except Exception:
    put(label+'_ORIGINAL_NETWORK_ERROR_'+str(attempt)+'.json',dict(epoch=time.time(),error=traceback.format_exc(),bounded_network_retry_only_no_system_DNS_change=True))
    if attempt==3:raise
    time.sleep(2*attempt)
 primary='https://pypi.org/pypi/packaging/26.0/json';raw=bounded_TLS(primary,'PACKAGING26_PRIMARY');(RUN/'PACKAGING26_OFFICIAL_PRIMARY_FULL_UTF8.json').write_bytes(raw);metadata=json.loads(raw)
 candidates=[x for x in metadata['urls'] if x['filename']=='packaging-26.0-py3-none-any.whl'];assert len(candidates)==1;wheel=candidates[0];url=wheel['url'];assert urllib.parse.urlsplit(url).scheme=='https' and urllib.parse.urlsplit(url).hostname=='files.pythonhosted.org';sha=wheel['digests']['sha256'];assert len(sha)==64 and wheel['size']<1024**2
 data=bounded_TLS(url,'PACKAGING26_EXACT_WHEEL');assert len(data)==wheel['size'] and hashlib.sha256(data).hexdigest()==sha
 packaging_wheel=house/wheel['filename'];packaging_wheel.write_bytes(data);put('PACKAGING26_TINY_OFFICIAL_WHEEL_TLS_PUBLISHED_SHA_ACTUAL.json',dict(passed=True,path=str(packaging_wheel),bytes=len(data),SHA=sha,primary_source=primary,official_url=url,default_CA_hostname_TLS_verification=True,network_retries_bounded_to_three=True,no_hosts_DNS_profile_or_global_environment_changed=True))
 python=str(VENV/'bin/python3');front=str(S1/'venv/bin/python3');cache=S7/'cache/pip'
 def command(label,argv):
  log=RUN/'logs'/(label+'.log')
  with log.open('xb') as f:
   p=subprocess.Popen(argv,env=env,cwd=RUN,stdout=f,stderr=subprocess.STDOUT,close_fds=True)
   row=ident(p.pid)
   with (RUN/'EXACT_PIP_CHILDREN_STARTED_ACTUAL.jsonl').open('a') as q:q.write(json.dumps(row)+chr(10))
   emit('OWN_PIP_STARTED',label=label,identity=row);last=0
   while p.poll() is None:
    if time.time()-last>=25:emit('OWN_PIP_PROGRESS',label=label,pid=p.pid,log_bytes=log.stat().st_size);last=time.time()
    time.sleep(1)
   rc=p.wait();emit('OWN_PIP_WAITED',label=label,returncode=rc);assert rc==0,'own required command failed '+label+' '+str(rc)
 built=S9/'exact_sdk_built_wheels';assert built.is_dir()
 sources=[sdk/'source'/name for name in ['isaaclab','isaaclab_rl','isaaclab_physx','isaaclab_ov','isaaclab_ovphysx','isaaclab_assets','isaaclab_tasks']]
 wheels=[]
 for label,want in [('Torch','628e89bd5110ced7debee2a57c69959725b7fbc64eab81a39dd70e46c7e28ba5'),('vision','1255a0ca2bf987acf9f103b96c5c4cfe3415fc4a1eef17fa08af527a04a4f573')]:
  row=json.loads((S4/'logs'/('download_official_'+label+'_exact_DNS_TLS_SHA.log')).read_text().splitlines()[-1]);p=Path(row['local_wheel']);assert p.is_relative_to(S4/'wheelhouse') and p.stat().st_size==row['bytes'] and row['SHA']==want and row['TLS_verified'];wheels.append(str(p))
 packages=[str(p) for p in sorted(built.glob('*.whl'))];assert len(packages)==7
 requirements=[*wheels,str(kit),str(packaging_wheel),'isaacsim[all,extscache]==6.0.1.0','rsl-rl-lib==5.0.1','numpy==2.3.1','packaging==26.0','warp-lang==1.13.0','tensordict==0.14.1','scipy==1.17.0','gymnasium==1.2.1',*packages]
 pip=[front,'-B','-m','pip','--python',python,'--isolated','--disable-pip-version-check','--cache-dir',str(cache),'install','--no-clean','--no-input','--retries','3','--timeout','20','--index-url','https://pypi.org/simple','--extra-index-url','https://pypi.nvidia.com','-c',str(constraints)]
 command('joint_all_runtime_resolution',pip+['--dry-run','--report',str(RUN/'JOINT_RUNTIME_RESOLUTION_ACTUAL.json'),*requirements])
 command('install_all_joint_required_dependencies',pip+['--report',str(RUN/'JOINT_RUNTIME_INSTALL_ACTUAL.json'),*requirements])
 paths=[str(p) for p in sources];registry=VENV/'lib/python3.12/site-packages/000_mod4_exact72_source_registration.pth'
 with registry.open('x') as f:f.write('import sys; sys.path[:0] = '+repr(paths)+chr(10))
 put('EXACT_SOURCE_REGISTRATION_ACTUAL.json',dict(paths=paths,path=str(registry),scope='this owned runtime only',all_runtime_PY_SHA_unchanged=runtime_rows()==before,explicit_vendor_metadata_deltas=['Lab test coverage extra split','Lab_rl packaging requirement ==26.0']))
 command('pip_check_all_required_dependencies',[front,'-B','-m','pip','--python',python,'--isolated','check'])
 code='import importlib.metadata as m,importlib.util as u,json;from packaging import version;assert m.version("packaging")=="26.0";assert version.parse("5.0.1")>=version.parse("5.0.0")>version.parse("4.0.0");names=["torch","torchvision","isaacsim","isaaclab","isaaclab_rl","rsl-rl-lib","numpy","packaging","coverage"];print(json.dumps({"versions":{n:m.version(n) for n in names},"packaging26_exact_API_used_by_Lab_rl_passed":True,"source_origins":{n:u.find_spec(n).origin for n in ["isaaclab","isaaclab_rl","isaaclab_physx","isaaclab_ovphysx"]}}))'
 command('package_and_source_origin_metadata_and_packaging_API_only',[python,'-B','-c',code])
 put('STAGE10_PACKAGES_AND_SOURCE_REGISTRATION_PASSED_ACTUAL.json',dict(passed=True,venv=str(VENV),no_Torch_SDK_import_GPU_model_GO_or_account=True,actual_source_SDK_CPU_CUDA_restore_native_and_PPO_pending=True,explicit_vendor_metadata_not_official_identical=True))
def supervise():
 scope();budget=json.loads((RUN/'INSTALL_BUDGET.json').read_bytes())['max_seconds'];assert budget in (1800,2400);env=environment();identity=ident(os.getpid());put('SUPERVISOR_IDENTITY_ACTUAL.json',identity)
 lock=(VENV/'MOD4_OWN_RUNTIME_INSTALLER.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);put('OWN_INSTALL_LOCK_ACQUIRED_ACTUAL.json',dict(epoch=time.time(),supervisor=identity,budget_seconds=budget))
 p=None;timed=False;rc=None;error=None
 try:
  with (RUN/'INSTALLER_FULL.log').open('xb') as f:
   p=subprocess.Popen([sys.executable,'-u','-B',str(Path(__file__).resolve()),'--install'],cwd=RUN,env=env,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True,close_fds=True);child=ident(p.pid);put('INSTALLER_IDENTITY_ACTUAL.json',child)
   try:rc=p.wait(timeout=budget)
   except subprocess.TimeoutExpired:
    timed=True;assert status(p.pid)[1]==child['creation'];os.killpg(p.pid,signal.SIGTERM)
    try:rc=p.wait(timeout=10)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);rc=p.wait(timeout=10)
 except BaseException:error=traceback.format_exc()
 finally:
  if p is not None and p.poll() is None:os.killpg(p.pid,signal.SIGTERM);rc=p.wait(timeout=10)
  # Every pip inherits the owned installer process group. After a timeout/error,
  # inspect only exact recorded owned children and wait for their original IDs.
  rows=[];path=RUN/'EXACT_PIP_CHILDREN_STARTED_ACTUAL.jsonl'
  if path.exists():rows=[json.loads(line) for line in path.read_text().splitlines()]
  outstanding=[row for row in rows if not own_out(row)]
  if outstanding and p is not None:
   assert all(os.getpgid(x['pid'])==p.pid for x in outstanding);os.killpg(p.pid,signal.SIGTERM);until=time.time()+10
   while time.time()<until and any(not own_out(row) for row in outstanding):time.sleep(.1)
   live=[row for row in outstanding if not own_out(row)]
   if live:
    assert all(os.getpgid(x['pid'])==p.pid for x in live);os.killpg(p.pid,signal.SIGKILL);until=time.time()+10
    while time.time()<until and any(not own_out(row) for row in live):time.sleep(.1)
  allout=all(own_out(row) for row in rows)
  put('SUPERVISOR_TERMINAL_ACTUAL.json',dict(epoch=time.time(),passed=rc==0 and allout and not timed and error is None and (RUN/'STAGE10_PACKAGES_AND_SOURCE_REGISTRATION_PASSED_ACTUAL.json').exists(),actual_child_waited=True,all_recorded_pip_children_out_or_nonexecuting=allout,returncode=rc,deadline_terminated=timed,error=error,supervisor=identity,owned_pip_identities=rows,no_GPU_model_GO_or_account=True))
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close();put('SUPERVISOR_EXIT_ACTUAL.json',dict(epoch=time.time(),all_recorded_own_children_out_or_nonexecuting=allout,own_runtime_install_lock_released=True,no_foreign_process_inspected_or_signalled=True))
if __name__=='__main__':
 if sys.argv[1:]==['--supervise']:supervise()
 elif sys.argv[1:]==['--install']:
  try:install()
  except BaseException:put('INSTALLER_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),partial_and_completed_bytes_preserved=True));raise
 else:raise SystemExit('exact owned role required')
